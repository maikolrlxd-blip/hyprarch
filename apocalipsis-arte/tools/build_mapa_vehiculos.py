# Vehiculos abandonados del mapa apocalíptico: sedan oxidado, sedan quemado, sedan volcado, pickup y furgoneta.
# Origen en el centro de la base; el frente apunta a +Y; 1 unidad = 1 stud (coche ~15 studs de largo, ~5 de alto).
# blender -b --factory-startup -P build_mapa_vehiculos.py
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
OUT = os.path.join(ROOT, 'mapa', 'vehiculos')


def ell(u, v, cx, cy, rx, ry):
    return ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2


def car_paint(belt=3.4, wheel_y=(-4.6, 4.6), wheel_z=1.25, glass_col=(0.10, 0.14, 0.16), smashed=True, cabin=(-3.2, 3.2), doors=(-2.1, 0.2, 2.4)):
    def f(P, msk, pos, nrm, col):
        x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
        side = np.abs(nrm[:, 0]) > 0.6
        # arcos de rueda oscuros
        for wy in wheel_y:
            arch = side & (ell(y, z, wy, wheel_z, 1.75, 1.75) < 1)
            col[arch] = col[arch] * 0.22
        # ventanas laterales, parabrisas y luneta (vidrio oscuro con reflejo y grietas)
        wl = side & (z > belt + 0.1) & (y > cabin[0] + 0.2) & (y < cabin[1] - 0.2)
        wf = (nrm[:, 1] > 0.3) & (nrm[:, 2] > 0.25) & (z > belt + 0.1)
        wr = (nrm[:, 1] < -0.3) & (nrm[:, 2] > 0.25) & (z > belt + 0.1)
        gl = wl | wf | wr
        g = np.array(glass_col, np.float32)
        shine = smooth(0.4, 0.6, A.fbm(np.stack([x * 0.9 + z * 0.9, y * 0.3, z * 0.1], 1) + 7.0, 2, 201))
        col[gl] = g * (0.8 + 0.7 * shine[gl])[:, None]
        if smashed:
            # telarana de grietas desde un impacto por cristal: rayos rectos + dos anillos; el lateral izquierdo, roto
            mid = (cabin[0] + cabin[1]) / 2
            for (sel, uu, vv, cu, cv, roto) in ((gl & (nrm[:, 1] > 0.3), x, z, 0.8, belt + 0.9, False),
                                                 (gl & (nrm[:, 0] < -0.6), y, z, mid + 0.6, belt + 0.8, True),
                                                 (gl & (nrm[:, 0] > 0.6), y, z, mid - 1.2, belt + 0.7, False),
                                                 (gl & (nrm[:, 1] < -0.3), x, z, -0.7, belt + 0.8, False)):
                du, dv = uu - cu, vv - cv
                r = np.hypot(du, dv)
                a = np.arctan2(dv, du)
                k = a / (2 * np.pi) * 9 + 0.25 * np.sin(r * 4.0 + cu)
                kr = np.round(k)
                largo = 0.9 + 0.9 * ((np.abs(kr.astype(np.int64) * 7919 + 13) % 11) / 10.0)
                rayo = (np.abs(k - kr) * 2 * np.pi * r / 9 < 0.022) & (r < largo)
                anillo = ((np.abs(r - 0.35) < 0.016) | (np.abs(r - 0.75) < 0.014)) & (r < largo)
                m = sel & (rayo | anillo | (r < 0.07))
                col[m] = col[m] * 0.35 + np.array([0.50, 0.55, 0.57], np.float32) * 0.65
                if roto:
                    h = sel & (r < 0.55 + 0.12 * np.sin(a * 7.0 + 1.3))
                    col[h] = np.array([0.03, 0.03, 0.035], np.float32)
        # molduras del vidrio
        frame = (z > belt - 0.08) & (z < belt + 0.10) & side
        col[frame] = col[frame] * 0.35
        # puertas: juntas verticales y manijas
        for dy in doors:
            seam = side & (np.abs(y - dy) < 0.045) & (z > 1.2) & (z < belt + 1.6)
            col[seam] = col[seam] * 0.30
        for hy in (doors[0] + 1.7, doors[1] + 1.7):
            hnd = side & (np.abs(y - hy) < 0.35) & (np.abs(z - (belt - 0.35)) < 0.10)
            col[hnd] = np.array([0.55, 0.55, 0.52], np.float32)
        return col
    return f


STY = dict(var=0.10, stroke=(1, 3, 1), stroke_scale=3.5, blotch=0.12, ao=0.55, ao_tint='#0b0d12', light=0.24, grime=0.38, grime_col='#2a241d',
           dust=0.25, dust_col='#8a7f6a', edge_col='#c6c0b0', edge=0.8, edge_th=0.04, edge_break=0.4)
STYLES = {
    'pintura_azul': dict(base='#2c5f8e', rust=0.55, seed=3, **STY),
    'pintura_roja': dict(base='#8e2c27', rust=0.45, seed=5, **STY),
    'pintura_blanca': dict(base='#c3c2b8', rust=0.40, seed=7, **STY),
    'pintura_verde': dict(base='#4a6b3a', rust=0.55, seed=9, **STY),
    'pintura_negra': dict(base='#1c1b1a', rust=0.10, seed=11, **{**STY, 'grime': 0.55, 'dust': 0.35, 'edge_col': '#4a4640', 'edge': 0.5}),
    # quemado: chapa sin pintura, oxido naranja en manchas, hollin y ceniza (no un coche negro)
    'quemado': dict(base='#3a2e26', var=0.14, stroke=(1, 3, 1), stroke_scale=3.5, blotch=0.22, ao=0.6, ao_tint='#0b0a09', light=0.20,
                    rust=0.85, grime=0.60, grime_col='#151210', dust=0.35, dust_col='#8a8278', edge_col='#7a5a40', edge=0.6, edge_th=0.04,
                    edge_break=0.5, seed=31),
    'cromo': dict(base='#7d7f80', var=0.10, stroke=(1, 4, 1), stroke_scale=5, ao=0.55, edge_col='#d6d8d8', edge=0.8, rust=0.40, grime=0.35, seed=13),
    'goma': dict(base='#201f1e', var=0.08, stroke=(1, 1, 1), stroke_scale=6, ao=0.5, edge_col='#4a4846', edge=0.5, grime=0.30, dust=0.30, dust_col='#6a6256', seed=15),
    'llanta': dict(base='#6f7173', var=0.10, stroke=(1, 1, 1), stroke_scale=6, ao=0.6, edge_col='#b8babb', edge=0.7, rust=0.50, grime=0.30, seed=17),
    'faro': dict(base='#cfd0b8', var=0.08, ao=0.4, edge_col='#f0f0e0', edge=0.6, grime=0.30, seed=19),
    'luz_t': dict(base='#8a1f1a', var=0.08, ao=0.4, edge_col='#c85a50', edge=0.6, grime=0.30, seed=21),
    'interior': dict(base='#1a1a1c', var=0.06, ao=0.3, seed=23),
    'madera': dict(base='#6d4f33', var=0.15, stroke=(8, 1, 1), stroke_scale=6, blotch=0.12, ao=0.6, edge_col='#a88358', edge=0.7, grime=0.35, dust=0.15, seed=25),
    'chatarra': dict(base='#5d4b3c', var=0.15, stroke=(1, 1, 1), stroke_scale=5, blotch=0.15, ao=0.6, rust=0.5, grime=0.35, edge_col='#9a8870', edge=0.6, seed=27),
    'placa': dict(base='#cfcbb6', var=0.06, ao=0.4, edge_col='#f0eed8', edge=0.6, grime=0.35, seed=29),
}
cat = Z.Cat('Vehiculos', OUT, STYLES)
XF = {}


def with_xf(f):
    """La pintura se escribe para el coche en su posicion normal; si la pieza se roto (volcado) se deshace la rotacion antes."""
    def g(P, msk, pos, nrm, col):
        if XF.get('R') is None:
            return f(P, msk, pos, nrm, col)
        Rinv = np.array(XF['R'].to_3x3().inverted())
        p = (pos - np.array(XF['t'])) @ Rinv.T
        n = nrm @ Rinv.T
        return f(P, msk, p, n, col)
    return g


def sedan(name_mat, rot_deg=(0, 0, 0), burnt=False, flat=False, hood_open=False, no_door=False):
    def build(C):
        XF.clear()
        mb = A.MB('Sedan')
        M = name_mat
        # carroceria baja (perfil lateral) y cabina
        lower = [(-7.5, 1.0), (-7.3, 3.0), (-4.6, 3.25), (-3.3, 3.4), (3.3, 3.4), (5.0, 3.15), (7.1, 2.95), (7.5, 2.35), (7.5, 1.0)]
        mb.prism([(y, z) for (y, z) in lower], -3.0, 3.0, M, plane='YZ', bevel=0.16)
        cab = [(-3.4, 3.4), (-2.3, 5.1), (1.9, 5.1), (3.3, 3.4)]
        mb.prism(cab, -2.55, 2.55, M, plane='YZ', bevel=0.12)
        if hood_open:
            mk = mb.mark()
            mb.box((0, 0, 0), (5.6, 4.6, 0.3), M, bevel=0.05)
            R = Euler([math.radians(a) for a in (-48, 0, 0)], 'XYZ').to_matrix().to_4x4()
            mb.xform_since(mk, Matrix.Translation(Vector((0, 5.6, 4.0))) @ R)
        # parachoques, faros, luces, matricula, espejos, rejilla
        mb.box((0, 7.65, 1.55), (6.2, 0.5, 0.75), 'cromo', bevel=0.12)
        mb.box((0, -7.65, 1.55), (6.2, 0.5, 0.75), 'cromo', bevel=0.12)
        for sx in (-1, 1):
            mb.box((sx * 2.25, 7.58, 2.75), (1.15, 0.3, 0.6), 'faro', bevel=0.06)
            mb.box((sx * 2.4, -7.52, 2.8), (1.0, 0.3, 0.55), 'luz_t', bevel=0.06)
            mb.box((sx * 3.1, 2.7, 3.7), (0.35, 0.6, 0.45), M, bevel=0.05)
        mb.box((0, -7.6, 2.3), (1.6, 0.14, 0.55), 'placa', bevel=0.03)
        mb.box((0, 7.62, 2.3), (4.0, 0.16, 0.45), 'cromo', bevel=0.04)
        # ruedas
        for wy in (-4.6, 4.6):
            for sx in (-1, 1):
                r = 1.25
                if burnt:
                    mb.cyl((sx * 2.5, wy, 1.0), (sx * 3.1, wy, 1.0), 0.95, 8, 'llanta', rot=0.0)
                    continue
                zc = r if not (flat and wy < 0 and sx < 0) else 0.95
                rr = r if zc == r else 1.0
                mb.cyl((sx * 2.55, wy, zc), (sx * 3.45, wy, zc), rr, 8, 'goma', rot=0.0)
                mb.cyl((sx * 3.40, wy, zc), (sx * 3.50, wy, zc), rr * 0.55, 8, 'llanta', rot=0.0)
        ob = mb.finish(C)
        if rot_deg != (0, 0, 0):
            Rm = Euler([math.radians(a) for a in rot_deg], 'XYZ').to_matrix().to_4x4()
            ob.data.transform(Rm)
            # apoyar sobre el suelo
            zs = [v.co.z for v in ob.data.vertices]
            ob.data.transform(Matrix.Translation(Vector((0, 0, -min(zs)))))
            XF['R'] = Rm
            XF['t'] = (0.0, 0.0, -min(zs))
        return ob
    return build


def pickup(C):
    mb = A.MB('Pickup')
    M = 'pintura_verde'
    cab = [(-3.0, 1.1), (-3.0, 3.6), (-1.8, 5.5), (2.1, 5.5), (3.4, 3.75), (8.0, 3.4), (8.3, 2.5), (8.3, 1.1)]
    mb.prism(cab, -3.1, 3.1, M, plane='YZ', bevel=0.16)
    # caja de carga abierta
    mb.box((0, -5.8, 2.1), (6.2, 5.6, 0.4), M, bevel=0.06)
    for sx in (-1, 1):
        mb.box((sx * 3.0, -5.8, 3.0), (0.4, 5.6, 1.6), M, bevel=0.06)
    mb.box((0, -8.55, 3.0), (6.2, 0.4, 1.6), M, bevel=0.06)
    mb.box((0, -3.3, 3.0), (6.2, 0.4, 1.6), M, bevel=0.06)
    # carga: tablones y cajas
    mb.box((-1.0, -6.0, 2.7), (2.4, 2.0, 1.3), 'madera', bevel=0.06)
    mb.box((1.2, -5.2, 2.6), (1.8, 1.6, 1.1), 'chatarra', bevel=0.06)
    mk = mb.mark(); mb.box((0, 0, 0), (0.5, 4.8, 0.3), 'madera', bevel=0.03)
    mb.xform_since(mk, Matrix.Translation(Vector((0.4, -6.2, 3.7))) @ Euler((math.radians(8), 0, math.radians(12)), 'XYZ').to_matrix().to_4x4())
    mb.box((0, 8.4, 1.5), (6.4, 0.5, 0.75), 'cromo', bevel=0.12)
    mb.box((0, -8.9, 1.5), (6.4, 0.5, 0.7), 'cromo', bevel=0.12)
    for sx in (-1, 1):
        mb.box((sx * 2.4, 8.3, 2.7), (1.2, 0.3, 0.6), 'faro', bevel=0.06)
        mb.box((sx * 2.6, -8.78, 2.9), (0.9, 0.3, 0.55), 'luz_t', bevel=0.06)
        mb.box((sx * 3.3, 1.8, 3.9), (0.35, 0.6, 0.45), M, bevel=0.05)
    for wy in (-5.2, 5.3):
        for sx in (-1, 1):
            mb.cyl((sx * 2.6, wy, 1.35), (sx * 3.55, wy, 1.35), 1.35, 8, 'goma', rot=0.0)
            mb.cyl((sx * 3.5, wy, 1.35), (sx * 3.6, wy, 1.35), 0.75, 8, 'llanta', rot=0.0)
    return mb.finish(C)


def furgoneta(C):
    mb = A.MB('Furgoneta')
    M = 'pintura_blanca'
    body = [(-8.6, 1.2), (-8.6, 7.2), (3.6, 7.2), (6.2, 5.6), (8.2, 4.6), (8.4, 3.0), (8.4, 1.2)]
    mb.prism(body, -3.25, 3.25, M, plane='YZ', bevel=0.2)
    mb.box((0, 8.55, 1.6), (6.6, 0.5, 0.8), 'cromo', bevel=0.12)
    mb.box((0, -8.8, 1.6), (6.6, 0.5, 0.8), 'cromo', bevel=0.12)
    for sx in (-1, 1):
        mb.box((sx * 2.5, 8.46, 3.0), (1.2, 0.3, 0.7), 'faro', bevel=0.06)
        mb.box((sx * 2.7, -8.7, 3.2), (0.8, 0.3, 1.2), 'luz_t', bevel=0.06)
        mb.box((sx * 3.5, 5.0, 5.0), (0.35, 0.6, 0.55), M, bevel=0.05)
    mb.box((0, -8.95, 4.2), (4.6, 0.12, 3.8), M, bevel=0.03)        # puertas traseras (relieve)
    mb.box((0, 0.5, 7.5), (5.0, 11.0, 0.35), 'chatarra', bevel=0.04) # baca
    for wy in (-5.6, 5.6):
        for sx in (-1, 1):
            mb.cyl((sx * 2.6, wy, 1.4), (sx * 3.6, wy, 1.4), 1.4, 8, 'goma', rot=0.0)
            mb.cyl((sx * 3.55, wy, 1.4), (sx * 3.65, wy, 1.4), 0.8, 8, 'llanta', rot=0.0)
    return mb.finish(C)


def van_extra(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    side = np.abs(nrm[:, 0]) > 0.6
    for wy in (-5.6, 5.6):
        arch = side & (ell(y, z, wy, 1.4, 1.9, 1.9) < 1)
        col[arch] = col[arch] * 0.22
    # parabrisas
    wf = (nrm[:, 1] > 0.25) & (nrm[:, 2] > 0.2) & (z > 4.6)
    col[wf] = np.array([0.10, 0.14, 0.16], np.float32) * (0.8 + 0.6 * smooth(0.4, 0.6, A.fbm(pos * 0.7 + 3.0, 2, 211)))[wf][:, None]
    cr = wf & (np.abs(A.fbm(pos * 1.7 + 4.0, 3, 213) - 0.5) < 0.02)
    col[cr] = np.array([0.55, 0.60, 0.62], np.float32)
    # ventana lateral de cabina y puerta corrediza
    wl = side & (y > 3.0) & (y < 6.3) & (z > 4.6) & (z < 6.2)
    col[wl] = np.array([0.10, 0.14, 0.16], np.float32)
    for dy in (2.8, -3.4, 0.0):
        seam = side & (np.abs(y - dy) < 0.05) & (z > 1.4) & (z < 7.0)
        col[seam] = col[seam] * 0.3
    # franja de pintura descolorida y marcas
    band = side & (z > 3.3) & (z < 4.2)
    col[band] = col[band] * 0.55 + np.array([0.55, 0.15, 0.12], np.float32) * 0.45
    return col


def pickup_extra(P, msk, pos, nrm, col):
    return car_paint(belt=3.75, wheel_y=(-5.2, 5.3), wheel_z=1.35, cabin=(-3.0, 3.4), doors=(-1.2, 1.2, 3.4))(P, msk, pos, nrm, col)


ex_car = with_xf(car_paint())
EX = {k: ex_car for k in ('pintura_azul', 'pintura_roja', 'pintura_negra')}
cat.piece('Coche_Sedan_Oxidado', sedan('pintura_azul', flat=True), size=1024, ao_dist=0.7, bevel_r=0.06, extra=EX)
cat.piece('Coche_Sedan_Quemado', sedan('quemado', burnt=True, hood_open=True), size=1024, ao_dist=0.7, bevel_r=0.06,
          extra={'quemado': with_xf(car_paint(glass_col=(0.025, 0.025, 0.028), smashed=False))})     # sin cristales: hueco negro
cat.piece('Coche_Sedan_Volcado', sedan('pintura_roja', rot_deg=(180, 0, 0)), size=1024, ao_dist=0.7, bevel_r=0.06, extra=EX)
def clear_xf(fn):
    def b(C):
        XF.clear()
        return fn(C)
    return b


cat.piece('Pickup_Abandonada', clear_xf(pickup), size=1024, ao_dist=0.7, bevel_r=0.06, extra={'pintura_verde': with_xf(pickup_extra)})
cat.piece('Furgoneta_Blanca', clear_xf(furgoneta), size=1024, ao_dist=0.8, bevel_r=0.06, extra={'pintura_blanca': with_xf(van_extra)})
cat.previews(dist_k=1.5)
cat.finish()
A.log('vehiculos listos')
