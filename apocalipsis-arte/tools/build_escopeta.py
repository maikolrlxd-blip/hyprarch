# Escopeta de corredera (generica, sin marcas) para el juego "apocalipsis".
# blender -b --factory-startup -P build_escopeta.py        (QUICK=1 salta las hojas de contacto)
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import importlib
import ap_lib as A
import ap_armas as W
importlib.reload(A); importlib.reload(W)
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler

NOMBRE = 'Escopeta'
QUICK = os.environ.get('QUICK') == '1'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'armas', 'escopeta')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

LARGO = 4.0                    # studs, de la culata a la boca (estilizada, legible en un R15)
s = LARGO / 990.0
GY, GZ = 300.0, -15.0          # centro de la garganta de la culata (agarre, origen) en mm del dibujo; eje del canon en z = 9
XS = 1.3                       # engrosado en X (estilo Roblox: que no sea un palillo en la mano R15)
P_BACK = 90.0 * s              # recorrido de la bomba


def yz(y, z):
    return ((y - GY) * s, (z - GZ) * s)


def xz(x, z):
    return (x * s, (z - GZ) * s)


def P3(x, y, z):
    return Vector((x * s, (y - GY) * s, (z - GZ) * s))


def Y(y):
    return (y - GY) * s


A.clean_scene()
A.REGIONS.clear()
CM = A.collection('Arma_Mundo')

# ------------------------------------------------------------------ CUERPO (culata, cajon, canon, tubo, guardamonte)
mb = A.MB('Cuerpo')
stock = [(0, 30), (200, 18), (338, 24), (338, -40), (285, -32), (170, -62), (40, -100), (0, -112)]
mb.prism([yz(*p) for p in stock], -16 * s, 16 * s, 'madera', plane='YZ', bevel=1.6 * s)
mb.prism([yz(*p) for p in [(-14, 28), (0, 30), (0, -112), (-14, -108)]], -16.5 * s, 16.5 * s, 'goma', plane='YZ', bevel=1.2 * s)
# cajon de mecanismos: bloque principal (x -21..12) + pared derecha en 4 piezas alrededor de la ventana de expulsion
rec = [(330, -48), (560, -48), (560, 22), (552, 30), (338, 30), (330, 22)]
mb.prism([yz(*p) for p in rec], -21 * s, 12 * s, 'metal', plane='YZ')
mb.box(P3(16.5, 362.5, -9), (9 * s, 65 * s, 78 * s), 'metal')
mb.box(P3(16.5, 522.5, -9), (9 * s, 75 * s, 78 * s), 'metal')
mb.box(P3(16.5, 440, -26), (9 * s, 90 * s, 44 * s), 'metal')
mb.box(P3(16.5, 440, 26), (9 * s, 90 * s, 8 * s), 'metal')
mb.box(P3(0, 352, -30), (46 * s, 7 * s, 7 * s), 'metal')                          # boton de seguro
# canon con costilla, mira de bolita y tubo cargador
mb.cyl(P3(0, 548, 9), P3(0, 990, 9), 11.5 * s, 8, 'canon', inset_cap1=6.5 * s, inset_depth=9 * s, inset_mat='interior')
mb.box(P3(0, 765, 23.0), (9 * s, 450 * s, 5 * s), 'canon')
mb.box(P3(0, 975, 28.5), (5 * s, 7 * s, 8 * s), 'mira')
mb.cyl(P3(0, 548, -14), P3(0, 905, -14), 10.2 * s, 8, 'canon', cap0=False)
mb.cyl(P3(0, 905, -14), P3(0, 926, -14), 13.2 * s, 8, 'canon')
mb.box(P3(0, 884, -3), (30 * s, 18 * s, 50 * s), 'canon')
# guardamonte
guard = [(338, -48), (338, -84), (347, -95), (420, -95), (430, -84), (432, -48)]
mb.band([yz(*p) for p in guard], 6.5 * s, -5 * s, 5 * s, 'metal', plane='YZ')         # v2b: guardamonte mas fino
cuerpo = mb.finish(CM, origin=(0, 0, 0))

# ------------------------------------------------------------------ BOMBA (guardamano de madera, se desliza)
mb = A.MB('Bomba')
sec = lambda k: [(x * k, GZ0 + (z - GZ0) * k) for (x, z) in
                 [(-22, -42), (22, -42), (27, -22), (22, -6), (-22, -6), (-27, -22)]]
GZ0 = -24
sections = [[xz(*p) for p in sec(0.86)], [xz(*p) for p in sec(1.0)], [xz(*p) for p in sec(1.0)], [xz(*p) for p in sec(0.9)]]
mb.loft(sections, [Y(595), Y(606), Y(780), Y(792)], 'madera', plane='XZ', bevel=1.0 * s)
bomba = mb.finish(CM, origin=P3(0, 693, -24))

# ------------------------------------------------------------------ CERROJO (visible por la ventana de expulsion)
mb = A.MB('Cerrojo')
mb.box(P3(9.5, 437, 9), (7 * s, 66 * s, 18 * s), 'cerrojo')          # asoma 1 mm por la ventana (x 12-13)
cerrojo = mb.finish(CM, origin=P3(9.5, 437, 9))

# ------------------------------------------------------------------ GATILLO
mb = A.MB('Gatillo')
trig = [(378, -50), (373, -66), (366, -84)]
mb.band([yz(*p) for p in trig], 5.5 * s, -2.8 * s, 2.8 * s, 'gatillo', plane='YZ')    # v2b: gatillo mas fino
gatillo = mb.finish(CM, origin=P3(0, 378, -50))

# ------------------------------------------------------------------ CARTUCHO (nuevo) y CASQUILLO (gastado): calibre 12, 70 mm
SH = [(10.3, 0.0), (10.3, 0.17), (9.8, 0.19), (9.8, 1.0)]
def shell(name, y0, z0, gast):
    mb = A.MB(name)
    mats = ['laton', 'laton', 'cartucho'] if not gast else ['laton', 'laton', 'casq']
    mb.lathe(P3(0, y0, z0), P3(0, y0 + 70, z0), [(r * s, t) for r, t in SH], 6, 'cartucho', mats=mats)
    return mb.finish(CM, origin=P3(0, y0 + 35, z0))
cartucho = shell('Cartucho', 405.0, -24.0, False)
casquillo = shell('Casquillo', 412.0, -33.0, True)

partes = [cuerpo, bomba, cerrojo, gatillo, cartucho, casquillo]
for o in partes:                    # engrosar en X respecto al origen del arma (no al de cada pieza)
    o.data.transform(Matrix.Scale(XS, 4, (1, 0, 0)))
    o.location.x *= XS
TRIS = {o.name: A.tris([o]) for o in partes}
A.log('triangulos', TRIS, 'total', sum(TRIS.values()))

# ------------------------------------------------------------------ UV + horneado + pintura
ref = bpy.data.objects.new('RefPos', None)
CM.objects.link(ref)
A.uv_unwrap(partes, angle=50, margin=0.004,
            weights={'Cuerpo': 1.0, 'Bomba': 1.25, 'Cerrojo': 0.8, 'Gatillo': 0.7, 'Cartucho': 0.8, 'Casquillo': 0.8})
R = 3.4
maps = A.bake_maps(partes, 2048, R=R, ao_dist=0.16, bevel_r=0.014, samples=20, pos_ref=ref,
                   explode={bomba: (0, 0, -3.0), cerrojo: (0, 0, 3.0), gatillo: (0, 0, -6.0),
                            cartucho: (0, 0, -6.0), casquillo: (0, 0, -9.0)})
P = A.Paint(maps, R=R, light=(-0.30, 0.25, 0.92))
mm = lambda v: v / s


def wood(P, msk, pos, nrm, col):
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    x = mm(pos[:, 0])
    # veta: lineas largas a lo largo de y, onduladas
    wob = A.fbm(np.stack([y * 0.012, z * 0.05, x * 0.05], 1), 2, 61) * 6.0
    g = np.sin((z * 0.55 + x * 0.55 + wob) * 1.6)
    d = (g > 0.78) * 0.24 + (g < -0.88) * 0.12
    col = col * (1 - d[:, None]) + col * 0.52 * d[:, None]
    # lustre claro en caras superiores y desgaste oscuro de aceite cerca de la empunadura
    oil = np.exp(-(((y - 300) / 55.0) ** 2 + ((z + 95) / 70.0) ** 2)) * (np.abs(nrm[:, 0]) > 0.7)
    col = col * (1 - 0.30 * oil[:, None]) + np.array([0.22, 0.12, 0.06], np.float32) * 0.30 * oil[:, None]
    # tablero de agarre rayado en la empunadura y el guardamano
    grip = (np.abs(nrm[:, 0]) > 0.7) & (y > 258) & (y < 330) & (z < -62) & (z > -128)
    chk = (((y * 0.55) % 1.0) < 0.5) ^ (((z * 0.55 + y * 0.2) % 1.0) < 0.5)
    col[grip & chk] = col[grip & chk] * 0.78
    return col


def pump_grooves(P, msk, pos, nrm, col):
    y = mm(pos[:, 1]) + GY
    ring = np.zeros(y.shape, bool)
    for y0 in (640, 668, 696, 724, 752):
        ring |= np.abs(y - y0) < 3.4
    col[ring] = col[ring] * 0.55
    col = wood(P, msk, pos, nrm, col)
    return col


def receiver(P, msk, pos, nrm, col):
    x = mm(pos[:, 0]) / XS
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    side = np.abs(nrm[:, 0]) > 0.8
    # fondo de la ventana de expulsion (cara del bloque en x = 12 mm): interior oscuro con un poco de luz arriba
    win = (nrm[:, 0] > 0.8) & (np.abs(x - 12.0) < 1.5) & (y > 393) & (y < 487) & (z > -6) & (z < 24)
    col[win] = np.array([0.05, 0.05, 0.055], np.float32) * (1.0 + 1.5 * np.clip((z[win] + 4) / 26.0, 0, 1))[:, None]
    # rayones largos y panel de la ventana
    sp = np.stack([pos[:, 0] * 25.0, pos[:, 1] * 2.2, pos[:, 2] * 30.0], 1)
    sc = side & (A.vnoise(sp, 71) > 0.86)
    col[sc] = np.clip(col[sc] * 1.22 + 0.02, 0, 1)
    col[side & (A.vnoise(sp * 1.8 + 5.0, 73) < 0.10)] *= 0.62
    # puerto de carga inferior (oscuro) y marcas
    port = (nrm[:, 2] < -0.8) & (y > 438) & (y < 522) & (np.abs(x) < 14)
    col[port] = np.array([0.04, 0.04, 0.045], np.float32)
    # lineas de union del cajon
    j = side & (np.abs(y - 395) < 0.9) & (z < 30)
    col[j] = col[j] * 0.5
    # ranuras de agarre tipo rejilla en la tapa
    top = (nrm[:, 2] > 0.8) & (y > 345) & (y < 395)
    col[top & (((y - 345) % 7.0) < 2.2)] *= 0.55
    return col


def shell_paint(P, msk, pos, nrm, col):
    y = mm(pos[:, 1]) + GY
    # raya clara del cuerpo del cartucho (etiqueta) y marca del casquillo
    stripe = (np.abs((y - 405.0) - 38.0) < 2.2) | (np.abs((y - 412.0) - 38.0) < 2.2)
    col[stripe & (nrm[:, 2] > -2)] = col[stripe] * 0.55 + np.array([0.9, 0.85, 0.7], np.float32) * 0.45
    return col


P.region('madera', '#755339', var=0.12, stroke=(10, 1, 1), stroke_scale=6, blotch=0.10, ao=0.62, ao_tint='#1d1008', light=0.26,
         tone_steps=5, grad=0.10, edge_col='#a98a6a', edge=0.9, edge_th=0.035, edge_break=0.45, grime=0.25, grime_col='#2a190c',
         dust=0.10, seed=3, extra=wood)
P.regions_alias = None
P.region('metal', '#555b62', var=0.09, stroke=(1, 5, 1), stroke_scale=7, blotch=0.08, ao=0.62, ao_tint='#171d28', light=0.26, grad=0.14,
         edge_col='#cfd5da', edge=1.0, edge_th=0.035, edge_break=0.40, grime=0.22, rust=0.16, dust=0.14, seed=5, extra=receiver)
P.region('canon', '#3a3f45', var=0.08, stroke=(1, 8, 1), stroke_scale=7, ao=0.55, ao_tint='#10151b', light=0.3, grad=0.12,
         edge_col='#aab2b9', edge=1.0, edge_th=0.035, grime=0.22, rust=0.10, dust=0.10, seed=7)
P.region('goma', '#2a2723', var=0.06, stroke=(1, 1, 1), stroke_scale=14, ao=0.5, edge_col='#5c564e', edge=0.8, seed=9)
P.region('interior', '#0d0d0f', var=0.04, ao=0.3, seed=11)
P.region('mira', '#e1dcc7', var=0.05, ao=0.4, edge_col='#ffffff', edge=0.6, seed=13)
P.region('cerrojo', '#989fa6', var=0.08, stroke=(1, 4, 1), stroke_scale=9, ao=0.55, edge_col='#e6eaed', edge=0.9, grime=0.2, seed=15)
P.region('gatillo', '#40403f', var=0.04, ao=0.4, edge_col='#8e8e8e', edge=0.9, seed=17)
P.region('laton', '#cba14a', var=0.08, stroke=(1, 3, 1), stroke_scale=14, ao=0.3, light=0.3, edge_col='#f3d994', edge=0.9, seed=19)
P.region('cartucho', '#b8392c', var=0.08, stroke=(1, 4, 1), stroke_scale=10, ao=0.45, edge_col='#e08a6a', edge=0.8, grime=0.15,
         seed=21, extra=shell_paint)
P.region('casq', '#9d3328', var=0.10, stroke=(1, 4, 1), stroke_scale=10, ao=0.5, edge_col='#c46a4c', edge=0.8, grime=0.50,
         grime_col='#1a1612', seed=23, extra=shell_paint)
TEX = os.path.join(OUT, 'texturas', NOMBRE + '_Color.png')
P.save(TEX, 1024)
mat = A.final_material('M_' + NOMBRE, TEX)
A.assign_final(partes, mat)
bpy.data.objects.remove(ref, do_unlink=True)

# ------------------------------------------------------------------ RIG de mundo (tercera persona)
MOV = ['Bomba', 'Cerrojo', 'Gatillo', 'Cartucho', 'Casquillo']
piv = {o.name: o.location.copy() for o in (bomba, cerrojo, gatillo, cartucho, casquillo)}
bones_w = [('Arma', (0, 0, 0), None, 0.3)] + [(k, tuple(piv[k]), 'Arma', 0.12) for k in MOV]
rig_w = A.make_armature(NOMBRE, bones_w, CM)
A.skin_rigid(cuerpo, rig_w, 'Arma')
for o in (bomba, cerrojo, gatillo, cartucho, casquillo):
    A.skin_rigid(o, rig_w, o.name)
BW = [b[0] for b in bones_w]

# ------------------------------------------------------------------ VIEWMODEL (primera persona)
CV = A.collection('Arma_VM')
G = Vector((0.32, 0.70, -0.58))          # v2c: mas cerca y mas alta (en v2 se veia pequena y lejana)
SRa, SLa = Vector((0.90, -0.70, -1.05)), Vector((-0.85, 0.20, -1.05))      # hombros (absolutos, fuera de cuadro)
HR = Vector((0.03, 0.00, 0.00))
WR = Vector((0.05, -0.22, -0.10))
HL = Vector((-0.06, 1.59, -0.17))                                            # mano izquierda bajo la bomba
WL = Vector((-0.26, 1.29, -0.31))
POUCH = Vector((-0.45, 0.45, -0.75))                                          # donde la mano coge cartuchos (fuera de cuadro)


def elbow(S, Wr, L1, L2, pole):
    d = Wr - S
    dist = min(d.length, L1 + L2 - 0.01)
    dv = d.normalized()
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(L1 * L1 - a * a, 0))
    pp = Vector(pole) - dv * Vector(pole).dot(dv)
    pp.normalize()
    return S + dv * a + pp * h


SR, SL = SRa - G, SLa - G
ER = elbow(SR, WR, 1.30, 1.20, (1, 0, -1))
EL = elbow(SL, WL, 1.30, 1.20, (-1, -0.3, -1))
J = {'R': dict(S=SR, E=ER, W=WR, H=HR, Hs=(0.36, 0.46, 0.33), Hr=(-8, 0, 0)),
     'L': dict(S=SL, E=EL, W=WL, H=HL, Hs=(0.31, 0.44, 0.28), Hr=(0, 0, 0))}
arms = W.build_vm_arms(CV, G, J)
W.paint_arms(arms, os.path.join(OUT, 'texturas', 'BrazosVM_Color.png'))
vm_parts = {}
for o in partes:
    o2 = o.copy()
    o2.data = o.data.copy()
    for m in list(o2.modifiers):
        o2.modifiers.remove(m)
    o2.parent = None
    o2.location = o.location + G
    o2.name = o.name + '_VM'
    CV.objects.link(o2)
    vm_parts[o.name] = o2
bones_v = [('Camara', (0, 0, 0), None, 0.2), ('Arma', tuple(G), 'Camara', 0.3)]
bones_v += [(k, tuple(piv[k] + G), 'Arma', 0.12) for k in MOV]
for pre, side in (('Right', 'R'), ('Left', 'L')):
    j = J[side]
    bones_v += [(pre + 'UpperArm', tuple(j['S'] + G), 'Arma', 0.15), (pre + 'LowerArm', tuple(j['E'] + G), pre + 'UpperArm', 0.15),
                (pre + 'Hand', tuple(j['W'] + G), pre + 'LowerArm', 0.12)]
rig_v = A.make_armature(NOMBRE + '_VM', bones_v, CV)
for k, o in vm_parts.items():
    A.skin_rigid(o, rig_v, 'Arma' if k == 'Cuerpo' else k)
for n, o in arms.items():
    A.skin_rigid(o, rig_v, n)
BV = [b[0] for b in bones_v]

# ------------------------------------------------------------------ CLIPS
POLE_L = (-1, -0.3, -1)
POLE_R = (1, 0, -1)
CERROJO_BACK = 75.0 * s
ESC = {}


def pump_pull(c, t0, dur_back, hold, dur_fwd, hand=True, wl=None):
    """Mueve bomba y cerrojo atras y adelante; la mano izquierda acompana a la bomba."""
    t1, t2, t3 = t0 + dur_back, t0 + dur_back + hold, t0 + dur_back + hold + dur_fwd
    c.e(t1, 'bomba_atras').e(t3, 'bomba_adelante')
    c.p('Bomba', t0).p('Bomba', t1, (0, -P_BACK, 0)).p('Bomba', t2, (0, -P_BACK, 0)).p('Bomba', t3)
    c.p('Cerrojo', t0).p('Cerrojo', t1, (0, -CERROJO_BACK, 0)).p('Cerrojo', t2, (0, -CERROJO_BACK, 0)).p('Cerrojo', t3)
    if hand:
        w0 = wl or WL
        c.hand('L', t0, w0, J, POLE_L).hand('L', t1, w0 + Vector((0, -P_BACK, 0)), J, POLE_L) \
         .hand('L', t2, w0 + Vector((0, -P_BACK, 0)), J, POLE_L).hand('L', t3, w0, J, POLE_L)
    return t1, t2, t3


def casing_eject(c, t0):
    """Casquillo gastado sale por la ventana derecha. En reposo esta oculto dentro del cajon (no se anima escala en Roblox)."""
    c.e(t0 + 0.04, 'casquillo_sale')
    c.p('Casquillo', t0).p('Casquillo', t0 + 0.04, (0, -4 * s, 30 * s), ip='LINEAR') \
     .p('Casquillo', t0 + 0.08, (30 * s, -8 * s, 62 * s), (0, 0, -40), ip='LINEAR') \
     .p('Casquillo', t0 + 0.17, (150 * s, -40 * s, 112 * s), (90, 30, -120), ip='LINEAR') \
     .p('Casquillo', t0 + 0.30, (420 * s, -130 * s, 130 * s), (260, 60, -250), ip='LINEAR') \
     .p('Casquillo', t0 + 0.40, (700 * s, -200 * s, -150 * s), (420, 80, -380), ip='CONSTANT') \
     .p('Casquillo', t0 + 0.46)


def seg_inicio(c, t0):
    c.v('Arma', t0).v('Arma', t0 + 0.20, (-0.10, 0.02, 0.10), (6, 8, 22), ip='BEZIER').v('Arma', t0 + 0.45, (-0.10, 0.02, 0.10), (6, 8, 22))
    c.hand('L', t0, WL, J, POLE_L).hand('L', t0 + 0.12, WL + Vector((-0.05, -0.15, -0.30)), J, POLE_L) \
     .hand('L', t0 + 0.30, POUCH, J, POLE_L).hand('L', t0 + 0.45, POUCH, J, POLE_L)


PORT = P3(0, 480, -40)            # boca del puerto de carga (abajo del cajon)
SHELL_REST = Vector((0, 0, 0))


def seg_cartucho(c, t0, first=False):
    """Un cartucho: sale de la bolsa (mano izquierda), sube al puerto y entra. dura 0.50 s."""
    pouch = POUCH
    hand_off = Vector((0.0, 0.10, -0.05))                       # la muneca esta un poco mas atras y abajo del cartucho
    sh0 = pouch + Vector((0.10, 0.20, 0.05))                    # cartucho en la mano
    sh1 = PORT + Vector((-0.02, -0.02, -0.18))                  # frente al puerto
    sh2 = PORT + Vector((0.0, 0.0, 0.04))                       # dentro
    rest_c = Vector(piv['Cartucho'])
    rel = lambda p: tuple(p - rest_c)
    c.e(t0 + 0.34, 'cartucho_dentro')
    c.p('Cartucho', t0).p('Cartucho', t0 + 0.02, rel(sh0), ip='LINEAR') \
     .p('Cartucho', t0 + 0.26, rel(sh1), (-8, 0, 0), ip='LINEAR').p('Cartucho', t0 + 0.34, rel(sh2), ip='LINEAR') \
     .p('Cartucho', t0 + 0.38, (0, 0, 0), ip='CONSTANT').p('Cartucho', t0 + 0.50)
    c.hand('L', t0, pouch, J, POLE_L).hand('L', t0 + 0.26, sh1 + hand_off, J, POLE_L).hand('L', t0 + 0.34, sh2 + hand_off, J, POLE_L) \
     .hand('L', t0 + 0.42, sh1 + hand_off + Vector((0, 0, -0.15)), J, POLE_L).hand('L', t0 + 0.50, pouch, J, POLE_L)
    c.v('Arma', t0, (-0.10, 0.02, 0.10), (6, 8, 22)).v('Arma', t0 + 0.30, (-0.10, 0.02, 0.10), (6, 8, 22)) \
     .v('Arma', t0 + 0.34, (-0.10, 0.02, 0.095), (5.5, 8, 22)).v('Arma', t0 + 0.50, (-0.10, 0.02, 0.10), (6, 8, 22))


def seg_fin(c, t0):
    c.v('Arma', t0, (-0.10, 0.02, 0.10), (6, 8, 22)).v('Arma', t0 + 0.20, (0, 0, 0), (0, 0, 0)).v('Arma', t0 + 0.55)
    c.hand('L', t0, POUCH, J, POLE_L).hand('L', t0 + 0.18, WL, J, POLE_L)
    c.e(t0 + 0.28, 'bomba_atras').e(t0 + 0.46, 'bomba_adelante')
    c.p('Bomba', t0 + 0.18).p('Bomba', t0 + 0.28, (0, -P_BACK, 0)).p('Bomba', t0 + 0.34, (0, -P_BACK, 0)).p('Bomba', t0 + 0.46).p('Bomba', t0 + 0.55)
    c.p('Cerrojo', t0 + 0.18).p('Cerrojo', t0 + 0.28, (0, -CERROJO_BACK, 0)).p('Cerrojo', t0 + 0.34, (0, -CERROJO_BACK, 0)).p('Cerrojo', t0 + 0.46).p('Cerrojo', t0 + 0.55)
    c.hand('L', t0 + 0.28, WL + Vector((0, -P_BACK, 0)), J, POLE_L).hand('L', t0 + 0.34, WL + Vector((0, -P_BACK, 0)), J, POLE_L) \
     .hand('L', t0 + 0.46, WL, J, POLE_L).hand('L', t0 + 0.55, WL, J, POLE_L)


clips = []
c = W.ClipDef('Equipar', 0.90)
c.v('Arma', 0.0, (0.40, -0.30, -0.95), (-52, 22, -12)).v('Arma', 0.34, (0.02, -0.03, -0.03), (4, -3, 2)).v('Arma', 0.46, (0, 0, 0), (0, 0, 0)) \
 .v('Arma', 0.90)
c.hand('L', 0.0, WL + Vector((-0.1, -0.1, -0.5)), J, POLE_L).hand('L', 0.34, WL, J, POLE_L)
pump_pull(c, 0.48, 0.10, 0.05, 0.14)
clips.append(c)

c = W.ClipDef('Disparo', 0.45)
c.e(0.0, 'disparo')
c.v('Arma', 0.0).v('Arma', 0.03, (0.0, -0.27, 0.035), (11.5, 0.8, -1.0)).v('Arma', 0.12, (0.0, -0.10, 0.015), (4.5, 0.3, -0.4)) \
 .v('Arma', 0.28, (0, -0.02, 0.0), (1.0, 0, 0)).v('Arma', 0.45)
c.p('Gatillo', 0.0).p('Gatillo', 0.02, rot=(-16, 0, 0), ip='LINEAR').p('Gatillo', 0.12, rot=(-16, 0, 0)).p('Gatillo', 0.24)
c.p('Bomba', 0.0).p('Bomba', 0.03, (0, -0.03, 0), ip='LINEAR').p('Bomba', 0.14).p('Bomba', 0.45)
c.hand('L', 0.0, WL, J, POLE_L).hand('L', 0.45, WL, J, POLE_L)
clips.append(c)

c = W.ClipDef('Bombear', 0.60)
t1, t2, t3 = pump_pull(c, 0.04, 0.12, 0.08, 0.16)
casing_eject(c, 0.14)
c.v('Arma', 0.0).v('Arma', 0.10, (0, -0.025, 0.01), (1.2, 0, 0)).v('Arma', 0.30, (0, 0.012, -0.004), (-0.6, 0, 0)).v('Arma', 0.60)
clips.append(c)

c = W.ClipDef('Recargar_Inicio', 0.45); seg_inicio(c, 0.0); clips.append(c)
c = W.ClipDef('Recargar_Cartucho', 0.50); seg_cartucho(c, 0.0); clips.append(c)
c = W.ClipDef('Recargar_Fin', 0.55); seg_fin(c, 0.0); clips.append(c)
c = W.ClipDef('Recargar', 0.45 + 3 * 0.50 + 0.55)
seg_inicio(c, 0.0)
for i in range(3):
    seg_cartucho(c, 0.45 + i * 0.50)
seg_fin(c, 0.45 + 1.5)
clips.append(c)

c = W.ClipDef('Reposo', 2.0, loop=True)
c.v('Arma', 0.0).v('Arma', 0.5, (0, 0, 0.007), (0.5, 0, 0.3)).v('Arma', 1.0).v('Arma', 1.5, (0, 0, -0.007), (-0.4, 0, -0.25)).v('Arma', 2.0)
c.hand('L', 0.0, WL, J, POLE_L).hand('L', 2.0, WL, J, POLE_L)
clips.append(c)

# Inspeccionar (Maikol la dejo a nuestro criterio): gira el arma para mirar la ventana de expulsion, abre la recamara con
# medio bombeo, cierra, gira al otro lado y vuelve. La mano izquierda no suelta la bomba.
PH, CH = 45.0 * s, 38.0 * s
INSP = [(0.00, (0, 0, 0), (0, 0, 0)),                      # v2c: giros mas marcados y el arma mas alta (en v2b casi no se notaba)
        (0.45, (-0.18, -0.08, 0.20), (10, -45, 20)),
        (0.70, (-0.18, -0.08, 0.20), (11, -47, 21)),
        (1.30, (-0.18, -0.08, 0.20), (11, -47, 21)),
        (1.95, (-0.10, -0.06, 0.20), (12, 40, -26)),
        (2.40, (-0.10, -0.06, 0.20), (13, 42, -28)),
        (3.00, (0, 0, 0), (0, 0, 0))]
c = W.ClipDef('Inspeccionar', 3.00)
c.p('Bomba', 0.75).p('Bomba', 0.92, (0, -PH, 0)).p('Bomba', 1.08, (0, -PH, 0)).p('Bomba', 1.25)
c.p('Cerrojo', 0.75).p('Cerrojo', 0.92, (0, -CH, 0)).p('Cerrojo', 1.08, (0, -CH, 0)).p('Cerrojo', 1.25)
c.e(0.92, 'bomba_atras').e(1.25, 'bomba_adelante')
W.inspect(c, INSP, J, {'R': POLE_R, 'L': POLE_L},
          lambda t, T, R: (WL + Vector((0, -PH * W.ramp(t, 0.75, 0.92, 1.08, 1.25), 0)), False, 1.0))
clips.append(c)


def export_rig_clips(rig, objs, acts, tag):
    first = acts['Reposo']
    A.set_action(rig, first)
    A.export_fbx(os.path.join(OUT, '%s_%s.fbx' % (NOMBRE, tag)), objs, anim=True, all_actions=True)
    for n, act in acts.items():
        A.set_action(rig, act)
        A.export_fbx(os.path.join(OUT, 'clips', '%s_%s_%s.fbx' % (NOMBRE, tag, n)), objs, anim=True)
    rig.animation_data.action = None


acts_w = {cd.name: cd.build(rig_w, BW, vm=False) for cd in clips}
mundo_objs = [rig_w] + partes
export_rig_clips(rig_w, mundo_objs, acts_w, 'Mundo')
for act in acts_w.values():
    bpy.data.actions.remove(act)
acts_v = {cd.name: cd.build(rig_v, BV, vm=True) for cd in clips}
vm_objs = [rig_v] + list(vm_parts.values()) + list(arms.values())
export_rig_clips(rig_v, vm_objs, acts_v, 'VM')
for act in list(acts_v.values()):
    bpy.data.actions.remove(act)
acts_w, acts_v = {}, {}
for cd in clips:
    act = cd.build(rig_w, BW, vm=False)
    act.name = 'Mundo_' + cd.name
    acts_w[cd.name] = act
    act = cd.build(rig_v, BV, vm=True)
    act.name = 'VM_' + cd.name
    acts_v[cd.name] = act
rig_w.animation_data.action = None
rig_v.animation_data.action = None
for o in partes:
    o.name = o.name + '_rig'
cst, st_objs = W.static_copies(partes)
for o2, o in zip(st_objs, partes):
    o2.name = {'Cuerpo_rig': 'Handle'}.get(o.name, o.name[:-4])
A.export_fbx(os.path.join(OUT, NOMBRE + '_Mundo_Estatico.fbx'), st_objs)
A.export_glb(os.path.join(OUT, NOMBRE + '_Mundo.glb'), st_objs)
W.remove_collection(cst)
for o in partes:
    o.name = o.name[:-4]
cst, st_objs = W.static_copies(list(vm_parts.values()) + list(arms.values()), 'TMP_VM')
A.export_glb(os.path.join(OUT, NOMBRE + '_VM.glb'), st_objs)
W.remove_collection(cst)
# puntos para efectos/camara (la X va engrosada por XS como las piezas)
PUNTOS = {'Boca': P3(0, 990, 9), 'Expulsion': P3(21 * XS, 440, 9), 'PuertoCarga': P3(0, 480, -40),
          'MiraTrasera': P3(0, 345, 30), 'MiraDelantera': P3(0, 975, 32.5)}
W.write_eventos(OUT, NOMBRE, clips, PUNTOS, cuerpo)
A.log('exportado')

# ------------------------------------------------------------------ RENDERS de comprobacion
CR = A.collection('Ref')
CC = A.collection('Camaras')
A.setup_world((0.50, 0.54, 0.58), 0.85)
A.add_lights(CC)
PV = os.path.join(OUT, 'previews')
rig_w.animation_data.action = None
rig_v.animation_data.action = None
for pb in list(rig_w.pose.bones) + list(rig_v.pose.bones):
    pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
mn, mx = W.bounds(partes)
ctr = (mn + mx) / 2
A.setup_render((1280, 720), 'CYCLES', 48)
W.hide_only({'Arma_Mundo', 'Camaras'})
cams = {
    '1_tres_cuartos': W.look_cam(CC, 'C1', ctr, (1.0, 0.75, 0.45), 7.2, 50),
    '2_lado_izq': W.look_cam(CC, 'C2', ctr, (-1, 0, 0), 9.0, 50, ortho=4.9),
    '3_atras_arriba': W.look_cam(CC, 'C3', ctr + Vector((0, -0.6, 0.0)), (0.55, -1.0, 0.5), 5.2, 50),
    '4_abajo_der': W.look_cam(CC, 'C4', ctr, (0.8, 0.35, -0.5), 6.8, 50),
}
for n, cam in cams.items():
    A.render(os.path.join(PV, NOMBRE + '_' + n + '.png'), cam)
W.hide_only({'Arma_VM', 'Camaras'})
camvm = W.vm_camera(CC)
A.render(os.path.join(PV, NOMBRE + '_5_primera_persona.png'), camvm)
W.hide_only({'Ref', 'Arma_Mundo', 'Camaras'})
figs = A.reference_figure(CR, x=0, y=0, h=5.2)
A.ruler(CR, -2.6, 0, 6)
W.backdrop(CR, 0.0)
rig_w.location = W.tool_pose(figs)              # en la mano, con el brazo hacia delante como un Tool de Roblox
bpy.context.view_layer.update()
cs = W.look_cam(CC, 'CEsc', (0.6, 1.4, 2.9), (1.0, 0.75, 0.35), 13.5, 50)
A.render(os.path.join(PV, NOMBRE + '_6_escala_R15.png'), cs)
rig_w.location = (0, 0, 0)
rig_w.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

if not QUICK:
    A.setup_render((480, 270), 'CYCLES', 16)
    sc = bpy.context.scene
    TIMES = {'Equipar': [0, 0.15, 0.30, 0.42, 0.52, 0.60, 0.72, 0.88], 'Disparo': [0, 0.03, 0.06, 0.12, 0.20, 0.30, 0.38, 0.44],
             'Bombear': [0, 0.08, 0.16, 0.22, 0.28, 0.38, 0.48, 0.58],
             'Recargar_Inicio': [0, 0.1, 0.2, 0.3, 0.4], 'Recargar_Cartucho': [0, 0.06, 0.14, 0.22, 0.30, 0.36, 0.42, 0.49],
             'Recargar_Fin': [0, 0.1, 0.2, 0.3, 0.4, 0.5], 'Recargar': [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.9, 2.4, 2.6, 2.9, 3.1, 3.4],
             'Reposo': [0, 0.5, 1.0, 1.5], 'Inspeccionar': [0.3, 0.6, 0.92, 1.1, 1.6, 2.0, 2.4, 2.8]}
    camvx = W.look_cam(CC, 'CVX', G + Vector((-0.2, 0.9, 0.1)), (1.0, 0.45, 0.30), 6.4, 50)
    camw = W.look_cam(CC, 'CW', ctr + Vector((0, 0, 0.0)), (1.0, 0.15, 0.25), 8.0, 50)
    for n, ts in TIMES.items():
        W.hide_only({'Arma_VM', 'Camaras'})
        A.set_action(rig_v, acts_v[n])
        for cam_, tag, ttl in ((camvm, 'VM', 'primera persona'), (camvx, 'VMext', 'vista externa')):
            items = []
            for t in ts:
                sc.frame_set(int(round(t * 60)))
                p = os.path.join(PV, '_f_%s_%03d.png' % (n, int(t * 1000)))
                A.render(p, cam_)
                items.append((p, '%s %.2fs' % (n, t)))
            W.contact_sheet(items, 4, os.path.join(PV, '%s_clip_%s_%s.png' % (NOMBRE, tag, n)),
                            title='%s %s - %s (%.2fs)' % (NOMBRE, ttl, n, [x for x in clips if x.name == n][0].length))
            for p, _ in items:
                os.remove(p)
    rig_v.animation_data.action = None
    W.hide_only({'Arma_Mundo', 'Camaras'})
    for n in ('Disparo', 'Bombear', 'Recargar_Cartucho', 'Inspeccionar'):
        A.set_action(rig_w, acts_w[n])
        items = []
        for t in TIMES[n]:
            sc.frame_set(int(round(t * 60)))
            p = os.path.join(PV, '_f_w_%s_%03d.png' % (n, int(t * 1000)))
            A.render(p, camw)
            items.append((p, '%s %.2fs' % (n, t)))
        W.contact_sheet(items, 4, os.path.join(PV, '%s_clip_Mundo_%s.png' % (NOMBRE, n)), title='%s mundo - %s' % (NOMBRE, n))
        for p, _ in items:
            os.remove(p)
    rig_w.animation_data.action = None
    sc.frame_set(0)

W.hide_only({'Arma_Mundo', 'Arma_VM', 'Ref', 'Camaras'})
A.save_blend(os.path.join(OUT, NOMBRE + '.blend'))
mn, mx = W.bounds(partes)
A.write_json(os.path.join(OUT, 'datos.json'), {
    'triangulos': TRIS, 'triangulos_total': sum(TRIS.values()), 'triangulos_brazos_vm': A.tris(arms.values()),
    'largo_studs': LARGO, 'medidas_studs': [round(v, 3) for v in (mx - mn)],
    'clips': {cd.name: {'duracion_s': cd.length, 'bucle': cd.loop, 'partes': sorted(cd.parts.keys()), 'vm_extra': sorted(cd.vm.keys())} for cd in clips},
    'viewmodel_origen_arma_desde_camara': list(G), 'exportacion': 'FBX global_scale=0.01, ejes -Z delante / Y arriba (1 unidad = 1 stud)'})
A.log('listo')
