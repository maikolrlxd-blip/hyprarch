# Edificios en ruinas del mapa apocalíptico (realista facetado). Frente del edificio = -Y; base centrada en el origen.
# Tienda de 2 plantas, bloque de 5 plantas con esquina derrumbada y almacen con el tejado hundido.
# blender -b --factory-startup -P build_mapa_edificios.py
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import importlib
import ap_lib as A
import ap_armas as W
import ap_piezas as Z
import ap_estilos as E
importlib.reload(A); importlib.reload(W); importlib.reload(Z); importlib.reload(E)
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler

smooth = A.smoothstep
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'mapa', 'edificios')
rng = np.random.default_rng(5)


def rbox(mb, c, sz, mat, rot=(0, 0, 0), bevel=0.0):
    mk = mb.mark()
    mb.box((0, 0, 0), sz, mat, bevel=bevel)
    R = Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()
    mb.xform_since(mk, Matrix.Translation(Vector(c)) @ R)


def wall(mb, axis, fixed, a0, a1, z0, z1, thick, wins, mat, boards=0.3, glass=0.25, sill=True):
    """Muro con huecos reales. axis 'x': muro a lo largo de X con cara exterior en y = fixed (exterior hacia -Y si fixed < 0).
    wins: [(centro_a, centro_z, ancho, alto)]. Detras de cada hueco: panel 'interior' oscuro; algunas ventanas tapiadas con tablas."""
    out = -1.0 if fixed < 0 else 1.0
    cen = fixed - out * thick / 2

    def B(a_c, z_c, a_s, z_s, m, depth=thick, off=0.0):
        if axis == 'x':
            mb.box((a_c, cen + off, z_c), (a_s, depth, z_s), m)
        else:
            mb.box((cen + off, a_c, z_c), (depth, a_s, z_s), m)

    bounds = sorted({a0, a1} | {w[0] - w[2] / 2 for w in wins} | {w[0] + w[2] / 2 for w in wins})
    for b0, b1 in zip(bounds[:-1], bounds[1:]):
        if b1 - b0 < 1e-4:
            continue
        mid = (b0 + b1) / 2
        cov = sorted([(w[1] - w[3] / 2, w[1] + w[3] / 2) for w in wins if abs(mid - w[0]) < w[2] / 2 - 1e-4])
        zc = z0
        for (lo, hi) in cov + [(z1, z1)]:
            if lo - zc > 1e-3:
                B(mid, (zc + lo) / 2, b1 - b0, lo - zc, mat)
            zc = max(zc, hi)
    if wins:                                                                                 # un solo fondo oscuro por muro
        zl = min(w[1] - w[3] / 2 for w in wins); zh = max(w[1] + w[3] / 2 for w in wins)
        # mas corto que el muro: si llega a las esquinas, su canto asoma en la cara exterior de los laterales (raya negra)
        B((a0 + a1) / 2, (zl + zh) / 2, a1 - a0 - 2 * thick - 0.2, zh - zl, 'interior', depth=0.12, off=-out * (thick / 2 + 0.8))
    for (ac, zcn, w, h) in wins:
        if sill:
            B(ac, zcn - h / 2 - 0.12, w + 0.5, 0.24, 'hormigon', depth=thick + 0.5, off=out * 0.25)
        r = rng.random()
        if r < boards:                                                                       # tablas clavadas
            for k in range(2):
                ang = (18 if k == 0 else -14) + rng.uniform(-6, 6)
                if axis == 'x':
                    rbox(mb, (ac, fixed + out * 0.12, zcn + (k - 0.5) * h * 0.35), (w * 1.12, 0.12, 0.45), 'madera_vieja', (0, ang, 0))
                else:
                    rbox(mb, (fixed + out * 0.12, ac, zcn + (k - 0.5) * h * 0.35), (0.12, w * 1.12, 0.45), 'madera_vieja', (ang, 0, 0))
        elif r < boards + glass:                                                             # cristal roto: un triangulo
            pts = [(-w / 2 + 0.1, h / 2 - 0.1), (w * 0.15, h / 2 - 0.1), (-w / 2 + 0.1, -h * 0.1)]
            mk = mb.mark()
            mb.prism(pts, -0.03, 0.03, 'vidrio', plane='XZ')
            M = Matrix.Translation(Vector((ac, fixed - out * thick * 0.5, zcn)) if axis == 'x' else Vector((fixed - out * thick * 0.5, ac, zcn)))
            if axis != 'x':
                M = M @ Euler((0, 0, math.radians(90)), 'XYZ').to_matrix().to_4x4()
            mb.xform_since(mk, M)


def parapet(mb, x0, x1, y0, y1, z, h=1.4, t=0.6, mat='hormigon'):
    mb.box(((x0 + x1) / 2, y0 + t / 2, z + h / 2), (x1 - x0, t, h), mat)
    mb.box(((x0 + x1) / 2, y1 - t / 2, z + h / 2), (x1 - x0, t, h), mat)
    mb.box((x0 + t / 2, (y0 + y1) / 2, z + h / 2), (t, y1 - y0 - 2 * t, h), mat)
    mb.box((x1 - t / 2, (y0 + y1) / 2, z + h / 2), (t, y1 - y0 - 2 * t, h), mat)


def jag_top(mb, axis, fixed, a0, a1, ztop, thick, mat, n=6, amp=2.5, seed=1):
    """Borde superior roto de un muro: dientes triangulares irregulares."""
    r = np.random.default_rng(seed)
    out = -1.0 if fixed < 0 else 1.0
    cen = fixed - out * thick / 2
    xs = np.linspace(a0, a1, n + 1)
    for i in range(n):
        h = amp * (0.3 + 0.7 * r.random())
        pk = xs[i] + (xs[i + 1] - xs[i]) * r.uniform(0.2, 0.8)
        pts = [(xs[i], ztop), (xs[i + 1], ztop), (pk, ztop + h)]
        if axis == 'x':
            mb.prism(pts, cen - thick / 2, cen + thick / 2, mat, plane='XZ')
        else:
            mb.prism([(p[0], p[1]) for p in pts], cen - thick / 2, cen + thick / 2, mat, plane='YZ')


# ------------------------------------------------------------------ pintura especifica de fachadas
def brick(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    side = np.abs(nrm[:, 2]) < 0.5
    u = np.where(np.abs(nrm[:, 0]) > 0.6, y, x)
    row = np.floor(z / 0.62)
    uu = u + (row % 2) * 0.8
    col_i = np.floor(uu / 1.6)
    mortar = side & ((((z / 0.62) % 1.0) < 0.10) | (((uu / 1.6) % 1.0) < 0.05))
    hv = A._hash(row.astype(np.int64), col_i.astype(np.int64), np.zeros_like(row, dtype=np.int64), 7)
    col[side] = col[side] * (0.86 + 0.26 * hv[side])[:, None]
    col[mortar] = col[mortar] * 0.35 + np.array([0.62, 0.58, 0.52], np.float32) * 0.65
    # hollin y manchas de humedad que bajan de las ventanas
    st = smooth(0.55, 0.8, A.fbm(np.stack([u * 0.35, u * 0.0, z * 0.06], 1) + 3.0, 3, 701)) * side
    col = col * (1 - 0.4 * st[:, None])
    return col


def plaster(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    side = np.abs(nrm[:, 2]) < 0.5
    u = np.where(np.abs(nrm[:, 0]) > 0.6, y, x)
    # desconchones que dejan ver ladrillo
    pe = side & (smooth(0.64, 0.68, A.fbm(np.stack([u * 0.22, z * 0.22, u * 0.0], 1) + 9.0, 3, 711)) > 0.5)
    row = np.floor(z / 0.62)
    uu = u + (row % 2) * 0.8
    br = np.array([0.52, 0.30, 0.22], np.float32)
    col[pe] = br * (0.8 + 0.3 * A._hash(row.astype(np.int64)[pe], np.floor(uu / 1.6).astype(np.int64)[pe], np.zeros(pe.sum(), np.int64), 3))[:, None]
    mt = pe & ((((z / 0.62) % 1.0) < 0.10) | (((uu / 1.6) % 1.0) < 0.05))
    col[mt] = np.array([0.55, 0.52, 0.47], np.float32)
    rim = side & ~pe & (smooth(0.60, 0.64, A.fbm(np.stack([u * 0.22, z * 0.22, u * 0.0], 1) + 9.0, 3, 711)) > 0.5)
    col[rim] = col[rim] * 0.7
    # chorretones de suciedad verticales
    dr = smooth(0.58, 0.82, A.fbm(np.stack([u * 0.9, z * 0.05, u * 0.0], 1) + 1.0, 3, 713)) * side
    col = col * (1 - 0.35 * dr[:, None])
    # ventanas pintadas en las fachadas laterales y traseras (solo en caras que no son el frente)
    pw = side & (nrm[:, 1] > -0.6)
    for (ufun, zs, us, w, h) in PAINTED.get('cur', []):
        pass
    return col


PAINTED = {}


def painted_windows(spec):
    """spec: lista de (normal_eje, signo, [centros_u], [centros_z], ancho, alto) -> pinta ventanas oscuras con marco y alfeizar."""
    def f(P, msk, pos, nrm, col):
        col = plaster(P, msk, pos, nrm, col) if spec.get('base') == 'yeso' else brick(P, msk, pos, nrm, col)
        x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
        for (ax, sg, us, zs, w, h) in spec['wins']:
            face = (nrm[:, ax] * sg > 0.8)
            u = y if ax == 0 else x
            for uc in us:
                for zc in zs:
                    m = face & (np.abs(u - uc) < w / 2) & (np.abs(z - zc) < h / 2)
                    gl = m & (np.abs(u - uc) < w / 2 - 0.25) & (np.abs(z - zc) < h / 2 - 0.25)
                    col[m & ~gl] = col[m & ~gl] * 0.5 + np.array([0.30, 0.28, 0.25], np.float32) * 0.5
                    g = np.array([0.08, 0.10, 0.12], np.float32)
                    sh = smooth(0.4, 0.7, A.fbm(pos[gl] * 0.6, 2, 721))
                    col[gl] = g * (0.8 + 0.8 * sh)[:, None]
                    mull = gl & ((np.abs(u - uc) < 0.08) | (np.abs(z - zc) < 0.08))
                    col[mull] = np.array([0.25, 0.24, 0.22], np.float32)
                    sill = face & (np.abs(u - uc) < w / 2 + 0.25) & (z > zc - h / 2 - 0.35) & (z < zc - h / 2)
                    col[sill] = col[sill] * 0.5 + np.array([0.62, 0.60, 0.55], np.float32) * 0.5
        return col
    return f


def interior_x(P, msk, pos, nrm, col):
    # habitacion oscura con un poco de luz y restos (no plano negro)
    n = A.fbm(pos * 0.8, 3, 731)
    col *= (0.7 + 0.8 * n)[:, None]
    return col


def letrero_x(P, msk, pos, nrm, col):
    """Cartel generico de la tienda: TIENDA (sin marcas)."""
    x, z = pos[:, 0], pos[:, 2]
    fr = nrm[:, 1] < -0.8
    tu = (x + 7.8) / 0.45
    tv = (10.2 - z) / 0.32
    m = fr & (tu >= 0) & (tu < 36) & (tv >= 0) & (tv < 7)
    if m.any():
        iu, iv = np.floor(tu[m]).astype(int), np.floor(tv[m]).astype(int)
        hit = np.zeros(iu.shape, bool)
        for i, ch in enumerate('TIENDA'):
            g = W._G[ch]
            for rr, row in enumerate(g):
                for cc, px in enumerate(row):
                    if px == '#':
                        hit |= (iu == i * 6 + cc) & (iv == rr)
        idx = np.where(m)[0][hit]
        col[idx] = np.array([0.86, 0.80, 0.62], np.float32) * (0.75 + 0.35 * A.vnoise(pos[idx] * 3.0, 3))[:, None]
    return col


def toldo_x(P, msk, pos, nrm, col):
    x = pos[:, 0]
    st = ((x + 40.0) % 2.4) < 1.2
    col[st] = col[st] * 0.35 + np.array([0.70, 0.66, 0.58], np.float32) * 0.65
    return col


def chapa_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    side = np.abs(nrm[:, 2]) < 0.5
    u = np.where(np.abs(nrm[:, 0]) > 0.6, y, x)
    corr = 0.5 + 0.5 * np.sin(u * 2 * math.pi / 0.9)
    col[side] = col[side] * (0.80 + 0.30 * corr[side])[:, None]
    top = nrm[:, 2] > 0.3
    corr2 = 0.5 + 0.5 * np.sin(x * 2 * math.pi / 0.9)
    col[top] = col[top] * (0.80 + 0.30 * corr2[top])[:, None]
    rs = smooth(0.55, 0.75, A.fbm(np.stack([u * 0.6, z * 0.12, u * 0], 1) + 4.0, 3, 741))
    col = col * (1 - 0.5 * rs[:, None]) + np.array([0.45, 0.25, 0.12], np.float32) * (0.5 * rs)[:, None]
    return col


STYLES = dict(E.STYLES)
STYLES.update({
    'ladrillo': dict(base='#8c4e3a', var=0.10, stroke=(2, 2, 1), stroke_scale=2.0, blotch=0.12, ao=0.6, ao_tint='#1a110d', light=0.20,
                     grime=0.35, grime_col='#2a1f19', dust=0.12, edge_col='#c08a70', edge=0.5, edge_th=0.05, face_var=0.0, seed=3),
    'yeso': dict(base='#b8ac93', var=0.10, stroke=(2, 2, 1), stroke_scale=1.6, blotch=0.15, ao=0.6, ao_tint='#1d1a15', light=0.20,
                 grime=0.40, grime_col='#4a4236', dust=0.10, edge_col='#ddd3be', edge=0.6, edge_th=0.05, face_var=0.0, seed=5),
    'hormigon': dict(base='#9d998f', var=0.10, stroke=(2, 2, 1), stroke_scale=2.0, blotch=0.12, ao=0.6, ao_tint='#1d1c1a', light=0.22,
                     grime=0.40, grime_col='#4d4a42', dust=0.15, edge_col='#cfcbbf', edge=0.8, edge_th=0.05, face_var=0.0, seed=7),
    'interior': dict(base='#191716', var=0.05, ao=0.3, light=0.05, face_var=0.0, seed=9, extra=interior_x),
    'vidrio': dict(base='#5d7078', var=0.10, ao=0.3, light=0.3, edge_col='#c7d2d6', edge=0.8, face_var=0.0, seed=11),
    'madera_vieja': dict(base='#6f5841', var=0.16, stroke=(6, 1, 1), stroke_scale=3, tone_steps=5, blotch=0.12, ao=0.6, ao_tint='#1a120a',
                         light=0.26, grime=0.35, grime_col='#2f2318', dust=0.2, edge_col='#a88a66', edge=0.7, edge_th=0.05, seed=13),
    'letrero': dict(base='#2f4a5c', var=0.10, stroke=(4, 1, 1), stroke_scale=2, ao=0.5, light=0.2, rust=0.4, grime=0.35, edge_col='#8aa0ae',
                    edge=0.6, face_var=0.0, seed=15, extra=letrero_x),
    'toldo': dict(base='#8a2f2b', var=0.12, stroke=(1, 4, 1), stroke_scale=2, blotch=0.15, ao=0.55, light=0.2, grime=0.45, grime_col='#2a201a',
                  dust=0.2, edge_col='#c08070', edge=0.5, face_var=0.0, seed=17, extra=toldo_x),
    'tejado': dict(base='#3b3936', var=0.10, stroke=(3, 3, 1), stroke_scale=1.5, blotch=0.12, ao=0.55, light=0.2, grime=0.35, dust=0.35,
                   dust_col='#7a7468', edge_col='#6a6762', edge=0.5, face_var=0.0, seed=19),
    'chapa': dict(base='#7a7f84', var=0.10, stroke=(1, 1, 6), stroke_scale=2, blotch=0.12, ao=0.6, ao_tint='#121417', light=0.24, rust=0.5,
                  grime=0.35, dust=0.15, edge_col='#c9cdd0', edge=0.7, face_var=0.0, seed=21, extra=chapa_x),
    'metal_gris': dict(base='#5f6367', var=0.10, stroke=(1, 1, 4), stroke_scale=3, ao=0.6, light=0.24, rust=0.45, grime=0.3, edge_col='#b3b7bb',
                       edge=0.8, face_var=0.0, seed=23),
    'hierro': dict(base='#6d4a36', var=0.12, stroke=(1, 4, 1), stroke_scale=5.0, ao=0.6, light=0.24, rust=0.5, grime=0.25, edge_col='#a07250',
                   edge=0.6, face_var=0.0, seed=25),
    'escombro': dict(base='#8d877c', var=0.14, stroke=(1, 1, 1), stroke_scale=2.5, blotch=0.15, ao=0.65, ao_tint='#1a1916', light=0.24,
                     grime=0.35, dust=0.35, dust_col='#b0a998', edge_col='#cdc6b6', edge=0.7, face_var=0.06, seed=27),
})


# ------------------------------------------------------------------ TIENDA (2 plantas)
def tienda(C):
    mb = A.MB('Tienda')
    X0, X1, Y0, Y1 = -18.0, 18.0, -12.0, 12.0
    T = 0.8
    # planta baja: escaparates y puerta; planta alta: 4 ventanas
    wall(mb, 'x', Y0, X0, X1, 0.0, 11.0, T, [(-10.0, 4.6, 8.0, 6.8), (2.0, 3.8, 3.6, 7.6), (11.0, 4.6, 6.0, 6.8)], 'yeso', boards=0.34, glass=0.66,
         sill=False)
    wall(mb, 'x', Y0, X0, X1, 11.0, 20.0, T, [(-13.0, 15.2, 3.6, 4.6), (-5.0, 15.2, 3.6, 4.6), (3.0, 15.2, 3.6, 4.6), (11.0, 15.2, 3.6, 4.6)], 'yeso')
    mb.box((0, Y1 - T / 2, 10.0), (36.0, T, 20.0), 'yeso')                       # fachada trasera
    mb.box((X0 + T / 2, 0, 10.0), (T, 24.0 - 2 * T, 20.0), 'yeso')               # laterales
    mb.box((X1 - T / 2, 0, 10.0), (T, 24.0 - 2 * T, 20.0), 'yeso')
    mb.box((0, 0, 19.7), (36.0, 24.0, 0.6), 'tejado')                             # cubierta
    parapet(mb, X0, X1, Y0, Y1, 20.0)
    mb.box((0, Y0 - 0.25, 11.2), (36.4, 0.5, 0.5), 'hormigon')                   # cornisa entre plantas
    mb.box((0, Y0 - 0.45, 9.6), (17.0, 0.5, 2.2), 'letrero')                      # cartel
    rbox(mb, (-6.0, Y0 - 2.0, 8.2), (16.0, 3.8, 0.18), 'toldo', (-14, 6, 0))      # toldo roto e inclinado
    rbox(mb, (8.5, Y0 - 1.2, 7.6), (6.0, 2.4, 0.18), 'toldo', (-38, -10, 0))
    # tejado: maquina de aire, chimenea, caseton
    mb.box((8.0, 4.0, 21.0), (4.0, 3.0, 2.0), 'metal_gris', bevel=0.08)
    mb.cyl((-10.0, 6.0, 20.0), (-10.0, 6.0, 23.5), 0.5, 8, 'metal_gris')
    mb.box((-4.0, 7.0, 21.5), (5.0, 4.0, 3.0), 'hormigon')
    # escombros y cristales al pie del escaparate
    for i in range(5):
        mb.rock((-12.0 + i * 4.5 + rng.uniform(-1, 1), Y0 - 1.0 - rng.uniform(0, 1.5), 0.25), 0.5 + 0.4 * rng.random(), 'escombro', subdiv=1,
                seed=40 + i, jitter=0.3, squash=(1.3, 1.0, 0.6))
    return mb.finish(C)


# ------------------------------------------------------------------ BLOQUE DE 5 PLANTAS con la esquina derecha derrumbada
def bloque(C):
    mb = A.MB('Bloque')
    X0, X1, Y0, Y1 = -15.0, 15.0, -12.0, 12.0
    T = 0.8
    FL = 9.0
    xs = [-10.5, -3.5, 3.5, 10.5]
    # planta baja: portal y dos ventanas
    wall(mb, 'x', Y0, X0, X1, 0.0, FL, T, [(-10.5, 4.2, 3.4, 4.6), (0.0, 3.6, 4.0, 7.2), (10.5, 4.2, 3.4, 4.6)], 'ladrillo', boards=0.5, glass=0.3)
    for f in range(1, 5):
        z0, z1 = f * FL, (f + 1) * FL
        if f <= 2:
            wall(mb, 'x', Y0, X0, X1, z0, z1, T, [(x, z0 + 4.8, 3.2, 4.2) for x in xs], 'ladrillo', boards=0.25, glass=0.3, sill=False)
        else:                                            # plantas 4 y 5: solo la parte izquierda sigue en pie
            wall(mb, 'x', Y0, X0, 4.0, z0, z1, T, [(x, z0 + 4.8, 3.2, 4.2) for x in xs[:2]], 'ladrillo', boards=0.25, glass=0.3, sill=False)
    jag_top(mb, 'x', Y0, 4.0, X1, 3 * FL, T, 'ladrillo', n=4, amp=3.0, seed=3)
    # trasera y laterales (ventanas pintadas para ahorrar triangulos)
    mb.box((-5.5, Y1 - T / 2, 22.5), (19.0, T, 45.0), 'ladrillo')
    mb.box((9.5, Y1 - T / 2, 13.5), (11.0, T, 27.0), 'ladrillo')
    jag_top(mb, 'x', Y1, 4.0, X1, 27.0, T, 'ladrillo', n=3, amp=2.5, seed=5)
    mb.box((X0 + T / 2, 0, 22.5), (T, 24.0 - 2 * T, 45.0), 'ladrillo')
    mb.box((X1 - T / 2, 0, 13.5), (T, 24.0 - 2 * T, 27.0), 'ladrillo')
    jag_top(mb, 'y', X1, Y0 + T, Y1 - T, 27.0, T, 'ladrillo', n=5, amp=3.5, seed=7)
    # forjados asomando, cubierta parcial y losas colgando
    mb.box((-5.5, 0, 44.7), (19.0, 24.0, 0.6), 'tejado')
    parapet(mb, X0, 4.0, Y0, Y1, 45.0)
    for f in range(1, 4):
        mb.box((0, 0, f * FL), (30.0 - 0.2, 24.0 - 0.2, 0.5), 'hormigon')
    mb.box((-5.5, 0, 4 * FL), (19.0, 23.8, 0.5), 'hormigon')
    rbox(mb, (9.0, -2.0, 25.0), (9.0, 12.0, 0.5), 'hormigon', (16, -24, 8))       # losa caida colgando
    rbox(mb, (11.0, 4.0, 28.5), (7.0, 9.0, 0.5), 'hormigon', (-10, 30, -12))
    for (p0, p1) in (((4.2, -11.5, 27.0), (6.5, -12.8, 30.5)), ((14.5, 0.0, 27.0), (15.8, 1.5, 30.0)), ((8.0, -6.0, 26.0), (9.5, -9.0, 31.0))):
        mb.cyl(p0, p1, 0.12, 5, 'hierro')
    # monton de escombros al pie
    for i in range(8):
        mb.rock((6.0 + i * 1.6 + rng.uniform(-1, 1), Y0 - 2.0 - rng.uniform(0, 3.0), 0.4 + rng.uniform(0, 1.0)), 0.9 + 0.8 * rng.random(), 'escombro',
                subdiv=1, seed=60 + i, jitter=0.35, squash=(1.3, 1.1, 0.7))
    return mb.finish(C)


# ------------------------------------------------------------------ ALMACEN con persiana a medio subir y tejado hundido
def almacen(C):
    mb = A.MB('Almacen')
    X0, X1, Y0, Y1 = -22.0, 22.0, -15.0, 15.0
    T = 0.7
    H = 14.0
    wall(mb, 'x', Y0, X0, X1, 0.0, H, T, [(-4.0, 5.0, 12.0, 10.0), (14.0, 3.6, 3.0, 7.2), (-17.0, 11.5, 4.0, 2.4), (6.0, 11.5, 4.0, 2.4)], 'chapa',
         boards=0.0, glass=0.4, sill=False)
    mb.box((-4.0, Y0 + 0.2, 8.0), (12.2, 0.35, 4.0), 'chapa')                     # persiana a medio subir
    mb.box((-4.0, Y0 - 0.6, 0.6), (16.0, 1.2, 1.2), 'hormigon')                  # muelle de carga
    mb.box((0, Y1 - T / 2, H / 2), (44.0, T, H), 'chapa')
    for sx, X in ((-1, X0), (1, X1)):
        mb.box((X - sx * T / 2, 0, H / 2), (T, 30.0 - 2 * T, H), 'chapa')
        mb.prism([(-15.0, H), (15.0, H), (0.0, H + 5.0)], X - sx * T, X, 'chapa', plane='YZ')   # piñones
    # tejado a dos aguas: faldon izquierdo entero, derecho roto con hueco
    ang = math.degrees(math.atan2(5.0, 15.0))
    rbox(mb, (0, -7.5, H + 2.5), (45.0, 15.9, 0.35), 'chapa', (ang, 0, 0))
    rbox(mb, (-11.5, 7.5, H + 2.5), (22.0, 15.9, 0.35), 'chapa', (-ang, 0, 0))
    rbox(mb, (16.0, 7.5, H + 2.5), (12.0, 15.9, 0.35), 'chapa', (-ang, 0, 0))
    rbox(mb, (5.0, 6.0, H - 3.5), (9.0, 12.0, 0.35), 'chapa', (-55, 12, 8))     # trozo de tejado caido dentro
    mb.box((0, 0, H + 4.9), (44.6, 0.6, 0.6), 'metal_gris')                      # cumbrera
    for x in (-15.0, -5.0, 5.0, 15.0):                                           # cerchas a la vista por el hueco
        mb.box((x, 0, H - 0.3), (0.5, 30.0 - 2 * T, 0.6), 'metal_gris')
    mb.cyl((18.0, 10.0, H + 3.0), (18.0, 10.0, H + 7.0), 0.6, 8, 'metal_gris')   # chimenea de ventilacion
    return mb.finish(C)


cat = Z.Cat('Edificios', OUT, STYLES)
cat.piece('Edificio_Tienda', tienda, size=1024, ao_dist=1.2, bevel_r=0.08, samples=16, angle=60,
          extra={'yeso': painted_windows({'base': 'yeso', 'wins': [(0, -1, [-6.0, 4.0], [15.2], 3.6, 4.6), (0, 1, [-6.0, 4.0], [15.2], 3.6, 4.6),
                                                                    (1, 1, [-12.0, -4.0, 4.0, 12.0], [5.0, 15.2], 3.6, 4.6)]})})
cat.piece('Edificio_Bloque', bloque, size=1024, ao_dist=1.2, bevel_r=0.08, samples=16, angle=60,
          extra={'ladrillo': painted_windows({'base': 'ladrillo', 'wins': [(0, -1, [-6.0, 6.0], [4.8 + 9 * k for k in range(5)], 3.2, 4.2),
                                                                         (0, 1, [-6.0, 6.0], [4.8 + 9 * k for k in range(3)], 3.2, 4.2),
                                                                         (1, 1, [-10.5, -3.5], [4.8 + 9 * k for k in range(5)], 3.2, 4.2)]})})
cat.piece('Edificio_Almacen', almacen, size=1024, ao_dist=1.2, bevel_r=0.08, samples=16, angle=60)
cat.previews(dist_k=1.05)
cat.finish()
A.log('edificios listos')
