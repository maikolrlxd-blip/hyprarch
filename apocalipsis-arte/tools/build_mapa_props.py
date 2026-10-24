# Barricadas y objetos de calle del mapa apocalíptico (cada pieza: un objeto con la base centrada en el origen).
# blender -b --factory-startup -P build_mapa_props.py
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
OUT = os.path.join(ROOT, 'mapa', 'props')
rng = np.random.default_rng(11)


def rbox(mb, c, sz, mat, rot=(0, 0, 0), bevel=0.0, edges='all'):
    mk = mb.mark()
    mb.box((0, 0, 0), sz, mat, bevel=bevel, edges=edges)
    R = Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()
    mb.xform_since(mk, Matrix.Translation(Vector(c)) @ R)


def rcyl(mb, c, r, h, segs, mat, rot=(0, 0, 0), **kw):
    """cilindro vertical de altura h con la base en c, girado con rot (grados)"""
    mk = mb.mark()
    mb.cyl((0, 0, 0), (0, 0, h), r, segs, mat, **kw)
    R = Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()
    mb.xform_since(mk, Matrix.Translation(Vector(c)) @ R)


# ------------------------------------------------------------------ pintura especifica
def saco_x(P, msk, pos, nrm, col):
    # trama de arpillera y costura
    t = (((pos[:, 0] * 9.0) % 1.0) < 0.5) ^ (((pos[:, 2] * 9.0 + pos[:, 1] * 9.0) % 1.0) < 0.5)
    col[t] = col[t] * 0.92
    return col


def hormigon_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    side = np.abs(nrm[:, 1]) > 0.6
    # franjas rojas y blancas desgastadas en la parte alta
    band = side & (z > 1.6) & (z < 2.3)
    rw = ((x + 40.0) % 2.0) < 1.0
    wear = A.fbm(pos * 1.5, 3, 301) > 0.42
    col[band & rw & wear] = col[band & rw & wear] * 0.3 + np.array([0.70, 0.18, 0.15], np.float32) * 0.7
    col[band & ~rw & wear] = col[band & ~rw & wear] * 0.3 + np.array([0.82, 0.80, 0.74], np.float32) * 0.7
    # chorretones de suciedad bajo las franjas y grietas quebradas en zonas (sin manchas de colores)
    drip = side & (z < 1.6) & (A.fbm(np.stack([x * 5.0, z * 0.35, y], 1), 2, 307) > 0.60)
    col[drip] = col[drip] * 0.80
    cr = side & E.zonas(x, z, 0.3, 9, 0.5) & E.grietas(x, z, 0.9, 9, 0.025)
    col[cr] = col[cr] * 0.45
    return col


def caja_x(P, msk, pos, nrm, col):
    # tablones horizontales: juntas oscuras cada 0,5 studs en las caras laterales
    side = np.abs(nrm[:, 2]) < 0.5
    g = side & (np.abs(((pos[:, 2] + 10.0) % 0.5) - 0.25) > 0.215)
    col[g] = col[g] * 0.55
    return col


def alto_x(P, msk, pos, nrm, col):
    """Senal octogonal roja con borde blanco y la palabra ALTO."""
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    front = nrm[:, 1] < -0.8
    u, v = x - 0.753, z - 7.16
    r = np.maximum(np.abs(u), np.abs(v)) * 0.95 + (np.abs(u) + np.abs(v)) * 0.28
    border = front & (r > 1.05)
    col[border] = np.array([0.86, 0.84, 0.78], np.float32)
    # letras ALTO (fuente 5x7 de ap_armas) centradas
    tu = (u + 1.02) / 0.105
    tv = (0.40 - v) / 0.105
    m = front & (tu >= 0) & (tu < 24) & (tv >= 0) & (tv < 7)
    if m.any():
        iu, iv = np.floor(tu[m]).astype(int), np.floor(tv[m]).astype(int)
        hit = np.zeros(iu.shape, bool)
        for i, ch in enumerate('ALTO'):
            g = W._G[ch]
            for rr, row in enumerate(g):
                for cc, px in enumerate(row):
                    if px == '#':
                        hit |= (iu == i * 6 + cc) & (iv == rr)
        idx = np.where(m)[0][hit]
        col[idx] = np.array([0.88, 0.86, 0.80], np.float32)
    back = nrm[:, 1] > 0.8
    col[back] = col[back] * 0.25 + np.array([0.45, 0.46, 0.46], np.float32) * 0.75
    return col


def semaforo_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    front = nrm[:, 1] < -0.8
    for zc, c_ in ((13.2, (0.35, 0.05, 0.04)), (12.2, (0.38, 0.28, 0.04)), (11.2, (0.05, 0.25, 0.08))):
        m = front & (((x - 3.6) ** 2 + (z - zc) ** 2) < 0.30 ** 2)
        col[m] = np.array(c_, np.float32) * (0.7 + 0.6 * A.vnoise(pos[m] * 12, 7))[:, None]
    return col


def barril_x(P, msk, pos, nrm, col):
    z = pos[:, 2]
    rings = ((z % 1.32) < 0.08) & (np.abs(nrm[:, 2]) < 0.5)
    col[rings] = col[rings] * 0.55
    # simbolo de peligro generico (rombo amarillo) en un lado
    side = (nrm[:, 1] < -0.6)
    d = np.abs(pos[:, 0] - 0.0) + np.abs(z - 1.9)
    m = side & (d < 0.42)
    col[m] = col[m] * 0.3 + np.array([0.80, 0.66, 0.12], np.float32) * 0.7
    return col


STYLES = dict(E.STYLES)
STYLES.update({
    'saco': dict(base='#8f7a55', var=0.12, stroke=(1, 1, 1), stroke_scale=4, blotch=0.12, ao=0.65, ao_tint='#1e160c', light=0.28,
                 grime=0.35, grime_col='#4a3b28', dust=0.25, dust_col='#b4a07a', edge_col='#bfa77c', edge=0.5, seed=31),
    'madera_vieja': dict(base='#7a6248', var=0.16, stroke=(6, 1, 1), stroke_scale=4, tone_steps=5, blotch=0.12, ao=0.6, ao_tint='#1a120a',
                         light=0.26, grime=0.35, grime_col='#2f2318', dust=0.2, edge_col='#b39470', edge=0.8, edge_th=0.04, seed=33),
    'hormigon': dict(base='#a39f94', var=0.10, stroke=(2, 2, 1), stroke_scale=3, blotch=0.12, ao=0.6, ao_tint='#1d1c1a', light=0.24,
                     grime=0.35, grime_col='#4d4a42', dust=0.15, edge_col='#cfcbbf', edge=0.9, edge_th=0.04, seed=35),
    'metal_pintado': dict(base='#3d6a4f', var=0.12, stroke=(1, 3, 1), stroke_scale=3.5, blotch=0.12, ao=0.6, ao_tint='#0c1410',
                          light=0.26, rust=0.55, grime=0.35, grime_col='#2b261e', dust=0.2, edge_col='#a9b3a2', edge=0.9, edge_th=0.04, seed=37),
    'metal_gris': dict(base='#6c7074', var=0.10, stroke=(1, 1, 4), stroke_scale=3.5, blotch=0.10, ao=0.6, ao_tint='#121417', light=0.26,
                       rust=0.40, grime=0.30, dust=0.15, edge_col='#c3c7cb', edge=0.9, edge_th=0.04, seed=39),
    'rojo_senal': dict(base='#a12a24', var=0.08, stroke=(1, 1, 1), stroke_scale=4, ao=0.5, light=0.2, rust=0.25, grime=0.25,
                       edge_col='#d48a7a', edge=0.6, seed=41),
    'amarillo': dict(base='#c39a2a', var=0.10, stroke=(1, 1, 3), stroke_scale=4, ao=0.55, light=0.24, rust=0.35, grime=0.3,
                     edge_col='#ecd27a', edge=0.8, seed=43),
    'chapa': dict(base='#7d8287', var=0.14, stroke=(1, 1, 6), stroke_scale=3, blotch=0.15, ao=0.6, ao_tint='#121417', light=0.26,
                  rust=0.70, grime=0.35, dust=0.15, edge_col='#c9cdd0', edge=0.8, seed=45),
    'goma': dict(base='#232220', var=0.08, stroke=(1, 1, 1), stroke_scale=6, ao=0.55, edge_col='#4d4a46', edge=0.5, grime=0.30, dust=0.30,
                 dust_col='#6a6256', seed=47),
    'barril': dict(base='#2f4f74', var=0.12, stroke=(1, 1, 4), stroke_scale=4, blotch=0.12, ao=0.6, ao_tint='#0b1018', light=0.26,
                   rust=0.65, grime=0.35, dust=0.2, edge_col='#a8b6c4', edge=0.8, seed=49),
    'cristal_luz': dict(base='#d8d4bf', var=0.06, ao=0.4, edge_col='#ffffff', edge=0.5, grime=0.4, seed=51),
    'interior': dict(base='#151515', var=0.05, ao=0.3, seed=53),
    'bolsa': dict(base='#2c312c', var=0.08, stroke=(1, 1, 1), stroke_scale=4, blotch=0.10, ao=0.5, light=0.32, edge_col='#636c63',
                  edge=0.6, grime=0.2, seed=55),
})
STYLES['caja'] = dict(STYLES['madera_vieja'], seed=57)
EXTRAS = {'saco': saco_x, 'hormigon': hormigon_x, 'barril': barril_x, 'caja': caja_x}
cat = Z.Cat('Props', OUT, STYLES, EXTRAS)


# ------------------------------------------------------------------ piezas
def sacos(C):
    mb = A.MB('Sacos')
    for row, (z, n, off) in enumerate(((0.36, 5, 0.0), (1.02, 5, 1.2), (1.68, 4, 0.6))):
        for i in range(n):
            x = -4.8 + i * 2.4 + off + rng.uniform(-0.15, 0.15)
            rbox(mb, (x, rng.uniform(-0.1, 0.1), z), (2.3, 1.25, 0.72), 'saco', (rng.uniform(-3, 3), rng.uniform(-4, 4), rng.uniform(-6, 6)),
                 bevel=0.22)
    return mb.finish(C)


def barricada_madera(C):
    mb = A.MB('BarricadaMadera')
    for sx in (-1, 1):
        rbox(mb, (sx * 3.2, 0, 1.5), (0.35, 0.35, 3.6), 'madera_vieja', (0, sx * 28, 0), 0.04)
        rbox(mb, (sx * 3.2, 0, 1.5), (0.35, 0.35, 3.6), 'madera_vieja', (0, -sx * 28, 0), 0.04)
    for i, (z, rz) in enumerate(((0.9, 4), (1.9, -3), (2.8, 7))):
        rbox(mb, (rng.uniform(-0.3, 0.3), -0.3, z), (8.6, 0.25, 0.75), 'madera_vieja', (0, rz, rng.uniform(-3, 3)), 0.03)
    # palet apoyado
    for i in range(5):
        rbox(mb, (-1.5 + i * 0.75, 0.9, 1.2), (0.55, 0.18, 2.4), 'madera_vieja', (-12, 0, 0), 0.02)
    rbox(mb, (0.0, 0.75, 0.5), (3.6, 0.3, 0.3), 'madera_vieja', (-12, 0, 0), 0.02)
    rbox(mb, (0.0, 1.0, 1.9), (3.6, 0.3, 0.3), 'madera_vieja', (-12, 0, 0), 0.02)
    return mb.finish(C)


def barrera_hormigon(C):
    mb = A.MB('BarreraHormigon')
    sec = [(-1.2, 0), (1.2, 0), (1.2, 0.3), (0.45, 1.0), (0.35, 2.6), (-0.35, 2.6), (-0.45, 1.0), (-1.2, 0.3)]
    sec_xz = [(y, z) for (y, z) in sec]
    # loft a lo largo de X: planta en YZ -> usamos plane='YZ' con la seccion en (y,z) y grosor en x
    mb.prism(sec_xz, -5.0, 5.0, 'hormigon', plane='YZ', bevel=0.08)
    # trozo roto en un extremo
    rbox(mb, (5.6, 0.5, 0.35), (1.2, 0.9, 0.7), 'hormigon', (8, -6, 20), 0.06)
    mb.cyl((4.0, 0.0, 2.4), (5.4, 0.3, 3.1), 0.06, 5, 'hierro')
    return mb.finish(C)


def contenedor(C):
    mb = A.MB('Contenedor')
    mb.loft([[(-3.0, 0.5), (3.0, 0.5), (3.0, 4.6), (-3.0, 4.6)], [(-3.0, 0.5), (3.0, 0.5), (3.0, 4.6), (-3.0, 4.6)]], [-2.0, 2.0],
            'metal_pintado', plane='XZ', bevel=0.10)
    # borde superior y tapa abierta inclinada
    mb.box((0, 0, 4.7), (6.3, 4.3, 0.25), 'metal_pintado', bevel=0.05)
    rbox(mb, (0, -2.5, 5.9), (6.2, 0.18, 2.6), 'metal_gris', (-25, 0, 0), 0.04)
    mb.box((0, 0, 4.55), (5.9, 3.9, 0.05), 'interior')
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.cyl((sx * 2.6, sy * 1.6, 0.0), (sx * 2.6, sy * 1.6, 0.5), 0.28, 6, 'goma')
    # bolsas de basura asomando
    mb.rock((1.0, 0.6, 4.8), 0.75, 'bolsa', subdiv=1, seed=3, jitter=0.12, squash=(1.25, 1.0, 0.7))
    mb.rock((-1.3, -0.3, 4.75), 0.65, 'bolsa', subdiv=1, seed=5, jitter=0.12, squash=(1.2, 1.05, 0.7))
    return mb.finish(C)


def farola(C):
    mb = A.MB('Farola')
    mb.cyl((0, 0, 0), (0, 0, 0.5), 0.55, 8, 'metal_gris')
    mb.cyl((0, 0, 0.5), (0, 0, 7.0), 0.26, 8, 'metal_gris', cap0=False)
    mb.cyl((0, 0, 7.0), (1.2, 0.3, 12.5), 0.22, 8, 'metal_gris', cap0=False)        # doblada
    mb.cyl((1.2, 0.3, 12.5), (3.6, 0.7, 13.6), 0.18, 8, 'metal_gris', cap0=False)
    rbox(mb, (4.2, 0.8, 13.3), (1.6, 0.8, 0.5), 'metal_gris', (0, 18, 10), 0.05)
    rbox(mb, (4.2, 0.8, 13.0), (1.2, 0.55, 0.12), 'cristal_luz', (0, 18, 10))
    return mb.finish(C)


def hidrante(C):
    mb = A.MB('Hidrante')
    mb.lathe((0, 0, 0), (0, 0, 2.6), [(0.55, 0.0), (0.55, 0.12), (0.42, 0.16), (0.40, 0.80), (0.48, 0.84), (0.46, 0.95), (0.22, 1.0)], 8,
             'rojo_senal', close0=True, close1=True)
    for sx in (-1, 1):
        mb.cyl((sx * 0.38, 0, 1.5), (sx * 0.70, 0, 1.5), 0.17, 6, 'rojo_senal')
    mb.cyl((0, -0.38, 1.25), (0, -0.72, 1.25), 0.22, 6, 'rojo_senal')
    return mb.finish(C)


def barriles(C):
    mb = A.MB('Barriles')
    for (x, y) in ((0, 0), (2.25, 0.4), (1.0, 2.0)):
        mb.cyl((x, y, 0), (x, y, 4.0), 1.05, 10, 'barril', rot=0.0)
    mk = mb.mark()
    mb.cyl((0, 0, -2.0), (0, 0, 2.0), 1.05, 10, 'barril', rot=0.0)
    mb.xform_since(mk, Matrix.Translation(Vector((-2.4, 1.6, 1.05))) @ Euler((math.radians(90), 0, math.radians(30)), 'XYZ').to_matrix().to_4x4())
    return mb.finish(C)


def senal_alto(C):
    mb = A.MB('SenalAlto')
    rcyl(mb, (0, 0, 0), 0.12, 6.3, 6, 'metal_gris', rot=(0, 6, 0))
    pts = [(1.25 * math.cos(math.pi / 8 + i * math.pi / 4), 7.2 + 1.25 * math.sin(math.pi / 8 + i * math.pi / 4)) for i in range(8)]
    mk = mb.mark()
    mb.prism(pts, -0.10, -0.02, 'rojo_senal', plane='XZ')
    mb.xform_since(mk, Euler((0, math.radians(6), 0), 'XYZ').to_matrix().to_4x4())
    return mb.finish(C)


def semaforo(C):
    mb = A.MB('Semaforo')
    mb.cyl((0, 0, 0), (0, 0, 0.5), 0.5, 8, 'metal_gris')
    mb.cyl((0, 0, 0.5), (0, 0, 14.5), 0.24, 8, 'metal_gris', cap0=False)
    mb.cyl((0, 0, 14.0), (5.0, 0, 13.6), 0.16, 6, 'metal_gris')
    rbox(mb, (3.6, 0, 12.2), (1.0, 0.8, 3.0), 'amarillo', (0, 0, 0), 0.06)
    return mb.finish(C)


def cajas(C):
    mb = A.MB('Cajas')
    for (c, s_, r) in (((0, 0, 1.0), (2.0, 2.0, 2.0), 5), ((2.1, 0.3, 0.9), (1.8, 1.8, 1.8), -8), ((1.0, 0.2, 2.9), (1.8, 1.8, 1.8), 14),
                       ((-1.9, 0.6, 0.75), (1.5, 1.5, 1.5), 20)):
        rbox(mb, c, s_, 'caja', (0, 0, r), 0.06)
    return mb.finish(C)


def neumaticos(C):
    mb = A.MB('Neumaticos')
    for i, (x, y, z, rx) in enumerate(((0, 0, 0.0, 0), (0.15, 0.1, 0.62, 0), (-0.1, 0.05, 1.24, 0), (2.4, 0.4, 0.0, 70))):
        mk = mb.mark()
        mb.cyl((0, 0, 0), (0, 0, 0.6), 1.15, 10, 'goma', rot=0.0, inset_cap1=0.45, inset_depth=0.5, inset_mat='interior')
        R = Euler((math.radians(rx), 0, 0), 'XYZ').to_matrix().to_4x4()
        mb.xform_since(mk, Matrix.Translation(Vector((x, y, z + (1.15 if rx else 0)))) @ R)
    return mb.finish(C)


def valla_chapa(C):
    mb = A.MB('VallaChapa')
    for i in range(4):
        x = -4.5 + i * 3.0
        rbox(mb, (x, 0, 3.4), (3.1, 0.12, 6.6), 'chapa', (rng.uniform(-3, 3), rng.uniform(-4, 4), rng.uniform(-3, 3)))
    for x in (-6.1, -1.5, 3.0, 6.1):
        mb.cyl((x, 0.2, 0), (x, 0.2, 7.0), 0.13, 6, 'metal_gris')
    mb.box((0, 0.2, 6.6), (12.4, 0.15, 0.2), 'metal_gris')
    return mb.finish(C)


cat.piece('Barricada_Sacos', sacos, size=1024, ao_dist=0.5, bevel_r=0.08)
cat.piece('Barricada_Madera', barricada_madera, size=1024, ao_dist=0.5, bevel_r=0.05)
cat.piece('Barrera_Hormigon', barrera_hormigon, size=1024, ao_dist=0.5, bevel_r=0.06)
cat.piece('Valla_Chapa', valla_chapa, size=1024, ao_dist=0.6, bevel_r=0.05)
cat.piece('Contenedor_Basura', contenedor, size=1024, ao_dist=0.6, bevel_r=0.06)
cat.piece('Farola_Doblada', farola, size=512, ao_dist=0.5, bevel_r=0.04)
cat.piece('Hidrante', hidrante, size=512, ao_dist=0.25, bevel_r=0.03)
cat.piece('Barriles', barriles, size=1024, ao_dist=0.5, bevel_r=0.05)
cat.piece('Senal_Alto', senal_alto, size=512, ao_dist=0.3, bevel_r=0.03, extra={'rojo_senal': alto_x})
cat.piece('Semaforo_Torcido', semaforo, size=512, ao_dist=0.4, bevel_r=0.04, extra={'amarillo': semaforo_x})
cat.piece('Cajas_Madera', cajas, size=512, ao_dist=0.4, bevel_r=0.05)
cat.piece('Neumaticos', neumaticos, size=512, ao_dist=0.4, bevel_r=0.05)
cat.previews(dist_k=1.25)
cat.finish()
A.log('props listos')
