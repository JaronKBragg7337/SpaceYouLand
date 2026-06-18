"""Fortis corner watchtower (headless Blender, meters, Z up).
Trussed 4-leg tower: splayed legs + cross-braces + mid ring, railed platform,
enclosed cabin with window slits, slanted roof + peak, searchlight + antenna.
Single steel mesh. ~3 m footprint, ~9.6 m tall (overlooks the ~5 m walls).
Origin at base center; searchlight faces +X."""
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

# legs + feet
for sx in (-1.0,1.0):
    for sy in (-1.0,1.0):
        box((sx,sy,3.1), (0.3,0.3,6.2))
        box((sx,sy,0.2), (0.55,0.55,0.4))
# mid ring
box((0, 1.0,3.0), (2.3,0.25,0.3)); box((0,-1.0,3.0), (2.3,0.25,0.3))
box(( 1.0,0,3.0), (0.25,2.3,0.3)); box((-1.0,0,3.0), (0.25,2.3,0.3))
# face cross-braces
box(( 1.0,0,3.0), (0.22,0.22,5.9), 'X',  20)
box((-1.0,0,3.0), (0.22,0.22,5.9), 'X', -20)
box((0, 1.0,3.0), (0.22,0.22,5.9), 'Y', -20)
box((0,-1.0,3.0), (0.22,0.22,5.9), 'Y',  20)
# platform + railing
box((0,0,6.3), (3.0,3.0,0.35))
box((0, 1.45,6.8), (3.0,0.12,0.5)); box((0,-1.45,6.8), (3.0,0.12,0.5))
box(( 1.45,0,6.8), (0.12,3.0,0.5)); box((-1.45,0,6.8), (0.12,3.0,0.5))
# cabin + window slits
box((0,0,7.6), (2.4,2.4,2.2))
box((0, 1.21,7.9), (1.4,0.1,0.4)); box((0,-1.21,7.9), (1.4,0.1,0.4))
box(( 1.21,0,7.9), (0.1,1.4,0.4)); box((-1.21,0,7.9), (0.1,1.4,0.4))
# roof + peak
box((0,0,8.85), (2.9,2.9,0.3))
box((0,0,9.2), (1.0,1.0,0.5))
# searchlight (+X) + antenna
box((1.25,0,7.0), (0.6,0.55,0.55))
box((-1.0,-1.0,9.7), (0.12,0.12,1.6))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("SM_Fortis_Watchtower")
bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("SM_Fortis_Watchtower", me)
bpy.context.collection.objects.link(ob)
ob.select_set(True); bpy.context.view_layer.objects.active = ob
out = os.path.join(OUT, "Fortis_Watchtower.fbx")
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'},
                         apply_unit_scale=True, global_scale=1.0,
                         axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
print("WATCHTOWER_OK", out, "verts", len(me.vertices), "tris~", sum(len(p.vertices)-2 for p in me.polygons))
