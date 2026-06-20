"""Author SYL's local Earth COLLISION patch (normal-scale, invisible).

True-scale planets can't use the 6.38-million-times-scaled visual Earth cap for
character/ship collision: Chaos loses precision at that scale and the player
bounces/jitters. Standard fix: the giant cap stays VISUAL-only, and a separate
NORMAL-scale (1x) collision patch — coincident with the cap surface, invisible —
carries the physics. This patch is a curvature-correct grid around the north pole
(Fortis region) using Earth's polar radius of curvature, authored in metres so it
imports to Unreal at true cm with no scaling, giving stable collision.
"""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
FBX_PATH = ROOT / "SM_SYL_EarthLocalCollision_North.fbx"

# Earth WGS84 polar radius of curvature Rc = a^2 / c (metres). Near the pole the
# surface height is z = -(x^2 + y^2) / (2 Rc) to first order, matching the visual cap.
A_M = 6378137.0
C_M = 6356752.0
RC_M = A_M * A_M / C_M            # 6,399,593.6 m
HALF_M = 20000.0                  # patch half-extent: +/- 20 km (covers foot + local flight)
SEG = 80                         # 80x80 cells (~500 m), locally flat -> smooth walking


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def height(x: float, y: float) -> float:
    return -(x * x + y * y) / (2.0 * RC_M)


def build_patch() -> bpy.types.Object:
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    width = 2.0 * HALF_M
    for iy in range(SEG + 1):
        y = -HALF_M + width * iy / SEG
        for ix in range(SEG + 1):
            x = -HALF_M + width * ix / SEG
            verts.append((x, y, height(x, y)))
    row = SEG + 1
    for iy in range(SEG):
        for ix in range(SEG):
            a = iy * row + ix
            b = a + 1
            d = (iy + 1) * row + ix
            c = d + 1
            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new("SM_SYL_EarthLocalCollision_North")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new("SM_SYL_EarthLocalCollision_North", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def main() -> None:
    clear_scene()
    patch = build_patch()
    bpy.ops.object.select_all(action="DESELECT")
    patch.select_set(True)
    bpy.context.view_layer.objects.active = patch
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
    print(f"Exported {FBX_PATH}; Rc={RC_M:.1f} m, half={HALF_M} m, edge drop={-height(HALF_M,0):.2f} m")


if __name__ == "__main__":
    main()
