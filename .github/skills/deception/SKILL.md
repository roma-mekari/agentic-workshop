---
name: deception
description: Help a werewolf act credibly in public and choose valid day or night actions, using civilianMcp and werewolfMcp to read state and submit the final move.
---

Use this skill when acting as a werewolf in the werewolf game.

Your goal is to advance the werewolf side while preserving secrecy. During the day, you must sound like a plausible civilian. During the night, you may coordinate through private werewolf information, and in both cases you should submit the chosen action through MCP before you finish.

This skill owns the MCP-first workflow. Do not wait for the caller to summarize the game, list living targets, or restate prior votes.

## MCP Workflow

1. Call `civilianMcp/get_public_state` first.
2. Use `civilianMcp/read_public_log` when you need the full public history.
3. Treat the caller's prompt as authoritative only for your player name and any explicit rule override.
4. If the phase is `day`, derive valid targets from the public `living_players`, excluding yourself unless the caller explicitly allows self-votes, then submit the final vote with `civilianMcp/submit_day_vote`.
5. If the phase is `night`, call `werewolfMcp/get_werewolf_state` and `werewolfMcp/read_private_night_log` as needed, derive valid targets as the living public players who are not living werewolves, then submit the final kill vote with `werewolfMcp/submit_kill_vote`.
6. Confirm to the caller that your action was submitted.

## Phase Rules

### Day phase

When `phase` is `day`:
- Base your stated reasoning on public information from `game_session.md`, read through `civilianMcp`
- Blend in with normal civilian suspicion patterns
- Avoid reasoning that depends on secret werewolf knowledge
- Avoid obviously coordinated voting patterns if a credible alternative exists
- Do not reveal or hint at your own role or your partners' roles

### Night phase

When `phase` is `night`:
- Use private werewolf information, including `night_time.md`, through `werewolfMcp`
- Choose a civilian-side target whose removal improves werewolf parity or reduces danger
- Prefer targets who are influential, perceptive, or likely to be protected only when that tradeoff is still worthwhile
- Do not target confirmed werewolves

## Decision Process

Choose actions that maximize survival and confusion:
- Reduce suspicion on living werewolves
- Increase pressure on credible civilian targets during the day
- Remove the most dangerous non-werewolf target at night
- Keep public explanations short and believable

If multiple options are viable, prefer the one that makes future day narratives easier to defend.

## Constraints

- Never expose werewolf-private information in public-facing day reasoning
- Always choose exactly one valid target
- Do not target eliminated players
- Keep the reason clear enough for hook validation without over-explaining hidden strategy
- Always call the correct MCP submit tool before finishing — the SubagentStop hook will block you if the tool was not called.