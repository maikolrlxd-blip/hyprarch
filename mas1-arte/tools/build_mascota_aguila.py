# Aguila LEGENDARIA v02 para «+1 de lanzamiento por segundo»: mascota voladora alta. Estilo de las mascotas de Codex (volumenes escalonados de
# celda 0,2) y, por peticion de Maikol (29/10), referencia de «Roba un huevo» (Steal an Egg): cuerpo rechoncho, escamas de plumas en relieve,
# ojos diminutos y, en las mascotas de rareza alta, alas grandes de plumas en capas con puntas doradas y adornos dorados en rombo.
# v02 rehace la v01 (alas de persiana, cola de tabla, hombros sueltos): alas en arco de plumas en abanico, cola unida al cuerpo.
# blender -b --factory-startup --python-exit-code 1 -P build_mascota_aguila.py
#   MASCOTA_FASE=geo   -> geometria con colores planos y renders rapidos
#   MASCOTA_FASE=full  -> textura pintada, rig, clips Fly/Glide/Celebrate, FBX/GLB y renders (por defecto)
# Ejes: +Y delante, +Z arriba, +X derecha; el origen esta en el suelo bajo el cuerpo.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *

FASE = os.environ.get('MASCOTA_FASE', 'full')
RENDER = FASE != 'assets'          # 'assets': solo textura, rig, clips y exportacion (sin renders); los previews no cambian
NOMBRE = 'AguilaLegendaria'
OUT = os.path.abspath(os.path.join(HERE, '..', 'mascotas-altas-v02', 'aguila-legendaria'))
PREV = os.path.join(OUT, 'previews')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

A.clean_scene()
bpy.context.scene.render.fps = 30
CM = A.collection('Mascota')
CR = A.collection('Ref')
CC = A.collection('Camaras')

PAL = {
    'cuerpo': '#5d3b23', 'cuerpo_osc': '#47291a', 'pecho': '#a77848', 'escama': '#d1a263', 'escama_osc': '#744c2b', 'vientre': '#dcc79d',
    'cabeza': '#f6f0e3', 'pico': '#f5b82e', 'pico_inf': '#d99a1c', 'cera': '#ffd54a', 'ojo': '#fffbe8', 'pupila': '#15100e',
    'ceja': '#6b4a26', 'oro': '#ffc42e', 'ala_a': '#553520', 'ala_b': '#74502e', 'ala_c': '#a47845', 'ala_c2': '#d3aa68',
    'ala_punta': '#ffd66e', 'cola': '#f6f0e3', 'cola_punta': '#553520', 'garra': '#f1b222', 'una': '#2a2024',
}
C = 0.2
V = Vox(C)
MBS = {b: A.MB('G_' + b) for b in BONES}


def reg_torso(p, n):
    if p.z > 2.42 and p.y > -0.50:
        return 'cabeza'                                              # gola blanca: la cabeza sigue por el pecho alto
    if p.y > -0.15 and abs(p.x) < 0.86 and 1.30 < p.z <= 2.42:
        return 'pecho'
    if p.y > -0.15 and abs(p.x) < 0.86 and p.z <= 1.30:
        return 'vientre'
    if p.z > 1.9 and p.y < 0.1:
        return 'cuerpo_osc'                                          # manto oscuro en la parte alta de la espalda
    return 'cuerpo'


def b(bone, c, size, mat):
    MBS[bone].box(c, size, mat)


# ---------------------------------------------------------------- cuerpo rechoncho, cabeza grande, muslos, tarsos, cresta (volumenes escalonados)
V.elipsoide((0, -0.15, 1.60), (1.00, 0.92, 1.05), 'Body', reg_torso, exp=2.8)
V.elipsoide((0, 0.55, 3.05), (0.98, 0.92, 0.86), 'Head', 'cabeza', exp=2.6)
for s in (-1, 1):
    V.elipsoide((s * 0.52, 0.02, 0.88), (0.42, 0.50, 0.50), 'Body', 'escama_osc', exp=2.4)           # muslos emplumados
    V.caja((s * 0.52, 0.18, 0.40), (0.30, 0.34, 0.52), 'Leg_R' if s > 0 else 'Leg_L', 'garra')        # tarso amarillo (hueso de la pata)
V.construir(MBS)
# mechon barrido hacia atras sobre la nuca (tres bloques girados), la punta dorada (rareza legendaria)
cubo_girado(MBS['Head'], (0, -0.10, 3.98), (0.44, 0.44, 0.62), 'cabeza', rot=(18, 0, 0))
cubo_girado(MBS['Head'], (0, -0.40, 4.08), (0.36, 0.38, 0.54), 'cabeza', rot=(36, 0, 0))
cubo_girado(MBS['Head'], (0, -0.66, 4.06), (0.28, 0.32, 0.38), 'oro', rot=(54, 0, 0))
# escamas de plumas en relieve sobre la piel escalonada (pecho, flancos, espalda y muslos), pegadas a las caras: nada flota
N_ESC = 0
N_ESC += escamas(V, MBS, 'Body', 'escama', (0, 1, 0), lambda p: 1.30 < p.z < 2.40 and abs(p.x) < 0.80, alto=0.09, patron=tresbolillo)
N_ESC += escamas(V, MBS, 'Body', 'escama_osc', (0, -1, 0), lambda p: 1.00 < p.z < 2.30 and abs(p.x) < 0.80, alto=0.09, patron=dispersas(0.5, 3))
for sx in (-1, 1):
    N_ESC += escamas(V, MBS, 'Body', 'escama_osc', (sx, 0, 0), lambda p: 1.15 <= p.z < 2.05 and p.y > -0.75, alto=0.09, patron=dispersas(0.5, 5 + sx))
    N_ESC += escamas(V, MBS, 'Body', 'escama', (sx, 0, 0), lambda p: 0.62 < p.z < 1.15 and p.y > -0.3, alto=0.08, patron=dispersas(0.5, 9 + sx))

# ---------------------------------------------------------------- cara: pico ancho con gancho, ojos diminutos negros con un brillo y ceja fiera
b('Head', (0, 1.50, 3.10), (0.74, 0.60, 0.50), 'pico')
b('Head', (0, 1.90, 2.99), (0.56, 0.34, 0.40), 'pico')
b('Head', (0, 2.08, 2.74), (0.36, 0.22, 0.34), 'pico')
b('Head', (0, 2.13, 2.52), (0.22, 0.14, 0.20), 'pico_inf')              # punta del gancho
b('Head', (0, 1.42, 2.70), (0.58, 0.62, 0.17), 'pico_inf')
b('Head', (0, 1.22, 3.40), (0.74, 0.18, 0.15), 'cera')
for s in (-1, 1):
    b('Head', (s * 0.60, 1.34, 3.22), (0.22, 0.15, 0.27), 'pupila')
    b('Head', (s * 0.56, 1.43, 3.29), (0.08, 0.04, 0.09), 'ojo')
    DY_PARPADO = parpado(MBS['Lid_R' if s > 0 else 'Lid_L'], (s * 0.60, 1.34, 3.22), (0.22, 0.15, 0.27), 1.45, 'cabeza', 'pupila')
    cubo_girado(MBS['Head'], (s * 0.58, 1.34, 3.50), (0.50, 0.16, 0.14), 'ceja', rot=(0, -s * 16, 0))
rombo(MBS['Body'], (0, 0.76, 1.95), 0.52, 0.11, 'oro', 'Y')               # medalla dorada en el pecho (rareza legendaria)

# ---------------------------------------------------------------- pies: tres dedos al frente con unas negras, dedo trasero
for s in (-1, 1):
    for k in (-1, 0, 1):
        b('Leg_R' if s > 0 else 'Leg_L', (s * 0.52 + k * 0.19, 0.42, 0.20), (0.15, 0.66, 0.15), 'garra')
        b('Leg_R' if s > 0 else 'Leg_L', (s * 0.52 + k * 0.19, 0.80, 0.17), (0.12, 0.16, 0.12), 'una')
    b('Leg_R' if s > 0 else 'Leg_L', (s * 0.52, -0.22, 0.20), (0.15, 0.34, 0.15), 'garra')
# patas que cuelgan al volar (Maikol): tarso y dedos giran desde la cadera, dentro del muslo; los dedos apuntan hacia abajo
PIVOTE_PATA = {lado: Vector((s * 0.52, 0.12, 0.68)) for s, lado in ((1, 'R'), (-1, 'L'))}
for s, lado in ((1, 'R'), (-1, 'L')):
    colgar_pata(MBS['Leg_' + lado], PIVOTE_PATA[lado], -48.0, s * 4.0)

# ---------------------------------------------------------------- alas: brazo, secundarias, primarias y cubiertas de plumas en abanico, en arco (dihedro)
S_HOMBRO = Vector((0.94, -0.20, 2.10))
A_BRAZO = 1.50
D1, SW1, D2, SW2 = 14.0, 8.0, 22.0, 14.0
MARCOS = {}
for s, lado in ((1, 'R'), (-1, 'L')):
    W_, T_ = 'Wing_' + lado, 'Tip_' + lado
    Sv = Vector((s * S_HOMBRO.x, S_HOMBRO.y, S_HOMBRO.z))
    M1, M2, H = marco_ala(Sv, s, A_BRAZO, D1, SW1, D2, SW2)
    MARCOS[lado] = (M1, M2, H, Sv)
    # brazo (hueso del ala) y hombrera
    caja_marco(MBS[W_], M1, (s * 0.62, 0.0, 0.0), (1.40, 0.52, 0.50), 'cuerpo_osc')
    caja_marco(MBS[W_], M1, (s * 1.45, 0.0, 0.0), (0.64, 0.46, 0.44), 'cuerpo_osc')
    # secundarias (seis), detras del brazo
    for i in range(6):
        L = 1.12 + 0.07 * i
        pluma(MBS[W_], M1, (s * (0.22 + 0.24 * i), -0.30), dir_ala(s, 84 - 2 * i), L, 0.54, 0.20, 0.05 * i,
              [(0.56, 'ala_a'), (0.84, 'ala_b'), (1.0, 'ala_c2')])
    # cubiertas (capas de arriba, mas claras) desde el borde de ataque: el brazo queda tapado de plumas
    for i in range(5):
        pluma(MBS[W_], M1, (s * (0.22 + 0.28 * i), 0.24), dir_ala(s, 82 - 3 * i), 1.10 - 0.07 * i, 0.50, 0.16, 0.27 + 0.035 * i,
              [(0.58, 'ala_c'), (1.0, 'ala_c2')])
    for i in range(4):
        pluma(MBS[W_], M1, (s * (0.34 + 0.30 * i), 0.30), dir_ala(s, 80 - 3 * i), 0.62 - 0.04 * i, 0.44, 0.14, 0.46 + 0.035 * i,
              [(1.0, 'ala_c2')])
    # mano: siete primarias en abanico desde la muneca
    for i in range(7):
        th = 4.0 + 9.6 * i
        pluma(MBS[T_], M2, (s * 0.04 * i, -0.06 * i), dir_ala(s, th), 2.20 - 0.15 * i, 0.50, 0.20, 0.05 * i,
              [(0.52, 'ala_a'), (0.80, 'ala_b'), (1.0, 'ala_punta')])
    for i in range(3):
        pluma(MBS[T_], M2, (s * 0.02, 0.22 - 0.04 * i), dir_ala(s, 14 + 20 * i), 1.0 - 0.12 * i, 0.46, 0.14, 0.27 + 0.04 * i,
              [(0.6, 'ala_c'), (1.0, 'ala_c2')])
    caja_marco(MBS[T_], M2, (s * 0.10, 0.0, 0.0), (0.46, 0.50, 0.46), 'cuerpo_osc')                # muneca
    rombo(MBS[W_], (s * 1.25, 0.12, 0.29), 0.36, 0.10, 'oro', 'Z', 45.0, M=M1)                      # rombo dorado sobre el brazo

# ---------------------------------------------------------------- cola: abanico de cinco plumas blancas con la punta oscura, unido a la grupa
M_COLA = tr((0, -0.98, 1.02)) @ rx(-16)                       # cola levantada: de 3/4 no se ve como una tabla suelta y de lado se lee como abanico
caja_marco(MBS['Tail'], M_COLA, (0, 0.06, 0.0), (0.92, 0.56, 0.46), 'cuerpo_osc')
for k in range(5):
    Mk = M_COLA @ rx((0, 6, 12)[abs(k - 2)])                    # las plumas de fuera caen mas: la cola sale en copa y se ve gruesa de lado
    pluma(MBS['Tail'], Mk, ((k - 2) * 0.12, 0.0), -90 + (k - 2) * 19, 1.80 - 0.26 * abs(k - 2), 0.62, 0.26, 0.06 * k,
          [(0.78, 'cola'), (1.0, 'cola_punta')])

# ---------------------------------------------------------------- rig (los ocho huesos de las mascotas de Codex) y malla unica
HUESOS = [('Root', (0, 0, 1.0), None, 0.5), ('Body', (0, -0.15, 1.60), 'Root', 0.6), ('Head', (0, 0.15, 2.60), 'Body', 0.6),
          ('Tail', (0, -0.98, 1.02), 'Body', 0.6)]
for lado in ('R', 'L'):
    M1, M2, H, Sv = MARCOS[lado]
    HUESOS.append(('Wing_' + lado, tuple(Sv), 'Body', 0.6))
    HUESOS.append(('Tip_' + lado, tuple(H), 'Wing_' + lado, 0.6))
for s, lado in ((1, 'R'), (-1, 'L')):
    HUESOS.append(('Leg_' + lado, tuple(PIVOTE_PATA[lado]), 'Body', 0.4))
    HUESOS.append(('Lid_' + lado, (s * 0.60, 1.34, 3.22), 'Head', 0.3))
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

E = Escena(CR, CC, PREV, FASE, radio=11.5, maniqui=(-6.0, 0.4), regla=(6.6, 0.4), objetivo=(-0.6, -0.3, 2.2))
shot = E.foto

if FASE == 'geo':
    planos(ob, PAL)
    pose()
    shot('_geo_frente', 180, 8, 23.0, scale=True)
    shot('_geo_34', 148, 16, 21.0)
    shot('_geo_lado', 90, 8, 21.0)
    shot('_geo_cara', 160, 10, 9.5, target=(0, 0.6, 3.0))
    shot('_geo_espalda', 0, 12, 21.0)
    shot('_geo_arriba', 180, 82, 23.0)
    acts, CLIPS = clips_pet(rig)
    for nom, t in (('a', 0.0), ('d', 0.60), ('f', 0.90)):
        en(rig, acts, 'Fly', t)
        shot('_geo_fly_' + nom, 180, 10, 21.0)
    A.log('fase geo lista')
    sys.exit(0)

# ---------------------------------------------------------------- textura pintada (sombras frias lavanda, mas variacion por cara)
Pn = hornear(ob, 5.0)
E.reiniciar_render()
BASE = dict(var=0.05, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.06, ao=0.55, ao_tint='#2b2455', light=0.26,
            hue_var=0.02, blotch=0.045, edge=0.7, edge_th=0.05, edge_break=0.3)


def reg(name, **kw):
    if name not in A.REGIONS:               # region sin caras en este modelo
        return None
    k = dict(BASE)
    k.update(kw)
    if 'edge_col' not in k:
        k['edge_col'] = claro(PAL[name])
    return Pn.region(name, PAL[name], **k)


reg('cuerpo', extra=chevrones('#3d2616', 0.34, 0.14), seed=1)
reg('cuerpo_osc', seed=2)
reg('pecho', extra=chevrones('#8f6a3a', 0.30, 0.20), seed=3)
reg('escama', edge_col='#f1d79a', seed=4)
reg('escama_osc', edge_col='#a77a4c', seed=5)
reg('vientre', extra=chevrones('#b99f78', 0.28, 0.16), seed=6)
reg('cabeza', ao_tint='#7f8bb0', var=0.03, seed=7, extra=chevrones('#c9c6c0', 0.28, 0.12))
reg('pico', edge_col='#fff0a0', var=0.03, seed=8)
reg('pico_inf', edge_col='#f1c860', var=0.03, seed=9)
reg('cera', edge_col='#fff3b8', var=0.02, seed=10)
reg('ojo', edge_col='#ffffff', var=0.0, ao=0.1, light=0.0, face_var=0.0, seed=11)
reg('pupila', edge=0.0, var=0.0, ao=0.1, face_var=0.0, seed=12)
reg('ceja', seed=13)
reg('oro', edge_col='#fff0a0', var=0.03, ao=0.25, light=0.12, grad=0.4, seed=14)
WING = dict(stroke=(6.0, 1.0, 1.0), stroke_scale=3.0, var=0.06, blotch=0.05)
reg('ala_a', edge_col='#8a6240', seed=21, **WING)
reg('ala_b', edge_col='#a77a4c', seed=22, **WING)
reg('ala_c', edge_col='#c9a06a', seed=23, **WING)
reg('ala_c2', edge_col='#f1d79a', seed=24, **WING)
reg('ala_punta', edge_col='#fff0c8', ao=0.25, light=0.10, seed=25, **WING)
reg('cola', ao_tint='#7f8bb0', var=0.03, seed=26, stroke=(1.0, 6.0, 1.0), stroke_scale=3.0)
reg('cola_punta', edge_col='#8a6240', seed=27, stroke=(1.0, 6.0, 1.0), stroke_scale=3.0)
reg('garra', edge_col='#fff0a0', seed=28)
reg('una', edge_col='#6a5a60', var=0.02, seed=29)
guardar_textura(Pn, ob, OUT, NOMBRE)

# ---------------------------------------------------------------- clips y renders
acts, CLIPS = clips_pet(rig)
if RENDER:
    shots = []
    rig.animation_data_clear()
    pose()
    shots.append((shot('Aguila-legendaria-frente', 180, 8, 23.0, scale=True), 'FRENTE (REGLA 6 STUDS)'))
    shots.append((shot('Aguila-legendaria-tres-cuartos', 148, 16, 21.0), '3/4'))
    shots.append((shot('Aguila-legendaria-lateral', 90, 8, 21.0), 'LATERAL'))
    shots.append((shot('Aguila-legendaria-espalda', 0, 12, 21.0), 'ESPALDA'))
    shots.append((shot('Aguila-legendaria-arriba', 180, 82, 23.0), 'DESDE ARRIBA'))
    shots.append((shot('Aguila-legendaria-cara', 160, 10, 9.5, target=(0, 0.6, 3.0)), 'CARA'))
    pose(lid=1.0)
    shots.append((shot('Aguila-legendaria-cara-parpadeo', 160, 10, 9.5, target=(0, 0.6, 3.0)), 'PARPADEO (CLIP BLINK)'))
    pose()
    en(rig, acts, 'Fly', 0.0)
    shots.append((shot('Aguila-legendaria-aleteo-alto', 150, 10, 21.0), 'ALETEO ARRIBA (EXTENDIDA)'))
    en(rig, acts, 'Fly', 0.46)
    shots.append((shot('Aguila-legendaria-aleteo-bajo', 150, 10, 21.0), 'ALETEO ABAJO'))
    en(rig, acts, 'Fly', 0.70)
    shots.append((shot('Aguila-legendaria-aleteo-recogida', 150, 10, 21.0), 'ALETEO RECOGIENDO'))
    en(rig, acts, 'Glide', 0.5)
    shots.append((shot('Aguila-legendaria-planeo', 150, 10, 21.0), 'PLANEO'))
    en(rig, acts, 'Celebrate', 0.8)
    shots.append((shot('Aguila-legendaria-celebrar', 160, 10, 21.0), 'CELEBRAR'))
    W.contact_sheet(shots, 3, os.path.join(PREV, '_hoja.png'), title='AGUILA LEGENDARIA V02 - RENDERS DE BLENDER')
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, 'Aguila-legendaria-hoja.jpg'), 0.5)

    # secuencia del aleteo (recoger -> extender -> impulsar -> recoger), render ligero
    A.setup_render((700, 560), 'CYCLES', 24)
    E.formato()
    seq = []
    for nom, t, etq in (('a', 0.0, 'ARRIBA EXTENDIDA'), ('b', 0.28, 'IMPULSO'), ('c', 0.46, 'ABAJO'), ('d', 0.60, 'RECOGE'), ('e', 0.78, 'RECOGIDA'), ('f', 0.90, 'EXTIENDE')):
        en(rig, acts, 'Fly', t)
        seq.append((shot('_seq_' + nom, 150, 10, 21.0), etq))
    W.contact_sheet(seq, 3, os.path.join(PREV, '_seq.png'), title='AGUILA LEGENDARIA - ALETEO (1 S, 6 POSES)')
    a_jpg(os.path.join(PREV, '_seq.png'), os.path.join(PREV, 'Aguila-legendaria-aleteo-secuencia.jpg'), 0.6)
    for nom in 'abcdef':
        try:
            os.remove(os.path.join(PREV, '_seq_%s.jpg' % nom))
        except OSError:
            pass
    E.reiniciar_render()

exportar_pet(OUT, NOMBRE, ob, rig, acts, CLIPS, pose, {
    'pieza': 'Aguila legendaria v02 (mascota voladora alta)', 'triangulos': TRIS, 'limites_studs': BOUNDS,
    'huesos': [h[0] for h in HUESOS], 'rejilla_voxel_studs': C, 'paleta': PAL, 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPLANARES, 'escamas': N_ESC})
A.log('listo')
