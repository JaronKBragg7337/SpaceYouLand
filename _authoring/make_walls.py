"""Fortis perimeter: modular armored wall panel + gatehouse (headless Blender, meters, Z up).
Exports two FBX. Wall panel: 6 m wide (X), 0.7 thick (Y), ~5 m tall with battered base,
buttress ribs, crenellated parapet. Gate: twin towers flanking an X-axis opening with a
lintel + merlons. Single steel mesh each. Origin at base center."""
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

# ---- wall panel (6 m along X, faces +/-Y) ----
bm = bmesh.new()
box(bm, (0,0,2.25), (6.0,0.6,4.2))           # main panel
box(bm, (0,0,0.4),  (6.2,0.95,0.8))          # battered base
for x in (-2.5,0.0,2.5):                       # buttress ribs
    box(bm, (x,0,2.3), (0.5,0.85,4.6))
box(bm, (0,0,4.5), (6.0,0.85,0.5))           # parapet beam
for x in (-2.5,-1.25,0.0,1.25,2.5):           # merlons
    box(bm, (x,0,4.95), (0.55,0.9,0.6))
box(bm, (0,0,2.9), (3.2,0.66,0.3))           # vent band
export_one(finalize(bm,"SM_Fortis_WallPanel"), os.path.join(OUT,"Fortis_WallPanel.fbx"))

# ---- gatehouse (opening along X, towers flank in Y) ----
bm = bmesh.new()
for sy in (-3.3,3.3):                          # twin towers
    box(bm, (0,sy,3.3), (2.4,2.4,6.6))
    box(bm, (0,sy,6.8), (2.6,2.6,0.6))         # tower cap
    for mx in (-0.8,0.8):                       # tower merlons
        box(bm, (mx,sy,7.2), (0.5,2.4,0.6))
box(bm, (0,0,5.8), (2.6,6.8,1.5))             # lintel over opening
for y in (-2.5,-1.25,0.0,1.25,2.5):            # lintel merlons
    box(bm, (0,y,6.7), (2.4,0.5,0.7))
box(bm, (0,0,0.25), (3.2,7.0,0.5))            # threshold slab
box(bm, (0,-1.95,2.6), (2.2,0.3,4.4))         # inner door frame L
box(bm, (0, 1.95,2.6), (2.2,0.3,4.4))         # inner door frame R
export_one(finalize(bm,"SM_Fortis_Gate"), os.path.join(OUT,"Fortis_Gate.fbx"))
print("WALLS_DONE")
