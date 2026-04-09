#!/usr/bin/env python3
"""SubagentStop hook: validates that a player subagent called the required MCP submit tool."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp_servers.common import build_public_state
from mcp_servers.common import build_werewolf_state

AUDIT_LOG_PATH = PROJECT_ROOT / ".werewolf" / "audit" / "mcp_tool_calls.jsonl"
# How far back (in seconds) to search the audit log for a matching tool call.
_AUDIT_WINDOW_SECONDS = 600


# Required MCP submit tool for each (agent_type, phase) combination.
_REQUIRED_SUBMIT_TOOL: dict[tuple[str, str], str] = {
    ("civilian", "day"): "mcp_civilianmcp_submit_day_vote",
    ("doctor", "day"): "mcp_civilianmcp_submit_day_vote",
    ("doctor", "night"): "mcp_civilianmcp_submit_protection",
    ("werewolf", "day"): "mcp_civilianmcp_submit_day_vote",
    ("werewolf", "night"): "mcp_werewolfmcp_submit_kill_vote",
}


def read_event() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("SubagentStop hook received an empty payload.")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("SubagentStop hook payload must be a JSON object.")
    return payload


def mcp_tool_calls_from_transcript(path: Path) -> list[str]:
    """Return the names of MCP tool calls found in the subagent transcript."""
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    tool_names: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            entry = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue

        entry_type = entry.get("type", "")

        # Tool_use blocks embedded inside assistant messages (Anthropic content format).
        if entry_type == "assistant.message":
            data = entry.get("data") or {}
            content = data.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = str(block.get("name") or "")
                        if name:
                            tool_names.append(name)

        # Standalone tool call/use entry types.
        elif entry_type in ("tool_call", "tool_use", "function_call"):
            data = entry.get("data") or {}
            name = str(
                data.get("name")
                or data.get("tool_name")
                or entry.get("name")
                or entry.get("tool_name")
                or ""
            )
            if name:
                tool_names.append(name)

    return tool_names


def audit_log_has_recent_call(required_tool: str) -> bool:
    """Return True if the audit log contains a call to required_tool within the recent window.

    The PreToolUse hook writes every MCP tool invocation to the audit log before the
    tool runs, so this is always populated even when the transcript cannot be parsed.
    """
    if not AUDIT_LOG_PATH.exists():
        return False
    try:
        lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False

    now = datetime.now(timezone.utc)
    for line in reversed(lines):  # most-recent entries first
        stripped = line.strip()
        if not stripped:
            continue
        try:
            entry = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("tool_name") != required_tool:
            continue
        recorded_at_str = entry.get("recorded_at", "")
        try:
            recorded_at = datetime.fromisoformat(recorded_at_str)
            if (now - recorded_at).total_seconds() <= _AUDIT_WINDOW_SECONDS:
                return True
        except (ValueError, TypeError):
            continue
    return False


def main() -> int:
    event = read_event()
    hook_event = str(event.get("hookEventName") or "").strip()
    if hook_event and hook_event != "SubagentStop":
        return 0

    agent_type = str(event.get("agent_type") or "").strip().lower()
    if agent_type not in {"civilian", "doctor", "werewolf"}:
        return 0

    # Guard: never block an already-continuing subagent to prevent infinite loops.
    if event.get("stop_hook_active"):
        print(json.dumps({
            "systemMessage": (
                f"WARNING: {agent_type} subagent finished without calling the required MCP "
                "submit tool. Allowing completion to avoid an infinite loop."
            )
        }, ensure_ascii=True))
        return 0

    try:
        public_state = build_public_state()
        werewolf_state = build_werewolf_state() if agent_type == "werewolf" else {}
    except Exception as exc:
        # Fail open if game state cannot be read.
        print(json.dumps({"systemMessage": f"SubagentStop hook could not read game state: {exc}"}, ensure_ascii=True))
        return 0

    phase = str(public_state.get("phase") or "day").lower()
    required_tool = _REQUIRED_SUBMIT_TOOL.get((agent_type, phase))
    if required_tool is None:
        return 0  # Unknown combination — skip validation.

    # Check the transcript for the required MCP tool call.
    transcript_raw = event.get("transcript_path") or event.get("agent_transcript_path")
    tool_calls: list[str] = []
    if isinstance(transcript_raw, str) and transcript_raw.strip():
        tool_calls = mcp_tool_calls_from_transcript(Path(transcript_raw.strip()))

    if required_tool in tool_calls:
        return 0

    # Fallback: the transcript parser may not support the current VS Code transcript
    # format. The PreToolUse audit log is written unconditionally for every MCP call
    # and is always parseable, so use it as the authoritative fallback.
    if audit_log_has_recent_call(required_tool):
        return 0

    # Required submit tool was not called — block and instruct the subagent.
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"The {agent_type} subagent must call '{required_tool}' to submit its "
            f"{phase}-phase action before finishing. Call the MCP tool now and then complete."
        ),
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover — fail open so hook errors don't block the game.
        print(json.dumps({"systemMessage": f"SubagentStop hook failed unexpectedly: {exc}"}, ensure_ascii=True))
        raise SystemExit(0)