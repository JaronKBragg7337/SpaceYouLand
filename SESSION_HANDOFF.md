# SESSION_HANDOFF — operating manual for a fresh Claude session

> Read this to know exactly what the previous session knew and could do. Pair with **BUILDLOG.md**
> (current state + history + "Next up") and your **memory** (auto-loads on this machine: MEMORY.md +
> linked files). If you paste PASTE_INTO_NEW_CHAT.txt into a new chat, it points you here.

## 0. Orientation order
1. **This file** — how to operate (tools, pipeline, gotchas).
2. **BUILDLOG.md** — what's built, conventions/coordinates, and the live **"Next up"** TODO.
3. **Memory** (MEMORY.md index → files): `realism-law`, `syl-endgame-intent`, `syl-project-reality`,
   `working-style-jaron`, `asset-pipeline-toolchain`, `syl-drive-docs`. These hold the design law + the *why*.
4. **CLAUDE.md** — note its "Curtis lab / obstacle course" framing is a wrapper; the real project is
   **SYL (Space You Land)**, a 100%-realistic first-person space game (see memory).

## 1. What SYL is (one paragraph)
Persistent, first-person space game. **Design law: relate to reality 100%, no fakes** — real physics,
real gravity, walkable ships/stations, cargo/crew physical, "menus observe reality," "the world is
built not spawned." Long-term it's a precursor to real space-drone operation; planets→real planets,
factions→real governments later — so **build forward-compatible**: data-driven factions/planets, real
units. No premade assets — **everything is authored from scratch.** Current build: a walkable Fortis
outpost + a real-physics flyable ship (space arc Stage 1). Owner: Jaron.

## 2. Connect to Unreal — the build tools are DEFERRED (must be loaded)
- The `unreal-mcp` tools are NOT loaded by default. Load them with **ToolSearch** (query `unreal`, or
  `select:mcp__unreal-mcp__list_toolsets,mcp__unreal-mcp__describe_toolset,mcp__unreal-mcp__call_tool`).
- Server runs in **tool-search mode**: 3 meta-tools — `list_toolsets`, `describe_toolset(name)`,
  `call_tool(toolset_name, tool_name, arguments)`. **tool_name is the SHORT name** (no toolset prefix).
- Needs Unreal Editor OPEN with the MCP server on `http://127.0.0.1:8000/mcp` (auto-starts). If down:
  confirm the editor is open; `Test-NetConnection 127.0.0.1 -Port 8000`. Ask Jaron to open the project.
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

## 4. Viewport screenshots (IMPORTANT decode trick)
`EditorAppToolset.CaptureViewport` returns a base64 PNG **too big to inline** (it errors and saves to a
tool-result `.txt`). To see it: read the newest tool-result file, `json.loads`, take
`returnValue.image.data`, base64-decode, write a `.png`, then Read the png. Snippet:
```python
import json,base64,glob,os
f=max(glob.glob('<tool-results-dir>/mcp-unreal-mcp-call_tool-*.txt'),key=os.path.getmtime)
raw=open(f).read(); rv=json.loads(raw[raw.find('{'):])['returnValue']
rv=json.loads(rv) if isinstance(rv,str) else rv
open('out.png','wb').write(base64.b64decode(rv['image']['data']))
```
Pass an `annotations` object with all fields 0/null to disable overlays. `captureTransform: null` = current
camera (works during PIE, but during PIE it may grab the editor cam — verify via `find_actors`/transforms).

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

## 6. Version control — auto-backup every meaningful change
- Private GitHub repo: **github.com/JaronKBragg7337/SpaceYouLand**. `gh` is authed (token in OS keyring).
- `git add -A && git commit -m "…" && git push` after each chunk. End commit messages with
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Git LFS tracks `*.uasset *.umap`.
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
