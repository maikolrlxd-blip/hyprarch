# Piezas comunes de las armas: brazos de viewmodel estilo R15, IK de dos huesos, clips (mundo y viewmodel),
# hojas de contacto con rotulos, renders de comprobacion y exportaciones.
import os, math
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion
import ap_lib as A

# ------------------------------------------------------------------ fuente 5x7 para rotular hojas de contacto
_G = {
 'A': [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"], 'B': ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
 'C': [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "], 'D': ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
 'E': ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"], 'F': ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
 'G': [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"], 'H': ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
 'I': [" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "], 'J': ["  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
 'K': ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"], 'L': ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
 'M': ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"], 'N': ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
 'O': [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "], 'P': ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
 'Q': [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"], 'R': ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
 'S': [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "], 'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
 'U': ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "], 'V': ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
 'W': ["#   #", "#   #", "#   #", "# # #", "# # #", "# # #", " # # "], 'X': ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
 'Y': ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "], 'Z': ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
 '0': [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "], '1': ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
 '2': [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"], '3': ["#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "],
 '4': ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "], '5': ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
 '6': ["  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "], '7': ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
 '8': [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "], '9': [" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "],
 '.': ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "], ':': ["     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "],
 '_': ["     ", "     ", "     ", "     ", "     ", "     ", "#####"], '-': ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
 '/': ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "], ' ': ["     "] * 7,
 '(': ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "], ')': [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
 '=': ["     ", "     ", "#####", "     ", "#####", "     ", "     "], '+': ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
}
_ACC = str.maketrans('ÁÉÍÓÚÑÜáéíóúñü', 'AEIOUNUaeiounu')


def draw_text(img, x, y, text, scale=2, col=(1, 1, 1), bg=(0, 0, 0)):
    text = text.translate(_ACC).upper()
    w = len(text) * 6 * scale + 2 * scale
    h = 9 * scale
    H, W = img.shape[:2]
    y0, y1, x0, x1 = y, min(H, y + h), x, min(W, x + w)
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * 0.25 + np.array(bg) * 0.75
    for i, ch in enumerate(text):
        g = _G.get(ch, _G[' '])
        for r, row in enumerate(g):
            for c, px in enumerate(row):
                if px == '#':
                    yy = y + scale + r * scale
                    xx = x + scale + (i * 6 + c) * scale
                    img[yy:yy + scale, xx:xx + scale] = col


def load_png(path):
    im = bpy.data.images.load(path, check_existing=False)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1, :, :3].copy()


def save_png(arr, path):
    h, w = arr.shape[:2]
    rgba = np.ones((h, w, 4), np.float32)
    rgba[:, :, :3] = np.clip(arr[::-1], 0, 1)
    im = bpy.data.images.new(os.path.basename(path), w, h, alpha=False)
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = path
    im.file_format = 'PNG'
    im.save()
    bpy.data.images.remove(im)


def contact_sheet(items, cols, path, title=None, pad=6, bg=(0.11, 0.115, 0.13)):
    """items: [(ruta_png, rotulo)]"""
    imgs = [(load_png(p), lab) for p, lab in items]
    h, w = imgs[0][0].shape[:2]
    rows = (len(imgs) + cols - 1) // cols
    top = 30 if title else 0
    sheet = np.zeros((top + rows * (h + pad) + pad, cols * (w + pad) + pad, 3), np.float32)
    sheet[:] = bg
    for i, (im, lab) in enumerate(imgs):
        r, c = divmod(i, cols)
        y, x = top + pad + r * (h + pad), pad + c * (w + pad)
        sheet[y:y + h, x:x + w] = im
        if lab:
            draw_text(sheet, x + 4, y + 4, lab, 2)
    if title:
        draw_text(sheet, pad, 6, title, 2, col=(1, 0.85, 0.4), bg=bg)
    save_png(sheet, path)
    return path


# ------------------------------------------------------------------ camara de primera persona
def vm_camera(coll, fov_v=70.0, name='Cam_VM'):
    cam = A.camera(coll, name, (0, 0, 0), (0, 1, 0))
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.angle_y = math.radians(fov_v)
    cam.data.clip_start = 0.02
    return cam


# ------------------------------------------------------------------ brazos de viewmodel (bloques estilo R15)
ARM = dict(w=0.40, cuff=0.45, sleeve_col='#4b5136', cuff_col='#3a3f2b', glove_col='#6b5a44')


def build_vm_arms(coll, G, J):
    """G: posicion del origen del arma respecto a la camara. J['R'|'L'] = dict(S,E,W,H,Hs,Hr): hombro, codo, muneca,
    centro de la mano, tamano de la mano y giro de la mano (grados) en espacio del arma. Devuelve {nombre_R15: objeto}."""
    G = Vector(G)
    objs = {}
    for side, pre in (('R', 'Right'), ('L', 'Left')):
        j = J[side]
        S, E, W, Hc = (Vector(j[k]) + G for k in ('S', 'E', 'W', 'H'))
        mb = A.MB(pre + 'UpperArm')
        mb.seg_box(S, E, ARM['w'] * 1.04, ARM['w'] * 1.04, 'manga', bevel=0.03, extend=0.05)
        objs[pre + 'UpperArm'] = mb.finish(coll, origin=S)
        mb = A.MB(pre + 'LowerArm')
        d = (W - E).normalized()
        mb.seg_box(E, W - d * 0.10, ARM['w'], ARM['w'], 'manga', bevel=0.03, extend=0.04)
        mb.seg_box(W - d * 0.16, W, ARM['cuff'], ARM['cuff'], 'puno', bevel=0.025)
        objs[pre + 'LowerArm'] = mb.finish(coll, origin=E)
        mb = A.MB(pre + 'Hand')
        mk = mb.mark()
        mb.box((0, 0, 0), j['Hs'], 'guante', bevel=0.035)
        R = Euler([math.radians(a) for a in j.get('Hr', (0, 0, 0))], 'XYZ').to_matrix().to_4x4()
        mb.xform_since(mk, Matrix.Translation(Hc) @ R)
        objs[pre + 'Hand'] = mb.finish(coll, origin=W)
    return objs


def paint_arms(objs, out_png, size=1024, out_size=512):
    ob = list(objs.values())
    A.uv_unwrap(ob, angle=50, margin=0.01)
    maps = A.bake_maps(ob, size, R=4.0, ao_dist=0.25, bevel_r=0.03, samples=12)
    P = A.Paint(maps, R=4.0)
    P.region('manga', ARM['sleeve_col'], var=0.10, stroke=(1, 1, 3), stroke_scale=5, blotch=0.08, ao=0.6,
             edge_col='#7a8160', edge=0.6, grime=0.25, dust=0.25, face_var=0.05)
    P.region('puno', ARM['cuff_col'], var=0.08, stroke=(3, 1, 1), stroke_scale=9, ao=0.6, edge_col='#646b4c', edge=0.5)
    P.region('guante', ARM['glove_col'], var=0.10, stroke=(1, 1, 1), stroke_scale=8, ao=0.55, edge_col='#a08a6a',
             edge=0.7, grime=0.3, face_var=0.05)
    P.save(out_png, out_size)
    mat = A.final_material('M_BrazosVM', out_png)
    A.assign_final(ob, mat)
    return mat


# ------------------------------------------------------------------ IK de dos huesos (en espacio del arma)
def ik_two_bone(S, E, W, Wt, pole):
    S, E, W, Wt, pole = (Vector(v) for v in (S, E, W, Wt, pole))
    L1, L2 = (E - S).length, (W - E).length
    d = Wt - S
    dist = min(max(d.length, abs(L1 - L2) + 1e-3), L1 + L2 - 1e-3)
    dv = d.normalized()
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(L1 * L1 - a * a, 0.0))
    pp = pole - dv * pole.dot(dv)
    pp = pp.normalized() if pp.length > 1e-6 else Vector((0, 0, -1))
    E2 = S + dv * a + pp * h
    W2 = S + dv * dist
    qu = (E - S).rotation_difference(E2 - S)
    Q = (W - E).rotation_difference(W2 - E2)
    ql = qu.inverted() @ Q
    return qu, ql, Q


def qdeg(q):
    e = q.to_euler('XYZ')
    return tuple(math.degrees(a) for a in e)


# ------------------------------------------------------------------ definicion de clips (partes del arma + extras de viewmodel)
class ClipDef:
    def __init__(self, name, length, loop=False):
        self.name, self.length, self.loop = name, length, loop
        self.parts = {}
        self.vm = {}

    def p(self, bone, t, loc=(0, 0, 0), rot=(0, 0, 0), ip='BEZIER'):
        self.parts.setdefault(bone, []).append((t, loc, rot, ip))
        return self

    def v(self, bone, t, loc=(0, 0, 0), rot=(0, 0, 0), ip='BEZIER'):
        self.vm.setdefault(bone, []).append((t, loc, rot, ip))
        return self

    def hand(self, side, t, Wt, J, pole, extra=(0, 0, 0), ip='BEZIER'):
        """Mueve la mano (muneca) al punto Wt (espacio del arma) con IK; extra: giro adicional de la mano (grados)."""
        pre = 'Right' if side == 'R' else 'Left'
        j = J[side]
        qu, ql, Q = ik_two_bone(j['S'], j['E'], j['W'], Wt, pole)
        qh = Euler([math.radians(a) for a in extra], 'XYZ').to_quaternion()
        self.v(pre + 'UpperArm', t, rot=qdeg(qu), ip=ip)
        self.v(pre + 'LowerArm', t, rot=qdeg(ql), ip=ip)
        self.v(pre + 'Hand', t, rot=qdeg(qh), ip=ip)
        return self

    def rest_hand(self, side, t, ip='BEZIER'):
        pre = 'Right' if side == 'R' else 'Left'
        for b in ('UpperArm', 'LowerArm', 'Hand'):
            self.v(pre + b, t, ip=ip)
        return self

    def build(self, arm_ob, bones, vm):
        c = A.Clip(arm_ob, self.name, self.length, self.loop)
        for b, ks in self.parts.items():
            if b in bones:
                for k in ks:
                    c.k(b, *k)
        if vm:
            for b, ks in self.vm.items():
                if b in bones:
                    for k in ks:
                        c.k(b, *k)
        return c.build(bones)


# ------------------------------------------------------------------ utilidades de exportacion/render
def static_copies(objs, coll_name='TMP_Estatico', rename=None):
    """Copias sin rig (cada pieza en su sitio, mismo pivote) para el FBX/GLB estatico."""
    c = A.collection(coll_name)
    out = []
    for o in objs:
        o2 = o.copy()
        o2.data = o.data
        for m in list(o2.modifiers):
            o2.modifiers.remove(m)
        o2.vertex_groups.clear()
        mw = o.matrix_world.copy()
        o2.parent = None
        o2.matrix_world = mw
        if rename and o.name in rename:
            o2.name = rename[o.name]
        c.objects.link(o2)
        out.append(o2)
    return c, out


def remove_collection(c):
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(c)


def bounds(objs):
    pts = [o.matrix_world @ Vector(v) for o in objs if o.type == 'MESH' for v in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def look_cam(coll, name, target, dirv, dist, lens=50.0, ortho=None):
    t = Vector(target)
    d = Vector(dirv).normalized()
    return A.camera(coll, name, t + d * dist, t, lens=lens, ortho=ortho)


def hide_only(visible_colls):
    """Deja visibles para el render solo las colecciones indicadas (por nombre)."""
    for c in bpy.data.collections:
        c.hide_render = c.name not in visible_colls


def backdrop(coll, z=0.0, size=60.0, col=(0.36, 0.37, 0.38)):
    m = A.flat_mat('Suelo_Ref', col)
    mb = A.MB('Suelo_Ref')
    mb.box((0, 0, z - 0.05), (size, size, 0.1), 'ref')
    o = mb.finish(coll)
    o.data.materials.clear()
    o.data.materials.append(m)
    return o
