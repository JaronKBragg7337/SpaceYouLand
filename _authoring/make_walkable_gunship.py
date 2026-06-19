"""SYL Fortis walkable gunship vertical slice (Blender 5.1, meters, Z-up).

Creates a modular, human-scale dropship rather than a sealed vehicle prop.
Fixed pieces are authored in ship-local coordinates.  Ramp and pressure door
are authored around their own pivots so Unreal can animate them physically.

Exports:
  Fortis_Gunship_PhysicsDeck.fbx physics root / walkable floor + landing contacts
  Fortis_Gunship_Exterior.fbx   armored hull, wings, engines, landing gear
  Fortis_Gunship_Interior.fbx   cockpit, seat, cargo bay, ribs and equipment
  Fortis_Gunship_Trim.fbx       red armor trim and hazard rails
  Fortis_Gunship_Glass.fbx      cockpit glazing
  Fortis_Gunship_Fasteners.fbx  modeled bolts and panel clamps
  Fortis_Gunship_Ramp.fbx       rear ramp, pivot at forward hinge
  Fortis_Gunship_Door.fbx       sliding pressure door, pivot at lower center
  Fortis_Gunship_Identity.fbx   raised FORTIS 01 hull marking
"""
import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

OUT = r"C:\Users\lilli\Documents\Unreal Projects\CurtisAILab\_authoring"
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)


def box(bm, center, size, rot_axis=None, rot_deg=0.0):
    cx, cy, cz = center
    hx, hy, hz = (size[0] / 2, size[1] / 2, size[2] / 2)
    corners = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    rotation = Matrix.Rotation(math.radians(rot_deg), 3, rot_axis) if rot_axis else None
    verts = []
    for corner in corners:
        value = Vector(corner)
        if rotation:
            value = rotation @ value
        verts.append(bm.verts.new(value + Vector((cx, cy, cz))))
    for face in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([verts[index] for index in face])


def wedge(bm, x0, x1, y0, y1, z_bottom, z0_top, z1_top):
    """Eight-vertex wedge running along X; useful for armored nose/roof plates."""
    coords = [
        (x0, y0, z_bottom), (x1, y0, z_bottom),
        (x1, y1, z_bottom), (x0, y1, z_bottom),
        (x0, y0, z0_top), (x1, y0, z1_top),
        (x1, y1, z1_top), (x0, y1, z0_top),
    ]
    verts = [bm.verts.new(Vector(value)) for value in coords]
    for face in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([verts[index] for index in face])


def cylinder(bm, center, radius, depth, segments=20, axis='Z'):
    result = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=radius, depth=depth,
    )
    rotation = None
    if axis == 'X':
        rotation = Matrix.Rotation(math.radians(90), 3, 'Y')
    elif axis == 'Y':
        rotation = Matrix.Rotation(math.radians(90), 3, 'X')
    for vert in result['verts']:
        if rotation:
            vert.co = rotation @ vert.co
        vert.co += Vector(center)


def finalize(bm, name, bevel=0.025):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if bevel:
        modifier = obj.modifiers.new("ManufacturedEdgeRadius", 'BEVEL')
        modifier.width = bevel
        modifier.segments = 2
        modifier.limit_method = 'ANGLE'
    return obj


def export_object(obj, filename):
    for candidate in bpy.context.scene.objects:
        candidate.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = os.path.join(OUT, filename)
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'MESH'},
        apply_unit_scale=True, global_scale=1.0,
        axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
    )
    tris = sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    print("EXPORT_OK", filename, "verts", len(obj.data.vertices), "base_tris", tris)


def collision_box_object(name, center, size):
    collision_bm = bmesh.new()
    box(collision_bm, center, size)
    return finalize(collision_bm, name, bevel=0.0)


def export_objects(objects, filename):
    for candidate in bpy.context.scene.objects:
        candidate.select_set(False)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    path = os.path.join(OUT, filename)
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'MESH'},
        apply_unit_scale=True, global_scale=1.0,
        axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
    )
    print("EXPORT_OK", filename, "objects", len(objects), "custom_collision", len(objects) - 1)


# ---------------------------------------------------------------------------
# Physics deck.  A low, solid slab gives the ship a stable root body while the
# rest of the hollow collision cage is assembled from Blueprint box components.
# ---------------------------------------------------------------------------
bm = bmesh.new()
box(bm, (-0.45, 0, 0.48), (10.9, 3.65, 0.28))
box(bm, (-0.8, 0, 0.25), (8.6, 0.55, 0.32))              # keel
box(bm, (-4.9, 0, 0.38), (1.0, 3.85, 0.48))             # ramp hinge beam
for sx in (-3.55, 2.45):
    for sy in (-1.55, 1.55):
        box(bm, (sx, sy, -0.05), (0.22, 0.22, 0.95))     # load-bearing strut
        box(bm, (sx, sy, -0.58), (1.15, 0.42, 0.18))    # ground-contact pad
deck = finalize(bm, "SM_Fortis_Gunship_PhysicsDeckV2", bevel=0.035)
export_object(deck, "Fortis_Gunship_PhysicsDeck.fbx")

# Exact compound collision for the simulated body.  UE recognizes UCX_* meshes
# as collision hulls and welds them into one rigid body without self-collision.
ucx_specs = [
    ((-0.45, 0, 0.48), (10.9, 3.65, 0.28)),
    ((-0.8, 0, 0.25), (8.6, 0.55, 0.32)),
    ((-4.9, 0, 0.38), (1.0, 3.85, 0.48)),
]
for sx in (-3.55, 2.45):
    for sy in (-1.55, 1.55):
        ucx_specs.append(((sx, sy, -0.05), (0.22, 0.22, 0.95)))
        ucx_specs.append(((sx, sy, -0.58), (1.15, 0.42, 0.18)))
collision_objects = []
for index, (center, size) in enumerate(ucx_specs):
    collision_objects.append(collision_box_object(
        f"UCX_SM_Fortis_Gunship_PhysicsDeckV2_{index:02d}", center, size
    ))
export_objects([deck] + collision_objects, "Fortis_Gunship_PhysicsDeckV2.fbx")


# ---------------------------------------------------------------------------
# Exterior shell.  The rear is intentionally open for the pressure door/ramp.
# Overall hull 14 m long, 4.4 m wide; wing span 10 m; interior clear height 2.6 m.
# ---------------------------------------------------------------------------
bm = bmesh.new()
# Armored side shells and upper shoulders
for sy in (-2.02, 2.02):
    box(bm, (-0.55, sy, 1.85), (10.7, 0.28, 2.7))
    box(bm, (-0.35, sy * 0.94, 3.13), (9.3, 0.34, 0.36), 'X', 0)
    for xp in (-4.7, -3.15, -1.55, 0.05, 1.65, 3.25):
        box(bm, (xp, sy * 1.035, 1.85), (0.18, 0.22, 2.75))
# Roof and armored belly edges
box(bm, (-0.8, 0, 3.32), (8.7, 3.9, 0.26))
box(bm, (-0.8, -1.88, 0.47), (9.0, 0.35, 0.42))
box(bm, (-0.8, 1.88, 0.47), (9.0, 0.35, 0.42))
# Faceted cockpit/nose around a hollow cabin
wedge(bm, 3.55, 6.55, -1.85, -1.5, 0.55, 3.15, 2.05)
wedge(bm, 3.55, 6.55, 1.5, 1.85, 0.55, 3.15, 2.05)
wedge(bm, 3.65, 6.65, -1.48, 1.48, 0.55, 0.92, 0.62)
wedge(bm, 3.55, 6.3, -1.5, 1.5, 2.82, 3.18, 2.12)
box(bm, (6.3, 0, 1.33), (0.35, 2.9, 1.35), 'Y', -8)
# Rear pressure frame
for sy in (-1.82, 1.82):
    box(bm, (-5.82, sy, 1.82), (0.4, 0.46, 2.95))
box(bm, (-5.82, 0, 3.18), (0.4, 3.9, 0.42))
# Wings and engine pylons
for sy in (-3.45, 3.45):
    box(bm, (-1.1, sy, 1.45), (3.4, 3.0, 0.24), 'X', 0)
    box(bm, (-2.2, sy, 1.75), (2.8, 0.45, 0.55))
for sy in (-3.75, 3.75):
    cylinder(bm, (-2.55, sy, 2.05), 0.72, 3.8, 24, 'X')
    cylinder(bm, (-4.55, sy, 2.05), 0.82, 0.28, 24, 'X')
    cylinder(bm, (-4.82, sy, 2.05), 0.6, 0.25, 24, 'X')
# Tail shoulders and stabilizers
box(bm, (-4.85, 0, 3.78), (1.6, 0.34, 1.45), 'Y', -12)
for sy in (-2.35, 2.35):
    box(bm, (-4.65, sy, 3.05), (1.8, 2.2, 0.2))
# Landing gear with real round struts and broad feet
for sx in (-3.55, 2.45):
    for sy in (-1.55, 1.55):
        cylinder(bm, (sx, sy, -0.05), 0.11, 0.95, 16, 'Z')
        box(bm, (sx, sy, -0.58), (1.15, 0.42, 0.18))
exterior = finalize(bm, "SM_Fortis_Gunship_Exterior", bevel=0.045)
export_object(exterior, "Fortis_Gunship_Exterior.fbx")


# ---------------------------------------------------------------------------
# Interior: walkable cargo bay, cockpit, real seat/console and equipment.
# ---------------------------------------------------------------------------
bm = bmesh.new()
# Non-collision visual deck plating, ceiling liner, wall liners
box(bm, (-0.65, 0, 0.67), (10.0, 3.45, 0.10))
box(bm, (-0.75, 0, 3.10), (8.6, 3.45, 0.10))
for sy in (-1.77, 1.77):
    box(bm, (-0.8, sy, 1.88), (9.4, 0.10, 2.35))
# Floor panel seams and transverse structural ribs
for xp in (-4.65, -3.45, -2.25, -1.05, 0.15, 1.35, 2.55, 3.55):
    box(bm, (xp, 0, 0.735), (0.055, 3.35, 0.03))
for xp in (-4.7, -3.25, -1.75, -0.25, 1.25, 2.75):
    box(bm, (xp, -1.68, 1.88), (0.14, 0.16, 2.38))
    box(bm, (xp, 1.68, 1.88), (0.14, 0.16, 2.38))
    box(bm, (xp, 0, 3.02), (0.14, 3.38, 0.15))
# Cockpit bulkhead with open central passage
box(bm, (2.65, -1.25, 1.9), (0.16, 0.9, 2.35))
box(bm, (2.65, 1.25, 1.9), (0.16, 0.9, 2.35))
box(bm, (2.65, 0, 2.95), (0.16, 1.65, 0.25))
# Pilot seat facing +X, dimensioned for a human body
box(bm, (4.1, 0, 0.92), (0.75, 0.72, 0.32))
box(bm, (3.82, 0, 1.48), (0.22, 0.76, 0.95), 'Y', -12)
box(bm, (4.15, -0.5, 1.12), (0.75, 0.16, 0.18))
box(bm, (4.15, 0.5, 1.12), (0.75, 0.16, 0.18))
box(bm, (4.0, 0, 0.48), (0.26, 0.5, 0.65))
# Physical control console, side panels and overhead instrument block
wedge(bm, 4.55, 5.55, -1.05, 1.05, 0.73, 1.35, 1.05)
box(bm, (4.72, -1.4, 1.45), (1.2, 0.35, 1.15), 'Y', -8)
box(bm, (4.72, 1.4, 1.45), (1.2, 0.35, 1.15), 'Y', -8)
box(bm, (4.25, 0, 2.82), (1.3, 1.5, 0.2))
# Cargo bay benches and restraints
for sy in (-1.42, 1.42):
    box(bm, (-1.2, sy, 0.9), (4.7, 0.48, 0.28))
    box(bm, (-1.2, sy * 1.08, 1.38), (4.7, 0.16, 0.72), 'X', 4 if sy > 0 else -4)
    for xp in (-3.0, -1.8, -0.6, 0.6):
        box(bm, (xp, sy * 0.93, 1.12), (0.08, 0.08, 0.62))
# Equipment lockers, med cabinet, conduits
for xp in (-4.35, -3.55):
    box(bm, (xp, -1.48, 1.62), (0.65, 0.42, 1.55))
box(bm, (-4.0, 1.5, 1.7), (1.3, 0.38, 1.35))
for sy in (-1.25, 1.25):
    cylinder(bm, (-0.8, sy, 2.86), 0.055, 6.4, 12, 'X')
interior = finalize(bm, "SM_Fortis_Gunship_Interior", bevel=0.025)
export_object(interior, "Fortis_Gunship_Interior.fbx")


# ---------------------------------------------------------------------------
# Contrasting trim / hazard geometry.
# ---------------------------------------------------------------------------
bm = bmesh.new()
for sy in (-2.18, 2.18):
    box(bm, (-0.55, sy, 1.18), (10.25, 0.06, 0.14))
    box(bm, (-0.55, sy, 2.62), (10.25, 0.06, 0.10))
for sy in (-1.6, 1.6):
    box(bm, (-5.96, sy, 1.8), (0.06, 0.18, 2.55))
# Cockpit dashboard strips and cargo floor guides
box(bm, (5.0, 0, 1.22), (0.9, 1.7, 0.055), 'Y', -12)
for sy in (-1.35, 1.35):
    box(bm, (-1.0, sy, 0.79), (7.5, 0.08, 0.035))
# Engine bands
for sy in (-3.75, 3.75):
    cylinder(bm, (-3.3, sy, 2.05), 0.77, 0.12, 24, 'X')
trim = finalize(bm, "SM_Fortis_Gunship_Trim", bevel=0.012)
export_object(trim, "Fortis_Gunship_Trim.fbx")


# ---------------------------------------------------------------------------
# Cockpit glazing as distinct material component.
# ---------------------------------------------------------------------------
bm = bmesh.new()
wedge(bm, 4.05, 5.82, -1.37, -0.12, 2.52, 3.02, 2.08)
wedge(bm, 4.05, 5.82, 0.12, 1.37, 2.52, 3.02, 2.08)
box(bm, (4.75, -1.53, 2.33), (1.25, 0.055, 0.58), 'Y', -18)
box(bm, (4.75, 1.53, 2.33), (1.25, 0.055, 0.58), 'Y', -18)
glass = finalize(bm, "SM_Fortis_Gunship_Glass", bevel=0.015)
export_object(glass, "Fortis_Gunship_Glass.fbx")


# ---------------------------------------------------------------------------
# Modeled fasteners and clamps.  These cast real highlights instead of relying
# on a generic texture and remain authored from scratch.
# ---------------------------------------------------------------------------
bm = bmesh.new()
for sy in (-2.19, 2.19):
    for xp in (-5.1, -4.35, -3.6, -2.85, -2.1, -1.35, -0.6, 0.15, 0.9, 1.65, 2.4, 3.15):
        for zp in (0.92, 1.75, 2.58):
            cylinder(bm, (xp, sy, zp), 0.045, 0.055, 10, 'Y')
for xp in (-4.7, -3.25, -1.75, -0.25, 1.25, 2.75):
    for sy in (-1.55, 1.55):
        box(bm, (xp, sy, 3.11), (0.22, 0.18, 0.09))
fasteners = finalize(bm, "SM_Fortis_Gunship_Fasteners", bevel=0.008)
export_object(fasteners, "Fortis_Gunship_Fasteners.fbx")


# ---------------------------------------------------------------------------
# Rear ramp: local pivot at (0,0,0), geometry extends rearward along -X.
# Open rotation = zero; closed rotation = +78 degrees pitch in Unreal.
# ---------------------------------------------------------------------------
bm = bmesh.new()
box(bm, (-1.45, 0, 0), (2.9, 3.35, 0.20))
for sy in (-1.52, 1.52):
    box(bm, (-1.45, sy, 0.14), (2.9, 0.18, 0.28))
for xp in (-2.5, -1.75, -1.0, -0.25):
    box(bm, (xp, 0, 0.14), (0.10, 3.05, 0.12))
ramp = finalize(bm, "SM_Fortis_Gunship_Ramp", bevel=0.025)
export_object(ramp, "Fortis_Gunship_Ramp.fbx")


# Sliding pressure door: local pivot at lower center.  It lifts into the roof.
bm = bmesh.new()
box(bm, (0, 0, 1.15), (0.18, 3.28, 2.30))
box(bm, (-0.11, 0, 1.15), (0.08, 2.5, 1.55))
for sy in (-1.42, 1.42):
    box(bm, (-0.16, sy, 1.15), (0.08, 0.14, 2.05))
door = finalize(bm, "SM_Fortis_Gunship_Door", bevel=0.03)
export_object(door, "Fortis_Gunship_Door.fbx")


# Raised side identity marking, authored as actual geometry.
curve = bpy.data.curves.new("FortisIdentityText", type='FONT')
curve.body = "FORTIS  01"
curve.align_x = 'CENTER'
curve.align_y = 'CENTER'
curve.size = 0.34
curve.extrude = 0.025
identity = bpy.data.objects.new("SM_Fortis_Gunship_Identity", curve)
bpy.context.collection.objects.link(identity)
identity.location = (-0.2, -2.22, 2.05)
identity.rotation_euler = (math.radians(90), 0, 0)
for candidate in bpy.context.scene.objects:
    candidate.select_set(False)
identity.select_set(True)
bpy.context.view_layer.objects.active = identity
bpy.ops.object.convert(target='MESH')
identity = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
export_object(identity, "Fortis_Gunship_Identity.fbx")

print("WALKABLE_GUNSHIP_COMPLETE")
