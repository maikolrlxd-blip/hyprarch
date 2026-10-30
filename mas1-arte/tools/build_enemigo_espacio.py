# Enemigos voladores de la zona del espacio para «+1 de lanzamiento por segundo»: el Ovni (platillo de voxeles con un alienígena enfadado
# asomado y luces que giran en el borde) y el Meteorito (roca de voxeles con bloques de lava, cara enfadada y cola de fuego). v02: todo en
# voxeles de 0,2 como las nubes (Maikol, 30/10: «enemigos todos en voxel»; la v01 mezclaba platillo liso y roca facetada). Como las nubes
# (build_enemigo_nube.py): blancos que el jugador golpea en pleno vuelo, ojos diminutos con párpados, cejas en su hueso, clips Idle (2,0 s,
# bucle), Hit (0,5 s), Defeat (1,0 s) y Blink (8 fotogramas, solo párpados). En Roblox un hueso no se escala: encoger o desvanecer al
# derrotarlos lo hace el juego.
# Rig del ovni: Root, Body, Rim (luces del borde), Alien, Antenna, Brow, Lid_R/L. Rig del meteorito: Root, Body, Tail, Brow, Lid_R/L.
# blender -b --factory-startup --python-exit-code 1 -P build_enemigo_espacio.py
#   ESPACIO_FASE=geo | check | full (por defecto);  ESPACIO_SOLO=ovni|meteorito
# Cara, claves y clips comunes en mas1_enemigo.py.
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo la pieza. Sin probar en Roblox.
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_enemigo import *
from mas1_enemigo import _h3

FASE = os.environ.get('ESPACIO_FASE', 'full')
SOLO = os.environ.get('ESPACIO_SOLO')
BASE_OUT = os.path.abspath(os.path.join(HERE, '..', 'enemigos-v02'))

VARIANTES = [
    dict(clave='ovni', nombre='OvniEnfadado', titulo='OVNI', objetivo=(-0.3, 0.0, 2.1), cara=(0, 0.6, 2.75),
         pal={'metal': '#dfe3f0', 'metal_osc': '#959bba', 'banda': '#7a5cff', 'luz': '#ffe14d', 'emisor': '#7df9ff',
              'alien': '#86e35a', 'parpado': '#86e35a', 'pupila': '#1d1626', 'ojo': '#ffffff', 'ceja': '#2f5b2a', 'boca': '#1d1626'}),
    dict(clave='meteorito', nombre='MeteoritoFurioso', titulo='METEORITO', objetivo=(-0.3, -0.4, 2.0), cara=(0, 1.0, 2.15),
         pal={'roca': '#7a6a86', 'parpado': '#7a6a86', 'roca_osc': '#554860', 'lava': '#ff8a2a', 'fuego': '#ff7a1a', 'fuego_claro': '#ffe36b',
              'fuego_osc': '#ff4a3a', 'pupila': '#1d1626', 'ojo': '#ffffff', 'ceja': '#2b2233', 'boca': '#1d1626'}),
]
C = 0.2


# ---------------------------------------------------------------- ovni
def construir_ovni(var, MBS):
    V = Vox(C)

    def plato(p, n):
        r = math.hypot(p.x, p.y)
        if r > 1.55:
            return 'banda'                                                     # borde violeta
        if n.z < -0.5 and r < 0.45:
            return 'emisor'                                                    # emisor del rayo tractor
        return 'metal' if p.z > 1.75 else 'metal_osc'
    V.elipsoide((0, 0, 1.75), (2.05, 2.05, 0.42), 'Body', plato)
    for i in range(-5, 6):                                                     # collar de la cabina: anillo de voxeles sobre el plato
        for j in range(-5, 6):
            if 0.62 <= math.hypot(i * C, j * C) <= 0.92:
                V.cells[(i, j, 11)] = ('Body', 'banda')                        # z = 2,2
    V.elipsoide((0, 0.0, 2.75), (0.52, 0.46, 0.48), 'Alien', 'alien')         # alienígena asomado
    V.elipsoide((0, 0.0, 2.36), (0.34, 0.30, 0.22), 'Alien', 'alien')
    V.construir({'Body': MBS['Body'], 'Alien': MBS['Alien']})
    for i in range(10):                                                        # luces del borde (giran con el hueso Rim)
        a = 2 * math.pi * (i + 0.5) / 10
        cubo_girado(MBS['Rim'], (2.06 * math.cos(a), 2.06 * math.sin(a), 1.75), (0.24, 0.24, 0.24), 'luz', rot=(0, 0, math.degrees(a) + 45))
        # caras de arriba y abajo en z = 1,63 y 1,87: lejos de los planos de voxel (1,7 y 1,9), también con la mascota encogida
    for s in (-1, 1):                                                          # manos agarradas al collar
        MBS['Body'].box((s * 0.34, 0.80, 2.34), (0.18, 0.15, 0.13), 'alien')
    MBS['Antenna'].box((0, 0, 3.38), (0.07, 0.07, 0.42), 'alien')
    MBS['Antenna'].box((0, 0, 3.62), (0.17, 0.17, 0.17), 'luz')
    dy, ceja = cara({'Body': MBS['Alien'], 'Brow': MBS['Brow'], 'Lid_R': MBS['Lid_R'], 'Lid_L': MBS['Lid_L']}, 0.20,
                    2.75, frente_de(MBS['Alien']), tam=(0.16, 0.13, 0.22), sep_ceja=0.24, z_boca=2.51, boca=0.62)   # ojos de 2,64 a 2,86: lejos de 2,7 y 2,9
    huesos = [('Root', (0, 0, 2.0), None, 0.5), ('Body', (0, 0, 2.0), 'Root', 0.5), ('Rim', (0, 0, 1.80), 'Body', 0.4),
              ('Alien', (0, 0, 2.36), 'Body', 0.4), ('Antenna', (0, 0, 3.17), 'Alien', 0.3), ('Brow', ceja, 'Alien', 0.3),
              ('Lid_R', (0.20, 0.5, 2.75), 'Alien', 0.3), ('Lid_L', (-0.20, 0.5, 2.75), 'Alien', 0.3)]
    return huesos, dy


# ---------------------------------------------------------------- meteorito
def construir_meteorito(var, MBS):
    V = Vox(C)

    def piel(p, n):
        if n.z < -0.5 or p.z < 1.35:
            return 'roca_osc'
        en_cara = p.y > 0.55 and abs(p.x) < 0.75 and 1.55 < p.z < 2.75
        return 'lava' if (not en_cara and _h3(*V.idx(p), 13) < 0.12) else 'roca'        # bloques de lava sueltos, la cara limpia
    for c, r in (((0, 0, 2.0), (1.05, 0.95, 1.0)), ((0.55, -0.25, 2.65), (0.55, 0.55, 0.45)), ((-0.6, 0.05, 1.5), (0.5, 0.5, 0.42)),
                 ((0.75, 0.15, 1.55), (0.42, 0.45, 0.40)), ((-0.45, -0.35, 2.7), (0.45, 0.45, 0.35))):
        V.elipsoide(c, r, 'Body', piel, exp=2.2)                               # roca de bultos
    V.caja((0, 0.8, 2.1), (1.2, 0.2, 0.8), 'Body', piel)                       # cara plana (frente en y = 0,9)
    V.construir({'Body': MBS['Body']})
    dy, ceja = cara(MBS, 0.32, 2.26, frente_de(MBS['Body']))          # ojos de 2,13 a 2,39: lejos de los planos de voxel
    # cola de fuego: lenguas en flecha hacia atrás y arriba (35°, para que se vean por encima de la roca) en dos abanicos cruzados,
    # con la raíz dentro de la roca (como las plumas de llama del fénix)
    base = (0.0, -0.35, 2.15)
    MA = tr(base) @ rx(-35) @ rz(-90) @ rx(90)                             # plano vertical: hacia atrás y arriba
    MB_ = tr(base) @ rx(-35) @ rz(-90)                                     # plano inclinado: hacia atrás y a los lados
    banda = [(0.32, 'fuego_claro'), (0.68, 'fuego'), (1.0, 'fuego_osc')]
    for i, (a, L_) in enumerate(((-14, 1.95), (6, 2.45), (26, 1.95))):
        pluma(MBS['Tail'], MA, (0, 0), a, L_, 0.62, 0.12, -0.10 + 0.10 * i, banda, afilar=0.9, punta=0.55)
    for i, (a, L_) in enumerate(((-24, 1.75), (24, 1.75))):
        pluma(MBS['Tail'], MB_, (0, 0), a, L_, 0.56, 0.12, 0.17 - 0.34 * i, banda, afilar=0.9, punta=0.55)
    huesos = [('Root', (0, 0, 2.0), None, 0.5), ('Body', (0, 0, 2.0), 'Root', 0.5), ('Tail', base, 'Body', 0.4),
              ('Brow', ceja, 'Body', 0.3), ('Lid_R', (0.32, 0.9, 2.26), 'Body', 0.3), ('Lid_L', (-0.32, 0.9, 2.26), 'Body', 0.3)]
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


def clips(rig, dy, ovni):
    def idle(t, p):
        if ovni:          # flota, se balancea, las luces dan una vuelta entera, el alienígena se asoma y la antena se mueve
            ex = {'Rim': ((0, 0, 0), (0, 0, 360.0 * t / 2.0)), 'Alien': ((0, 0, 0.05 * math.sin(2 * p)), (0, 0, 8 * math.sin(p))),
                  'Antenna': ((0, 0, 0), (10 * math.sin(2 * p + 0.6), 8 * math.sin(p + 1.1), 0))}
            body = ((0, 0, 0.16 * math.sin(p)), (4 * math.sin(p + 0.4), 5 * math.cos(p), 0))
        else:             # da vueltas despacio, la cola de fuego tiembla
            ex = {'Tail': ((0, 0, 0), (6 * math.sin(3 * p), 0, 7 * math.sin(2 * p + 0.5)))}
            body = ((0, 0, 0.14 * math.sin(p)), (5 * math.sin(p), 4 * math.sin(p + 1.3), 6 * math.sin(p + 0.3)))
        return body, -0.02 + 0.02 * math.sin(2 * p), ex

    def golpe(i, rx_):    # el alienígena se agacha; la cola se queda atrás
        return {'Alien': ((0, 0, (0, -0.18, 0.04, 0, 0)[i]), (0, 0, 0)), 'Tail': ((0, 0, 0), (-rx_, 0, 0))}

    def derrota(i, rz_):  # las luces giran al revés, el alienígena se esconde
        return {'Alien': ((0, 0, -0.12), (0, 0, 0)), 'Rim': ((0, 0, 0), (0, 0, -2 * rz_))}
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
    W.contact_sheet(shots, 4, os.path.join(PREV, '_hoja.png'), title='%s V02 (VOXEL) - ENEMIGO DE LA ZONA DEL ESPACIO - RENDERS DE BLENDER' % var['titulo'])
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, pref + '-hoja.jpg'), 0.5)
    E.reiniciar_render()
    exportar_pet(OUT, var['nombre'], ob, rig, acts, CLIPS, lambda: pose0(rig), {
        'pieza': '%s v02 (voxel): enemigo volador de la zona del espacio (se golpea en vuelo para sumar puntos)' % var['titulo'],
        'triangulos': TRIS, 'limites_studs': BOUNDS, 'huesos': [h[0] for h in HUESOS], 'paleta': PAL,
        'parpadeo_dy_studs': round(DY, 3), 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPL},
        sin_bucle=('Hit', 'Defeat', 'Blink'))
    resumen.append((var['clave'], TRIS, BOUNDS, len(SUELTAS), COPL))
A.log('RESUMEN', resumen)
A.log('listo')
