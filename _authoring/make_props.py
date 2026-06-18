"""Fortis courtyard prop kit (headless Blender, meters, Z up). Two FBX.
Barrier: chunky armored blast barrier (~1.8 m long, ~1.3 m tall).
Floodlight: 5 m pole + cross-arm + tilted lamp housing (head faces +Y).
Single steel mesh each. Origin at base center."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def box(bm, center, size, rot_axis=None, rot_deg=0.0):
    cx, cy, cz = center
    hx, hy, hz = size[0]/2.0, size[1]/2.0, size[2]/2.0
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

def finalize(bm, name):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob

def export_one(ob, path):
    for o in bpy.context.scene.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, global_scale=1.0,
                             axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
    print("EXPORT_OK", os.path.basename(path), "tris~", sum(len(p.vertices)-2 for p in ob.data.polygons))

# blast barrier (long axis X)
bm = bmesh.new()
box(bm, (0,0,0.18), (1.8,0.85,0.36))
box(bm, (0,0,0.52), (1.8,0.6,0.36))
box(bm, (0,0,0.92), (1.8,0.4,0.45))
box(bm, (0,0,1.2),  (1.85,0.46,0.12))     # hazard cap
for sx in (-0.9,0.9):                       # end ribs
    box(bm, (sx,0,0.6), (0.12,0.9,1.1))
export_one(finalize(bm,"SM_Fortis_Barrier"), os.path.join(OUT,"Fortis_Barrier.fbx"))

# floodlight pole (head faces +Y)
bm = bmesh.new()
box(bm, (0,0,0.12), (0.6,0.6,0.24))         # foot
box(bm, (0,0,2.6),  (0.22,0.22,5.0))        # pole
box(bm, (0,0.3,5.0), (0.22,0.9,0.22))       # cross arm
box(bm, (0,0.7,4.85),(0.95,0.55,0.5), 'X', -22)  # tilted lamp housing
export_one(finalize(bm,"SM_Fortis_Floodlight"), os.path.join(OUT,"Fortis_Floodlight.fbx"))
print("PROPS_DONE")
