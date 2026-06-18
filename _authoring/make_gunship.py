"""Fortis gunship/dropship (headless Blender, meters, Z up).
Armored angular hull: fuselage, raked cockpit, chin turret, top spine,
twin rear engine nacelles + exhausts, stub wings with weapon pods, tail
fin + stabilizers, landing skids. Single steel mesh. ~11 m long. Nose = +X.
Origin at skid base center."""
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

# hull
box((0,0,1.8), (8.0,2.6,2.2))            # fuselage
box((0,0,0.7), (5.2,2.0,0.4))            # belly
box((4.6,0,1.75),(2.6,2.0,1.5),'Y',-12)  # raked nose
box((3.6,0,0.95),(0.9,0.9,0.7))          # chin turret
box((3.0,0,2.95),(1.9,1.7,1.0),'Y',-20)  # cockpit canopy
box((-0.3,0,3.05),(3.2,1.4,0.8))         # top spine / intake
# engines
for sy in (-1.15,1.15):
    box((-3.7,sy,2.05),(2.6,0.95,1.1))   # nacelle
    box((-5.05,sy,2.05),(0.5,1.05,1.05)) # exhaust ring
# wings + weapon pods
for sy in (-2.2,2.2):
    box((-0.3,sy,1.9),(1.3,2.0,0.4))
for sy in (-2.95,2.95):
    box((-0.3,sy,1.45),(1.9,0.5,0.5))    # weapon pod
# tail
box((-4.1,0,3.3),(1.4,0.3,1.9))          # vertical fin
for sy in (-0.95,0.95):
    box((-4.3,sy,2.5),(1.2,1.1,0.3))     # h-stabilizer
# landing skids + struts
for sy in (-1.2,1.2):
    box((0.3,sy,0.16),(4.8,0.26,0.28))   # skid rail
    for sx in (1.7,-1.6):
        box((sx,sy,0.55),(0.24,0.24,0.8))# strut

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("SM_Fortis_Gunship")
bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("SM_Fortis_Gunship", me)
bpy.context.collection.objects.link(ob)
ob.select_set(True); bpy.context.view_layer.objects.active = ob

out = os.path.join(OUT, "Fortis_Gunship.fbx")
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'},
                         apply_unit_scale=True, global_scale=1.0,
                         axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print("GUNSHIP_OK", out, "verts", len(me.vertices), "tris~", tris)
