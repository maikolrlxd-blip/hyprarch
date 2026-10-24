import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fuentes'))
import ap_lib as A
from clip_contacts import reset_pose
errors=[]
def check(c,m):
    if not c:errors.append(m)
def geometry(obs):
    tris=0
    for ob in obs:
        me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles)
        used={i for p in me.polygons for i in p.vertices}
        check(len(used)==len(me.vertices),ob.name+' vertices sueltos')
        check(all(t.area>1e-12 for t in me.loop_triangles),ob.name+' degenerados')
        check(me.uv_layers.active is not None,ob.name+' UV faltantes')
        if me.uv_layers.active:check(all(math.isfinite(x) and -.0001<=x<=1.0001 for v in me.uv_layers.active.data for x in v.uv),ob.name+' UV invalidas')
    return tris
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Lanzallamas.blend'))
rw=bpy.data.objects['Lanzallamas_Mundo'];rv=bpy.data.objects['Lanzallamas_VM']
world=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==rw]
vm=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==rv]
tw=geometry(world);tv=geometry(vm)
check(tw<=800,'Presupuesto arma excedido');check(len(world)==3 and len(vm)==9,'Piezas inesperadas')
check(len(rw.data.bones)==3 and len(rv.data.bones)==10,'Rig incorrecto')
for rig,obs in [(rw,world),(rv,vm)]:
    check(rig.animation_data.action is None,rig.name+' no neutral')
    check(all(pb.location.length<1e-6 and sum(abs(x) for x in pb.rotation_euler)<1e-6 for pb in rig.pose.bones),rig.name+' pose residual')
    for o in obs:
        check(all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in o.data.vertices),o.name+' pesos incompletos')
tex=[im for im in bpy.data.images if im.type=='IMAGE' and '_Color' in im.name]
check(len(tex)==2 and all(i.packed_file for i in tex),'Texturas no empacadas')
events=json.loads((ROOT/'eventos.json').read_text());expected={'Equipar':.85,'Guardar':.65,'Reposo':2,'Disparo':.6,'Recargar':2.8,'Inspeccionar':3.2}
check(set(events['clips'])==set(expected),'Faltan clips del pedido')
for n,secs in expected.items():
    for tag in ('Mundo','VM'):
        act=bpy.data.actions.get(tag+'_'+n)
        check(act is not None,tag+'_'+n+' falta')
        if act:check(abs((act.frame_range[1]-act.frame_range[0])/60-secs)<.001,n+' duracion incorrecta')
    check(all(0<=e['t']<=secs for e in events['clips'][n]['eventos']),n+' eventos fuera de tiempo')
results=[]
loop_errors={}
for tag,rig in [('Mundo',rw),('VM',rv)]:
    for name in ('Reposo','Disparo'):
        reset_pose(rig);act=bpy.data.actions[tag+'_'+name];A.set_action(rig,act)
        endpoints=[]
        for f in (act.frame_range[0],act.frame_range[1]):
            bpy.context.scene.frame_set(round(f));endpoints.append([list(b.matrix[i]) for b in rig.pose.bones for i in range(4)])
        delta=max(abs(x-y) for a,b in zip(*endpoints) for x,y in zip(a,b))
        check(delta<1e-5,tag+'/'+name+' cierre discontinuo');loop_errors[tag+'/'+name]=delta
    reset_pose(rig)
masters=[]
for tag,num,tris,bones in [('Mundo',3,tw,3),('VM',9,tv,10)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/f'Lanzallamas_{tag}.fbx'))
    ms=[o for o in bpy.data.objects if o.type=='MESH'];ar=[o for o in bpy.data.objects if o.type=='ARMATURE']
    check(len(ms)==num and geometry(ms)==tris,tag+' master geometria')
    check(sum(len(o.data.bones) for o in ar)==bones,tag+' master rig')
    check(len(bpy.data.actions)==6,tag+' master acciones')
    masters.append({'rig':tag,'actions':len(bpy.data.actions)})
for ext in ('fbx','glb'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(ROOT/'Lanzallamas_Estatico.fbx'))
    else:bpy.ops.import_scene.gltf(filepath=str(ROOT/'Lanzallamas_Estatico.glb'))
    ms=[o for o in bpy.data.objects if o.type=='MESH']
    check({o.name for o in ms}=={'Handle','Cartucho','Cierre'},'Nombres estatico '+ext)
    check(geometry(ms)==tw,'Geometria estatico '+ext)
    check(not any(o.type=='ARMATURE' for o in bpy.data.objects),'Rig inesperado en estatico '+ext)
for tag,num,tris,bones in [('Mundo',3,tw,3),('VM',9,tv,10)]:
    for name,secs in expected.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(ROOT/'clips'/f'Lanzallamas_{tag}_{name}.fbx'),use_anim=True)
        ms=[o for o in bpy.data.objects if o.type=='MESH'];ar=[o for o in bpy.data.objects if o.type=='ARMATURE']
        check(len(ms)==num and geometry(ms)==tris,f'{tag}/{name} geometria diferente')
        check(sum(len(o.data.bones) for o in ar)==bones,f'{tag}/{name} huesos')
        actions=list(bpy.data.actions)
        check(len(actions)==1,f'{tag}/{name} acciones mezcladas')
        actual=(actions[0].frame_range[1]-actions[0].frame_range[0])/bpy.context.scene.render.fps if actions else -1
        check(abs(actual-secs)<.025,f'{tag}/{name} duracion importada {actual}')
        results.append({'clip':f'{tag}/{name}','meshes':len(ms),'seconds':actual})
report={'passed':not errors,'errors':errors,'scope':'Blender/FBX offline, no Studio ni revision visual completa','triangles_weapon':tw,'triangles_viewmodel':tv,'reimported_masters':masters,'loop_endpoint_matrix_errors':loop_errors,'reimported_clips':results}
(ROOT/'qa'/'VALIDACION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FLAME_QA',json.dumps(report))
if errors:raise RuntimeError(errors)
