# Comprueba la escala de exportacion: importa FBX con los ajustes por defecto de Blender y mide.
# Convencion de Codex (probada en Studio con la roca Rock_Sentinel): global_scale=0.01 -> Blender lee metros = studs / 100,
# y Studio (que lee cm) vuelve a mostrar studs.
import bpy, sys, os
from mathutils import Vector

paths = sys.argv[sys.argv.index('--') + 1:]
for p in paths:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=p)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    mn = Vector((min(v.x for v in pts), min(v.y for v in pts), min(v.z for v in pts)))
    mx = Vector((max(v.x for v in pts), max(v.y for v in pts), max(v.z for v in pts)))
    d = mx - mn
    arm = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    acts = sorted(a.name for a in bpy.data.actions)
    print('CHK', os.path.basename(p), 'meshes', len(meshes), 'dim_blender(m) = (%.4f %.4f %.4f)' % tuple(d),
          '-> si Studio lee cm: studs = (%.3f %.3f %.3f)' % tuple(d * 100), 'armaduras', len(arm), 'acciones', acts)
