# SYL — First Playable Build Plan

> Read this first if you're a fresh Claude Code session connecting to this project.
> Context: the user (Jaron) is building **Space You Land (SYL)**, a persistent first-person
> space game. Full design bible lives in Google Drive folder "Space-You-Land (2026-2027)"
> (Foundation docs: 01 Vision / 02 Player Experience Bible / 03 Simulation Architecture).
> The user does NOT code — they describe what they want and Claude builds it in Unreal via
> the `unreal-mcp` server (project `.mcp.json`, http://127.0.0.1:8000/mcp).

## Decided scope
- **First playable = ONE faction slice: the Militaristic Empire (Fortis).**
- Mood: realistic, armored/industrial, serious. Combat-forward.
- This is a vertical slice that *feels* like SYL — NOT the full MMO. Build one honest place,
  not a fake everything. Full SYL (persistent server sim, 9 factions, seamless planet-to-space,
  no loading screens) is a long-term, multi-year goal — we grow toward it in slices.

## First Playable: "Fortis Outpost on Alert"
One sentence: *You're a lone Fortis soldier on a frontier outpost when the perimeter goes hot —
survive it, scavenge what you can, and glimpse the war beyond.*

Build sequence (do in order, confirm each looks right before moving on):
1. **The place** — walled Fortis outpost: armored modular buildings, crates, blast walls,
   landing pad. Serious lighting (overcast / red-alert).
2. **You** — third-person template character reskinned as a Fortis soldier; movement feel.
3. **Survival/collect** — scattered supply caches / salvage the player physically picks up
   (ammo, parts). Simple needs meter so collecting matters.
4. **Combat** — a hostile incursion: enemies approach the perimeter; player fights them off.
   Health, damage, a weapon.
5. **Exploration beat** — a docked Fortis gunship on the pad the player can walk up to and
   inspect. The hook into the wider universe.
6. **Win/lose** — repel the wave = outpost held. First real game loop.

## Connection status (as of 2026-06-18) — SETUP SOLVED ✅
- UE 5.8 installed and CurtisAILab opens in it.
- MCP server **auto-starts** (`bAutoStartServer=True` in `Config/DefaultEditorPerProjectUserSettings.ini`).
  Confirmed live at http://127.0.0.1:8000/mcp.
- **Building toolsets are enabled.** The `EditorToolset` plugin is now enabled in `CurtisAILab.uproject`.
  Without it, the server only exposed `AgentSkillToolset` (a "skills/notes" tool) and NO build tools —
  that was the "only one tool in the toolbox" confusion. After enabling EditorToolset + restarting the
  editor, the registry exposes the full build suite: **SceneTools** (place/remove actors, load levels,
  camera, outliner), **PrimitiveTools** (geometry), Static/SkeletalMeshTools, Material/TextureTools,
  BlueprintTools, ActorTools, ObjectTools, DataTable/CurveTable, EditorAppToolset (viewport/PIE), etc.
  (Want even more later — PCG procedural, Niagara VFX, GAS abilities — enable `AllToolsets`, then restart.)
- **The server runs in tool-search mode** (`bEnableToolSearch=True`). It exposes 3 meta-tools:
  `list_toolsets`, `describe_toolset`, `call_tool`. To DO anything: call `list_toolsets` to see
  categories, `describe_toolset <name>` to see a category's tools + schemas, then `call_tool` with
  `toolset_name`, `tool_name`, `arguments`. (The individual build tools are NOT top-level — reach them
  via `call_tool`.) To expose every tool directly instead, set `bEnableToolSearch=False` and restart.
- If running from the CurtisAILab folder and you see the `unreal-mcp` server's tools, YOU ARE CONNECTED.
  If not: confirm editor open + `Test-NetConnection 127.0.0.1 -Port 8000`; if down, editor console
  `ModelContextProtocol.StartServer`. After ANY plugin/uproject change, the editor must be restarted.

## ⚠️ Known issue to fix — ROOT CAUSE FOUND
The **"Load Errors (86)"** are NOT random corruption. The log shows the Third Person blueprints
(`BP_ThirdPersonCharacter`, `BP_ThirdPersonGameMode`, `BP_ThirdPersonPlayerController`) are parented to
**C++ classes in a module `TP_ThirdPerson` that does not exist in this project**
(`Failed to load Class /Script/TP_ThirdPerson.TP_ThirdPersonCharacter as Parent ...`). The project was
created from the **C++** Third Person template but has **no Source/ and no compiled binaries**, so those
parent classes can't load — cascading into the 86 errors. The template character is effectively broken.

**Recommended fix (no compiler needed):** don't depend on the broken `BP_ThirdPersonCharacter`. For step 2,
build the Fortis soldier from a **fresh Blueprint** (parent it to the engine `Character` class directly,
add a mesh + camera) using BlueprintTools, and set a new Blueprint GameMode/PlayerController. That sidesteps
the missing C++ module entirely. (Alternative, heavier: add a C++ `TP_ThirdPerson` module and compile —
needs Visual Studio build tools; avoid unless the user wants a code project.)

## First Playable build steps (recap — full detail above)
1. Fortis outpost environment  2. Reskin character as Fortis soldier  3. Collect/salvage + needs meter
4. Combat (enemies, health, weapon)  5. Docked gunship exploration beat  6. Win/lose on repelling the wave.

## Environment facts
- Unreal Engine: project targets **5.8** (installing as of 2026-06-18). 5.6 also installed.
- Project: `C:\Users\lilli\Documents\Unreal Projects\CurtisAILab` (Blueprint-only, Third Person template,
  `ModelContextProtocol` plugin enabled, 571 content assets).
- To connect: UE 5.8 installed -> open CurtisAILab -> turn on in-editor MCP server (port 8000)
  -> relaunch Claude Code from THIS project folder so `.mcp.json` loads -> `unreal-mcp` tools appear.
