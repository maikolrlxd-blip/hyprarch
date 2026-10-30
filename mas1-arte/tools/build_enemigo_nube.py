# Enemigos voladores de la zona de nubes para «+1 de lanzamiento por segundo»: la Nube gruñona (blanca) y el Nubarrón de tormenta (gris
# azulado con un rayo colgando). Son blancos que el jugador golpea en pleno vuelo para sumar puntos (DISENO.md de Codex: «aros y enemigos
# atacados aumentan puntos»). Voxeles de 0,2 como las mascotas (estilo Roba un huevo: bultos gordos, ojos diminutos, sombras lavanda),
# cara enfadada con cejas en su hueso, párpados que parpadean y nubecitas laterales que se mueven como brazos.
# Rig: Root, Body, Puff_R/L, Brow, Lid_R/L (+ Bolt en el nubarrón). Clips a 30 fps: Idle (2,0 s, bucle), Hit (0,5 s), Defeat (1,0 s) y
# Blink (8 fotogramas, solo párpados). En Roblox un hueso no se escala: el golpe se hace moviendo piezas; encoger o desvanecer al
# derrotarla lo hace el juego.
# blender -b --factory-startup --python-exit-code 1 -P build_enemigo_nube.py
#   NUBE_FASE=geo | check | full (por defecto);  NUBE_SOLO=<clave>
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo la nube. Sin probar en Roblox.
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *
import mas1_pet

FASE = os.environ.get('NUBE_FASE', 'full')
SOLO = os.environ.get('NUBE_SOLO')
BASE_OUT = os.path.abspath(os.path.join(HERE, '..', 'enemigos-v02'))

VARIANTES = [
    dict(clave='nube-grunona', nombre='NubeGrunona', titulo='NUBE GRUNONA', rayo=False,
         pal={'nube': '#f7f9ff', 'parpado': '#f7f9ff', 'nube_base': '#cfd0f5', 'pupila': '#2a2440', 'ojo': '#ffffff', 'ceja': '#4a4560', 'boca': '#2a2440'}),
    dict(clave='nubarron', nombre='NubarronTormenta', titulo='NUBARRON DE TORMENTA', rayo=True, yunque=True,
         pal={'nube': '#7484a8', 'parpado': '#7484a8', 'nube_base': '#48526f', 'pupila': '#ffe14d', 'ojo': '#fffbe0', 'ceja': '#1d2235', 'boca': '#1d2235',
              'rayo': '#ffd23f', 'rayo_claro': '#fff6b0'}),
]
C = 0.2
CZ = 2.2                          # centro del bulto principal
OJO = (0.36, 0.945, 2.30)          # ojo derecho (x se espeja)
OJO_TAM = (0.20, 0.15, 0.26)
FRENTE_OJO = OJO[1] + OJO_TAM[1] / 2


def cara_nube(MBS):
    """Ojos diminutos con brillo, cejas enfadadas y morro gruñón sobre la cara plana (y = 0,9). Devuelve el recorrido del párpado.
    La versión mascota (build_mascotas_enemigos.py) la cambia por cara_amable()."""
    dy = 0.0
    for s, lado in ((1, 'R'), (-1, 'L')):
        c = (s * OJO[0], OJO[1], OJO[2])
        MBS['Body'].box(c, OJO_TAM, 'pupila')
        MBS['Body'].box((s * (OJO[0] - 0.04), FRENTE_OJO + 0.015, OJO[2] + 0.06), (0.07, 0.04, 0.08), 'ojo')
        dy = parpado(MBS['Lid_' + lado], c, OJO_TAM, FRENTE_OJO + 0.035, 'parpado', 'boca')
        cubo_girado(MBS['Brow'], (s * 0.37, 0.95, 2.58), (0.40, 0.14, 0.12), 'ceja', rot=(0, -s * 22, 0))
    frown = [(-0.27, 1.95), (-0.14, 2.04), (0.14, 2.04), (0.27, 1.95), (0.20, 1.90), (0.10, 1.96), (-0.10, 1.96), (-0.20, 1.90)]
    MBS['Body'].prism(frown, 0.87, 1.00, 'boca', plane='XZ')
    return dy


def construir_nube(var):
    A.clean_scene()
    A.REGIONS.clear()
    bpy.context.scene.render.fps = 30
    CM, CR, CC = A.collection('Mascota'), A.collection('Ref'), A.collection('Camaras')
    PAL = dict(var['pal'])
    huesos = ['Root', 'Body', 'Puff_R', 'Puff_L', 'Brow', 'Lid_R', 'Lid_L'] + (['Bolt'] if var['rayo'] else [])
    MBS = {b: A.MB('G_' + b) for b in huesos}
    V = Vox(C)

    def piel(p, n):
        return 'nube_base' if (n.z < -0.5 or p.z < 1.55) else 'nube'
    plano = lambda p: p.z > 1.3                                     # base plana de nube
    V.elipsoide((0, -0.55, 2.40), (0.95, 0.75, 0.85), 'Body', piel, cortar=plano)
    V.elipsoide((0, 0.00, CZ), (1.20, 1.00, 1.00), 'Body', piel, cortar=plano)
    V.elipsoide((-0.55, -0.05, 3.00), (0.60, 0.62, 0.55), 'Body', piel)
    V.elipsoide((0.60, -0.10, 2.95), (0.55, 0.60, 0.50), 'Body', piel)
    V.elipsoide((1.30, 0.00, 1.95), (0.75, 0.78, 0.68), 'Puff_R', piel, cortar=plano)
    V.elipsoide((-1.30, 0.05, 1.90), (0.72, 0.76, 0.66), 'Puff_L', piel, cortar=plano)
    if var.get('yunque'):   # nubarron: torre y yunque ancho y plano arriba (cumulonimbo), para que no se lea como la nube blanca
        V.elipsoide((0, -0.20, 3.10), (0.85, 0.85, 0.62), 'Body', piel)   # hasta delante: sin ranura entre los bultos de arriba
        V.elipsoide((0, -0.35, 3.62), (1.95, 1.05, 0.36), 'Body', piel)
    V.borrar_caja((0, 1.0, 2.25), (1.4, 0.2, 0.9))                 # cara plana (frente en y = 0,9)
    V.construir(MBS)
    dy = cara_nube(MBS)
    if var['rayo']:
        bolt = [(0.16, 1.46), (-0.34, 0.78), (-0.05, 0.78), (-0.26, 0.14), (0.44, 0.98), (0.11, 0.98), (0.36, 1.46)]   # rayo grande
        MBS['Bolt'].prism(bolt, -0.11, 0.11, 'rayo', plane='XZ', side_mat='rayo_claro')

    HUESOS = [('Root', (0, 0, CZ), None, 0.5), ('Body', (0, 0, CZ), 'Root', 0.5),
              ('Puff_R', (0.90, 0, 1.95), 'Body', 0.4), ('Puff_L', (-0.90, 0, 1.90), 'Body', 0.4),
              ('Brow', (0, 0.95, 2.58), 'Body', 0.3),
              ('Lid_R', (OJO[0], OJO[1], OJO[2]), 'Body', 0.3), ('Lid_L', (-OJO[0], OJO[1], OJO[2]), 'Body', 0.3)]
    if var['rayo']:
        HUESOS.append(('Bolt', (0, 0, 1.40), 'Body', 0.4))
    ob, rig = armar(var['nombre'], MBS, HUESOS, CM)
    return ob, rig, HUESOS, PAL, CR, CC, dy


def claves(c, t, rayo, bodyz=0.0, bodyy=0.0, rx_=0.0, ry_=0.0, rz_=0.0, puff=0.0, puffz=0.0, brow=0.0, lid=0.0, bolt=0.0, dy=0.18):
    c.k('Root', t)
    c.k('Body', t, loc=(0, bodyy, bodyz), rot=(rx_, ry_, rz_))
    c.k('Puff_R', t, loc=(puff, 0, puffz))
    c.k('Puff_L', t, loc=(-puff, 0, -puffz))
    c.k('Brow', t, loc=(0, 0, brow))
    for lado in ('R', 'L'):
        c.k('Lid_' + lado, t, loc=(0, dy * lid, 0))
    if rayo:
        c.k('Bolt', t, rot=(0, bolt, 0))


def clips_nube(rig, rayo, dy):
    huesos = [b.name for b in rig.data.bones]
    acts = {}
    c = A.Clip(rig, 'Idle', 2.0, loop=True, fps=30)                 # flota, respira y mueve las nubecitas como brazos
    for i in range(9):
        t = 2.0 * i / 8
        p = 2 * math.pi * t / 2.0
        claves(c, t, rayo, bodyz=0.15 * math.sin(p), ry_=3 * math.sin(p + 0.7), puff=0.06 * math.sin(p + 1.2),
               puffz=0.05 * math.sin(2 * p), brow=-0.02 + 0.02 * math.sin(2 * p), bolt=7 * math.sin(3 * p), dy=dy)
    acts['Idle'] = c.build(huesos)
    c = A.Clip(rig, 'Hit', 0.5, loop=False, fps=30)                 # golpe: sale hacia atrás, se encoge, cierra los ojos y sube las cejas
    for t, by, rx_, puff, brow, lid, bolt in ((0.0, 0, 0, 0, 0, 0, 0), (0.07, -0.40, 16, -0.14, 0.09, 1, -14), (0.20, 0.08, -5, 0.05, 0.03, 1, 9),
                                              (0.32, -0.03, 2, -0.02, 0.0, 0.3, -4), (0.5, 0, 0, 0, 0, 0, 0)):
        claves(c, t, rayo, bodyy=by, rx_=rx_, puff=puff, brow=brow, lid=lid, bolt=bolt, dy=dy)
    acts['Hit'] = c.build(huesos)
    c = A.Clip(rig, 'Defeat', 1.0, loop=False, fps=30)              # derrota: golpe, vuelta entera y caída (el juego la encoge y la desvanece)
    for t, by, bz, rx_, rz_, puff, lid in ((0.0, 0, 0, 0, 0, 0, 0), (0.08, -0.40, 0.05, 16, 0, -0.14, 1), (0.30, -0.6, 0.15, 10, 120, 0.08, 1),
                                           (0.55, -0.8, -0.30, 20, 240, 0.12, 1), (0.80, -0.9, -0.90, 30, 330, 0.14, 1),
                                           (1.0, -1.0, -1.30, 34, 360, 0.14, 1)):
        claves(c, t, rayo, bodyy=by, bodyz=bz, rx_=rx_, rz_=rz_, puff=puff, brow=0.06, lid=lid, bolt=0, dy=dy)
    acts['Defeat'] = c.build(huesos)
    mas1_pet.PARPADO_DY['dy'] = dy
    acts['Blink'] = clip_parpadeo(rig)
    return acts, {'Idle': 2.0, 'Hit': 0.5, 'Defeat': 1.0, 'Blink': DUR_PARPADEO}


def pose_nube(rig, dy=0.0, lid=0.0):
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
    ob, rig, HUESOS, PAL, CR, CC, DY = construir_nube(var)
    TRIS = A.tris([ob])
    mn = Vector([min(v.co[a] for v in ob.data.vertices) for a in range(3)])
    mx = Vector([max(v.co[a] for v in ob.data.vertices) for a in range(3)])
    BOUNDS = dict(ancho=round(mx.x - mn.x, 2), alto=round(mx.z - mn.z, 2), fondo=round(mx.y - mn.y, 2), z_min=round(mn.z, 2))
    SUELTAS, N_ISLAS = piezas_sueltas(ob)
    COPL, EJ = caras_coplanares(ob)
    A.log(var['clave'], 'triangulos', TRIS, BOUNDS, 'sueltas', len(SUELTAS), 'de', N_ISLAS, 'coplanares', COPL, EJ[:4], 'dy parpado', round(DY, 3))
    if FASE == 'check':
        continue
    E = Escena(CR, CC, PREV, 'geo' if FASE == 'geo' else 'full', radio=7.5, maniqui=(-3.9, 0.4), regla=(4.2, 0.4), objetivo=(-0.3, 0.0, 2.0))
    shot = E.foto
    pref = var['clave'][0].upper() + var['clave'][1:]
    if FASE == 'geo':
        planos(ob, PAL)
        pose_nube(rig)
        shot('_geo_frente', 180, 8, 13.5, scale=True)
        shot('_geo_34', 148, 14, 12.5)
        shot('_geo_cara', 180, 4, 6.0, target=(0, 0.9, 2.3))
        shot('_geo_lateral', 90, 6, 12.5)
        continue
    Pn = hornear(ob, 3.0)
    E.reiniciar_render()
    BASE = dict(var=0.04, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.05, ao=0.55, ao_tint='#6f6ab8', light=0.22,
                hue_var=0.02, blotch=0.05, edge=0.5, edge_th=0.05, edge_break=0.3)

    def reg(name, **kw):
        if name not in A.REGIONS:
            return None
        k = dict(BASE)
        k.update(kw)
        if 'edge_col' not in k:
            k['edge_col'] = claro(PAL[name])
        return Pn.region(name, PAL[name], **k)
    reg('nube', grad=0.2, seed=1)
    reg('nube_base', seed=2)
    reg('parpado', ao=0.0, light=0.0, var=0.0, face_var=0.0, edge=0.0, seed=9)   # escondido: sin oclusión
    reg('pupila', edge=0.0, var=0.0, ao=0.1, face_var=0.0, seed=3)
    reg('ojo', edge_col='#ffffff', var=0.0, ao=0.1, light=0.0, face_var=0.0, seed=4)
    reg('ceja', seed=5)
    reg('boca', edge=0.0, var=0.0, ao=0.1, seed=6)
    reg('rayo', edge_col='#ffffff', var=0.03, ao=0.15, light=0.1, seed=7)
    reg('rayo_claro', edge=0.0, var=0.02, ao=0.1, seed=8)
    guardar_textura(Pn, ob, OUT, var['nombre'])
    acts, CLIPS = clips_nube(rig, var['rayo'], DY)
    rig.animation_data_clear()
    pose_nube(rig)
    shots = []
    shots.append((shot(pref + '-frente', 180, 8, 13.5, scale=True), 'FRENTE (REGLA 6 STUDS) - ' + var['titulo']))
    shots.append((shot(pref + '-tres-cuartos', 148, 14, 12.5), '3/4'))
    shots.append((shot(pref + '-cara', 180, 4, 6.0, target=(0, 0.9, 2.3)), 'CARA'))
    shots.append((shot(pref + '-lateral', 90, 6, 12.5), 'LATERAL'))
    shots.append((shot(pref + '-espalda', 0, 12, 12.5), 'ESPALDA'))
    en(rig, acts, 'Hit', 0.07)
    shots.append((shot(pref + '-golpe', 150, 10, 12.5), 'GOLPE (HIT)'))
    en(rig, acts, 'Defeat', 0.55)
    shots.append((shot(pref + '-derrota', 150, 10, 12.5), 'DERROTA (DEFEAT)'))
    rig.animation_data_clear()                                     # Blink solo mueve los párpados: el resto vuelve a la pose neutra
    pose_nube(rig, DY, 1.0)
    shots.append((shot(pref + '-parpadeo', 180, 4, 6.0, target=(0, 0.9, 2.3)), 'PARPADEO (BLINK)'))
    W.contact_sheet(shots, 4, os.path.join(PREV, '_hoja.png'), title='%s V02 - ENEMIGO DE LA ZONA DE NUBES - RENDERS DE BLENDER' % var['titulo'])
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, pref + '-hoja.jpg'), 0.5)
    E.reiniciar_render()
    exportar_pet(OUT, var['nombre'], ob, rig, acts, CLIPS, lambda: pose_nube(rig), {
        'pieza': '%s v02 (igual que la v01): enemigo volador de la zona de nubes (se golpea en vuelo para sumar puntos)' % var['titulo'],
        'triangulos': TRIS, 'limites_studs': BOUNDS, 'huesos': [h[0] for h in HUESOS], 'rejilla_voxel_studs': C, 'paleta': PAL,
        'parpadeo_dy_studs': round(DY, 3), 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPL},
        sin_bucle=('Hit', 'Defeat', 'Blink'))
    resumen.append((var['clave'], TRIS, BOUNDS, len(SUELTAS), COPL))
A.log('RESUMEN', resumen)
A.log('listo')
