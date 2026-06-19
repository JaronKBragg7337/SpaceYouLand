"""Author SYL's reusable unit geoid mesh from scratch and export it to FBX.

The Unreal celestial-body Blueprint scales this one-metre-radius mesh using
real body radii expressed in metres. Surface terrain will be streamed as
separate local patches; this mesh is the body's continuous round geoid and
orbital silhouette, not a flat playable-zone substitute.
"""

from pathlib import Path

import bmesh
import bpy


ROOT = Path(__file__).resolve().parent
FBX_PATH = ROOT / "SM_SYL_CelestialBody_UnitGeoid.fbx"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def build_unit_geoid() -> bpy.types.Object:
    mesh = bpy.data.meshes.new("SM_SYL_CelestialBody_UnitGeoid")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm,
        u_segments=256,
        v_segments=128,
        radius=1.0,
    )
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    geoid = bpy.data.objects.new("SM_SYL_CelestialBody_UnitGeoid", mesh)
    bpy.context.collection.objects.link(geoid)

    for polygon in mesh.polygons:
        polygon.use_smooth = True

    material = bpy.data.materials.new("PlanetSurface")
    geoid.data.materials.append(material)
    return geoid


def export_fbx(geoid: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    geoid.select_set(True)
    bpy.context.view_layer.objects.active = geoid
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


def main() -> None:
    clear_scene()
    geoid = build_unit_geoid()
    export_fbx(geoid)
    print(f"Exported {FBX_PATH}")


if __name__ == "__main__":
    main()
