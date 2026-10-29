# Alas AVANZADAS v0.2 (oscuras con turquesa y pinchos) para "+1 de lanzamiento por segundo", al estilo de Codex:
# plumas-cuchilla escalonadas con ribete oscuro y punta de color, brazo oseo con espinas, placa dorsal con gema, textura pintada a mano.
# blender -b --factory-startup --python-exit-code 1 -P build_alas_avanzadas_v02.py
#   ALAS_FASE=geo   -> solo geometria con colores planos y renders rapidos (para ajustar la silueta y las poses)
#   ALAS_FASE=full  -> textura horneada y pintada, rig, clips, FBX/GLB y renders finales (por defecto)
# Ejes: +Y = delante del personaje, +Z arriba, +X = su derecha. El origen es el punto de montaje en la espalda (BodyBackAttachment);
# las alas quedan detras (y < 0) para no atravesar el torso R15 (profundidad 1).
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'apocalipsis-arte', 'tools'))
import ap_lib as A
import ap_armas as W
import bpy
import numpy as np
from mathutils import Vector, Euler, Matrix

FASE = os.environ.get('ALAS_FASE', 'full')
RENDER = FASE != 'assets'          # 'assets': solo textura, rig, clips y exportacion (sin renders)
OUT = os.path.abspath(os.path.join(HERE, '..', 'alas-avanzadas-v02'))
PREV = os.path.join(OUT, 'previews')
for d in ('', 'texturas', 'clips', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
FBX_FORWARD = 'Z'      # el importador 3D de Studio gira 180 grados los FBX exportados con -Z delante (comprobado con el mapa y las armas de Luto)
SCL = 0.88             # escala final del conjunto: envergadura ~10 studs

A.clean_scene()
bpy.context.scene.render.fps = 30
CM = A.collection('Alas')
CR = A.collection('Ref')
CC = A.collection('Camaras')

# ------------------------------------------------------------------ paleta (obsidiana azulada, turquesa apagado, hueso oscuro)
PAL = {
    'pluma_c': '#2a3558', 'pluma_s': '#222b4a', 'pluma_p': '#1b2340', 'pluma_u': '#131929',
    'borde': '#0b0f1c', 'punta': '#1d9186', 'punta_m': '#13706a', 'punta_d': '#0d4d4c', 'punta_borde': '#093a39',
    'hueso': '#454e6e', 'espina': '#323953', 'espina_punta': '#27a899',
    'placa': '#28304c', 'gema': '#34c8b5', 'aro': '#177f76', 'remache': '#5a6890',
}

# ------------------------------------------------------------------ arco del ala (ala derecha; la izquierda es el espejo en X)
ARM = {'S': (0.50, -0.70, -0.05), 'E': (1.25, -0.92, 1.25), 'W': (2.55, -1.20, 2.05), 'H': (3.55, -1.50, 1.55),
       'C': (4.45, -1.72, 0.80)}
PTS = [Vector(ARM[k]) for k in 'SEWH']
SEG = [(PTS[i + 1] - PTS[i]).length for i in range(3)]
TOTAL = sum(SEG)
T_E = SEG[0] / TOTAL
T_W = (SEG[0] + SEG[1]) / TOTAL


def arm_at(t):
    s = min(max(t, 0.0), 1.0) * TOTAL
    for i, L in enumerate(SEG):
        if s <= L or i == 2:
            f = min(s / L, 1.0)
            return PTS[i] + (PTS[i + 1] - PTS[i]) * f, (PTS[i + 1] - PTS[i]).normalized()
        s -= L


def bone_of(t):
    return 'Wing' if t < T_E else ('Mid' if t < T_W else 'Tip')


MBS = {}


def mb_for(bone, side):
    key = 'Root' if bone == 'Root' else '%s_%s' % (bone, 'R' if side > 0 else 'L')
    if key not in MBS:
        MBS[key] = A.MB('G_' + key)
    return MBS[key]


def P3(side, v):
    return Vector((side * v[0], v[1], v[2]))


# ------------------------------------------------------------------ pieza: pluma lanceolada (base oscura + punta de color)
ROW = {   # off: profundidad respecto al brazo (negativo = hacia quien mira desde atras), cut: donde empieza la punta de color
    'c': dict(off=-0.14, T=0.085, cut=0.76, lean=0.10, tip='punta_d', ph=0.0),
    's': dict(off=-0.04, T=0.085, cut=0.72, lean=-0.08, tip='punta_m', ph=1.7),
    'p': dict(off=0.07, T=0.085, cut=0.68, lean=0.06, tip='punta', ph=3.1),
    'u': dict(off=0.12, T=0.09, cut=0.74, lean=-0.05, tip='punta_d', ph=4.4),     # la fila de debajo toca a la de las primarias (con 0,18 quedaba suelta 0,09-0,14 studs); 0,12 es el escalon con menos caras casi coplanares sin piezas sueltas
}
if os.environ.get('ALAS_U_OFF'):
    ROW['u']['off'] = float(os.environ['ALAS_U_OFF'])      # solo para buscar el escalon de la fila de debajo (ALAS_FASE=check)
BLADES = []     # datos de cada pluma (en el espacio de diseno, antes de SCL) para pintar el eje y las barbas


def blade(side, row, i, t, theta, L, w):
    r = ROW[row]
    att, _ = arm_at(t)
    ax, ay, az = att.x, att.y, att.z
    th = math.radians(theta)
    d = (math.sin(th), -math.cos(th))
    n = (math.cos(th), math.sin(th))
    L = L * (1 + 0.07 * math.sin(i * 2.3 + r['ph']))      # largos irregulares: el borde inferior no es un peine
    h = w / 2

    def pt(u, v):
        return (side * (ax + u * n[0] + v * d[0]), az + u * n[1] + v * d[1])
    cut, lean = r['cut'], r['lean'] * (1 if i % 2 == 0 else -1)
    hc = 1.0 - 0.22 * (cut - 0.30) / 0.55                  # semiancho en el corte (la pluma se afina hacia la punta)
    v0 = -0.14
    base = [pt(-0.62 * h, v0), pt(0.62 * h, v0), pt(h, 0.30 * L), pt(hc * h, cut * L), pt(-hc * h, cut * L), pt(-h, 0.30 * L)]
    tip = [pt(-hc * h, cut * L), pt(hc * h, cut * L), pt(0.70 * h, 0.90 * L), pt((0.12 + lean) * h, L), pt(-0.78 * h, 0.94 * L)]
    y0 = ay + r['off'] - r['T'] / 2 - 0.012 * i
    y1 = y0 + r['T']
    mb = mb_for(bone_of(t), side)
    mb.prism(base, y0, y1, 'pluma_' + row, plane='XZ', side_mat='borde')
    mb.prism(tip, y0 - 0.012, y1 + 0.012, r['tip'], plane='XZ', side_mat='punta_borde')
    BLADES.append(dict(side=side, row=row, ax=ax, az=az, th=th, L=L, h=h, cut=cut, y0=y0, y1=y1))


# (t a lo largo del brazo, giro hacia fuera en grados, largo, ancho): las interiores son cortas para dejar ver el cuerpo
COV = [(0.10, 0, 1.1, .66), (0.22, 3, 1.4, .66), (0.34, 7, 1.8, .66), (0.46, 11, 2.1, .66), (0.58, 15, 2.3, .66),
       (0.70, 20, 2.3, .64), (0.82, 27, 2.1, .62), (0.94, 34, 1.7, .58)]
SEC = [(0.10, 2, 1.8, .62), (0.21, 5, 2.5, .62), (0.33, 8, 3.2, .62), (0.45, 12, 3.9, .62), (0.57, 16, 4.4, .62),
       (0.69, 21, 4.7, .60), (0.80, 26, 4.5, .58)]
PRI = [(0.72, 16, 4.9, .54), (0.78, 21, 5.0, .54), (0.84, 26, 4.8, .52), (0.90, 31, 4.4, .50), (0.95, 36, 3.8, .48),
       (1.00, 40, 3.1, .46)]
UND = [(0.08, 4, 2.6, .40), (0.20, 7, 3.4, .40), (0.32, 10, 4.2, .40), (0.44, 14, 4.9, .40), (0.56, 18, 5.5, .40),
       (0.68, 23, 5.8, .38), (0.78, 28, 5.6, .36)]


def plumas(side):
    for row, lst in (('u', UND), ('c', COV), ('s', SEC), ('p', PRI)):
        for i, (t, th, L, w) in enumerate(lst):
            blade(side, row, i, t, th, L, w)


# ------------------------------------------------------------------ pieza: espinas y cuernos (base oscura, punta turquesa)
def thorn(mb, p0, p1, r0, frac=0.64):
    p0, p1 = Vector(p0), Vector(p1)
    pm = p0 + (p1 - p0) * frac
    rm = r0 * (1 - frac) + 0.02 * frac
    mb.cyl(p0, pm, r0, 4, 'espina', r1=rm, cap0=True, cap1=False, rot=math.pi / 4)
    mb.cyl(pm, p1, rm, 4, 'espina_punta', r1=0.015, cap0=False, cap1=True, rot=math.pi / 4)


def horn(mb, pts, r0):
    """Cuerno curvo: cadena de tramos que adelgazan; el ultimo es turquesa."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for k in range(n):
        ra = r0 * (1 - 0.8 * k / n)
        rb = r0 * (1 - 0.8 * (k + 1) / n) if k < n - 1 else 0.015
        mb.cyl(pts[k], pts[k + 1], ra, 4, 'espina_punta' if k == n - 1 else 'espina', r1=rb, cap0=(k == 0), cap1=True, rot=math.pi / 4)


ADY = Vector((0, -0.30, 0))     # el brazo va por delante de las plumas (hacia quien mira desde atras): se ve el arco oseo


def espinas(side):
    up = Vector((0, 0, 1))
    for t, L, r0 in ((0.12, 0.70, 0.17), (0.25, 0.95, 0.20), (0.40, 1.10, 0.22), (0.55, 1.20, 0.22), (0.66, 1.10, 0.20),
                     (0.86, 0.85, 0.16), (0.95, 0.60, 0.13)):
        p, tg = arm_at(t)
        nrm = Vector((-tg.z, 0, tg.x)).normalized()
        d = (nrm * 0.45 + up * 0.45 + tg * 0.55 + Vector((0, -0.35, 0))).normalized()
        mb = mb_for(bone_of(t), side)
        b = p + ADY + Vector((0, 0, 0.12))
        thorn(mb, P3(side, b), P3(side, b + d * L), r0)
    # cuerno grande de la muneca (el punto mas alto) y garra de la mano
    Wp = Vector(ARM['W']) + ADY + Vector((0, 0, 0.14))
    horn(mb_for('Tip', side), [P3(side, Wp), P3(side, Wp + Vector((0.12, -0.20, 0.70))),
                              P3(side, Wp + Vector((0.55, -0.50, 1.20))), P3(side, Wp + Vector((1.20, -0.62, 1.38)))], 0.27)
    Hp = Vector(ARM['H']) + ADY
    horn(mb_for('Tip', side), [P3(side, Hp), P3(side, Vector((4.05, -1.62, 1.30)) + ADY), P3(side, Vector(ARM['C']) + ADY)], 0.21)


# ------------------------------------------------------------------ pieza: brazo oseo (hexagonal, afinado) con anillos y gemas en los codos
def articulacion(mb, c, r):
    """Anillo turquesa oscuro con una pequena gema al centro (mira hacia quien ve el ala desde atras)."""
    mb.cyl(c + Vector((0, -0.26, 0)), c + Vector((0, 0.16, 0)), r, 8, 'aro', rot=0.0)
    mb.cyl(c + Vector((0, -0.34, 0)), c + Vector((0, -0.20, 0)), r * 0.42, 4, 'gema', r1=r * 0.30, rot=math.pi / 4)


def brazo(side):
    S, E, Wr, H = [P3(side, Vector(ARM[k]) + ADY) for k in 'SEWH']
    mb = mb_for('Wing', side)
    mb.cyl(S - (E - S).normalized() * 0.10, E, 0.28, 6, 'hueso', r1=0.23, cap0=True, cap1=False, rot=0.0)
    articulacion(mb, S, 0.22)
    mm = mb_for('Mid', side)
    mm.cyl(E, Wr, 0.23, 6, 'hueso', r1=0.19, cap0=False, cap1=False, rot=0.0)
    articulacion(mm, E, 0.30)
    mt = mb_for('Tip', side)
    mt.cyl(Wr, H, 0.19, 6, 'hueso', r1=0.12, cap0=False, cap1=True, rot=0.0)
    articulacion(mt, Wr, 0.27)


# ------------------------------------------------------------------ pieza: placa dorsal con gema
def placa():
    mb = mb_for('Root', 1)
    plate = [(-0.55, 0.30), (0.55, 0.30), (0.78, 0.05), (0.78, -0.60), (0.40, -1.00), (-0.40, -1.00), (-0.78, -0.60), (-0.78, 0.05)]
    mb.prism(plate, -0.58, -0.04, 'placa', plane='XZ', side_mat='borde')
    mb.prism([(0.0, -0.80), (0.38, -0.30), (0.0, 0.20), (-0.38, -0.30)], -0.64, -0.57, 'aro', plane='XZ')
    mb.prism([(0.0, -0.66), (0.26, -0.30), (0.0, 0.06), (-0.26, -0.30)], -0.72, -0.62, 'gema', plane='XZ', side_mat='aro')
    for x in (-0.58, 0.58):
        mb.prism([(x - 0.07, 0.14), (x + 0.07, 0.14), (x + 0.07, 0.00), (x - 0.07, 0.00)], -0.64, -0.56, 'remache', plane='XZ')
    for x, L in ((-0.32, 0.55), (0.0, 0.75), (0.32, 0.55)):
        thorn(mb, (x, -0.34, 0.26), (x, -0.40, 0.26 + L), 0.11)


for side in (1, -1):
    plumas(side)
    brazo(side)
    espinas(side)
placa()

# ------------------------------------------------------------------ rig: Root, Wing/Mid/Tip por lado (los de Codex son Root, Wing, Tip)
bones = [('Root', (0, -0.30 * SCL, 0.0), None, 0.5 * SCL)]
for side, suf in ((1, 'R'), (-1, 'L')):
    for nm, key, par in (('Wing', 'S', 'Root'), ('Mid', 'E', 'Wing_' + suf), ('Tip', 'W', 'Mid_' + suf)):
        bones.append(('%s_%s' % (nm, suf), tuple(P3(side, ARM[key]) * SCL), par, 0.8 * SCL))
rig = A.make_armature('AlasAvanzadas_Rig', bones, CM)
parts = []
for key, mb in MBS.items():
    o = mb.finish(CM)
    A.skin_rigid(o, rig, key)
    parts.append(o)
A.select_only(parts)
bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
ob.name = 'AlasAvanzadas'
ob.data.name = 'AlasAvanzadas'
ob.data.transform(Matrix.Scale(SCL, 4))
ob.data.update()
TRIS = A.tris([ob])
mn = Vector([min(v.co[a] for v in ob.data.vertices) for a in range(3)])      # desde los vertices: bound_box no se refresca tras transform()
mx = Vector([max(v.co[a] for v in ob.data.vertices) for a in range(3)])
A.log('triangulos', TRIS, 'envergadura %.2f  alto %.2f..%.2f  fondo %.2f..%.2f' % (mx.x - mn.x, mn.z, mx.z, mn.y, mx.y))
BOUNDS = dict(envergadura=round(mx.x - mn.x, 2), z_min=round(mn.z, 2), z_max=round(mx.z, 2), y_min=round(mn.y, 2), y_max=round(mx.y, 2))
if FASE == 'check':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mas1_ave import piezas_sueltas, caras_coplanares
    _s, _n = piezas_sueltas(ob)
    _p, _e = caras_coplanares(ob, maximo=0)
    _p3, _ = caras_coplanares(ob, eps=0.003, maximo=0)
    A.log('COMPROBACION off_u=%s sueltas=%d coplanares(<=0,008)=%d coplanares(<=0,003)=%d' % (ROW['u']['off'], len(_s), _p, _p3))
    sys.exit(0)


# ------------------------------------------------------------------ pose (para los renders y para los clips)
def pose(wing=(0, 0, 0), mid=(0, 0, 0), tip=(0, 0, 0), bob=0.0):
    """Cada tupla es (aleteo, barrido, cabeceo) en grados, con el convenio del ala derecha: aleteo + baja la punta,
    barrido + la lleva hacia atras. El ala izquierda sale espejada."""
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
    for s, suf in ((1, 'R'), (-1, 'L')):
        for nm, (roll, yaw, pit) in (('Wing', wing), ('Mid', mid), ('Tip', tip)):
            rig.pose.bones['%s_%s' % (nm, suf)].rotation_euler = Euler((math.radians(pit), math.radians(s * roll), math.radians(-s * yaw)), 'XYZ')
    rig.pose.bones['Root'].location = (0, 0, bob)
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ escena de comprobacion: maniqui R15 de 5,2 studs, plataforma, luces
MOUNT_Z = 3.8     # BodyBackAttachment en el R15: centro del torso superior + 0,6
figs = A.reference_figure(CR, x=0.0, y=0.475, h=5.2)
for f in figs:
    f.location.z -= MOUNT_Z
mbp = A.MB('Plataforma')
mbp.cyl((0, 0, -MOUNT_Z - 0.25), (0, 0, -MOUNT_Z), 9.5, 48, 'ref', rot=0.0)
plat = mbp.finish(CR)
plat.data.materials.clear()
plat.data.materials.append(A.flat_mat('Plataforma', (0.40, 0.48, 0.57)))
rul = A.ruler(CR, 6.6, 0.0, h=6.0, w=0.25)
for o in rul:
    o.location.z -= MOUNT_Z
    o.hide_render = True          # la regla solo se muestra en la vista de escala


def sun(name, energy, direction, angle=6.0):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy = energy
    ld.angle = math.radians(angle)
    lo = bpy.data.objects.new(name, ld)
    lo.rotation_euler = Vector(direction).normalized().to_track_quat('-Z', 'Y').to_euler()
    CC.objects.link(lo)


sun('Sol', 3.0, (-0.35, 0.55, -0.75))
sun('Relleno', 1.0, (0.55, 0.35, -0.45), 20.0)
sun('Contraluz', 0.9, (0.0, -0.7, -0.3), 12.0)
A.setup_world((0.50, 0.60, 0.72), 1.15)
RES = (1100, 880) if FASE == 'geo' else (1400, 1120)
SAMPLES = 20 if FASE == 'geo' else 64
A.setup_render(RES, 'CYCLES', SAMPLES)
EXT = 'png' if FASE == 'geo' else 'jpg'          # los renders finales van en JPG (calidad 92) para no pesar en git


def formato():
    s = bpy.context.scene.render.image_settings
    s.file_format = 'JPEG' if EXT == 'jpg' else 'PNG'
    if EXT == 'jpg':
        s.quality = 92


def shot(name, az, el, dist, target=(0.0, -0.8, -0.3), lens=50.0, scale=False):
    t = Vector(target)
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam = A.camera(CC, 'cam_' + name, t + d * dist, t, lens=lens)
    for o in rul:
        o.hide_render = not scale
    formato()
    path = os.path.join(PREV, name + '.' + EXT)
    A.render(path, cam)
    return path


def lin(h):
    return tuple(float(v) ** 2.2 for v in A.hexrgb(h))


# Pose plegada encontrada con tools/buscar_pliegue_alas.py (cinematica directa + busqueda): las alas cuelgan juntas detras de la espalda,
# ancho +-1,5 studs, a menos de 2,6 detras del montaje, sin bajar del suelo del maniqui ni entrar en el torso.
FOLD = dict(wing=(0.0, 61.5, -19.3), mid=(27.7, 58.6, 1.8), tip=(16.5, 15.0, 2.3))

if FASE == 'geo':
    for s in ob.material_slots:
        s.material = A.flat_mat('F_' + s.material.name[2:], lin(PAL[s.material.name[2:]]), 0.85)
    pose()
    shot('_geo_espalda', 0, 6, 19.0, scale=True)
    shot('_geo_34', 38, 14, 18.0)
    shot('_geo_detalle', 22, 10, 8.5, target=(2.3, -1.0, 1.1), lens=50)
    if os.environ.get('ALAS_LADO'):
        shot('_geo_lado', 78, 10, 18.0)
    if os.environ.get('ALAS_POSES'):
        pose(**FOLD)
        shot('_geo_pliegue_a', 38, 14, 18.0)
        shot('_geo_pliegue_b', 90, 8, 18.0)
        pose()
    A.log('fase geo lista')
    sys.exit(0)

# ------------------------------------------------------------------ textura pintada (se hornea con Cycles y se compone en numpy)
A.uv_unwrap([ob], angle=52.0, margin=0.004)
R = 8.0
maps = A.bake_maps([ob], 2048, R, 0.6, 0.05, samples=16)
Pn = A.Paint(maps, R)
A.setup_render(RES, 'CYCLES', SAMPLES)


def detalle_pluma(filas, es_punta, linea_col):
    """Pinta en cada pluma de esas filas el eje central (nervio), las dos mitades con distinto brillo y las barbas oblicuas."""
    sel = [b for b in BLADES if b['row'] in filas]
    lc = A.hexrgb(linea_col)

    def extra(P, msk, pos, nrm, col):
        x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
        out = col.copy()
        vis = nrm[:, 1] < -0.6                                   # cara que mira a quien ve el ala desde atras
        for b in sel:
            th = b['th']
            n0, n1, d0, d1 = math.cos(th), math.sin(th), math.sin(th), -math.cos(th)
            rx, rz = b['side'] * x / SCL - 0.0 - b['ax'], z / SCL - b['az']
            u = rx * n0 + rz * n1
            v = rx * d0 + rz * d1
            ycap = (b['y0'] - 0.012) if es_punta else b['y0']
            m = vis & (np.abs(y / SCL - ycap) < 0.004) & (v > 0) & (v < b['L'] * 1.02) & (np.abs(u) < b['h'])
            if not m.any():
                continue
            f = v / b['L']
            # mitades: la derecha de la pluma un poco mas clara que la izquierda
            k = 1.0 + 0.07 * np.sign(u)
            out[m] = out[m] * k[m][:, None]
            # barbas: bandas suaves que parten del nervio hacia fuera y hacia la punta
            s = v * 7.0 - np.abs(u) * 9.0
            bar = 1.0 + 0.045 * (np.sin(s * 2 * math.pi) * 0.5)
            out[m] = out[m] * bar[m][:, None]
            # nervio central
            ln = m & (np.abs(u) < 0.032) & (f > 0.05) & (f < 0.90 if not es_punta else f < 0.96)
            a = np.clip(1.0 - np.abs(u) / 0.032, 0, 1) * 0.55
            out[ln] = out[ln] * (1 - a[ln][:, None]) + lc[None, :] * a[ln][:, None]
        return out
    return extra


def reg(name, **kw):
    return Pn.region(name, PAL[name], **kw)


PLUMA = dict(var=0.045, stroke=(1.0, 1.0, 5.0), stroke_scale=3.2, face_var=0.015, ao=0.60, ao_tint='#0a0f20', light=0.20,
             hue_var=0.02, blotch=0.035, edge=0.8, edge_th=0.035, edge_break=0.15, grad=0.35, grad_axis=2)
PUNTA = dict(var=0.04, stroke=(1.0, 1.0, 5.0), stroke_scale=3.2, face_var=0.015, ao=0.50, ao_tint='#04201f', light=0.18,
             hue_var=0.015, blotch=0.03, edge=0.9, edge_th=0.035, edge_break=0.15)
reg('pluma_c', edge_col='#5b6faa', extra=detalle_pluma(('c',), False, '#6f83be'), seed=11, **PLUMA)
reg('pluma_s', edge_col='#52659f', extra=detalle_pluma(('s',), False, '#667ab5'), seed=12, **PLUMA)
reg('pluma_p', edge_col='#4a5c95', extra=detalle_pluma(('p',), False, '#5d70ab'), seed=13, **PLUMA)
reg('pluma_u', edge_col='#3b4a7a', extra=detalle_pluma(('u',), False, '#4c5d8f'), seed=14, **PLUMA)
reg('punta_d', edge_col='#36988e', extra=detalle_pluma(('c', 'u'), True, '#4fb5aa'), seed=21, **PUNTA)
reg('punta_m', edge_col='#4aaea3', extra=detalle_pluma(('s',), True, '#66c6ba'), seed=22, **PUNTA)
reg('punta', edge_col='#7fd0c4', extra=detalle_pluma(('p',), True, '#97e0d6'), seed=23, **PUNTA)
reg('borde', var=0.02, ao=0.3, light=0.1, face_var=0.0, blotch=0.0, seed=3)
reg('punta_borde', var=0.02, ao=0.3, light=0.1, face_var=0.0, blotch=0.0, seed=4)
reg('hueso', var=0.06, stroke=(1.0, 1.0, 3.0), stroke_scale=4.0, edge_col='#9aa7d2', edge=0.9, edge_th=0.04, ao=0.6, light=0.28,
    grime=0.15, grime_col='#1c2036', blotch=0.05, seed=31)
reg('espina', var=0.05, stroke=(1.0, 1.0, 3.0), stroke_scale=4.0, edge_col='#7384b8', edge=0.8, edge_th=0.04, ao=0.55, light=0.26, seed=32)
reg('espina_punta', var=0.03, edge_col='#8fe0d4', edge=0.8, edge_th=0.04, ao=0.3, light=0.2, seed=33)
reg('placa', var=0.05, edge_col='#6070a8', edge=0.8, edge_th=0.04, ao=0.6, light=0.26, grime=0.1, grime_col='#12162a', seed=34)
reg('gema', var=0.02, edge_col='#bff5ec', edge=0.9, edge_th=0.05, ao=0.15, light=0.12, grad=0.5, seed=35)
reg('aro', var=0.04, edge_col='#5fc4b6', edge=0.8, edge_th=0.04, ao=0.5, light=0.22, seed=36)
reg('remache', var=0.04, edge_col='#a8b6e0', edge=0.8, edge_th=0.04, ao=0.5, light=0.22, seed=37)
# sangrado de las islas UV: el filtrado y los mipmaps de Roblox no deben mezclar los bordes de las caras con el fondo negro
_occ = Pn.ids > 0
for _ in range(10):
    _acc = np.zeros_like(Pn.img)
    _cnt = np.zeros(_occ.shape, np.float32)
    for _dy, _dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        _acc += np.roll(Pn.img, (_dy, _dx), axis=(0, 1)) * np.roll(_occ, (_dy, _dx), axis=(0, 1))[..., None]
        _cnt += np.roll(_occ, (_dy, _dx), axis=(0, 1))
    _nuevo = (~_occ) & (_cnt > 0)
    Pn.img[_nuevo] = _acc[_nuevo] / _cnt[_nuevo][:, None]
    _occ = _occ | _nuevo
TEX = os.path.join(OUT, 'texturas', 'AlasAvanzadas_paleta_1024.png')
Pn.save(TEX, out_size=1024)
A.assign_final([ob], A.final_material('AlasAvanzadas', TEX))
A.log('textura pintada', TEX)

# ------------------------------------------------------------------ clips (30 fps; angulos con el convenio de pose())
ALL = ['Root'] + ['%s_%s' % (n, s) for s in 'RL' for n in ('Wing', 'Mid', 'Tip')]


def keys(c, t, wing, mid, tip, bob=0.0, interp='BEZIER'):
    for s, suf in ((1, 'R'), (-1, 'L')):
        for nm, (roll, yaw, pit) in (('Wing', wing), ('Mid', mid), ('Tip', tip)):
            c.k('%s_%s' % (nm, suf), t, rot=(pit, s * roll, -s * yaw), interp=interp)
    c.k('Root', t, loc=(0, 0, bob), interp=interp)


def glide(t):
    p = 2 * math.pi * t / 2.4
    return ((-2 + 2.5 * math.sin(p), 8 + 1.5 * math.sin(p + 0.8), 0), (1.0 * math.sin(p - 0.35), 0, 0),
            (-1 + 4 * math.sin(p - 0.7), 3, 0), 0.06 * math.sin(p - 0.4))


# Aleteo (Maikol, 29/10): recoger -> extender -> impulsar -> recoger. Arriba extendidas; el empuje baja las alas enteras con la punta retrasada (mas arriba);
# abajo empiezan a recogerse: codo y punta flexionan hacia atras mientras suben; arriba se extienden otra vez.
# Claves por fase del ciclo: (fase, (aleteo, barrido) hombro, (aleteo, barrido) codo, (aleteo, barrido) punta); aleteo + baja la punta, barrido + la lleva atras.
FLAP_CLAVES = [
    (0.00, -30, 6, -6, 0, -4, 2),        # arriba, extendida
    (0.10, -26, 6, -8, 0, -12, 2),
    (0.28, -4, 5, -10, 0, -22, 2),       # empuje: la punta se queda atras (mas arriba que el hombro)
    (0.46, 14, 8, 0, 6, -8, 6),          # abajo
    (0.60, 0, 28, 14, 48, 14, 26),       # recoge: codo y punta flexionan hacia atras
    (0.78, -22, 34, 20, 56, 16, 30),     # recogida, subiendo
    (0.90, -30, 12, -4, 12, 0, 6),       # extiende
]


def _suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def _ciclo(knots, fase):
    f = fase % 1.0
    ks = knots + [(knots[0][0] + 1.0,) + tuple(knots[0][1:])]
    for i in range(len(ks) - 1):
        a, b = ks[i], ks[i + 1]
        fa = f if f >= a[0] else f + 1.0
        if a[0] <= fa <= b[0] + 1e-9:
            u = _suave((fa - a[0]) / (b[0] - a[0]))
            return [a[j] + (b[j] - a[j]) * u for j in range(1, len(a))]
    return list(knots[0][1:])


def flap(t):
    p = (t / 0.9) % 1.0
    v = _ciclo(FLAP_CLAVES, p)
    return ((v[0], v[1], 0), (v[2], v[3], 0), (v[4], v[5], 0), 0.18 * math.sin(2 * math.pi * (p - 0.15)))


acts = {}
c = A.Clip(rig, 'Glide', 2.4, loop=True, fps=30)
for i in range(9):
    keys(c, i * 0.3, *glide(i * 0.3))
acts['Glide'] = c.build(ALL)
c = A.Clip(rig, 'Flap', 0.9, loop=True, fps=30)
for i in range(19):                      # de 0 a 0,9 s cada 0,05 s: la ultima clave repite la primera y el bucle cierra
    keys(c, i * 0.05, *flap(min(i * 0.05, 0.9 - 1e-9) if i == 18 else i * 0.05))
acts['Flap'] = c.build(ALL)
c = A.Clip(rig, 'Deploy', 1.2, loop=False, fps=30)
g0 = glide(0)
keys(c, 0.00, FOLD['wing'], FOLD['mid'], FOLD['tip'], 0.0)
keys(c, 0.15, (2.0, 64.0, -21.0), (30.0, 60.0, 2.0), (19.0, 17.0, 2.5), -0.10, interp='EXPO_OUT')   # anticipacion: se cierra un poco mas
keys(c, 0.42, (-18, -10, 0), (-12, 0, 0), (-22, 4, 0), 0.25)
keys(c, 0.70, (4, 12, 0), (3, 0, 0), (8, 6, 0), 0.05)
keys(c, 1.20, g0[0], g0[1], g0[2], g0[3])
acts['Deploy'] = c.build(ALL)
CLIPS = {'Deploy': 1.2, 'Flap': 0.9, 'Glide': 2.4}


def en(nombre, t):
    A.set_action(rig, acts[nombre])
    bpy.context.scene.frame_set(int(round(t * 30)))
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ renders de comprobacion
def a_jpg(png, jpg, escala=0.5):
    im = bpy.data.images.load(png, check_existing=False)
    im.scale(int(im.size[0] * escala), int(im.size[1] * escala))
    im.filepath_raw = jpg
    im.file_format = 'JPEG'
    im.save()
    bpy.data.images.remove(im)
    os.remove(png)


if RENDER:
    shots = []
    rig.animation_data_clear()      # sin accion activa: la pose manual manda
    pose()
    shots.append((shot('Alas-avanzadas-v02-espalda', 0, 6, 19.0, scale=True), 'ESPALDA (REGLA 6 STUDS)'))
    shots.append((shot('Alas-avanzadas-v02-tres-cuartos', 38, 14, 18.0), '3/4'))
    shots.append((shot('Alas-avanzadas-v02-lateral', 78, 10, 18.0), 'LATERAL'))
    shots.append((shot('Alas-avanzadas-v02-frontal', 180, 6, 19.0), 'DE FRENTE'))
    shots.append((shot('Alas-avanzadas-v02-detalle', 22, 10, 8.5, target=(2.3, -1.0, 1.1)), 'DETALLE BRAZO'))
    en('Deploy', 0.0)
    shots.append((shot('Alas-avanzadas-v02-plegadas', 38, 14, 18.0), 'PLEGADAS (DEPLOY T=0)'))
    en('Flap', 0.0)
    shots.append((shot('Alas-avanzadas-v02-aleteo-alto', 25, 8, 19.0), 'ALETEO ARRIBA'))
    en('Flap', 0.45)
    shots.append((shot('Alas-avanzadas-v02-aleteo-bajo', 25, 8, 19.0), 'ALETEO ABAJO'))
    en('Glide', 0.6)
    shots.append((shot('Alas-avanzadas-v02-planeo', 20, 8, 19.0), 'PLANEO'))
    A.setup_render((560, 450), 'CYCLES', 24)
    seq = []
    for t in (0.0, 0.15, 0.30, 0.42, 0.60, 1.2):
        en('Deploy', t)
        seq.append((shot('_deploy_%03d' % int(round(t * 100)), 38, 14, 20.0), 'T=%.2f' % t))
    W.contact_sheet(seq, 3, os.path.join(PREV, '_deploy.png'), title='DEPLOY 1,2 S: PLEGADAS A ABIERTAS')
    a_jpg(os.path.join(PREV, '_deploy.png'), os.path.join(PREV, 'Alas-avanzadas-v02-deploy-secuencia.jpg'), 1.0)
    for p, _ in seq:
        os.remove(p)
    seq = []                                  # aleteo: recoger -> extender -> impulsar -> recoger (seis poses del ciclo de 0,9 s)
    for fase, etq in ((0.00, 'ARRIBA EXTENDIDA'), (0.28, 'IMPULSO'), (0.46, 'ABAJO'), (0.60, 'RECOGE'), (0.78, 'RECOGIDA'), (0.90, 'EXTIENDE')):
        en('Flap', fase * 0.9)
        seq.append((shot('_flap_%03d' % int(round(fase * 100)), 25, 8, 20.0), etq))
    W.contact_sheet(seq, 3, os.path.join(PREV, '_flap.png'), title='FLAP 0,9 S: RECOGER - EXTENDER - IMPULSAR - RECOGER')
    a_jpg(os.path.join(PREV, '_flap.png'), os.path.join(PREV, 'Alas-avanzadas-v02-flap-secuencia.jpg'), 1.0)
    for p, _ in seq:
        os.remove(p)
    W.contact_sheet(shots, 3, os.path.join(PREV, '_hoja.png'), title='ALAS AVANZADAS V02 - RENDERS DE BLENDER')
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, 'Alas-avanzadas-v02-hoja.jpg'), 0.5)


# ------------------------------------------------------------------ exportacion (FBX Roblox: global_scale 0.01, 1 unidad = 1 stud)


def fbx(path, objs, anim):
    A.select_only(objs)
    kw = dict(filepath=path, use_selection=True, object_types={'MESH', 'ARMATURE', 'EMPTY'}, global_scale=0.01,
              apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True, bake_space_transform=False, axis_forward=FBX_FORWARD,
              axis_up='Y', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', use_mesh_modifiers=False,
              add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL', bake_anim=anim)
    if anim:
        kw.update(bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False,
                  bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0)
    bpy.ops.export_scene.fbx(**kw)


rig.animation_data_clear()
pose()
fbx(os.path.join(OUT, 'AlasAvanzadas_v02_Rig.fbx'), [ob, rig], False)
for nombre in CLIPS:
    A.set_action(rig, acts[nombre])
    fbx(os.path.join(OUT, 'clips', 'AlasAvanzadas_v02_%s.fbx' % nombre), [ob, rig], True)
rig.animation_data_clear()
ad = rig.animation_data_create()
for nombre, act in acts.items():
    tr = ad.nla_tracks.new()
    tr.name = nombre
    tr.strips.new(nombre, 1, act)
A.select_only([ob, rig])
NLA_PISTAS = list(ad.nla_tracks)
try:
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'AlasAvanzadas_v02.glb'), export_format='GLB', use_selection=True,
                              export_yup=True, export_animations=True, export_animation_mode='NLA_TRACKS')
except TypeError:
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'AlasAvanzadas_v02.glb'), export_format='GLB', use_selection=True,
                              export_yup=True, export_animations=True)
for tr in NLA_PISTAS:                       # el .blend queda con la pose neutra: las pistas guardan los clips pero silenciadas
    tr.mute = True
pose()
A.save_blend(os.path.join(OUT, 'AlasAvanzadas_v02.blend'))
A.write_json(os.path.join(OUT, 'datos.json'), {
    'pieza': 'Alas avanzadas v0.2 (oscuras con turquesa y pinchos)', 'triangulos': TRIS, 'limites_studs': BOUNDS,
    'huesos': [b[0] for b in bones], 'clips_30fps': {k: {'duracion_s': v, 'frames': int(round(v * 30)), 'bucle': k != 'Deploy'} for k, v in CLIPS.items()},
    'textura': 'texturas/AlasAvanzadas_paleta_1024.png (1024, un material, una malla)', 'escala_final': SCL,
    'ejes': 'Blender +Y delante, +Z arriba, +X derecha; origen = BodyBackAttachment; FBX axis_forward=%s axis_up=Y global_scale=0.01' % FBX_FORWARD,
    'paleta': PAL, 'sin_probar_en_roblox': True})
A.log('listo')
