# SYL shared memory

This file is the durable, agent-neutral memory index for Claude, Codex, and future builders.
Read `SESSION_HANDOFF.md`, then `BUILDLOG.md`, then this file before changing the project. The live
implementation queue is always `BUILDLOG.md` → **Next up**.

## Design law

- Relate to reality 100%, always. Do not use a visual/menu/teleport fake where a physical system is
  intended. Taking longer is acceptable.
- The player is a body. Ships, stations, cargo, seats, doors, crew, construction, damage, and travel
  exist physically in the world. Menus observe reality; they do not replace it.
- Build forward-compatible systems in real units: real gravity and momentum, UE Large World
  Coordinates, round planets, radial gravity, atmosphere, true-scale travel/orbit, data-driven worlds
  and factions. Never substitute a flat zone or distant-sphere illusion for the promised system.
- Everything visible is authored from scratch. No premade asset packs.

## Intended game

SYL (Space You Land) is Jaron's persistent first-person shared-galaxy space game. The seamless chain is
body → walkable ship → dock/station → planet surface → atmosphere → space → orbit → another real world.
The world is built by machines and labor over time rather than appearing from menus. Fortis is the
first playable faction slice: armored, practical, militarized, and physically legible.

## Working with Jaron

- Be proactive and build coherent chunks; do not stop at plans when implementation is possible.
- Keep explanations concrete and visual. Show what exists, what was verified, and what comes next.
- Ask Jaron for hands-on feel tests when real input or subjective tuning is required, but automate
  structural, physics, compile, log, and transform checks first.
- One coherent chunk per pass: save Unreal, update BUILDLOG with date + builder, capture evidence,
  commit, and push. Preserve another agent's or Jaron's unrelated changes.

## Cross-agent protocol

1. Begin with `git status` and read the three handoff files. Pull only when the worktree is safe.
2. Treat repo files—not private runtime memory—as the shared source of truth.
3. Record exact asset paths, Blueprint behavior, coordinates, verification results, unresolved issues,
   and `Builder: Claude|Codex` in BUILDLOG.
4. End a completed chunk with a Git commit and push to
   `github.com/JaronKBragg7337/SpaceYouLand` (`main`). The repository is currently public; never commit
   secrets or personal data.
5. The next agent resumes the first current item under BUILDLOG **Next up**, not an older stale plan.

## Current reality (2026-06-18)

Fortis outpost and bespoke prop kit exist at the origin. A 36×28 m clear development apron sits east
of the walls at (4500,0). The modular Fortis gunship is walkable, uses the same player body for its
physical pilot seat, has an animated pressure door/ramp, and flies through real Chaos force/torque.
Jaron's first full boarding/flight/exit playtest passed apart from ramp touchdown and forward visibility;
both are now corrected (−31° open ramp, eye-level windscreen) and await his quick confirmation.
