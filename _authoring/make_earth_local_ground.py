"""Author SYL's local Earth GROUND pad (flat, rock-solid, visible + collidable).

Curved complex-as-simple collision at true planet scale produces unstable Chaos
contacts -> the player bounces violently (and that velocity punched the player
through the ship). A real planet is imperceptibly flat locally (Earth curves
~8 m over 10 km), so the LOCAL walkable ground is just a flat pad at the pole:
it gets SIMPLE (box/convex) collision -> rock solid, no bounce; and it is the
VISIBLE surface too -> no float (you walk on exactly what you see). The big
curved cap continues the surface into the distance and gives the round body.
"""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
FBX_PATH = ROOT / "SM_SYL_EarthLocalGround_Flat.fbx"

HALF_M = 10000.0   # +/- 10 km flat pad (edge is well past the ~5 km eye-level horizon)
SEG = 24           # light tessellation (flat; just helps lighting)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def build_pad() -> bpy.types.Object:
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    width = 2.0 * HALF_M
    for iy in range(SEG + 1):
        y = -HALF_M + width * iy / SEG
        for ix in range(SEG + 1):
            x = -HALF_M + width * ix / SEG
            verts.append((x, y, 0.0))   # FLAT
    row = SEG + 1
    for iy in range(SEG):
        for ix in range(SEG):
            a = iy * row + ix
            b = a + 1
            d = (iy + 1) * row + ix
            c = d + 1
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new("SM_SYL_EarthLocalGround_Flat")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)
    mesh.materials.append(bpy.data.materials.new("EarthMeanAlbedo"))
    obj = bpy.data.objects.new("SM_SYL_EarthLocalGround_Flat", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def main() -> None:
    clear_scene()
    pad = build_pad()
    bpy.ops.object.select_all(action="DESELECT")
    pad.select_set(True)
    bpy.context.view_layer.objects.active = pad
    bpy.ops.export_scene.fbx(
        filepath=str(FBX_PATH),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        global_scale=1.0,
        axis_forward="-Z",
        axis_up="Y",
        mesh_smooth_type="FACE",
    )
    print(f"Exported {FBX_PATH}; flat pad half={HALF_M} m")


if __name__ == "__main__":
    main()
