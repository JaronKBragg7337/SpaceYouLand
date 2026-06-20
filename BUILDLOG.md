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

> **Older entries (2026-06-18 → early 2026-06-20) are rotated to `BUILDLOG_ARCHIVE.md`** to keep this
> file small. This live log keeps only the current-state entries + Next up. Read the archive only for a
> deep dive into past how/when/who.

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

- **2026-06-20 — ONE physical Earth surface built; Fortis now stands on Earth (Builder: Claude).** Authored
  `_authoring/make_earth_local_cap.py` from scratch: a cap that reproduces the EXACT missing piece of the
  Earth shell — its outer boundary ring is the shell's last open ring (ring 127, latitude **88.59375°**, 256
  segments at identical longitudes, same unit-sphere math), 28 rings closing to the pole. Imported
  `/Game/Curtis/Meshes/Celestial/Bodies/SM_SYL_EarthLocalCap_North`, set BodySetup
  `CTF_UseComplexAsSimple` + double-sided, placed `SYL_EarthLocalSurface_North` at the Earth's EXACT
  transform (loc (0,0,−635675200), scale (6378137,6378137,6356752)) so the boundary verts coincide with the
  shell → seamless, no second global shell. Always-loaded, `BlockAll` QueryAndPhysics, `bNeverDistanceCull`,
  Earth mean-albedo material. Verified: down-trace at the pole hits the Fortis foundation (z=50) on the cap;
  open ground 1 km out hits the cap at z≈−47 cm (gentle dome, Fortis on the high point); a capture shows
  Fortis seated on one continuous Earth surface to the horizon, no floating brown layer. Fortis is now ON
  the Earth at the north pole. NOTE: pole region is a smooth gentle dome (rings evenly spaced over 1.4° so
  the apex cone spans ~5.6 km — imperceptible slope; could densify rings near the pole later). NEXT: wire
  `BP_SYL_CelestialBody` as generic inverse-square gravity + reconnect ship; radial character orientation.

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
