import bpy,json,math,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fuentes'))
import ap_lib as A
from clip_contacts import reset_pose,_bounds
errors=[]
def check(c,m):
    if not c:errors.append(m)
def meshes(rig):
    return sorted([o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)],key=lambda o:o.name)
def signature(obs):
    return {o.name:{'co':[list(v.co) for v in o.data.vertices],'poly':[list(p.vertices) for p in o.data.polygons],'uv':[list(u.uv) for u in o.data.uv_layers.active.data]} for o in obs}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'fuentes'/'Base-zombi.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');original=signature(meshes(rig))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Zombi_Quemado.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');obs=meshes(rig)
check(signature(obs)==original,'La geometria o UV cambio frente a base')
check(len(obs)==15 and A.tris(obs)==1966 and len(rig.data.bones)==16,'Conteos diferentes')
check(rig.animation_data.action is None,'La pose guardada no esta neutral')
check(all(pb.matrix_basis.is_identity for pb in rig.pose.bones),'Pose residual')
used_images={n.image for o in obs for mat in o.data.materials if mat and mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
image_details=[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size),'pixels':len(i.pixels)} for i in used_images]
print('IMAGE_DETAILS',json.dumps(image_details))
check(len(used_images)==4 and all(i.packed_file and len(i.pixels)>0 for i in used_images),'Atlas usados no empaquetados')
for o in obs:
    check(all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in o.data.vertices),o.name+' pesos')
    check(all(math.isfinite(x) and -.0001<=x<=1.0001 for uv in o.data.uv_layers.active.data for x in uv.uv),o.name+' UV')
expected={'QuemadoInicio':.85,'QuemadoBucle':1.2,'QuemadoCaer':1.8}
check({a.name for a in bpy.data.actions}==set(expected),'Acciones mezcladas o faltantes')
minima={};loop_ends=[]
for name,secs in expected.items():
    act=bpy.data.actions[name];reset_pose(rig);A.set_action(rig,act)
    check(abs((act.frame_range[1]-act.frame_range[0])/60-secs)<.0001,name+' duracion')
    mins=[]
    for f in range(round(secs*60)+1):
        bpy.context.scene.frame_set(f);mins.append(_bounds(obs)['min'][2])
    minima[name]=min(mins)
    check(min(mins)>=-.001,name+' atraviesa suelo')
    if name=='QuemadoBucle':
        for f in [0,round(secs*60)]:
            bpy.context.scene.frame_set(f)
            loop_ends.append([list(pb.matrix[i]) for pb in rig.pose.bones for i in range(4)])
loop_delta=max(abs(x-y) for a,b in zip(*loop_ends) for x,y in zip(a,b))
check(loop_delta<1e-5,'Bucle discontinuo en extremos')
contact=json.loads((ROOT/'qa'/'CONTACTO-CAIDA.json').read_text())
check(contact['passed'],'Caida falla muestreo de cuartos de fotograma')
imports=[]
for name,secs in expected.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'clips'/f'Zombi_{name}.fbx'))
    ms=[o for o in bpy.data.objects if o.type=='MESH'];ar=[o for o in bpy.data.objects if o.type=='ARMATURE'];ac=list(bpy.data.actions)
    check(len(ms)==15 and A.tris(ms)==1966 and sum(len(a.data.bones) for a in ar)==16,name+' reimportacion rig/malla')
    dur=(ac[0].frame_range[1]-ac[0].frame_range[0])/bpy.context.scene.render.fps if ac else -1
    check(len(ac)==1 and abs(dur-secs)<.02,name+' reimportacion clip')
    imports.append({'clip':name,'seconds':dur})
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'Zombi_Quemado.glb'))
check(len(bpy.data.actions)==3,'GLB pierde acciones')
report={'passed':not errors,'errors':errors,'scope':'Blender y reimportacion FBX/GLB, no motor','geometry_uv_unchanged':True,'triangles':1966,'bones':16,'clips':imports,'min_z_integer_frames':minima,'fall_quarterframe_min_z':contact['after_min_z'],'loop_endpoint_matrix_error':loop_delta}
(ROOT/'qa'/'VALIDACION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BURN_QA',json.dumps(report))
if errors:raise RuntimeError(errors)
