"""Build the clear Fortis development apron used for vehicle integration tests.

The apron is a real 36 m x 28 m load-bearing steel platform, not an editor-only
floor.  Plate joints, perimeter beams, tie-down sockets, and safety markings are
modeled as geometry.  Coordinates are meters; the Unreal placement supplies the
world-space location.
"""
import bpy
import bmesh
import os
from mathutils import Vector

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
bpy.ops.wm.read_factory_settings(use_empty=True)


def box(bm, center, size):
    cx, cy, cz = center
    hx, hy, hz = (size[0] / 2, size[1] / 2, size[2] / 2)
    points = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    verts = [bm.verts.new(Vector(p) + Vector((cx, cy, cz))) for p in points]
    for face in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([verts[i] for i in face])


def cylinder(bm, center, radius, depth, segments=20):
    result = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=radius, depth=depth,
    )
    for vert in result['verts']:
        vert.co += Vector(center)


def finish(bm, name, bevel=0.02):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new("FabricatedEdgeRadius", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj


def export(obj, filename):
    for candidate in bpy.context.scene.objects:
        candidate.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, filename), use_selection=True,
        object_types={'MESH'}, apply_unit_scale=True, global_scale=1.0,
        axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
    )
    print("EXPORT_OK", filename, len(obj.data.vertices), len(obj.data.polygons))


# Structural apron: 45 cm slab with perimeter beams and flush tie-down sockets.
base = bmesh.new()
box(base, (0, 0, 0), (36.0, 28.0, 0.45))
for x in (-17.65, 17.65):
    box(base, (x, 0, -0.18), (0.30, 28.0, 0.55))
for y in (-13.65, 13.65):
    box(base, (0, y, -0.18), (36.0, 0.30, 0.55))

# Plate-joint cover strips create a legible engineering grid without fake texture.
for x in range(-15, 16, 5):
    box(base, (x, 0, 0.235), (0.045, 27.3, 0.025))
for y in range(-12, 13, 4):
    box(base, (0, y, 0.235), (35.3, 0.045, 0.025))

# Recessed-looking tie-down cups: dark steel cylinders sit nearly flush.
for x in (-15, -10, -5, 0, 5, 10, 15):
    for y in (-10, -5, 0, 5, 10):
        cylinder(base, (x, y, 0.245), 0.10, 0.035, segments=16)

apron = finish(base, "SM_Fortis_DevelopmentApron", bevel=0.025)
export(apron, "Fortis_DevelopmentApron.fbx")


# Raised safety paint geometry: open center, broad corner brackets, center datum.
marks = bmesh.new()
z = 0.275
for sx in (-1, 1):
    for sy in (-1, 1):
        box(marks, (sx * 15.6, sy * 11.6, z), (3.8, 0.18, 0.035))
        box(marks, (sx * 16.9, sy * 10.3, z), (0.18, 2.8, 0.035))
for x in range(-12, 13, 4):
    box(marks, (x, 0, z), (1.8, 0.12, 0.035))
box(marks, (0, -12.8, z), (8.0, 0.20, 0.035))
markings = finish(marks, "SM_Fortis_DevelopmentApron_Markings", bevel=0.008)
export(markings, "Fortis_DevelopmentApron_Markings.fbx")
