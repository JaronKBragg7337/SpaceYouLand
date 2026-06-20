"""Author SYL's reusable true-scale celestial-body shell meshes from scratch.

The meshes are one-metre reference bodies. Unreal scales them by each body's
real radii, so geometry and simulation data share the same metre-based values.

Earth's distant shell deliberately omits the final 1.40625-degree north-polar
cap. Fortis will receive one exact local visible+physical surface in that
opening next; the distant shell can never become a second ground layer there.
The Moon shell is complete because no lunar surface site exists yet.
"""

from math import cos, pi, sin
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
EARTH_FBX = ROOT / "SM_SYL_UnitBody_EarthOpenNorth.fbx"
MOON_FBX = ROOT / "SM_SYL_UnitBody_MoonFull.fbx"
U_SEGMENTS = 256
V_SEGMENTS = 128
EARTH_OPENING_DEGREES = 180.0 / V_SEGMENTS


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def build_unit_body(name: str, close_north_pole: bool, material_name: str) -> bpy.types.Object:
    """Build a one-metre UV reference sphere without using premade geometry."""
    vertices: list[tuple[float, float, float]] = [(0.0, 0.0, -1.0)]
    faces: list[tuple[int, ...]] = []

    # Rings stop one angular step below the north pole. Earth leaves that ring
    # open; Moon closes it with a final pole vertex.
    for ring in range(1, V_SEGMENTS):
        latitude = -0.5 * pi + pi * ring / V_SEGMENTS
        radial = cos(latitude)
        z = sin(latitude)
        for segment in range(U_SEGMENTS):
            longitude = 2.0 * pi * segment / U_SEGMENTS
            vertices.append((radial * cos(longitude), radial * sin(longitude), z))

    first_ring = 1
    for segment in range(U_SEGMENTS):
        nxt = (segment + 1) % U_SEGMENTS
        faces.append((0, first_ring + nxt, first_ring + segment))

    for ring in range(V_SEGMENTS - 2):
        lower = 1 + ring * U_SEGMENTS
        upper = lower + U_SEGMENTS
        for segment in range(U_SEGMENTS):
            nxt = (segment + 1) % U_SEGMENTS
            faces.append((lower + segment, lower + nxt, upper + nxt, upper + segment))

    if close_north_pole:
        north = len(vertices)
        vertices.append((0.0, 0.0, 1.0))
        last_ring = 1 + (V_SEGMENTS - 2) * U_SEGMENTS
        for segment in range(U_SEGMENTS):
            nxt = (segment + 1) % U_SEGMENTS
            faces.append((last_ring + segment, last_ring + nxt, north))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = True

    material = bpy.data.materials.new(material_name)
    mesh.materials.append(material)

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def export_fbx(obj: bpy.types.Object, path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=str(path),
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
    earth = build_unit_body(
        "SM_SYL_UnitBody_EarthOpenNorth",
        close_north_pole=False,
        material_name="EarthMeanAlbedo",
    )
    moon = build_unit_body(
        "SM_SYL_UnitBody_MoonFull",
        close_north_pole=True,
        material_name="MoonMeanAlbedo",
    )
    export_fbx(earth, EARTH_FBX)
    export_fbx(moon, MOON_FBX)
    print(
        f"Exported {EARTH_FBX} and {MOON_FBX}; "
        f"Earth north opening={EARTH_OPENING_DEGREES:.8f} degrees"
    )


if __name__ == "__main__":
    main()
