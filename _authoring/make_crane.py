"""Fortis build crane — authored from scratch, headless Blender.
Portal gantry: 2 box-section legs w/ cross-bracing, double main girder,
end ties, trolley + cable + hook block, operator cabin. Single steel mesh.
Modeled in meters (Z up). Exported GLB for Unreal import."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

# --- empty scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)
mesh = bpy.data.meshes.new("Fortis_BuildCrane")
obj = bpy.data.objects.new("Fortis_BuildCrane", mesh)
bpy.context.collection.objects.link(obj)
bm = bmesh.new()

def add_box(center, size, rot_axis=None, rot_deg=0.0):
    cx, cy, cz = center
    hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    corners = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
               (-hx,-hy, hz),(hx,-hy, hz),(hx,hy, hz),(-hx,hy, hz)]
    R = Matrix.Rotation(math.radians(rot_deg), 3, rot_axis) if (rot_axis and rot_deg) else None
    vs = []
    for c in corners:
        v = Vector(c)
        if R: v = R @ v
        vs.append(bm.verts.new(v + Vector((cx, cy, cz))))
    for f in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vs[i] for i in f])

# --- dimensions (meters) ---
span   = 11.0          # X distance between the two legs
lx     = span / 2.0
depth  = 3.0           # Y distance between the two columns of one leg
cy     = depth / 2.0
H      = 8.5           # height to underside of girder
col    = 0.45          # column cross-section
foot_z = 0.6
girder_len = 12.0
gy     = 1.0           # double girder offset in Y (girders at +/-gy)
gsec_y, gsec_z = 0.55, 0.85
girder_z = H + gsec_z / 2.0

# legs: 4 box columns
for sx in (-lx, lx):
    for sy in (-cy, cy):
        add_box((sx, sy, (foot_z + H) / 2.0), (col, col, H - foot_z))
# feet / bogies
for sx in (-lx, lx):
    for sy in (-cy, cy):
        add_box((sx, sy, foot_z / 2.0), (1.3, 0.9, foot_z))
# bottom sill + top tie per end (run along Y)
for sx in (-lx, lx):
    add_box((sx, 0, 0.55), (0.5, depth, 0.5))
    add_box((sx, 0, H - 0.3), (0.55, depth, 0.6))
# X cross-bracing on each end frame (Y-Z plane, rotate about X)
brace_len = math.hypot(depth, H - 1.4)
brace_ang = math.degrees(math.atan2(depth, H - 1.4))
for sx in (-lx, lx):
    add_box((sx, 0, (foot_z + H) / 2.0), (0.28, 0.26, brace_len), 'X',  brace_ang)
    add_box((sx, 0, (foot_z + H) / 2.0), (0.28, 0.26, brace_len), 'X', -brace_ang)
# double main girder (run along X) + end cross-ties
for g in (-gy, gy):
    add_box((0, g, girder_z), (girder_len, gsec_y, gsec_z))
for sx in (-lx, lx):
    add_box((sx, 0, girder_z), (0.6, 2 * gy + gsec_y, gsec_z * 0.9))
# walkway rail along one girder (thin)
add_box((0, gy + 0.5, girder_z + gsec_z / 2 + 0.5), (girder_len, 0.08, 1.0))

# trolley riding on top of the girders, offset toward +X (over the pad)
tx = 1.8
trolley_z = girder_z + gsec_z / 2.0 + 0.35
add_box((tx, 0, trolley_z), (1.6, 2.6, 0.7))
# hoist cable + hook block hanging below the trolley
tb = trolley_z - 0.35
cable_len = 4.2
add_box((tx, 0, tb - cable_len / 2.0), (0.14, 0.14, cable_len))
add_box((tx, 0, tb - cable_len - 0.35), (0.75, 0.75, 0.7))
# operator cabin slung under the girder near +X leg
add_box((lx - 1.6, 0, girder_z - 1.1), (1.4, 1.7, 1.5))

# --- finalize + export ---
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

out = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring\Fortis_BuildCrane.fbx"
os.makedirs(os.path.dirname(out), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=False, object_types={'MESH'},
                         apply_unit_scale=True, global_scale=1.0,
                         axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')

tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
print("CRANE_EXPORT_OK", out, "verts", len(mesh.vertices), "polys", len(mesh.polygons), "tris~", tris)
