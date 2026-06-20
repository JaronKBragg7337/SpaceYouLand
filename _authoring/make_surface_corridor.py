"""Author the first contiguous, curvature-correct SYL surface corridor.

The corridor is two neighboring tangent-frame tiles on the same 6,360 km
sphere: Home spans -1..+1 km along the route and Remote spans +1..+3 km.
Their shared edge is mathematically coincident after the remote tile actor is
placed at 2 km arc distance and pitched to radial up.  Both tiles carry coarse
closed convex collision and deterministic vertex-colour lithology authored
from real metre coordinates; the global geoid remains only the distant round
silhouette.
"""

from dataclasses import dataclass
from math import cos, sin, sqrt
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
PLANET_RADIUS_M = 6_360_000.0
HALF_ROUTE_M = 1_000.0
HALF_CROSS_ROUTE_M = 2_000.0


@dataclass(frozen=True)
class Tile:
    asset_name: str
    arc_center_m: float


TILES = (
    Tile("SM_SYL_SurfaceTile_Home_02", 0.0),
    Tile("SM_SYL_SurfaceTile_Remote_02", 2_000.0),
)

BASALT = (0.045, 0.075, 0.085)
IRON_RICH = (0.34, 0.075, 0.025)
PALE_SILICATE = (0.34, 0.29, 0.17)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def spherical_height(x: float, y: float) -> float:
    """Height below a tile's tangent plane, in metres."""
    return sqrt(PLANET_RADIUS_M**2 - x * x - y * y) - PLANET_RADIUS_M


def home_tangent_coordinates(tile: Tile, x: float, y: float, z: float):
    """Map tile-local metres into the home tangent frame for shared colouring."""
    angle = tile.arc_center_m / PLANET_RADIUS_M
    center_x = PLANET_RADIUS_M * sin(angle)
    world_x = center_x + cos(angle) * x + sin(angle) * z
    return world_x, y


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = clamp((value - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def mix(a, b, amount: float):
    return tuple(x + (y - x) * amount for x, y in zip(a, b))


def lithology_weights(x: float, y: float):
    iron_field = (
        0.55 * sin((x + 0.42 * y) / 360.0)
        + 0.30 * sin((0.31 * x - y) / 155.0)
        + 0.15 * sin((x + y) / 73.0)
    )
    basin_field = (
        0.60 * sin((x - 1_250.0) / 620.0)
        + 0.25 * cos((y + 180.0) / 280.0)
        + 0.15 * sin((x - 0.6 * y) / 110.0)
    )
    iron_weight = smoothstep(-0.35, 0.35, iron_field)
    basin_weight = smoothstep(0.10, 0.72, basin_field)
    return iron_weight, basin_weight


def lithology_colour(x: float, y: float):
    """Broad mineral regions used as physical surface navigation landmarks."""
    iron_weight, basin_weight = lithology_weights(x, y)
    colour = mix(BASALT, IRON_RICH, iron_weight * 0.78)
    colour = mix(colour, PALE_SILICATE, basin_weight * 0.72)
    return colour


def lithology_region(x: float, y: float) -> int:
    """Return the dominant authored material section for reliable FBX import."""
    iron_weight, basin_weight = lithology_weights(x, y)
    if basin_weight > 0.58:
        return 2
    if iron_weight > 0.52:
        return 1
    return 0


def grid_vertices(tile: Tile, segments_x: int, segments_y: int):
    vertices = []
    colours = []
    for iy in range(segments_y + 1):
        y = -HALF_CROSS_ROUTE_M + 2.0 * HALF_CROSS_ROUTE_M * iy / segments_y
        for ix in range(segments_x + 1):
            x = -HALF_ROUTE_M + 2.0 * HALF_ROUTE_M * ix / segments_x
            z = spherical_height(x, y)
            vertices.append((x, y, z))
            home_x, home_y = home_tangent_coordinates(tile, x, y, z)
            colours.append(lithology_colour(home_x, home_y))
    return vertices, colours


def grid_faces(segments_x: int, segments_y: int):
    faces = []
    row = segments_x + 1
    for iy in range(segments_y):
        for ix in range(segments_x):
            a = iy * row + ix
            b = a + 1
            d = (iy + 1) * row + ix
            c = d + 1
            faces.append((a, b, c, d))
    return faces


def make_render_mesh(tile: Tile, segments_x: int = 64, segments_y: int = 128):
    mesh = bpy.data.meshes.new(tile.asset_name)
    vertices, colours = grid_vertices(tile, segments_x, segments_y)
    mesh.from_pydata(vertices, [], grid_faces(segments_x, segments_y))
    mesh.update()

    colour_layer = mesh.color_attributes.new(
        name="SYL_Lithology",
        type="BYTE_COLOR",
        domain="CORNER",
    )
    for polygon in mesh.polygons:
        polygon.use_smooth = True
        center = sum(
            (mesh.vertices[index].co for index in polygon.vertices),
            start=mesh.vertices[polygon.vertices[0]].co.copy() * 0.0,
        ) / len(polygon.vertices)
        home_x, home_y = home_tangent_coordinates(
            tile,
            center.x,
            center.y,
            center.z,
        )
        polygon.material_index = lithology_region(home_x, home_y)
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            colour_layer.data[loop_index].color = (*colours[vertex_index], 1.0)

    obj = bpy.data.objects.new(tile.asset_name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(bpy.data.materials.new("Basalt"))
    obj.data.materials.append(bpy.data.materials.new("IronRich"))
    obj.data.materials.append(bpy.data.materials.new("PaleSilicate"))
    return obj


def perimeter(segments_x: int, segments_y: int):
    points = []
    points.extend((ix, 0) for ix in range(segments_x + 1))
    points.extend((segments_x, iy) for iy in range(1, segments_y + 1))
    points.extend((ix, segments_y) for ix in range(segments_x - 1, -1, -1))
    points.extend((0, iy) for iy in range(segments_y - 1, 0, -1))
    return points


def make_collision(tile: Tile, segments_x: int = 8, segments_y: int = 16):
    name = f"UCX_{tile.asset_name}_00"
    mesh = bpy.data.meshes.new(name)
    vertices, _ = grid_vertices(tile, segments_x, segments_y)
    faces = grid_faces(segments_x, segments_y)
    border = perimeter(segments_x, segments_y)
    bottom_indices = []
    for ix, iy in border:
        x = -HALF_ROUTE_M + 2.0 * HALF_ROUTE_M * ix / segments_x
        y = -HALF_CROSS_ROUTE_M + 2.0 * HALF_CROSS_ROUTE_M * iy / segments_y
        bottom_indices.append(len(vertices))
        vertices.append((x, y, -30.0))

    row = segments_x + 1
    for index, (ix0, iy0) in enumerate(border):
        ix1, iy1 = border[(index + 1) % len(border)]
        top0 = iy0 * row + ix0
        top1 = iy1 * row + ix1
        bot0 = bottom_indices[index]
        bot1 = bottom_indices[(index + 1) % len(border)]
        faces.append((top0, bot0, bot1, top1))
    faces.append(tuple(reversed(bottom_indices)))

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def export_tile(tile: Tile, objects) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=str(ROOT / f"{tile.asset_name}.fbx"),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        global_scale=1.0,
        axis_forward="-Z",
        axis_up="Y",
        mesh_smooth_type="FACE",
        colors_type="LINEAR",
    )


def main() -> None:
    for tile in TILES:
        clear_scene()
        render = make_render_mesh(tile)
        collision = make_collision(tile)
        export_tile(tile, [render, collision])
        print(f"Exported {tile.asset_name}")


if __name__ == "__main__":
    main()
