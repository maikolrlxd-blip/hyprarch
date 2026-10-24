# Piezas de calle del mapa apocalíptico: 3 losetas de 60x60 studs con la superficie de la calzada en z = 0.
# blender -b --factory-startup -P build_mapa_calles.py
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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'mapa', 'calles')
cat = Z.Cat('Calles', OUT, E.STYLES, {'asfalto': E.lineas_calle, 'acera': E.acera_x, 'bordillo': E.bordillo_x})


def rot_box(mb, c, sz, mat, rot_deg, bevel=0.0):
    mk = mb.mark()
    mb.box((0, 0, 0), sz, mat, bevel=bevel)
    R = Euler([math.radians(a) for a in rot_deg], 'XYZ').to_matrix().to_4x4()
    mb.xform_since(mk, Matrix.Translation(Vector(c)) @ R)


def sidewalks_straight(mb, y0=18.0, w=12.0, h=0.55):
    for sgn in (-1, 1):
        yc = sgn * (y0 + w / 2)
        mb.box((0, yc, h / 2 - 0.5), (60, w, h + 1.0), 'acera', bevel=0.06, mats={'-y': 'bordillo', '+y': 'bordillo'} if False else None)
        # bordillo: cara vertical hacia la calzada (franja delgada con pintura)
        mb.box((0, sgn * (y0 + 0.28), (h - 0.2) / 2 - 0.0 + 0.0), (60, 0.56, h + 0.2), 'bordillo', bevel=0.05, edges='x')


def calle_recto(C):
    mb = A.MB('Calle_Recto')
    mb.box((0, 0, -0.5), (60, 36, 1.0), 'asfalto', bevel=0.05, edges='x')
    sidewalks_straight(mb)
    # tapa de alcantarilla y rejilla de desague
    mb.cyl((6, -6, -0.02), (6, -6, 0.05), 1.7, 8, 'tapa', rot=0.0)
    mb.box((-12, 17.5, 0.0), (3.0, 0.8, 0.12), 'tapa', bevel=0.03)
    return mb.finish(C)


def calle_cruce(C):
    mb = A.MB('Calle_Cruce')
    mb.box((0, 0, -0.5), (60, 60, 1.0), 'asfalto', bevel=0.05, edges='all')
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = (sx * 24, sy * 24, 0.05)
            mb.box((c[0], c[1], 0.05), (12, 12, 1.2), 'acera', bevel=0.06)
            mb.box((sx * 18.28, sy * 24, 0.05), (0.56, 12, 1.4), 'bordillo', bevel=0.05, edges='y')
            mb.box((sx * 24, sy * 18.28, 0.05), (12, 0.56, 1.4), 'bordillo', bevel=0.05, edges='x')
    mb.cyl((0, 0, -0.02), (0, 0, 0.05), 1.7, 8, 'tapa', rot=0.0)
    return mb.finish(C)


def calle_rota(C):
    mb = A.MB('Calle_Rota')
    # losa con crater en el carril central: cuatro bloques alrededor del foso
    mb.box((-19.5, 0, -0.5), (21, 36, 1.0), 'asfalto', bevel=0.05, edges='x')
    mb.box((19.5, 0, -0.5), (21, 36, 1.0), 'asfalto', bevel=0.05, edges='x')
    mb.box((0, 13.5, -0.5), (18, 9, 1.0), 'asfalto', bevel=0.05, edges='x')
    mb.box((0, -13.5, -0.5), (18, 9, 1.0), 'asfalto', bevel=0.05, edges='x')
    # foso de tierra
    mb.box((0, 0, -2.2), (18.4, 18.4, 0.6), 'tierra', bevel=0.05)
    # paredes del foso (tierra irregular)
    for (c, s_) in (((0, 9.3, -1.2), (18.4, 0.8, 2.2)), ((0, -9.3, -1.2), (18.4, 0.8, 2.2)),
                    ((9.3, 0, -1.2), (0.8, 18.4, 2.2)), ((-9.3, 0, -1.2), (0.8, 18.4, 2.2))):
        mb.box(c, s_, 'tierra', bevel=0.06)
    # placas de asfalto rotas inclinadas dentro del foso
    rot_box(mb, (-3.5, 4.0, -1.1), (7.0, 5.0, 0.7), 'asfalto', (14, -9, 22), 0.04)
    rot_box(mb, (4.0, -3.5, -1.3), (6.0, 6.5, 0.7), 'asfalto', (-18, 10, -35), 0.04)
    rot_box(mb, (-5.5, -5.5, -1.6), (4.5, 3.6, 0.6), 'asfalto', (8, 20, 60), 0.04)
    # barras de refuerzo retorcidas que sobresalen
    for (p0, p1) in (((-7.0, 8.5, -0.9), (-6.0, 4.5, 1.4)), ((8.6, -7.0, -1.0), (5.2, -6.0, 1.6)), ((8.8, 8.8, -1.4), (7.0, 7.0, 0.9))):
        mb.cyl(p0, p1, 0.12, 5, 'hierro')
    # losas sueltas alrededor
    rot_box(mb, (11.5, 11.0, 0.35), (4.0, 3.0, 0.8), 'asfalto', (0, 0, 28), 0.04)
    rot_box(mb, (-12.0, -11.5, 0.3), (3.4, 2.4, 0.7), 'asfalto', (0, 6, -20), 0.04)
    sidewalks_straight(mb)
    return mb.finish(C)


def solar(C):
    """Solar vacio de 60x60 (tierra con hierba rala) a la altura de la acera (z = 0.55)."""
    mb = A.MB('Solar')
    mb.box((0, 0, 0.05), (60, 60, 1.0), 'tierra_solar', bevel=0.05)
    for i in range(6):
        mb.rock((-22 + i * 9 + float(np.random.default_rng(i).uniform(-3, 3)), float(np.random.default_rng(i + 9).uniform(-24, 24)), 0.6),
                0.9 + 0.3 * i % 2, 'escombro_s', subdiv=1, seed=500 + i, jitter=0.35, squash=(1.3, 1.1, 0.55))
    return mb.finish(C)


def tierra_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    top = nrm[:, 2] > 0.7
    g = A.fbm(np.stack([x * 0.12, y * 0.12, x * 0], 1), 4, 151)
    grass = top & (A.smoothstep(0.45, 0.62, g) > 0.5)
    col[grass] = col[grass] * 0.35 + np.array([0.30, 0.38, 0.16], np.float32) * (0.75 + 0.5 * A.vnoise(pos[grass] * 1.3, 153))[:, None] * 0.65
    dry = top & (A.smoothstep(0.62, 0.75, g) > 0.5)
    col[dry] = col[dry] * 0.4 + np.array([0.55, 0.50, 0.30], np.float32) * 0.6
    tracks = top & (np.abs(np.sin(x * 0.18 + 0.4 * np.sin(y * 0.07))) < 0.06)
    col[tracks] = col[tracks] * 0.8
    return col


cat.styles['tierra_solar'] = dict(base='#5e4a35', var=0.14, stroke=(1, 1, 1), stroke_scale=1.0, blotch=0.18, ao=0.6, ao_tint='#140e08', light=0.20,
                                  grime=0.25, grime_col='#2a1d12', dust=0.15, dust_col='#8a6d4c', face_var=0.0, seed=17)
cat.styles['escombro_s'] = dict(base='#8d877c', var=0.14, stroke=(1, 1, 1), stroke_scale=2.5, blotch=0.15, ao=0.65, light=0.26, grime=0.35,
                                dust=0.35, dust_col='#b0a998', edge_col='#cdc6b6', edge=0.8, edge_th=0.05, face_var=0.06, seed=19)
# ref: el maniqui de la vista previa se pone de pie sobre la pieza (en la calzada, z = 0, o sobre el solar, z = 0.55)
cat.piece('Suelo_Solar_60', solar, size=1024, ao_dist=0.6, bevel_r=0.05, extra={'tierra_solar': tierra_x}, ref=(-8, -8, 0.55))
cat.piece('Calle_Recto_60', calle_recto, size=1024, ao_dist=0.5, bevel_r=0.07, ref=(-8, -8, 0))
cat.piece('Calle_Cruce_60', calle_cruce, size=1024, ao_dist=0.5, bevel_r=0.07,
          extra={'asfalto': E.cruce_x}, ref=(-8, -8, 0))
cat.piece('Calle_Rota_60', calle_rota, size=1024, ao_dist=0.8, bevel_r=0.07, ref=(-20, -12, 0))
cat.previews()
cat.finish()
A.log('calles listas')
