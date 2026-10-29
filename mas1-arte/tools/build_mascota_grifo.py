# Grifo MITICO v02 para «+1 de lanzamiento por segundo»: mascota voladora alta. Cabeza y pecho de aguila, cuerpo y cola de leon, alas grandes
# violetas con puntas doradas (rareza mitica). Mismo lenguaje que el aguila v02: volumenes escalonados de celda 0,2, escamas de plumas en
# relieve, ojos pequenos, alas en arco de plumas en abanico y rombos dorados; referencia de «Roba un huevo» (Steal an Egg) pedida por Maikol.
# blender -b --factory-startup --python-exit-code 1 -P build_mascota_grifo.py      (MASCOTA_FASE=geo para la fase rapida)
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo el cuerpo.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *

FASE = os.environ.get('MASCOTA_FASE', 'full')
RENDER = FASE != 'assets'          # 'assets': solo textura, rig, clips y exportacion (sin renders); los previews no cambian
NOMBRE = 'GrifoMitico'
OUT = os.path.abspath(os.path.join(HERE, '..', 'mascotas-altas-v02', 'grifo-mitico'))
PREV = os.path.join(OUT, 'previews')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

A.clean_scene()
bpy.context.scene.render.fps = 30
CM = A.collection('Mascota')
CR = A.collection('Ref')
CC = A.collection('Camaras')

PAL = {
    'cuerpo': '#c9923f', 'cuerpo_osc': '#9c6a2b', 'escama_osc': '#b57d33', 'pecho': '#f6efe0', 'escama': '#e6dcf4', 'vientre': '#eadbb8',
    'cabeza': '#fbf7ee', 'pico': '#f5b82e', 'pico_inf': '#d99a1c', 'cera': '#ffd54a', 'ojo': '#7ee8ff', 'pupila': '#10161f', 'brillo': '#ffffff',
    'ceja': '#9c6a2b', 'oro': '#ffc42e', 'oreja': '#efe6d2', 'ala_a': '#4a2aa6', 'ala_b': '#6a3fd0', 'ala_c': '#9a7bf0', 'ala_c2': '#cdbcff',
    'ala_punta': '#ffd66e', 'cola': '#c9923f', 'cola_punta': '#6a3fd0', 'garra': '#f1b222', 'una': '#2a2024', 'pata': '#a9742f', 'dedo': '#6e4a1f',
    'melena': '#7b4be0',
}
C = 0.2
V = Vox(C)
MBS = {b: A.MB('G_' + b) for b in BONES + BONES_PATAS_TRASERAS}


def reg_cuerpo(p, n):
    if p.y > 0.05 and p.z > 1.05 and abs(p.x) < 0.88:
        return 'pecho'                                              # pecho emplumado blanco de aguila
    if p.z < 0.95 and p.y > -0.5:
        return 'vientre'
    if p.y < -0.9 and p.z < 1.15:
        return 'cuerpo_osc'                                         # grupa y muslos mas oscuros
    return 'cuerpo'


def b(bone, c, size, mat):
    MBS[bone].box(c, size, mat)


# ---------------------------------------------------------------- cuerpo: pecho de aguila delante, tronco y ancas de leon detras
V.elipsoide((0, 0.50, 1.70), (0.96, 0.86, 1.00), 'Body', reg_cuerpo, exp=2.8)               # pecho
V.elipsoide((0, -0.85, 1.38), (0.92, 1.15, 0.82), 'Body', reg_cuerpo, exp=2.7)              # tronco
for s in (-1, 1):
    V.elipsoide((s * 0.70, -1.30, 1.02), (0.46, 0.66, 0.66), 'Body', 'cuerpo_osc', exp=2.4)      # ancas
# cabeza de aguila, grande
V.elipsoide((0, 1.20, 3.12), (0.94, 0.88, 0.84), 'Head', 'cabeza', exp=2.6)
# patas delanteras de aguila (amarillas) y traseras de leon (pardas)
for s in (-1, 1):
    V.caja((s * 0.46, 0.78, 0.50), (0.34, 0.34, 0.80), 'Leg_R' if s > 0 else 'Leg_L', 'garra')
    V.caja((s * 0.70, -1.40, 0.36), (0.46, 0.52, 0.56), 'LegB_R' if s > 0 else 'LegB_L', 'pata')
# cola de leon: cadena de elipsoides que se tocan, sube en S y acaba en la borla violeta (todo unido)
cola = [((0, -2.05, 1.40), 0.36), ((0, -2.30, 1.58), 0.34), ((0, -2.50, 1.84), 0.32), ((0, -2.58, 2.14), 0.31)]
for c_, r_ in cola:
    V.elipsoide(c_, (r_, r_, r_ * 1.05), 'Tail', 'cola', exp=2.4)
V.elipsoide((0, -2.54, 2.62), (0.50, 0.46, 0.56), 'Tail', 'melena', exp=2.4)         # borla de pelo violeta
V.construir(MBS)
# plumas en llama sobre la borla (tres hojas verticales barridas hacia atras, apoyadas en la bola)
for j, (tilt, L_, off) in enumerate(((4, 1.15, -0.07), (28, 1.02, 0.0), (52, 0.88, 0.07))):
    Mc = tr((off, -2.50, 3.00)) @ rx(tilt) @ ry(-90)
    pluma(MBS['Tail'], Mc, (0, 0), 0, L_, 0.62, 0.20 + 0.02 * j, 0.0, [(0.5, 'ala_b'), (1.0, 'ala_c')], afilar=0.45, chaflan=0.07)

# escamas de plumas en relieve (pecho, hombros) y pelaje del leon en el tronco
N_ESC = 0
N_ESC += escamas(V, MBS, 'Body', 'escama', (0, 1, 0), lambda p: 1.15 < p.z < 2.55 and abs(p.x) < 0.80 and p.y > 0.2, alto=0.09, patron=tresbolillo)
for sx in (-1, 1):
    N_ESC += escamas(V, MBS, 'Body', 'escama_osc', (sx, 0, 0), lambda p: 0.85 < p.z < 1.9 and p.y < -0.1, alto=0.08, patron=dispersas(0.45, 5 + sx))
N_ESC += escamas(V, MBS, 'Body', 'escama_osc', (0, 0, 1), lambda p: p.y < -0.2 and abs(p.x) < 0.7, alto=0.08, patron=dispersas(0.45, 11))

# ---------------------------------------------------------------- cara: pico ancho, ojos pequenos celestes con pupila y brillo, cejas, orejas-pluma
b('Head', (0, 2.06, 3.18), (0.72, 0.60, 0.50), 'pico')
b('Head', (0, 2.46, 3.07), (0.54, 0.34, 0.40), 'pico')
b('Head', (0, 2.64, 2.84), (0.34, 0.22, 0.34), 'pico')
b('Head', (0, 2.69, 2.62), (0.22, 0.14, 0.20), 'pico_inf')
b('Head', (0, 1.98, 2.76), (0.54, 0.62, 0.17), 'pico_inf')
b('Head', (0, 1.78, 3.50), (0.72, 0.18, 0.15), 'cera')
for s in (-1, 1):
    b('Head', (s * 0.58, 1.90, 3.30), (0.22, 0.15, 0.28), 'ojo')
    b('Head', (s * 0.58, 1.98, 3.32), (0.10, 0.05, 0.16), 'pupila')
    b('Head', (s * 0.54, 1.99, 3.40), (0.06, 0.04, 0.07), 'brillo')
    DY_PARPADO = parpado(MBS['Lid_R' if s > 0 else 'Lid_L'], (s * 0.58, 1.90, 3.30), (0.22, 0.15, 0.28), 2.01, 'cabeza', 'pupila')
    cubo_girado(MBS['Head'], (s * 0.56, 1.90, 3.58), (0.48, 0.16, 0.13), 'ceja', rot=(0, -s * 14, 0))
    # orejas-pluma: bloques girados hacia fuera, crema con la punta dorada
    cubo_girado(MBS['Head'], (s * 0.62, 1.00, 3.98), (0.36, 0.40, 0.56), 'oreja', rot=(0, s * 22, 0))
    cubo_girado(MBS['Head'], (s * 0.78, 1.00, 4.34), (0.26, 0.32, 0.28), 'oro', rot=(0, s * 30, 0))
# melena violeta: dos plumas barridas por detras de la cabeza
cubo_girado(MBS['Head'], (0, 0.55, 3.94), (0.36, 0.40, 0.44), 'melena', rot=(24, 0, 0))
cubo_girado(MBS['Head'], (0, 0.22, 3.90), (0.32, 0.36, 0.40), 'melena', rot=(44, 0, 0))
rombo(MBS['Head'], (0, 1.97, 3.62), 0.30, 0.10, 'oro', 'Y')                  # gema dorada en la frente (rareza mitica)
rombo(MBS['Body'], (0, 1.34, 1.95), 0.50, 0.11, 'oro', 'Y')                 # medalla dorada en el pecho

# pies: tres dedos al frente con unas negras (delanteros), garras de leon atras
for s in (-1, 1):
    for k in (-1, 0, 1):
        b('Leg_R' if s > 0 else 'Leg_L', (s * 0.46 + k * 0.19, 1.02, 0.20), (0.15, 0.66, 0.15), 'garra')
        b('Leg_R' if s > 0 else 'Leg_L', (s * 0.46 + k * 0.19, 1.40, 0.17), (0.12, 0.16, 0.12), 'una')
    for k in (-1, 0, 1):
        b('LegB_R' if s > 0 else 'LegB_L', (s * 0.70 + k * 0.17, -1.12, 0.21), (0.15, 0.30, 0.15), 'dedo')
# patas que cuelgan al volar (Maikol): las delanteras giran desde el pecho y las traseras desde el anca; los pies apuntan hacia abajo
PIVOTE_PATA = {lado: Vector((s * 0.46, 0.74, 0.98)) for s, lado in ((1, 'R'), (-1, 'L'))}
PIVOTE_PATA_B = {lado: Vector((s * 0.70, -1.36, 0.70)) for s, lado in ((1, 'R'), (-1, 'L'))}
for s, lado in ((1, 'R'), (-1, 'L')):
    colgar_pata(MBS['Leg_' + lado], PIVOTE_PATA[lado], -40.0, s * 4.0)
    colgar_pata(MBS['LegB_' + lado], PIVOTE_PATA_B[lado], -36.0, s * 3.0)

# ---------------------------------------------------------------- alas grandes violetas con puntas doradas, en arco
S_HOMBRO = Vector((0.92, 0.10, 2.22))
A_BRAZO = 1.60
D1, SW1, D2, SW2 = 14.0, 8.0, 22.0, 14.0
MARCOS = {}
for s, lado in ((1, 'R'), (-1, 'L')):
    W_, T_ = 'Wing_' + lado, 'Tip_' + lado
    Sv = Vector((s * S_HOMBRO.x, S_HOMBRO.y, S_HOMBRO.z))
    M1, M2, H = marco_ala(Sv, s, A_BRAZO, D1, SW1, D2, SW2)
    MARCOS[lado] = (M1, M2, H, Sv)
    caja_marco(MBS[W_], M1, (s * 0.66, 0.0, 0.0), (1.50, 0.52, 0.50), 'ala_a')
    caja_marco(MBS[W_], M1, (s * 1.55, 0.0, 0.0), (0.64, 0.46, 0.44), 'ala_a')
    for i in range(6):
        pluma(MBS[W_], M1, (s * (0.22 + 0.26 * i), -0.30), dir_ala(s, 84 - 2 * i), 1.20 + 0.07 * i, 0.56, 0.20, 0.05 * i,
              [(0.50, 'ala_a'), (0.80, 'ala_b'), (1.0, 'ala_c')])
    for i in range(5):
        pluma(MBS[W_], M1, (s * (0.22 + 0.30 * i), 0.24), dir_ala(s, 82 - 3 * i), 1.15 - 0.07 * i, 0.52, 0.16, 0.27 + 0.035 * i,
              [(0.55, 'ala_c'), (1.0, 'ala_c2')])
    for i in range(4):
        pluma(MBS[W_], M1, (s * (0.34 + 0.32 * i), 0.30), dir_ala(s, 80 - 3 * i), 0.64 - 0.04 * i, 0.46, 0.14, 0.46 + 0.035 * i,
              [(0.5, 'ala_c2'), (1.0, 'ala_punta')])
    for i in range(7):
        th = 4.0 + 9.6 * i
        pluma(MBS[T_], M2, (s * 0.04 * i, -0.06 * i), dir_ala(s, th), 2.35 - 0.16 * i, 0.52, 0.20, 0.05 * i,
              [(0.48, 'ala_b'), (0.78, 'ala_c'), (1.0, 'ala_punta')])
    for i in range(3):
        pluma(MBS[T_], M2, (s * 0.02, 0.22 - 0.04 * i), dir_ala(s, 14 + 20 * i), 1.0 - 0.12 * i, 0.46, 0.14, 0.27 + 0.04 * i,
              [(0.6, 'ala_c'), (1.0, 'ala_c2')])
    caja_marco(MBS[T_], M2, (s * 0.10, 0.0, 0.0), (0.46, 0.50, 0.46), 'ala_a')
    rombo(MBS[W_], (s * 1.30, 0.12, 0.29), 0.38, 0.10, 'oro', 'Z', 45.0, M=M1)

# ---------------------------------------------------------------- rig (los ocho huesos de las mascotas de Codex) y malla unica
HUESOS = [('Root', (0, 0, 1.0), None, 0.5), ('Body', (0, -0.20, 1.60), 'Root', 0.6), ('Head', (0, 0.85, 2.60), 'Body', 0.6),
          ('Tail', (0, -1.95, 1.40), 'Body', 0.6)]
for lado in ('R', 'L'):
    M1, M2, H, Sv = MARCOS[lado]
    HUESOS.append(('Wing_' + lado, tuple(Sv), 'Body', 0.6))
    HUESOS.append(('Tip_' + lado, tuple(H), 'Wing_' + lado, 0.6))
for s, lado in ((1, 'R'), (-1, 'L')):
    HUESOS.append(('Leg_' + lado, tuple(PIVOTE_PATA[lado]), 'Body', 0.4))
    HUESOS.append(('LegB_' + lado, tuple(PIVOTE_PATA_B[lado]), 'Body', 0.4))
    HUESOS.append(('Lid_' + lado, (s * 0.58, 1.90, 3.30), 'Head', 0.3))
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

E = Escena(CR, CC, PREV, FASE, radio=11.5, maniqui=(-6.0, 0.4), regla=(6.6, 0.4), objetivo=(-0.6, -0.4, 2.2))
shot = E.foto

if FASE == 'geo':
    planos(ob, PAL)
    pose()
    shot('_geo_frente', 180, 8, 23.0, scale=True)
    shot('_geo_34', 148, 16, 21.0)
    shot('_geo_lado', 90, 8, 21.0)
    shot('_geo_cara', 160, 10, 9.5, target=(0, 1.2, 3.0))
    shot('_geo_espalda', 0, 12, 21.0)
    shot('_geo_arriba', 180, 82, 23.0)
    acts, CLIPS = clips_pet(rig)
    for nom, t in (('a', 0.0), ('d', 0.60), ('f', 0.90)):
        en(rig, acts, 'Fly', t)
        shot('_geo_fly_' + nom, 180, 10, 21.0)
    A.log('fase geo lista')
    sys.exit(0)

# ---------------------------------------------------------------- textura pintada
Pn = hornear(ob, 5.0)
E.reiniciar_render()
BASE = dict(var=0.05, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.06, ao=0.55, ao_tint='#2b2455', light=0.26,
            hue_var=0.02, blotch=0.045, edge=0.7, edge_th=0.05, edge_break=0.3)


def reg(name, **kw):
    if name not in A.REGIONS:
        return None
    k = dict(BASE)
    k.update(kw)
    if 'edge_col' not in k:
        k['edge_col'] = claro(PAL[name])
    return Pn.region(name, PAL[name], **k)


reg('cuerpo', extra=chevrones('#8a5a20', 0.34, 0.14), seed=1)
reg('cuerpo_osc', extra=chevrones('#6e4617', 0.30, 0.16), seed=2)
reg('escama_osc', edge_col='#e0a85a', seed=3)
reg('pecho', ao_tint='#7f8bb0', extra=chevrones('#cfc6d8', 0.30, 0.14), seed=4)
reg('escama', ao_tint='#7f8bb0', edge_col='#ffffff', seed=5)
reg('vientre', extra=chevrones('#bda77a', 0.28, 0.16), seed=6)
reg('cabeza', ao_tint='#7f8bb0', var=0.03, seed=7, extra=chevrones('#d3cfc9', 0.28, 0.12))
reg('pico', edge_col='#fff0a0', var=0.03, seed=8)
reg('pico_inf', edge_col='#f1c860', var=0.03, seed=9)
reg('cera', edge_col='#fff3b8', var=0.02, seed=10)
reg('ojo', edge_col='#e2fbff', var=0.0, ao=0.1, light=0.0, face_var=0.0, seed=11)
reg('pupila', edge=0.0, var=0.0, ao=0.1, face_var=0.0, seed=12)
reg('brillo', edge=0.0, var=0.0, ao=0.0, light=0.0, face_var=0.0, seed=13)
reg('ceja', seed=14)
reg('oro', edge_col='#fff0a0', var=0.03, ao=0.25, light=0.12, grad=0.4, seed=15)
reg('oreja', ao_tint='#7f8bb0', edge_col='#ffffff', seed=16)
reg('melena', edge_col='#b99cff', seed=17)
WING = dict(stroke=(6.0, 1.0, 1.0), stroke_scale=3.0, var=0.06, blotch=0.05)
reg('ala_a', edge_col='#7f5fd0', seed=21, **WING)
reg('ala_b', edge_col='#9d7bf0', seed=22, **WING)
reg('ala_c', edge_col='#c9b4ff', seed=23, **WING)
reg('ala_c2', edge_col='#f1eaff', seed=24, **WING)
reg('ala_punta', edge_col='#fff0c8', ao=0.25, light=0.10, seed=25, **WING)
reg('cola', edge_col='#e0a85a', seed=26)
reg('cola_punta', edge_col='#b99cff', seed=27)
reg('garra', edge_col='#fff0a0', seed=28)
reg('una', edge_col='#6a5a60', var=0.02, seed=29)
reg('pata', edge_col='#d9a45a', seed=30)
reg('dedo', edge_col='#a0713a', seed=31)
guardar_textura(Pn, ob, OUT, NOMBRE)

# ---------------------------------------------------------------- clips y renders
acts, CLIPS = clips_pet(rig, amp={'ala': 1.0, 'cola': 1.1})
if RENDER:
    shots = []
    rig.animation_data_clear()
    pose()
    shots.append((shot('Grifo-mitico-frente', 180, 8, 23.0, scale=True), 'FRENTE (REGLA 6 STUDS)'))
    shots.append((shot('Grifo-mitico-tres-cuartos', 148, 16, 21.0), '3/4'))
    shots.append((shot('Grifo-mitico-lateral', 90, 8, 21.0), 'LATERAL'))
    shots.append((shot('Grifo-mitico-espalda', 0, 12, 21.0), 'ESPALDA'))
    shots.append((shot('Grifo-mitico-arriba', 180, 82, 23.0), 'DESDE ARRIBA'))
    shots.append((shot('Grifo-mitico-cara', 160, 10, 9.5, target=(0, 1.2, 3.0)), 'CARA'))
    pose(lid=1.0)
    shots.append((shot('Grifo-mitico-cara-parpadeo', 160, 10, 9.5, target=(0, 1.2, 3.0)), 'PARPADEO (CLIP BLINK)'))
    pose()
    en(rig, acts, 'Fly', 0.0)
    shots.append((shot('Grifo-mitico-aleteo-alto', 150, 10, 21.0), 'ALETEO ARRIBA (EXTENDIDA)'))
    en(rig, acts, 'Fly', 0.46)
    shots.append((shot('Grifo-mitico-aleteo-bajo', 150, 10, 21.0), 'ALETEO ABAJO'))
    en(rig, acts, 'Fly', 0.70)
    shots.append((shot('Grifo-mitico-aleteo-recogida', 150, 10, 21.0), 'ALETEO RECOGIENDO'))
    en(rig, acts, 'Glide', 0.5)
    shots.append((shot('Grifo-mitico-planeo', 150, 10, 21.0), 'PLANEO'))
    en(rig, acts, 'Celebrate', 0.8)
    shots.append((shot('Grifo-mitico-celebrar', 160, 10, 21.0), 'CELEBRAR'))
    W.contact_sheet(shots, 3, os.path.join(PREV, '_hoja.png'), title='GRIFO MITICO V02 - RENDERS DE BLENDER')
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, 'Grifo-mitico-hoja.jpg'), 0.5)

    A.setup_render((700, 560), 'CYCLES', 24)
    E.formato()
    seq = []
    for nom, t, etq in (('a', 0.0, 'ARRIBA EXTENDIDA'), ('b', 0.28, 'IMPULSO'), ('c', 0.46, 'ABAJO'), ('d', 0.60, 'RECOGE'), ('e', 0.78, 'RECOGIDA'), ('f', 0.90, 'EXTIENDE')):
        en(rig, acts, 'Fly', t)
        seq.append((shot('_seq_' + nom, 150, 10, 21.0), etq))
    W.contact_sheet(seq, 3, os.path.join(PREV, '_seq.png'), title='GRIFO MITICO - ALETEO (1 S, 6 POSES)')
    a_jpg(os.path.join(PREV, '_seq.png'), os.path.join(PREV, 'Grifo-mitico-aleteo-secuencia.jpg'), 0.6)
    for nom in 'abcdef':
        try:
            os.remove(os.path.join(PREV, '_seq_%s.jpg' % nom))
        except OSError:
            pass
    E.reiniciar_render()

exportar_pet(OUT, NOMBRE, ob, rig, acts, CLIPS, pose, {
    'pieza': 'Grifo mitico v02 (mascota voladora alta)', 'triangulos': TRIS, 'limites_studs': BOUNDS,
    'huesos': [h[0] for h in HUESOS], 'rejilla_voxel_studs': C, 'paleta': PAL, 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPLANARES, 'escamas': N_ESC})
A.log('listo')
