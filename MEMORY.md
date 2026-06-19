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

## Current reality (2026-06-19)

Fortis outpost and bespoke prop kit exist at the origin. A 36×28 m clear development apron sits east
of the walls at (4500,0). The modular Fortis gunship is walkable, uses the same player body for its
physical pilot seat, has an animated pressure door/ramp, and flies through real Chaos force/torque.
Ramp touchdown (−31°) and the eye-level windscreen are confirmed good by Jaron. The gunship now has a
pilot camera system: a first-person CockpitCam and a third-person ChaseCam, switched on sit/stand via
SetViewTargetWithBlend, with **C** toggling first/third person while seated; on-foot input is gated so
the arrow keys steer ONLY the ship while seated (head-look no longer fights the ship). Awaiting Jaron's
flight feel-test (camera placement + steering). Open-space motion reference (the "void") is deferred to
the real space arc (stars/planets); near home the chase cam gives reference against the apron/outpost.

Jaron has since confirmed controls are good for now. The real planet lane has begun: a data-driven,
true-scale 6,360 km-radius `BP_SYL_CelestialWorld` is centered 6,360 km beneath the origin, aligned with
the existing real SkyAtmosphere radius/height. The gunship reads that actor's radius and 9.80665 m/s²
surface acceleration and applies inverse-square radial gravity; an off-axis automated probe confirmed
force points exactly toward the body center. The continuous geoid is authored from scratch and always
loaded, but does not pretend to be local terrain. Streamed local surface geometry now supplies that
layer; radial character orientation is next.

The first destination now exists. `SYL_SurfaceSite_A01` is 2 km along the planet surface in the +X
direction from home, placed and pitched from exact 6,360 km spherical coordinates. It streams as a
World Partition surface actor with a 2×2 km curved UCX-collidable terrain cap, 80×80 m physical deck,
shelter, 45 m red beacon, and real pad lighting. The gunship passed an automated radial touchdown with
0.009 cm tangential drift and still settles normally at home. Jaron's next useful test is the full
home→site→home flight; its real travel time and approach visibility should drive the next tuning pass.
