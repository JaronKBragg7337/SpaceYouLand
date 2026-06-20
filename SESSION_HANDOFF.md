# SESSION_HANDOFF — operating manual for Claude, Codex, or a fresh session

> Read this to know exactly what the previous builder knew and could do. Pair with **BUILDLOG.md**
> (current state + history + "Next up") and the repo's **MEMORY.md**. These committed files are the
> shared state between Claude and Codex. `PASTE_INTO_NEW_CHAT.txt` points every new chat here.

## 0. Orientation order
1. **This file** — how to operate (tools, pipeline, gotchas).
2. **BUILDLOG.md** — what's built, conventions/coordinates, and the live **"Next up"** TODO.
3. **Shared memory** (`MEMORY.md`). Claude may also have private runtime memories (`realism-law`,
   `syl-endgame-intent`, `syl-project-reality`, `working-style-jaron`, `asset-pipeline-toolchain`,
   `syl-drive-docs`); use them when available, but commit durable state so every agent can see it.
4. **CLAUDE.md** — note its "Curtis lab / obstacle course" framing is a wrapper; the real project is
   **SYL (Space You Land)**, a 100%-realistic first-person space game (see memory).

## 1. What SYL is (one paragraph)
Persistent, first-person space game. **Design law: relate to reality 100%, no fakes** — real physics,
real gravity, walkable ships/stations, cargo/crew physical, "menus observe reality," "the world is
built not spawned." Long-term it's a precursor to real space-drone operation; planets→real planets,
factions→real governments later — so **build forward-compatible**: data-driven factions/planets, real
units. No premade assets — **everything is authored from scratch.** Current build: a walkable Fortis
outpost, a clear external vehicle-development apron, and a modular walkable real-physics gunship with
a physical pilot seat, pressure door, and ramp. Owner: Jaron.

**SYL is a REAL SOLAR SYSTEM — MULTIPLE planets people fly between (Jaron, 2026-06-19), eventually mapped to
our actual solar system.** Never build for "one planet." **★ BUILD-ORDER PRINCIPLE: the planet body is the
foundation — build/define the planet FIRST, then place every structure ON its surface** at the correct
spherical position with radial "up" (surface normal away from body center). ONE visible-and-physical surface
per location — never a near-field cap AND a coarse geoid both rendering as ground ("a planet inside the
planet"); the coarse geoid is only the distant silhouette. "Fixed" is MEASURED (down-traces at base and open
ground agree; looking straight up from open ground shows only sky), never declared from one framed capture.
The current planet height-mismatch came from authoring Fortis, the remote pad, and the planet in separate
sessions at different heights — do not repeat that. See MEMORY.md for the full statement.

## 2. Connect to Unreal — the build tools are DEFERRED (must be loaded)
- The `unreal-mcp` tools are NOT loaded by default. Load them with **ToolSearch** (query `unreal`, or
  `select:mcp__unreal-mcp__list_toolsets,mcp__unreal-mcp__describe_toolset,mcp__unreal-mcp__call_tool`).
- Server runs in **tool-search mode**: 3 meta-tools — `list_toolsets`, `describe_toolset(name)`,
  `call_tool(toolset_name, tool_name, arguments)`. **tool_name is the SHORT name** (no toolset prefix).
- Needs Unreal Editor OPEN with the MCP server on `http://127.0.0.1:8000/mcp` (auto-starts). If down:
  confirm the editor is open; `Test-NetConnection 127.0.0.1 -Port 8000`. Ask Jaron to open the project.
- If ToolSearch/unreal-mcp is not directly exposed (known Codex desktop case), use MCP JSON-RPC over
  local HTTP from PowerShell: initialize, send `notifications/initialized`, retain `Mcp-Session-Id`,
  then call the same meta-tools. This route is proven and does not require mouse automation.
- **Toolsets you'll use:** `SceneTools` (add/find/remove actors, folders, levels, add_to_scene_from_asset/
  _from_class), `ActorTools` (transforms, components, labels, get_root_component, set_parent_component),
  `ObjectTools` (get/set_properties, get_default_object CDO, search classes), `StaticMeshTools`
  (import_file, generate_convex_collisions, set_material), `MaterialTools` (create_material, expressions),
  `BlueprintTools` (create, write_graph_dsl, find_node_types, get_node_type_pins, compile), `EditorAppToolset`
  (StartPIE/StopPIE, CaptureViewport, camera), `AssetTools` (save_assets, find_assets).
- **`ProgrammaticToolset.execute_tool_script`** batches many tool calls inside ONE sandboxed python
  script via `execute_tool(name, json_str)`. USE IT to avoid overlapping calls and cut round-trips.
  (Call its `get_execution_environment` once for rules.) NEVER run overlapping Unreal tool calls.

## 3. From-scratch asset pipeline (Blender → UE) — PROVEN, reusable for ANY mesh
1. Write a Blender script in `_authoring/` (see existing `make_*.py`). Boxes via a bmesh helper;
   real cylinders via `bmesh.ops.create_cone`.
2. Export **FBX** — NOT glb (import_file only takes fbx/obj). Settings that work:
   `export_scene.fbx(filepath, use_selection=..., object_types={'MESH'}, apply_unit_scale=True,
   global_scale=1.0, axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')`. Model in **meters** →
   imports at correct cm (100x), Z-up preserved.
3. Run headless: `blender --background --python _authoring/<script>.py` (`blender` is on PATH; v5.1).
4. Import: `StaticMeshTools.import_file(folder_path='/Game/Curtis/Meshes', asset_name, source_file=<ABS .fbx>)`.
5. Place: `SceneTools.add_to_scene_from_asset`; material via component `OverrideMaterials`
   (`ObjectTools.set_properties` JSON `{"OverrideMaterials":["/Game/Curtis/Materials/M_x.M_x"]}`)
   or `StaticMeshTools.set_material`. Existing mats: `M_Fortis_Steel`, `M_Fortis_Red`, `M_Claude_Sign`.
- **UE 5.8 material gotcha:** an explicit `MaterialTools.recompile` immediately after programmatic graph
  edits crashed `MaterialEditor` with an access violation. Add/connect expressions, ensure an expression
  edit dirties the package, then `AssetTools.save_assets` and let normal shader compilation run. Commit
  before any explicit recompile attempt.

## 4. Viewport screenshots (IMPORTANT decode trick)
`EditorAppToolset.CaptureViewport` returns a base64 PNG **too big to inline**. Current MCP responses
place JSON in the first text content block; parse it, take `returnValue.image.data`, base64-decode,
write a `.png`, then inspect it. Older clients may save the same payload to a tool-result `.txt`:
```python
import json,base64,glob,os
f=max(glob.glob('<tool-results-dir>/mcp-unreal-mcp-call_tool-*.txt'),key=os.path.getmtime)
raw=open(f).read(); rv=json.loads(raw[raw.find('{'):])['returnValue']
rv=json.loads(rv) if isinstance(rv,str) else rv
open('out.png','wb').write(base64.b64decode(rv['image']['data']))
```
Pass an `annotations` object with every field present. Use zero values plus
`classFilter={refPath:"/Script/Engine.Actor"}` to disable overlays; the current server errors when the
object is omitted. `captureTransform: null` = current camera (verify world/pose during PIE).

## 5. Blueprints (scripting logic)
- `BlueprintTools.create(folder, name, asset_type={refPath:"/Script/Engine.Character|Pawn|GameModeBase"})`.
- Components via `ActorTools.add_component`; set defaults via `get_default_object` (CDO) + `ObjectTools.set_properties`.
  Make a mesh the physics root: `get_root_component(CDO)` then `set_parent_component(component=root, parent=mesh)`.
- Logic: `write_graph_dsl(graph={refPath:"<BP>:EventGraph"}, code)`. Get syntax from `get_graph_dsl_docs`.
  Discover node IDs with `find_node_types(filter)`, pins with `get_node_type_pins(type_id)`.
  Proven nodes: `Game|Player|IsInputKeyDown`, `Pawn|Input|AddMovementInput`, `Pawn|Input|AddController{Yaw,Pitch}Input`,
  `Physics|AddForce`, `Physics|AddTorqueinDegrees`, `Physics|SetSimulatePhysics`, `Variables|Default|Get<Component>`,
  `Transformation|GetActor{Forward,Right}Vector`, `Math|Vector|MakeVector`. FKeys pass as quoted names
  ("W","S","A","D","SpaceBar","LeftControl","Left","Right","Up","Down").
- Verify: `EditorAppToolset.StartPIE` → `SceneTools.find_actors` / `ActorTools.get_actor_transform` → `StopPIE`.
  You CANNOT simulate keypresses headlessly — Jaron tests flight/movement feel; magnitudes in the graph are tunables.
- `read_graph_dsl` currently exports Blueprint boolean accessors as invalid IDs such as
  `|GetbPilotSeated`. Before writing a read graph back, repair them to
  `Variables|Default|GetPilotSeated` / `SetPilotSeated` (same pattern for RampOpen/InteractLatch).
- Walkable-ship collision law: only flat `Hull` + four landing-pad boxes join the rigid body. Ramp,
  rear door, cabin walls, roof, and nose must be `SetCollisionEnabled QueryOnly` with
  `bAutoWeld=false`. Otherwise Chaos welds the cabin cage into the body and it parks nose-down.

## 6. Version control — auto-backup every meaningful change
- **PUBLIC** (open-source) GitHub repo: **github.com/JaronKBragg7337/SpaceYouLand**. `gh` is authed (token in OS keyring).
  Since it's public: never commit secrets or personal data; double-check before adding new file types.
- `git add -A && git commit -m "…" && git push` after each chunk. Attribute the actual builder only;
  BUILDLOG entries should say `Builder: Claude` or `Builder: Codex`. Git LFS tracks `*.uasset *.umap`.
- `.gitignore` excludes `Intermediate/ Saved/ DerivedDataCache/ Binaries/ .claude/` + authoring scratch.
- **NEVER** paste a token/secret in chat. If re-auth needed: `gh auth login` (device flow — Jaron approves in browser).

## 7. If a capability seems missing — don't assume; discover or build it
- Deferred tool? → `ToolSearch`. Unreal capability? → `list_toolsets` / `describe_toolset`. Blueprint node?
  → `find_node_types`. A mesh/prop that doesn't exist? → author it from scratch in Blender (§3). Game logic?
  → build it with the Blueprint DSL (§5). The pipeline can make almost anything — search/build before saying "can't."

## 8. Local toolchain (verified on this machine)
Blender 5.1.2 (PATH), Unity 6000.4.11f1, Python 3.12.10 (PATH), git 2.54, gh 2.93 (authed), git-lfs 3.7.
Project root: `C:\Users\lilli\Documents\Unreal Projects\CurtisAILab`. Engine: UE 5.8, World Partition + OFPA.

## 9. Working rules (from memory — follow these)
- **Realism law:** 100% real, no fakes/shortcuts (esp. space/planets). Forward-compatible (data-driven, real units).
- **No philosophy/"robe" language.** Concrete, build-focused, proof-over-theory; web-check live player reality when useful.
- **Loop discipline:** ONE coherent chunk per pass; save + append BUILDLOG + checkpoint screenshot + git push each pass;
  additive/reversible; never overlap Unreal calls. Honor pause immediately; a stale queued `/loop` tick during a pause = stand down.

## 11. Current cross-agent handoff (2026-06-19, Builder: Codex)
> **★ LIVE TOP PRIORITY: JARON RE-TEST THE ONE-SURFACE PLANET.** His three screenshots showed the first
> tile fix still rendered stacked layers: coarse brown geoid + dark rectangular local sheets. Codex has
> now replaced the whole 156 km north-pole facet with one true spherical visual/physical cap and hidden
> the rectangular tile renders. Repeat the same altitude/fall-through views, then fly home→remote→home.
> Full evidence is in **BUILDLOG.md → One visible + physical planet surface**.

- New source: `_authoring/make_planet_nearfield_cap.py`. Active near-field planet asset:
  `/Game/Curtis/Meshes/Celestial/SurfaceLOD/SM_SYL_NorthPolarCap_01` (65,537 verts / 130,816 tris), placed
  at (0,0,0) as non-spatially-loaded `SYL_NorthPolarCap_01`. It is the exact 6,360 km sphere from the pole
  to the coarse geoid's first matching 256-vertex ring, 156.082 km away. All cap slots and the geoid use
  `M_SYL_World_Surface`, so there is no material ring that reads like another platform.
- The cap is real static collision (`CTF_UseComplexAsSimple`, double-sided, BlockAll), not visual-only.
  PIE outside both old tiles at (2000 m,2200 m) rested the player at z=20.3694 cm over analytic surface
  z=−69.4969 cm. The ship simultaneously kept its exact home settle. This directly replaces the brown
  pass-through layer Jaron photographed.
- The 2×4 km Home_02/Remote_02 components still exist as hidden exact collision backups, but never render;
  they must not appear as rectangular terrain shelves again. Close/high/orbit checkpoints:
  `_codex_planet_cap_remote_close.png`, `_codex_planet_cap_high_continuous.png`,
  `_codex_planet_true_orbit.png` (gitignored).

- New source: `_authoring/make_surface_corridor.py`. Active assets:
  `/Game/Curtis/Meshes/Celestial/SurfaceTiles/SM_SYL_SurfaceTile_Home_02` and
  `SM_SYL_SurfaceTile_Remote_02`; each is 2×4 km and uses the exact 6,360 km spherical equation. They are
  now **render-hidden collision backups**. Home is a World Partition actor at (0,0,0);
  `BP_SYL_SurfaceSite.Terrain` uses the remote tile at the existing 2 km arc transform. Their x=1 km seam
  matches the analytic sphere within 0.025 cm after reload.
- Terrain materials are `/Game/Curtis/Materials/Celestial/M_SYL_Terrain_{Basalt,IronRich,PaleSilicate}`.
  They are deterministic metre-space lithology sections authored in Blender, not screen UI or fake water.
  Close checkpoint: `_codex_unified_surface_remote_close_final.png` (gitignored).
- `SM_SYL_UnitGeoid` no longer has Claude's temporary convex hull. It remains the always-loaded distant
  round/orbital silhouette; streamed local tiles own playable collision. Six-second PIE regression:
  ship (4500.000007,0,138.361473), rotation 0/0/0; player rests at home; home/seam/remote traces hit and
  outside-corridor trace is null.

- Jaron confirmed controls are good until there are real destinations. Codex started the planet lane:
  `BP_SYL_CelestialWorld` now places a true-scale 6,360 km-radius reference world at
  (0,0,-636,000,000 cm), aligned exactly with the level's existing 6,360 km / 60 km SkyAtmosphere.
  Editable parameters: body name, radius, surface gravity, atmosphere height, sidereal rotation, axial
  tilt. From-scratch geoid source: `_authoring/make_celestial_body.py`; UE mesh/material under
  `/Game/Curtis/Meshes/Celestial` and `/Game/Curtis/Materials/Celestial`.
- `BP_SYL_Ship.GravityBody` points to the placed world. Its Hull now uses inverse-square radial
  acceleration read from that body; global-down gravity is disabled only when the body ref is valid.
  Six-second home settle remains ~(4500,0,138.36147), rotation 0/0/0. A 100 km off-axis PIE probe moved
  with cosine 1.0 toward the world center. Both Blueprints compile warnings-as-errors.
- The geoid is the continuous round body/orbital silhouette and deliberately has no monolithic collision.
  `BP_SYL_SurfaceSite` now supplies streamed local terrain/collision. `SYL_SurfaceSite_A01` is the first
  remote destination: 2 km arc-distance straight +X from home at (199,999.9967,0,-31.4465), pitched
  −0.01801754° to radial up. It has a 2×2 km exact spherical cap, 80×80 m deck, shelter, 45 m red beacon,
  and physical red pad lighting. Source: `_authoring/make_remote_surface_site.py`; assets under
  `/Game/Curtis/Meshes/Celestial/SurfaceSites`.
- Automated remote touchdown passed: deck/terrain radial traces hit correctly; the ship settled at
  287.0 cm radial altitude with 0.009 cm tangential drift and matched site pitch. Home settle remains
  unchanged. **Next action is Jaron's round-trip:** launch from apron, hold W/+X ~1.95 km, acquire beacon,
  land, and return. Use that evidence before tuning cruise or landing. Then build radial character up.

- **Pilot camera system added to `BP_SYL_Ship`.** Two CameraComponents: `CockpitCam` (child of
  `SeatAnchor`, rel (10,0,64), FOV 95, first-person, AutoActivate) and the reused `ChaseCam` (child of
  `Hull`, rel (-1300,0,480) pitch -12, FOV 90, third-person, AutoActivate OFF). Sitting blends the view
  target to the ship actor (`SetViewTargetwithBlend`); standing blends back to the player body. **`C`**
  toggles first/third person while seated via new bool vars `bThirdPerson` + `bViewLatch` (latched) and
  `Components|Activation|SetActive` (exactly one cam active).
- **`BP_SYL_Player` EventTick now gates all on-foot input** behind `Utilities|IsValid(GetAttachParentActor)
  = Is Not Valid`. While seated the body is attached to `SeatAnchor` → arrows drive ONLY the ship, head no
  longer fights it. Preserve this gate if you rewrite the player graph.
- Ship flight tunables (EventTick): thrust 2000/-1500, lift ±1900/-1100, yaw ±140, pitch ±95, **roll ±90
  (A/D)**. Seated controls: WASD-thrust+roll, Space/Ctrl lift, arrows yaw/pitch, A/D roll, C view, E stand.
  Camera feel lives on the CockpitCam/ChaseCam component transforms + FOV. No possession swap; GameMode
  still spawns `BP_SYL_Player_C` on foot.
- **CockpitCam pose is driven in BeginPlay** (`SetRelativeLocation (55,0,48)` + `SetRelativeRotation pitch
  -6`, rel SeatAnchor → canopy). This is deliberate: the placed World Partition ship had a stale
  per-instance override on `CockpitCam.RelativeLocation` that ignored `z` edits (template/instance writes
  silently failed), so the cam sat at the seat base below the windscreen. If you re-tune the cockpit eye,
  change the BeginPlay values (not just the template) and verify the LIVE/PIE component value. To move a
  component on any already-placed OFPA actor, prefer driving it in BeginPlay or re-placing the instance.
- Verified: both BPs compile (warnings-as-errors); 5 s PIE settle unchanged at (4500,0,138.36) 0/0/0.
- DSL gotcha confirmed this pass: `read_graph_dsl` exports member-var accessors as `|GetbPilotSeated`
  (broken) — repair to `Variables|Default|GetPilotSeated` (the `b` is dropped) before any write-back. Also
  **literals can't be `(bind …)`-ed** — inline numeric/bool literals instead of binding them.

## 10. Prior cross-agent handoff (2026-06-18, Builder: Codex)
- `BP_SYL_GameMode` spawns `BP_SYL_Player_C` on foot. Do not restore the "spawn as ship" shortcut.
- `BP_SYL_Ship` keeps the same character body and attaches it to `SeatAnchor`; there is no possession
  swap. E controls door/seat/stand by proximity; flight forces run only while `bPilotSeated`.
- Gunship assets: `/Game/Curtis/Meshes/Gunship`; source `_authoring/make_walkable_gunship.py`.
  Apron assets: `/Game/Curtis/Meshes/Infrastructure`; source `_authoring/make_dev_apron.py`.
- Development apron is centered at (4500,0,27.5). Ship is in
  `Fortis_Outpost/Development/Vehicles`, placed at (4500,0,130) for a short gear drop.
- Automated PIE physics passed: after 5+ seconds the ship remained at ~(4500,0,138.36) with exact
  0/0/0 pitch/yaw/roll. Jaron's full boarding/flight/exit loop otherwise passed. Claude rebuilt the
  windscreen at eye level; Codex restored its material slots and changed ramp-open pitch to −31°.
  Next is Jaron's quick visual/touchdown confirmation at the top of BUILDLOG "Next up".
