# Enemigos voladores de la zona del espacio para «+1 de lanzamiento por segundo»: el Ovni (platillo facetado con un alienígena enfadado
# asomado y luces que giran en el borde) y el Meteorito (roca facetada con grietas de lava, cara enfadada y cola de fuego). Como las nubes
# (build_enemigo_nube.py): blancos que el jugador golpea en pleno vuelo, ojos diminutos con párpados, cejas en su hueso, clips Idle (2,0 s,
# bucle), Hit (0,5 s), Defeat (1,0 s) y Blink (8 fotogramas, solo párpados). En Roblox un hueso no se escala: encoger o desvanecer al
# derrotarlos lo hace el juego.
# Rig del ovni: Root, Body, Rim (luces del borde), Alien, Antenna, Brow, Lid_R/L. Rig del meteorito: Root, Body, Tail, Brow, Lid_R/L.
# blender -b --factory-startup --python-exit-code 1 -P build_enemigo_espacio.py
#   ESPACIO_FASE=geo | check | full (por defecto);  ESPACIO_SOLO=ovni|meteorito
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo la pieza. Sin probar en Roblox.
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *
from mathutils.bvhtree import BVHTree
import mas1_pet

FASE = os.environ.get('ESPACIO_FASE', 'full')
SOLO = os.environ.get('ESPACIO_SOLO')
BASE_OUT = os.path.abspath(os.path.join(HERE, '..', 'enemigos-v01'))

VARIANTES = [
    dict(clave='ovni', nombre='OvniEnfadado', titulo='OVNI', objetivo=(-0.3, 0.0, 2.1), cara=(0, 0.6, 2.75),
         pal={'metal': '#dfe3f0', 'metal_osc': '#959bba', 'banda': '#7a5cff', 'luz': '#ffe14d', 'emisor': '#7df9ff',
              'alien': '#86e35a', 'parpado': '#86e35a', 'pupila': '#1d1626', 'ojo': '#ffffff', 'ceja': '#2f5b2a', 'boca': '#1d1626'}),
    dict(clave='meteorito', nombre='MeteoritoFurioso', titulo='METEORITO', objetivo=(-0.3, -0.4, 2.0), cara=(0, 1.0, 2.15),
         pal={'roca': '#7a6a86', 'parpado': '#7a6a86', 'roca_osc': '#554860', 'lava': '#ff8a2a', 'fuego': '#ff7a1a', 'fuego_claro': '#ffe36b',
              'fuego_osc': '#ff4a3a', 'pupila': '#1d1626', 'ojo': '#ffffff', 'ceja': '#2b2233', 'boca': '#1d1626'}),
]
C = 0.2


def _h(i, seed):
    h = (i * 73856093) ^ (seed * 2654435761)
    return ((h >> 3) & 0xffff) / 65535.0


def cara(MBS, ojo_x, z_ojos, frente_en, tam=(0.20, 0.15, 0.26), sep_ceja=0.28, z_boca=None, boca=1.0):
    """Ojos diminutos con brillo, párpados, cejas enfadadas (hueso Brow) y morro gruñón sobre una superficie cuyo frente en (x, z) da
    frente_en(x, z) (y de la superficie). Devuelve (dy del párpado, centro de la ceja)."""
    dy = 0.0
    y_ojo = max(frente_en(s * ojo_x, z_ojos) for s in (-1, 1)) + tam[1] / 2 - 0.05
    for s, lado in ((1, 'R'), (-1, 'L')):
        c = (s * ojo_x, y_ojo, z_ojos)
        MBS['Body'].box(c, tam, 'pupila')
        frente = y_ojo + tam[1] / 2
        MBS['Body'].box((s * (ojo_x - 0.04), frente + 0.015, z_ojos + 0.06), (0.07, 0.04, 0.08), 'ojo')
        dy = parpado(MBS['Lid_' + lado], c, tam, frente + 0.035, 'parpado', 'boca')
    z_c = z_ojos + sep_ceja
    y_c = max(frente_en(s * ojo_x, z_c) for s in (-1, 1)) + 0.02
    for s in (1, -1):
        cubo_girado(MBS['Brow'], (s * (ojo_x + 0.01), y_c, z_c), (0.40, 0.14, 0.12), 'ceja', rot=(0, -s * 22, 0))
    z_b = z_boca if z_boca is not None else z_ojos - 0.30
    y_b = max(frente_en(x, z_b) for x in (-0.27, 0.0, 0.27))
    frown = [(-0.27, -0.05), (-0.14, 0.04), (0.14, 0.04), (0.27, -0.05), (0.20, -0.10), (0.10, -0.04), (-0.10, -0.04), (-0.20, -0.10)]
    MBS['Body'].prism([(boca * x, z_b + boca * z) for x, z in frown], y_b - 0.06, y_b + 0.07, 'boca', plane='XZ')
    return dy, (0.0, y_c, z_c)


def frente_de(mb):
    """y de la cara delantera de lo que ya hay en el MB, mirando desde delante (+Y) en (x, z)."""
    bm = mb.bm.copy()
    bm.normal_update()
    arbol = BVHTree.FromBMesh(bm)

    def f(x, z):
        hit = arbol.ray_cast(Vector((x, 9.0, z)), Vector((0, -1, 0)))
        return hit[0].y if hit[0] is not None else 0.0
    return f


# ---------------------------------------------------------------- ovni
def construir_ovni(var, MBS):
    mb = MBS['Body']
    prof = [(0.30, 1.40), (0.62, 1.44), (1.30, 1.60), (1.80, 1.78), (2.00, 1.88), (2.00, 1.98), (1.70, 2.08), (1.10, 2.20), (0.80, 2.26)]
    mats = ['metal_osc', 'metal_osc', 'metal_osc', 'banda', 'banda', 'banda', 'metal', 'metal']
    mb.lathe((0, 0, 0), (0, 0, 1), prof, 20, 'metal', close0=False, close1=True, mats=mats + ['metal'])
    mb.cyl((0, 0, 1.31), (0, 0, 1.43), 0.36, 20, 'emisor')                  # emisor del rayo tractor (tapa el hueco de abajo)
    mb.lathe((0, 0, 0), (0, 0, 1), [(0.88, 2.20), (0.88, 2.37), (0.74, 2.37), (0.74, 2.27)], 20, 'banda', close0=False, close1=False)
    for i in range(10):                                                    # luces del borde (giran con el hueso Rim)
        a = 2 * math.pi * (i + 0.5) / 10
        cubo_girado(MBS['Rim'], (2.0 * math.cos(a), 2.0 * math.sin(a), 1.93), (0.20, 0.20, 0.20), 'luz', rot=(0, 0, math.degrees(a) + 45))
    # alienígena asomado: cabeza de voxeles, manos agarradas al borde, antena con bola
    V = Vox(C)
    V.elipsoide((0, 0.0, 2.75), (0.52, 0.46, 0.48), 'Alien', 'alien')
    V.elipsoide((0, 0.0, 2.36), (0.34, 0.30, 0.22), 'Alien', 'alien')
    V.construir({'Alien': MBS['Alien']})
    for s in (-1, 1):
        MBS['Body'].box((s * 0.34, 0.80, 2.42), (0.18, 0.15, 0.13), 'alien')
    MBS['Antenna'].box((0, 0, 3.38), (0.07, 0.07, 0.42), 'alien')
    MBS['Antenna'].box((0, 0, 3.62), (0.17, 0.17, 0.17), 'luz')
    f_alien = frente_de(MBS['Alien'])
    dy, ceja = cara({'Body': MBS['Alien'], 'Brow': MBS['Brow'], 'Lid_R': MBS['Lid_R'], 'Lid_L': MBS['Lid_L']}, 0.20,
                    2.80, f_alien, tam=(0.16, 0.13, 0.22), sep_ceja=0.24, z_boca=2.55, boca=0.62)
    huesos = [('Root', (0, 0, 2.0), None, 0.5), ('Body', (0, 0, 2.0), 'Root', 0.5), ('Rim', (0, 0, 1.93), 'Body', 0.4),
              ('Alien', (0, 0, 2.36), 'Body', 0.4), ('Antenna', (0, 0, 3.17), 'Alien', 0.3), ('Brow', ceja, 'Alien', 0.3),
              ('Lid_R', (0.20, 0.5, 2.78), 'Alien', 0.3), ('Lid_L', (-0.20, 0.5, 2.78), 'Alien', 0.3)]
    return huesos, dy


# ---------------------------------------------------------------- meteorito
def construir_meteorito(var, MBS):
    mb = MBS['Body']
    caras = mb.rock((0, 0, 2.0), 1.05, 'roca', subdiv=3, seed=5, jitter=0.07, squash=(1.08, 0.92, 1.0))
    for k, f in enumerate(caras):
        c = f.calc_center_median()
        h = _h(k, 13)
        if c.y > 0.55 and abs(c.x) < 0.75 and 1.55 < c.z < 2.75:
            f.material_index = mb.mi('roca')                              # la cara, limpia
        elif h < 0.11:
            f.material_index = mb.mi('lava')                              # grietas de lava
        elif c.z < 1.55:
            f.material_index = mb.mi('roca_osc')
    f_roca = frente_de(mb)
    dy, ceja = cara(MBS, 0.32, 2.24, f_roca)
    # cola de fuego: lenguas en flecha hacia atrás y arriba (35°, para que se vean por encima de la roca) en dos abanicos cruzados,
    # con la raíz dentro de la roca
    base = (0.0, -0.35, 2.15)
    MA = tr(base) @ rx(-35) @ rz(-90) @ rx(90)                             # plano vertical: hacia atrás y arriba
    MB_ = tr(base) @ rx(-35) @ rz(-90)                                     # plano inclinado: hacia atrás y a los lados
    banda = [(0.32, 'fuego_claro'), (0.68, 'fuego'), (1.0, 'fuego_osc')]
    for i, (a, L_) in enumerate(((-14, 1.95), (6, 2.45), (26, 1.95))):
        pluma(MBS['Tail'], MA, (0, 0), a, L_, 0.62, 0.12, -0.10 + 0.10 * i, banda, afilar=0.9, punta=0.55)
    for i, (a, L_) in enumerate(((-24, 1.75), (24, 1.75))):
        pluma(MBS['Tail'], MB_, (0, 0), a, L_, 0.56, 0.12, 0.17 - 0.34 * i, banda, afilar=0.9, punta=0.55)
    huesos = [('Root', (0, 0, 2.0), None, 0.5), ('Body', (0, 0, 2.0), 'Root', 0.5), ('Tail', base, 'Body', 0.4),
              ('Brow', ceja, 'Body', 0.3), ('Lid_R', (0.32, 0.9, 2.24), 'Body', 0.3), ('Lid_L', (-0.32, 0.9, 2.24), 'Body', 0.3)]
    return huesos, dy


def construir(var):
    A.clean_scene()
    A.REGIONS.clear()
    bpy.context.scene.render.fps = 30
    CM, CR, CC = A.collection('Mascota'), A.collection('Ref'), A.collection('Camaras')
    nombres = (['Root', 'Body', 'Rim', 'Alien', 'Antenna', 'Brow', 'Lid_R', 'Lid_L'] if var['clave'] == 'ovni'
               else ['Root', 'Body', 'Tail', 'Brow', 'Lid_R', 'Lid_L'])
    MBS = {b: A.MB('G_' + b) for b in nombres}
    huesos, dy = (construir_ovni if var['clave'] == 'ovni' else construir_meteorito)(var, MBS)
    ob, rig = armar(var['nombre'], MBS, huesos, CM)
    return ob, rig, huesos, dict(var['pal']), CR, CC, dy


def claves(c, rig, t, dy, body=((0, 0, 0), (0, 0, 0)), brow=0.0, lid=0.0, extra=None):
    c.k('Root', t)
    c.k('Body', t, loc=body[0], rot=body[1])
    c.k('Brow', t, loc=(0, 0, brow))
    for lado in ('R', 'L'):
        c.k('Lid_' + lado, t, loc=(0, dy * lid, 0))
    for b in ('Rim', 'Alien', 'Antenna', 'Tail'):
        if b in rig.pose.bones:
            loc, rot = (extra or {}).get(b, ((0, 0, 0), (0, 0, 0)))
            c.k(b, t, loc=loc, rot=rot)


def clips(rig, dy, ovni):
    huesos = [b.name for b in rig.data.bones]
    acts = {}
    c = A.Clip(rig, 'Idle', 2.0, loop=True, fps=30)
    for i in range(13):
        t = 2.0 * i / 12
        p = 2 * math.pi * t / 2.0
        if ovni:          # flota, se balancea, las luces dan una vuelta entera, el alienígena se asoma y la antena se mueve
            ex = {'Rim': ((0, 0, 0), (0, 0, 360.0 * t / 2.0)), 'Alien': ((0, 0, 0.05 * math.sin(2 * p)), (0, 0, 8 * math.sin(p))),
                  'Antenna': ((0, 0, 0), (10 * math.sin(2 * p + 0.6), 8 * math.sin(p + 1.1), 0))}
            body = ((0, 0, 0.16 * math.sin(p)), (4 * math.sin(p + 0.4), 5 * math.cos(p), 0))
        else:             # da vueltas despacio, la cola de fuego tiembla
            ex = {'Tail': ((0, 0, 0), (6 * math.sin(3 * p), 0, 7 * math.sin(2 * p + 0.5)))}
            body = ((0, 0, 0.14 * math.sin(p)), (5 * math.sin(p), 4 * math.sin(p + 1.3), 6 * math.sin(p + 0.3)))
        claves(c, rig, t, dy, body=body, brow=-0.02 + 0.02 * math.sin(2 * p), extra=ex)
    acts['Idle'] = c.build(huesos)
    c = A.Clip(rig, 'Hit', 0.5, loop=False, fps=30)                  # golpe: sale hacia atrás, cierra los ojos y sube las cejas
    for t, by, rx_, brow, lid, ag in ((0.0, 0, 0, 0, 0, 0), (0.07, -0.40, 16, 0.09, 1, -0.18), (0.20, 0.08, -5, 0.03, 1, 0.04),
                                      (0.32, -0.03, 2, 0.0, 0.3, 0.0), (0.5, 0, 0, 0, 0, 0)):
        ex = {'Alien': ((0, 0, ag), (0, 0, 0)), 'Tail': ((0, 0, 0), (-rx_, 0, 0))}
        claves(c, rig, t, dy, body=((0, by, 0), (rx_, 0, 0)), brow=brow, lid=lid, extra=ex)
    acts['Hit'] = c.build(huesos)
    c = A.Clip(rig, 'Defeat', 1.0, loop=False, fps=30)               # derrota: golpe, vuelta entera y caída (el juego lo encoge y desvanece)
    for t, by, bz, rx_, rz_, lid in ((0.0, 0, 0, 0, 0, 0), (0.08, -0.40, 0.05, 16, 0, 1), (0.30, -0.6, 0.15, 10, 120, 1),
                                     (0.55, -0.8, -0.30, 20, 240, 1), (0.80, -0.9, -0.90, 30, 330, 1), (1.0, -1.0, -1.30, 34, 360, 1)):
        ex = {'Alien': ((0, 0, -0.12), (0, 0, 0)), 'Rim': ((0, 0, 0), (0, 0, -2 * rz_))}
        claves(c, rig, t, dy, body=((0, by, bz), (rx_, 0, rz_)), brow=0.06, lid=lid, extra=ex)
    acts['Defeat'] = c.build(huesos)
    mas1_pet.PARPADO_DY['dy'] = dy
    acts['Blink'] = clip_parpadeo(rig)
    return acts, {'Idle': 2.0, 'Hit': 0.5, 'Defeat': 1.0, 'Blink': DUR_PARPADEO}


def pose0(rig, dy=0.0, lid=0.0):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
    for lado in ('R', 'L'):
        rig.pose.bones['Lid_' + lado].location = (0, dy * lid, 0)
    bpy.context.view_layer.update()


resumen = []
for var in VARIANTES:
    if SOLO and var['clave'] != SOLO:
        continue
    OUT = os.path.join(BASE_OUT, var['clave'])
    PREV = os.path.join(OUT, 'previews')
    for d in ('', 'texturas', 'clips', 'previews'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    ob, rig, HUESOS, PAL, CR, CC, DY = construir(var)
    TRIS = A.tris([ob])
    mn = Vector([min(v.co[a] for v in ob.data.vertices) for a in range(3)])
    mx = Vector([max(v.co[a] for v in ob.data.vertices) for a in range(3)])
    BOUNDS = dict(ancho=round(mx.x - mn.x, 2), alto=round(mx.z - mn.z, 2), fondo=round(mx.y - mn.y, 2), z_min=round(mn.z, 2))
    SUELTAS, N_ISLAS = piezas_sueltas(ob)
    COPL, EJ = caras_coplanares(ob)
    A.log(var['clave'], 'triangulos', TRIS, BOUNDS, 'sueltas', len(SUELTAS), 'de', N_ISLAS, 'coplanares', COPL, EJ[:4], 'dy parpado', round(DY, 3))
    if FASE == 'check':
        continue
    E = Escena(CR, CC, PREV, 'geo' if FASE == 'geo' else 'full', radio=7.5, maniqui=(-3.9, 0.4), regla=(4.2, 0.4), objetivo=var['objetivo'])
    shot = E.foto
    pref = var['clave'][0].upper() + var['clave'][1:]
    if FASE == 'geo':
        planos(ob, PAL)
        pose0(rig)
        shot('_geo_frente', 180, 8, 13.5, scale=True)
        shot('_geo_34', 148, 14, 12.5)
        shot('_geo_cara', 180, 4, 6.0, target=var['cara'])
        shot('_geo_lateral', 90, 6, 12.5)
        continue
    Pn = hornear(ob, 3.0)
    E.reiniciar_render()
    BASE = dict(var=0.04, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.05, ao=0.55, ao_tint='#6f6ab8', light=0.22,
                hue_var=0.02, blotch=0.05, edge=0.45, edge_th=0.05, edge_break=0.3)

    def reg(name, **kw):
        if name not in A.REGIONS:
            return None
        k = dict(BASE)
        k.update(kw)
        if 'edge_col' not in k:
            k['edge_col'] = claro(PAL[name])
        return Pn.region(name, PAL[name], **k)
    for i, name in enumerate(('metal', 'metal_osc', 'banda', 'alien', 'roca', 'roca_osc', 'ceja')):
        reg(name, seed=1 + i)
    for i, name in enumerate(('luz', 'emisor', 'lava', 'fuego_claro')):
        reg(name, edge_col='#ffffff', var=0.02, ao=0.10, light=0.08, seed=11 + i)
    reg('fuego', stroke=(6.0, 1.0, 1.0), var=0.05, ao=0.15, seed=16)
    reg('fuego_osc', stroke=(6.0, 1.0, 1.0), var=0.05, ao=0.15, seed=17)
    reg('pupila', edge=0.0, var=0.0, ao=0.1, face_var=0.0, seed=18)
    reg('ojo', edge_col='#ffffff', var=0.0, ao=0.1, light=0.0, face_var=0.0, seed=19)
    reg('boca', edge=0.0, var=0.0, ao=0.1, seed=20)
    reg('parpado', ao=0.0, light=0.0, var=0.0, face_var=0.0, edge=0.0, seed=21)   # escondido: sin oclusión
    guardar_textura(Pn, ob, OUT, var['nombre'])
    acts, CLIPS = clips(rig, DY, var['clave'] == 'ovni')
    rig.animation_data_clear()
    pose0(rig)
    shots = []
    shots.append((shot(pref + '-frente', 180, 8, 13.5, scale=True), 'FRENTE (REGLA 6 STUDS) - ' + var['titulo']))
    shots.append((shot(pref + '-tres-cuartos', 148, 14, 12.5), '3/4'))
    shots.append((shot(pref + '-cara', 180, 4, 6.0, target=var['cara']), 'CARA'))
    shots.append((shot(pref + '-lateral', 90, 6, 12.5), 'LATERAL'))
    shots.append((shot(pref + '-espalda', 0, 12, 12.5), 'ESPALDA'))
    en(rig, acts, 'Hit', 0.07)
    shots.append((shot(pref + '-golpe', 150, 10, 12.5), 'GOLPE (HIT)'))
    en(rig, acts, 'Defeat', 0.55)
    shots.append((shot(pref + '-derrota', 150, 10, 12.5), 'DERROTA (DEFEAT)'))
    rig.animation_data_clear()                                     # Blink solo mueve los párpados: el resto vuelve a la pose neutra
    pose0(rig, DY, 1.0)
    shots.append((shot(pref + '-parpadeo', 180, 4, 6.0, target=var['cara']), 'PARPADEO (BLINK)'))
    W.contact_sheet(shots, 4, os.path.join(PREV, '_hoja.png'), title='%s V01 - ENEMIGO DE LA ZONA DEL ESPACIO - RENDERS DE BLENDER' % var['titulo'])
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, pref + '-hoja.jpg'), 0.5)
    E.reiniciar_render()
    exportar_pet(OUT, var['nombre'], ob, rig, acts, CLIPS, lambda: pose0(rig), {
        'pieza': '%s v01: enemigo volador de la zona del espacio (se golpea en vuelo para sumar puntos)' % var['titulo'],
        'triangulos': TRIS, 'limites_studs': BOUNDS, 'huesos': [h[0] for h in HUESOS], 'paleta': PAL,
        'parpadeo_dy_studs': round(DY, 3), 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPL},
        sin_bucle=('Hit', 'Defeat', 'Blink'))
    resumen.append((var['clave'], TRIS, BOUNDS, len(SUELTAS), COPL))
A.log('RESUMEN', resumen)
A.log('listo')
