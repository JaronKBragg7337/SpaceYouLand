"""Fortis servicing props (headless Blender, meters, Z up). Two FBX.
FuelDrum: real cylinder barrel w/ rim bands (~0.65 m tall).
Antenna: box mast + crossbars + a radar drum + whip (~5.9 m tall).
Single steel mesh each. Origin at base center."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def box(bm, center, size):
    cx, cy, cz = center
    hx, hy, hz = size[0]/2.0, size[1]/2.0, size[2]/2.0
    corners = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
               (-hx,-hy, hz),(hx,-hy, hz),(hx,hy, hz),(-hx,hy, hz)]
    vs = [bm.verts.new(Vector(c)+Vector((cx,cy,cz))) for c in corners]
    for f in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vs[i] for i in f])

def cyl(bm, center, radius, depth, segs=12):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                                radius1=radius, radius2=radius, depth=depth)
    for v in res['verts']:
        v.co = v.co + Vector(center)

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

# fuel drum
bm = bmesh.new()
cyl(bm, (0,0,0.33), 0.32, 0.62)
cyl(bm, (0,0,0.60), 0.34, 0.07)   # top rim
cyl(bm, (0,0,0.06), 0.34, 0.07)   # bottom rim
cyl(bm, (0,0,0.33), 0.34, 0.05)   # mid band
export_one(finalize(bm,"SM_Fortis_FuelDrum"), os.path.join(OUT,"Fortis_FuelDrum.fbx"))

# antenna mast
bm = bmesh.new()
box(bm, (0,0,0.15), (0.7,0.7,0.3))      # base
box(bm, (0,0,2.0),  (0.25,0.25,4.0))    # mast
for z in (2.5,3.0,3.5):
    box(bm, (0,0,z), (1.6,0.1,0.1))     # crossbars
cyl(bm, (0,0,4.25), 0.5, 0.28)          # radar drum
box(bm, (0,0,4.95), (0.06,0.06,1.3))    # whip
export_one(finalize(bm,"SM_Fortis_Antenna"), os.path.join(OUT,"Fortis_Antenna.fbx"))
print("SERVICE_DONE")
