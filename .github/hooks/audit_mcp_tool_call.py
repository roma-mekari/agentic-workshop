#!/usr/bin/env python3
"""PreToolUse hook: records every call to a civilian or werewolf MCP tool for audit."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

_MCP_PREFIXES = ("mcp_civilianmcp_", "mcp_werewolfmcp_")
AUDIT_PATH = PROJECT_ROOT / ".werewolf" / "audit" / "mcp_tool_calls.jsonl"


def read_event() -> dict[str, Any]:
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            return {}
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    event = read_event()
    tool_name = str(event.get("tool_name") or "")
    if not any(tool_name.startswith(prefix) for prefix in _MCP_PREFIXES):
        return 0

    record: dict[str, Any] = {
        "recorded_at": utc_now(),
        "hook_event": "PreToolUse",
        "tool_name": tool_name,
        "tool_use_id": event.get("tool_use_id"),
        "tool_input": event.get("tool_input"),
        "session_id": event.get("sessionId"),
        "cwd": event.get("cwd"),
    }

    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    except OSError:
        pass  # Audit failures must never block tool use.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
