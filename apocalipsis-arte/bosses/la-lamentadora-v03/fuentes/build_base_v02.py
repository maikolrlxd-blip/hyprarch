# Mujer zombi REALISTA (proporciones humanas tipo Rthro) con esqueleto y piezas R15 para Roblox.
# Pedido de Maikol (2026-10-22 noche): "que el zombie sea mujer" y "vete por lo realista". Sin gore: moretones, rasguños, ropa rota.
# blender -b --factory-startup -P build_zombi.py        (QUICK=1 salta las hojas de contacto de los clips)
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import importlib
import ap_lib as A
import ap_armas as W
importlib.reload(A); importlib.reload(W)
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler

# Variantes sobre la misma base (piezas R15, rig y clips): la mujer zombi y los dos jefes de Luto (sin gore).
# ZOMBI_VARIANTE=lamentadora|alta  ->  escala total, brazos mas largos, ropa de luto y cara propia.
VARIANTE = os.environ.get('ZOMBI_VARIANTE', 'mujer')
VAR = {
    'mujer': dict(nombre='ZombiMujer', out='zombi-mujer', plantilla='Zombi_Mujer', escala=1.0, brazo=1.0, piel=(0.66, 0.68, 0.58),
                  vestido='#7d8ea2', pelo='#2e231d', floral=True, boca=1.0, huecos=False),
    # La Lamentadora: larga y deformada, de luto, con la boca abierta en un lamento y los ojos hundidos y oscuros
    'lamentadora': dict(nombre='LaLamentadora', out=os.path.join('bosses', 'la-lamentadora-v02'), plantilla='Jefe_lamentadora',
                        escala=1.75, brazo=1.35, piel=(0.72, 0.73, 0.70), vestido='#2c282b', pelo='#141113', floral=False, boca=1.9,
                        huecos=True),
    # La Alta: muy alta y delgada, vestido gris apagado, brazos largos
    'alta': dict(nombre='JefeAlta', out=os.path.join('bosses', 'jefe-alta-v01'), plantilla='Jefe_alta', escala=2.0, brazo=1.25,
                 piel=(0.63, 0.64, 0.57), vestido='#6f6a66', pelo='#3a2c22', floral=False, boca=1.3, huecos=False),
}[VARIANTE]
ESC = VAR['escala']
NOMBRE = VAR['nombre']
QUICK = os.environ.get('QUICK') == '1'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, VAR['out'])
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

A.clean_scene()
A.REGIONS.clear()
A.NRM_SMOOTH = True
CM = A.collection('Zombi')
rng = np.random.default_rng(23)
TAU = 2 * math.pi


# ------------------------------------------------------------------ constructores organicos
def ring(rx, ry, n=12, yc=0.0, off=0.0, mod=None):
    pts = []
    for k in range(n):
        th = off + TAU * k / n
        x, y = rx * math.cos(th), ry * math.sin(th) + yc
        if mod:
            x, y = mod(x, y, th)
        pts.append((x, y))
    return pts


def limb(mb, centers, secs, mat, n=8, fwd=(0, 1, 0), cap0=True, cap1=True, jag=None):
    """Loft a lo largo de una polilinea 3D. secs[i] = (rx, ry) o lista de n puntos (u, v) en el plano (lado, delante).
    jag: (amplitud, semilla) para dejar el ultimo anillo rasgado (ropa)."""
    C = [Vector(c) for c in centers]
    rings = []
    for i, c in enumerate(C):
        if i == 0:
            t = (C[1] - C[0]).normalized()
        elif i == len(C) - 1:
            t = (C[-1] - C[-2]).normalized()
        else:
            t = (C[i + 1] - C[i - 1]).normalized()
        f = Vector(fwd)
        f = (f - t * f.dot(t)).normalized()
        sd = f.cross(t)
        sec = secs[i]
        pts = ring(sec[0], sec[1], n) if isinstance(sec, tuple) else sec
        rr = []
        for j, (u, v) in enumerate(pts):
            p = c + sd * u + f * v
            if jag and i == len(C) - 1:
                a, sd_ = jag
                k = 1.0 if j % 2 == 0 else 0.35
                p = p + t * (a * k * (0.6 + 0.8 * np.random.default_rng(sd_ + j).random()))
            rr.append(mb.bm.verts.new(p))
        rings.append(rr)
    faces = []
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(n):
            faces.append(mb.face((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]), mat))
    if cap0:
        faces.append(mb.face(rings[0][::-1], mat))
    if cap1 and not jag:
        faces.append(mb.face(rings[-1], mat))
    return faces


def paint_faces(faces, mb, fn):
    """Reasigna la region de cada cara segun su centro y normal (para cara/pelo/ropa dentro de una pieza)."""
    for f in faces:
        c = f.calc_center_median()
        f.normal_update()
        r = fn(c, f.normal)
        if r:
            f.material_index = mb.mi(r)


parts = {}

# ------------------------------------------------------------------ CABEZA (craneo + cara + pelo largo)
mb = A.MB('Head')


def face_mod_factory(level):
    def mod(x, y, th):
        a = (th % TAU)
        front = math.sin(th)                       # 1 delante
        cx = math.cos(th)
        if level == 'nose' and abs(cx) < 0.01 and front > 0.9:
            y += 0.075                              # punta de la nariz
        if level == 'eyes':
            if abs(cx) < 0.01 and front > 0.9:
                y += 0.035                          # puente de la nariz
            elif front > 0.6:
                y -= 0.020                          # cuencas
        if level == 'brow' and front > 0.6:
            y += 0.008
        if level == 'mouth' and abs(cx) < 0.01 and front > 0.9:
            y += 0.020                              # labios
        if level == 'chin' and front > 0.6:
            y += 0.02
        return x, y
    return mod


HEAD = [  # (z, rx, ry, yc, nivel)
    (4.86, 0.10, 0.08, 0.15, 'chin'), (4.94, 0.20, 0.19, 0.08, 'jaw'), (5.03, 0.255, 0.255, 0.04, 'mouth'),
    (5.12, 0.275, 0.285, 0.03, 'nose'), (5.22, 0.285, 0.300, 0.01, 'eyes'), (5.32, 0.292, 0.308, 0.00, 'brow'),
    (5.45, 0.280, 0.300, -0.01, 'fore'), (5.56, 0.215, 0.240, -0.02, 'crown'), (5.63, 0.10, 0.12, -0.02, 'top')]
centers = [(0, 0, z) for (z, *_r) in HEAD]
secs = [ring(rx, ry, 12, yc, 0.0, face_mod_factory(lv)) for (z, rx, ry, yc, lv) in HEAD]
fs = limb(mb, centers, secs, 'piel', n=12, fwd=(0, 1, 0))


def head_region(c, nrm):
    if c.y > 0.05 and 4.84 < c.z < 5.42 and nrm.y > 0.15:
        return 'cara'
    return 'piel'


paint_faces(fs, mb, head_region)
# pelo: casquete sobre el craneo (deja libre la frente baja), melena larga por detras y mechones delanteros
def hair_mod(cut_y):
    def mod(x, y, th):
        if math.sin(th) > 0.35:
            y = min(y, cut_y)
        return x, y
    return mod


HAIR = [(5.71, 0.13, 0.15, -0.02, 1.0), (5.64, 0.255, 0.28, -0.02, 1.0), (5.50, 0.32, 0.34, -0.02, 0.30), (5.36, 0.335, 0.35, -0.02, 0.17),
        (5.18, 0.35, 0.345, -0.05, 0.02), (4.95, 0.37, 0.31, -0.11, -0.04), (4.62, 0.42, 0.20, -0.20, -0.10), (4.25, 0.45, 0.15, -0.27, -0.18),
        (3.90, 0.44, 0.13, -0.31, -0.22), (3.62, 0.40, 0.11, -0.33, -0.24)]
hc = [(0, 0, z) for (z, *_r) in HAIR]
hs = [ring(rx, ry, 16, yc, 0.0, hair_mod(cut)) for (z, rx, ry, yc, cut) in HAIR]
fh = limb(mb, hc, hs, 'pelo', n=16, fwd=(0, 1, 0), cap0=True, cap1=False, jag=(0.26, 77))   # v4: 16 lados (con 12 parecia un casco)
# mechones que caen delante de los hombros (enmarcan la cara); v4: seccion mas redonda, en v3 parecian tablas
for sx in (-1, 1):
    limb(mb, [(sx * 0.29, 0.06, 5.30), (sx * 0.34, 0.14, 4.95), (sx * 0.37, 0.24, 4.62), (sx * 0.36, 0.30, 4.36)],
         [(0.085, 0.072), (0.088, 0.074), (0.075, 0.064), (0.035, 0.03)], 'pelo', n=7, fwd=(0, 1, 0))
    limb(mb, [(sx * 0.33, -0.08, 5.20), (sx * 0.40, -0.06, 4.80), (sx * 0.44, -0.03, 4.45), (sx * 0.45, 0.0, 4.15)],
         [(0.08, 0.072), (0.082, 0.072), (0.072, 0.062), (0.03, 0.028)], 'pelo', n=7, fwd=(0, 1, 0))
    limb(mb, [(sx * 0.18, 0.27, 5.42), (sx * 0.24, 0.29, 5.30), (sx * 0.27, 0.27, 5.16)], [(0.06, 0.02), (0.05, 0.02), (0.02, 0.015)],
         'pelo', n=5, fwd=(0, 1, 0))
parts['Head'] = mb.finish(CM)

# ------------------------------------------------------------------ TORSO SUPERIOR (pecho, hombros, cuello) con vestido de tirantes
mb = A.MB('UpperTorso')


def bust(x, y, th):
    if y > 0:
        for bx in (-0.20, 0.20):
            y += 0.085 * math.exp(-((x - bx) / 0.15) ** 2)
    return x, y


TORSO_U = [(3.48, 0.43, 0.30, 0.0, None), (3.78, 0.48, 0.31, 0.01, None), (4.02, 0.53, 0.33, 0.02, bust), (4.22, 0.58, 0.33, 0.01, None),
           (4.40, 0.60, 0.29, 0.0, None), (4.54, 0.40, 0.22, -0.01, None), (4.66, 0.19, 0.16, 0.0, None)]
fu = limb(mb, [(0, 0, z) for (z, *_r) in TORSO_U], [ring(rx, ry, 12, yc, 0.0, m) for (z, rx, ry, yc, m) in TORSO_U], 'vestido', n=12)
limb(mb, [(0, 0.0, 4.62), (0, 0.01, 4.80), (0, 0.02, 4.92)], [(0.15, 0.14), (0.14, 0.13), (0.13, 0.12)], 'piel', n=8)   # cuello


def top_region(c, nrm):
    # piel en hombros y escote; vestido de tirantes en el resto
    if c.z > 4.30 and abs(c.x) > 0.22 and not (0.30 < abs(c.x) < 0.40 and c.z < 4.62):
        return 'piel'
    if c.z > 4.18 and c.y > 0.10 and abs(c.x) < 0.30:
        return 'piel'
    return 'vestido'


paint_faces(fu, mb, top_region)
parts['UpperTorso'] = mb.finish(CM)

# ------------------------------------------------------------------ TORSO INFERIOR (cadera) + falda del vestido rasgada
mb = A.MB('LowerTorso')


def hips(x, y, th):
    if y < 0:
        y -= 0.05 * math.exp(-((abs(x) - 0.22) / 0.2) ** 2)   # gluteos
    return x, y


TORSO_L = [(2.66, 0.46, 0.27, 0.0, None), (2.84, 0.60, 0.35, 0.0, hips), (3.05, 0.62, 0.36, 0.0, hips), (3.30, 0.52, 0.32, 0.0, None),
           (3.53, 0.44, 0.30, 0.0, None)]
limb(mb, [(0, 0, z) for (z, *_r) in TORSO_L], [ring(rx, ry, 12, yc, 0.0, m) for (z, rx, ry, yc, m) in TORSO_L], 'vestido', n=12)
SK = [(3.50, 0.46, 0.32), (3.05, 0.66, 0.40), (2.62, 0.76, 0.50), (2.14, 0.84, 0.58)]
limb(mb, [(0, 0.02, z) for (z, *_r) in SK], [(rx, ry) for (z, rx, ry) in SK], 'vestido', n=16,
     cap0=False, cap1=False, jag=(0.32, 41))
parts['LowerTorso'] = mb.finish(CM)

# ------------------------------------------------------------------ BRAZOS (en A, 12 grados)
ARM = {}
for side, sx in (('Left', -1), ('Right', 1)):
    sh, el, wr, ft = Vector((sx * 0.64, 0.0, 4.40)), Vector((sx * 0.79, -0.04, 3.52)), Vector((sx * 0.87, 0.02, 2.74)), Vector((sx * 0.91, 0.07, 2.16))
    el, wr, ft = (sh + (p - sh) * VAR['brazo'] for p in (el, wr, ft))          # jefes: brazos mas largos
    ARM[side] = (sh, el, wr, ft)
    mb = A.MB(side + 'UpperArm')
    # v4: brazos un 15 % mas gruesos (en v3 parecian de maniqui a la escala de Roblox)
    limb(mb, [sh + Vector((-sx * 0.10, 0, 0.04)), sh - Vector((0, 0, 0.06)), sh.lerp(el, 0.45), el - (el - sh).normalized() * 0.02], [(0.15, 0.15), (0.19, 0.185), (0.16, 0.16), (0.138, 0.138)], 'piel', n=8)
    parts[side + 'UpperArm'] = mb.finish(CM)
    mb = A.MB(side + 'LowerArm')
    limb(mb, [el + (el - wr).normalized() * 0.12, el.lerp(wr, 0.25), wr + (wr - el).normalized() * 0.04], [(0.12, 0.12), (0.145, 0.133), (0.092, 0.072)], 'piel', n=8)
    parts[side + 'LowerArm'] = mb.finish(CM)
    mb = A.MB(side + 'Hand')
    kn = wr.lerp(ft, 0.45)
    limb(mb, [wr + (wr - ft).normalized() * 0.08, wr.lerp(ft, 0.2), kn], [(0.065, 0.045), (0.09, 0.037), (0.085, 0.03)], 'piel', n=6,
         fwd=(-sx, 0, 0))
    tip = ft + Vector((0, 0.07, 0.04))
    limb(mb, [kn, kn.lerp(tip, 0.5) + Vector((0, 0.03, 0)), tip], [(0.08, 0.025), (0.072, 0.024), (0.06, 0.018)], 'piel', n=6, fwd=(-sx, 0, 0))
    th0 = wr.lerp(ft, 0.25) + Vector((-sx * 0.06, 0.05, 0))
    limb(mb, [th0, th0 + Vector((-sx * 0.02, 0.08, -0.10)), th0 + Vector((-sx * 0.02, 0.12, -0.20))], [(0.03, 0.025), (0.028, 0.022), (0.02, 0.016)],
         'piel', n=5, fwd=(-sx, 0, 0))
    parts[side + 'Hand'] = mb.finish(CM)

# ------------------------------------------------------------------ PIERNAS (pie izquierdo descalzo, derecho con zapato plano)
LEG = {}
for side, sx in (('Left', -1), ('Right', 1)):
    hip, kn, an = Vector((sx * 0.31, 0.0, 2.92)), Vector((sx * 0.25, 0.02, 1.62)), Vector((sx * 0.23, -0.02, 0.30))
    LEG[side] = (hip, kn, an)
    mb = A.MB(side + 'UpperLeg')
    limb(mb, [hip + Vector((0, 0, 0.12)), hip, hip.lerp(kn, 0.45), kn - Vector((0, 0, 0.04))], [(0.27, 0.28), (0.30, 0.31), (0.24, 0.25), (0.185, 0.185)], 'piel', n=10)
    parts[side + 'UpperLeg'] = mb.finish(CM)
    mb = A.MB(side + 'LowerLeg')
    limb(mb, [kn + Vector((0, 0, 0.14)), kn.lerp(an, 0.30) + Vector((0, -0.03, 0)), an], [(0.165, 0.165), (0.20, 0.22), (0.115, 0.125)], 'piel', n=10)
    parts[side + 'LowerLeg'] = mb.finish(CM)
    mb = A.MB(side + 'Foot')
    shoe = (side == 'Right')
    fm = 'zapato' if shoe else 'piel'
    k = 1.06 if shoe else 1.0
    limb(mb, [Vector((an.x, -0.14, 0.10)), Vector((an.x, 0.0, 0.14)), Vector((an.x + sx * 0.01, 0.22, 0.08)), Vector((an.x + sx * 0.02, 0.50, 0.05))],
         [(0.10 * k, 0.10 * k), (0.11 * k, 0.13 * k), (0.14 * k, 0.07 * k), (0.12 * k, 0.045 * k)], fm, n=8, fwd=(0, 0, 1))
    parts[side + 'Foot'] = mb.finish(CM)

ORDER = ['LowerTorso', 'UpperTorso', 'Head', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand', 'RightUpperArm', 'RightLowerArm',
         'RightHand', 'LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot']
objs = [parts[n] for n in ORDER]
for o in objs:                       # sombreado suave en la piel organica (las aristas del vestido roto siguen marcadas por la textura)
    for p in o.data.polygons:
        p.use_smooth = True
TRIS = {n: A.tris([parts[n]]) for n in ORDER}
A.log('triangulos', TRIS, 'total', sum(TRIS.values()))

# ------------------------------------------------------------------ pintura realista (sin gore)
smooth = A.smoothstep
SKIN = np.array(VAR['piel'], np.float32)                  # palido gris verdoso (cada variante el suyo)
MOUTH, HOLLOW = VAR['boca'], VAR['huecos']
BRUISE = np.array([0.36, 0.26, 0.34], np.float32)
VEIN = np.array([0.33, 0.38, 0.40], np.float32)
DIRT = np.array([0.33, 0.27, 0.20], np.float32)


def ell(u, v, cx, cy, rx, ry):
    return ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2


def segdist(u, v, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    t = np.clip(((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(u - (ax + t * dx), v - (ay + t * dy)), t


def skin_x(P, msk, pos, nrm, col):
    # moteado palido, venas apenas visibles en zonas, moretones, suciedad abajo y rasgunos (sin sangre)
    mot = A.fbm(pos * 9.0, 3, 501)
    col *= (0.94 + 0.12 * mot)[:, None]
    patch = smooth(0.60, 0.75, A.fbm(pos * 1.6 + 5.0, 2, 503))
    vn = A.fbm(pos * 7.0 + 3.0, 3, 505)
    vein = (np.abs(vn - 0.5) < 0.006) & (patch > 0.4)
    col[vein] = col[vein] * 0.80 + VEIN * 0.20
    br = smooth(0.64, 0.82, A.fbm(pos * 2.4 + 11.0, 3, 507))
    col = col * (1 - 0.5 * br[:, None]) + BRUISE * (0.5 * br)[:, None]
    low = smooth(1.3, 0.2, pos[:, 2]) * smooth(0.40, 0.75, A.fbm(pos * 3.0 + 2.0, 3, 509))
    col = col * (1 - 0.55 * low[:, None]) + DIRT * (0.55 * low)[:, None]
    hand = (pos[:, 2] < 2.75) & (pos[:, 2] > 1.9) & (np.abs(pos[:, 0]) > 0.7)
    hd = hand * smooth(0.45, 0.7, A.fbm(pos * 6.0, 2, 511))
    col = col * (1 - 0.4 * hd[:, None]) + DIRT * (0.4 * hd)[:, None]
    # zarpazos: tres rayas paralelas de distinto largo (en v3 parecian chevrones), marron oscuro con borde rosado apagado
    def claws(c0, d, sep=0.026, lens=(0.16, 0.19, 0.14)):
        d = np.array(d, np.float32) / np.linalg.norm(d)
        pp = np.array([-d[1], d[0]], np.float32)
        out = []
        for i, ln in enumerate(lens):
            o = (i - (len(lens) - 1) / 2) * sep
            a = (c0[0] + pp[0] * o, c0[1] + pp[1] * o)
            out.append((a, (a[0] + d[0] * ln, a[1] + d[1] * ln)))
        return out
    # v5: sin zarpazos en el antebrazo (sobre el cilindro se leian como chevrones); solo en el muslo
    SCR = (((-0.27, 0.0), claws((0.20, 2.44), (0.07, -0.15), lens=(0.14, 0.17, 0.12))),)
    for (cx, cz), lines in SCR:
        side = (np.sign(pos[:, 0]) == np.sign(cx)) & (np.abs(pos[:, 0] - cx) < 0.25) & (nrm[:, 1] > 0.0)
        for (a, b) in lines:
            d, _ = segdist(pos[:, 1], pos[:, 2], (a[0], cz + a[1]), (b[0], cz + b[1]))
            m = side & (d < 0.006)
            col[m] = col[m] * 0.35 + np.array([0.30, 0.18, 0.16], np.float32) * 0.65
            m2 = side & (d >= 0.006) & (d < 0.016)
            col[m2] = col[m2] * 0.90 + np.array([0.55, 0.36, 0.36], np.float32) * 0.10
    nails = (pos[:, 2] < 2.30) & (np.abs(pos[:, 0]) > 0.8)
    col[nails] = col[nails] * 0.80 + np.array([0.25, 0.20, 0.26], np.float32) * 0.20
    return col


def face_x(P, msk, pos, nrm, col):
    col = skin_x(P, msk, pos, nrm, col)
    u, v = pos[:, 0], pos[:, 2]
    fr = nrm[:, 1] > 0.15
    for sx in (-1, 1):
        # cuencas hundidas y ojeras (suaves)
        e = ell(u, v, sx * 0.105, 5.212, 0.095, 0.060)
        so = fr & (e < 1.8)
        k = smooth(1.8, 0.3, e[so])[:, None]
        col[so] = col[so] * (1 - 0.50 * k) + np.array([0.34, 0.27, 0.32], np.float32) * (0.50 * k)
        ck = fr & (ell(u, v, sx * 0.17, 5.07, 0.09, 0.07) < 1)
        col[ck] = col[ck] * 0.88
        # v4, cara de angustia (Luto): ojo abierto y nublado, parpado inferior enrojecido, mirada perdida
        ex = (u - sx * 0.105) / 0.054
        ey = (v - 5.214) / 0.026
        shape = ex ** 2 + (ey / (1.0 - 0.30 * np.abs(ex))) ** 2
        eye = fr & (shape < 1) & (ey < 0.70)
        col[eye] = np.array([0.72, 0.70, 0.60], np.float32)
        ir = eye & (ell(u, v, sx * 0.100, 5.216, 0.020, 0.020) < 1)
        col[ir] = np.array([0.64, 0.68, 0.69], np.float32)
        ring_ = ir & (ell(u, v, sx * 0.100, 5.216, 0.020, 0.020) > 0.55)
        col[ring_] = np.array([0.48, 0.52, 0.54], np.float32)
        pu = eye & (ell(u, v, sx * 0.100, 5.216, 0.006, 0.006) < 1)
        col[pu] = np.array([0.42, 0.44, 0.46], np.float32)
        if HOLLOW:                                                   # jefe: ojos hundidos y oscuros con un brillo apagado
            col[eye] = np.array([0.07, 0.06, 0.07], np.float32)
            col[pu] = np.array([0.55, 0.57, 0.56], np.float32)
        rim = fr & (shape < 1.40) & ~eye
        col[rim] = col[rim] * 0.62 + np.array([0.52, 0.26, 0.27], np.float32) * 0.38
        lid = fr & (shape < 1.30) & (ey >= 0.70) & (ey < 0.95)
        col[lid] = col[lid] * 0.45 + np.array([0.14, 0.11, 0.11], np.float32) * 0.55
        lash = fr & (np.abs(ey - 0.78) < 0.09) & (np.abs(ex) < 0.95)
        col[lash] = col[lash] * 0.35 + np.array([0.08, 0.06, 0.06], np.float32) * 0.65
        # cejas de angustia: el extremo interior sube (antes estaban rectas y la cara no expresaba nada)
        d, t = segdist(u, v, (sx * 0.040, 5.298), (sx * 0.178, 5.272))
        bm = fr & (d < 0.0095 * (1.0 - 0.5 * t)) & (np.abs(u) > 0.03)
        col[bm] = col[bm] * 0.40 + np.array([0.20, 0.15, 0.12], np.float32) * 0.60
    # nariz: sombra lateral y fosas
    for sx in (-1, 1):
        col[fr & (ell(u, v, sx * 0.022, 5.088, 0.011, 0.007) < 1)] = np.array([0.22, 0.17, 0.17], np.float32)
        ns = fr & (np.abs(u - sx * 0.03) < 0.010) & (v > 5.10) & (v < 5.20)
        col[ns] = col[ns] * 0.88
    # arrugas de preocupacion en la frente y surcos de la nariz a la boca
    for k in (0, 1):
        fw = fr & (np.abs(v - (5.318 + 0.016 * k) - 0.012 * np.cos(u / 0.09)) < 0.0035) & (np.abs(u) < 0.075 - 0.015 * k)
        col[fw] = col[fw] * 0.88                                     # v5: mas suaves (en v4 parecian trazos dibujados)
    for sx in (-1, 1):
        d, _ = segdist(u, v, (sx * 0.040, 5.100), (sx * 0.072, 5.030))
        sk = fr & (d < 0.007)
        col[sk] = col[sk] * (0.86 + 0.14 * (d[sk] / 0.007))[:, None]
    # boca abierta en un gemido: labios palidos, hueco oscuro y la fila de dientes de arriba (sin sangre)
    # MOUTH > 1 (jefes): boca mas abierta hacia abajo, en un lamento
    mz = 5.030 - 0.010 * (MOUTH - 1.0)
    le = ell(u, v, 0.0, mz, 0.064 * min(MOUTH, 1.25), 0.034 * MOUTH)
    lips = fr & (le < 1)
    col[lips] = col[lips] * (0.55 + 0.25 * le[lips])[:, None] + np.array([0.40, 0.31, 0.33], np.float32) * (0.45 - 0.25 * le[lips])[:, None]
    gap = fr & (ell(u, v, 0.0, mz - 0.002, 0.045 * min(MOUTH, 1.2), 0.019 * MOUTH) < 1)
    col[gap] = np.array([0.10, 0.06, 0.07], np.float32)
    ttop = mz + 0.006 + 0.019 * (MOUTH - 1.0)
    teeth = gap & (v > ttop) & (v < ttop + 0.007) & (np.abs(u) < 0.034) & ((np.abs(u) % 0.0105) > 0.0012)
    col[teeth] = np.array([0.66, 0.62, 0.50], np.float32)
    # dos rasgunos cortos en la mejilla y moreton en la sien
    for (a, b) in (((0.19, 5.15), (0.13, 5.06)), ((0.21, 5.12), (0.16, 5.05))):
        d, _ = segdist(u, v, a, b)
        m = fr & (d < 0.0035)
        col[m] = col[m] * 0.4 + np.array([0.32, 0.18, 0.17], np.float32) * 0.6
    tb = fr & (ell(u, v, -0.24, 5.30, 0.07, 0.09) < 1)
    col[tb] = col[tb] * 0.65 + BRUISE * 0.35
    return col


def hair_x(P, msk, pos, nrm, col):
    # mechones finos verticales con brillos tenues (sin manchas anaranjadas)
    s = A.vnoise(np.stack([pos[:, 0] * 55.0, pos[:, 1] * 55.0, pos[:, 2] * 2.5], 1), 33)
    col = col * (0.72 + 0.40 * s)[:, None]
    hl = A.vnoise(np.stack([pos[:, 0] * 35.0, pos[:, 1] * 35.0, pos[:, 2] * 1.5], 1), 35) > 0.80
    col[hl] = col[hl] * 0.75 + np.array([0.36, 0.27, 0.20], np.float32) * 0.25
    knot = smooth(0.66, 0.76, A.fbm(pos * 6.0, 2, 37))
    col = col * (1 - 0.25 * knot[:, None])
    return col


def dress_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    # estampado floral pequeno y desvaido
    q = np.stack([x * 14.0, y * 14.0, z * 14.0], 1)
    fl = A.vnoise(q, 601)
    if VAR['floral']:                                              # los jefes visten de luto liso
        flower = (fl > 0.80)
        col[flower] = col[flower] * 0.55 + np.array([0.85, 0.80, 0.70], np.float32) * 0.45
        cen = (fl > 0.88)
        col[cen] = col[cen] * 0.5 + np.array([0.72, 0.45, 0.42], np.float32) * 0.5
    # pliegues verticales pintados
    fold = 0.5 + 0.5 * np.sin(np.arctan2(y, x) * 9.0 + A.fbm(pos * 3.0, 2, 603) * 4.0)
    col *= (0.86 + 0.18 * fold)[:, None]
    # manchas de tierra/humedad (no sangre) y agujeros oscuros
    st = smooth(0.58, 0.76, A.fbm(pos * 2.0 + 7.0, 3, 605))
    col = col * (1 - 0.5 * st[:, None]) + np.array([0.30, 0.26, 0.20], np.float32) * (0.5 * st)[:, None]
    hole = smooth(0.70, 0.72, A.fbm(pos * 3.5 + 1.0, 3, 607)) > 0.5
    col[hole] = SKIN * 0.55
    # tirantes y escote
    return col


P_STYLE = {
    'piel': dict(base=SKIN, var=0.05, stroke=(1, 1, 1), stroke_scale=6, blotch=0.06, ao=0.62, ao_tint='#2a2230', light=0.22, face_var=0.0,
                 edge_col='#c4c7b5', edge=0.25, grime=0.18, grime_col='#4a4237', hue_var=0.02, seed=2, extra=skin_x),
    'cara': dict(base=SKIN, var=0.04, stroke=(1, 1, 1), stroke_scale=8, blotch=0.05, ao=0.55, ao_tint='#2a2230', light=0.22, face_var=0.0,
                 edge_col='#c4c7b5', edge=0.15, grime=0.10, grime_col='#4a4237', hue_var=0.02, seed=3, extra=face_x),
    'pelo': dict(base=VAR['pelo'], var=0.10, stroke=(1, 1, 8), stroke_scale=10, blotch=0.10, ao=0.60, ao_tint='#0a0707', light=0.30,
                 edge_col='#5c4637', edge=0.5, grime=0.20, dust=0.12, dust_col='#6a5a4c', face_var=0.0, seed=9, extra=hair_x),
    'vestido': dict(base=VAR['vestido'], var=0.08, stroke=(1, 1, 5), stroke_scale=7, blotch=0.12, ao=0.62, ao_tint='#141820', light=0.26,
                    edge_col='#b9c3cd', edge=0.6, edge_th=0.04, grime=0.40, grime_col='#3a3128', dust=0.12, face_var=0.0, seed=5, extra=dress_x),
    'zapato': dict(base='#252322', var=0.08, stroke=(1, 1, 1), stroke_scale=8, ao=0.55, edge_col='#5a5550', edge=0.6, grime=0.35,
                   grime_col='#3d342a', dust=0.2, face_var=0.0, seed=13),
}
GROUPS = {'Cabeza': ['Head'], 'Torso': ['UpperTorso', 'LowerTorso'],
          'Brazos': ['LeftUpperArm', 'LeftLowerArm', 'LeftHand', 'RightUpperArm', 'RightLowerArm', 'RightHand'],
          'Piernas': ['LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot']}
ref = bpy.data.objects.new('RefPos', None)
CM.objects.link(ref)
R = 6.0
TEXS = {}
for g, names in GROUPS.items():
    gobjs = [parts[n] for n in names]
    A.uv_unwrap(gobjs, angle=60, margin=0.004)
    maps = A.bake_maps(gobjs, 2048, R=R, ao_dist=0.18, bevel_r=0.015, samples=20, pos_ref=ref)
    P = A.Paint(maps, R=R, light=(-0.25, 0.55, 0.80))
    for reg in sorted(set(r for o in gobjs for r in [s.material.name[2:] for s in o.material_slots])):
        st = dict(P_STYLE[reg])
        base = st.pop('base')
        P.region(reg, base, **st)
    tex = os.path.join(OUT, 'texturas', '%s_%s_Color.png' % (NOMBRE, g))
    P.save(tex, 1024)
    mat = A.final_material('M_%s_%s' % (NOMBRE, g), tex)
    A.assign_final(gobjs, mat)
    for o in gobjs:
        for p in o.data.polygons:
            p.use_smooth = True
    TEXS[g] = os.path.basename(tex)
bpy.data.objects.remove(ref, do_unlink=True)
if ESC != 1.0:                       # jefes: se pinta a tamano normal (la pintura usa posiciones) y se escala despues
    for o in parts.values():
        o.data.transform(Matrix.Scale(ESC, 4))
        o.location = o.location * ESC

# ------------------------------------------------------------------ RIG (huesos con nombres R15)
J = {'HumanoidRootPart': (0, 0, 2.95), 'LowerTorso': (0, 0, 2.95), 'UpperTorso': (0, 0, 3.50), 'Head': (0, 0.02, 4.90),
     'LeftUpperArm': tuple(ARM['Left'][0]), 'LeftLowerArm': tuple(ARM['Left'][1]), 'LeftHand': tuple(ARM['Left'][2]),
     'RightUpperArm': tuple(ARM['Right'][0]), 'RightLowerArm': tuple(ARM['Right'][1]), 'RightHand': tuple(ARM['Right'][2]),
     'LeftUpperLeg': tuple(LEG['Left'][0]), 'LeftLowerLeg': tuple(LEG['Left'][1]), 'LeftFoot': tuple(LEG['Left'][2]),
     'RightUpperLeg': tuple(LEG['Right'][0]), 'RightLowerLeg': tuple(LEG['Right'][1]), 'RightFoot': tuple(LEG['Right'][2])}
J = {k: tuple(v * ESC for v in p) for k, p in J.items()}
PAR = {'HumanoidRootPart': None, 'LowerTorso': 'HumanoidRootPart', 'UpperTorso': 'LowerTorso', 'Head': 'UpperTorso',
       'LeftUpperArm': 'UpperTorso', 'LeftLowerArm': 'LeftUpperArm', 'LeftHand': 'LeftLowerArm',
       'RightUpperArm': 'UpperTorso', 'RightLowerArm': 'RightUpperArm', 'RightHand': 'RightLowerArm',
       'LeftUpperLeg': 'LowerTorso', 'LeftLowerLeg': 'LeftUpperLeg', 'LeftFoot': 'LeftLowerLeg',
       'RightUpperLeg': 'LowerTorso', 'RightLowerLeg': 'RightUpperLeg', 'RightFoot': 'RightLowerLeg'}
BONES = [(n, J[n], PAR[n], 0.2) for n in ['HumanoidRootPart'] + ORDER]
rig = A.make_armature(NOMBRE, BONES, CM)
for n in ORDER:
    A.skin_rigid(parts[n], rig, n)
BN = [b[0] for b in BONES]


# ------------------------------------------------------------------ CLIPS (angulos en grados, ejes del armature: X = cabeceo, Y = alabeo, Z = giro)
def cyc(t, ph=0.0, amp=1.0):
    return amp * math.cos(TAU * (t + ph))


class Pose:
    def __init__(self, name, length, loop=False):
        self.c = A.Clip(rig, name, length, loop)
        self.name, self.length, self.loop = name, length, loop

    def k(self, bone, t, rot=(0, 0, 0), loc=(0, 0, 0), ip='BEZIER'):
        self.c.k(bone, t, tuple(v * ESC for v in loc), rot, ip)          # los desplazamientos crecen con el tamano
        return self

    def build(self):
        return self.c.build(BN)


clips = []
# Reposo: encorvada, cabeza caida hacia un lado, brazos colgando con leve balanceo (bucle 2 s)
c = Pose('Reposo', 2.0, True)
for t in (0.0, 0.5, 1.0, 1.5, 2.0):
    ph = t / 2.0
    c.k('UpperTorso', t, (-9 + 1.5 * cyc(ph), 0, 3 * cyc(ph, 0.25)))
    c.k('Head', t, (-12 + 2.0 * cyc(ph, 0.1), 14 + 3 * cyc(ph, 0.3), 4 * cyc(ph, 0.5)))
    c.k('LowerTorso', t, (0, 2, 0), (0, 0, 0.015 * cyc(ph * 2)))
    c.k('LeftUpperArm', t, (10 + 3 * cyc(ph, 0.2), -4, 0)).k('RightUpperArm', t, (14 + 3 * cyc(ph, 0.7), 4, 0))
    c.k('LeftLowerArm', t, (10 + 2 * cyc(ph, 0.4), 0, 0)).k('RightLowerArm', t, (16 + 2 * cyc(ph, 0.9), 0, 0))
    c.k('LeftHand', t, (-8, 0, 0)).k('RightHand', t, (-12, 0, 0))
    c.k('LeftUpperLeg', t, (-2, 0, 0)).k('RightUpperLeg', t, (4, 0, 2)).k('RightLowerLeg', t, (-6, 0, 0))
clips.append(c)

# Caminar: zancada arrastrada (pie derecho arrastra), brazos medio levantados, torso torcido (bucle 1.1 s)
c = Pose('Caminar', 1.1, True)
for t in (0.0, 0.275, 0.55, 0.825, 1.1):
    ph = t / 1.1
    ul = 22 * cyc(ph)
    ur = -0.7 * ul
    knee_l = -34 * max(0.0, -math.sin(TAU * ph)) - 4
    knee_r = -20 * max(0.0, math.sin(TAU * ph)) - 8
    c.k('LeftUpperLeg', t, (ul, 0, 0)).k('RightUpperLeg', t, (ur, 0, 3))
    c.k('LeftLowerLeg', t, (knee_l, 0, 0)).k('RightLowerLeg', t, (knee_r, 0, 0))
    c.k('LeftFoot', t, (-0.6 * (ul + knee_l), 0, 0)).k('RightFoot', t, (-0.5 * (ur + knee_r) + 10, 0, 0))
    c.k('LowerTorso', t, (2, 0, 7 * cyc(ph, 0.25)), (0, 0, 0.06 * abs(cyc(ph)) - 0.04))
    c.k('UpperTorso', t, (-13, 3 * cyc(ph, 0.25), -9 * cyc(ph, 0.25)))
    c.k('Head', t, (-10 + 2 * cyc(ph * 2), 12 * cyc(ph, 0.1) + 6, 7 * cyc(ph, 0.25)))
    c.k('LeftUpperArm', t, (58 + 8 * cyc(ph, 0.45), -6, 0)).k('RightUpperArm', t, (52 + 8 * cyc(ph, 0.95), 6, 0))
    c.k('LeftLowerArm', t, (22 + 6 * cyc(ph, 0.2), 0, 0)).k('RightLowerArm', t, (28 + 6 * cyc(ph, 0.7), 0, 0))
    c.k('LeftHand', t, (-25, 0, 0)).k('RightHand', t, (-30, 0, 0))
clips.append(c)

# Atacar: levanta los brazos, se lanza y araña hacia abajo (0.9 s)
c = Pose('Atacar', 0.9)
K = {
    'UpperTorso': [(0.0, (-9, 0, 0)), (0.26, (10, 0, -6)), (0.42, (-30, 0, 8)), (0.60, (-22, 0, 4)), (0.9, (-9, 0, 0))],
    'LowerTorso': [(0.0, (0, 0, 0), (0, 0, 0)), (0.26, (4, 0, 0), (0, -0.08, -0.04)), (0.42, (-8, 0, 0), (0, 0.32, -0.22)),
                   (0.60, (-6, 0, 0), (0, 0.26, -0.18)), (0.9, (0, 0, 0), (0, 0, 0))],
    'Head': [(0.0, (-12, 10, 0)), (0.26, (16, 0, 0)), (0.42, (-24, 0, 0)), (0.60, (-16, 6, 0)), (0.9, (-12, 10, 0))],
    'LeftUpperArm': [(0.0, (14, -4, 0)), (0.26, (150, -10, 0)), (0.42, (48, -4, 0)), (0.60, (60, -4, 0)), (0.9, (14, -4, 0))],
    'RightUpperArm': [(0.0, (16, 4, 0)), (0.28, (142, 10, 0)), (0.45, (44, 4, 0)), (0.62, (56, 4, 0)), (0.9, (16, 4, 0))],
    'LeftLowerArm': [(0.0, (12, 0, 0)), (0.26, (40, 0, 0)), (0.42, (8, 0, 0)), (0.60, (14, 0, 0)), (0.9, (12, 0, 0))],
    'RightLowerArm': [(0.0, (16, 0, 0)), (0.28, (42, 0, 0)), (0.45, (8, 0, 0)), (0.62, (14, 0, 0)), (0.9, (16, 0, 0))],
    'LeftHand': [(0.0, (-8, 0, 0)), (0.26, (-35, 0, 0)), (0.42, (25, 0, 0)), (0.9, (-8, 0, 0))],
    'RightHand': [(0.0, (-12, 0, 0)), (0.28, (-35, 0, 0)), (0.45, (25, 0, 0)), (0.9, (-12, 0, 0))],
    'LeftUpperLeg': [(0.0, (-2, 0, 0)), (0.26, (-10, 0, 0)), (0.42, (26, 0, 0)), (0.60, (22, 0, 0)), (0.9, (-2, 0, 0))],
    'RightUpperLeg': [(0.0, (4, 0, 2)), (0.26, (8, 0, 0)), (0.42, (-20, 0, 0)), (0.60, (-16, 0, 0)), (0.9, (4, 0, 2))],
    'LeftLowerLeg': [(0.0, (-4, 0, 0)), (0.26, (-18, 0, 0)), (0.42, (-14, 0, 0)), (0.60, (-10, 0, 0)), (0.9, (-4, 0, 0))],
    'RightLowerLeg': [(0.0, (-6, 0, 0)), (0.26, (-24, 0, 0)), (0.42, (-48, 0, 0)), (0.60, (-36, 0, 0)), (0.9, (-6, 0, 0))],
}
for bn, ks in K.items():
    for kk in ks:
        c.k(bn, kk[0], kk[1], kk[2] if len(kk) > 2 else (0, 0, 0))
clips.append(c)

# Caer: tropieza, se le doblan las rodillas y cae de espaldas (1.4 s, se queda tumbada)
c = Pose('Caer', 1.4)
F = {
    'UpperTorso': [(0.0, (-9, 0, 0)), (0.20, (8, 0, 4)), (0.55, (-18, 0, 0)), (1.0, (-4, 0, 0)), (1.4, (0, 0, 0))],
    'LowerTorso': [(0.0, (0, 0, 0), (0, 0, 0)), (0.30, (-6, 0, 0), (0, 0.05, -0.25)), (0.62, (-12, 0, 0), (0, 0.10, -1.00)),
                   (1.05, (90, 0, 0), (0, 0.0, -2.48)), (1.4, (90, 0, 0), (0, 0, -2.58))],
    'Head': [(0.0, (-12, 10, 0)), (0.20, (24, 0, 10)), (0.62, (-16, 0, 0)), (1.05, (28, 0, -16)), (1.4, (24, 0, -22))],
    'LeftUpperArm': [(0.0, (10, -4, 0)), (0.20, (60, -30, 0)), (0.62, (30, -50, 0)), (1.05, (16, -72, 0)), (1.4, (10, -80, 0))],
    'RightUpperArm': [(0.0, (14, 4, 0)), (0.20, (40, 40, 0)), (0.62, (70, 24, 0)), (1.05, (22, 70, 0)), (1.4, (14, 84, 0))],
    'LeftLowerArm': [(0.0, (10, 0, 0)), (0.62, (30, 0, 0)), (1.05, (8, 0, 0)), (1.4, (12, 0, 0))],
    'RightLowerArm': [(0.0, (16, 0, 0)), (0.62, (40, 0, 0)), (1.05, (24, 0, 0)), (1.4, (30, 0, 0))],
    'LeftUpperLeg': [(0.0, (-2, 0, 0)), (0.30, (20, 0, 0)), (0.62, (70, 0, 0)), (1.05, (-6, 0, 0)), (1.4, (-8, 0, 0))],
    'RightUpperLeg': [(0.0, (4, 0, 0)), (0.30, (-8, 0, 0)), (0.62, (30, 0, 0)), (1.05, (-2, 0, 0)), (1.4, (2, 0, 0))],
    'LeftLowerLeg': [(0.0, (-4, 0, 0)), (0.30, (-30, 0, 0)), (0.62, (-100, 0, 0)), (1.05, (-12, 0, 0)), (1.4, (-8, 0, 0))],
    'RightLowerLeg': [(0.0, (-6, 0, 0)), (0.30, (-14, 0, 0)), (0.62, (-70, 0, 0)), (1.05, (-6, 0, 0)), (1.4, (-6, 0, 0))],
    'LeftFoot': [(0.0, (0, 0, 0)), (0.62, (30, 0, 0)), (1.4, (10, 0, 0))],
    'RightFoot': [(0.0, (0, 0, 0)), (0.62, (20, 0, 0)), (1.4, (8, 0, 0))],
}
for bn, ks in F.items():
    for kk in ks:
        c.k(bn, kk[0], kk[1], kk[2] if len(kk) > 2 else (0, 0, 0))
clips.append(c)

acts = {cl.name: cl.build() for cl in clips}
rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ RENDERS de comprobacion
CC = A.collection('Camaras')
CR = A.collection('Ref')
A.setup_world((0.50, 0.54, 0.58), 0.85)
A.add_lights(CC)
PV = os.path.join(OUT, 'previews')
A.setup_render((1280, 720), 'CYCLES', 48)
A.reference_figure(CR, x=-3.8 * ESC, y=-0.6, h=5.2)  # a la izquierda y un poco atras: no tapa a la zombi en la vista 3/4
A.ruler(CR, 2.4 * ESC, 0.0, 6)
W.backdrop(CR, 0.0, 40.0, (0.40, 0.42, 0.40))
W.hide_only({'Zombi', 'Ref', 'Camaras'})
# pose de muestra (fotograma 0.5 s de Reposo) para que no salga rigida en los renders
A.set_action(rig, acts['Reposo'])
bpy.context.scene.frame_set(30)
cams = {
    # v4: distancias para que la figura quepa entera (antes cortaba pies y cabeza) y caras completas de cerca
    '1_frente_con_ref': W.look_cam(CC, 'C1', Vector((-0.7, 0.0, 2.9)) * ESC, (0.0, 1.0, 0.06), 20.0 * ESC, 50),
    '2_tres_cuartos': W.look_cam(CC, 'C2', Vector((0.0, 0.0, 2.85)) * ESC, (0.75, 1.0, 0.12), 17.0 * ESC, 50),
    '3_espalda': W.look_cam(CC, 'C3', Vector((0.0, 0.0, 2.85)) * ESC, (-0.3, -1.0, 0.10), 17.0 * ESC, 50),
    '4_cara_tres_cuartos': W.look_cam(CC, 'C4', Vector((0.0, 0.05, 5.10)) * ESC, (0.45, 1.0, 0.05), 3.4 * ESC, 50),
    '5_cara_frente_muy_cerca': W.look_cam(CC, 'C5', Vector((0.0, 0.05, 5.12)) * ESC, (0.0, 1.0, 0.0), 2.6 * ESC, 50),
    '6_torso_y_manos': W.look_cam(CC, 'C6', Vector((0.2, 0.0, 3.4)) * ESC, (0.35, 1.0, 0.18), 7.0 * ESC, 50),
    '7_perfil_izq': W.look_cam(CC, 'C7', Vector((0.0, 0.0, 2.85)) * ESC, (-1.0, 0.0, 0.08), 17.0 * ESC, 50),
}
for n, cam in cams.items():
    A.render(os.path.join(PV, NOMBRE + '_' + n + '.png'), cam)
rig.animation_data.action = None
bpy.context.scene.frame_set(0)

if not QUICK:
    A.setup_render((480, 360), 'CYCLES', 16)
    sc = bpy.context.scene
    TIMES = {'Reposo': [0, 0.5, 1.0, 1.5], 'Caminar': [0, 0.14, 0.28, 0.41, 0.55, 0.69, 0.83, 0.96],
             'Atacar': [0, 0.13, 0.26, 0.34, 0.42, 0.50, 0.65, 0.88], 'Caer': [0, 0.2, 0.4, 0.62, 0.8, 1.0, 1.2, 1.4]}
    camc = W.look_cam(CC, 'CK', Vector((0.0, 0.0, 2.7)) * ESC, (0.95, 0.85, 0.22), 17.0 * ESC, 50)
    for n, ts in TIMES.items():
        A.set_action(rig, acts[n])
        items = []
        for t in ts:
            sc.frame_set(int(round(t * 60)))
            p = os.path.join(PV, '_f_%s_%03d.png' % (n, int(t * 1000)))
            A.render(p, camc)
            items.append((p, '%s %.2fs' % (n, t)))
        W.contact_sheet(items, 4, os.path.join(PV, '%s_clip_%s.png' % (NOMBRE, n)),
                        title='%s - %s (%.2fs)' % (NOMBRE, n, [x for x in clips if x.name == n][0].length))
        for p, _ in items:
            os.remove(p)
    rig.animation_data.action = None
    sc.frame_set(0)

# ------------------------------------------------------------------ guardar y exportar
for o in list(CR.objects):
    bpy.data.objects.remove(o, do_unlink=True)
W.hide_only({'Zombi', 'Camaras'})
A.save_blend(os.path.join(OUT, NOMBRE + '.blend'))
mn, mx = W.bounds(objs)
A.write_json(os.path.join(OUT, 'datos.json'), {
    'triangulos': TRIS, 'triangulos_total': sum(TRIS.values()), 'medidas_studs': [round(v, 3) for v in (mx - mn)],
    'texturas': TEXS, 'clips': {cl.name: {'duracion_s': cl.length, 'bucle': cl.loop} for cl in clips},
    'huesos': BN, 'exportacion': 'FBX global_scale=0.01, ejes -Z delante / Y arriba (1 unidad = 1 stud)'})
A.set_action(rig, acts['Reposo'])
A.export_fbx(os.path.join(OUT, NOMBRE + '.fbx'), [rig] + objs, anim=True, all_actions=True)
for n, act in acts.items():
    A.set_action(rig, act)
    A.export_fbx(os.path.join(OUT, 'clips', '%s_%s.fbx' % (NOMBRE, n)), [rig] + objs, anim=True)
rig.animation_data.action = None
# estatico con los nombres R15 exactos (sin renombrar, las copias saldrian como Head.001)
for o in objs:
    o.name = o.name + '_rig'
cst, st_objs = W.static_copies(objs)
for o2, o in zip(st_objs, objs):
    o2.name = o.name[:-4]
A.export_fbx(os.path.join(OUT, NOMBRE + '_Estatico.fbx'), st_objs)
A.export_glb(os.path.join(OUT, NOMBRE + '_Estatico.glb'), st_objs)
W.remove_collection(cst)
for o in objs:
    o.name = o.name[:-4]

# script para la barra de comandos de Studio: convierte el Model importado (ZombiMujer_Estatico.fbx) en un rig R15 jugable
rb = lambda v: 'Vector3.new(%.3f, %.3f, %.3f)' % (v[0], v[2], -v[1])
M6 = {'LowerTorso': 'Root', 'UpperTorso': 'Waist', 'Head': 'Neck', 'LeftUpperArm': 'LeftShoulder', 'LeftLowerArm': 'LeftElbow',
      'LeftHand': 'LeftWrist', 'RightUpperArm': 'RightShoulder', 'RightLowerArm': 'RightElbow', 'RightHand': 'RightWrist',
      'LeftUpperLeg': 'LeftHip', 'LeftLowerLeg': 'LeftKnee', 'LeftFoot': 'LeftAnkle', 'RightUpperLeg': 'RightHip',
      'RightLowerLeg': 'RightKnee', 'RightFoot': 'RightAnkle'}
ut = parts['UpperTorso']
bb = [ut.matrix_world @ Vector(c) for c in ut.bound_box]
utc = [(min(v[i] for v in bb) + max(v[i] for v in bb)) / 2 for i in range(3)]
L = ['-- Ejecutar en la barra de comandos de Studio con el Model importado de %s_Estatico.fbx SELECCIONADO.' % NOMBRE,
     '-- Lo deja como rig R15: HumanoidRootPart invisible, Motor6D en cada articulacion (nombres R15) y Humanoid R15.',
     '-- Luego se mueve a ServerStorage.LUTO_Plantillas. Generado por tools/build_zombi.py.',
     'local m = game:GetService("Selection"):Get()[1]',
     'assert(m and m:IsA("Model"), "Selecciona el Model importado de la zombi")',
     'm.Name = "%s"' % VAR['plantilla'],
     'local off = m:FindFirstChild("UpperTorso", true).Position - %s  -- donde lo dejo el importador' % rb(utc),
     'local J = {']
for n, p in J.items():
    L.append('\t%s = %s,' % (n, rb(p)))
L += ['}', 'local hrp = Instance.new("Part")',
      'hrp.Name = "HumanoidRootPart"; hrp.Size = Vector3.new(2, 2, 1); hrp.Transparency = 1; hrp.CanCollide = false',
      'hrp.CFrame = CFrame.new(J.HumanoidRootPart + off); hrp.Parent = m',
      'for _, d in ipairs(m:GetDescendants()) do',
      '\tif d:IsA("BasePart") then d.Anchored = false; d.CanCollide = false end',
      'end',
      'local function motor(nombre, p0, p1, junta)',
      '\tlocal a, b = m:FindFirstChild(p0, true), m:FindFirstChild(p1, true)',
      '\tlocal j = CFrame.new(junta + off)',
      '\tlocal mt = Instance.new("Motor6D")',
      '\tmt.Name = nombre; mt.Part0 = a; mt.Part1 = b; mt.C0 = a.CFrame:Inverse() * j; mt.C1 = b.CFrame:Inverse() * j',
      '\tmt.Parent = b',
      'end']
for n, mname in M6.items():
    L.append('motor("%s", "%s", "%s", J.%s)' % (mname, PAR[n], n, n))
L += ['local h = Instance.new("Humanoid")', 'h.RigType = Enum.HumanoidRigType.R15',
      'h.HipHeight = %.3f  -- de la base del HumanoidRootPart al suelo' % (J['HumanoidRootPart'][2] - 1.0),
      'h.Parent = m', 'm.PrimaryPart = hrp', 'print("%s lista como R15")' % VAR['plantilla']]
os.makedirs(os.path.join(OUT, 'integracion'), exist_ok=True)
with open(os.path.join(OUT, 'integracion', 'ArmarZombi.lua'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(L) + '\n')
A.log('listo')
