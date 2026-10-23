# Subfusil (estilo MP5 generico, sin marcas) para el juego "apocalipsis".
# blender -b --factory-startup -P build_subfusil.py        (QUICK=1 salta las hojas de contacto)
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import importlib
import ap_lib as A
import ap_armas as W
importlib.reload(A); importlib.reload(W)
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler

NOMBRE = 'Subfusil'
QUICK = os.environ.get('QUICK') == '1'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'armas', 'subfusil')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

LARGO = 2.9                    # studs, de la culata a la boca
s = LARGO / 650.0
GY, GZ = 252.0, -100.0         # centro de la empunadura (origen) en mm del dibujo; eje del canon en z = 0


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

# ------------------------------------------------------------------ CUERPO
mb = A.MB('Cuerpo')
stock = [(0, 26), (60, 30), (176, 22), (176, -22), (120, -34), (60, -58), (0, -68)]
mb.prism([yz(*p) for p in stock], -17 * s, 17 * s, 'polimero', plane='YZ', bevel=1.8 * s)
mb.prism([yz(*p) for p in [(-13, 24), (0, 26), (0, -68), (-13, -64)]], -17.5 * s, 17.5 * s, 'goma', plane='YZ', bevel=1.2 * s)
# receptor (tubo de chapa octogonal) con tapa trasera
mb.cyl(P3(0, 170, 0), P3(0, 482, 0), 31 * s, 8, 'metal')
mb.cyl(P3(0, 160, 0), P3(0, 172, 0), 26 * s, 8, 'polimero')
# alza trasera de tambor y proteccion
mb.box(P3(0, 206, 37), (26 * s, 30 * s, 10 * s), 'mira', bevel=1.4 * s, edges='y')
mb.box(P3(-10.0, 206, 45), (4 * s, 30 * s, 9 * s), 'mira')
mb.box(P3(10.0, 206, 45), (4 * s, 30 * s, 9 * s), 'mira')
mb.cyl(P3(0, 300, 22), P3(0, 600, 22), 10.5 * s, 8, 'metal', cap0=False)               # tubo de la palanca de carga (silueta MP5)
# guardamano (cubre el canon)
sec = lambda k: [(x * k, -3 + (z + 3) * k) for (x, z) in [(-17, -36), (17, -36), (33, -18), (33, 18), (17, 36), (-17, 36), (-33, 18), (-33, -18)]]
mb.loft([[xz(*p) for p in sec(0.9)], [xz(*p) for p in sec(1.0)], [xz(*p) for p in sec(1.0)], [xz(*p) for p in sec(0.88)]],
        [Y(322), Y(332), Y(462), Y(474)], 'polimero', plane='XZ')
# canon, tunel de la mira y punto de mira
mb.cyl(P3(0, 470, -2), P3(0, 600, -2), 10 * s, 8, 'canon', cap0=False)
mb.cyl(P3(0, 590, 10), P3(0, 640, 10), 23 * s, 8, 'canon', inset_cap1=9 * s, inset_depth=8 * s, inset_mat='interior')
mb.cyl(P3(0, 600, -2), P3(0, 652, -2), 9 * s, 8, 'canon', inset_cap1=3 * s, inset_depth=8 * s, inset_mat='interior')
mb.box(P3(0, 615, 31.5), (4.4 * s, 4.4 * s, 12 * s), 'mira')
mb.box(P3(-9.5, 615, 35.0), (3.0 * s, 9 * s, 14 * s), 'canon')
mb.box(P3(9.5, 615, 35.0), (3.0 * s, 9 * s, 14 * s), 'canon')
# caja del disparador, boca del cargador y empunadura
mb.box(P3(0, 318, -39), (44 * s, 168 * s, 16 * s), 'polimero', bevel=1.8 * s, edges='y')
mb.box(P3(0, 366, -58), (42 * s, 64 * s, 54 * s), 'polimero', bevel=1.6 * s, edges='z')
mb.box(P3(0, 262, -56), (40 * s, 48 * s, 36 * s), 'polimero')
mb.prism([yz(*p) for p in [(240, -52), (284, -52), (273, -100), (260, -150), (214, -150), (222, -100)]], -15 * s, 15 * s, 'polimero', plane='YZ')
mb.box(P3(0, 236, -151), (31 * s, 52 * s, 5 * s), 'goma')
guard = [(288, -62), (292, -86), (300, -94), (330, -94), (337, -86), (340, -66)]
mb.band([yz(*p) for p in guard], 7.5 * s, -6 * s, 6 * s, 'polimero', plane='YZ')
# selector y boton del cargador (lado izquierdo)
mb.box(P3(-25.5, 270, -42), (5 * s, 24 * s, 8 * s), 'metal')
mb.cyl(P3(-23, 332, -60), P3(-29, 332, -60), 4.2 * s, 6, 'metal')
cuerpo = mb.finish(CM, origin=(0, 0, 0))

# ------------------------------------------------------------------ CARGADOR CURVO (se mueve)
mb = A.MB('Cargador')
mag = [(366, -40), (373, -84), (391, -128), (419, -167)]
mb.band([yz(*p) for p in mag], 42 * s, -11 * s, 11 * s, 'cargador', plane='YZ', bevel=1.2 * s)
mb.prism([yz(*p) for p in [(407, -166), (445, -176), (440, -184), (402, -174)]], -12.5 * s, 12.5 * s, 'base', plane='YZ')
cargador = mb.finish(CM, origin=P3(0, 366, -40))

# ------------------------------------------------------------------ PALANCA DE CARGA (izquierda, se mueve)
mb = A.MB('Palanca')
mb.box(P3(-33, 340, 10), (13 * s, 30 * s, 12 * s), 'palanca')
mb.box(P3(-41, 344, 17), (9 * s, 20 * s, 20 * s), 'palanca', bevel=1.4 * s, edges='x')
palanca = mb.finish(CM, origin=P3(-33, 340, 10))

# ------------------------------------------------------------------ CERROJO (visible en la ventana de expulsion derecha)
mb = A.MB('Cerrojo')
mb.box(P3(28.5, 365, 9), (3.4 * s, 40 * s, 14 * s), 'cerrojo')
cerrojo = mb.finish(CM, origin=P3(28.5, 365, 9))

# ------------------------------------------------------------------ GATILLO
mb = A.MB('Gatillo')
mb.band([yz(*p) for p in [(318, -52), (314, -68), (308, -84)]], 7 * s, -3.4 * s, 3.4 * s, 'gatillo', plane='YZ')
gatillo = mb.finish(CM, origin=P3(0, 318, -52))

# ------------------------------------------------------------------ CASQUILLO 9 mm (oculto dentro del receptor)
mb = A.MB('Casquillo')
mb.lathe(P3(0, 330, 6), P3(0, 349, 6), [(r * s, t) for r, t in [(4.9, 0.0), (4.9, 0.12), (4.7, 0.19), (4.7, 1.0)]], 6, 'laton')
casquillo = mb.finish(CM, origin=P3(0, 340, 6))

partes = [cuerpo, cargador, palanca, cerrojo, gatillo, casquillo]
TRIS = {o.name: A.tris([o]) for o in partes}
A.log('triangulos', TRIS, 'total', sum(TRIS.values()))

# ------------------------------------------------------------------ UV + horneado + pintura
ref = bpy.data.objects.new('RefPos', None)
CM.objects.link(ref)
A.uv_unwrap(partes, angle=50, margin=0.004,
            weights={'Cuerpo': 1.0, 'Cargador': 0.95, 'Palanca': 0.8, 'Cerrojo': 0.7, 'Gatillo': 0.7, 'Casquillo': 0.6})
R = 2.5
maps = A.bake_maps(partes, 2048, R=R, ao_dist=0.14, bevel_r=0.012, samples=20, pos_ref=ref,
                   explode={cargador: (0, 0, -3.0), palanca: (0, 0, 3.0), cerrojo: (3.0, 0, 0), gatillo: (0, 0, -6.0),
                            casquillo: (0, 0, 6.0)})
P = A.Paint(maps, R=R, light=(-0.30, 0.25, 0.92))
mm = lambda v: v / s


def body_paint(P, msk, pos, nrm, col):
    x = mm(pos[:, 0])
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    # ventana de expulsion (derecha): fondo oscuro y marco
    win = (nrm[:, 0] > 0.6) & (y > 292) & (y < 388) & (z > -6) & (z < 24) & (x > 20)
    col[win] = np.array([0.05, 0.05, 0.055], np.float32)
    frame = (nrm[:, 0] > 0.6) & (y > 288) & (y < 392) & (z > -9) & (z < 27) & ~win & (x > 20)
    col[frame] = col[frame] * 0.72
    # ranuras de ventilacion verticales en el guardamano
    vent = (np.abs(nrm[:, 0]) > 0.5) & (y > 345) & (y < 480) & (z < 8) & (z > -28)
    k = ((y - 345) % 15.0) < 5.0
    col[vent & k] = col[vent & k] * 0.45
    # rejilla de agarre en la empunadura y el guardamano
    grip = (np.abs(nrm[:, 0]) > 0.6) & (z < -62) & (z > -149) & (y > 212) & (y < 286)
    chk = (((y * 0.5) % 1.0) < 0.5) ^ (((z * 0.5) % 1.0) < 0.5)
    col[grip & chk] = col[grip & chk] * 0.80
    # marcas del selector (tres puntos) y rayones largos del receptor
    sel = (nrm[:, 0] < -0.6) & (np.abs(y - 270) < 14) & (np.abs(z + 42) < 4)
    col[sel] = col[sel] * 0.55
    side = np.abs(nrm[:, 0]) > 0.6
    sp = np.stack([pos[:, 0] * 25.0, pos[:, 1] * 2.2, pos[:, 2] * 30.0], 1)
    sc = side & (z > -30) & (y > 172) & (y < 485) & (A.vnoise(sp, 81) > 0.86)
    col[sc] = np.clip(col[sc] * 1.22 + 0.02, 0, 1)
    sc2 = side & (z > -30) & (y > 172) & (y < 485) & (A.vnoise(sp * 1.8 + 5.0, 83) < 0.10)
    col[sc2] = col[sc2] * 0.62
    # canon: boca oscura
    r = np.sqrt(x ** 2 + z ** 2)
    sooty = (y > 646) & (r >= 7.0)
    col[sooty] = col[sooty] * 0.6
    return col


def metal_paint(P, msk, pos, nrm, col):
    return body_paint(P, msk, pos, nrm, col)


def mag_paint(P, msk, pos, nrm, col):
    z = mm(pos[:, 2]) + GZ
    k = (nrm[:, 0] > 0.6) & (((z + 60) % 16.0) < 3.0) & (z < -70)
    col[k] = col[k] * 0.5
    return col


P.region('polimero', '#35373b', var=0.10, stroke=(1, 1, 1), stroke_scale=8, blotch=0.09, ao=0.62, ao_tint='#121316', light=0.26,
         grad=0.12, edge_col='#7b7f84', edge=1.0, edge_th=0.035, edge_break=0.45, grime=0.28, dust=0.24, seed=3, extra=body_paint)
P.region('metal', '#4a5057', var=0.09, stroke=(1, 5, 1), stroke_scale=7, blotch=0.08, ao=0.62, ao_tint='#171d28', light=0.26, grad=0.14,
         edge_col='#cdd3d8', edge=1.0, edge_th=0.035, edge_break=0.40, grime=0.22, rust=0.16, dust=0.14, seed=5, extra=metal_paint)
P.region('canon', '#3a3f45', var=0.08, stroke=(1, 8, 1), stroke_scale=7, ao=0.55, ao_tint='#10151b', light=0.3, grad=0.12,
         edge_col='#aab2b9', edge=1.0, edge_th=0.035, grime=0.22, rust=0.10, seed=7, extra=body_paint)
P.region('goma', '#2a2723', var=0.06, stroke=(1, 1, 1), stroke_scale=14, ao=0.5, edge_col='#5c564e', edge=0.8, seed=9)
P.region('mira', '#2d3135', var=0.05, ao=0.4, edge_col='#a3abb2', edge=0.9, seed=11)
P.region('interior', '#0d0d0f', var=0.04, ao=0.3, seed=13)
P.region('cargador', '#43474c', var=0.07, stroke=(1, 1, 3), stroke_scale=8, ao=0.4, edge_col='#a8afb6', edge=1.0, edge_th=0.035,
         seed=15, extra=mag_paint)
P.region('base', '#33302d', var=0.06, ao=0.45, edge_col='#77726a', edge=1.0, grime=0.25, seed=17)
P.region('palanca', '#2a2d31', var=0.05, ao=0.45, edge_col='#b4bcc3', edge=1.0, seed=19)
P.region('cerrojo', '#a2a8ae', var=0.08, stroke=(1, 4, 1), stroke_scale=9, ao=0.5, edge_col='#e9edf0', edge=0.9, grime=0.2, seed=21)
P.region('gatillo', '#3a3a3a', var=0.04, ao=0.4, edge_col='#8e8e8e', edge=0.9, seed=23)
P.region('laton', '#cba14a', var=0.08, stroke=(1, 3, 1), stroke_scale=14, ao=0.3, light=0.3, edge_col='#f3d994', edge=0.9, seed=25)
TEX = os.path.join(OUT, 'texturas', NOMBRE + '_Color.png')
P.save(TEX, 1024)
mat = A.final_material('M_' + NOMBRE, TEX)
A.assign_final(partes, mat)
bpy.data.objects.remove(ref, do_unlink=True)

# ------------------------------------------------------------------ RIG de mundo
MOV = ['Cargador', 'Palanca', 'Cerrojo', 'Gatillo', 'Casquillo']
piv = {o.name: o.location.copy() for o in (cargador, palanca, cerrojo, gatillo, casquillo)}
bones_w = [('Arma', (0, 0, 0), None, 0.3)] + [(k, tuple(piv[k]), 'Arma', 0.12) for k in MOV]
rig_w = A.make_armature(NOMBRE, bones_w, CM)
A.skin_rigid(cuerpo, rig_w, 'Arma')
for o in (cargador, palanca, cerrojo, gatillo, casquillo):
    A.skin_rigid(o, rig_w, o.name)
BW = [b[0] for b in bones_w]

# ------------------------------------------------------------------ VIEWMODEL
CV = A.collection('Arma_VM')
G = Vector((0.36, 1.10, -0.66))
SRa, SLa = Vector((0.90, -0.90, -1.00)), Vector((-0.85, -0.10, -1.00))
HR = Vector((0.03, 0.00, 0.00))
WR = Vector((0.04, -0.19, -0.10))
HL = Vector((-0.08, 0.70, 0.30))
WL = Vector((-0.32, 0.40, 0.15))


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
ER = elbow(SR, WR, 1.15, 1.05, (1, 0, -1))
EL = elbow(SL, WL, 1.15, 1.05, (-1, -0.3, -1))
J = {'R': dict(S=SR, E=ER, W=WR, H=HR, Hs=(0.36, 0.46, 0.33), Hr=(-18, 0, 0)),
     'L': dict(S=SL, E=EL, W=WL, H=HL, Hs=(0.31, 0.42, 0.30), Hr=(-8, 0, 0))}
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
BOLT = 38.0 * s
HANDLE = 70.0 * s
MAG_DOWN = Vector((0.0, 0.07, -1.0)).normalized()
clips = []


def eject(c, t0, dur):
    c.p('Casquillo', t0).p('Casquillo', t0 + 0.02, (0, 0, 14 * s), ip='LINEAR') \
     .p('Casquillo', t0 + 0.04, (34 * s, -6 * s, 28 * s), (0, 0, -40), ip='LINEAR') \
     .p('Casquillo', t0 + 0.09, (150 * s, -22 * s, 86 * s), (120, 30, -140), ip='LINEAR') \
     .p('Casquillo', t0 + dur - 0.01, (330 * s, -60 * s, 40 * s), (330, 50, -300), ip='CONSTANT').p('Casquillo', t0 + dur)


def charge(c, t0, hand=True):
    """Tirar de la palanca de carga y soltarla (la mano izquierda cruza sobre el arma)."""
    hp = Vector((-0.08, 0.50, 0.70))
    c.p('Palanca', t0).p('Palanca', t0 + 0.10, (0, -HANDLE, 0)).p('Palanca', t0 + 0.14, (0, -HANDLE, 0)).p('Palanca', t0 + 0.17, ip='LINEAR') \
     .p('Palanca', t0 + 0.30)
    c.p('Cerrojo', t0).p('Cerrojo', t0 + 0.10, (0, -BOLT, 0)).p('Cerrojo', t0 + 0.14, (0, -BOLT, 0)).p('Cerrojo', t0 + 0.17, ip='LINEAR') \
     .p('Cerrojo', t0 + 0.30)
    if hand:
        c.hand('L', t0, WL, J, POLE_L).hand('L', t0 + 0.05, hp, J, POLE_L).hand('L', t0 + 0.10, hp + Vector((0, -HANDLE, 0)), J, POLE_L) \
         .hand('L', t0 + 0.14, hp + Vector((0, -HANDLE, 0)), J, POLE_L).hand('L', t0 + 0.17, hp + Vector((0, 0.0, 0.0)), J, POLE_L) \
         .hand('L', t0 + 0.30, WL, J, POLE_L)


c = W.ClipDef('Equipar', 0.80)
c.v('Arma', 0.0, (0.30, -0.30, -0.95), (-55, 22, -10)).v('Arma', 0.30, (0.02, -0.03, -0.03), (4, -3, 2)).v('Arma', 0.40, (0, 0, 0), (0, 0, 0)) \
 .v('Arma', 0.80)
c.hand('L', 0.0, WL + Vector((-0.1, -0.1, -0.5)), J, POLE_L).hand('L', 0.28, WL, J, POLE_L)
charge(c, 0.42)
clips.append(c)

c = W.ClipDef('Disparo', 0.16)
c.v('Arma', 0.0).v('Arma', 0.02, (0.0, -0.11, 0.016), (3.4, 0.4, -0.5)).v('Arma', 0.07, (0, -0.035, 0.005), (1.0, 0.1, -0.1)).v('Arma', 0.12)
c.p('Gatillo', 0.0).p('Gatillo', 0.01, rot=(-14, 0, 0), ip='LINEAR').p('Gatillo', 0.08, rot=(-14, 0, 0)).p('Gatillo', 0.14)
c.p('Cerrojo', 0.0).p('Cerrojo', 0.02, (0, -BOLT, 0), ip='LINEAR').p('Cerrojo', 0.07).p('Cerrojo', 0.16)
eject(c, 0.0, 0.16)
c.hand('L', 0.0, WL, J, POLE_L).hand('L', 0.16, WL, J, POLE_L)
clips.append(c)

c = W.ClipDef('Recargar', 1.95)
mag_piv = Vector(piv['Cargador'])
base_bottom = P3(0, 425, -179) - mag_piv                  # base del cargador respecto a su pivote
slot = Vector(piv['Cargador'])
def hand_under(k): return slot + base_bottom + MAG_DOWN * k + Vector((-0.12, 0.0, -0.18))
pouch = Vector((-0.34, 0.30, -0.55))
c.v('Arma', 0.0).v('Arma', 0.20, (-0.12, 0.03, 0.10), (6, 10, 18)).v('Arma', 1.10, (-0.12, 0.03, 0.10), (6, 10, 18)) \
 .v('Arma', 1.18, (-0.12, 0.03, 0.085), (5, 10, 18)).v('Arma', 1.35, (0, 0, 0), (0, 0, 0)).v('Arma', 1.95)
c.hand('L', 0.0, WL, J, POLE_L).hand('L', 0.18, hand_under(0.0) + Vector((0.0, -0.05, -0.05)), J, POLE_L) \
 .hand('L', 0.34, hand_under(0.15), J, POLE_L).hand('L', 0.44, hand_under(0.55) + Vector((0, 0.0, -0.1)), J, POLE_L) \
 .hand('L', 0.60, pouch, J, POLE_L).hand('L', 0.78, pouch, J, POLE_L).hand('L', 0.98, hand_under(0.55), J, POLE_L) \
 .hand('L', 1.08, hand_under(0.12), J, POLE_L).hand('L', 1.16, hand_under(0.0), J, POLE_L).hand('L', 1.30, WL, J, POLE_L)
rel = lambda p: tuple(p - mag_piv)
c.p('Cargador', 0.0).p('Cargador', 0.30).p('Cargador', 0.36, tuple(MAG_DOWN * 0.18), ip='LINEAR') \
 .p('Cargador', 0.50, tuple(MAG_DOWN * 1.4 + Vector((0, 0.05, 0))), (20, 0, 8), ip='CONSTANT') \
 .p('Cargador', 0.84, rel(pouch + Vector((0.12, 0.10, 0.12))), (12, 0, 0), ip='LINEAR').p('Cargador', 0.98, tuple(MAG_DOWN * 0.60 + Vector((0, 0, 0))), ip='LINEAR') \
 .p('Cargador', 1.08, tuple(MAG_DOWN * 0.12)).p('Cargador', 1.16).p('Cargador', 1.95)
charge(c, 1.34)
clips.append(c)

c = W.ClipDef('Amartillar', 0.40)
charge(c, 0.0)
c.v('Arma', 0.0).v('Arma', 0.10, (0, -0.012, 0.004), (0.8, 0, 0)).v('Arma', 0.40)
clips.append(c)

c = W.ClipDef('Reposo', 2.0, loop=True)
c.v('Arma', 0.0).v('Arma', 0.5, (0, 0, 0.006), (0.5, 0, 0.3)).v('Arma', 1.0).v('Arma', 1.5, (0, 0, -0.006), (-0.4, 0, -0.25)).v('Arma', 2.0)
c.hand('L', 0.0, WL, J, POLE_L).hand('L', 2.0, WL, J, POLE_L)
clips.append(c)


def export_rig_clips(rig, objs, acts, tag):
    A.set_action(rig, acts['Reposo'])
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
    '1_tres_cuartos': W.look_cam(CC, 'C1', ctr, (1.0, 0.75, 0.45), 5.4, 50),
    '2_lado_izq': W.look_cam(CC, 'C2', ctr, (-1, 0, 0), 8.0, 50, ortho=3.5),
    '3_atras_arriba': W.look_cam(CC, 'C3', ctr + Vector((0, -0.4, 0.0)), (0.55, -1.0, 0.5), 4.3, 50),
    '4_abajo_der': W.look_cam(CC, 'C4', ctr, (0.8, 0.35, -0.5), 5.0, 50),
}
for n, cam in cams.items():
    A.render(os.path.join(PV, NOMBRE + '_' + n + '.png'), cam)
W.hide_only({'Arma_VM', 'Camaras'})
camvm = W.vm_camera(CC)
A.render(os.path.join(PV, NOMBRE + '_5_primera_persona.png'), camvm)
W.hide_only({'Ref', 'Arma_Mundo', 'Camaras'})
A.reference_figure(CR, x=0, y=0, h=5.2)
A.ruler(CR, -2.6, 0, 6)
W.backdrop(CR, 0.0)
rig_w.location = (1.3, 0.1, 3.0)
rig_w.rotation_euler = (0, math.radians(6), 0)
bpy.context.view_layer.update()
cs = W.look_cam(CC, 'CEsc', (0.5, 0.2, 2.8), (1.0, 1.0, 0.25), 12.0, 50)
A.render(os.path.join(PV, NOMBRE + '_6_escala_R15.png'), cs)
rig_w.location = (0, 0, 0)
rig_w.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

if not QUICK:
    A.setup_render((480, 270), 'CYCLES', 16)
    sc = bpy.context.scene
    TIMES = {'Equipar': [0, 0.15, 0.30, 0.42, 0.50, 0.55, 0.62, 0.78], 'Disparo': [0, 0.01, 0.02, 0.04, 0.06, 0.09, 0.12, 0.15],
             'Recargar': [0, 0.18, 0.34, 0.50, 0.70, 0.98, 1.10, 1.20, 1.38, 1.45, 1.52, 1.85],
             'Amartillar': [0, 0.05, 0.10, 0.14, 0.17, 0.25], 'Reposo': [0, 0.5, 1.0, 1.5]}
    camvx = W.look_cam(CC, 'CVX', G + Vector((-0.1, 0.7, 0.05)), (1.0, 0.45, 0.30), 5.2, 50)
    camw = W.look_cam(CC, 'CW', ctr, (1.0, 0.15, 0.25), 6.4, 50)
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
    for n in ('Disparo', 'Recargar'):
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
