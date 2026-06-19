# SYL — Build Log

> **Read this first if you're a fresh session.** This is the running record of what's been
> built in-engine and how. Pair it with `SYL_FirstPlayable_Plan.md` (older, partly off-canon)
> and the canonical design docs in Google Drive (folder **Space-You-Land (2026-2027)**).
> Shared project memory lives in `MEMORY.md`; operational details live in `SESSION_HANDOFF.md`.
> These repo files are the handoff contract between Claude, Codex, and future sessions.

## What SYL actually is (one paragraph)
Persistent, **first-person**, shared-galaxy space game. **Menus observe reality; they don't
replace it.** You are a body; ships and stations are walkable places; cargo is physical; crew
are positioned actors. **Seamless scale, no loading screens** (chair → ship → dock → station →
planet → space). **The world is built, not spawned** — structures are made by machines + labor,
visibly, over time; build gear is faction-formed; Builder is a full role. 7 playable factions;
**Fortis** (militaristic, armored, serious) is the first slice. No premade assets — **everything
is authored from scratch.** Don't write philosophy/lore framing; keep it concrete and buildable.

## Jaron's standing direction (2026-06-18)
"Keep going and finish this game. Just log what you do so the next you can pick up no issue."
Full access granted. Autonomy to continue building as I see fit. Signature / "made by Claude Code"
marks and easter eggs are explicitly welcomed. The design-doc track is handled in a separate
Drive thread — **my lane is the in-engine build.** Don't rewrite the Drive docs unless asked.

## The from-scratch asset pipeline (PROVEN — use this for all geometry)
1. Write a Blender Python script under `_authoring/` that builds geometry (`bmesh`, boxes, etc.).
2. Export **FBX** (UE's `import_file` accepts only fbx/obj — NOT glb). Settings that work:
   `export_scene.fbx(filepath=..., use_selection=..., object_types={'MESH'}, apply_unit_scale=True,
   global_scale=1.0, axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')`. Model in **meters**;
   UE imports at correct cm (100x), Z-up preserved.
3. Run headless: `blender --background --python _authoring/<script>.py`.
4. Import: `StaticMeshTools.import_file(folder_path='/Game/Curtis/Meshes', asset_name=..., source_file=<abs .fbx>)`.
5. Place with `SceneTools.add_to_scene_from_asset`; assign materials via component `OverrideMaterials`
   (set_properties JSON `{"OverrideMaterials":["/Game/.../M_x.M_x"]}`) or `StaticMeshTools.set_material`.

## Engine / scene conventions
- **Level:** `/Game/ThirdPerson/Lvl_ThirdPerson` (World Partition + OFPA; save with `AssetTools.save_assets([])`).
- **Player spawn:** origin (0,0,302). Player faces **+X**. Units = cm.
- **Fortis outpost:** 3000×3000 compound centered at origin, foundation top at **z=50**. Entrance gap
  on **-X** (behind spawn). Everything named `Fortis_*`, filed in outliner folder `Fortis_Outpost/...`.
- **Development apron:** 36×28 m clear integration platform centered at **(4500,0)** outside the east
  wall; structural top collision is **z=52.25**. Folder `Fortis_Outpost/Development`. Use this area for
  vehicle construction, physics settling, boarding tests, and clean captures—not the crowded courtyard.
- **Materials** (`/Game/Curtis/Materials`): `M_Fortis_Steel` (dark metallic), `M_Fortis_Red` (red emissive beacon).
- **Lighting:** grim overcast dusk — DirectionalLight intensity 7, warm; SkyLight 3.2 cool fill; fog 0.035;
  two red `Fortis_AlertLight_*` point lights over the courtyard (intensity 5000, radius 1800).
- **Viewport capture note:** `CaptureViewport` returns a base64 PNG too big to inline. Decode it:
  read the saved tool-result .txt, `json.loads`, `returnValue.image.data` → base64 → write a .png → Read it.
  Pass an `annotations` object with all fields zero/null to disable overlays.

## Build history
- **2026-06-18 — Step 1: Fortis outpost blockout.** 22 primitive actors (foundation, perimeter blast
  walls + gate pillars, 3 corner buildings, 2 guard towers, comms mast + red beacon, landing pad,
  7 crates) + red-alert lighting. Steel material on all, red on beacon. Saved.
- **2026-06-18 — Pipeline proof.** Authored `SM_Fortis_BuildCrane` from scratch (portal gantry,
  legs+bracing+double girder+trolley+cable+hook+cabin, ~300 tris) in Blender, imported, placed on
  the landing pad with steel. Confirmed Blender→FBX→UE loop end-to-end at correct real-world scale.
  Script: `_authoring/make_crane.py`.

- **2026-06-18 — Asset kit + construction staging + signature.** Authored from scratch (script
  `_authoring/make_assets.py`): `SM_Fortis_Crate`, `SM_Fortis_HullFrame` (half-built ship hull),
  `SM_Claude_Monolith`, `SM_Claude_Sign` (real 3D text "MADE BY / CLAUDE CODE"). Imported all 4.
  Swapped the 7 cube crates to the real crate mesh. Staged the hull frame under the crane hook at
  (1130,900,90) so the site reads as under construction. Placed monolith+sign at the entrance gate
  (~-1250,0). New material `M_Claude_Sign` (warm coral emissive). Saved.
  NOTE: Blender FONT text bakes glyph fronts toward -Y after `rotation_euler=(90°,0,0)`+apply; in UE the
  sign needed actor **yaw 90** (not -90) to face the entering player (-X) — else text renders mirrored.

- **2026-06-18 — First-person player (part 1 of 2).** From scratch: `BP_SYL_Player` (parent
  `/Script/Engine.Character`) with a `FPCamera` CameraComponent at relative (10,0,64),
  `bUsePawnControlRotation=true`, and `bUseControllerRotationYaw=true` on the CDO. `BP_SYL_GameMode`
  (parent GameModeBase) with `DefaultPawnClass = BP_SYL_Player_C`. Level WorldSettings
  `DefaultGameMode = BP_SYL_GameMode_C`. Both compiled. PIE launches and renders the outpost in-game.
  All under `/Game/Curtis/Blueprints`. Created via `BlueprintTools.create(asset_type={refPath:class})`,
  components via `ActorTools.add_component`, defaults via CDO from `get_default_object` + `set_properties`.
  **STILL TODO (part 2):** no movement/look input yet — UE5.8 uses Enhanced Input, so next pass create
  InputAction + InputMappingContext, add the IMC on BeginPlay, and bind Move/Look in the event graph
  (use `BlueprintTools.write_graph_dsl`; see `get_graph_dsl_docs`). Then verify first-person walking.

- **2026-06-18 — First-person player (part 2 — WALKABLE ✅).** Wired move+look in `BP_SYL_Player`
  EventGraph via `write_graph_dsl` on `EventTick`, polling keys with `Game|Player|IsInputKeyDown`
  (no Enhanced Input assets / no restart needed): W/S → `Pawn|Input|AddMovementInput` along
  `GetActorForwardVector`; A/D along `GetActorRightVector`; arrow keys → `AddControllerYawInput` /
  `AddControllerPitchInput`. Compiled clean. PIE verified: GameMode spawns & possesses
  `BP_SYL_Player_C_0`; player camera sits at ~(10,0,204) eye height facing +X — true first-person.
  Checkpoint `_pie_fp2.png`. NOTE: movement *logic* is correct + possession confirmed, but I can't
  simulate keypresses headlessly — Jaron should press WASD/arrows in PIE to feel it. Optional polish
  later: mouse-look (needs multi-output `GetInputMouseDelta` handled via create_node/connect_pins, not
  inline DSL) and migrating to proper Enhanced Input assets. Key FKeys pass as quoted names ("W","Left").

- **2026-06-18 — Modular armored building (replaced cube buildings).** Authored `SM_Fortis_Building`
  from scratch (`_authoring/make_building.py`, ~252 tris): armored hull with foundation lip, corner
  buttresses, parapet roof, recessed doorway + step, wall vent slits, a battered angled armor panel,
  roof vent/antenna. Imported, **deleted the 3 cube buildings** (Barracks/Armory/CommandBunker) and
  placed real instances at the same spots, scaled per footprint, each yawed so the **door faces the
  courtyard** (137/43/-45). Steel material. Saved. Checkpoint `_view_buildings.png`.

- **2026-06-18 — Fortis gunship (from scratch).** Authored `SM_Fortis_Gunship`
  (`_authoring/make_gunship.py`, ~276 tris): armored dropship — fuselage, raked cockpit, chin turret,
  top spine, twin rear engine nacelles + exhausts, stub wings w/ weapon pods, tail fin + stabilizers,
  landing skids. Imported, docked in the courtyard at (-150,-720,50) yaw 150 (the landing pad itself
  holds the crane + under-construction hull, so the finished gunship sits in open courtyard). Steel
  material. Saved. Checkpoint `_view_gunship.png`. The exploration-beat hook now exists physically.

- **2026-06-18 — Perimeter walls + gatehouse (replaced cube walls).** Authored `SM_Fortis_WallPanel`
  (6 m, crenellated parapet, buttress ribs, battered base) and `SM_Fortis_Gate` (twin-tower gatehouse,
  X-axis opening) from scratch (`_authoring/make_walls.py`). Removed the 7 cube wall/gate-pillar actors;
  placed 19 panels around the perimeter (5 N, 5 E, 5 W, 4 S w/ center gap) + the gatehouse at the
  entrance (-1500,0,50). Steel material. Checkpoint `_view_walls.png`. (Note: this pass ran from a
  leftover queued loop tick during a pause — Jaron OK'd keeping it.)

- **2026-06-18 — Corner watchtowers (replaced cylinder towers).** Authored `SM_Fortis_Watchtower`
  (`_authoring/make_watchtower.py`, ~360 tris): trussed 4-leg tower w/ cross-braces, railed platform,
  cabin + window slits, slanted roof, searchlight + antenna; ~9.6 m tall (overlooks the ~5 m walls).
  Removed the 2 cylinder guard towers; placed 4 watchtowers at all corners (searchlights facing out).
  Steel. Checkpoint `_view_towers.png`. **All primitive/cube blockout is now replaced by from-scratch
  geometry** — outpost is fully bespoke.

- **2026-06-18 — Courtyard prop kit + functional lighting.** Authored `SM_Fortis_Barrier` (blast
  barrier) and `SM_Fortis_Floodlight` (5 m lamp pole) from scratch (`_authoring/make_props.py`).
  Placed 7 barriers (gate chicane + scattered) and 4 floodlight poles with real warm `PointLight`
  actors (intensity 9000, radius 1700, warm white) for courtyard readability + atmosphere. Steel.
  Checkpoint `_view_props.png`. Compound now reads as an active, lit, defended outpost.

- **2026-06-18 — Servicing props.** Authored `SM_Fortis_FuelDrum` (real cylinder barrel) and
  `SM_Fortis_Antenna` (mast + crossbars + radar drum) from scratch (`_authoring/make_service.py`,
  first use of `bmesh.ops.create_cone` for real cylinders). Placed a 6-drum cluster by the gunship +
  an antenna near the command bunker. Steel. Checkpoint `_view_service.png`.

- **2026-06-18 — Walkable Fortis gunship + development apron (Builder: Codex).** Replaced the sealed
  low-detail gunship prop with a modular, human-scale ship authored from scratch in
  `_authoring/make_walkable_gunship.py`: physics deck, armored exterior, modeled interior, trim,
  cockpit glass, fasteners/bolts, rear ramp, sliding pressure door, raised identity marking, landing
  gear, engines, cockpit/seat/console, cargo bay benches/lockers/conduits, and internal lights. Assets
  live under `/Game/Curtis/Meshes/Gunship`; new materials are `M_Fortis_Glass` and
  `M_Fortis_Interior`. `BP_SYL_Ship` now keeps the player's existing body: E near the exterior door
  control toggles the ramp/door; E near the pilot seat disables character movement/collision and
  attaches that same character to `SeatAnchor`; E while seated detaches to `StandAnchor`. Flight forces
  are gated by `bPilotSeated`; the GameMode again spawns `BP_SYL_Player_C` on foot.

  Built `_authoring/make_dev_apron.py` and imported a real 36×28 m steel development apron plus raised
  red safety markings under `/Game/Curtis/Meshes/Infrastructure`, centered at (4500,0,27.5). Moved the
  gunship to the clear apron. Removed 12 stale ThirdPerson template obstacle actors that obstructed the
  outpost and were not part of Fortis. Final collision architecture: flat deck is the simulated root;
  four welded box colliders match the modeled landing pads; ramp, pressure door, cabin walls, roof, and
  nose are `QueryOnly` so characters can walk against them without welding the cabin cage into the
  flight body. PIE simulation after 5+ seconds: ship location ~(4500,0,138.36), rotation exactly
  pitch/yaw/roll 0/0/0. Apron trace was flat across its full width. Checkpoints:
  `_codex_walkable_ship_exterior.png`, `_codex_walkable_ship_interior.png`,
  `_codex_walkable_ship_apron_pie.png` (ignored scratch captures, not committed).

- **2026-06-18 — Playtest fixes (Builder: Claude).** From Jaron's first boarding playtest: (1) couldn't
  jump and hit a step he couldn't clear → added **Space = Jump** (`Character|Jump`) to `BP_SYL_Player`
  EventTick (preserved Codex's empty BeginPlay/Overlap events); raised `CharMoveComp` **MaxStepHeight 55**,
  **JumpZVelocity 520**. (2) spawn (outpost) and the east apron weren't connected → **opened the east wall**
  (removed `Fortis_WallPanel_03` @ (1500,0)) and laid a steel walkway `Fortis_ApronWalkway_01` (deck plate)
  bridging the foundation to the apron west edge at deck height. **Trace-verified** continuous walkable
  ground along y=0: z 50→51→52→54 outpost→apron, no gaps (all within step height). Saved.
  (Walkway is a quick steel deck plate — upgrade to an authored road later if desired.)

- **2026-06-18 — Playtest fixes 2 (Builder: Claude).** (a) **GLASS — fixed:** `M_Fortis_Glass` was
  `BLEND_Translucent` but opacity **0.38** with a near-black tint → couldn't see out. Set opacity **0.12**,
  lightened tint to pale glass (r0.08,g0.16,b0.22), recompiled. Windows are see-through now.
  (b) **RAMP — diagnosed, NOT changed:** open angle is **−26°**, which leaves the ramp tip ~19 cm above
  the apron (hinge world z≈192, apron deck ≈54 → 138 cm drop; ramp mesh ≈290 cm long). Geometry says it
  should be **≈−31°** to touch down. Could NOT change it cleanly: the value lives in **3 literal nodes**
  (`K2Node_CallFunction_109/268/423`, "Make Literal", Value=−26) feeding the ramp `Select` in
  `BP_SYL_Ship`; `set_pin_value` couldn't target those pins, and a full `read_graph_dsl`→`write_graph_dsl`
  rewrite is **blocked** because the read shorthand `(|SetbPilotSeated …)` for custom Blueprint variables
  is not write-parseable. **Left Codex's graph UNTOUCHED and verified intact** (boarding still works).
  Walkable for now (MaxStepHeight 55 steps the 19 cm lip).
  **>> TODO for Codex (graph author): change ramp open pitch −26 → −31** (the 3 literal nodes, or re-emit
  the Tick graph). Trivial in a Codex session since it owns the graph's variable handling.

- **2026-06-18 — Cockpit windscreen fix (Builder: Claude).** Jaron: "still can't see out the windows…
  two layers, something behind the glass." Root cause (diagnosed by capturing from the pilot eye @
  world≈(4910,0,300)): the glass was authored at **z 2.52–3.02 m (roof height)** while the pilot eye is
  ~1.7 m, and a solid **nose cap** (`box (6.3,0,1.33) size (.35,2.9,1.35)`) filled the forward view at eye
  level — so the window was a thin ceiling slit. Fix: in `_authoring/make_walkable_gunship.py` lowered the
  nose cap (now `(6.3,0,0.86) size (.35,2.9,.66)`) and rebuilt the glass as a **large raked windscreen at
  eye level** (two wedges, x 4.45–6.28, z 1.15→2.6/2.0). Regenerated Exterior+Glass FBX, **deleted + re-
  imported** them (import_file won't overwrite) — that nulled the mesh refs, so **re-linked StaticMesh on
  both the placed instance AND the BP class** components (`Exterior_GEN_VARIABLE`, `Glass_GEN_VARIABLE`),
  recompiled. Pilot-eye capture now shows sky through the windscreen. (The earlier glass-material opacity
  tweak 0.38→0.12 was a red herring but is kept — clearer glass.) **Jaron to confirm from the seat in PIE.**
  NOTE on pipeline: to revise a Codex/other mesh, edit its `_authoring/make_*.py`, re-run, then DELETE the
  old asset before re-import (import_file errors on existing) and RE-LINK refs on instance + BP class.

- **2026-06-18 — Windscreen/material recovery + ramp touchdown (Builder: Codex).** Resumed at Claude's
  request-limit failure. The Exterior and Glass re-imports had `WorldGridMaterial` in their only slots;
  restored `/Game/Curtis/Materials/M_Fortis_Steel` on `SM_Fortis_Gunship_Exterior` and
  `M_Fortis_Glass` on `SM_Fortis_Gunship_Glass`. Pilot-eye capture at (4910,0,300) now shows a broad,
  unobstructed forward view through the real windscreen; front-quarter capture confirms the glazing and
  steel exterior are both present. Completed Claude's measured ramp fix by safely round-tripping the
  single connected Tick graph (repairing the known boolean-accessor export shorthand first) and changing
  open pitch **−26° → −31°**. Blueprint compiled with warnings-as-errors. Five-second PIE regression:
  ship still settles level at ~(4500,0,138.36), rotation 0/0/0. Scratch evidence:
  `_codex_pilot_windscreen_fixed.png`, `_codex_windscreen_front_fixed.png` (gitignored).

- **2026-06-19 — Physical interaction panels (Builder: Codex).** Completed the next living TODO without
  adding screen-space UI or possession shortcuts. Authored a real four-fastener armored panel kit in
  `_authoring/make_interaction_panel.py`, with separate steel housing, emissive lens, and raised Blender
  geometry for `E  RAMP` / `E  PILOT`; imported the four meshes under
  `/Game/Curtis/Meshes/Gunship/Interaction`. Added door and seat panel components to `BP_SYL_Ship` and
  extended its existing proximity state so each lens and physical label is visible only when the same
  player body is within the real interaction radius and not seated. The labels sit in a separate lower
  row from the lens after visual QA. Blueprint compiled with warnings-as-errors. Combined PIE tests passed
  both reciprocal states (door on/seat off, then door off/seat on); the ship still settled after 5+ seconds
  at ~(4500,0,138.36), rotation 0/0/0. Forced a clean level unload/reload and verified the saved World
  Partition ship reconstructed with both prompt meshes, correct transforms, and hidden defaults. Scratch
  evidence: `_codex_physical_ramp_prompt.png`, `_codex_physical_pilot_prompt.png` (gitignored).

- **2026-06-19 — Pilot camera system + look/steer decouple (Builder: Claude).** From Jaron's first flight
  test: while seated the arrow keys fought over BOTH his head-look (BP_SYL_Player) AND the ship yaw/pitch
  (BP_SYL_Ship), so his view spun while the ship barely turned; and with the bare apron/void there was no
  way to tell he was moving or turning. Fixes, all structural (no screen UI, no possession swap):
  (1) **First/third-person ship cameras.** Reused the pre-existing unused `ChaseCam` CameraComponent
  (parented to `Hull`, rel (-1300,0,480) pitch -12, FOV 90 — third-person chase) and authored a new
  `CockpitCam` CameraComponent parented to `SeatAnchor` at rel (10,0,64) FOV 95 (seated eye, faces +X
  through the windscreen). `CockpitCam.bAutoActivate=true`, `ChaseCam.bAutoActivate=false`.
  (2) **View-target switching** via `Game|Player|SetViewTargetwithBlend` (0.25 s Cubic): sitting blends the
  player camera → the ship actor (uses its active camera component); standing blends back to the player
  body. Because both ship cams ignore controller rotation and rigidly follow the Hull, the pilot now SEES
  the ship bank/yaw (cockpit turns with it; chase shows the whole hull turning) — fixing "is my ship
  actually turning / am I moving."
  (3) **`C` toggles first/third person** while seated (latched on `bViewLatch`): flips new bool
  `bThirdPerson` and `Components|Activation|SetActive` on the two cams (exactly one active at a time).
  (4) **Head-look no longer fights the ship.** BP_SYL_Player EventTick now gates ALL on-foot input
  (WASD/arrows/jump) behind `Utilities|IsValid(GetAttachParentActor)=invalid` — i.e. it only runs when the
  body is NOT attached to the ship. While seated the body is attached to `SeatAnchor`, so arrows drive ONLY
  the ship; control rotation freezes at the sit pose, so standing back up faces a sane direction.
  New ship vars: `bThirdPerson`, `bViewLatch`. Both Blueprints compiled with warnings-as-errors. 5 s PIE
  regression: ship still settles level at (4500,0,138.36), rotation 0/0/0 — no physics regression from the
  added (non-colliding) cameras. **Jaron to feel-test:** board, fly, and press **C** to swap first/third
  person; confirm arrows now steer the ship cleanly without the head spinning. NOTE: the open-space "void"
  (no motion reference once away from the outpost) is inherent until the real space arc adds stars/planets;
  near home the chase cam against the apron/outpost now gives clear motion reference. Minor known edge: if
  you release `C` while standing, the next sit needs one throwaway `C` press to re-arm the latch.

- **2026-06-19 — Pilot camera/roll follow-up from Jaron's feel-test (Builder: Claude).** Jaron flew the
  new system and reported: (a) seated first-person, a big object blocked the view + the `E PILOT` panel was
  in frame; (b) no way to re-level after tilting sideways. Diagnosis via edit-mode `CaptureViewport` from
  the cockpit pose: the seat-eye pose itself was clear, so the blocker is the **pilot's own character body**
  (only present in PIE, attached at `SeatAnchor`). Fixes: (1) Moved `CockpitCam` forward to the canopy —
  rel-to-SeatAnchor (55,0,48), pitch -6, FOV 95 (world ~(4965,0,296) with ship at (4500,0,130)). A probe
  capture from there shows a wide, clean windscreen view (sky fills the frame, console glow at the bottom);
  being forward of the body, the pilot mesh and the seat panel now sit behind the camera. (2) Added **roll
  on A/D** (previously unbound while seated) — `AddTorqueInDegrees` ±90 about the hull forward vector — so
  the pilot now has full 3-axis attitude control and can recover from any tilt. Ship compiled
  warnings-as-errors; 5 s PIE settle unchanged at (4500,0,138.36) 0/0/0. **Seated flight controls now:**
  W/S thrust fwd/back, Space/LeftCtrl up/down, Left/Right yaw, Up/Down pitch, **A/D roll**, **C** first/third
  person, E stand. NOTE: manual re-leveling in open space is still real-hard (no global \"up\"); if Jaron
  wants it easier, next pass can add a realistic reaction-wheel \"stabilize\" key (damp angular velocity /
  hold-to-level near gravity) — flagged, not yet built.

- **2026-06-19 — Cockpit-view root cause: stale instance override (Builder: Claude).** Jaron's 2nd shot
  still showed a gray wall (sky only a thin top strip) — the "eye below the windscreen" symptom, NOT the
  body. Root cause: the **placed World Partition ship instance** carried a per-instance override on
  `CockpitCam.RelativeLocation = (0,0,0)` that shadowed the Blueprint template; worse, the instance would
  not accept a `z` override (set x=55 stuck, z=48 reverted to 0; `reset_properties` dropped to class
  default (0,0,0), not the SCS template). So every prior camera reposition only touched the template and
  never moved the actual in-level/PIE camera — it sat at the seat base, below the glass. **Robust fix:**
  drive the camera into place in `BP_SYL_Ship` BeginPlay — `SetRelativeLocation (55,0,48)` +
  `SetRelativeRotation (pitch -6)` on `CockpitCam` — so it's forced to the canopy pose at runtime
  regardless of instance/template drift (and any future instance is correct). PIE-verified: cockpit cam
  reads (55,0,48)/pitch -6 after BeginPlay; edit capture from that world pose (4965,0,296) shows a clean
  wide windscreen (sky fills the frame, console glow at bottom — scratch `_cockpit_fixed.png`). Ship still
  settles (4500,0,138.36) 0/0/0. **Lesson for both agents:** to move a component on an already-placed
  OFPA/World-Partition actor, editing the BP template or the instance property may silently fail — drive
  it in BeginPlay (or re-place the instance). Verify the LIVE/PIE component value, not just the template.

- **2026-06-19 — Mouse-look on foot (Builder: Claude).** Jaron chose controls-polish as the next lane
  (he'll route the planet + home-base arcs to Codex; the planet must exist before base design — see memory
  `syl-build-direction`). Added first-person **mouse-look** to `BP_SYL_Player` EventTick: one
  `Game|Player|GetInputMouseDelta` node, `DeltaX → AddControllerYawInput`, `DeltaY → AddControllerPitchInput`,
  inside the existing not-seated gate (so it's off while piloting). Used the DSL multi-output bind
  `(bind (_dx _dy) ...)`; the read-back export is lossy (re-inlines it) so I verified the real wiring with
  `get_connected_subgraph`: DeltaX→Yaw.Val, DeltaY→Pitch.Val (correct). Arrow-key look + WASD + jump all
  preserved. Compiled warnings-as-errors. **Jaron to feel-test:** mouse should turn the head on foot;
  report if pitch is inverted (one-sign flip) or sensitivity needs scaling — both are quick tunables.
  NOTE: this is mouse-look via the existing polling architecture (the felt win). A full **Enhanced Input
  asset migration** (IA_/IMC_ assets, EnhancedInputAction events, ship-input rebind) remains a larger
  follow-up if desired; the SYL project currently has only Variant_* input assets, no IA_Move/IA_Look/IMC.

## ⭐ Design law (Jaron, 2026-06-18): RELATE TO REALITY 100%, ALWAYS — even if it means going
## above and beyond / taking longer. Do NOT default to fake/shortcut approaches that break realism.
## Applies to the space arc: aim for the REAL thing (round planets w/ radial gravity, true scale,
## real flight/orbit via UE5 Large World Coordinates), not a flat zone + planet-as-a-distant-sphere
## fake. Stage it as real systems built incrementally, never as placeholders that cheat reality.

## Next up (living TODO — keep current)
1. **Jaron re-test the cockpit view + roll** (2026-06-19 follow-up): seated first-person should now look
   cleanly out the windscreen (no body/panel blocking); **A/D roll** should let you flip back upright after
   a tilt. Report if the canopy cam height/angle is good and whether manual leveling needs a stabilize
   assist. ChaseCam (press **C**) distance/angle feedback still welcome.
2. Tune cockpit first-person flight feel with Jaron: thrust, pitch/yaw authority, camera position, and
   landing response. Add roll/strafe only as physically supported controls. (Tunable magnitudes live in
   BP_SYL_Ship EventTick: thrust 2000/-1500, lift ±1900/-1100, yaw ±140, pitch ±95; cam FOV/offsets on
   CockpitCam/ChaseCam.) Optional: add camera lag on ChaseCam (SpringArm) and a free-look modifier key.
3. Mouse-look on foot is DONE (polling-based). Remaining input polish: tune mouse sensitivity / pitch sign
   with Jaron; optionally migrate to full Enhanced Input assets (IA_/IMC_) and rebind ship flight to it,
   preserving the same body/seat/ship state model. (Per Jaron 2026-06-19, planet + home arcs go to Codex.)
4. Continue the real space arc: atmosphere transition, LWC true-scale travel/orbit, radial gravity and
   round planets. Build small→full in real units—never a flat-zone or sky-sphere fake.
5. Secondary world work: roads/ground detailing, walkable building interiors, construction animation,
   station district, physical needs/health, hostile incursion loop.

## Signature
A small easter egg is placed in-world per Jaron's blessing: a dedication monolith reading
**"MADE BY CLAUDE CODE"** near the outpost entrance. Keep such marks tasteful and physical (on-canon
as built objects, never UI chrome).

## Repository (2026-06-18)
Version-controlled and backed up to GitHub — **PUBLIC** repo (open source, per Jaron)
**https://github.com/JaronKBragg7337/SpaceYouLand** (account JaronKBragg7337, default branch `main`).
Auth via `gh` (token in OS keyring — never paste secrets in chat; use `gh auth login` device flow).
`.gitignore` excludes `Intermediate/ Saved/ DerivedDataCache/ Binaries/ .claude/` and authoring
scratch (`_authoring/*.fbx|*.log`, root `_*.png`); **Git LFS** tracks `*.uasset *.umap *.ubulk *.uexp`.
To push future work: `git add -A && git commit -m "…" && git push`. Repo is PUBLIC / open-source — never commit secrets, personal data, or anything not world-safe.
`Config/DefaultEngine.ini` holds a UE-generated `SecurityToken` (project-local, not an external
credential — harmless in a public repo).
