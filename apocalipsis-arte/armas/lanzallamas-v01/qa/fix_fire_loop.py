"""Correccion puntual del cierre periodico, sin tocar otros clips/modelo/renders."""
import bpy,sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fuentes'))
import ap_lib as A
import ap_armas as W
from clip_contacts import reset_pose
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Lanzallamas.blend'))
c=W.ClipDef('Disparo',.60,loop=True)
for t in (0,.1,.2,.3,.4,.5,.6):
    wig=.5+.5*math.sin(math.tau*t/.2)
    c.v('Arma',t,(0,-.025*wig,.006*wig),(.6*wig,0,.25*math.sin(math.tau*t/.6*2)))
c.e(0,'fuego_sostener')
for tag in ('Mundo','VM'):
    rig=bpy.data.objects['Lanzallamas_'+tag];reset_pose(rig)
    bpy.data.actions.remove(bpy.data.actions[tag+'_Disparo'])
    action=c.build(rig,[b.name for b in rig.data.bones],tag=='VM');action.name=tag+'_Disparo'
    A.set_action(rig,action)
    obs=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig]
    A.export_fbx(str(ROOT/'clips'/f'Lanzallamas_{tag}_Disparo.fbx'),[rig]+obs,anim=True)
    reset_pose(rig)
A.save_blend(str(ROOT/'Lanzallamas.blend'))
for tag in ('Mundo','VM'):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Lanzallamas.blend'))
    for action in list(bpy.data.actions):
        if not action.name.startswith(tag+'_'):bpy.data.actions.remove(action)
    rig=bpy.data.objects['Lanzallamas_'+tag]
    obs=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig]
    A.set_action(rig,bpy.data.actions[tag+'_Reposo'])
    A.export_fbx(str(ROOT/f'Lanzallamas_{tag}.fbx'),[rig]+obs,anim=True,all_actions=True)
print('FIRE_LOOP_FIXED')
