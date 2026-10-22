# Pistola 9mm (estilo Glock generico, sin marcas) para el juego "apocalipsis".
# blender -b --factory-startup -P build_pistola.py
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import importlib
import ap_lib as A
import ap_armas as W
importlib.reload(A); importlib.reload(W)
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler

NOMBRE = 'Pistola9mm'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'armas', 'pistola-9mm')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
RENDERS = os.path.join(ROOT, 'renders')
os.makedirs(RENDERS, exist_ok=True)

LARGO = 1.5                    # studs de punta a punta (decision de estilo: legible en mano R15)
s = LARGO / 186.0              # studs por mm del dibujo
GY, GZ = 19.6, 70.0            # punto de agarre (origen) en mm


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

# ------------------------------------------------------------------ CORREDERA (con miras y canon)
full = [(-12.75, 105), (12.75, 105), (12.75, 127), (8.5, 133.5), (-3, 133.5), (-8.5, 133.5), (-12.75, 127)]
port = [(-12.75, 105), (12.75, 105), (12.75, 114), (-3, 114), (-3, 133.5), (-8.5, 133.5), (-12.75, 127)]
nose = [(-12.75, 105), (12.75, 105), (12.75, 124), (8.5, 128.5), (-3, 128.5), (-8.5, 128.5), (-12.75, 124)]
mb = A.MB('Corredera')
mb.prism([xz(*p) for p in full], Y(0), Y(36), 'corredera', plane='XZ', bevel=1.1 * s)
mb.prism([xz(*p) for p in port], Y(36), Y(78), 'corredera', plane='XZ', cap0=False, cap1=False)
mb.loft([[xz(*p) for p in full], [xz(*p) for p in full], [xz(*p) for p in nose]], [Y(78), Y(181), Y(186)], 'corredera', plane='XZ', bevel=0.8 * s)
notch = [(-7, 133.5), (7, 133.5), (7, 140), (2.2, 140), (2.2, 136.8), (-2.2, 136.8), (-2.2, 140), (-7, 140)]
mb.prism([xz(*p) for p in notch], Y(8), Y(19), 'mira', plane='XZ', bevel=0.5 * s)
mb.box(P3(0, 175, 136.6), (4 * s, 6 * s, 6.4 * s), 'mira', bevel=0.5 * s)
mb.cyl(P3(0, 178, 119), P3(0, 187, 119), 7.0 * s, 8, 'canon', inset_cap1=2.4 * s, inset_depth=7 * s)
mb.box(P3(4, 57, 121), (16 * s, 41 * s, 14 * s), 'canon')
corredera = mb.finish(CM, origin=P3(0, 93, 119.5))

# ------------------------------------------------------------------ ARMAZON (polimero)
outline = [(0, 105.6), (178, 105.6), (180, 104), (180, 95), (177, 92), (167, 92), (165, 89), (122, 89), (120, 92),
           (100, 92), (52, 92), (50.5, 87)]
A_, B_ = Vector((50.5, 87)), Vector((19, 9))
for t, off in ((0.12, 0), (0.22, 3.4), (0.33, 0), (0.45, 3.4), (0.56, 0), (0.68, 3.0), (0.80, 0), (0.92, 1.0)):
    p = A_.lerp(B_, t)
    nrm = Vector((-(B_ - A_).y, (B_ - A_).x)).normalized()   # hacia delante
    if nrm.x < 0:
        nrm = -nrm
    q = p + nrm * off
    outline.append((q.x, q.y))
outline += [(19, 9), (-28, 9), (-29.5, 14), (-15, 50), (-2.5, 86), (-7, 95), (-9.5, 100.5), (-4, 105.6)]
mb = A.MB('Armazon')
mb.prism([yz(*p) for p in outline], -14 * s, 14 * s, 'armazon', plane='YZ', bevel=1.4 * s)
guard = [(96, 93), (98.5, 73), (94, 66.5), (62, 65), (54, 70.5), (51, 81)]
mb.band([yz(*p) for p in guard], 7 * s, -6.5 * s, 6.5 * s, 'armazon', plane='YZ', bevel=0.9 * s)
mb.box(P3(-14.7, 78, 103.4), (1.8 * s, 13 * s, 3.6 * s), 'palanca', bevel=0.4 * s)
mb.box(P3(0, 92, 101.2), (31 * s, 5 * s, 3.6 * s), 'palanca', bevel=0.4 * s)
armazon = mb.finish(CM, origin=(0, 0, 0))

# ------------------------------------------------------------------ CARGADOR (cuerpo inclinado + base)
T, Bc = Vector((27.0, 92.0)), Vector((-4.5, 9.0))
ax = (T - Bc)
ang = math.atan2(ax.x, ax.y)
mb = A.MB('Cargador')
mk = mb.mark()
mb.box((0, 0, 0), (22 * s, 31 * s, ax.length * s), 'cargador', bevel=1.0 * s, edges='z')
mid = (T + Bc) / 2
mb.xform_since(mk, Matrix.Translation(P3(0, mid.x, mid.y)) @ Matrix.Rotation(-ang, 4, 'X'))
mb.box(P3(0, -5, 5), (27 * s, 50 * s, 8 * s), 'base', bevel=1.6 * s)
cargador = mb.finish(CM, origin=P3(0, T.x, T.y))
MAG_DOWN = Vector((0, -math.sin(ang), -math.cos(ang)))   # direccion de salida del cargador

# ------------------------------------------------------------------ GATILLO
mb = A.MB('Gatillo')
trig = [(62, 91), (63.6, 84), (62.6, 78), (59.4, 73)]
mb.band([yz(*p) for p in trig], 5.2 * s, -3 * s, 3 * s, 'gatillo', plane='YZ', bevel=0.6 * s)
gatillo = mb.finish(CM, origin=P3(0, 62, 91))

# ------------------------------------------------------------------ CASQUILLO (escondido en la recamara en reposo)
mb = A.MB('Casquillo')
prof = [(4.9, 0.0), (4.9, 0.08), (4.2, 0.13), (4.7, 0.19), (4.7, 1.0)]
mb.lathe(P3(0, 52, 119), P3(0, 71, 119), [(r * s, t) for r, t in prof], 7, 'laton')
casquillo = mb.finish(CM, origin=P3(0, 61.5, 119))

partes = [armazon, corredera, cargador, gatillo, casquillo]
TRIS = {o.name: A.tris([o]) for o in partes}
A.log('triangulos', TRIS, 'total', sum(TRIS.values()))

# ------------------------------------------------------------------ UV + horneado + pintura
ref = bpy.data.objects.new('RefPos', None)
CM.objects.link(ref)
A.uv_unwrap(partes, angle=48, margin=0.005,
            weights={'Corredera': 1.55, 'Armazon': 1.0, 'Cargador': 0.75, 'Gatillo': 0.9, 'Casquillo': 0.6})
R = 2.0
maps = A.bake_maps(partes, 2048, R=R, ao_dist=0.12, bevel_r=0.012, samples=20, pos_ref=ref,
                   explode={cargador: (0, 0, -3.0), casquillo: (0, 0, 3.0), gatillo: (0, 0, -6.0)})
P = A.Paint(maps, R=R, light=(-0.30, 0.25, 0.92))
mm = lambda v: v / s   # studs -> mm del dibujo


def serrations(P, msk, pos, nrm, col):
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    side = np.abs(nrm[:, 0]) > 0.8
    zone = side & (y > 3) & (y < 33) & (z > 108) & (z < 129)
    u = (y + (z - 118) * 0.18) / 3.6
    fr = u - np.floor(u)
    groove = zone & (fr < 0.42)
    lip = zone & (fr >= 0.42) & (fr < 0.55)
    col[groove] = col[groove] * 0.42
    col[lip] = np.clip(col[lip] * 1.45 + 0.04, 0, 1)
    # tapa trasera de la corredera
    back = (nrm[:, 1] < -0.85) & (y < 2) & (np.abs(mm(pos[:, 0])) < 8) & (z > 110) & (z < 129)
    col[back] = col[back] * 1.18 + 0.02
    # puerto de expulsion: paredes interiores mas oscuras
    inner = (np.abs(nrm[:, 1]) > 0.85) & (y > 34) & (y < 80) & (z > 113)
    col[inner] = col[inner] * 0.55
    return col


def sights(P, msk, pos, nrm, col):
    x = mm(pos[:, 0])
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    rear = nrm[:, 1] < -0.8
    dot_f = rear & (y > 160) & ((x ** 2 + (z - 137.0) ** 2) < 1.25 ** 2)
    dot_r = rear & (y < 25) & ((((x - 4.6) ** 2 + (z - 137.6) ** 2) < 1.2 ** 2) | (((x + 4.6) ** 2 + (z - 137.6) ** 2) < 1.2 ** 2))
    white = np.array([0.93, 0.92, 0.86], np.float32)
    ring = np.array([0.55, 0.55, 0.52], np.float32)
    for m_ in (dot_f, dot_r):
        col[m_] = white
    near_f = rear & (y > 160) & ((x ** 2 + (z - 137.0) ** 2) < 1.7 ** 2) & ~dot_f
    col[near_f] = ring
    return col


def barrel(P, msk, pos, nrm, col):
    x = mm(pos[:, 0])
    z = mm(pos[:, 2]) + GZ
    y = mm(pos[:, 1]) + GY
    r = np.sqrt(x ** 2 + (z - 119) ** 2)
    bore = (y > 179) & (r < 4.7)
    col[bore] = np.array([0.05, 0.045, 0.04], np.float32) * (0.6 + 0.4 * (r[bore] / 4.7))[:, None]
    soot = (y > 185.5) & (r >= 4.7)
    col[soot] = col[soot] * 0.55
    return col


def grip(P, msk, pos, nrm, col):
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    yf = 19 + (z - 9) * 0.40 - 3.0
    yb = -28 + (z - 9) * 0.37 + 3.0
    zone = (np.abs(nrm[:, 0]) > 0.75) & (z > 14) & (z < 84) & (y < yf) & (y > yb)
    # textura de agarre: puntos pintados
    n1 = A.vnoise(pos[zone] * 95.0, 77)
    n2 = A.vnoise(pos[zone] * 95.0 + 13.3, 78)
    c = col[zone]
    c = c * (0.86 + 0.10 * (n1 > 0.60)[:, None] - 0.06 * (n2 < 0.30)[:, None])
    col[zone] = c * 0.93
    # borde del panel de agarre
    edge = (np.abs(nrm[:, 0]) > 0.75) & (z > 12) & (z < 86) & (np.abs(y - yf) < 1.0)
    col[edge] = col[edge] * 0.7
    # ranura del riel (bajo el guardapolvo)
    rail = (nrm[:, 2] < -0.8) & (y > 124) & (y < 163) & (z < 90)
    rr = ((y - 124) % 9.5) < 3.2
    col[rail & rr] = col[rail & rr] * 0.6
    return col


def mag_top(P, msk, pos, nrm, col):
    y = mm(pos[:, 1]) + GY
    z = mm(pos[:, 2]) + GZ
    top = (z > 89) & (nrm[:, 2] > 0.5)
    brass = np.array([0.80, 0.62, 0.27], np.float32)
    col[top] = brass * (0.85 + 0.25 * A.vnoise(pos[top] * 40, 5))[:, None]
    # agujeros testigo en la espalda del cargador
    back = (nrm[:, 1] < -0.6) & (z > 25) & (z < 85)
    k = ((z - 25) % 12.0) < 3.0
    col[back & k] = col[back & k] * 0.45
    return col


def trigger_blade(P, msk, pos, nrm, col):
    x = mm(pos[:, 0])
    blade = (np.abs(x) < 1.0) & (nrm[:, 1] > 0.5)
    col[blade] = col[blade] * 1.7 + 0.05
    return col


def primer(P, msk, pos, nrm, col):
    x = mm(pos[:, 0])
    z = mm(pos[:, 2]) + GZ
    r = np.sqrt(x ** 2 + (z - 119) ** 2)
    back = nrm[:, 1] < -0.8
    col[back & (r < 2.0)] = np.array([0.62, 0.5, 0.36], np.float32)
    col[back & (r >= 2.0) & (r < 2.5)] = col[back & (r >= 2.0) & (r < 2.5)] * 0.5
    return col


P.region('corredera', '#3e444b', var=0.07, stroke=(1, 4, 1), stroke_scale=7, blotch=0.06, ao=0.6, light=0.26, grad=0.16,
         edge_col='#b2bac2', edge=1.0, edge_th=0.05, edge_break=0.45, grime=0.18, rust=0.10, dust=0.12, seed=3, extra=serrations)
P.region('mira', '#2c2f33', var=0.05, ao=0.4, edge_col='#8e969e', edge=0.8, seed=5, extra=sights)
P.region('canon', '#857559', var=0.06, stroke=(1, 3, 1), stroke_scale=9, ao=0.7, edge_col='#d3bf93', edge=0.9,
         grime=0.25, grime_col='#2b241c', seed=7, extra=barrel)
P.region('armazon', '#35332f', var=0.05, stroke=(1, 1, 1), stroke_scale=9, blotch=0.05, ao=0.6, light=0.24, grad=0.12,
         edge_col='#736d62', edge=0.85, edge_th=0.05, grime=0.30, dust=0.22, seed=11, extra=grip)
P.region('palanca', '#30353a', var=0.05, ao=0.5, edge_col='#a5adb5', edge=1.0, seed=13)
P.region('cargador', '#3b3e42', var=0.06, stroke=(1, 1, 3), stroke_scale=8, ao=0.35, edge_col='#a3aab0', edge=0.9,
         seed=17, extra=mag_top)
P.region('base', '#2f2d2a', var=0.05, ao=0.45, edge_col='#67625a', edge=0.9, grime=0.2, seed=19)
P.region('gatillo', '#2b2b2b', var=0.04, ao=0.4, edge_col='#6f6f6f', edge=0.8, seed=23, extra=trigger_blade)
P.region('laton', '#c79f48', var=0.08, stroke=(1, 3, 1), stroke_scale=14, ao=0.3, light=0.3, edge_col='#f1d793',
         edge=0.9, seed=29, extra=primer)
TEX = os.path.join(OUT, 'texturas', NOMBRE + '_Color.png')
P.save(TEX, 1024)
mat = A.final_material('M_' + NOMBRE, TEX)
A.assign_final(partes, mat)
bpy.data.objects.remove(ref, do_unlink=True)

# ------------------------------------------------------------------ RIG de mundo (tercera persona)
piv = {'Corredera': corredera.location.copy(), 'Cargador': cargador.location.copy(),
       'Gatillo': gatillo.location.copy(), 'Casquillo': casquillo.location.copy()}
bones_w = [('Arma', (0, 0, 0), None, 0.25)] + [(k, tuple(v), 'Arma', 0.12) for k, v in piv.items()]
rig_w = A.make_armature(NOMBRE, bones_w, CM)
A.skin_rigid(armazon, rig_w, 'Arma')
for o in (corredera, cargador, gatillo, casquillo):
    A.skin_rigid(o, rig_w, o.name)
BW = [b[0] for b in bones_w]

# ------------------------------------------------------------------ VIEWMODEL (primera persona)
CV = A.collection('Arma_VM')
G = Vector((0.42, 1.40, -0.62))
HR = Vector((0.02, -0.02, -0.03))
WR = Vector((0.05, -0.20, -0.17))
HL = Vector((-0.21, 0.05, -0.10))
WL = Vector((-0.27, -0.10, -0.24))
SR = Vector((0.50, -1.80, -0.30))
SL = Vector((-1.30, -1.75, -0.36))


def elbow(S, Wr, L1, L2, pole):
    d = Wr - S
    dist = min(d.length, L1 + L2 - 0.01)
    dv = d.normalized()
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(L1 * L1 - a * a, 0))
    pp = Vector(pole) - dv * Vector(pole).dot(dv)
    pp.normalize()
    return S + dv * a + pp * h


ER = elbow(SR, WR, 1.05, 1.0, (1, 0, -1))
EL = elbow(SL, WL, 1.05, 1.0, (-1, -0.3, -1))
J = {'R': dict(S=SR, E=ER, W=WR, H=HR, Hs=(0.36, 0.46, 0.33), Hr=(-21, 0, 0)),
     'L': dict(S=SL, E=EL, W=WL, H=HL, Hs=(0.31, 0.42, 0.30), Hr=(-21, 0, -10))}
arms = W.build_vm_arms(CV, G, J)
A.log('tris brazos', A.tris(arms.values()))
W.paint_arms(arms, os.path.join(OUT, 'texturas', 'BrazosVM_Color.png'))
vm_parts = {}
for o in partes:
    o2 = o.copy()
    o2.data = o.data
    for m in list(o2.modifiers):
        o2.modifiers.remove(m)
    o2.parent = None
    o2.location = o.location + G
    o2.name = o.name + '_VM'
    CV.objects.link(o2)
    vm_parts[o.name] = o2
bones_v = [('Camara', (0, 0, 0), None, 0.2), ('Arma', tuple(G), 'Camara', 0.25)]
bones_v += [(k, tuple(v + G), 'Arma', 0.12) for k, v in piv.items()]
for pre, side in (('Right', 'R'), ('Left', 'L')):
    j = J[side]
    bones_v += [(pre + 'UpperArm', tuple(j['S'] + G), 'Arma', 0.15), (pre + 'LowerArm', tuple(j['E'] + G), pre + 'UpperArm', 0.15),
                (pre + 'Hand', tuple(j['W'] + G), pre + 'LowerArm', 0.12)]
rig_v = A.make_armature(NOMBRE + '_VM', bones_v, CV)
A.skin_rigid(vm_parts['Armazon'], rig_v, 'Arma')
for k in ('Corredera', 'Cargador', 'Gatillo', 'Casquillo'):
    A.skin_rigid(vm_parts[k], rig_v, k)
for n, o in arms.items():
    A.skin_rigid(o, rig_v, n)
BV = [b[0] for b in bones_v]

# ------------------------------------------------------------------ CLIPS
md = lambda k: tuple(MAG_DOWN * k)
slide_back = 0.30
SLIDE_GRAB = Vector((-0.10, -0.20, 0.50))       # muneca izquierda para agarrar la corredera por detras/arriba
POLE_L = (-1, -0.3, -1)
clips = []

c = W.ClipDef('Equipar', 0.80)
c.p('Corredera', 0.40).p('Corredera', 0.48, (0, -slide_back, 0), ip='LINEAR').p('Corredera', 0.505, (0, -slide_back, 0), ip='LINEAR') \
 .p('Corredera', 0.53, ip='LINEAR').p('Corredera', 0.80)
c.v('Arma', 0.0, (0.25, -0.35, -0.95), (-55, 25, -10)).v('Arma', 0.28, (0.02, -0.02, -0.03), (4, -3, 2)) \
 .v('Arma', 0.36, (0, 0, 0), (0, 0, 0)).v('Arma', 0.48, (-0.03, 0.03, 0.0), (2, 0, 3)).v('Arma', 0.56, (0, -0.02, 0), (-1, 0, 0)) \
 .v('Arma', 0.80)
c.rest_hand('L', 0.34).hand('L', 0.42, SLIDE_GRAB, J, POLE_L).hand('L', 0.48, SLIDE_GRAB + Vector((0, -slide_back, 0)), J, POLE_L) \
 .hand('L', 0.53, SLIDE_GRAB + Vector((-0.08, -0.36, 0.10)), J, POLE_L).rest_hand('L', 0.72)
clips.append(c)

c = W.ClipDef('Disparo', 0.25)
c.p('Gatillo', 0.0).p('Gatillo', 0.016, rot=(-14, 0, 0), ip='LINEAR').p('Gatillo', 0.10, rot=(-14, 0, 0)).p('Gatillo', 0.16)
c.p('Corredera', 0.0).p('Corredera', 0.033, (0, -slide_back, 0), ip='LINEAR').p('Corredera', 0.05, (0, -slide_back, 0)) \
 .p('Corredera', 0.11).p('Corredera', 0.25)
c.p('Casquillo', 0.0).p('Casquillo', 0.033, (0.0, -0.02, 0.0), ip='LINEAR').p('Casquillo', 0.05, (0.16, -0.03, 0.10), (0, 0, -30), ip='LINEAR') \
 .p('Casquillo', 0.12, (0.45, -0.12, 0.30), (90, 0, -120), ip='LINEAR') \
 .p('Casquillo', 0.233, (0.95, -0.30, 0.36), (300, 40, -260), ip='CONSTANT').p('Casquillo', 0.25)
c.v('Arma', 0.0).v('Arma', 0.025, (0.01, -0.10, 0.025), (7.5, 1.2, -1.0)).v('Arma', 0.09, (0, -0.035, 0.01), (2.2, 0.3, -0.3)).v('Arma', 0.25)
clips.append(c)

c = W.ClipDef('Recargar', 1.70)
c.p('Cargador', 0.0).p('Cargador', 0.22).p('Cargador', 0.32, md(0.65), ip='LINEAR') \
 .p('Cargador', 0.50, tuple(MAG_DOWN * 0.65 + Vector((0, -0.10, -1.40))), (25, 0, 10), ip='CONSTANT') \
 .p('Cargador', 0.56, md(0.80)).p('Cargador', 0.88, md(0.30)).p('Cargador', 1.00, md(0.08)).p('Cargador', 1.04, ip='LINEAR').p('Cargador', 1.70)
c.p('Corredera', 0.0).p('Corredera', 1.10).p('Corredera', 1.18, (0, -slide_back, 0), ip='LINEAR').p('Corredera', 1.21, (0, -slide_back, 0), ip='LINEAR') \
 .p('Corredera', 1.24, ip='LINEAR').p('Corredera', 1.70)
RP = ((-0.18, 0.05, 0.33), (14, 22, 10))
c.v('Arma', 0.0).v('Arma', 0.18, *RP).v('Arma', 1.00, (-0.18, 0.05, 0.34), (14, 22, 10)).v('Arma', 1.05, (-0.18, 0.05, 0.37), (16, 22, 10)) \
 .v('Arma', 1.12, (-0.08, 0.03, 0.18), (6, 8, 4)).v('Arma', 1.20, (-0.05, 0.06, 0.16), (5, 6, 4)).v('Arma', 1.27, (-0.03, -0.02, 0.10), (3, 3, 2)) \
 .v('Arma', 1.70)
base_bottom = Vector((0, (-5 - GY) * s, (5 - GZ) * s)) - Vector((0, (T.x - GY) * s, (T.y - GZ) * s))   # base del cargador respecto a su pivote
mag_piv = piv['Cargador']
def hand_under_mag(k):
    return mag_piv + base_bottom + MAG_DOWN * k + Vector((-0.10, -0.14, -0.20))
c.rest_hand('L', 0.20).hand('L', 0.30, WL + Vector((-0.15, -0.20, -0.45)), J, POLE_L) \
 .hand('L', 0.50, WL + Vector((-0.10, -0.35, -1.05)), J, POLE_L).hand('L', 0.60, hand_under_mag(0.80), J, POLE_L) \
 .hand('L', 0.88, hand_under_mag(0.30), J, POLE_L).hand('L', 1.00, hand_under_mag(0.08), J, POLE_L) \
 .hand('L', 1.05, hand_under_mag(0.0) + Vector((0, 0, 0.03)), J, POLE_L) \
 .hand('L', 1.13, SLIDE_GRAB, J, POLE_L).hand('L', 1.19, SLIDE_GRAB + Vector((0, -slide_back, 0)), J, POLE_L) \
 .hand('L', 1.25, SLIDE_GRAB + Vector((-0.06, -0.38, 0.12)), J, POLE_L).rest_hand('L', 1.55)
clips.append(c)

c = W.ClipDef('Reposo', 2.0, loop=True)
c.v('Arma', 0.0).v('Arma', 0.5, (0, 0, 0.006), (0.5, 0, 0.25)).v('Arma', 1.0).v('Arma', 1.5, (0, 0, -0.006), (-0.4, 0, -0.2)).v('Arma', 2.0)
clips.append(c)

def export_rig_clips(rig, objs, acts, tag):
    """FBX con todos los clips + un FBX por clip (nombres exactos de clip)."""
    A.set_action(rig, acts['Reposo'])
    A.export_fbx(os.path.join(OUT, '%s_%s.fbx' % (NOMBRE, tag)), objs, anim=True, all_actions=True)
    for n, act in acts.items():
        A.set_action(rig, act)
        A.export_fbx(os.path.join(OUT, 'clips', '%s_%s_%s.fbx' % (NOMBRE, tag, n)), objs, anim=True)
    rig.animation_data.action = None


# 1) mundo: clips con nombre exacto, exportar y borrar (para que el FBX del viewmodel no los arrastre)
acts_w = {cd.name: cd.build(rig_w, BW, vm=False) for cd in clips}
mundo_objs = [rig_w] + partes
export_rig_clips(rig_w, mundo_objs, acts_w, 'Mundo')
for act in acts_w.values():
    bpy.data.actions.remove(act)
# 2) viewmodel
acts_v = {cd.name: cd.build(rig_v, BV, vm=True) for cd in clips}
vm_objs = [rig_v] + list(vm_parts.values()) + list(arms.values())
export_rig_clips(rig_v, vm_objs, acts_v, 'VM')
# 3) volver a crear los clips de mundo para el .blend y los renders (prefijo Mundo_)
acts_w = {}
for cd in clips:
    act = cd.build(rig_w, BW, vm=False)
    act.name = 'Mundo_' + cd.name
    acts_w[cd.name] = act
rig_w.animation_data.action = None
# estatico (sin rig): piezas separadas con su pivote, para montar con Motor6D/Weld en Studio
for o in partes:
    o.name = o.name + '_rig'
cst, st_objs = W.static_copies(partes)
for o2, o in zip(st_objs, partes):
    o2.name = {'Armazon_rig': 'Handle'}.get(o.name, o.name[:-4])
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
    '1_tres_cuartos': W.look_cam(CC, 'C1', ctr, (1.0, 0.75, 0.45), 2.4, 50),
    '2_lado_izq': W.look_cam(CC, 'C2', ctr, (-1, 0, 0), 4.0, 50, ortho=1.85),
    '3_atras_arriba': W.look_cam(CC, 'C3', ctr + Vector((0, -0.1, 0.1)), (0.35, -1.0, 0.55), 2.3, 50),
    '4_abajo_der': W.look_cam(CC, 'C4', ctr, (0.8, 0.3, -0.5), 2.4, 50),
}
for n, cam in cams.items():
    A.render(os.path.join(PV, NOMBRE + '_' + n + '.png'), cam)
# primera persona
W.hide_only({'Arma_VM', 'Camaras'})
camvm = W.vm_camera(CC)
A.render(os.path.join(PV, NOMBRE + '_5_primera_persona.png'), camvm)
# escala: maniqui R15 de 5,2 studs + regla de 6 studs, arma en la mano derecha
W.hide_only({'Ref', 'Arma_Mundo', 'Camaras'})
A.reference_figure(CR, x=0, y=0, h=5.2)
A.ruler(CR, -2.6, 0, 6)
W.backdrop(CR, 0.0)
rig_w.location = (1.5, 0.35, 1.75)
bpy.context.view_layer.update()
cs = W.look_cam(CC, 'CEsc', (0.3, 0.4, 2.6), (1.0, 0.85, 0.35), 11.5, 50)
A.render(os.path.join(PV, NOMBRE + '_6_escala_R15.png'), cs)
rig_w.location = (0, 0, 0)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ hojas de contacto de los clips
A.setup_render((480, 270), 'CYCLES', 16)
sc = bpy.context.scene
TIMES = {'Equipar': [0, 0.1, 0.2, 0.3, 0.42, 0.48, 0.53, 0.7], 'Disparo': [0, 0.016, 0.033, 0.05, 0.08, 0.12, 0.18, 0.24],
         'Recargar': [0, 0.2, 0.32, 0.5, 0.62, 0.9, 1.04, 1.13, 1.19, 1.25, 1.4, 1.65], 'Reposo': [0, 0.5, 1.0, 1.5]}
sheets = []
for n, ts in TIMES.items():
    W.hide_only({'Arma_VM', 'Camaras'})
    A.set_action(rig_v, acts_v[n])
    items = []
    for t in ts:
        sc.frame_set(int(round(t * 60)))
        p = os.path.join(PV, '_f_vm_%s_%03d.png' % (n, int(t * 1000)))
        A.render(p, camvm)
        items.append((p, '%s %.2fs' % (n, t)))
    out = os.path.join(PV, '%s_clip_VM_%s.png' % (NOMBRE, n))
    W.contact_sheet(items, 4, out, title='%s VM - %s (%.2fs)' % (NOMBRE, n, clips[[x.name for x in clips].index(n)].length))
    sheets.append(out)
    for p, _ in items:
        os.remove(p)
rig_v.animation_data.action = None
# tercera persona (solo partes): disparo y recarga vistos de lado
W.hide_only({'Arma_Mundo', 'Camaras'})
camw = W.look_cam(CC, 'CW', ctr + Vector((0, 0, -0.25)), (1.0, 0.15, 0.2), 4.2, 50)
for n in ('Disparo', 'Recargar', 'Equipar'):
    A.set_action(rig_w, acts_w[n])
    items = []
    for t in TIMES[n]:
        sc.frame_set(int(round(t * 60)))
        p = os.path.join(PV, '_f_w_%s_%03d.png' % (n, int(t * 1000)))
        A.render(p, camw)
        items.append((p, '%s %.2fs' % (n, t)))
    out = os.path.join(PV, '%s_clip_Mundo_%s.png' % (NOMBRE, n))
    W.contact_sheet(items, 4, out, title='%s mundo - %s' % (NOMBRE, n))
    for p, _ in items:
        os.remove(p)
rig_w.animation_data.action = None
sc.frame_set(0)

# ------------------------------------------------------------------ guardar .blend + datos
W.hide_only({'Arma_Mundo', 'Arma_VM', 'Ref', 'Camaras'})
A.save_blend(os.path.join(OUT, NOMBRE + '.blend'))
A.write_json(os.path.join(OUT, 'datos.json'), {
    'triangulos': TRIS, 'triangulos_total': sum(TRIS.values()), 'triangulos_brazos_vm': A.tris(arms.values()),
    'largo_studs': LARGO, 'medidas_studs': [round(v, 3) for v in (mx - mn)],
    'clips': {cd.name: {'duracion_s': cd.length, 'bucle': cd.loop, 'partes': sorted(cd.parts.keys()), 'vm_extra': sorted(cd.vm.keys())} for cd in clips},
    'viewmodel_origen_arma_desde_camara': list(G), 'exportacion': 'FBX global_scale=0.01, ejes -Z delante / Y arriba (1 unidad = 1 stud)'})
A.log('listo')
