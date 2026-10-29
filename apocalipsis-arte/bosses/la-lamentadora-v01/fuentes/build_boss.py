"""La Lamentadora: boss original, mujer zombi adulta. Ejecutar SOLO Blender background.
1 unidad = 1 stud de diseño. +Y delante, +Z arriba. No modifica ningún asset previo.
"""
import os, sys, math, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import ap_lib_snapshot as A
import bpy, bmesh
import numpy as np
from mathutils import Vector, Euler

OUT = Path(__file__).resolve().parent.parent
NAME = 'LaLamentadora'
TAU = math.tau
QUICK = os.environ.get('BOSS_QUICK') == '1'
A.clean_scene(); A.REGIONS.clear(); A.NRM_SMOOTH = True
sc = bpy.context.scene
sc.render.threads_mode = 'FIXED'; sc.render.threads = 3
sc.render.fps = 30
CM = A.collection('BOSS_LaLamentadora')
parts = {}; anchors = {}; parents = {}

def tube(mb, points, radii, mat, n=10, caps=True, jag=0):
    cs = [Vector(p) for p in points]; rings=[]
    for k,c in enumerate(cs):
        tangent = (cs[min(k+1,len(cs)-1)]-cs[max(0,k-1)]).normalized()
        front = Vector((0,1,0))
        if abs(front.dot(tangent))>.94: front=Vector((0,0,1))
        front=(front-tangent*front.dot(tangent)).normalized(); side=front.cross(tangent)
        rx,ry=radii[k]; rr=[]
        for j in range(n):
            a=TAU*j/n; ripple=1+.055*math.sin(3*a+k*.6)
            p=c+side*(rx*math.cos(a)*ripple)+front*(ry*math.sin(a))
            if jag and k==len(cs)-1: p+=tangent*jag*(.25+.75*((j*7)%11)/10)
            rr.append(mb.bm.verts.new(p))
        rings.append(rr)
    for aa,bb in zip(rings,rings[1:]):
        for j in range(n): mb.face((aa[j],aa[(j+1)%n],bb[(j+1)%n],bb[j]),mat)
    if caps:
        mb.face(rings[0][::-1],mat); mb.face(rings[-1],mat)
    return rings

def finish(mb,bone,anchor,parent,smooth=True):
    ob=mb.finish(CM,recalc=True)
    for p in ob.data.polygons: p.use_smooth=smooth
    parts[bone]=ob; anchors[bone]=anchor; parents[bone]=parent
    return ob

# Cuerpo encorvado y vestido de cuello alto: silueta ancha arriba y cintura contraida.
mb=A.MB('LowerTorso')
tube(mb,[(0,-.15,3.6),(0,-.15,4.25),(0,-.08,4.9),(0,.0,5.5)],
     [(.73,.46),(.83,.52),(.59,.39),(.57,.4)],'cloth',12)
finish(mb,'LowerTorso',(0,-.1,4.2),'HumanoidRootPart')
mb=A.MB('UpperTorso')
tube(mb,[(0,0,5.35),(0,.02,5.9),(-.08,.12,6.5),(-.12,.1,7.05),(-.1,.15,7.4)],
     [(.58,.4),(.73,.48),(1.05,.52),(1.22,.48),(.68,.34)],'cloth',14)
tube(mb,[(-.1,.12,7.1),(-.1,.27,7.48),(-.05,.48,7.77)],[(.36,.28),(.24,.23),(.23,.22)],'skin',10)
# Costillas de cuello, claviculas bajo piel y borde de cuello deshilachado.
for sx in (-1,1):
    tube(mb,[(sx*.14,.54,7.57),(sx*.36,.57,7.28),(sx*.83,.44,7.12)],[(.045,.04),(.055,.04),(.025,.025)],'skin',6)
    tube(mb,[(sx*.6,.44,7.18),(sx*.34,.6,6.97),(0,.64,6.88)],[(.04,.035)]*3,'trim',5)
finish(mb,'UpperTorso',(0,0,5.4),'LowerTorso')

# Falda exterior: ocho faldones, separacion real, costura y borde desigual.
for k in range(8):
    mb=A.MB('Faldon%02d'%k); a=TAU*k/8; da=TAU/8*.48
    rows=[]
    for j,(z,r) in enumerate([(4.5,.86),(3.65,1.02),(2.7,1.21),(1.4,1.4)]):
        row=[]
        for q in range(5):
            th=a-da+2*da*q/4; zz=z
            if j==3: zz+=.36*math.sin(k*2.4+q*1.9)+(.4 if k==2 else 0)
            rr=r*(1+.06*math.cos(q*math.pi))
            row.append(mb.bm.verts.new((rr*math.cos(th),-.1+rr*.68*math.sin(th),zz)))
        rows.append(row)
    for aa,bb in zip(rows,rows[1:]):
        for q in range(4): mb.face((aa[q],aa[q+1],bb[q+1],bb[q]),'cloth' if k%3 else 'lining')
    ob=finish(mb,'Faldon%02d'%k,(.86*math.cos(a),-.1+.58*math.sin(a),4.45),'LowerTorso')
    # Espesor real mínimo sin paredes ocultas excesivas.
    sol=ob.modifiers.new('EspesorTela','SOLIDIFY'); sol.thickness=.035
    A.select_only([ob]); bpy.ops.object.modifier_apply(modifier=sol.name)

# Pies y piernas: postura amplia, rodillas ligeramente hacia dentro.
LEGS={}
for side,sx in [('Left',-1),('Right',1)]:
    hip=(sx*.44,-.12,4.15); knee=(sx*.49,.1,2.18); ankle=(sx*.72,-.02,.43)
    LEGS[side]=(hip,knee,ankle)
    mb=A.MB(side+'UpperLeg')
    tube(mb,[hip,(sx*.45,-.1,3.45),knee],[(.38,.36),(.34,.32),(.22,.22)],'skin',10)
    finish(mb,side+'UpperLeg',hip,'LowerTorso')
    mb=A.MB(side+'LowerLeg')
    tube(mb,[(knee[0],knee[1],knee[2]+.12),(sx*.59,-.08,1.55),ankle],[(.24,.23),(.3,.32),(.14,.16)],'skin',10)
    finish(mb,side+'LowerLeg',knee,side+'UpperLeg')
    mb=A.MB(side+'Foot')
    tube(mb,[(sx*.72,-.22,.22),(sx*.72,.12,.25),(sx*.75,.57,.15),(sx*.76,.85,.12)],[(.16,.14),(.23,.22),(.29,.13),(.2,.08)],'skin',8)
    for j in range(3):
        mb.cyl((sx*.76+(j-1)*.16,.68,.18),(sx*.76+(j-1)*.16,.94,.13),.065,5,'nail',r1=.012)
    finish(mb,side+'Foot',ankle,side+'LowerLeg')

# Brazos deliberadamente diferentes: el derecho cae muy bajo y tiene una mano grande.
ARMS={}
for side,sx in [('Left',-1),('Right',1)]:
    big=side=='Right'; sh=(sx*1.14,.12,7.02 if not big else 7.25)
    el=(sx*(1.55 if not big else 1.76),.19,5.2 if not big else 4.9)
    wr=(sx*(1.83 if not big else 2.02),.55,3.84 if not big else 3.28)
    ARMS[side]=(sh,el,wr)
    mb=A.MB(side+'UpperArm'); f=1.3 if big else 1
    tube(mb,[sh,(sx*1.35,.12,6.35),(el[0],el[1],el[2]-.08)],[(.39*f,.37*f),(.3*f,.28*f),(.21*f,.21*f)],'skin',10)
    # Manga rota que se apoya sobre el brazo.
    tube(mb,[(sh[0]-.06*sx,sh[1],sh[2]+.16),(sx*1.29,.1,6.68),(sx*1.4,.13,6.22)],
         [(.44*f,.41*f),(.41*f,.38*f),(.34*f,.31*f)],'cloth',10,caps=False,jag=.28)
    finish(mb,side+'UpperArm',sh,'UpperTorso')
    mb=A.MB(side+'LowerArm')
    tube(mb,[(el[0],el[1],el[2]+.12),(sx*1.83,.34,4.36 if big else 4.75),wr],
         [(.26*f,.24*f),(.34*f,.28*f),(.16*f,.15*f)],'skin',10)
    finish(mb,side+'LowerArm',el,side+'UpperArm')
    mb=A.MB(side+'Hand'); width=.4 if big else .3
    palm=(wr[0]+sx*.04,wr[1]+.08,wr[2]-.48)
    tube(mb,[wr,(wr[0],wr[1]+.04,wr[2]-.22),palm],[(.16*f,.13),(.29*f,.15),(width,.14)],'skin',8)
    for j in range(4):
        x=palm[0]+(j-1.5)*width*.47
        length=(.75 if big else .56)*(1-.13*abs(j-1.5))
        base=(x,palm[1],palm[2]+.08); mid=(x+(j-1.5)*.06,palm[1]+.12,palm[2]-length*.62)
        tip=(mid[0],mid[1]+.18,palm[2]-length)
        tube(mb,[base,mid,tip],[(.075*f,.072*f),(.06*f,.055*f),(.034,.028)],'skin',6)
        mb.cyl(tip,(tip[0],tip[1]+.2,tip[2]-.16),.045,5,'nail',r1=.003)
    tube(mb,[(wr[0]-sx*.19,wr[1]+.05,wr[2]-.13),(wr[0]-sx*.4,wr[1]+.24,wr[2]-.38),
             (wr[0]-sx*.42,wr[1]+.4,wr[2]-.58)],[(.1,.085),(.08,.065),(.03,.025)],'skin',6)
    finish(mb,side+'Hand',wr,side+'LowerArm')

# Cabeza con cavidad bucal topologica: faltan las caras exteriores de la boca y el fondo esta dentro.
mb=A.MB('Head'); n=24; hr=[]
levels=[(7.65,.22,.24),(7.79,.35,.31),(8.02,.47,.37),(8.24,.52,.4),
        (8.4,.56,.42),(8.55,.58,.43),(8.72,.6,.45),(8.94,.53,.43),(9.12,.36,.33),(9.2,.1,.13)]
for z,rx,ry in levels:
    rr=[]
    for i in range(n):
        a=TAU*i/n; x=rx*math.cos(a); y=.38+ry*math.sin(a)
        if math.sin(a)>.35:
            # Cuencas hundidas, pómulos anchos y cara afilada.
            eye=math.exp(-((abs(x)-.29)/.16)**2-((z-8.56)/.14)**2)
            y-=.11*eye
            if abs(x)<.12 and 8.33<z<8.7: y+=.055
        rr.append(mb.bm.verts.new((x,y,z)))
    hr.append(rr)
for j in range(len(hr)-1):
    for i in range(n):
        if 1<=j<=3 and 4<=i<=7: continue
        mb.face((hr[j][i],hr[j][(i+1)%n],hr[j+1][(i+1)%n],hr[j+1][i]),'skin')
mb.face(hr[0][::-1],'skin'); mb.face(hr[-1],'skin')
boundary=hr[1][4:9]+[hr[j][8] for j in range(2,5)]+[hr[4][i] for i in range(7,3,-1)]+[hr[j][4] for j in (3,2)]
inner=[]; center=Vector((0,.43,8.08))
for v in boundary:
    p=center+(v.co-center)*.80; p.y=.42
    inner.append(mb.bm.verts.new(p))
deep=[]
for v in inner:
    p=center+(v.co-center)*.64; p.y=.16; deep.append(mb.bm.verts.new(p))
for i in range(len(boundary)):
    q=(i+1)%len(boundary)
    mb.face((boundary[i],boundary[q],inner[q],inner[i]),'lip')
    mb.face((inner[i],inner[q],deep[q],deep[i]),'mouth')
mb.face(deep[::-1],'mouth')
# Nariz rota en sombra, dientes irregulares dentro de la abertura (sin colmillos exteriores).
mb.prism([(-.095,8.67),(.08,8.65),(.13,8.39),(.03,8.34),(-.1,8.4)],.72,.86,'skin',plane='XZ')
for j in range(5):
    x=(j-2)*.083; ln=.11+.05*((j*3)%4)/3
    mb.cyl((x,.62,8.37),(x,.61,8.37-ln),.041,4,'tooth',r1=.025)
for j in (0,2,3):
    x=(j-1.5)*.085
    mb.cyl((x,.57,7.87),(x,.58,7.97),.035,4,'tooth',r1=.019)
# Almendras en cuencas: contorno oscuro, ojo pequeño hundido, pupila mínima.
for sx in (-1,1):
    cx=sx*.29; zc=8.59; outer=[]; inside=[]
    for i in range(12):
        a=TAU*i/12
        outer.append(mb.bm.verts.new((cx+.19*math.cos(a),.734,zc+.10*math.sin(a)+sx*.025*math.cos(a))))
        inside.append(mb.bm.verts.new((cx+.112*math.cos(a),.712,zc+.055*math.sin(a)+sx*.018*math.cos(a))))
    for i in range(12): mb.face((outer[i],outer[(i+1)%12],inside[(i+1)%12],inside[i]),'socket')
    mb.face(inside,'eye' if sx==-1 else 'socket')
    if sx==-1:
        mb.cyl((cx-.012,.714,zc),(cx-.012,.723,zc),.028,8,'pupil')
finish(mb,'Head',(-.05,.46,7.76),'UpperTorso')

# Cabello formado por mechones volumetricos irregulares, con huesos propios para evitar un casco rigido.
mb=A.MB('HairCap')
tube(mb,[(0,.35,9.25),(0,.32,9.13),(0,.27,8.96)],[(.13,.15),(.4,.38),(.56,.45)],'hair',16)
finish(mb,'HairCap',(0,.4,8.95),'Head')
for k in range(11):
    a=math.pi*.1+math.pi*1.8*k/10
    # Cara libre: se omite el arco frontal central.
    x=.52*math.cos(a); y=.33+.42*math.sin(a)
    if y>.59 and abs(x)<.37: y=.15
    end=6.0+.5*math.sin(k*2.0)
    drift=.13*math.sin(k*1.4)
    mb=A.MB('Mechon%02d'%k)
    tube(mb,[(x,y,9.02),(x*1.14,y-.06,8.55),(x*1.3+drift,y-.12,7.63),
             (x*1.47+drift,y-.16,end+.3),(x*1.37+drift,y-.18,end)],
         [(.16,.10),(.17,.10),(.15,.08),(.095,.045),(.016,.015)],'hair',6)
    finish(mb,'Mechon%02d'%k,(x,y,8.9),'Head')
# Flequillo quebrado sobre el ojo oscuro, sin tapar la boca.
mb=A.MB('Flequillo')
tube(mb,[(.3,.63,9.03),(.44,.78,8.76),(.44,.81,8.48),(.49,.72,8.25)],[(.17,.07),(.13,.07),(.075,.04),(.008,.01)],'hair',6)
finish(mb,'Flequillo',(.3,.63,9),'Head')

# Cinturon y un pequeño aro de llaves oxidadas: memoria humana legible de cerca.
mb=A.MB('Cinturon')
tube(mb,[(0,-.03,5.38),(0,-.03,5.52)],[(.61,.435),(.61,.435)],'leather',14,caps=False)
mb.box((0,.425,5.45),(.25,.065,.18),'metal',bevel=.025)
for k in range(3):
    x=.23+k*.09
    mb.cyl((x,.46,5.38),(x+.02,.48,5.02-k*.06),.025,5,'metal')
    mb.box((x+.055,.48,5.04-k*.06),(.1,.045,.05),'metal')
finish(mb,'Cinturon',(0,0,5.42),'UpperTorso',False)

objs=list(parts.values())
A.log('GEOMETRIA',A.tris(objs),'triangulos',len(objs),'mallas')

# Atlas pintado por coordenadas comunes: motas, venas apagadas, ojeras, trazos de pelo, costuras.
def skin_paint(P,mask,pos,nrm,col):
    x,y,z=pos.T
    n=A.fbm(pos*np.array([2.7,3.4,2.2]),3,31)
    bruise=A.smoothstep(.55,.77,n)*.38
    col=col*(1-bruise[:,None])+np.array([.27,.22,.29])*bruise[:,None]
    vein=np.exp(-((np.sin(x*15+z*5+np.sin(z*3)))*9)**2)*.12
    col=col*(1-vein[:,None])+np.array([.27,.33,.33])*vein[:,None]
    face=(y>.48)&(z>7.7)
    for cx in (-.29,.29):
        eye=np.exp(-((x-cx)/.23)**2-((z-8.56)/.22)**2)*face*.6
        col=col*(1-eye[:,None])+np.array([.15,.16,.19])*eye[:,None]
        tear=np.exp(-((x-cx-.025*np.sin(z*22))/.034)**2)*np.clip((8.6-z)*3,0,1)*np.clip((z-8.05)*3,0,1)*face*.5
        col=col*(1-tear[:,None])+np.array([.19,.23,.23])*tear[:,None]
    return col

def hair_paint(P,mask,pos,nrm,col):
    x,y,z=pos.T
    strands=(np.sin(x*90+y*64+np.sin(z*2)*1.7)*.5+.5)**9
    col+=strands[:,None]*np.array([.045,.038,.028])
    return col

def cloth_paint(P,mask,pos,nrm,col):
    x,y,z=pos.T; angle=np.arctan2(y+.1,x)
    folds=(.5+.5*np.sin(angle*23+z*.5))*.10
    col+=folds[:,None]*np.array([.5,.65,.7])
    dirt=A.smoothstep(.48,.73,A.fbm(pos*3.4,3,67))*.35*np.clip((4.8-z)/3,0,1)
    col=col*(1-dirt[:,None])+np.array([.27,.23,.17])*dirt[:,None]
    seam=np.exp(-(np.sin(angle*4+.2)*45)**2)
    stitch=(np.sin(z*65)>0).astype(float)*seam*.32
    return col+stitch[:,None]*np.array([.4,.37,.29])

styles={
 'skin':dict(base='#a8aaa0',extra=skin_paint,var=.18,blotch=.22,ao=.42,light=.17,face_var=.02,grime=.18,seed=13),
 'cloth':dict(base='#31454c',extra=cloth_paint,var=.22,blotch=.22,stroke=(1,1,6),ao=.42,light=.12,edge=.25,edge_col='#7d8378',seed=34),
 'lining':dict(base='#655e59',extra=cloth_paint,var=.19,ao=.35,light=.12,grime=.3,seed=8),
 'hair':dict(base='#282322',extra=hair_paint,var=.2,stroke=(1,1,8),ao=.3,light=.12,seed=15),
 'lip':dict(base='#51464d',var=.15,ao=.3,light=.1),
 'mouth':dict(base='#160f1b',var=.1,ao=.1,light=0),
 'socket':dict(base='#252630',var=.1,ao=.1,light=.1),
 'eye':dict(base='#ccc8a0',var=.08,ao=.1,light=.05),
 'pupil':dict(base='#1d191b',var=.02,ao=0,light=0),
 'tooth':dict(base='#b9b599',var=.18,ao=.2,light=.15),
 'nail':dict(base='#4d4b46',var=.2,ao=.3,edge=.3,edge_col='#aaa18b'),
 'trim':dict(base='#989485',var=.24,ao=.35,grime=.3),
 'leather':dict(base='#3f3530',var=.22,ao=.3,grime=.2),
 'metal':dict(base='#776248',var=.2,ao=.35,rust=.5,edge=.4,edge_col='#aaa18c')}
ref=bpy.data.objects.new('CoordenadasPintura',None); CM.objects.link(ref)
groups={'Rostro':[parts['Head']], 'Cuerpo':[o for n,o in parts.items() if n!='Head']}
for group,group_objs in groups.items():
    A.uv_unwrap(group_objs,angle=58,margin=.004)
    size=1024 if QUICK else (1024 if group=='Rostro' else 2048)
    maps=A.bake_maps(group_objs,size,R=12,ao_dist=.2,bevel_r=.02,samples=12,pos_ref=ref)
    paint=A.Paint(maps,R=12,light=(-.3,.6,.8))
    regions=set(slot.material.name[2:] for o in group_objs for slot in o.material_slots)
    for region in sorted(regions):
        kw=dict(styles[region]); base=kw.pop('base'); paint.region(region,base,**kw)
    tex=OUT/'texturas'/f'{NAME}_{group}_Color.png'; paint.save(str(tex))
    A.assign_final(group_objs,A.final_material('Pintura_'+group,str(tex)))
    del maps,paint
bpy.data.objects.remove(ref,do_unlink=True)

# Rig propio con nombres R15 y huesos auxiliares de tela/pelo. No se declara compatible hasta Studio.
bones=[('HumanoidRootPart',(0,0,4.2),None,.3)]
for name in parts: bones.append((name,anchors[name],parents[name],.2))
rig=A.make_armature(NAME+'_Rig',bones,CM)
for name,ob in parts.items(): A.skin_rigid(ob,rig,name)
BN=[b[0] for b in bones]
actions={}

def pose(clip,t,phase=0,walk=0,attack=0,roar=0,fall=0):
    sway=math.sin(phase)
    clip.k('HumanoidRootPart',t,loc=(0,0,.035*sway-fall*.8),rot=(fall*82,0,0))
    clip.k('UpperTorso',t,rot=(-9-2*sway-roar*8,2,4+attack*18))
    clip.k('Head',t,rot=(5+2*sway+roar*19,7+3*math.sin(phase*.5),-9-attack*14))
    for side,sx in [('Left',-1),('Right',1)]:
        swing=walk*math.sin(phase+(0 if sx==1 else math.pi))
        clip.k(side+'UpperLeg',t,rot=(swing*17,0,sx*2))
        clip.k(side+'LowerLeg',t,rot=(max(0,-swing)*24,0,0))
        clip.k(side+'Foot',t,rot=(-swing*6,0,0))
        clip.k(side+'UpperArm',t,rot=(-8-swing*9-attack*(62 if sx==1 else 22)-roar*28,sx*4,sx*(5+roar*12)))
        clip.k(side+'LowerArm',t,rot=(-12+attack*28-roar*12,0,sx*4))
        clip.k(side+'Hand',t,rot=(-10-attack*22,0,sx*6))
    for k in range(8): clip.k('Faldon%02d'%k,t,rot=(walk*5*math.sin(phase+k),walk*3*math.cos(phase+k),0))
    for k in range(11): clip.k('Mechon%02d'%k,t,rot=(2*math.sin(phase+k)+roar*6,2*math.sin(phase*.7+k),0))

for name,length,loop,kind in [('Reposo',3,True,'idle'),('Acechar',1.6,True,'walk'),('Zarpazo',1.15,False,'attack'),
                               ('Lamento',2.4,False,'roar'),('Impacto',.65,False,'hurt'),('Caer',2.0,False,'fall')]:
    cl=A.Clip(rig,name,length,loop=loop,fps=30)
    for j in range(17):
        u=j/16; phase=TAU*u
        a=math.sin(math.pi*min(1,max(0,(u-.12)/.68))) if kind=='attack' else 0
        roar=math.sin(math.pi*u)**2 if kind=='roar' else 0
        if kind=='hurt': a=-.23*math.sin(math.pi*u)
        pose(cl,length*u,phase,walk=1 if kind=='walk' else 0,attack=a,roar=roar,fall=(u*u*(3-2*u)) if kind=='fall' else 0)
    actions[name]=cl.build(BN)

def reset_pose():
    rig.animation_data.action=None
    for pb in rig.pose.bones: pb.location=(0,0,0); pb.rotation_euler=(0,0,0); pb.scale=(1,1,1)
    sc.frame_set(0); bpy.context.view_layer.update()

reset_pose()
# Exportaciones independientes de la escena de presentacion.
A.export_fbx(str(OUT/(NAME+'_Rig.fbx')),[rig]+objs,anim=True,all_actions=True)
for name,act in actions.items():
    A.set_action(rig,act)
    A.export_fbx(str(OUT/'clips'/f'{NAME}_{name}.fbx'),[rig]+objs,anim=True)
reset_pose()
A.export_fbx(str(OUT/(NAME+'_Estatico.fbx')),objs)
A.export_glb(str(OUT/(NAME+'_Estatico.glb')),objs)

# LOD de respaldo bajo el presupuesto original de 3000 triangulos.
LOD=A.collection('LOD1_2600'); lod=[]; ratio=min(1,2600/A.tris(objs))
for ob in objs:
    lo=ob.copy(); lo.data=ob.data.copy(); LOD.objects.link(lo); lo.name=ob.name+'_LOD1'
    lo.parent=None; lo.matrix_world=ob.matrix_world.copy()
    for m in list(lo.modifiers): lo.modifiers.remove(m)
    if len(lo.data.polygons)>12:
        dec=lo.modifiers.new('LOD','DECIMATE'); dec.ratio=ratio
        A.select_only([lo]); bpy.ops.object.modifier_apply(modifier=dec.name)
    lod.append(lo)
A.export_fbx(str(OUT/(NAME+'_LOD1_Estatico.fbx')),lod)
LOD.hide_render=True; LOD.hide_viewport=True

# Presentacion sobria con referencia humana; las piezas del escenario NO se exportan con el boss.
ST=A.collection('ESTUDIO_no_exportar')
ground=A.MB('SueloEstudio'); ground.box((0,0,-.16),(200,200,.3),'ground')
g=ground.finish(ST); A.assign_final([g],A.flat_mat('SueloMate',(.075,.09,.105)))
refobs=A.reference_figure(ST,x=-4.1,y=-.4,h=6,name='Referencia_6studs')
A.ruler(ST,-5.2,-.8,6)
def area(name,loc,target,power,color,size):
    light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.color=color; light.shape='DISK'; light.size=size
    ob=bpy.data.objects.new(name,light); ST.objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler(); return ob
area('Principal',(-5,8,12),(0,0,5.5),1150,(.75,.88,1),5)
area('Relleno',(4,7,6),(0,0,5),550,(.78,.86,1),4)
area('Contra',(2,-4,10),(0,0,6),1450,(.48,.7,.78),3)
A.setup_world((.12,.15,.19),.45)
A.setup_render((1200,1200),engine='CYCLES',samples=24 if QUICK else 48)
sc.render.threads_mode='FIXED'; sc.render.threads=3
sc.view_settings.view_transform='AgX'
neutral=A.camera(ST,'CamaraEscala',(11,24,11),(-.6,0,4.7),lens=55)
hero=A.camera(ST,'CamaraRetrato',(7.5,20,7.3),(0,.1,4.8),lens=62)
face=A.camera(ST,'CamaraRostro',(2.1,6.9,8.6),(0,.5,8.45),lens=65)
A.set_action(rig,actions['Reposo']); sc.frame_set(0)
A.render(str(OUT/'previews'/'Lamentadora-01-escala-Blender.png'),neutral)
for ob in list(ST.objects):
    if ob.name.startswith('Referencia') or ob.name.startswith('Regla'): ob.hide_render=True
A.render(str(OUT/'previews'/'Lamentadora-02-retrato-Blender.png'),hero)
A.render(str(OUT/'previews'/'Lamentadora-03-rostro-Blender.png'),face)
# Pose de ataque muestra manos, pelvis y silueta desde un ángulo distinto.
A.set_action(rig,actions['Zarpazo']); sc.frame_set(18)
A.render(str(OUT/'previews'/'Lamentadora-04-zarpazo-Blender.png'),hero)
reset_pose()
A.stash_actions(rig,list(actions.values()))
sc.camera=hero
bpy.ops.file.pack_all()
A.save_blend(str(OUT/(NAME+'.blend')))
bbox=[ob.matrix_world@Vector(v) for ob in objs for v in ob.bound_box]
size=[max(p[i] for p in bbox)-min(p[i] for p in bbox) for i in range(3)]
A.write_json(str(OUT/'datos.json'),{'nombre':'La Lamentadora','version':'0.1.0','triangulos':A.tris(objs),
 'triangulos_lod1':A.tris(lod),'mallas':len(objs),'huesos':len(BN),'dimensiones_reposo_blender_XYZ_studs':size,
 'clips':{n:{'segundos':float(a.frame_end)/30,'bucle':n in ('Reposo','Acechar')} for n,a in actions.items()},
 'texturas':['LaLamentadora_Rostro_Color.png','LaLamentadora_Cuerpo_Color.png'],
 'estado':'Blender; pendiente reimportacion y Roblox Studio','estilo':'mujer zombi adulta, terror sin gore',
 'export':'FBX global_scale .01 -Z/Y; GLB escala Blender distinta, verificar importador'})
A.log('BOSS_COMPLETO',OUT)
