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
VARIANTE = 'lamentadora'
VAR = {
    'mujer': dict(nombre='ZombiMujer', out='zombi-mujer', plantilla='Zombi_Mujer', escala=1.0, brazo=1.0, piel=(0.66, 0.68, 0.58),
                  vestido='#7d8ea2', pelo='#2e231d', floral=True, boca=1.0, huecos=False),
    # La Lamentadora: larga y deformada, de luto, con la boca abierta en un lamento y los ojos hundidos y oscuros
    'lamentadora': dict(nombre='LaLamentadora', out='', plantilla='Jefe_lamentadora',
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
bpy.context.scene.render.threads_mode='FIXED'
bpy.context.scene.render.threads=3
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

# Cabeza y pelo originales de esta revision, sin modificar la base de Claude.
from boss_head import build_head
parts['Head']=build_head(A,CM)

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
    # Palma y cinco dedos separados. No hay una tablilla haciendo de cuatro dedos.
    kn=wr+Vector((sx*.018,.055,-.27))
    limb(mb,[wr+Vector((0,0,.05)),wr+Vector((0,.02,-.14)),kn],
         [(.095,.075),(.143,.08),(.15,.058)],'piel',n=8)
    for digit in range(4):
        bx=kn.x+(digit-1.5)*.077
        ln=[.38,.47,.44,.33][digit]*(1.12 if side=='Right' else 1.0)
        base=Vector((bx,kn.y,kn.z+.025))
        mid=base+Vector(((digit-1.5)*.015,.065,-ln*.55))
        tip=base+Vector(((digit-1.5)*.024,.17,-ln))
        limb(mb,[base,mid,tip],[(.043,.037),(.035,.031),(.018,.018)],'piel',n=5)
        limb(mb,[tip+Vector((0,0,.04)),tip+Vector((0,.05,-.055))],[(.02,.016),(.003,.003)],'diente',n=4)
    th=wr+Vector((-sx*.11,.03,-.14))
    limb(mb,[th,th+Vector((-sx*.12,.07,-.13)),th+Vector((-sx*.13,.16,-.28))],
         [(.05,.045),(.038,.032),(.017,.017)],'piel',n=5)
    parts[side+'Hand']=mb.finish(CM,recalc=True)

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

# Hito de revision: modelo real Blender con materiales provisionales, no render final.
CS=A.collection('QA_FORMAS')
saved_materials={o.name:list(o.data.materials) for o in objs}
palette={'piel':(.42,.45,.43),'cara':(.48,.49,.46),'pelo':(.035,.031,.038),
         'vestido':(.075,.065,.076),'boca':(.018,.012,.017),'ojo':(.62,.64,.58),
         'diente':(.43,.42,.34),'labio':(.29,.25,.27),'zapato':(.06,.055,.05)}
for o in objs:
    for slot in o.material_slots:
        key=slot.material.name[2:]
        slot.material=A.flat_mat('Preview_'+key,palette.get(key,(.25,.25,.25)))
A.setup_world((.18,.21,.24),.5)
A.add_lights(CS)
A.setup_render((1000,1000),'CYCLES',20)
bpy.context.scene.render.threads_mode='FIXED'; bpy.context.scene.render.threads=3
cc=A.camera(CS,'FormaCara',(.95,3.5,5.4),(0,.05,5.08),lens=62)
A.render(os.path.join(OUT,'previews','Lamentadora-v03b-01-rostro-forma-Blender.png'),cc)
for o in objs:
    # Sustituir slots IN SITU: clear() reinicia indices de las caras a cero.
    for slot,m in zip(o.material_slots,saved_materials[o.name]):slot.material=m
for o in list(CS.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(CS)

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
    # Piel estratificada. Los ojos y la boca se forman en geometria, no como pegatinas.
    col=skin_x(P,msk,pos,nrm,col)
    u,v=pos[:,0],pos[:,2]; front=np.clip(nrm[:,1],0,1)
    for sx in (-1,1):
        hollow=np.exp(-ell(u,v,sx*.112,5.205,.105,.075)*1.4)*front
        col=col*(1-.35*hollow[:,None])+np.array([.27,.25,.31])*(.35*hollow[:,None])
        cheek=np.exp(-ell(u,v,sx*.2,5.075,.07,.085)*1.5)*front
        col*=1-.14*cheek[:,None]
        # Surco lagrimal irregular, ancho variable, muy poco saturado.
        line=sx*(.11+.008*np.sin(v*52))
        tear=np.exp(-((u-line)/.009)**2)*smooth(5.10,5.20,v)*smooth(5.24,5.18,v)*front
        col=col*(1-.30*tear[:,None])+np.array([.20,.19,.22])*(.30*tear[:,None])
    noise=A.fbm(pos*32,2,801)
    col*=.96+.07*noise[:,None]
    return col


def hair_x(P, msk, pos, nrm, col):
    # mechones finos verticales con brillos tenues (sin manchas anaranjadas)
    s = A.vnoise(np.stack([pos[:, 0] * 55.0, pos[:, 1] * 55.0, pos[:, 2] * 2.5], 1), 33)
    col = col * (0.72 + 0.40 * s)[:, None]
    hl = A.vnoise(np.stack([pos[:, 0] * 35.0, pos[:, 1] * 35.0, pos[:, 2] * 1.5], 1), 35) > 0.80
    col[hl] = col[hl] * 0.75 + np.array([0.18, 0.19, 0.21], np.float32) * 0.25
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
    col[hole] = col[hole]*0.65 # desgaste oscuro, sin parches planos de piel
    # tirantes y escote
    return col


P_STYLE = {
    'piel': dict(base=SKIN, var=0.05, stroke=(1, 1, 1), stroke_scale=6, blotch=0.06, ao=0.62, ao_tint='#2a2230', light=0.22, face_var=0.0,
                 edge_col='#c4c7b5', edge=0.25, grime=0.18, grime_col='#4a4237', hue_var=0.02, seed=2, extra=skin_x),
    'cara': dict(base=SKIN, var=0.04, stroke=(1, 1, 1), stroke_scale=8, blotch=0.05, ao=0.55, ao_tint='#2a2230', light=0.22, face_var=0.0,
                 edge_col='#c4c7b5', edge=0.15, grime=0.10, grime_col='#4a4237', hue_var=0.02, seed=3, extra=face_x),
    'pelo': dict(base=VAR['pelo'], var=0.10, stroke=(1, 1, 8), stroke_scale=10, blotch=0.10, ao=0.60, ao_tint='#0a0707', light=0.30,
                 edge_col='#38383d', edge=0.25, grime=0.20, dust=0.12, dust_col='#6a5a4c', face_var=0.0, seed=9, extra=hair_x),
    'vestido': dict(base=VAR['vestido'], var=0.08, stroke=(1, 1, 5), stroke_scale=7, blotch=0.12, ao=0.62, ao_tint='#141820', light=0.26,
                    edge_col='#b9c3cd', edge=0.6, edge_th=0.04, grime=0.40, grime_col='#3a3128', dust=0.12, face_var=0.0, seed=5, extra=dress_x),
    'zapato': dict(base='#252322', var=0.08, stroke=(1, 1, 1), stroke_scale=8, ao=0.55, edge_col='#5a5550', edge=0.6, grime=0.35,
                   grime_col='#3d342a', dust=0.2, face_var=0.0, seed=13),
}
P_STYLE.update({
 'boca':dict(base='#151018',var=.025,ao=.25,light=.08),
 'ojo':dict(base='#abae9f',var=.025,ao=.35,light=.12),
 'diente':dict(base='#8b8977',var=.04,ao=.40,light=.12),
 'labio':dict(base='#4a4045',var=.03,ao=.35,light=.12),
})

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
    maps = A.bake_maps(gobjs, 1024, R=R, ao_dist=0.18, bevel_r=0.015, samples=12, pos_ref=ref)
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
def deform(p):
    x,y,z=p
    k=max(0,min(1,(z-3.5)/1.3)); k=k*k*(3-2*k)
    # Centro del pecho se adelanta progresivamente; cuello largo y cabeza descentrada.
    y+=.19*k
    x-=.045*k
    if z>4.65:z+=.13*min(1,(z-4.65)/.23)
    return Vector((x,y,z))
for ob in parts.values():
    for v in ob.data.vertices:v.co=deform(v.co)

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
J = {k: tuple(v * ESC for v in deform(p)) for k, p in J.items()}
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
    c.k('UpperTorso', t, (-16 + 1.5 * cyc(ph), 0, 5 * cyc(ph, 0.25)))
    c.k('Head', t, (-7 + 2.0 * cyc(ph, 0.1), 18 + 3 * cyc(ph, 0.3), 4 * cyc(ph, 0.5)))
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

from clip_contacts import correct_fall_contact, reset_pose
contact_report=correct_fall_contact(rig,objs,acts['Caer'],bpy.context.scene.render.fps)
A.write_json(os.path.join(OUT,'qa','CONTACTO-CAIDA.json'),contact_report)
reset_pose(rig)

# ------------------------------------------------------------------ RENDERS de comprobacion
CC = A.collection('Camaras')
CR = A.collection('Ref')
A.setup_world((0.50, 0.54, 0.58), 0.85)
A.add_lights(CC)
PV = os.path.join(OUT, 'previews')
A.setup_render((1280, 960), 'CYCLES', 32)
bpy.context.scene.render.threads_mode='FIXED'; bpy.context.scene.render.threads=3
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
    if n not in ('1_frente_con_ref','2_tres_cuartos','4_cara_tres_cuartos','5_cara_frente_muy_cerca'): continue
    A.render(os.path.join(PV, NOMBRE + '_v03b_' + n + '.png'), cam)
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
reset_pose(rig)
bpy.ops.file.pack_all()
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
reset_pose(rig)
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
