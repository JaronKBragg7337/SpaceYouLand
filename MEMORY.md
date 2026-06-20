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

**SYL is a REAL SOLAR SYSTEM (Jaron, 2026-06-19).** The endgame is *multiple* real planets — eventually
mapped to our actual solar system — that players physically fly between. There is never just "the planet";
every planet is a data-driven body, and the way one planet is built must be the reusable pattern for all of
them. (Reference frame: the seamless body→ship→surface→orbit→other-world scale is the KSP-style *mechanic*,
but the *principle* is realism + correct placement on a sphere. Do not over-index on any one game; build the
general, reusable, data-driven system — see [[syl-endgame-intent]], [[realism-law]].)

## ★ BUILD-ORDER PRINCIPLE — planet first, then place things ON it (Jaron, 2026-06-19)

The home/remote/planet height-mismatch bug came from PROCESS: Fortis (a flat platform), the remote pad, and
the planet were each authored in *separate sessions* at *different heights/levels*, then a planet was bolted
on afterward. That is backwards and must never be repeated.

- **The planet body is the foundation. Build/define it FIRST.** Then place every structure ON its surface at
  the correct spherical position with **radial "up" orientation** (the surface normal points away from the
  body center). A site's flat local pad is fine, but it must be *seated on* the sphere at that point.
- **One surface, not stacked shells.** A location must have exactly one visible-and-physical ground. Never a
  near-field cap *and* a coarse global geoid both rendering as separate surfaces at a location ("a planet
  inside the planet"). The coarse geoid is ONLY the distant silhouette beyond the near-field surface.
- **Acceptance is measured, not screenshotted.** "Fixed" = a straight-down trace at a base and at open
  ground hit ONE continuous surface (heights agree within the structure's intended raise), AND looking
  straight up from open ground shows only sky (no second shell). Do not declare a planet fixed from a single
  framed capture.
- This pattern is **per-planet and reusable** for the future multi-planet solar system.

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
direction from home, placed and pitched from exact 6,360 km spherical coordinates. After Jaron's altitude
screenshots exposed stacked visual layers, the world now has one always-loaded high-resolution north-pole
cap covering 156.082 km and matching the global geoid's first ring. The cap is both visible and physical
(`CTF_UseComplexAsSimple`); all of it and the distant geoid share one material. The old neighboring 2×4 km
tiles remain hidden collision backups only, so they cannot appear as rectangular shelves. A PIE player
spawn outside both tiles landed on the cap's analytic sphere instead of falling through. The remote
80×80 m deck, shelter, 45 m beacon, and real pad lights remain intact, and the ship still settles at home
with exact zero rotation.

**CORRECTION (Jaron testing, 2026-06-19 — the cap fix is NOT finished).** Jaron flew it and the planet still
reads as two stacked shells with the bases floating. Claude verified live (editor, commit 5cb310f): the cap
IS a real physical curved surface (top z=0, open ground 1 km out traces to −7.86 cm = true sphere ✓), BUT
(a) the home apron deck traces at **+54 cm while the surface under it is ≈0** → the base is NOT seated on the
planet (it floats ~0.5 m above), and (b) the coarse global geoid is a SEPARATE actor that doesn't even load
in the editor world while the cap is always-loaded → two surfaces, "a planet inside the planet." Codex's
captures looked fine only because they framed the new cap in isolation. **The fix Claude now owns (Codex out
of usage): apply the BUILD-ORDER PRINCIPLE above — one surface, bases seated on it, measured acceptance.**
