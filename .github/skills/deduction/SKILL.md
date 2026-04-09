---
name: deduction
description: Deduce the most likely werewolf from public game history, using civilianMcp to read state and submit the final day vote.
---

Use this skill when acting as a civilian-side player during the day phase of the werewolf game.

Your job is to make the strongest public deduction you can from public information only and submit the resulting day vote through MCP before you finish.

This skill owns the MCP-first workflow. Do not wait for the caller to summarize the game, list living targets, or restate prior votes.

## MCP Workflow

1. Call `civilianMcp/get_public_state` first.
2. If the parsed state is incomplete or you need exact vote language, call `civilianMcp/read_public_log`.
3. Treat the caller's prompt as authoritative only for your player name and any explicit rule override.
4. Build valid targets from `living_players`, excluding yourself unless the caller explicitly allows self-votes.
5. Choose the strongest public suspect supported by the log.
6. Call `civilianMcp/submit_day_vote` with your chosen player, target, and reason.
7. Confirm to the caller that your vote was submitted.

## Available Information

You may rely on:
- Public history from `game_session.md`, read through `civilianMcp`
- Announced eliminations and survival outcomes
- Prior public votes and stated reasons
- The current list of living and eliminated players

You must not rely on:
- `night_time.md`
- Hidden role assignments
- Out-of-band guesses that contradict the public record

## Decision Process

Before choosing a target, evaluate the public record for:
- Vote inconsistency across days
- Opportunistic bandwagoning
- Sudden defense of suspicious players without solid reasoning
- Reactions to night outcomes and eliminations
- Players whose public explanations do not match their earlier positions

Prefer evidence grounded in the log over vague intuition. If evidence is weak, choose the player with the strongest cumulative public suspicion and say so plainly.

## Constraints

- Vote for exactly one living player other than yourself unless the game master explicitly allows self-votes
- Do not target eliminated players
- Do not claim certainty unless the public evidence justifies it
- Keep reasoning concise, specific, and public-safe
- Always call `civilianMcp/submit_day_vote` before finishing — the SubagentStop hook will block you if the tool was not called.