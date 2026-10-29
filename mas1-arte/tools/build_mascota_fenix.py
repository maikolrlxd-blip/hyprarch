# Fenix v02 para «+1 de lanzamiento por segundo» (mascota voladora alta, de pago con Robux): cuerpo rechoncho rojo y naranja, cresta de plumas-llama,
# alas grandes de plumas con degradado rojo-naranja-amarillo y cola de cinco plumas largas que se curvan. El fuego va APARTE (ParticleEmitter, ver
# mas1-juego/src/Efectos.lua tipo «fuego_fenix»): aqui solo se dejan los puntos donde colocar los emisores (datos.json: puntos_fuego).
# Mismo lenguaje que el aguila v02 (celda 0,2, escamas en relieve, ojos pequenos, alas en arco, rombos dorados); referencia «Roba un huevo» (Steal an Egg).
# blender -b --factory-startup --python-exit-code 1 -P build_mascota_fenix.py      (MASCOTA_FASE=geo para la fase rapida)
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo el cuerpo.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *

FASE = os.environ.get('MASCOTA_FASE', 'full')
RENDER = FASE != 'assets'          # 'assets': solo textura, rig, clips y exportacion (sin renders); los previews no cambian
NOMBRE = 'FenixDeFuego'
OUT = os.path.abspath(os.path.join(HERE, '..', 'mascotas-altas-v02', 'fenix'))
PREV = os.path.join(OUT, 'previews')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

A.clean_scene()
bpy.context.scene.render.fps = 30
CM = A.collection('Mascota')
CR = A.collection('Ref')
CC = A.collection('Camaras')

PAL = {
    'cuerpo': '#d8321c', 'cuerpo_osc': '#a31f12', 'pecho': '#ff8a1f', 'vientre': '#ffd23f', 'escama': '#ffb02e', 'escama_osc': '#bf2a18',
    'cabeza': '#e8431f', 'pico': '#ffc42e', 'pico_inf': '#e29a1a', 'cera': '#ffe27a', 'ojo': '#fff4c8', 'pupila': '#2a0d08', 'brillo': '#ffffff',
    'ceja': '#7d160d', 'oro': '#ffd23f', 'ala_a': '#b3200f', 'ala_b': '#e8431f', 'ala_c': '#ff8a1f', 'ala_c2': '#ffc04a', 'ala_punta': '#fff08a',
    'cola_a': '#c4271a', 'cola_b': '#ff7a1a', 'cola_c': '#ffd23f', 'llama_a': '#e8431f', 'llama_b': '#ff9a1f', 'llama_c': '#ffe27a',
    'garra': '#ffc42e', 'una': '#3a1a10',
}
C = 0.2
V = Vox(C)
MBS = {b: A.MB('G_' + b) for b in BONES}


def reg_torso(p, n):
    if p.z > 2.42 and p.y > -0.50:
        return 'cabeza'
    if p.y > -0.15 and abs(p.x) < 0.84 and p.z > 1.55:
        return 'pecho'                                              # pecho naranja
    if p.y > -0.15 and abs(p.x) < 0.84 and p.z <= 1.55:
        return 'vientre'                                            # vientre amarillo
    if p.z > 1.9 and p.y < 0.1:
        return 'cuerpo_osc'
    return 'cuerpo'


def b(bone, c, size, mat):
    MBS[bone].box(c, size, mat)


# ---------------------------------------------------------------- cuerpo rechoncho, cabeza grande, muslos y tarsos (volumenes escalonados)
V.elipsoide((0, -0.10, 1.58), (0.92, 0.86, 1.02), 'Body', reg_torso, exp=2.7)
V.elipsoide((0, 0.55, 3.02), (0.90, 0.86, 0.82), 'Head', 'cabeza', exp=2.6)
for s in (-1, 1):
    V.elipsoide((s * 0.50, 0.02, 0.88), (0.40, 0.48, 0.48), 'Body', 'cuerpo_osc', exp=2.4)
    V.caja((s * 0.50, 0.16, 0.40), (0.28, 0.32, 0.52), 'Leg_R' if s > 0 else 'Leg_L', 'garra')       # tarso (hueso de la pata)
V.construir(MBS)
N_ESC = 0
N_ESC += escamas(V, MBS, 'Body', 'escama', (0, 1, 0), lambda p: 0.75 < p.z < 2.40 and abs(p.x) < 0.78, alto=0.09, patron=tresbolillo)
N_ESC += escamas(V, MBS, 'Body', 'escama_osc', (0, -1, 0), lambda p: 1.00 < p.z < 2.30 and abs(p.x) < 0.78, alto=0.09, patron=dispersas(0.5, 3))
for sx in (-1, 1):
    N_ESC += escamas(V, MBS, 'Body', 'escama_osc', (sx, 0, 0), lambda p: 0.95 < p.z < 2.05 and -0.7 < p.y < 0.2, alto=0.09, patron=dispersas(0.5, 5 + sx))

# ---------------------------------------------------------------- cara: pico dorado en gancho, ojos diminutos negros con un brillo, cejas
b('Head', (0, 1.40, 3.06), (0.54, 0.52, 0.44), 'pico')
b('Head', (0, 1.76, 2.96), (0.44, 0.32, 0.36), 'pico')
b('Head', (0, 1.96, 2.76), (0.28, 0.20, 0.30), 'pico')
b('Head', (0, 2.01, 2.56), (0.18, 0.12, 0.16), 'pico_inf')
b('Head', (0, 1.34, 2.66), (0.46, 0.50, 0.14), 'pico_inf')
b('Head', (0, 1.16, 3.40), (0.62, 0.16, 0.14), 'cera')
for s in (-1, 1):
    b('Head', (s * 0.56, 1.24, 3.20), (0.20, 0.14, 0.25), 'pupila')
    b('Head', (s * 0.53, 1.32, 3.27), (0.07, 0.04, 0.08), 'brillo')
    DY_PARPADO = parpado(MBS['Lid_R' if s > 0 else 'Lid_L'], (s * 0.56, 1.24, 3.20), (0.20, 0.14, 0.25), 1.34, 'cabeza', 'pupila')
    cubo_girado(MBS['Head'], (s * 0.54, 1.24, 3.46), (0.44, 0.15, 0.13), 'ceja', rot=(0, -s * 16, 0))
rombo(MBS['Body'], (0, 0.76, 1.95), 0.50, 0.11, 'oro', 'Y')                # gema dorada en el pecho

# cresta de plumas-llama: cinco hojas verticales barridas hacia atras (la central la mas alta), sobre la coronilla
PLUMAS_CRESTA = []
for j, (x_, tilt, L_) in enumerate(((-0.44, 62, 1.00), (-0.22, 48, 1.35), (0.0, 34, 1.75), (0.22, 48, 1.35), (0.44, 62, 1.00))):
    Mc = tr((x_, 0.22, 3.68)) @ rx(tilt) @ ry(-90)
    pluma(MBS['Head'], Mc, (0, 0), 0, L_, 0.46, 0.19, 0.0, [(0.40, 'llama_a'), (0.72, 'llama_b'), (1.0, 'llama_c')], afilar=0.5, chaflan=0.08)
    PLUMAS_CRESTA.append(tuple(round(v, 3) for v in (Mc @ Vector((L_, 0, 0)))))

# pies: tres dedos al frente con unas negras, dedo trasero
for s in (-1, 1):
    for k in (-1, 0, 1):
        b('Leg_R' if s > 0 else 'Leg_L', (s * 0.50 + k * 0.18, 0.42, 0.20), (0.14, 0.64, 0.14), 'garra')
        b('Leg_R' if s > 0 else 'Leg_L', (s * 0.50 + k * 0.18, 0.78, 0.17), (0.11, 0.15, 0.11), 'una')
    b('Leg_R' if s > 0 else 'Leg_L', (s * 0.50, -0.20, 0.20), (0.14, 0.32, 0.14), 'garra')
# patas que cuelgan al volar (Maikol): tarso y dedos giran desde la cadera, dentro del muslo; los dedos apuntan hacia abajo
PIVOTE_PATA = {lado: Vector((s * 0.50, 0.10, 0.68)) for s, lado in ((1, 'R'), (-1, 'L'))}
for s, lado in ((1, 'R'), (-1, 'L')):
    colgar_pata(MBS['Leg_' + lado], PIVOTE_PATA[lado], -48.0, s * 4.0)

# ---------------------------------------------------------------- alas grandes de plumas con degradado rojo-naranja-amarillo, en arco
S_HOMBRO = Vector((0.92, -0.15, 2.12))
A_BRAZO = 1.60
D1, SW1, D2, SW2 = 14.0, 8.0, 24.0, 16.0
MARCOS = {}
PUNTOS_ALA = {}
for s, lado in ((1, 'R'), (-1, 'L')):
    W_, T_ = 'Wing_' + lado, 'Tip_' + lado
    Sv = Vector((s * S_HOMBRO.x, S_HOMBRO.y, S_HOMBRO.z))
    M1, M2, H = marco_ala(Sv, s, A_BRAZO, D1, SW1, D2, SW2)
    MARCOS[lado] = (M1, M2, H, Sv)
    caja_marco(MBS[W_], M1, (s * 0.66, 0.0, 0.0), (1.50, 0.52, 0.50), 'ala_a')
    caja_marco(MBS[W_], M1, (s * 1.55, 0.0, 0.0), (0.64, 0.46, 0.44), 'ala_a')
    for i in range(6):
        L = 1.12 + 0.07 * i + (0.14 if i % 2 == 0 else 0.0)                  # dientes de sierra en el borde de salida
        pluma(MBS[W_], M1, (s * (0.22 + 0.26 * i), -0.30), dir_ala(s, 84 - 2 * i), L, 0.54, 0.20, 0.05 * i,
              [(0.45, 'ala_a'), (0.78, 'ala_b'), (1.0, 'ala_c')], afilar=0.72)
    for i in range(5):
        pluma(MBS[W_], M1, (s * (0.22 + 0.30 * i), 0.24), dir_ala(s, 82 - 3 * i), 1.10 - 0.07 * i, 0.50, 0.16, 0.27 + 0.035 * i,
              [(0.5, 'ala_c'), (1.0, 'ala_c2')], afilar=0.75)
    for i in range(4):
        pluma(MBS[W_], M1, (s * (0.34 + 0.30 * i), 0.30), dir_ala(s, 80 - 3 * i), 0.62 - 0.04 * i, 0.44, 0.14, 0.46 + 0.035 * i,
              [(1.0, 'ala_punta')], afilar=0.7)
    for i in range(8):
        th = 3.0 + 8.6 * i
        L = 2.45 - 0.15 * i + (0.24 if i % 2 == 0 else 0.0)                  # primarias largas y cortas alternas: borde de llamas
        pluma(MBS[T_], M2, (s * 0.04 * i, -0.06 * i), dir_ala(s, th), L, 0.50, 0.20, 0.05 * i,
              [(0.30, 'ala_b'), (0.58, 'ala_c'), (0.80, 'ala_c2'), (1.0, 'ala_punta')], afilar=0.62, chaflan=0.10)
        if i == 0:
            a_ = math.radians(dir_ala(s, th))
            PUNTOS_ALA[lado] = tuple(round(v, 3) for v in (M2 @ Vector((math.cos(a_) * L, math.sin(a_) * L, 0))))
    for i in range(3):
        pluma(MBS[T_], M2, (s * 0.02, 0.22 - 0.04 * i), dir_ala(s, 14 + 20 * i), 1.0 - 0.12 * i, 0.46, 0.14, 0.27 + 0.04 * i,
              [(0.6, 'ala_c'), (1.0, 'ala_c2')])
    caja_marco(MBS[T_], M2, (s * 0.10, 0.0, 0.0), (0.46, 0.50, 0.46), 'ala_a')
    rombo(MBS[W_], (s * 1.30, 0.12, 0.29), 0.38, 0.10, 'oro', 'Z', 45.0, M=M1)

# ---------------------------------------------------------------- cola: siete plumas largas de dos tramos en copa que se curvan hacia abajo (rojo -> naranja -> amarillo)
M_COLA = tr((0, -0.98, 1.05)) @ rx(8)
caja_marco(MBS['Tail'], M_COLA, (0, 0.06, 0.0), (1.10, 0.56, 0.46), 'cuerpo_osc')
PUNTOS_COLA = []
for k in range(7):
    d_ = abs(k - 3)
    L1, L2 = ((1.55, 1.55), (1.45, 1.40), (1.25, 1.10), (1.05, 0.85))[d_]
    ang = -90 + (k - 3) * 12
    zc = 0.06 * k
    Ma = M_COLA @ rx((0, 4, 9, 15)[d_])                                      # las plumas de fuera caen mas: la cola sale en copa y se ve llena de lado
    pluma(MBS['Tail'], Ma, ((k - 3) * 0.11, 0.0), ang, L1, 0.50, 0.26, zc, [(0.55, 'cola_a'), (1.0, 'cola_b')], afilar=0.84, chaflan=0.0)
    a_ = math.radians(ang)
    fin = Vector(((k - 3) * 0.11 + math.cos(a_) * L1, math.sin(a_) * L1, 0.0))
    Mb = Ma @ tr(fin) @ rx(26)                                               # el segundo tramo cae mas: la pluma se curva como un cometa
    pluma(MBS['Tail'], Mb, (0.0, 0.0), ang, L2, 0.42, 0.26, zc, [(0.5, 'cola_b'), (1.0, 'cola_c')], afilar=0.55, chaflan=0.10)
    PUNTOS_COLA.append(tuple(round(v, 3) for v in (Mb @ Vector((math.cos(a_) * L2, math.sin(a_) * L2, 0)))))

# ---------------------------------------------------------------- rig (los ocho huesos de las mascotas de Codex) y malla unica
HUESOS = [('Root', (0, 0, 1.0), None, 0.5), ('Body', (0, -0.10, 1.58), 'Root', 0.6), ('Head', (0, 0.15, 2.60), 'Body', 0.6),
          ('Tail', (0, -0.98, 1.05), 'Body', 0.6)]
for lado in ('R', 'L'):
    M1, M2, H, Sv = MARCOS[lado]
    HUESOS.append(('Wing_' + lado, tuple(Sv), 'Body', 0.6))
    HUESOS.append(('Tip_' + lado, tuple(H), 'Wing_' + lado, 0.6))
for s, lado in ((1, 'R'), (-1, 'L')):
    HUESOS.append(('Leg_' + lado, tuple(PIVOTE_PATA[lado]), 'Body', 0.4))
    HUESOS.append(('Lid_' + lado, (s * 0.56, 1.24, 3.20), 'Head', 0.3))
PARPADO_DY['dy'] = DY_PARPADO
ob, rig = armar(NOMBRE, MBS, HUESOS, CM)
TRIS = A.tris([ob])
mn = Vector([min(v.co[a] for v in ob.data.vertices) for a in range(3)])
mx = Vector([max(v.co[a] for v in ob.data.vertices) for a in range(3)])
A.log('triangulos', TRIS, 'envergadura %.2f alto %.2f largo %.2f escamas %d' % (mx.x - mn.x, mx.z - mn.z, mx.y - mn.y, N_ESC))
BOUNDS = dict(envergadura=round(mx.x - mn.x, 2), alto=round(mx.z - mn.z, 2), largo=round(mx.y - mn.y, 2), z_min=round(mn.z, 2))
SUELTAS, N_ISLAS = piezas_sueltas(ob)
A.log('piezas sueltas:', SUELTAS if SUELTAS else 'ninguna', '(de %d islas)' % N_ISLAS)
COPLANARES, EJ_COPL = caras_coplanares(ob)
A.log('caras coplanares solapadas (posible parpadeo):', COPLANARES, EJ_COPL[:8])
if FASE == 'check':
    sys.exit(0)
pose = hacer_pose(rig)
PUNTOS_FUEGO = {'cresta': PLUMAS_CRESTA[2], 'punta_ala_R': PUNTOS_ALA['R'], 'punta_ala_L': PUNTOS_ALA['L'], 'puntas_cola': PUNTOS_COLA,
                'pecho': (0.0, 0.8, 1.9), 'huesos_recomendados': {'cresta': 'Head', 'punta_ala_R': 'Tip_R', 'punta_ala_L': 'Tip_L', 'puntas_cola': 'Tail', 'pecho': 'Body'}}

E = Escena(CR, CC, PREV, FASE, radio=11.5, maniqui=(-6.0, 0.4), regla=(6.6, 0.4), objetivo=(-0.6, -1.0, 2.1))
shot = E.foto

if FASE == 'geo':
    planos(ob, PAL)
    pose()
    shot('_geo_frente', 180, 8, 24.0, scale=True)
    shot('_geo_34', 148, 16, 23.0)
    shot('_geo_lado', 90, 8, 23.0)
    shot('_geo_cara', 160, 10, 9.5, target=(0, 0.6, 3.0))
    shot('_geo_espalda', 0, 12, 23.0)
    shot('_geo_arriba', 180, 82, 25.0)
    acts, CLIPS = clips_pet(rig)
    for nom, t in (('a', 0.0), ('d', 0.60), ('f', 0.90)):
        en(rig, acts, 'Fly', t)
        shot('_geo_fly_' + nom, 180, 10, 23.0)
    A.log('fase geo lista')
    sys.exit(0)

# ---------------------------------------------------------------- textura pintada (sombras calidas)
Pn = hornear(ob, 5.0)
E.reiniciar_render()
BASE = dict(var=0.05, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.06, ao=0.5, ao_tint='#4a0c08', light=0.24,
            hue_var=0.02, blotch=0.045, edge=0.7, edge_th=0.05, edge_break=0.3)


def reg(name, **kw):
    if name not in A.REGIONS:
        return None
    k = dict(BASE)
    k.update(kw)
    if 'edge_col' not in k:
        k['edge_col'] = claro(PAL[name])
    return Pn.region(name, PAL[name], **k)


reg('cuerpo', extra=chevrones('#8c150c', 0.34, 0.14), seed=1)
reg('cuerpo_osc', seed=2)
reg('pecho', extra=chevrones('#d96510', 0.30, 0.18), seed=3)
reg('vientre', extra=chevrones('#e0a820', 0.28, 0.16), seed=4)
reg('escama', edge_col='#ffe08a', seed=5)
reg('escama_osc', edge_col='#e05a40', seed=6)
reg('cabeza', var=0.03, seed=7, extra=chevrones('#b82610', 0.28, 0.12))
reg('pico', edge_col='#fff0a0', var=0.03, seed=8)
reg('pico_inf', edge_col='#f1c860', var=0.03, seed=9)
reg('cera', edge_col='#fff3b8', var=0.02, seed=10)
reg('pupila', edge=0.0, var=0.0, ao=0.1, face_var=0.0, seed=11)
reg('brillo', edge=0.0, var=0.0, ao=0.0, light=0.0, face_var=0.0, seed=12)
reg('ceja', seed=13)
reg('oro', edge_col='#fff0a0', var=0.03, ao=0.25, light=0.12, grad=0.4, seed=14)
WING = dict(stroke=(6.0, 1.0, 1.0), stroke_scale=3.0, var=0.06, blotch=0.05)
reg('ala_a', edge_col='#e05a40', seed=21, **WING)
reg('ala_b', edge_col='#ff8a60', seed=22, **WING)
reg('ala_c', edge_col='#ffc070', seed=23, **WING)
reg('ala_c2', edge_col='#fff0a8', ao=0.35, light=0.14, seed=24, **WING)
reg('ala_punta', edge_col='#ffffff', ao=0.2, light=0.08, seed=25, **WING)
COLA = dict(stroke=(1.0, 6.0, 1.0), stroke_scale=3.0, var=0.05)
reg('cola_a', edge_col='#f06a50', seed=26, **COLA)
reg('cola_b', edge_col='#ffa060', seed=27, **COLA)
reg('cola_c', edge_col='#fff0a8', ao=0.3, light=0.12, seed=28, **COLA)
reg('llama_a', edge_col='#f58060', seed=29, **COLA)
reg('llama_b', edge_col='#ffc070', seed=30, **COLA)
reg('llama_c', edge_col='#fff4b8', ao=0.2, light=0.1, seed=31, **COLA)
reg('garra', edge_col='#fff0a0', seed=32)
reg('una', edge_col='#6a4a40', var=0.02, seed=33)
guardar_textura(Pn, ob, OUT, NOMBRE)

# ---------------------------------------------------------------- clips y renders
acts, CLIPS = clips_pet(rig, amp={'ala': 1.0, 'cola': 1.3})
if RENDER:
    shots = []
    rig.animation_data_clear()
    pose()
    shots.append((shot('Fenix-frente', 180, 8, 24.0, scale=True), 'FRENTE (REGLA 6 STUDS)'))
    shots.append((shot('Fenix-tres-cuartos', 148, 16, 23.0), '3/4'))
    shots.append((shot('Fenix-lateral', 90, 8, 23.0), 'LATERAL'))
    shots.append((shot('Fenix-espalda', 0, 12, 23.0), 'ESPALDA'))
    shots.append((shot('Fenix-arriba', 180, 82, 25.0), 'DESDE ARRIBA'))
    shots.append((shot('Fenix-cara', 160, 10, 9.5, target=(0, 0.6, 3.0)), 'CARA'))
    pose(lid=1.0)
    shots.append((shot('Fenix-cara-parpadeo', 160, 10, 9.5, target=(0, 0.6, 3.0)), 'PARPADEO (CLIP BLINK)'))
    pose()
    en(rig, acts, 'Fly', 0.0)
    shots.append((shot('Fenix-aleteo-alto', 150, 10, 23.0), 'ALETEO ARRIBA (EXTENDIDA)'))
    en(rig, acts, 'Fly', 0.46)
    shots.append((shot('Fenix-aleteo-bajo', 150, 10, 23.0), 'ALETEO ABAJO'))
    en(rig, acts, 'Fly', 0.70)
    shots.append((shot('Fenix-aleteo-recogida', 150, 10, 23.0), 'ALETEO RECOGIENDO'))
    en(rig, acts, 'Glide', 0.5)
    shots.append((shot('Fenix-planeo', 150, 10, 23.0), 'PLANEO'))
    en(rig, acts, 'Celebrate', 0.8)
    shots.append((shot('Fenix-celebrar', 160, 10, 23.0), 'CELEBRAR'))
    W.contact_sheet(shots, 3, os.path.join(PREV, '_hoja.png'), title='FENIX V02 - RENDERS DE BLENDER')
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, 'Fenix-hoja.jpg'), 0.5)

    A.setup_render((700, 560), 'CYCLES', 24)
    E.formato()
    seq = []
    for nom, t, etq in (('a', 0.0, 'ARRIBA EXTENDIDA'), ('b', 0.28, 'IMPULSO'), ('c', 0.46, 'ABAJO'), ('d', 0.60, 'RECOGE'), ('e', 0.78, 'RECOGIDA'), ('f', 0.90, 'EXTIENDE')):
        en(rig, acts, 'Fly', t)
        seq.append((shot('_seq_' + nom, 150, 10, 23.0), etq))
    W.contact_sheet(seq, 3, os.path.join(PREV, '_seq.png'), title='FENIX - ALETEO (1 S, 6 POSES)')
    a_jpg(os.path.join(PREV, '_seq.png'), os.path.join(PREV, 'Fenix-aleteo-secuencia.jpg'), 0.6)
    for nom in 'abcdef':
        try:
            os.remove(os.path.join(PREV, '_seq_%s.jpg' % nom))
        except OSError:
            pass
    E.reiniciar_render()

exportar_pet(OUT, NOMBRE, ob, rig, acts, CLIPS, pose, {
    'pieza': 'Fenix v02 (mascota voladora alta, Robux; el fuego va aparte)', 'triangulos': TRIS, 'limites_studs': BOUNDS,
    'huesos': [h[0] for h in HUESOS], 'rejilla_voxel_studs': C, 'paleta': PAL, 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPLANARES, 'escamas': N_ESC,
    'puntos_fuego': PUNTOS_FUEGO})
A.log('listo')
