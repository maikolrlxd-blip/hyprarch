"""Reacciones estilizadas al fuego para la zombi existente. Blender, sin dano real."""
import sys,math,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import bpy
from mathutils import Vector
import ap_lib as A
import ap_armas as W
from clip_contacts import reset_pose,correct_fall_contact
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'fuentes'/'Base-zombi.blend'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
for im in bpy.data.images:
    if im.type=='IMAGE' and '_Color' in im.name:
        frozen=ROOT/'texturas'/im.name
        if not frozen.exists():raise RuntimeError('Falta atlas local: '+str(frozen))
        im.filepath=str(frozen);im.reload()
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');reset_pose(rig)
obs=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
for act in list(bpy.data.actions):bpy.data.actions.remove(act)
names=[b.name for b in rig.data.bones]
sc=bpy.context.scene;sc.render.fps=60;sc.render.threads_mode='FIXED';sc.render.threads=3
c=A.Clip(rig,'QuemadoInicio',.85)
for t,head,torso,la,ra in [(0,(-7,4,0),(-6,0,0),(16,0,0),(20,0,0)),
 (.15,(19,-13,8),(12,0,-9),(80,20,-8),(108,-18,13)),
 (.42,(-12,9,-6),(-12,0,9),(115,29,-8),(65,-12,8)),
 (.85,(-6,-4,0),(-8,0,0),(72,18,0),(84,-14,0))]:
    c.k('Head',t,rot=head);c.k('UpperTorso',t,rot=torso)
    c.k('LeftUpperArm',t,rot=la);c.k('RightUpperArm',t,rot=ra)
    c.k('LeftLowerArm',t,rot=(40,0,0));c.k('RightLowerArm',t,rot=(35,0,0))
    c.k('HumanoidRootPart',t,loc=(0,0,.03))
acts={'QuemadoInicio':c.build(names)}
c=A.Clip(rig,'QuemadoBucle',1.2,True)
for i in range(9):
    t=i*.15;s=math.sin(math.tau*t/1.2);co=math.cos(math.tau*t/1.2)
    c.k('UpperTorso',t,rot=(-8+5*s,0,6*s));c.k('Head',t,rot=(-6+8*co,-4+8*s,5*s))
    c.k('LeftUpperArm',t,rot=(72+24*s,18+7*co,0));c.k('RightUpperArm',t,rot=(84-24*s,-14-8*co,0))
    c.k('LeftLowerArm',t,rot=(40+15*co,0,0));c.k('RightLowerArm',t,rot=(35-15*co,0,0))
    c.k('LeftHand',t,rot=(-20+8*s,0,4*co));c.k('RightHand',t,rot=(-12-8*s,0,-4*co))
    c.k('HumanoidRootPart',t,loc=(0,0,.03))
acts['QuemadoBucle']=c.build(names)
c=A.Clip(rig,'QuemadoCaer',1.8)
for t,root,torso,head,arm,knee in [(0,(0,0,.03),(-8,0,0),(-6,0,0),78,-8),
 (.32,(0,0,-.25),(-18,0,8),(12,-10,0),110,-40),
 (.72,(0,.12,-1.0),(-25,0,-8),(-15,8,0),62,-90),
 (1.20,(0,0,-2.25),(82,0,0),(18,0,-15),22,-15),
 (1.8,(0,0,-2.35),(90,0,0),(23,0,-18),12,-8)]:
    c.k('HumanoidRootPart',t,loc=root)
    c.k('LowerTorso',t,rot=(torso[0],0,0));c.k('UpperTorso',t,rot=(0,0,torso[2]))
    c.k('Head',t,rot=head)
    c.k('LeftUpperArm',t,rot=(arm,30 if t<.8 else -70,0));c.k('RightUpperArm',t,rot=(arm+12,-25 if t<.8 else 72,0))
    c.k('LeftLowerArm',t,rot=(18,0,0));c.k('RightLowerArm',t,rot=(25,0,0))
    c.k('LeftUpperLeg',t,rot=(40 if .3<t<1 else -6,0,0));c.k('RightUpperLeg',t,rot=(20 if .3<t<1 else 4,0,0))
    c.k('LeftLowerLeg',t,rot=(knee,0,0));c.k('RightLowerLeg',t,rot=(knee*.75,0,0))
acts['QuemadoCaer']=c.build(names)
contact=correct_fall_contact(rig,obs,acts['QuemadoCaer'],60,expected_name='QuemadoCaer')
A.write_json(str(ROOT/'qa'/'CONTACTO-CAIDA.json'),contact)
reset_pose(rig)
texdir=ROOT/'texturas';texdir.mkdir(exist_ok=True)
for im in bpy.data.images:
    if im.type=='IMAGE' and '_Color' in im.name:
        im.filepath_raw=str(texdir/(im.name if im.name.endswith('.png') else im.name+'.png'));im.file_format='PNG';im.save()
bpy.ops.file.pack_all();A.save_blend(str(ROOT/'Zombi_Quemado.blend'))
A.set_action(rig,acts['QuemadoInicio']);A.export_fbx(str(ROOT/'Zombi_Quemado.fbx'),[rig]+obs,anim=True,all_actions=True)
for name,act in acts.items():A.set_action(rig,act);A.export_fbx(str(ROOT/'clips'/f'Zombi_{name}.fbx'),[rig]+obs,anim=True)
reset_pose(rig);A.export_glb(str(ROOT/'Zombi_Quemado.glb'),[rig]+obs,anim=True)
A.write_json(str(ROOT/'datos.json'),{'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'triangles':A.tris(obs),'bones':len(names),'clips':{'QuemadoInicio':.85,'QuemadoBucle':1.2,'QuemadoCaer':1.8},'scope':'Reacciones Blender; sin prueba Roblox. La muerte la decide el servidor, nunca el VFX.'})
CC=A.collection('QA_Quemado_Camaras');CR=A.collection('QA_Quemado_Ref')
A.setup_world((.50,.54,.58),.85);A.add_lights(CC);W.backdrop(CR,0,30,(.4,.42,.40))
W.hide_only({'Zombi','QA_Quemado_Camaras','QA_Quemado_Ref'})
A.setup_render((600,600),'CYCLES',16);sc.render.threads_mode='FIXED';sc.render.threads=3
cam=W.look_cam(CC,'QuemadoCam',(0,0,2.55),(.75,1,.18),13,50)
items=[]
for i,(name,t) in enumerate([('QuemadoInicio',.15),('QuemadoInicio',.42),('QuemadoBucle',.3),('QuemadoBucle',.9),('QuemadoCaer',.72),('QuemadoCaer',1.8)]):
    reset_pose(rig);A.set_action(rig,acts[name]);sc.frame_set(round(t*60))
    p=ROOT/'previews'/f'Zombi-quemado-v01-{i:02d}-Blender.png';A.render(str(p),cam);items.append((str(p),f'{name.upper()} {t:.2f}s'))
W.contact_sheet(items,3,str(ROOT/'previews'/'Zombi-quemado-v01-secuencia-Blender.png'),title='LUTO - REACCIONES AL FUEGO - BLENDER, SIN VFX')
print('BURN_BUILD_DONE')
