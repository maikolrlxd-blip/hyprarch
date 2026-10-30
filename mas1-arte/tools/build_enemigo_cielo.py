# Enemigos voladores de la Pradera y del cielo alto para «+1 de lanzamiento por segundo»: el Globo gruñón (globo de voxeles en gota con nudo
# y cordel que se balancea) y la Cometa enfadada (rombo de voxeles con ribete blanco, varillas detrás y una cola de tres cuadritos de papel que ondea).
# v02: todo en voxeles de 0,2 como las nubes (Maikol, 30/10: «enemigos todos en voxel»). Como los demás enemigos
# (mas1_enemigo.py): blancos que el jugador golpea en pleno vuelo, cara enfadada con párpados y clips Idle, Hit, Defeat y Blink.
# Rig del globo: Root, Body, String, Brow, Lid_R/L. Rig de la cometa: Root, Body, Tail_1/2/3 (cadena), Brow, Lid_R/L.
# blender -b --factory-startup --python-exit-code 1 -P build_enemigo_cielo.py
#   CIELO_FASE=geo | check | full (por defecto);  CIELO_SOLO=globo|cometa
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo la pieza. Sin probar en Roblox.
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_enemigo import *
from mas1_enemigo import _h3

FASE = os.environ.get('CIELO_FASE', 'full')
SOLO = os.environ.get('CIELO_SOLO')
BASE_OUT = os.path.abspath(os.path.join(HERE, '..', 'enemigos-v02'))
C = 0.2

VARIANTES = [
    dict(clave='globo', nombre='GloboGrunon', titulo='GLOBO GRUNON', zona='LA PRADERA', objetivo=(-0.3, 0.0, 2.2), cara=(0, 1.0, 2.75),
         pal={'globo': '#ff4f6d', 'parpado': '#ff4f6d', 'globo_osc': '#d63452', 'brillo': '#ffd3dc', 'cuerda': '#f4f1ea',
              'pupila': '#2a1420', 'ojo': '#ffffff', 'ceja': '#5a1a2c', 'boca': '#2a1420'}),
    dict(clave='cometa', nombre='CometaEnfadada', titulo='COMETA ENFADADA', zona='EL CIELO ALTO', objetivo=(-0.3, 0.0, 2.7), cara=(0, 0.4, 3.65),
         pal={'vela_a': '#ffd23f', 'parpado': '#ff5a4f', 'vela_b': '#ff5a4f', 'vela_borde': '#f2f2f2', 'vela_tras': '#e9a93a',
              'palo': '#9a6a3a', 'cuerda': '#f4f1ea', 'pupila': '#2a1810', 'ojo': '#ffffff', 'ceja': '#4a2a14', 'boca': '#2a1810'}),
]


# ---------------------------------------------------------------- globo
def construir_globo(MBS):
    V = Vox(C)
    centro = Vector((0, 0, 2.62))
    luz = Vector((0.45, 0.55, 0.70)).normalized()                    # brillo arriba a la izquierda visto de frente (el +X sale a la izquierda)

    def piel(p, n):
        if (p - centro).normalized().dot(luz) > 0.86 and n.dot(luz) > 0.2:
            return 'brillo'
        return 'globo_osc' if p.z < 1.75 else 'globo'

    def gota(p):                                                     # se estrecha hacia el nudo
        return p.z > 2.25 or math.hypot(p.x, p.y) <= 0.12 + (p.z - 1.40) * 1.15
    V.elipsoide(centro, (1.0, 0.95, 1.15), 'Body', piel, cortar=gota)
    V.caja((0, 0.8, 2.75), (1.0, 0.2, 0.6), 'Body', piel)            # cara plana (frente en y = 0,9)
    V.caja((0, 0, 1.40), (0.4, 0.4, 0.2), 'Body', 'globo_osc')      # nudo
    V.caja((0, 0, 1.20), (0.2, 0.2, 0.2), 'Body', 'globo_osc')
    V.construir({'Body': MBS['Body']})
    # cordel en S colgando del nudo (hueso String): tramos finos que cambian de dirección en cada codo
    pts = [Vector((0.0, 0.0, 1.12)), Vector((0.10, 0.02, 0.86)), Vector((0.02, 0.0, 0.60)), Vector((-0.10, -0.02, 0.34)),
           Vector((-0.02, 0.0, 0.10))]
    for a, b in zip(pts[:-1], pts[1:]):
        MBS['String'].seg_box(a, b, 0.05, 0.05, 'cuerda', extend=0.02)
    dy, ceja = cara(MBS, 0.33, 2.80, frente_de(MBS['Body']))
    huesos = [('Root', (0, 0, 2.6), None, 0.5), ('Body', (0, 0, 2.6), 'Root', 0.5), ('String', (0, 0, 1.12), 'Body', 0.4),
              ('Brow', ceja, 'Body', 0.3), ('Lid_R', (0.33, 1.0, 2.80), 'Body', 0.3), ('Lid_L', (-0.33, 1.0, 2.80), 'Body', 0.3)]
    return huesos, dy


# ---------------------------------------------------------------- cometa
TOP, CRUZ, BAJO, ANCHO = 4.60, 3.80, 2.00, 1.08
# cola: la raíz en la punta de abajo y tres cuadritos de papel de 2 × 2 celdas (los de x = ±0,1 y z = 1,7 / 1,1 / 0,5), con una celda de
# hueco entre uno y otro. Los lazos de la v02 a medias (pajarita de voxeles) se leían como letras «H».
LAZOS = [Vector((0.0, 0.0, BAJO)), Vector((0.1, 0.0, 1.7)), Vector((-0.1, 0.0, 1.1)), Vector((0.1, 0.0, 0.5))]
CUADRITOS = (((0, 1), (8, 9)), ((-1, 0), (5, 6)), ((0, 1), (2, 3)))      # (celdas en x, celdas en z) de cada cuadrito


def en_vela(i, k):
    x, z = i * C, k * C
    alto = (TOP - CRUZ) if z >= CRUZ else (CRUZ - BAJO)
    return abs(x) / ANCHO + abs(z - CRUZ) / alto <= 1.0 + 1e-6


def construir_cometa(MBS):
    V = Vox(C)

    def vela(p, n):
        i, _, k = V.idx(p)
        if n.y < -0.5:
            return 'vela_tras'
        if not all(en_vela(i + di, k + dk) for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            return 'vela_borde'                                                # ribete blanco en el borde escalonado
        return 'vela_a' if p.z > CRUZ + 0.1 else 'vela_b'                       # arriba amarilla, abajo roja (ojos y párpados en la roja)
    for i in range(-6, 7):                                                     # vela: rombo de una celda de grueso (frente en y = 0,1)
        for k in range(int(round(BAJO / C)) - 1, int(round(TOP / C)) + 2):
            if en_vela(i, k):
                V.cells[(i, 0, k)] = ('Body', vela)
    for k, (xs, zs) in enumerate(CUADRITOS):                                   # cuadritos de papel, uno por hueso de la cola
        for i in xs:
            for kz in zs:
                V.cells[(i, 0, kz)] = ('Tail_%d' % (k + 1), 'vela_b' if k % 2 == 0 else 'vela_a')
    V.construir({b: MBS[b] for b in ('Body', 'Tail_1', 'Tail_2', 'Tail_3')})
    mb = MBS['Body']
    mb.box((0, -0.14, (TOP + BAJO) / 2), (0.08, 0.16, TOP - BAJO - 0.10), 'palo')            # varillas detrás: y de -0,22 a -0,06
    mb.box((0, -0.13, CRUZ), (2 * ANCHO - 0.30, 0.16, 0.07), 'palo')                         # y de -0,21 a -0,05
    for k in range(3):                                                                       # cordel de la cola entre lazos
        MBS['Tail_%d' % (k + 1)].seg_box(LAZOS[k], LAZOS[k + 1], 0.045, 0.045, 'cuerda', extend=0.02)
    dy, ceja = cara(MBS, 0.30, CRUZ - 0.12, frente_de(mb), sep_ceja=0.27, z_boca=CRUZ - 0.42)
    huesos = [('Root', (0, 0, 3.2), None, 0.5), ('Body', (0, 0, 3.2), 'Root', 0.5),
              ('Tail_1', tuple(LAZOS[0]), 'Body', 0.3), ('Tail_2', tuple(LAZOS[1]), 'Tail_1', 0.3), ('Tail_3', tuple(LAZOS[2]), 'Tail_2', 0.3),
              ('Brow', ceja, 'Body', 0.3), ('Lid_R', (0.30, 0.2, CRUZ - 0.12), 'Body', 0.3), ('Lid_L', (-0.30, 0.2, CRUZ - 0.12), 'Body', 0.3)]
    return huesos, dy


def construir(var):
    A.clean_scene()
    A.REGIONS.clear()
    bpy.context.scene.render.fps = 30
    CM, CR, CC = A.collection('Mascota'), A.collection('Ref'), A.collection('Camaras')
    nombres = (['Root', 'Body', 'String', 'Brow', 'Lid_R', 'Lid_L'] if var['clave'] == 'globo'
               else ['Root', 'Body', 'Tail_1', 'Tail_2', 'Tail_3', 'Brow', 'Lid_R', 'Lid_L'])
    MBS = {b: A.MB('G_' + b) for b in nombres}
    huesos, dy = (construir_globo if var['clave'] == 'globo' else construir_cometa)(MBS)
    ob, rig = armar(var['nombre'], MBS, huesos, CM)
    return ob, rig, huesos, dict(var['pal']), CR, CC, dy


def clips(rig, dy, globo):
    def idle(t, p):
        if globo:         # sube y baja, se mece y el cordel va detrás
            ex = {'String': ((0, 0, 0), (8 * math.sin(p - 0.9), 12 * math.sin(p - 0.7), 0))}
            return ((0, 0, 0.18 * math.sin(p)), (3 * math.sin(p + 0.3), 5 * math.sin(p), 0)), -0.02 + 0.02 * math.sin(2 * p), ex
        ex = {'Tail_%d' % (k + 1): ((0, 0, 0), (4 * math.sin(2 * p - 0.8 * k), 14 * math.sin(p - 0.7 * (k + 1)), 0)) for k in range(3)}
        return ((0, 0, 0.20 * math.sin(p)), (5 * math.sin(p + 0.6), 8 * math.sin(p), 0)), -0.02 + 0.02 * math.sin(2 * p), ex

    def golpe(i, rx_):    # el cordel o la cola se quedan atrás
        return {b: ((0, 0, 0), (-1.4 * rx_, 0, 0)) for b in ('String', 'Tail_1', 'Tail_2', 'Tail_3')}

    def derrota(i, rz_):  # el cordel o la cola se agitan mientras cae
        return {b: ((0, 0, 0), (25 * math.sin(i * 1.3 + k), 20 * math.cos(i * 1.1 + k), 0))
                for k, b in enumerate(('String', 'Tail_1', 'Tail_2', 'Tail_3'))}
    return clips_enemigo(rig, dy, idle, golpe, derrota)


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
        shot('_geo_frente', 180, 8, 14.0, scale=True)
        shot('_geo_34', 148, 14, 13.0)
        shot('_geo_cara', 180, 4, 6.0, target=var['cara'])
        shot('_geo_lateral', 90, 6, 13.0)
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
    for i, name in enumerate(('globo', 'globo_osc', 'vela_a', 'vela_b', 'vela_borde', 'vela_tras', 'palo', 'cuerda', 'ceja')):
        reg(name, seed=1 + i)
    reg('brillo', edge=0.0, var=0.0, ao=0.1, light=0.0, face_var=0.0, seed=12)
    reg('pupila', edge=0.0, var=0.0, ao=0.1, face_var=0.0, seed=13)
    reg('ojo', edge_col='#ffffff', var=0.0, ao=0.1, light=0.0, face_var=0.0, seed=14)
    reg('boca', edge=0.0, var=0.0, ao=0.1, seed=15)
    reg('parpado', ao=0.0, light=0.0, var=0.0, face_var=0.0, edge=0.0, seed=16)   # escondido: sin oclusión
    guardar_textura(Pn, ob, OUT, var['nombre'])
    acts, CLIPS = clips(rig, DY, var['clave'] == 'globo')
    rig.animation_data_clear()
    pose0(rig)
    shots = []
    shots.append((shot(pref + '-frente', 180, 8, 14.0, scale=True), 'FRENTE (REGLA 6 STUDS) - ' + var['titulo']))
    shots.append((shot(pref + '-tres-cuartos', 148, 14, 13.0), '3/4'))
    shots.append((shot(pref + '-cara', 180, 4, 6.0, target=var['cara']), 'CARA'))
    shots.append((shot(pref + '-lateral', 90, 6, 13.0), 'LATERAL'))
    shots.append((shot(pref + '-espalda', 0, 12, 13.0), 'ESPALDA'))
    en(rig, acts, 'Hit', 0.07)
    shots.append((shot(pref + '-golpe', 150, 10, 13.0), 'GOLPE (HIT)'))
    en(rig, acts, 'Defeat', 0.55)
    shots.append((shot(pref + '-derrota', 150, 10, 13.0), 'DERROTA (DEFEAT)'))
    rig.animation_data_clear()                                     # Blink solo mueve los párpados: el resto vuelve a la pose neutra
    pose0(rig, DY, 1.0)
    shots.append((shot(pref + '-parpadeo', 180, 4, 6.0, target=var['cara']), 'PARPADEO (BLINK)'))
    W.contact_sheet(shots, 4, os.path.join(PREV, '_hoja.png'), title='%s V02 (VOXEL) - ENEMIGO DE %s - RENDERS DE BLENDER' % (var['titulo'], var['zona']))
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, pref + '-hoja.jpg'), 0.5)
    E.reiniciar_render()
    exportar_pet(OUT, var['nombre'], ob, rig, acts, CLIPS, lambda: pose0(rig), {
        'pieza': '%s v02 (voxel): enemigo volador de %s (se golpea en vuelo para sumar puntos)' % (var['titulo'], var['zona'].lower()),
        'triangulos': TRIS, 'limites_studs': BOUNDS, 'huesos': [h[0] for h in HUESOS], 'paleta': PAL,
        'parpadeo_dy_studs': round(DY, 3), 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPL},
        sin_bucle=('Hit', 'Defeat', 'Blink'))
    resumen.append((var['clave'], TRIS, BOUNDS, len(SUELTAS), COPL))
A.log('RESUMEN', resumen)
A.log('listo')
