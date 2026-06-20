"""Author SYL's local Earth surface cap from scratch (fills the Earth shell's
1.40625-degree north-polar opening seamlessly).

The Earth distant shell (`SM_SYL_UnitBody_EarthOpenNorth`, see make_celestial_body.py)
is a one-metre UV reference sphere with U=256, V=128 that OMITS the final polar cap
above latitude 88.59375 deg. This cap reproduces exactly that missing piece on the
same unit sphere: its outer boundary ring is the Earth shell's last ring (ring 127,
latitude 88.59375 deg, 256 segments at the identical longitudes), so when both meshes
are placed at the same Earth transform/scale the boundary vertices coincide and there
is no seam and no second global shell. Placed + scaled in Unreal to the WGS84 ellipsoid
this becomes the ONE visible + physical local Earth surface; Fortis sits at the pole.
"""

from math import cos, pi, sin
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
FBX_PATH = ROOT / "SM_SYL_EarthLocalCap_North.fbx"

U_SEGMENTS = 256          # must match the Earth shell longitude count
V_SEGMENTS = 128          # must match the Earth shell latitude count
CAP_RINGS = 28            # latitude rings from the opening boundary up toward the pole

# The Earth shell's last (open) ring; the cap's outer boundary must equal it exactly.
BOUNDARY_RING = V_SEGMENTS - 1
BOUNDARY_LAT = -0.5 * pi + pi * BOUNDARY_RING / V_SEGMENTS   # 88.59375 deg
POLE_LAT = 0.5 * pi


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def build_cap() -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    rings: list[list[int]] = []

    # Rings from the boundary latitude (r=0) toward the pole. r=0 reproduces the
    # Earth shell's last ring exactly so the seam closes.
    for r in range(CAP_RINGS):
        latitude = BOUNDARY_LAT + (POLE_LAT - BOUNDARY_LAT) * (r / CAP_RINGS)
        radial = cos(latitude)
        z = sin(latitude)
        idxs: list[int] = []
        for segment in range(U_SEGMENTS):
            longitude = 2.0 * pi * segment / U_SEGMENTS
            idxs.append(len(vertices))
            vertices.append((radial * cos(longitude), radial * sin(longitude), z))
        rings.append(idxs)

    pole = len(vertices)
    vertices.append((0.0, 0.0, 1.0))

    faces: list[tuple[int, ...]] = []
    # Quad bands between successive rings (same winding as the Earth shell body).
    for r in range(CAP_RINGS - 1):
        lower = rings[r]
        upper = rings[r + 1]
        for segment in range(U_SEGMENTS):
            nxt = (segment + 1) % U_SEGMENTS
            faces.append((lower[segment], lower[nxt], upper[nxt], upper[segment]))
    # Final triangle fan to the pole (same winding as the Moon's closed north cap).
    last = rings[CAP_RINGS - 1]
    for segment in range(U_SEGMENTS):
        nxt = (segment + 1) % U_SEGMENTS
        faces.append((last[segment], last[nxt], pole))

    mesh = bpy.data.meshes.new("SM_SYL_EarthLocalCap_North")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    mesh.materials.append(bpy.data.materials.new("EarthMeanAlbedo"))

    obj = bpy.data.objects.new("SM_SYL_EarthLocalCap_North", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def main() -> None:
    clear_scene()
    cap = build_cap()
    bpy.ops.object.select_all(action="DESELECT")
    cap.select_set(True)
    bpy.context.view_layer.objects.active = cap
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
    print(f"Exported {FBX_PATH}; boundary_lat={BOUNDARY_LAT * 180 / pi:.5f} deg, rings={CAP_RINGS}")


if __name__ == "__main__":
    main()
