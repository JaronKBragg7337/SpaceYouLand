# SYL — Build Log

> **Read this first if you're a fresh session.** This is the running record of what's been
> built in-engine and how. Pair it with `SYL_FirstPlayable_Plan.md` (older, partly off-canon)
> and the canonical design docs in Google Drive (folder **Space-You-Land (2026-2027)**).
> Persistent memory (`~/.claude/projects/.../memory/MEMORY.md`) holds the project reframe,
> the Drive doc IDs, the toolchain, and how Jaron wants to work. Load those before building.

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

## Next up (living TODO — keep current)
- Optional FP polish: mouse-look + Enhanced Input migration (see earlier note).
- World-fill: ground/road detailing (walkways/markings inside compound); a walkable building interior
  (ties to SYL "ships/stations are places"); antennae/comms dishes; fuel drums near the gunship.
- Consider: small interaction prompt when the player nears the gunship (exploration beat).
- Author from-scratch modular armored building to replace the cube buildings (task #9).
- Author from-scratch Fortis gunship for the landing pad (task #10).
- Later: animate/stage construction over time; walkable ship interior; a station district; needs/health;
  a hostile incursion loop.

## Signature
A small easter egg is placed in-world per Jaron's blessing: a dedication monolith reading
**"MADE BY CLAUDE CODE"** near the outpost entrance. Keep such marks tasteful and physical (on-canon
as built objects, never UI chrome).

## Repository (2026-06-18)
Version-controlled and backed up to GitHub — **private** repo
**https://github.com/JaronKBragg7337/SpaceYouLand** (account JaronKBragg7337, default branch `main`).
Auth via `gh` (token in OS keyring — never paste secrets in chat; use `gh auth login` device flow).
`.gitignore` excludes `Intermediate/ Saved/ DerivedDataCache/ Binaries/ .claude/` and authoring
scratch (`_authoring/*.fbx|*.log`, root `_*.png`); **Git LFS** tracks `*.uasset *.umap *.ubulk *.uexp`.
To push future work: `git add -A && git commit -m "…" && git push`. Keep the repo private until Jaron
chooses to make it public. Never commit secrets — `Config/DefaultEngine.ini` holds a UE-generated
`SecurityToken` (project-local, not an external credential; fine in a private repo).
