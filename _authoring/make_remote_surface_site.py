"""Author SYL's first curvature-correct remote surface destination.

The terrain patch is a real spherical cap for the current 6,360 km world,
expressed in local tangent coordinates. The landing infrastructure and its
collision hulls are authored separately so World Partition can stream the
site while the continuous geoid remains always loaded.
"""

from math import sqrt
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
PLANET_RADIUS_M = 6_360_000.0
PATCH_HALF_SIZE_M = 1_000.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def spherical_height(x: float, y: float) -> float:
    return sqrt(PLANET_RADIUS_M**2 - x * x - y * y) - PLANET_RADIUS_M


def make_grid_mesh(name: str, segments: int) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    vertices = []
    faces = []
    width = PATCH_HALF_SIZE_M * 2.0
    for iy in range(segments + 1):
        y = -PATCH_HALF_SIZE_M + width * iy / segments
        for ix in range(segments + 1):
            x = -PATCH_HALF_SIZE_M + width * ix / segments
            vertices.append((x, y, spherical_height(x, y)))
    row = segments + 1
    for iy in range(segments):
        for ix in range(segments):
            a = iy * row + ix
            b = a + 1
            d = (iy + 1) * row + ix
            c = d + 1
            faces.append((a, b, c, d))
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    material = bpy.data.materials.new("PlanetSurface")
    obj.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def make_terrain_collision(name: str, segments: int = 8) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    vertices = []
    faces = []
    width = PATCH_HALF_SIZE_M * 2.0
    for iy in range(segments + 1):
        y = -PATCH_HALF_SIZE_M + width * iy / segments
        for ix in range(segments + 1):
            x = -PATCH_HALF_SIZE_M + width * ix / segments
            vertices.append((x, y, spherical_height(x, y)))
    row = segments + 1
    for iy in range(segments):
        for ix in range(segments):
            a = iy * row + ix
            b = a + 1
            d = (iy + 1) * row + ix
            c = d + 1
            faces.append((a, b, c, d))

    border = []
    border.extend((ix, 0) for ix in range(segments + 1))
    border.extend((segments, iy) for iy in range(1, segments + 1))
    border.extend((ix, segments) for ix in range(segments - 1, -1, -1))
    border.extend((0, iy) for iy in range(segments - 1, 0, -1))
    bottom_indices = []
    for ix, iy in border:
        x = -PATCH_HALF_SIZE_M + width * ix / segments
        y = -PATCH_HALF_SIZE_M + width * iy / segments
        bottom_indices.append(len(vertices))
        vertices.append((x, y, -25.0))
    for edge in range(len(border)):
        ix0, iy0 = border[edge]
        ix1, iy1 = border[(edge + 1) % len(border)]
        top0 = iy0 * row + ix0
        top1 = iy1 * row + ix1
        bot0 = bottom_indices[edge]
        bot1 = bottom_indices[(edge + 1) % len(border)]
        faces.append((top0, bot0, bot1, top1))
    faces.append(tuple(reversed(bottom_indices)))

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_box(bm: bmesh.types.BMesh, center, size, material_index=0) -> None:
    result = bmesh.ops.create_cube(bm, size=1.0)
    verts = result["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=verts)
    faces = {face for vert in verts for face in vert.link_faces}
    for face in faces:
        face.material_index = material_index


def add_beam(
    bm: bmesh.types.BMesh,
    start,
    end,
    thickness: float,
    material_index=0,
) -> None:
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    midpoint = (start_v + end_v) * 0.5
    result = bmesh.ops.create_cube(bm, size=1.0)
    verts = result["verts"]
    bmesh.ops.scale(
        bm,
        vec=Vector((direction.length, thickness, thickness)),
        verts=verts,
    )
    rotation = direction.to_track_quat("X", "Z").to_matrix()
    bmesh.ops.rotate(bm, cent=Vector((0.0, 0.0, 0.0)), matrix=rotation, verts=verts)
    bmesh.ops.translate(bm, vec=midpoint, verts=verts)
    faces = {face for vert in verts for face in vert.link_faces}
    for face in faces:
        face.material_index = material_index


def make_landing_site() -> bpy.types.Object:
    name = "SM_SYL_RemoteLandingSite_01"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # 80 m landing deck, raised physical edge strips, and touchdown cross.
    add_box(bm, (0.0, 0.0, 1.1), (80.0, 80.0, 2.2), 0)
    for x, y, sx, sy in (
        (0.0, -38.5, 74.0, 1.0),
        (0.0, 38.5, 74.0, 1.0),
        (-38.5, 0.0, 1.0, 74.0),
        (38.5, 0.0, 1.0, 74.0),
        (0.0, 0.0, 24.0, 0.8),
        (0.0, 0.0, 0.8, 24.0),
    ):
        add_box(bm, (x, y, 2.25), (sx, sy, 0.12), 1)

    # Four deck support blocks extend into the terrain cap.
    for x in (-31.0, 31.0):
        for y in (-31.0, 31.0):
            add_box(bm, (x, y, -1.4), (3.0, 3.0, 5.0), 0)

    # Armored survey shelter with a physical door marker.
    shelter = (105.0, -70.0)
    add_box(bm, (shelter[0], shelter[1], 3.2), (24.0, 14.0, 6.4), 0)
    add_box(bm, (shelter[0], shelter[1], 6.8), (26.0, 16.0, 0.8), 0)
    add_box(bm, (shelter[0] - 12.1, shelter[1], 2.2), (0.25, 3.2, 4.4), 1)

    # 45 m truss beacon: high enough to remain visible over the real horizon.
    tower_x, tower_y = -105.0, -90.0
    leg_offsets = ((-2.0, -2.0), (-2.0, 2.0), (2.0, -2.0), (2.0, 2.0))
    for dx, dy in leg_offsets:
        add_box(bm, (tower_x + dx, tower_y + dy, 22.5), (0.65, 0.65, 45.0), 0)
    for z0 in range(0, 45, 5):
        z1 = z0 + 5.0
        for yoff in (-2.0, 2.0):
            add_beam(
                bm,
                (tower_x - 2.0, tower_y + yoff, z0),
                (tower_x + 2.0, tower_y + yoff, z1),
                0.28,
            )
            add_beam(
                bm,
                (tower_x + 2.0, tower_y + yoff, z0),
                (tower_x - 2.0, tower_y + yoff, z1),
                0.28,
            )
        for xoff in (-2.0, 2.0):
            add_beam(
                bm,
                (tower_x + xoff, tower_y - 2.0, z0),
                (tower_x + xoff, tower_y + 2.0, z1),
                0.28,
            )
            add_beam(
                bm,
                (tower_x + xoff, tower_y + 2.0, z0),
                (tower_x + xoff, tower_y - 2.0, z1),
                0.28,
            )
    add_box(bm, (tower_x, tower_y, 45.3), (6.0, 6.0, 0.6), 0)
    beacon = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=24,
        radius1=1.5,
        radius2=1.5,
        depth=1.4,
    )
    bmesh.ops.translate(
        bm,
        vec=Vector((tower_x, tower_y, 46.3)),
        verts=beacon["verts"],
    )
    beacon_faces = {face for vert in beacon["verts"] for face in vert.link_faces}
    for face in beacon_faces:
        face.material_index = 1

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(bpy.data.materials.new("Steel"))
    obj.data.materials.append(bpy.data.materials.new("BeaconRed"))
    return obj


def make_collision_box(name: str, center, size) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    add_box(bm, center, size)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def export_selection(path: Path, objects) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
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
    terrain = make_grid_mesh("SM_SYL_RemoteTerrainPatch_01", segments=64)
    terrain_collision = make_terrain_collision(
        "UCX_SM_SYL_RemoteTerrainPatch_01_00"
    )
    export_selection(
        ROOT / "SM_SYL_RemoteTerrainPatch_01.fbx",
        [terrain, terrain_collision],
    )

    clear_scene()
    site = make_landing_site()
    collisions = [
        make_collision_box(
            "UCX_SM_SYL_RemoteLandingSite_01_00",
            (0.0, 0.0, 1.1),
            (80.0, 80.0, 2.2),
        ),
        make_collision_box(
            "UCX_SM_SYL_RemoteLandingSite_01_01",
            (105.0, -70.0, 3.2),
            (24.0, 14.0, 6.4),
        ),
    ]
    for index, (dx, dy) in enumerate(
        ((-2.0, -2.0), (-2.0, 2.0), (2.0, -2.0), (2.0, 2.0)),
        start=2,
    ):
        collisions.append(
            make_collision_box(
                f"UCX_SM_SYL_RemoteLandingSite_01_{index:02d}",
                (-105.0 + dx, -90.0 + dy, 22.5),
                (0.65, 0.65, 45.0),
            )
        )
    export_selection(
        ROOT / "SM_SYL_RemoteLandingSite_01.fbx",
        [site, *collisions],
    )
    print("Exported remote terrain and landing-site FBX assets")


if __name__ == "__main__":
    main()
