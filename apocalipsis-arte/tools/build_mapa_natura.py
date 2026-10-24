# Escombros y vegetacion invasora del mapa apocalíptico (cada pieza: un objeto con la base centrada en el origen).
# blender -b --factory-startup -P build_mapa_natura.py
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
OUT = os.path.join(ROOT, 'mapa', 'natura')
rng = np.random.default_rng(31)


def rbox(mb, c, sz, mat, rot=(0, 0, 0), bevel=0.0):
    mk = mb.mark()
    mb.box((0, 0, 0), sz, mat, bevel=bevel)
    R = Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()
    mb.xform_since(mk, Matrix.Translation(Vector(c)) @ R)


def branch(mb, p0, p1, r0, r1, segs, mat):
    mb.cyl(p0, p1, r0, segs, mat, r1=r1, cap0=False)


def blade(mb, base, h, w, lean, rot, mat):
    """Brizna de hierba: prisma triangular fino que se estrecha hacia la punta."""
    x, y, z = base
    mk = mb.mark()
    mb.loft([[(-w, 0.0), (w, 0.0), (0.0, w * 0.8)], [(-w * 0.15, lean * 0.6), (w * 0.15, lean * 0.6), (0.0, lean * 0.6 + w * 0.2)]],
            [0.0, h], mat, plane='XY')
    R = Euler((0, 0, math.radians(rot)), 'XYZ').to_matrix().to_4x4()
    mb.xform_since(mk, Matrix.Translation(Vector((x, y, z))) @ R)


# ------------------------------------------------------------------ pintura
def hoja_x(P, msk, pos, nrm, col):
    # racimos de hojas: ruido posterizado + huecos oscuros + puntas claras
    n1 = A.fbm(pos * 3.2, 3, 801)
    q = np.floor(n1 * 5) / 5
    col *= (0.70 + 0.55 * q)[:, None]
    # huecos entre racimos: mas grandes y suaves (antes eran puntos negros que parecian moho)
    gaps = A.vnoise(pos * 5.0, 803) < 0.20
    col[gaps] = col[gaps] * 0.72
    tips = (A.vnoise(pos * 8.0, 805) > 0.72) & (nrm[:, 2] > -0.2)
    col[tips] = col[tips] * 0.5 + np.array([0.62, 0.70, 0.30], np.float32) * 0.5
    dry = smooth(0.60, 0.78, A.fbm(pos * 1.2 + 4.0, 2, 807))
    col = col * (1 - 0.45 * dry[:, None]) + np.array([0.52, 0.45, 0.22], np.float32) * (0.45 * dry)[:, None]
    return col


def hierba_x(P, msk, pos, nrm, col):
    z = pos[:, 2]
    g = np.clip(z / 2.2, 0, 1)
    tip = np.array([0.70, 0.66, 0.34], np.float32)
    col = col * (0.55 + 0.45 * g)[:, None]
    col = col * (1 - 0.45 * (g ** 2)[:, None]) + tip * (0.45 * g ** 2)[:, None]
    return col


def corteza_x(P, msk, pos, nrm, col):
    a = np.arctan2(pos[:, 1], pos[:, 0])
    gr = 0.5 + 0.5 * np.sin(a * 7.0 + A.fbm(np.stack([pos[:, 0] * 2, pos[:, 1] * 2, pos[:, 2] * 0.4], 1), 3, 811) * 6.0)
    col *= (0.70 + 0.45 * gr)[:, None]
    moss = smooth(0.55, 0.72, A.fbm(pos * 1.5 + 2.0, 3, 813)) * smooth(0.2, 0.8, nrm[:, 1] * 0.5 + 0.5)
    col = col * (1 - 0.5 * moss[:, None]) + np.array([0.28, 0.36, 0.16], np.float32) * (0.5 * moss)[:, None]
    return col


def ladrillo_x(P, msk, pos, nrm, col):
    hv = A._hash(np.floor(pos[:, 0] * 2).astype(np.int64), np.floor(pos[:, 1] * 2).astype(np.int64), np.floor(pos[:, 2] * 3).astype(np.int64), 5)
    col *= (0.85 + 0.3 * hv)[:, None]
    return col


STYLES = dict(E.STYLES)
STYLES.update({
    'escombro': dict(base='#8d877c', var=0.14, stroke=(1, 1, 1), stroke_scale=2.5, blotch=0.15, ao=0.65, ao_tint='#1a1916', light=0.26,
                     grime=0.35, dust=0.35, dust_col='#b0a998', edge_col='#cdc6b6', edge=0.8, edge_th=0.05, face_var=0.06, seed=27),
    'ladrillo': dict(base='#8c4e3a', var=0.12, stroke=(1, 1, 1), stroke_scale=3, blotch=0.12, ao=0.6, ao_tint='#1a110d', light=0.24, grime=0.35,
                     dust=0.30, dust_col='#a89a86', edge_col='#c69078', edge=0.7, face_var=0.05, seed=29),
    'hoja': dict(base='#4a6b2c', var=0.12, stroke=(1, 1, 1), stroke_scale=3, blotch=0.15, ao=0.70, ao_tint='#0b1406', light=0.34, face_var=0.06,
                 edge_col='#8db05a', edge=0.4, seed=31),
    'hoja_seca': dict(base='#6d6a35', var=0.14, stroke=(1, 1, 1), stroke_scale=3, blotch=0.18, ao=0.65, ao_tint='#141006', light=0.32,
                      face_var=0.06, edge_col='#a39a58', edge=0.4, seed=33),
    'hierba': dict(base='#4f6a2a', var=0.12, stroke=(1, 1, 6), stroke_scale=4, ao=0.5, light=0.25, face_var=0.08, seed=35),
    'corteza': dict(base='#5a4636', var=0.12, stroke=(1, 1, 6), stroke_scale=3, blotch=0.12, ao=0.65, ao_tint='#120c08', light=0.26,
                    edge_col='#8f7660', edge=0.5, grime=0.25, face_var=0.04, seed=37),
    'madera_vieja': dict(base='#6f5841', var=0.16, stroke=(6, 1, 1), stroke_scale=3, tone_steps=5, blotch=0.12, ao=0.6, light=0.26, grime=0.35,
                         dust=0.25, edge_col='#a88a66', edge=0.7, seed=39),
})
EXTRAS = {'hoja': hoja_x, 'hoja_seca': hoja_x, 'hierba': hierba_x, 'corteza': corteza_x, 'ladrillo': ladrillo_x}
cat = Z.Cat('Natura', OUT, STYLES, EXTRAS)


# ------------------------------------------------------------------ piezas
def escombros(size, n_rocks, n_bricks, seed, rebar=2, slab=True):
    def build(C):
        r = np.random.default_rng(seed)
        mb = A.MB('Escombros')
        for i in range(n_rocks):
            a = r.uniform(0, 2 * math.pi)
            d = r.uniform(0, size * 0.42)
            rad = r.uniform(0.6, 1.6) * size / 10.0 * (1.4 - d / size)
            mb.rock((math.cos(a) * d, math.sin(a) * d, rad * 0.45), rad, 'escombro', subdiv=1, seed=int(r.integers(1e6)), jitter=0.35,
                    squash=(1.2, 1.0, 0.65))
        for i in range(n_bricks):
            a = r.uniform(0, 2 * math.pi)
            d = r.uniform(0, size * 0.48)
            rbox(mb, (math.cos(a) * d, math.sin(a) * d, r.uniform(0.15, size * 0.12)), (0.8, 0.4, 0.3), 'ladrillo',
                 (r.uniform(-40, 40), r.uniform(-40, 40), r.uniform(0, 180)))
        if slab:
            rbox(mb, (size * 0.1, -size * 0.05, size * 0.10), (size * 0.45, size * 0.30, 0.45), 'escombro', (r.uniform(-20, 20), 14, r.uniform(0, 90)))
        for k in range(rebar):
            p0 = Vector((r.uniform(-1, 1) * size * 0.2, r.uniform(-1, 1) * size * 0.2, 0.3))
            p1 = p0 + Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(1.2, 2.4))) * size * 0.15
            mb.cyl(p0, p1, 0.08, 5, 'hierro')
        return mb.finish(C)
    return build


def arbusto(C):
    mb = A.MB('Arbusto')
    for i in range(7):
        a = i * 2 * math.pi / 7 + rng.uniform(-0.3, 0.3)
        d = rng.uniform(0.5, 1.6) if i else 0.0
        rad = rng.uniform(1.0, 1.6)
        mb.rock((math.cos(a) * d, math.sin(a) * d, rad * 0.75), rad, 'hoja' if i % 3 else 'hoja_seca', subdiv=1, seed=100 + i, jitter=0.30,
                squash=(1.0, 1.0, 0.85))
    for i in range(3):
        a = rng.uniform(0, 2 * math.pi)
        branch(mb, (0, 0, 0), (math.cos(a) * 1.8, math.sin(a) * 1.8, 2.6), 0.12, 0.04, 5, 'corteza')
    return mb.finish(C)


def hierba(C):
    mb = A.MB('Hierba')
    for i in range(22):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 1.3)
        blade(mb, (math.cos(a) * d, math.sin(a) * d, 0.0), rng.uniform(1.2, 2.4), rng.uniform(0.07, 0.12), rng.uniform(0.2, 0.7),
              math.degrees(a) + rng.uniform(-40, 40), 'hierba')
    return mb.finish(C)


def arbol_muerto(C):
    mb = A.MB('ArbolMuerto')
    mb.lathe((0, 0, 0), (0, 0, 9.0), [(0.95, 0.0), (0.70, 0.06), (0.55, 0.30), (0.45, 0.62), (0.32, 1.0)], 7, 'corteza', close0=True, close1=False)
    tips = []
    for (z, a, ln) in ((4.0, 20, 4.5), (5.6, 140, 4.0), (7.0, 260, 3.6), (8.2, 60, 3.0), (6.4, 330, 3.2)):
        ar = math.radians(a)
        p0 = Vector((0, 0, z))
        p1 = p0 + Vector((math.cos(ar) * ln, math.sin(ar) * ln, ln * 0.55))
        branch(mb, p0, p1, 0.26, 0.08, 5, 'corteza')
        tips.append((p1, ar))
    for (p1, ar) in tips:
        for da in (-0.6, 0.5):
            p2 = p1 + Vector((math.cos(ar + da) * 1.4, math.sin(ar + da) * 1.4, 0.9))
            branch(mb, p1, p2, 0.08, 0.025, 4, 'corteza')
    mb.cyl((0, 0, 9.0), (0.4, 0.2, 10.4), 0.30, 7, 'corteza', r1=0.10)
    return mb.finish(C)


def arbol_invasor(C):
    mb = A.MB('ArbolInvasor')
    mb.lathe((0, 0, 0), (0, 0, 7.5), [(1.0, 0.0), (0.75, 0.08), (0.55, 0.40), (0.42, 1.0)], 7, 'corteza', close0=True, close1=True)
    for (a, z, ln) in ((40, 5.5, 3.0), (170, 6.2, 3.2), (290, 6.8, 2.8)):
        ar = math.radians(a)
        branch(mb, (0, 0, z), (math.cos(ar) * ln, math.sin(ar) * ln, z + ln * 0.8), 0.28, 0.12, 5, 'corteza')
    for i in range(9):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.0, 3.4)
        rad = rng.uniform(2.0, 3.0)
        mb.rock((math.cos(a) * d, math.sin(a) * d, 9.5 + rng.uniform(-1.2, 1.8)), rad, 'hoja' if i % 4 else 'hoja_seca', subdiv=1,
                seed=200 + i, jitter=0.28, squash=(1.0, 1.0, 0.75))
    return mb.finish(C)


def enredadera(C):
    """Panel de enredadera para colgar en una fachada (plano XZ, grosor en -Y). Origen abajo al centro, pegado al muro en y = 0."""
    mb = A.MB('Enredadera')
    for k in range(4):
        x0 = -4.0 + k * 2.7 + rng.uniform(-0.5, 0.5)
        pts = [Vector((x0 + rng.uniform(-0.8, 0.8), -0.15, z)) for z in (0.0, 3.0, 6.0, 9.0, 11.5)]
        for p0, p1 in zip(pts[:-1], pts[1:]):
            mb.cyl(p0, p1, 0.10, 4, 'corteza', cap0=False)
    for i in range(16):
        x = rng.uniform(-5.0, 5.0)
        z = rng.uniform(0.6, 11.5)
        rad = rng.uniform(0.7, 1.4) * (1.2 - z / 20.0)
        mb.rock((x, -0.30, z), rad, 'hoja' if i % 5 else 'hoja_seca', subdiv=1, seed=300 + i, jitter=0.3, squash=(1.0, 0.35, 0.9))
    return mb.finish(C)


def maleza(C):
    mb = A.MB('Maleza')
    for i in range(10):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.7)
        blade(mb, (math.cos(a) * d, math.sin(a) * d, 0.0), rng.uniform(0.6, 1.2), rng.uniform(0.06, 0.10), rng.uniform(0.2, 0.5),
              math.degrees(a), 'hierba')
    for i in range(3):
        mb.rock((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 0.35), rng.uniform(0.35, 0.55), 'hoja', subdiv=1, seed=400 + i, jitter=0.3,
                squash=(1, 1, 0.7))
    return mb.finish(C)


cat.piece('Escombros_Grande', escombros(10.0, 12, 14, 7, rebar=3), size=1024, ao_dist=0.8, bevel_r=0.05)
cat.piece('Escombros_Pequeno', escombros(5.0, 7, 8, 11, rebar=1, slab=False), size=512, ao_dist=0.5, bevel_r=0.04)
cat.piece('Escombros_Ladrillos', escombros(6.0, 3, 22, 13, rebar=0, slab=True), size=512, ao_dist=0.5, bevel_r=0.04)
cat.piece('Arbusto', arbusto, size=512, ao_dist=0.8, bevel_r=0.05)
cat.piece('Hierba_Alta', hierba, size=512, ao_dist=0.4, bevel_r=0.02)
cat.piece('Maleza', maleza, size=512, ao_dist=0.3, bevel_r=0.02)
cat.piece('Arbol_Muerto', arbol_muerto, size=1024, ao_dist=0.8, bevel_r=0.05)
cat.piece('Arbol_Invasor', arbol_invasor, size=1024, ao_dist=1.0, bevel_r=0.06)
cat.piece('Enredadera_Muro', enredadera, size=1024, ao_dist=0.6, bevel_r=0.04)
cat.previews(dist_k=1.3)
cat.finish()
A.log('natura lista')
