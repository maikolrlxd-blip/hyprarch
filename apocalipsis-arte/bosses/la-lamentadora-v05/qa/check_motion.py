import sys,json,hashlib,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fuentes'))
import ap_lib as A
from clip_contacts import reset_pose,_bounds
errors=[]
def check(c,m):
    if not c:errors.append(m)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'LaLamentadora.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
head=bpy.data.objects['Head']
obs=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
meta=json.loads((ROOT/'datos.json').read_text())
hair=set(i for s in meta['hair_vertices'] for i in s['indices'])
check(len(rig.data.bones)==38,'Se esperaban 38 huesos')
check(len(hair)==325,'Se esperaban 325 vertices de mechones')
max_influences=max(len([g for g in v.groups if g.weight>0]) for v in head.data.vertices)
check(max_influences<=3,'Demasiadas influencias')
rest={o.name:{'verts':[tuple(v.co) for v in o.data.vertices],'uv':[tuple(v.uv) for v in o.data.uv_layers.active.data]} for o in obs}
def local_vertices(frame):
    reset_pose(rig);A.set_action(rig,bpy.data.actions['Lamento']);bpy.context.scene.frame_set(frame)
    dg=bpy.context.evaluated_depsgraph_get();ob=head.evaluated_get(dg);me=ob.to_mesh()
    inv=(rig.matrix_world@rig.pose.bones['Head'].matrix@rig.data.bones['Head'].matrix_local.inverted()).inverted()
    result=[inv@ob.matrix_world@v.co for v in me.vertices];ob.to_mesh_clear();return result
a=local_vertices(0);b=local_vertices(72)
hair_shift=max((a[i]-b[i]).length for i in hair)
face_shift=max((a[i]-b[i]).length for i in range(len(a)) if i not in hair)
check(hair_shift>.01,'Mechones no se mueven de forma independiente')
check(face_shift<.00005,'El movimiento del pelo altera la cara')
floor=1e9
for f in range(169):
    reset_pose(rig);A.set_action(rig,bpy.data.actions['Lamento']);bpy.context.scene.frame_set(f)
    floor=min(floor,_bounds(obs)['min'][2])
check(floor>-.0001,'Lamento atraviesa plano del suelo')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'fuentes'/'Base-v04.blend'))
same=True
for name,data in rest.items():
    o=bpy.data.objects[name]
    same &= data['verts']==[tuple(v.co) for v in o.data.vertices]
    same &= data['uv']==[tuple(v.uv) for v in o.data.uv_layers.active.data]
check(same,'La geometria o UV difiere de v04')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'LaLamentadora_Skinned.glb'))
glb_actions=[a.name for a in bpy.data.actions]
check(len(glb_actions)==5,'GLB no conserva cinco acciones')
check(sum(len(o.data.bones) for o in bpy.data.objects if o.type=='ARMATURE')==38,'GLB no conserva huesos')
report={'passed':not errors,'errors':errors,'scope':'Blender offline, no fisica Roblox ni aceptacion visual',
        'same_geometry_uv_as_v04':same,'hair_vertices':len(hair),'max_weights':max_influences,
        'hair_motion_head_local_studs':hair_shift,'other_head_motion_studs':face_shift,
        'Lamento_min_z_integer_frames':floor,'glb_actions':glb_actions}
(ROOT/'qa'/'VALIDACION-MOVIMIENTO.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('MOTION_QA',json.dumps(report))
if errors:raise RuntimeError(errors)
