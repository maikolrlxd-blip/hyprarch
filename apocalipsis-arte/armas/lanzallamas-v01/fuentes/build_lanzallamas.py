"""Asset ficticio de videojuego LUTO. Poli Pintado. No diseno tecnico funcional."""
import sys,math,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import bpy,numpy as np
from mathutils import Vector
import ap_lib as A
import ap_armas as W
from clip_contacts import reset_pose
ROOT=Path(__file__).resolve().parent.parent
A.clean_scene();A.REGIONS.clear()
sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=3
CM=A.collection('Arma_Mundo');CV=A.collection('Arma_VM')
mb=A.MB('Handle')
# Silueta industrial de fantasia: cuerpo acodado, carcasa, boquilla ancha.
mb.prism([(-.42,.14),(-.32,.62),(.84,.62),(1.18,.44),(1.10,.12)],-.25,.25,'oliva',plane='YZ')
mb.box((0,.12,.67),(.30,.42,.12),'metal',bevel=.018)
mb.prism([(-.30,.20),(-.04,.14),(-.10,-.50),(-.33,-.47)],-.11,.11,'goma',plane='YZ')
mb.seg_box((-.20,-.25,-.40),(-.20,.19,-.35),.055,.06,'metal')
mb.seg_box((-.20,.19,-.35),(-.20,.18,.16),.055,.06,'metal')
mb.cyl((0,.88,.32),(0,2.47,.32),.13,8,'metal')
mb.lathe((0,1.72,.32),(0,2.72,.32),[(.19,0),(.26,.16),(.26,.85),(.21,1)],8,'metal',close1=False)
mb.cyl((0,2.68,.32),(0,2.74,.32),.19,8,'oscuro',cap1=True)
mb.box((-.28,.46,.40),(.045,.53,.24),'amarillo')
mb.box((.28,.46,.40),(.045,.53,.24),'amarillo')
# Asa lateral compacta, deja visible el cartucho de recarga por debajo.
mb.seg_box((-.22,.92,.16),(-.48,.92,-.02),.08,.08,'metal')
mb.seg_box((-.48,.92,-.02),(-.48,1.30,-.02),.12,.12,'goma')
mb.seg_box((-.48,1.30,-.02),(-.17,1.30,.24),.08,.08,'metal')
# Placa de indicador y remaches pintados en textura, no geometria de mecanismo.
mb.box((0,.04,.76),(.24,.24,.035),'indicador')
handle=mb.finish(CM,recalc=True)
mb=A.MB('Cartucho')
mb.lathe((0,.48,-.91),(0,.48,.14),[(.19,0),(.24,.08),(.24,.84),(.14,1)],8,'rojo')
mb.cyl((0,.48,-.94),(0,.48,-.84),.25,8,'metal')
mb.box((-.245,.48,-.37),(.018,.25,.27),'etiqueta')
cart=mb.finish(CM,origin=(0,.48,-.25),recalc=True)
mb=A.MB('Cierre');mb.box((.30,.22,.05),(.08,.30,.07),'laton');lever=mb.finish(CM,origin=(.30,.36,.05),recalc=True)
parts=[handle,cart,lever]
tris=A.tris(parts);print('FLAME_TRIS',tris)
assert tris<=800,('Presupuesto arma',tris)
A.uv_unwrap(parts,angle=55,margin=.005)
ref=bpy.data.objects.new('PinturaPos',None);CM.objects.link(ref)
maps=A.bake_maps(parts,1024,R=4,ao_dist=.18,bevel_r=.016,samples=12,pos_ref=ref)
P=A.Paint(maps,R=4)
def detail(kind):
    def fn(P,mask,pos,nrm,col):
        x,y,z=pos.T
        if kind=='metal':
            vent=(y>1.91)&(y<2.48)&(abs(x)>.14)&(np.sin(y*39)>.40)
            col[vent]*=.35
            soot=np.clip((y-2.35)*2,0,.65);col*=1-soot[:,None]
        if kind=='amarillo':
            stripe=(np.sin(y*30+z*22)>.35)
            col[stripe]=col[stripe]*.25
        if kind=='goma':
            rib=(np.sin(z*55+y*25)>.65);col[rib]*=.65
        if kind=='indicador':
            q=((x)/.08)**2+((y-.04)/.08)**2
            col[q<1]=(.66,.69,.55);col[q<.35]=(.14,.20,.18)
        if kind=='etiqueta':
            mark=(abs(y-.48)<.055)&(abs(z+.37)<.085)
            col[mark]=(.20,.20,.16)
        return col
    return fn
styles={'oliva':('#52604b','#9b9f7d'),'metal':('#46505b','#a3abb3'),'goma':('#2e302c','#686b57'),
 'amarillo':('#aa9656','#cfbd83'),'rojo':('#855040','#bc8c66'),'oscuro':('#161c22','#53575c'),
 'indicador':('#404d48','#a2ad8e'),'etiqueta':('#b5b09a','#d1c9a9'),'laton':('#98815b','#c7b884')}
for reg,(color,edge) in styles.items():
    P.region(reg,color,var=.10,stroke=(1,4,1.8),stroke_scale=9,blotch=.09,ao=.60,light=.24,
             edge_col=edge,edge=.85,edge_th=.025,edge_break=.45,grime=.25,dust=.12,seed=11,extra=detail(reg))
tex=ROOT/'texturas'/'Lanzallamas_Color.png';P.save(str(tex),1024)
A.assign_final(parts,A.final_material('Lanzallamas_PoliPintado',str(tex)))
bpy.data.objects.remove(ref,do_unlink=True)
BW=['Arma','Cartucho','Cierre']
rw=A.make_armature('Lanzallamas_Mundo',[('Arma',(0,0,0),None,.2),('Cartucho',tuple(cart.location),'Arma',.15),('Cierre',tuple(lever.location),'Arma',.12)],CM)
for o,bone in zip(parts,BW):A.skin_rigid(o,rw,bone)
# Viewmodel con brazos R15 del proyecto, manos que siguen cartucho e inspeccion.
G=Vector((.48,1.8,-.68))
J={'R':dict(S=Vector((.56,-1.1,-.30)),E=Vector((.70,-.60,-.48)),W=Vector((.04,-.19,-.23)),H=Vector((.015,-.13,-.22)),Hs=(.27,.34,.29),Hr=(0,0,0)),
   'L':dict(S=Vector((-1.00,-1.1,-.30)),E=Vector((-.92,.18,-.50)),W=Vector((-.54,.94,-.15)),H=Vector((-.49,1.10,-.02)),Hs=(.27,.35,.26),Hr=(0,0,0))}
arms=W.build_vm_arms(CV,G,J);W.paint_arms(arms,str(ROOT/'texturas'/'BrazosVM_Color.png'))
vm={}
for o in parts:
    p=o.copy();p.data=o.data.copy();p.parent=None
    for m in list(p.modifiers):p.modifiers.remove(m)
    p.vertex_groups.clear();p.location=o.location+G;p.name=o.name+'_VM';CV.objects.link(p);vm[o.name]=p
bones=[('Camara',(0,0,0),None,.2),('Arma',tuple(G),'Camara',.2),('Cartucho',tuple(cart.location+G),'Arma',.15),('Cierre',tuple(lever.location+G),'Arma',.12)]
for side,pre in [('R','Right'),('L','Left')]:
    j=J[side];bones += [(pre+'UpperArm',tuple(j['S']+G),'Arma',.15),(pre+'LowerArm',tuple(j['E']+G),pre+'UpperArm',.15),(pre+'Hand',tuple(j['W']+G),pre+'LowerArm',.12)]
rv=A.make_armature('Lanzallamas_VM',bones,CV);BV=[b[0] for b in bones]
for o,bn in zip(parts,BW):A.skin_rigid(vm[o.name],rv,bn)
for n,o in arms.items():A.skin_rigid(o,rv,n)
clips=[]
c=W.ClipDef('Equipar',.85)
c.v('Arma',0,(.2,-.3,-1.1),(-35,12,-12)).v('Arma',.5,(0,0,.05),(3,0,0)).v('Arma',.85)
c.w('Arma',0,(0,0,-.5),(-25,0,0)).w('Arma',.85).e(.56,'agarre')
clips.append(c)
c=W.ClipDef('Guardar',.65)
c.v('Arma',0).v('Arma',.18,(.05,0,-.10),(-5,0,8)).v('Arma',.65,(.3,-.3,-1.2),(-45,20,20))
c.w('Arma',0).w('Arma',.65,(0,0,-.6),(-35,0,0)).e(0,'fuego_apagar').e(.60,'ocultar_arma');clips.append(c)
c=W.ClipDef('Reposo',2,loop=True)
for t in (0,.5,1,1.5,2):c.v('Arma',t,(0,0,.008*math.sin(t*math.pi)),(.5*math.sin(t*math.pi),0,0))
clips.append(c)
c=W.ClipDef('Disparo',.60,loop=True)
for t in (0,.1,.2,.3,.4,.5,.6):
    wig=.5+.5*math.sin(math.tau*t/.2)
    c.v('Arma',t,(0,-.025*wig,.006*wig),(.6*wig,0,.25*math.sin(math.tau*t/.6*2)))
c.e(0,'fuego_sostener');clips.append(c)
c=W.ClipDef('Recargar',2.8)
rp=((-0.10,.12,.13),(12,6,-12))
c.v('Arma',0).v('Arma',.32,*rp).v('Arma',2.30,*rp).v('Arma',2.8)
c.p('Cierre',0).p('Cierre',.34,rot=(0,35,0)).p('Cierre',2.20,rot=(0,35,0)).p('Cierre',2.42)
for t,loc in [(0,(0,0,0)),(.42,(0,0,0)),(.88,(-.15,-.10,-.75)),(1.10,(-.45,-.10,-1.30)),(1.36,(-.45,-.10,-1.30)),(1.75,(-.15,0,-.65)),(2.12,(0,0,0)),(2.8,(0,0,0))]:
    c.p('Cartucho',t,loc)
    if .42<=t<=2.12:c.hand('L',t,Vector((-.24,.43,-.54))+Vector(loc),J,(-1,0,-1))
c.rest_hand('L',0).rest_hand('L',2.63)
c.e(0,'fuego_apagar').e(.34,'cierre_abrir').e(.88,'cartucho_fuera').e(1.36,'cartucho_nuevo').e(2.12,'cartucho_insertar').e(2.42,'recarga_confirmar')
clips.append(c)
c=W.ClipDef('Inspeccionar',3.2)
keys=[(0,(0,0,0),(0,0,0)),(.65,(-.12,.14,.08),(8,12,-32)),(1.25,(-.12,.14,.08),(8,12,-32)),(2.1,(-.03,.12,.06),(5,-8,25)),(2.55,(-.03,.12,.06),(5,-8,25)),(3.2,(0,0,0),(0,0,0))]
W.inspect(c,keys,J,{'R':(1,0,-1),'L':(-1,0,-1)},lambda t,T,R:(J['L']['W'],False,1.0))
c.e(0,'fuego_apagar');clips.append(c)
# Exportar un rig por vez; reconstruir acciones separadas en el editable.
vparts=list(vm.values())+list(arms.values())
for rig,bs,objects,tag,isvm in [(rw,BW,parts,'Mundo',False),(rv,BV,vparts,'VM',True)]:
    acts={c.name:c.build(rig,bs,isvm) for c in clips}
    A.set_action(rig,acts['Reposo'])
    A.export_fbx(str(ROOT/f'Lanzallamas_{tag}.fbx'),[rig]+objects,anim=True,all_actions=True)
    for n,act in acts.items():A.set_action(rig,act);A.export_fbx(str(ROOT/'clips'/f'Lanzallamas_{tag}_{n}.fbx'),[rig]+objects,anim=True)
    reset_pose(rig)
    for act in acts.values():bpy.data.actions.remove(act)
actsW={};actsV={}
for c in clips:
    act=c.build(rw,BW,False);act.name='Mundo_'+c.name;actsW[c.name]=act
    act=c.build(rv,BV,True);act.name='VM_'+c.name;actsV[c.name]=act
reset_pose(rw);reset_pose(rv)
cst,stat=W.static_copies(parts)
static_names=[o.name for o in parts]
for o in parts:o.name+='_rig'
for o,name in zip(stat,static_names):o.name=name
A.export_fbx(str(ROOT/'Lanzallamas_Estatico.fbx'),stat);A.export_glb(str(ROOT/'Lanzallamas_Estatico.glb'),stat);W.remove_collection(cst)
for o,name in zip(parts,static_names):o.name=name
W.write_eventos(str(ROOT),'Lanzallamas',clips,{'Boca':Vector((0,2.75,.32))},handle)
bpy.ops.file.pack_all();A.save_blend(str(ROOT/'Lanzallamas.blend'))
A.write_json(str(ROOT/'datos.json'),{'triangles_weapon':tris,'triangles_arms':A.tris(arms.values()),'clips':{c.name:c.length for c in clips},'rigs':{'Mundo':len(BW),'VM':len(BV)},'scope':'Asset ficticio Blender; no Roblox ni arma real','world_parts':[o.name for o in parts]})
CC=A.collection('Camaras');A.setup_world((.50,.54,.58),.85);A.add_lights(CC)
A.setup_render((1100,740),'CYCLES',24);sc.render.threads_mode='FIXED';sc.render.threads=3
W.hide_only({'Arma_Mundo','Camaras'})
cam=W.look_cam(CC,'Hero',Vector((0,1.0,.02)),(-1,-.55,.65),7.7,50)
A.render(str(ROOT/'previews'/'Lanzallamas-v01b-01-PoliPintado-Blender.png'),cam)
W.hide_only({'Arma_VM','Camaras'});camvm=W.vm_camera(CC)
A.render(str(ROOT/'previews'/'Lanzallamas-v01b-02-primera-persona-Blender.png'),camvm)
A.setup_render((600,400),'CYCLES',16);sc.render.threads_mode='FIXED';sc.render.threads=3
for n,times in {'Equipar':[0,.25,.5,.85],'Guardar':[0,.18,.40,.65],'Recargar':[0,.42,.88,1.36,2.12,2.8],'Inspeccionar':[0,.65,1.25,2.1,2.55,3.2]}.items():
    items=[]
    for j,t in enumerate(times):
        reset_pose(rv);A.set_action(rv,actsV[n]);sc.frame_set(round(t*60))
        p=ROOT/'previews'/f'Lanzallamas-v01b-{n}-{j:02d}-Blender.png';A.render(str(p),camvm);items.append((str(p),f'{n.upper()} {t:.2f}s'))
    W.contact_sheet(items,3 if len(times)==6 else 4,str(ROOT/'previews'/f'Lanzallamas-v01b-{n}-secuencia-Blender.png'),title=f'LANZALLAMAS - {n.upper()} - BLENDER')
reset_pose(rw);reset_pose(rv)
print('FLAME_BUILD_DONE')
