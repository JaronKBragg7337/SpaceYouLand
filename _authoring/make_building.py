"""Fortis modular armored building (headless Blender, meters, Z up).
Boxy armored hull: foundation lip, corner buttresses, parapet roof,
recessed doorway, wall vents, a battered armor panel, roof vent + antenna.
Single steel mesh. Footprint ~8x8 m, ~6.5 m tall. Origin at base center."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new()

def box(center, size, rot_axis=None, rot_deg=0.0):
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

# foundation + hull
box((0,0,0.2), (8.2,8.2,0.4))
box((0,0,2.7), (7.4,7.4,5.0))
# corner buttresses
for sx in (-3.6,3.6):
    for sy in (-3.6,3.6):
        box((sx,sy,2.6), (0.9,0.9,5.4))
# parapet roof rim
box((0, 3.8,5.4), (8.0,0.4,0.8))
box((0,-3.8,5.4), (8.0,0.4,0.8))
box((-3.8,0,5.4), (0.4,8.0,0.8))
box(( 3.8,0,5.4), (0.4,8.0,0.8))
box((0,0,5.25), (7.2,7.2,0.3))             # roof slab
# doorway on +X face
box((3.75,0,1.5), (0.5,2.2,3.0))           # surround
box((3.95,0,1.25),(0.25,1.3,2.4))          # door (proud)
box((4.25,0,0.2), (1.1,2.4,0.4))           # step
# wall vent slits
box((0, 3.72,3.7), (3.2,0.2,0.4))
box((0,-3.72,3.7), (3.2,0.2,0.4))
box(( 3.72,2.0,3.7), (0.2,1.6,0.4))
# battered armor panel on -X face (angled)
box((-3.75,0,2.4), (0.55,5.2,3.4), 'Y', 14)
# roof details
box((1.6,1.6,5.75), (1.5,1.5,0.8))         # vent block
box((-1.9,-1.9,6.4), (0.2,0.2,1.8))        # antenna stub
box((-1.9,1.9,5.7), (1.0,1.0,0.5))         # roof box

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("SM_Fortis_Building")
bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("SM_Fortis_Building", me)
bpy.context.collection.objects.link(ob)
ob.select_set(True); bpy.context.view_layer.objects.active = ob

out = os.path.join(OUT, "Fortis_Building.fbx")
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'},
                         apply_unit_scale=True, global_scale=1.0,
                         axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print("BUILDING_OK", out, "verts", len(me.vertices), "tris~", tris)
