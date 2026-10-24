"""Revisa una copia congelada de v02. Nunca escribe fuera de esta entrega v03."""
from pathlib import Path
p=Path(__file__).parent
s=(p/'build_base_v02.py').read_text(encoding='utf-8')
s=s.replace("VARIANTE = os.environ.get('ZOMBI_VARIANTE', 'mujer')", "VARIANTE = 'lamentadora'")
s=s.replace("out=os.path.join('bosses', 'la-lamentadora-v02')", "out=''")
s=s.replace("A.NRM_SMOOTH = True", "A.NRM_SMOOTH = True\nbpy.context.scene.render.threads_mode='FIXED'\nbpy.context.scene.render.threads=3")
a=s.index('# ------------------------------------------------------------------ CABEZA')
b=s.index('# ------------------------------------------------------------------ TORSO SUPERIOR',a)
s=s[:a]+'''# Cabeza y pelo originales de esta revision, sin modificar la base de Claude.
from boss_head import build_head
parts['Head']=build_head(A,CM)

'''+s[b:]
a=s.index("    mb = A.MB(side + 'Hand')")
b=s.index('# ------------------------------------------------------------------ PIERNAS',a)
s=s[:a]+'''    mb = A.MB(side + 'Hand')
    # Palma y cinco dedos separados. No hay una tablilla haciendo de cuatro dedos.
    kn=wr+Vector((sx*.018,.055,-.27))
    limb(mb,[wr+Vector((0,0,.05)),wr+Vector((0,.02,-.14)),kn],
         [(.095,.075),(.143,.08),(.15,.058)],'piel',n=8)
    for digit in range(4):
        bx=kn.x+(digit-1.5)*.077
        ln=[.38,.47,.44,.33][digit]*(1.12 if side=='Right' else 1.0)
        base=Vector((bx,kn.y,kn.z+.025))
        mid=base+Vector(((digit-1.5)*.015,.065,-ln*.55))
        tip=base+Vector(((digit-1.5)*.024,.17,-ln))
        limb(mb,[base,mid,tip],[(.043,.037),(.035,.031),(.018,.018)],'piel',n=5)
        limb(mb,[tip+Vector((0,0,.04)),tip+Vector((0,.05,-.055))],[(.02,.016),(.003,.003)],'diente',n=4)
    th=wr+Vector((-sx*.11,.03,-.14))
    limb(mb,[th,th+Vector((-sx*.12,.07,-.13)),th+Vector((-sx*.13,.16,-.28))],
         [(.05,.045),(.038,.032),(.017,.017)],'piel',n=5)
    parts[side+'Hand']=mb.finish(CM,recalc=True)

'''+s[b:]
a=s.index('def face_x(')
b=s.index('def hair_x(',a)
s=s[:a]+'''def face_x(P, msk, pos, nrm, col):
    # Piel estratificada. Los ojos y la boca se forman en geometria, no como pegatinas.
    col=skin_x(P,msk,pos,nrm,col)
    u,v=pos[:,0],pos[:,2]; front=np.clip(nrm[:,1],0,1)
    for sx in (-1,1):
        hollow=np.exp(-ell(u,v,sx*.112,5.205,.105,.075)*1.4)*front
        col=col*(1-.35*hollow[:,None])+np.array([.27,.25,.31])*(.35*hollow[:,None])
        cheek=np.exp(-ell(u,v,sx*.2,5.075,.07,.085)*1.5)*front
        col*=1-.14*cheek[:,None]
        # Surco lagrimal irregular, ancho variable, muy poco saturado.
        line=sx*(.11+.008*np.sin(v*52))
        tear=np.exp(-((u-line)/.009)**2)*smooth(5.10,5.20,v)*smooth(5.24,5.18,v)*front
        col=col*(1-.30*tear[:,None])+np.array([.20,.19,.22])*(.30*tear[:,None])
    noise=A.fbm(pos*32,2,801)
    col*=.96+.07*noise[:,None]
    return col


'''+s[b:]
s=s.replace("np.array([0.36, 0.27, 0.20], np.float32) * 0.25", "np.array([0.18, 0.19, 0.21], np.float32) * 0.25")
s=s.replace("edge_col='#5c4637', edge=0.5", "edge_col='#38383d', edge=0.25")
s=s.replace("    col[hole] = SKIN * 0.55", "    col[hole] = col[hole]*0.65 # desgaste oscuro, sin parches planos de piel")
pos=s.index("GROUPS = {'Cabeza'")
s=s[:pos]+'''P_STYLE.update({
 'boca':dict(base='#151018',var=.025,ao=.25,light=.08),
 'ojo':dict(base='#abae9f',var=.025,ao=.35,light=.12),
 'diente':dict(base='#8b8977',var=.04,ao=.40,light=.12),
 'labio':dict(base='#4a4045',var=.03,ao=.35,light=.12),
})

'''+s[pos:]
# Produce un hito visual de formas antes de hornear texturas, con materiales provisionales.
pos=s.index('# ------------------------------------------------------------------ pintura')
block='''# Hito de revision: modelo real Blender con materiales provisionales, no render final.
CS=A.collection('QA_FORMAS')
saved_materials={o.name:list(o.data.materials) for o in objs}
palette={'piel':(.42,.45,.43),'cara':(.48,.49,.46),'pelo':(.035,.031,.038),
         'vestido':(.075,.065,.076),'boca':(.018,.012,.017),'ojo':(.62,.64,.58),
         'diente':(.43,.42,.34),'labio':(.29,.25,.27),'zapato':(.06,.055,.05)}
for o in objs:
    for slot in o.material_slots:
        key=slot.material.name[2:]
        slot.material=A.flat_mat('Preview_'+key,palette.get(key,(.25,.25,.25)))
A.setup_world((.18,.21,.24),.5)
A.add_lights(CS)
A.setup_render((1000,1000),'CYCLES',20)
bpy.context.scene.render.threads_mode='FIXED'; bpy.context.scene.render.threads=3
cc=A.camera(CS,'FormaCara',(.95,3.5,5.4),(0,.05,5.08),lens=62)
A.render(os.path.join(OUT,'previews','Lamentadora-v03-01-rostro-forma-Blender.png'),cc)
for o in objs:
    # Sustituir slots IN SITU: clear() reinicia indices de las caras a cero.
    for slot,m in zip(o.material_slots,saved_materials[o.name]):slot.material=m
for o in list(CS.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(CS)

'''
s=s[:pos]+block+s[pos:]
# Anatomia deforme, aplicada despues de pintura para no desalinear coordenadas de los pinceles.
pos=s.index('if ESC != 1.0:')
block='''def deform(p):
    x,y,z=p
    k=max(0,min(1,(z-3.5)/1.3)); k=k*k*(3-2*k)
    # Centro del pecho se adelanta progresivamente; cuello largo y cabeza descentrada.
    y+=.19*k
    x-=.045*k
    if z>4.65:z+=.13*min(1,(z-4.65)/.23)
    return Vector((x,y,z))
for ob in parts.values():
    for v in ob.data.vertices:v.co=deform(v.co)

'''
s=s[:pos]+block+s[pos:]
s=s.replace("J = {k: tuple(v * ESC for v in p) for k, p in J.items()}", "J = {k: tuple(v * ESC for v in deform(p)) for k, p in J.items()}")
s=s.replace("(-9 + 1.5 * cyc(ph), 0, 3 * cyc(ph, 0.25))", "(-16 + 1.5 * cyc(ph), 0, 5 * cyc(ph, 0.25))")
s=s.replace("(-12 + 2.0 * cyc(ph, 0.1), 14 + 3 * cyc(ph, 0.3), 4 * cyc(ph, 0.5))", "(-7 + 2.0 * cyc(ph, 0.1), 18 + 3 * cyc(ph, 0.3), 4 * cyc(ph, 0.5))")
pos=s.index("# ------------------------------------------------------------------ RENDERS")
s=s[:pos]+'''from clip_contacts import correct_fall_contact, reset_pose
contact_report=correct_fall_contact(rig,objs,acts['Caer'],bpy.context.scene.render.fps)
A.write_json(os.path.join(OUT,'qa','CONTACTO-CAIDA.json'),contact_report)
reset_pose(rig)

'''+s[pos:]
# Render mas util: pocos encuadres, figura sin superponerse, hito temprano para comentario del usuario.
s=s.replace("for n, cam in cams.items():\n    A.render", "for n, cam in cams.items():\n    if n not in ('1_frente_con_ref','2_tres_cuartos','4_cara_tres_cuartos','5_cara_frente_muy_cerca'): continue\n    A.render")
s=s.replace("A.save_blend(os.path.join(OUT, NOMBRE + '.blend'))", "reset_pose(rig)\nbpy.ops.file.pack_all()\nA.save_blend(os.path.join(OUT, NOMBRE + '.blend'))")
s=s.replace("rig.animation_data.action = None\n# estatico", "reset_pose(rig)\n# estatico")
s=s.replace("A.setup_render((1280, 720), 'CYCLES', 48)", "A.setup_render((1280, 960), 'CYCLES', 32)\nbpy.context.scene.render.threads_mode='FIXED'; bpy.context.scene.render.threads=3")
s=s.replace('A.bake_maps(gobjs, 2048,', 'A.bake_maps(gobjs, 1024,')
s=s.replace('samples=20, pos_ref=ref', 'samples=12, pos_ref=ref')
s=s.replace("NOMBRE + '_' + n + '.png'", "NOMBRE + '_v03b_' + n + '.png'")
s=s.replace('Lamentadora-v03-01-rostro-forma-Blender.png','Lamentadora-v03b-01-rostro-forma-Blender.png')
(p/'build_lamentadora.py').write_text(s,encoding='utf-8')
print('PREPARED',p/'build_lamentadora.py')
