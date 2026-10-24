"""Contact correction for the Blender Caer action; never edits other actions.

The correction is baked on the root bone. Geometry is measured after armature
evaluation in WORLD space, including the object's existing rotation and scale.
This is a Blender ground-contact check, not a Roblox physics validation.
"""
import math
import bpy
from mathutils import Matrix, Vector


def reset_pose(rig):
    """Detach the active action and clear every POSE-bone transform.

    Object transforms/rest bones are deliberately preserved. NLA tracks are
    muted so an old strip cannot silently contribute to a render/export.
    """
    ad = rig.animation_data_create()
    ad.action = None
    for track in ad.nla_tracks:
        track.mute = True
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pb.rotation_axis_angle = (0.0, 0.0, 1.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)
    rig.data.pose_position = 'POSE'
    bpy.context.view_layer.update()


def _assign(rig, action):
    ad = rig.animation_data_create()
    ad.action = action
    # Blender 4.4+/5.2 layered actions require an explicit slot.
    if hasattr(action, 'slots') and len(action.slots):
        ad.action_slot = action.slots[0]


def _evaluate(rig, action, frame):
    reset_pose(rig)
    _assign(rig, action)
    whole = math.floor(frame)
    bpy.context.scene.frame_set(whole, subframe=frame - whole)
    bpy.context.view_layer.update()


def _bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    minimum = [float('inf')] * 3
    maximum = [-float('inf')] * 3
    lowest = None
    count = 0
    for ob in objs:
        if ob.type != 'MESH':
            continue
        ev = ob.evaluated_get(dg)
        mesh = ev.to_mesh()
        try:
            for v in mesh.vertices:
                p = ev.matrix_world @ v.co
                if not all(math.isfinite(x) for x in p):
                    raise ValueError('Non-finite evaluated vertex in ' + ob.name)
                if p.z < minimum[2]:
                    lowest = ob.name
                for i in range(3):
                    minimum[i] = min(minimum[i], p[i])
                    maximum[i] = max(maximum[i], p[i])
                count += 1
        finally:
            ev.to_mesh_clear()
    if count == 0:
        raise ValueError('No mesh vertices to measure')
    return {'min': minimum, 'max': maximum, 'lowest_mesh': lowest}


def _location_for_world_shift(rig, pb, world_z):
    # Move the POSE matrix by the requested world vector, then convert it back
    # to basis space. This covers rotated/scaled armatures, rotated rest bones,
    # and root bones with parents; direct location.z += delta would not.
    desired = pb.matrix.copy()
    desired.translation += rig.matrix_world.to_3x3().inverted() @ Vector((0, 0, world_z))
    kw = {}
    if pb.parent:
        kw['parent_matrix'] = pb.parent.matrix
        kw['parent_matrix_local'] = pb.parent.bone.matrix_local
    basis = pb.bone.convert_local_to_pose(desired, pb.bone.matrix_local,
                                          invert=True, **kw)
    return basis.to_translation().copy()


def _linear_root_keys(rig, action, root):
    from bpy_extras import anim_utils
    ad = rig.animation_data
    cb = anim_utils.action_get_channelbag_for_slot(action, ad.action_slot)
    curves = list(cb.fcurves) if cb else []
    path = 'pose.bones["%s"].location' % root
    for fc in curves:
        if fc.data_path == path:
            for key in fc.keyframe_points:
                key.interpolation = 'LINEAR'
            fc.update()


def correct_fall_contact(rig, objs, action, fps):
    """Bake world-Z floor correction into Caer; return before/after evidence.

    Uses full evaluated meshes, not object bounding-box corners. All integer
    frames are keyed; additional midpoint keys are added only if verification
    finds a penetration between frames. Positive-only shifts retain intentional
    airborne poses. Input geometry, other actions and object transforms survive.
    Ends with no active action and a clean neutral pose.
    """
    if action.name.split('.')[0] != 'Caer':
        raise ValueError('Ground correction is restricted to the Caer action')
    if fps <= 0 or rig.type != 'ARMATURE':
        raise ValueError('A rig and a positive fps are required')
    root = 'HumanoidRootPart'
    if root not in rig.pose.bones:
        raise ValueError('Missing root bone HumanoidRootPart')
    objs = list(objs)
    pb = rig.pose.bones[root]
    start = float(action.frame_start if action.use_frame_range else action.frame_range[0])
    end = float(action.frame_end if action.use_frame_range else action.frame_range[1])
    frames = sorted(set([start, end] + [float(f) for f in range(math.ceil(start), math.floor(end) + 1)]))
    floor = 0.02
    safety = 0.001
    baseline, corrections, after = [], {}, []
    try:
        # First measure the untouched action in full. Inserting keys as we
        # measure would change interpolation and contaminate the baseline.
        for frame in frames:
            _evaluate(rig, action, frame)
            bb = _bounds(objs)
            delta = max(0.0, floor + safety - bb['min'][2])
            local = _location_for_world_shift(rig, pb, delta)
            baseline.append({'frame': frame, 'seconds': frame / fps, **bb})
            corrections[frame] = {'world_z': delta, 'local': list(local)}
        _assign(rig, action)
        for frame, record in corrections.items():
            pb.location = record['local']
            pb.keyframe_insert('location', frame=frame, group=root)
        _linear_root_keys(rig, action, root)
        # Verify at quarter frames. A fast rotation can dip below a floor even
        # with correct integer poses; add only those contact keys, then recheck.
        checkframes = sorted(set([start, end] + [start + i * .25 for i in range(int((end - start) * 4) + 1)]))
        for iteration in range(4):
            pending = []
            after = []
            for frame in checkframes:
                _evaluate(rig, action, frame)
                bb = _bounds(objs)
                after.append({'frame': frame, 'seconds': frame / fps, **bb})
                if bb['min'][2] < floor - 1e-5:
                    dz = floor + safety - bb['min'][2]
                    pending.append((frame, dz, list(_location_for_world_shift(rig, pb, dz))))
            if not pending:
                break
            if iteration == 3:
                break
            _assign(rig, action)
            for frame, dz, loc in pending:
                pb.location = loc
                pb.keyframe_insert('location', frame=frame, group=root)
                old = corrections.get(frame, {'world_z': 0.0})
                corrections[frame] = {'world_z': old['world_z'] + dz, 'local': loc, 'extra_subframe': True}
            _linear_root_keys(rig, action, root)
        return {
            'action': action.name, 'fps': fps, 'floor_world_z': floor,
            'root': root, 'space': 'evaluated world-space vertices',
            'verification_step_frames': .25,
            'passed': min(r['min'][2] for r in after) >= floor - 1e-5,
            'before_min_z': min(r['min'][2] for r in baseline),
            'after_min_z': min(r['min'][2] for r in after),
            'before': baseline, 'after': after,
            'rootshift': [{'frame': f, **r} for f, r in sorted(corrections.items())],
            'scope': 'Blender sampled contact only; Roblox runtime unverified',
        }
    finally:
        reset_pose(rig)
