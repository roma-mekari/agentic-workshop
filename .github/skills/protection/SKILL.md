---
name: protection
description: Choose the most defensible doctor protection target, using civilianMcp to read public state and submit the final protection action.
---

Use this skill when acting as the doctor during the night phase of the werewolf game.

Your job is to protect one player using only public information and submit that protection through MCP before you finish. You must not assume access to werewolf-private discussion or hidden roles.

This skill owns the MCP-first workflow. Do not wait for the caller to summarize the game, list living targets, or restate prior votes.

## MCP Workflow

1. Call `civilianMcp/get_public_state` first.
2. If you need the full public history, call `civilianMcp/read_public_log`.
3. Treat the caller's prompt as authoritative only for your player name and any explicit rule override, such as whether self-protection is allowed.
4. Build valid targets from `living_players`. Include yourself unless the caller explicitly forbids self-protection.
5. Choose the most defensible protection target from public evidence.
6. Call `civilianMcp/submit_protection` with your chosen player, target, and reason.
7. Confirm to the caller that your protection was submitted.

## Available Information

You may rely on:
- Public history from `game_session.md`, read through `civilianMcp`
- Voting patterns and accusation history
- Which players are alive
- Publicly visible night outcomes from earlier rounds

You must not rely on:
- `night_time.md`
- Hidden werewolf coordination
- Certainty about any player's role unless it is public knowledge

## Decision Process

Choose the protection target most likely to prevent a meaningful civilian-side loss.

Consider:
- Which player is most likely to be attacked next
- Which living player is most valuable for civilian-side deduction
- Whether self-protection is strategically justified if the rules allow it
- Whether a repeated protection is defensible from the public pattern, if repeated protections are allowed

If there is no strong signal, prefer protecting a player whose survival best preserves civilian information quality for the next day.

## Constraints

- Protect exactly one living player
- Do not target eliminated players
- Keep the reason concise and grounded in public signals
- Do not claim access to hidden information
- Always call `civilianMcp/submit_protection` before finishing — the SubagentStop hook will block you if the tool was not called.