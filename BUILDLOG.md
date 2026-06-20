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

- **2026-06-19 — True-scale world body + radial ship gravity (Builder: Codex).** Began the real
  planet/space lane after Jaron confirmed controls are good until there are destinations. Authored a
  reusable one-metre-radius, 256×128 smooth unit geoid from scratch in Blender
  (`_authoring/make_celestial_body.py`) and imported it as
  `/Game/Curtis/Meshes/Celestial/SM_SYL_UnitGeoid`, with the new physically rough
  `/Game/Curtis/Materials/Celestial/M_SYL_World_Surface`. Created the data-driven actor
  `/Game/Curtis/Blueprints/World/BP_SYL_CelestialWorld` with editable body name, radius, surface
  gravity, atmosphere height, sidereal rotation, and axial tilt. Placed `SYL_ReferenceWorld_01` at
  **(0,0,-636,000,000 cm)** with **6,360,000 m radius**, exactly matching the existing Unreal
  SkyAtmosphere's real 6,360 km bottom radius and 60 km atmosphere. The body is non-spatially-loaded
  so its geoid/gravity source remains present across World Partition cells.

  Added `GravityBody` to `BP_SYL_Ship` and assigned the placed world actor. When valid, BeginPlay
  disables Chaos's global-down gravity on the Hull; Tick applies acceleration-change force toward the
  body's live actor center using **g(r) = 9.80665 × (6,360,000 m / r)^2**, reading radius and surface
  acceleration from the body actor. If no body is assigned, the old global gravity remains as a safe
  fallback. Blueprint compiled warnings-as-errors. Six-second PIE regression: ship still settled at
  ~(4500,0,138.36147), exact rotation 0/0/0. A second PIE test temporarily placed it 100 km off the
  north-axis tangent; displacement was (-0.683,0,-43.416) cm with **1.0 cosine alignment** to the
  world center, proving gravity is radial rather than disguised global -Z. Orbital capture shows the
  true curved geoid/atmospheric limb (`_codex_reference_world_orbit_north.png`, gitignored scratch).
  The geoid intentionally has no monolithic collision: current Fortis structures remain on their real
  authored foundations, while curvature-conforming streamed terrain/collision is the next layer.

- **2026-06-19 — First remote surface destination (Builder: Codex).** Built the first real place to
  fly **to and from**, directly along the gunship's existing +X heading. Authored from scratch in
  `_authoring/make_remote_surface_site.py`: (1) a 2×2 km spherical terrain cap whose vertices use the
  exact local equation `z = sqrt(R²-x²-y²)-R` for the 6,360 km body, with a closed coarse UCX collision
  cap; and (2) an 80×80 m steel landing deck with physical supports, raised emissive edge/cross
  markings, an armored survey shelter, and a 45 m truss navigation tower with modeled beacon lens and
  UCX collision. Assets:
  `/Game/Curtis/Meshes/Celestial/SurfaceSites/SM_SYL_RemoteTerrainPatch_01` and
  `SM_SYL_RemoteLandingSite_01`. Terrain is 4,225 vertices / 8,192 triangles; infrastructure is 2,328
  vertices / 1,184 triangles.

  Created data-driven `/Game/Curtis/Blueprints/World/BP_SYL_SurfaceSite` (site name, arc distance,
  bearing, planet radius), containing the terrain, infrastructure, a real inverse-square tower beacon,
  and four inverse-square red pad lamps tied physically to the raised red corner markings. Placed
  `SYL_SurfaceSite_A01` at **2,000 m arc distance along +X**: world
  **(199,999.9967, 0, -31.4465 cm)**, pitch **−0.01801754°**, so its local up is the world's radial
  normal rather than global +Z. It remains a normal spatially-loaded World Partition actor.

  Collision proof: a radial trace over the deck hit at 9,769 cm from a 100 m start; a trace 500 m
  off-center hit the curved terrain at 4,999.9917 cm vs 5,000 cm expected. Touchdown proof: temporarily
  placed the real gunship above the remote pad and let radial gravity settle for 6 s; it stopped at
  **287.0 cm radial altitude**, only **0.009 cm tangential offset**, pitch −0.018039° vs site
  −0.018018°. Restored the saved ship home at (4500,0,130); five-second home PIE still settles at
  ~(4500,0,138.36147), 0/0/0. Checkpoint `_codex_remote_surface_site_pad.png` (gitignored) shows the
  illuminated physical deck. **Player route:** launch from the apron and fly straight +X/W for ~1.95 km;
  acquire the 45 m red beacon, then land on the lit square pad. Jaron's round-trip will now reveal the
  first real cruise-speed, beacon-range, approach, and landing-feel requirements.

- **2026-06-19 — Planet is now landable on foot (Builder: Claude).** Jaron's planet test: on foot he fell
  straight THROUGH the planet (and Codex's route assumed he was flying). Cause: the geoid mesh
  `SM_SYL_UnitGeoid` (1 m UV-sphere scaled ~6.36e6× by `BP_SYL_CelestialWorld`) had **no collision
  geometry**, so character capsule sweeps (which hit *simple* collision only) passed through — even though
  the `Geoid` component was already `QueryAndPhysics` / `BlockAllDynamic`. Fix: `generate_convex_collisions`
  on `SM_SYL_UnitGeoid` (1 hull, 64 verts) — a convex hull of a sphere is standable from outside, and over
  the ~2 km test region the surface is effectively flat (drop ≈ d²/2r). PIE proof: spawned the player 30 m
  up over open planet at (100000,0,3000); after 5 s it **rested at z≈81.8 cm with zero lateral drift** (no
  fall-through, no sliding). Home/outpost unaffected (its decks sit above the geoid at z≈0). This is a
  stopgap so Jaron can land/walk/test now; Codex's streamed curved terrain remains the proper surface.
  **Still open for Codex:** planet *surface color/material* — the gray geoid is hard to tell from the
  sun/sky; add land/water-style color variation so the surface reads and gives navigation landmarks.

- **2026-06-19 — ⚠️ ISSUE FOR CODEX: platforms not unified with the planet surface (found by Jaron + Claude).**
  Jaron flew the planet and reported it "looks like random platforms with a separate planet layer above
  them," only the beacons poking through. Root cause (confirmed from the authoring scripts, not yet
  measured live — Claude had no editor session): there are **three inconsistent "surfaces"** that don't
  share a height:
  1. **Global geoid** (`SM_SYL_UnitGeoid` via `BP_SYL_CelestialWorld`) is a **256×128 UV sphere** scaled to
     6,360 km. At that resolution the flat facets deviate from the true sphere by **tens of meters** within
     the first ~2 km of the pole (origin). Rough math: the coarse facet from the pole vertex (z=0) to the
     first ring (~155 km out) interpolates to ≈ **−24 m at 2 km horizontal**, whereas the true surface is
     ≈ −0.3 m there. So the *visible* near-field planet is NOT at the true surface height.
  2. **Home Fortis outpost** is the original **flat-world** foundation (z≈0–52), never re-seated onto a
     curved planet patch. It just sits at its legacy height.
  3. **Remote site** (`make_remote_surface_site.py`) has its **own** accurate curvature-correct terrain cap
     (`spherical_height()`), independent of the global geoid.
  These three don't coincide → platforms read as detached from the planet shell. **Fix direction:** make ONE
  true surface everything sits on — seat the home outpost on a curvature-correct patch like the remote site,
  ensure geoid + patches + platform decks share the exact surface height at each location, and either raise
  the global geoid's near-field fidelity or use it only as the distant silhouette (accurate streamed patches
  carry the near field). Jaron's surface **color/material** (land/water landmarks) rides along with this.
  Claude's convex-collision stopgap (prior entry) lets you stand on the geoid meanwhile. NEXT MEASUREMENT:
  open editor, read world Z of the geoid surface vs apron deck (z≈52) vs remote deck to get exact gaps.

- **2026-06-19 — Unified true surface corridor + physical lithology (Builder: Codex).** Resolved the
  detached-platform issue with live measurements first: the coarse global geoid was only −0.57 m near
  the apron but **−28.59 m** beside the remote site, while the accurate remote terrain was −0.33 m.
  Authored `_authoring/make_surface_corridor.py` and two neighboring 2×4 km streamed tiles on the same
  6,360 km sphere: `SM_SYL_SurfaceTile_Home_02` at the home tangent origin and
  `SM_SYL_SurfaceTile_Remote_02` at the existing site's exact 2 km arc transform. They meet at x=1 km;
  post-reload traces on both sides of the seam matched the analytic sphere within **0.025 cm**. Home and
  remote open-surface traces were within 0.025 cm and 0.018 cm respectively.

  Added three from-scratch, physically rough lithology materials—`M_SYL_Terrain_Basalt`,
  `M_SYL_Terrain_IronRich`, and `M_SYL_Terrain_PaleSilicate`—and encoded a deterministic metre-space
  mineral field as FBX material sections, giving real navigation-scale color regions without pretending
  painted ground is water. The home tile is a saved World Partition actor; `BP_SYL_SurfaceSite` now uses
  the matching remote tile. Removed Claude's temporary convex collision from `SM_SYL_UnitGeoid`; the
  coarse geoid is again only the always-loaded distant/orbital silhouette, while streamed true-surface
  tiles own playable collision. Outside the corridor now correctly returns no terrain hit instead of a
  false surface tens of metres away.

  Verification: clean level reload reconstructed both tiles and the remote Blueprint mesh reference;
  six-second PIE left the gunship at **(4500.000007, 0, 138.361473)** with exact 0/0/0 rotation and the
  player resting at home z=140.15. Home, seam, and remote traces remained valid in PIE; outside-corridor
  trace remained null. Close visual QA (`_codex_unified_surface_remote_close_final.png`, gitignored)
  shows the lit 80 m deck physically seated on pale terrain with its supports/shelter intact. Material
  automation gotcha: UE 5.8 crashed in `MaterialEditor` when `MaterialTools.recompile` was called after
  graph edits; recovery was clean. Add/connect nodes, save the dirtied package, and let normal shader
  compilation run—checkpoint before any explicit recompile.

- **2026-06-19 — One visible + physical planet surface; removed the stacked-layer read (Builder: Codex).**
  Jaron's three flight screenshots proved the prior corridor fix solved local collision heights but not
  the planet's visual LOD: the brown pass-through layer was the coarse `SM_SYL_UnitGeoid`; the dark giant
  rectangles were the exact 2×4 km home/remote tiles; from below the coarse shell the real sites appeared
  to float in open space. The tiles were mathematically correct but visually finite, while the geoid's
  first pole facet spanned ~156 km and sat tens of metres away near the sites.

  Authored `_authoring/make_planet_nearfield_cap.py` and imported
  `/Game/Curtis/Meshes/Celestial/SurfaceLOD/SM_SYL_NorthPolarCap_01`: a true 6,360 km-radius spherical
  cap with 65,537 vertices / 130,816 triangles. It replaces the entire coarse north-pole facet out to
  the geoid's real first ring (**156.082 km radius, −1.916 km edge height**); the outer 256 vertices are
  derived from Blender's actual unit-geoid ring so the LOD closes at the same geometry. The cap is
  non-spatially-loaded and uses the exact same `M_SYL_World_Surface` material as the global geoid on all
  sections, eliminating the circular material/platform boundary at altitude. The former home/remote
  tile components are now hidden in rendering (their exact collision remains as local backup), so there
  are no visible rectangular shelves.

  Made the cap itself physical with `BodySetup.CollisionTraceFlag = CTF_UseComplexAsSimple`, double-sided
  static collision, and `BlockAll`. Decisive PIE proof spawned the player 30 m above **(2000 m, 2200 m)**,
  outside both former tile bounds: analytic spherical surface z was −69.4969 cm and the player settled at
  z=20.3694 cm (surface + capsule), rather than falling through. At the same time the gunship remained at
  **(4500.000007, 0, 138.361473)** with exact 0/0/0 rotation. Visual QA:
  `_codex_planet_cap_remote_close.png` shows the beacon deck directly on continuous terrain;
  `_codex_planet_cap_high_continuous.png` shows no cap/geoid layer boundary at 5 km-scale altitude; and
  `_codex_planet_true_orbit.png` shows the real round globe/day-night limb from orbital distance. Reality
  note: a 6,360 km-radius body correctly looks nearly flat from only a few kilometres up; roundness becomes
  obvious at orbital distance, but separate shells/platform sheets must never appear.

- **2026-06-19 — Independent verification of the planet state at 5cb310f (Builder: Claude).** Claude now
  owns the planet fix (Codex out of usage). Measured the LIVE saved geometry directly (PIE):
  `BP_SYL_CelestialWorld` is at location (0,0,−636,000,000), scale 6,360,000 → radius 636,000,000 cm, **apex
  z=0**, and `bIsSpatiallyLoaded=false` (always loaded). The cap (`SYL_NorthPolarCap_01`) top is also **z=0**.
  So geoid and cap are **concentric, same radius, coincident at the pole — effectively one sphere**, both
  always-loaded (no streaming flicker). Bases sit on it: home foundation at the z≈0 surface (apron is a
  ~54 cm raised deck by design); remote deck at z≈−31 cm = the cap's true height there; open ground 1 km out
  traces to −7.86 cm (true sphere). **Acceptance tests PASS on the saved state:** (1) capture from 2.5 km
  out / 800 m up = one continuous surface to the horizon, no stacked layers; (2) capture looking straight up
  from open ground = only sky, no ceiling/second shell. So the "two stacked layers / fly through a layer"
  Jaron reported is NOT present in the final saved 5cb310f geometry — most likely he saw a MID-WORK state
  during Codex's many incremental commits. CAVEAT: static god-cam captures can't fully replicate live flight;
  if Jaron still sees layering on a FRESH test, capture his exact camera pose/altitude and chase it there.
  STILL OPEN (real): surface is uniform brown — the color/landmark/navigation request is unaddressed.

- **2026-06-19 — "Two layers" at the remote site DIAGNOSED: it is NOT geometry (Builder: Claude).** Jaron's
  decisive screenshots (above the remote tower → only the lit tip shows, everything below "covered by a brown
  layer"; at the tower base looking up → clear sky) localized the issue to the REMOTE site (2 km out), not
  home. Measured live in PIE: a straight-down trace at the tower hits the cap at **−28.3 cm** (true sphere,
  solid) and finds **NO collision geometry up high**; the coarse geoid and cap are concentric (apex z=0) and
  the geoid sits *below* the cap out there. So there is **no second shell** — the structural planet is one
  unified, solid surface and the bases sit on it. The "brown layer" is VISUAL: (1) `ExponentialHeightFog` was
  `FogMaxOpacity=1.0`, `FogHeightFalloff=0.2`, density 0.035 — i.e. it could become FULLY opaque and reached
  high, so looking *down* across distance it's a solid brown wall (tall tips poke through) while looking *up*
  it's clear; softened to density 0.015 / falloff 1.0 / MaxOpacity 0.5 (saved). (2) The bigger cause: the
  surface uses one **dark, untextured brown material** (`M_SYL_World_Surface`), so from altitude the ground,
  haze, and the dark tower truss all blend into an ambiguous brown mass — reducing fog alone did NOT reveal
  the tower, confirming the flat dark surface is the main culprit. **THE REAL FIX (next, was always open):
  give the planet surface real color/lightness/variation (land/water-style)** so it reads as terrain with
  landmarks; that dissolves the "layer" illusion. Apply via the shared `M_SYL_World_Surface` (cap + geoid use
  it) so one shader changes the whole planet — forward-compatible per the multi-planet vision.

- **2026-06-19 — Planet surface material: dark void → visible varied terrain (Builder: Claude).** Confirmed
  the "brown layer hiding the sites" is the SURFACE itself: `M_SYL_World_Surface` (shared by cap + geoid) was
  a flat near-black color **(0.045, 0.06, 0.07)** with no variation, so from the air everything read as a
  dark murk and dark buildings vanished. Even with fog turned nearly off, the site stayed an unreadable void
  — proving the material, not fog, was the cause. Rebuilt the material (carefully, recompiled once — Codex had
  crashed the Material Editor here): base color → warm rock **(0.37,0.26,0.17)**; added a second tone
  **(0.20,0.14,0.10)** and a `MaterialExpressionNoise` (Scale 0.00003 ≈ few-hundred-metre features, Levels 3,
  output 0–1) feeding a `LinearInterpolate` into BaseColor — so the planet now has lighter/darker rocky
  variation (navigation landmarks). Verified in PIE: surface is a visible warm rock field with large-scale
  variation instead of a black void. One shader repaints the whole planet (cap + geoid) and every future
  planet — forward-compatible per the solar-system vision. NOTE on captures: god-cam captures 2 km from the
  PIE player do NOT stream the remote site geometry (WP streams around the player), so far captures show only
  the always-loaded surface; the site renders normally when the player flies there. Fog also softened earlier
  (MaxOpacity 1.0→0.5, density→0.015, falloff→1.0). **Jaron to fly out and confirm: planet reads as terrain,
  not a brown layer, and the beacon/site are findable.** Tunable: terrain colors, noise scale, fog.

- **2026-06-19 — Real cause of "can't see the base from high": World Partition LOD culling (Builder: Claude).**
  Jaron: before the planet he could fly high and see the Fortis base; now a "brown layer" hides it. Measured:
  from a god-cam **45 m** straight down the full outpost (walls, towers, lights, courtyard) renders crystal
  clear; from **140 m** straight down it's GONE — only the orange surface shows — and cutting fog hard
  (density 0.005, MaxOpacity 0.3) did NOT bring it back. So it's not fog and not a geometry shell: the
  detailed structure meshes **cull/LOD out past ~100 m view distance** while the always-loaded planet
  surface (cap/geoid) keeps rendering. That is the "brown layer with nothing on it" from altitude — the
  ground stays, the buildings vanish. Before the planet there was no ground, so the culled-out base just
  read as empty sky; now the ground is there, so it reads as a covering layer. **NEXT TASK (clean, scoped):
  keep key structures visible at distance** — generate World Partition HLOD proxies and/or raise the
  outpost/site/beacon mesh draw distances (and consider Nanite on the bespoke meshes) so you can see where
  to fly from the air, not just from <100 m. Beacons (tall, emissive) already show from high and remain the
  primary far-navigation marker. Fog left light for atmosphere + visibility (density 0.006/falloff 1.4/
  MaxOpacity 0.35). Surface color/variation from the prior entry stands.

- **2026-06-20 — PROVEN root cause of the "layer": structures are DRAW-DISTANCE culled (Builder: Claude).**
  Definitive evidence via `CaptureViewport` with annotations from 140 m straight up over home: it labeled
  **30 actors in-frustum** (outpost StaticMeshActors at z=0–9.6 m + their PointLights, all ~132–140 m from
  camera) — yet the rendered image showed **none of them**, only the orange surface. Loaded + in-frustum +
  not drawn = **max-draw-distance / screen-size culling**, NOT fog (proven: fog fully off still hid them),
  NOT a geometry shell (trace finds nothing solid above; geoid/cap apex both z=0), NOT WP cell-unload (actors
  are loaded), NOT a Cull Distance Volume (none in level), NOT a config cvar (`Config/` unchanged since the
  initial commit). The beacon stays visible from any height because **lights/emissive have effectively
  unlimited draw distance** while solid meshes cull — that's why only the glowing tip "pokes through." So
  Jaron is right: it IS removable. **FIX (next): clear the structures' max draw distance** (set
  `LDMaxDrawDistance = 0` on the Fortis outpost + site StaticMeshComponents — ideally batch via
  ProgrammaticToolset across the level), and/or enable Nanite on the bespoke structure meshes so they render
  at all distances. Then re-verify with a 140 m labeled capture: the structures should render. The surface
  color/variation and fog work from prior entries stand; this is the remaining piece for "see the buildings
  when you fly in."

- **2026-06-20 — Clean-slate celestial wipe completed (Builder: Codex).** Preserved Fortis, the development
  apron, the walkable gunship/player Blueprints, all gunship meshes/materials, and every `_authoring/make_*.py`.
  Removed the four live experiment actors (`SYL_ReferenceWorld_01`, `SYL_NorthPolarCap_01`,
  `SYL_SurfaceTile_Home_01`, `SYL_SurfaceSite_A01`) and deleted the old `BP_SYL_CelestialWorld`,
  `BP_SYL_SurfaceSite`, all eight Celestial meshes, and all five Celestial materials. Asset-registry and
  scene re-enumeration found **zero** remaining celestial `SYL` actors/assets. The former home-open and
  remote-site downward traces both return null: the brown planet sheet—including the layer that appeared
  near the remote tower top—is physically gone, not hidden.

  Hardened 62 standalone Fortis/Claude StaticMeshComponents for aerial visibility:
  `LDMaxDrawDistance=0`, `MinDrawDistance=0`, `bNeverDistanceCull=true`, and
  `bAllowCullDistanceVolume=false`. A fresh 140 m labeled capture sees 80 scene actors and renders the
  Fortis/apron geometry with no planet surface covering it. Captures at the former 45 m tower band show
  empty space (only the atmospheric horizon remains); looking straight up from former open ground shows
  only sky. Evidence: `_codex_clean_slate_140m_labels.png`,
  `_codex_clean_slate_old_tower_height.png`, `_codex_clean_slate_look_up.png` (gitignored scratch).

  Deleting the old body class invalidated its typed nodes in `BP_SYL_Ship`; removed only the obsolete
  `GravityBody` variable, radius/surface-gravity getters, validity macros, and radial-force call at node
  level. BeginPlay now connects directly to `SetEnableGravity(true)` while the new reusable body interface
  is absent. Boarding, ramp/door, cameras, interaction prompts, and flight controls remain intact. The ship
  and player compile with warnings-as-errors. Restored the OFPA ship instance to its documented apron pose
  `(4500,0,130)`; after a clean level reload and six-second PIE it settled at
  **(4500.000000, ~0, 138.361473), rotation 0/0/0**.

- **2026-06-20 — True-scale Earth + Moon reference foundation (Builder: Codex).** Authored both body
  meshes from scratch in Blender with `_authoring/make_celestial_body.py`; no premade sphere asset is
  used. Imported one-metre unit meshes at
  `/Game/Curtis/Meshes/Celestial/Bodies/SM_SYL_UnitBody_EarthOpenNorth` and
  `SM_SYL_UnitBody_MoonFull`, then created reusable
  `/Game/Curtis/Blueprints/World/BP_SYL_CelestialBody`. Its 16 editable fields store body identity,
  parent, radii, mass, GM, rotation, axial tilt, orbit, atmosphere, surface-opening angle, and source
  revision in explicit km/kg/rad/s/hour units. The Blueprint compiles with warnings-as-errors.

  Placed `SYL_Earth_Reference_01` at `(0,0,-635675200 cm)`, scaled from the one-metre mesh to the
  WGS84/JPL ellipsoid radii **6378.137 km equatorial / 6356.752 km polar**. Placed
  `SYL_Moon_Reference_01` at `(38440000000,0,-635675200 cm)` with radius **1737.4 km**. Their measured
  center separation is exactly **38,440,000,000 cm = 384,400 km**. Both actors are always loaded and
  their distant shells are explicitly `NoCollision`, never distance-culled. Earth uses a precisely
  **1.40625° north-polar opening** (the last UV cap only) so the future one visible-and-physical local
  Earth surface can occupy the Fortis region without putting a second global shell beneath it; the Moon
  shell is complete. Mean-albedo reference materials are measured aggregate values, not fabricated
  geography: Earth 0.367, Moon 0.12.

  Source authority is NASA/JPL Horizons physical data: targets 399 (Earth, revised 2022-05-09) and 301
  (Moon, revised 2013-07-31). Stored values include Earth GM 398600.435436 km^3/s^2, mass
  5.97219e24 kg, sidereal period 23.9344695944 h, obliquity 23.4392911°; Moon GM 4902.800066 km^3/s^2,
  mass 7.349e22 kg, sidereal period 655.717968 h, orbital eccentricity 0.05490, and tilt 6.67°.
  Epic's UE 5.8 LWC documentation confirms 64-bit coordinates and an 88-million-km default world extent,
  so this remains the same project; no new template/project is needed for realistic planets.

  Clean-reload verification read every stored value and transform back correctly. Down-traces through
  the former brown layer at 1 km and 2 km remain null. A six-second PIE regression leaves the ship at
  `(4500.000000,~0,138.361473)`, exact rotation 0/0/0, proving the new non-colliding shells do not disturb
  the apron. Scratch evidence: `_codex_earth_true_scale_orbit.png`,
  `_codex_moon_true_scale_orbit.png`, `_codex_earth_moon_true_scale_system.png` (gitignored). This chunk
  establishes exact geometry + body data/reference frames; live inverse-square gravity and the single
  local physical Earth surface are deliberately the next coherent chunk, not claimed complete here.

## ⭐ Design law (Jaron, 2026-06-18): RELATE TO REALITY 100%, ALWAYS — even if it means going
## above and beyond / taking longer. Do NOT default to fake/shortcut approaches that break realism.
## Applies to the space arc: aim for the REAL thing (round planets w/ radial gravity, true scale,
## real flight/orbit via UE5 Large World Coordinates), not a flat zone + planet-as-a-distant-sphere
## fake. Stage it as real systems built incrementally, never as placeholders that cheat reality.

## Next up (living TODO — keep current)
1. **★ TOP PRIORITY (CODEX) — ONE PHYSICAL EARTH SURFACE + GENERIC GRAVITY.** The reusable true-scale Earth
   and Moon reference bodies now exist at real radii/separation with sourced data, but their shells are
   intentionally non-colliding and do not yet exert live force. Build exactly one visible-and-physical local
   Earth surface through the 1.40625° north opening; seat Fortis/apron/ship on it at a measured WGS84
   coordinate with radial up; make `BP_SYL_CelestialBody` the generic inverse-square gravity source; reconnect
   the ship and add radial character orientation. Never restore the old geoid/cap/tile stack.
2. **MEASURED ACCEPTANCE.** One down-trace surface (base and open ground agree), only sky looking up, no
   brown layer at the old tower band, Fortis rendered from 140 m, ship settles level under Earth gravity,
   and a far view shows round Earth + Moon. Then bind the atmosphere model to the same Earth data and extend
   into reference-frame-aware LWC travel/orbit.
3. Mouse-look on foot is DONE (polling-based), pitch set NON-inverted (mouse up = look up, FPS-standard;
   `AddControllerPitchInput(-DeltaY)`) per Jaron's test. Remaining input polish: tune mouse sensitivity
   with Jaron; optionally migrate to full Enhanced Input assets (IA_/IMC_) and rebind ship flight to it,
   preserving the same body/seat/ship state model. (Per Jaron 2026-06-19, planet + home arcs go to Codex.)
4. Secondary world work: roads/ground detailing, walkable building interiors, construction animation,
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
