"""Author the physical Fortis proximity/interaction panel kit.

The backing plate and illuminated lens are separate meshes so Blueprint can keep
the steel housing present while switching the emissive lens with real proximity
state. Units are meters; the panel face points toward local -X.
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
bpy.ops.wm.read_factory_settings(use_empty=True)


def box(bm, center, size):
    cx, cy, cz = center
    hx, hy, hz = (size[0] / 2, size[1] / 2, size[2] / 2)
    coords = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    verts = [bm.verts.new(Vector(p) + Vector((cx, cy, cz))) for p in coords]
    for face in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([verts[i] for i in face])


def cylinder_x(bm, center, radius, depth, segments=16):
    result = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=radius, depth=depth,
    )
    rotation = Matrix.Rotation(math.radians(90), 3, 'Y')
    for vert in result['verts']:
        vert.co = rotation @ vert.co
        vert.co += Vector(center)


def finish(bm, name, bevel=0.008):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new("ManufacturedEdgeRadius", 'BEVEL')
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


def prompt_text(body, name):
    """Create real raised lettering, upright and facing the panel's local -X."""
    curve = bpy.data.curves.new(name, type='FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = 0.075
    curve.extrude = 0.010
    curve.bevel_depth = 0.0015
    curve.bevel_resolution = 1
    curve.resolution_u = 8
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')

    # Blender font geometry starts in XY facing +Z. First stand it upright
    # facing -Y, then turn it clockwise around Z so it faces local -X.
    obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    obj.rotation_euler = (0, 0, math.radians(-90))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return obj


# Armored backing plate, raised bezel, cable boss, and four real fasteners.
base_bm = bmesh.new()
box(base_bm, (0.00, 0, 0), (0.060, 0.50, 0.28))
box(base_bm, (-0.040, 0, 0), (0.025, 0.42, 0.20))
box(base_bm, (0.045, 0, -0.19), (0.10, 0.18, 0.10))
for sy in (-0.205, 0.205):
    for sz in (-0.095, 0.095):
        cylinder_x(base_bm, (-0.055, sy, sz), 0.018, 0.020)
base = finish(base_bm, "SM_Fortis_InteractionPanel_Base")
export(base, "Fortis_InteractionPanel_Base.fbx")


# The lens protrudes from the rear-facing (-X) side and is switched by Blueprint.
lens_bm = bmesh.new()
box(lens_bm, (-0.068, 0, 0.045), (0.025, 0.30, 0.065))
for sy in (-0.125, 0.125):
    box(lens_bm, (-0.074, sy, 0.045), (0.012, 0.035, 0.095))
lens = finish(lens_bm, "SM_Fortis_InteractionPanel_Lens", bevel=0.006)
export(lens, "Fortis_InteractionPanel_Lens.fbx")


# Raised prompt lettering is physical geometry rather than screen-space UI.
ramp_prompt = prompt_text("E  RAMP", "SM_Fortis_InteractionPrompt_Ramp")
export(ramp_prompt, "Fortis_InteractionPrompt_Ramp.fbx")

pilot_prompt = prompt_text("E  PILOT", "SM_Fortis_InteractionPrompt_Pilot")
export(pilot_prompt, "Fortis_InteractionPrompt_Pilot.fbx")
