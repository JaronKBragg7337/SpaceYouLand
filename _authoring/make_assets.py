"""SYL from-scratch asset kit (headless Blender, meters, Z up).
Exports one FBX per asset into _authoring/. Each built from box primitives;
the monolith sign uses a real 3D text object converted to mesh.
Assets: crate, ship hull frame (under construction), dedication monolith, sign text."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def new_bm():
    return bmesh.new()

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
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob

def export_one(ob, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, global_scale=1.0,
                             axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("EXPORT_OK", os.path.basename(path), "tris~", tris)

# ---------- 1. Supply crate (~1.0 x 1.0 x 0.85 m) ----------
bm = new_bm()
box(bm, (0,0,0.425), (0.92,0.92,0.85))                       # body
for sx in (-0.46, 0.46):                                       # corner posts
    for sy in (-0.46, 0.46):
        box(bm, (sx,sy,0.425), (0.12,0.12,0.85))
box(bm, (0,0,0.83), (1.02,1.02,0.10))                         # top rim
box(bm, (0,0,0.04), (1.02,1.02,0.08))                         # bottom rim
box(bm, (0, 0.47,0.45), (0.8,0.05,0.14))                      # front rib
box(bm, (0,-0.47,0.45), (0.8,0.05,0.14))                      # back rib
box(bm, ( 0.47,0,0.45), (0.05,0.8,0.14))                      # side rib +
box(bm, (-0.47,0,0.45), (0.05,0.8,0.14))                      # side rib -
export_one(finalize(bm, "SM_Fortis_Crate"), os.path.join(OUT, "Fortis_Crate.fbx"))

# ---------- 2. Ship hull frame under construction (~6.4 x 2.2 x 2.7 m) ----------
bm = new_bm()
box(bm, (0,0,0.35), (6.4,0.5,0.5))                            # keel beam
for xp in (-2.6,-1.3,0.0,1.3,2.6):                            # rib arches
    box(bm, (xp,-0.95,1.35), (0.18,0.18,2.0))                 # left post
    box(bm, (xp, 0.95,1.35), (0.18,0.18,2.0))                 # right post
    box(bm, (xp, 0.0, 2.35), (0.18,2.1,0.18))                 # top tie
box(bm, (-1.95,-1.02,1.0), (2.4,0.06,1.4))                    # partial plating (port, 2 bays)
box(bm, (-1.95, 1.02,1.0), (2.4,0.06,1.4))                    # partial plating (starboard)
box(bm, (3.1,0,1.0), (0.8,1.9,1.6), 'Y', 18)                  # bow cap (angled)
export_one(finalize(bm, "SM_Fortis_HullFrame"), os.path.join(OUT, "Fortis_HullFrame.fbx"))

# ---------- 3. Dedication monolith (~1.2 x 0.8 base, ~3.6 m tall) ----------
bm = new_bm()
box(bm, (0,0,0.15), (1.3,0.9,0.3))                            # plinth
box(bm, (0,0,1.95), (0.95,0.38,3.3))                          # shaft
box(bm, (0,0,3.7),  (1.05,0.5,0.18))                          # cap
box(bm, (0,0.21,2.1),(0.7,0.06,1.5))                          # raised plaque on +Y face
export_one(finalize(bm, "SM_Claude_Monolith"), os.path.join(OUT, "Claude_Monolith.fbx"))

# ---------- 4. Sign: real 3D text, baked upright facing -Y ----------
cur = bpy.data.curves.new("claude_text", type='FONT')
cur.body = "MADE BY\nCLAUDE CODE"
cur.align_x = 'CENTER'; cur.align_y = 'CENTER'
cur.size = 0.17; cur.extrude = 0.035
sign = bpy.data.objects.new("SM_Claude_Sign", cur)
bpy.context.collection.objects.link(sign)
for o in bpy.context.scene.objects: o.select_set(False)
sign.select_set(True); bpy.context.view_layer.objects.active = sign
bpy.ops.object.convert(target='MESH')
sign = bpy.context.view_layer.objects.active
# stand it upright (text lies in XY facing +Z) -> rotate +90 about X so it faces -Y, upright in Z
sign.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)
export_one(sign, os.path.join(OUT, "Claude_Sign.fbx"))

print("ALL_ASSETS_DONE")
