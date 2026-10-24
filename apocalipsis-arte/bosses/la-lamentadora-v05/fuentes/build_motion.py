"""Revision de movimiento sobre snapshot v04. No rebake ni cambios de rostro."""
import sys, math, json, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import bpy
from mathutils import Vector
import ap_lib as A
import ap_armas as W
from clip_contacts import reset_pose,correct_fall_contact
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'fuentes'/'Base-v04.blend'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
reset_pose(rig)
obs=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
head=next(o for o in obs if o.name=='Head')
sc=bpy.context.scene
sc.render.threads_mode='FIXED';sc.render.threads=3
# Identificar mechones como componentes topologicos separados: preserva UV y pintura.
adj={v.index:set() for v in head.data.vertices}
for e in head.data.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
remaining=set(adj);components=[]
while remaining:
    todo=[remaining.pop()];ids=[]
    while todo:
        i=todo.pop();ids.append(i)
        for j in adj[i]&remaining:remaining.remove(j);todo.append(j)
    components.append(ids)
locks=[]
for ids in components:
    if len(ids) not in (25,30):continue
    zs=[head.data.vertices[i].co.z for i in ids]
    if max(zs)-min(zs)<.7 or max(zs)<9.6:continue
    locks.append(ids)
locks.sort(key=lambda ids:sum(head.data.vertices[i].co.x for i in ids)/len(ids))
assert len(locks)==11,('Esperados 11 mechones',len(locks))
specs=[]
for j,ids in enumerate(locks):
    coords=[head.data.vertices[i].co.copy() for i in ids]
    lo=min(v.z for v in coords);hi=max(v.z for v in coords)
    root=sum(sorted(coords,key=lambda v:-v.z)[:5],Vector())/5
    mid=sum(sorted(coords,key=lambda v:abs(v.z-(hi+lo)*.5))[:5],Vector())/5
    specs.append({'ids':ids,'lo':lo,'hi':hi,'root':root,'mid':mid,'a':f'Cabello{j:02d}_Base','b':f'Cabello{j:02d}_Punta'})
A.select_only([rig]);bpy.ops.object.mode_set(mode='EDIT')
for s in specs:
    a=rig.data.edit_bones.new(s['a']);a.head=s['root'];a.tail=s['root']+Vector((0,.15,0));a.parent=rig.data.edit_bones['Head']
    b=rig.data.edit_bones.new(s['b']);b.head=s['mid'];b.tail=s['mid']+Vector((0,.15,0));b.parent=a
bpy.ops.object.mode_set(mode='OBJECT')
for s in specs:
    va=head.vertex_groups.new(name=s['a']);vb=head.vertex_groups.new(name=s['b'])
    vh=head.vertex_groups['Head']
    for i in s['ids']:
        t=(s['hi']-head.data.vertices[i].co.z)/(s['hi']-s['lo'])
        rootfade=min(1,max(0,t/.25));tipfade=min(1,max(0,(t-.38)/.50))
        vh.remove([i]);weights=[(vh,1-rootfade),(va,rootfade*(1-tipfade)),(vb,rootfade*tipfade)]
        for g,w in weights:
            if w>1e-7:g.add([i],w,'REPLACE')
for pb in rig.pose.bones:pb.rotation_mode='XYZ'
acts={a.name:a for a in bpy.data.actions}
# Lamento: anticipacion que avisa, arqueo, sostenido y recuperacion. Sin desplazamiento de pies.
c=A.Clip(rig,'Lamento',2.8,False)
# La suela neutral de la base cruza Z=0 por 0.00336 studs; margen constante.
c.k('HumanoidRootPart',0,loc=(0,0,.024)).k('HumanoidRootPart',2.8,loc=(0,0,.024))
poses=[
 (0,(-16,0,0),(-7,18,0),(12,4,0),(14,-4,0),12),
 (.48,(-28,0,-5),(-28,12,-8),(72,12,-5),(78,-8,3),48),
 (.78,(-30,0,-6),(-34,8,-7),(82,12,-5),(88,-8,3),52),
 (1.10,(7,0,2),(34,5,0),(96,36,-9),(101,-32,7),16),
 (1.38,(5,0,-2),(29,-5,4),(94,34,-9),(100,-35,7),20),
 (1.65,(6,0,3),(33,6,-4),(96,38,-8),(99,-31,7),18),
 (2.10,(-9,0,0),(8,12,0),(40,15,0),(45,-14,0),30),
 (2.8,(-16,0,0),(-7,18,0),(12,4,0),(14,-4,0),12)]
for t,torso,hd,la,ra,el in poses:
    c.k('UpperTorso',t,rot=torso);c.k('Head',t,rot=hd)
    c.k('LeftUpperArm',t,rot=la);c.k('RightUpperArm',t,rot=ra)
    c.k('LeftLowerArm',t,rot=(el,0,0));c.k('RightLowerArm',t,rot=(el+5,0,0))
    c.k('LeftHand',t,rot=(-16,8,4));c.k('RightHand',t,rot=(-20,-6,-4))
acts['Lamento']=c.build([b.name for b in rig.data.bones])
# Movimiento secundario horneado: no simulacion impredecible ni fisica en tiempo real.
for name,act in acts.items():
    reset_pose(rig);A.set_action(rig,act)
    length=(act.frame_range[1]-act.frame_range[0])/60
    for f in sorted(set(range(0,round(length*60)+1,4))|{round(length*60)}):
        sc.frame_set(f);t=f/60
        for j,s in enumerate(specs):
            fringe=(s['hi']-s['lo'])<1.3
            factor=.35 if fringe else 1
            for namebone,delay,amp in ((s['a'],.03,1),(s['b'],.10,1.8)):
                phase=j*.43
                if name in ('Reposo','Caminar'):
                    strength=1.5 if name=='Reposo' else 3.0
                    a=strength*math.sin(math.tau*(t/length-delay)+phase)
                    b=strength*.45*math.sin(math.tau*t/length+phase+.8)
                elif name=='Lamento':
                    # Latigazo moderado hacia atras durante el arqueo; asentamiento posterior.
                    q=t-delay-.87
                    a=0 if q<0 else 11*math.exp(-q*1.7)*math.sin(q*7)
                    b=0 if q<0 else 2.5*math.exp(-q*2)*math.sin(q*9+phase)
                elif name=='Atacar':
                    q=t-delay-.25
                    a=0 if q<0 else 7*math.exp(-q*5)*math.sin(q*12)
                    b=a*.25*math.sin(phase)
                else:
                    a=4*math.sin(math.pi*t/max(.1,length))
                    b=1.5*math.sin(math.pi*t/max(.1,length)+phase)
                pb=rig.pose.bones[namebone]
                pb.rotation_euler=tuple(math.radians(v*factor*amp) for v in (a,b,0))
                pb.keyframe_insert('rotation_euler',frame=f,group=namebone)
    for fc in A._fcurves(rig):
        if 'Cabello' in fc.data_path:
            for k in fc.keyframe_points:k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
    act.use_fake_user=True
contact=correct_fall_contact(rig,obs,acts['Caer'],60)
A.write_json(str(ROOT/'qa'/'CONTACTO-CAIDA.json'),contact)
reset_pose(rig)
for im in bpy.data.images:
    if im.type=='IMAGE' and '_Color' in im.name:
        im.filepath=str(ROOT/'texturas'/Path(im.filepath).name)
bpy.ops.file.pack_all()
report={'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'triangles':A.tris(obs),'meshes':len(obs),'bones':len(rig.data.bones),'hair_locks':len(specs),'clips':list(acts),'scope':'Blender, no Roblox','hair_vertices':[{'base':s['a'],'tip':s['b'],'indices':s['ids']} for s in specs]}
A.write_json(str(ROOT/'datos.json'),report)
A.save_blend(str(ROOT/'LaLamentadora.blend'))
A.set_action(rig,acts['Reposo'])
A.export_fbx(str(ROOT/'LaLamentadora_Skinned.fbx'),[rig]+obs,anim=True,all_actions=True)
for name,act in acts.items():
    A.set_action(rig,act);A.export_fbx(str(ROOT/'clips'/f'LaLamentadora_{name}.fbx'),[rig]+obs,anim=True)
reset_pose(rig)
A.export_glb(str(ROOT/'LaLamentadora_Skinned.glb'),[rig]+obs,anim=True)
for o in obs:o.name+='_rig'
cst,stat=W.static_copies(obs)
for a,b in zip(stat,obs):a.name=b.name[:-4]
A.export_fbx(str(ROOT/'LaLamentadora_Estatico.fbx'),stat)
W.remove_collection(cst)
for o in obs:o.name=o.name[:-4]
# Renders reales de una secuencia, rostro v04 intacto.
CC=A.collection('Revision_v05');CR=A.collection('Ref_v05')
A.setup_world((.50,.54,.58),.85);A.add_lights(CC)
W.backdrop(CR,0,40,(.4,.42,.40))
W.hide_only({'Zombi','Revision_v05','Ref_v05'})
A.setup_render((800,800),'CYCLES',20);sc.render.threads_mode='FIXED';sc.render.threads=3
cam=W.look_cam(CC,'Lamento_v05',Vector((0,0,5.1)),(.55,1,.1),25,50)
items=[]
for n,t in enumerate((0,.48,.78,1.1,1.65,2.8)):
    reset_pose(rig);A.set_action(rig,acts['Lamento']);sc.frame_set(round(t*60))
    p=ROOT/'previews'/f'Lamentadora-v05b-Lamento-{n:02d}-Blender.png'
    A.render(str(p),cam);items.append((str(p),f'LAMENTO {t:.2f}s'))
W.contact_sheet(items,3,str(ROOT/'previews'/'Lamentadora-v05b-Lamento-secuencia-Blender.png'),title='LA LAMENTADORA v05b - LAMENTO - BLENDER')
reset_pose(rig)
print('BOSS_V05_BUILD',json.dumps({k:v for k,v in report.items() if k!='hair_vertices'}))
