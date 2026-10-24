"""Pequeno kit ambiental LUTO; piezas de decoracion, sin logica ni colision de motor."""
import sys,math,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import bpy,numpy as np
from mathutils import Vector,Matrix
import ap_lib as A
import ap_armas as W
ROOT=Path(__file__).resolve().parent.parent
A.clean_scene();A.REGIONS.clear();sc=bpy.context.scene
sc.render.threads_mode='FIXED';sc.render.threads=3

def camilla(C):
    m=A.MB('Camilla')
    # Marco, somier y colchon desgastado. Espacio libre visible debajo.
    m.box((0,0,2.3),(2.8,6.2,.18),'pintura',bevel=.035)
    m.box((0,-.12,2.58),(2.65,5.7,.43),'vinilo',bevel=.10)
    m.box((0,1.98,2.91),(1.95,.95,.22),'lino',bevel=.08)
    for x in (-1.1,1.1):
        for y in (-2.35,2.35):
            m.seg_box((x,y,.55),(x,y,2.28),.12,.14,'metal')
            m.box((x,y,.52),(.22,.25,.35),'pintura')
            m.cyl((x-.10,y,.26),(x+.10,y,.26),.26,8,'goma')
            m.cyl((x-.115,y,.26),(x+.115,y,.26),.11,6,'metal')
        m.seg_box((x,-2.4,.95),(x,2.4,.95),.12,.12,'metal')
    for y in (-2.35,2.35):m.seg_box((-1.1,y,.95),(1.1,y,.95),.10,.10,'metal')
    for y in (-3.03,3.03):
        for x in (-1.2,1.2):m.cyl((x,y,2.28),(x,y,3.30),.065,6,'pintura')
        m.cyl((-1.2,y,3.30),(1.2,y,3.30),.065,6,'pintura')
    # Barandillas en lados y correas caidas, sin tapar acceso completo.
    for x in (-1.42,1.42):
        for y in (-1.45,.95):m.cyl((x,y,2.27),(x,y,3.06),.045,6,'metal')
        m.cyl((x,-1.45,3.06),(x,.95,3.06),.045,6,'metal')
    for y in (-1.25,.6):
        m.box((0,y,2.805),(2.62,.17,.018),'correa')
        m.box((1.34,y,2.27),(.028,.17,1.05),'correa')
        m.box((1.36,y,1.72),(.045,.25,.14),'metal')
    m.box((0,-3.14,2.26),(.64,.018,.25),'placa')
    return m.finish(C,recalc=True)

def biombo(C):
    m=A.MB('Biombo')
    width=1.75
    for k,angle in enumerate((-.32,0,.32)):
        mk=m.mark()
        for x in (-width/2,width/2):
            m.cyl((x,0,.19),(x,0,5.75),.058,6,'pintura')
            m.box((x,0,.12),(.19,1.1,.24),'goma',bevel=.025)
        for z in (1.0,5.68):m.cyl((-width/2,0,z),(width/2,0,z),.05,6,'pintura')
        # Tela continua, con pliegues reales y dobladillo desigual (no franjas sueltas).
        front=[];back=[]
        for i in range(9):
            x=-.78+i*.195;y=.065 if i%2 else -.065
            low=1.20 + (.24 if (i+k)%7==2 else .04*math.sin(i*1.7+k))
            front.append([m.bm.verts.new((x,y-.018,low)),m.bm.verts.new((x,y-.018,5.47))])
            back.append([m.bm.verts.new((x,y+.018,low)),m.bm.verts.new((x,y+.018,5.47))])
        for i in range(8):
            m.face((front[i][0],front[i+1][0],front[i+1][1],front[i][1]),'tela')
            m.face((back[i][1],back[i+1][1],back[i+1][0],back[i][0]),'tela')
            m.face((front[i][1],front[i+1][1],back[i+1][1],back[i][1]),'tela')
            m.face((back[i][0],back[i+1][0],front[i+1][0],front[i][0]),'tela')
        for i in (0,8):m.face((front[i][0],front[i][1],back[i][1],back[i][0]),'tela')
        for x in (-.6,0,.6):m.seg_box((x,0,5.47),(x,0,5.68),.04,.04,'correa')
        matrix=Matrix.Translation(Vector(((k-1)*1.72,abs(k-1)*.29,0)))@Matrix.Rotation(angle,4,'Z')
        m.xform_since(mk,matrix)
    return m.finish(C,recalc=True)

def suero(C):
    m=A.MB('Soporte_Suero')
    m.cyl((0,0,.3),(0,0,5.7),.075,8,'metal')
    m.cyl((0,0,2.65),(0,0,3.12),.11,8,'pintura')
    m.box((.13,0,2.94),(.20,.14,.15),'goma')
    for i in range(4):
        angle=math.tau*i/4+.2;x,y=.85*math.cos(angle),.85*math.sin(angle)
        m.seg_box((0,0,.36),(x,y,.24),.11,.11,'metal')
        m.cyl((x-.09,y,.14),(x+.09,y,.14),.14,8,'goma')
    m.cyl((-.48,0,5.65),(.48,0,5.65),.035,6,'metal')
    for x in (-.48,.48):m.cyl((x,0,5.43),(x,0,5.65),.035,6,'metal')
    m.box((.39,0,4.82),(.65,.20,.93),'bolsa',bevel=.08)
    m.box((.39,-.111,4.96),(.46,.022,.31),'etiqueta')
    m.cyl((.39,0,4.25),(.39,0,4.39),.04,6,'goma')
    # Tubo corto recogido: parte decorativa, no toca ni atraviesa el suelo.
    points=[(.39,0,4.3),(.45,.03,3.9),(.60,.04,3.3),(.69,.05,2.55),(.55,.05,1.86),(.22,.05,1.73),(-.10,.05,2.05),(-.18,.05,2.58)]
    for a,b in zip(points,points[1:]):m.cyl(a,b,.026,5,'tubo')
    return m.finish(C,recalc=True)

def extra(kind):
    def fn(P,mask,pos,nrm,col):
        x,y,z=pos.T
        if kind=='vinilo':
            crease=(np.abs(y+.35*np.sin(x*2))<.035)|(np.abs(y+1.9+.2*x)<.025)
            col[crease]*=.57
        if kind in ('tela','lino'):
            thread=np.sin(z*48+x*12)*.015;col*=1+thread[:,None]
            stain=A.fbm(np.stack((x*2,y*3,z*.8),1),3,54)>.61
            col[stain]*=.75
            seam=(z<1.43) if kind=='tela' else (np.abs(x)>.81)
            col[seam]*=.8
        if kind=='placa':
            # Numero de inventario 07, pintado sobre la placa.
            mask0=(abs(x+.14)<.08)&(abs(z-2.26)<.07)
            inner=(abs(x+.14)<.035)&(abs(z-2.26)<.035)
            seven=(x>.04)&(x<.19)&((z>2.3)|(abs(x-.12-(z-2.26)*.4)<.024))
            col[(mask0&~inner)|seven]=(.18,.21,.20)
        if kind=='etiqueta':
            line=((np.sin(z*90)>.45)&(x>.22)&(x<.55));col[line]*=.45
        if kind=='bolsa':
            col[z<4.68]=col[z<4.68]*.6+np.array((.32,.40,.25))*.4
        return col
    return fn

styles={'metal':('#657270','#b3b8a3'),'pintura':('#7a8c84','#b7bfa5'),'goma':('#323a39','#69706a'),
 'vinilo':('#506c68','#8eaa94'),'lino':('#aaa894','#d1cbb1'),'correa':('#544c3e','#8c8063'),
 'placa':('#b1aa8f','#d0c6a4'),'tela':('#718b81','#a8b29c'),'bolsa':('#a6afa0','#c4cfb2'),
 'etiqueta':('#bdbca4','#d0ccb4'),'tubo':('#738e84','#b1c0a5')}
data={};objects=[]
for name,builder in [('Camilla',camilla),('Biombo',biombo),('Soporte_Suero',suero)]:
    C=A.collection(name);ob=builder(C);objects.append(ob);W.hide_only({name})
    t=A.tris([ob]);assert t<=1500,(name,t)
    A.uv_unwrap([ob],angle=55,margin=.006)
    ref=bpy.data.objects.new('PinturaPos',None);C.objects.link(ref)
    maps=A.bake_maps([ob],512,R=4,ao_dist=.24,bevel_r=.022,samples=12,pos_ref=ref);P=A.Paint(maps,R=4)
    for reg,(base,edge) in styles.items():
        if reg not in A.REGIONS:continue
        P.region(reg,base,var=.10,stroke=(1,1,5),stroke_scale=8,blotch=.10,ao=.55,light=.19,edge_col=edge,edge=.8,edge_th=.026,edge_break=.5,grime=.27,dust=.18,seed=42,extra=extra(reg))
    tex=ROOT/'texturas'/f'{name}_Color.png';P.save(str(tex),512)
    A.assign_final([ob],A.final_material(name+'_PoliPintado',str(tex)));bpy.data.objects.remove(ref,do_unlink=True)
    A.export_fbx(str(ROOT/'fbx'/f'{name}.fbx'),[ob]);A.export_glb(str(ROOT/'fbx'/f'{name}.glb'),[ob])
    bb=W.bounds([ob]);data[name]={'triangles':t,'texture_size':512,'local_bounds':[list(v) for v in bb[:2]],'unit':'1 Blender unit = 1 stud','runtime_verified':False}

# Escena de revision a escala: nunca se exportan piso, luces ni camaras con los assets.
CC=A.collection('QA_Camaras');CR=A.collection('QA_Referencia')
A.setup_world((.42,.48,.49),.8);A.add_lights(CC);W.backdrop(CR,0,40,(.32,.35,.34))
A.setup_render((850,850),'CYCLES',24);sc.render.threads_mode='FIXED';sc.render.threads=3
items=[]
for ob in objects:
    W.hide_only({ob.name,'QA_Camaras','QA_Referencia'})
    target=(0,0,2.6 if ob.name!='Camilla' else 1.6)
    cam=W.look_cam(CC,ob.name+'Cam',target,(.85,-1,.48),14 if ob.name=='Camilla' else 13,50)
    path=ROOT/'previews'/f'Hospital-v01-{ob.name}-Blender.png';A.render(str(path),cam);items.append((str(path),ob.name.upper()))
W.hide_only({'Camilla','Biombo','Soporte_Suero','QA_Camaras','QA_Referencia'})
objects[1].location=(0,4.7,0);objects[2].location=(-2.5,1.6,0)
cam=W.look_cam(CC,'KitCam',(0,1.3,2.4),(1,-1,.43),19,50)
sc.render.resolution_x=1200;sc.render.resolution_y=900
A.render(str(ROOT/'previews'/'Hospital-v01-kit-Blender.png'),cam)
bpy.ops.file.pack_all();A.save_blend(str(ROOT/'Hospital.blend'))
A.write_json(str(ROOT/'datos.json'),data)
W.contact_sheet(items,3,str(ROOT/'previews'/'Hospital-v01-piezas-Blender.png'),title='LUTO - HOSPITAL - POLI PINTADO - BLENDER')
print('HOSPITAL_BUILD_DONE',json.dumps(data))
