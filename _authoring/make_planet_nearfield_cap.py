"""Author the true high-resolution north-pole surface LOD for SYL's first world.

The always-loaded unit geoid is intentionally coarse enough for an orbital
silhouette, but its first UV-sphere facet spans roughly 156 km from the pole.
This cap replaces that entire facet with the exact 6,360 km sphere.  Its outer
ring uses the same 256 vertices as the geoid's first ring, so the two meshes
coincide mathematically at the LOD boundary instead of forming stacked layers.

Playable collision remains on smaller streamed exact-surface tiles.  This mesh
is visual terrain only and should have simple collision removed after import.
"""

from math import atan2, cos, pi, sin
from pathlib import Path

import bmesh
import bpy


ROOT = Path(__file__).resolve().parent
FBX_PATH = ROOT / "SM_SYL_NorthPolarCap_01.fbx"
ASSET_NAME = "SM_SYL_NorthPolarCap_01"
PLANET_RADIUS_M = 6_360_000.0
ANGULAR_SEGMENTS = 256
RADIAL_RINGS = 256
EDGE_THETA = pi / 128.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = clamp((value - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def lithology_region(x: float, y: float, radius: float) -> int:
    """Return broad real-scale mineral provinces: basalt, iron, or silicate."""
    edge_radius = PLANET_RADIUS_M * sin(EDGE_THETA)
    if radius > edge_radius * 0.90:
        return 0

    iron_field = (
        0.58 * sin((x + 0.37 * y) / 18_000.0)
        + 0.27 * sin((0.41 * x - y) / 8_500.0)
        + 0.15 * sin((x + y) / 3_700.0)
    )
    basin_field = (
        0.62 * sin((x - 31_000.0) / 29_000.0)
        + 0.24 * cos((y + 11_000.0) / 17_000.0)
        + 0.14 * sin((x - 0.55 * y) / 6_500.0)
    )
    iron_weight = smoothstep(-0.30, 0.34, iron_field)
    basin_weight = smoothstep(0.05, 0.70, basin_field)
    if basin_weight > 0.60:
        return 2
    if iron_weight > 0.55:
        return 1
    return 0


def geoid_first_ring():
    """Return the actual float vertices used by Blender's coarse unit geoid."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm,
        u_segments=ANGULAR_SEGMENTS,
        v_segments=128,
        radius=1.0,
    )
    below_pole = [vert for vert in bm.verts if vert.co.z < 0.999999]
    first_z = max(vert.co.z for vert in below_pole)
    ring = [vert.co.copy() for vert in below_pole if abs(vert.co.z - first_z) < 1e-7]
    bm.free()
    ring.sort(key=lambda value: (atan2(value.y, value.x) + 2.0 * pi) % (2.0 * pi))
    if len(ring) != ANGULAR_SEGMENTS:
        raise RuntimeError(f"Expected {ANGULAR_SEGMENTS} geoid edge vertices, found {len(ring)}")
    return ring


def build_cap() -> bpy.types.Object:
    vertices = [(0.0, 0.0, 0.0)]
    geoid_edge = geoid_first_ring()
    for ring in range(1, RADIAL_RINGS + 1):
        if ring == RADIAL_RINGS:
            vertices.extend(
                (
                    value.x * PLANET_RADIUS_M,
                    value.y * PLANET_RADIUS_M,
                    (value.z - 1.0) * PLANET_RADIUS_M,
                )
                for value in geoid_edge
            )
            continue
        theta = EDGE_THETA * ring / RADIAL_RINGS
        horizontal_radius = PLANET_RADIUS_M * sin(theta)
        z = PLANET_RADIUS_M * cos(theta) - PLANET_RADIUS_M
        for segment in range(ANGULAR_SEGMENTS):
            phi = 2.0 * pi * segment / ANGULAR_SEGMENTS
            vertices.append(
                (
                    horizontal_radius * cos(phi),
                    horizontal_radius * sin(phi),
                    z,
                )
            )

    faces = []
    for segment in range(ANGULAR_SEGMENTS):
        current = 1 + segment
        following = 1 + (segment + 1) % ANGULAR_SEGMENTS
        faces.append((0, current, following))

    for ring in range(1, RADIAL_RINGS):
        inner = 1 + (ring - 1) * ANGULAR_SEGMENTS
        outer = 1 + ring * ANGULAR_SEGMENTS
        for segment in range(ANGULAR_SEGMENTS):
            following = (segment + 1) % ANGULAR_SEGMENTS
            faces.append(
                (
                    inner + segment,
                    outer + segment,
                    outer + following,
                    inner + following,
                )
            )

    mesh = bpy.data.meshes.new(ASSET_NAME)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.validate()

    obj = bpy.data.objects.new(ASSET_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(bpy.data.materials.new("Basalt"))
    obj.data.materials.append(bpy.data.materials.new("IronRich"))
    obj.data.materials.append(bpy.data.materials.new("PaleSilicate"))

    for polygon in mesh.polygons:
        polygon.use_smooth = True
        center = sum(
            (mesh.vertices[index].co for index in polygon.vertices),
            start=mesh.vertices[polygon.vertices[0]].co.copy() * 0.0,
        ) / len(polygon.vertices)
        radius = (center.x * center.x + center.y * center.y) ** 0.5
        polygon.material_index = lithology_region(center.x, center.y, radius)
    return obj


def export_fbx(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
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
    cap = build_cap()
    export_fbx(cap)
    counts = [0, 0, 0]
    for polygon in cap.data.polygons:
        counts[polygon.material_index] += 1
    edge_radius = PLANET_RADIUS_M * sin(EDGE_THETA)
    edge_z = PLANET_RADIUS_M * cos(EDGE_THETA) - PLANET_RADIUS_M
    print(
        f"Exported {ASSET_NAME}: {len(cap.data.vertices)} vertices, "
        f"{len(cap.data.polygons)} faces, materials={counts}, "
        f"edge_radius={edge_radius:.6f} m, edge_z={edge_z:.6f} m"
    )


if __name__ == "__main__":
    main()
