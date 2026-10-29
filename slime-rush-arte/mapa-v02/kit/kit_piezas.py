"""Slime Rush - kit modular v0.2: constructores de cada pieza (bpy 5.0.1).

Cada funcion recibe (coleccion, variante) y devuelve un objeto con el origen
en el suelo (z=0 = donde apoya). Nombres: categoria_tipo_variante.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix
from kit_base import (Pieza, bm_blob, bm_caja, bm_cilindro, bm_tubo, mat_trs,
                      caja_biselada, obj_temporal, aplicar_mods, decimar, material)

TAU = 2 * math.pi


# ======================================================== naturaleza
def roca(col, tam, var):
    """Rocas redondeadas: peq (~2-3 studs), med (~7-9), gran (apilada ~16-20)."""
    seed = {"peq": 10, "med": 20, "gran": 30}[tam] + var
    r = random.Random(seed)
    p = Pieza(f"roca_{tam}_{'abc'[var]}", seed)
    if tam == "peq":
        bm = bm_blob(1.3, 2, 0.22, 1.1, seed, (1.15, 0.95, 0.7), base_plana=-0.35)
        p.anadir_bm(bm, "roca", mat_trs((0, 0, 0.55)))
    elif tam == "med":
        bm = bm_blob(3.6, 3, 0.2, 0.9, seed, (1.2, 1.0, 0.72), base_plana=-1.0)
        ob = obj_temporal(bm)
        decimar(ob, 0.4)
        ob.location = (0, 0, 1.6)
        p.anadir_obj_evaluado(ob, "roca")
        bm = bm_blob(1.5, 2, 0.25, 1.3, seed + 5, (1.1, 1.0, 0.75), base_plana=-0.4)
        p.anadir_bm(bm, "roca_clara", mat_trs((3.9, 1.2 * (1 if var else -1), 0.6)))
        # parche de musgo encima (masa achatada)
        bm = bm_blob(1.9, 2, 0.2, 1.0, seed + 9, (1.2, 1.0, 0.25))
        p.anadir_bm(bm, "musgo", mat_trs((-0.6, 0.3, 4.0)))
    else:
        # base ancha + 2-3 masas apiladas y ladeadas (Remesh las funde un poco)
        partes = [((0, 0, 3.0), 7.5, (1.25, 1.0, 0.62)),
                  ((1.8, 0.8, 8.2), 4.8, (1.1, 1.0, 0.8)),
                  ((-1.6, -0.8, 12.0), 2.9, (1.0, 1.15, 0.85))]
        if var == 1:
            partes = [((0, 0, 2.6), 8.5, (1.3, 0.9, 0.55)),
                      ((-3.0, 0.5, 7.0), 4.5, (1.0, 1.0, 0.8)),
                      ((4.2, -1.2, 5.6), 3.2, (1.0, 1.0, 0.9))]
        for i, (loc, rad, esc) in enumerate(partes):
            bm = bm_blob(rad, 3, 0.18, 0.9, seed + i * 3, esc, base_plana=-rad * 0.45)
            ob = obj_temporal(bm)
            decimar(ob, 0.35)
            ob.matrix_world = mat_trs(loc, (0, r.uniform(-0.12, 0.12), r.uniform(0, TAU)))
            p.anadir_obj_evaluado(ob, "roca" if i != 1 else "roca_clara")
        bm = bm_blob(3.2, 2, 0.2, 1.0, seed + 11, (1.2, 1.0, 0.22))
        top = partes[-1][0]
        p.anadir_bm(bm, "musgo", mat_trs((top[0], top[1], top[2] + partes[-1][1] * 0.7)))
    return p.objeto(col)


def arbusto(col, var):
    seed = 40 + var
    r = random.Random(seed)
    p = Pieza(f"arbusto_{'abc'[var]}", seed)
    n = [5, 4, 6][var]
    for i in range(n):
        a = TAU * i / n + r.uniform(-0.3, 0.3)
        d = r.uniform(1.2, 2.4) if i else 0
        rad = r.uniform(1.8, 2.8) if i else 3.0
        mat = ["follaje", "follaje_claro", "hierba"][(i + var) % 3]
        bm = bm_blob(rad, 2, 0.15, 1.2, seed + i, (1, 1, 0.85))
        p.anadir_bm(bm, mat, mat_trs((math.cos(a) * d, math.sin(a) * d, rad * 0.75 + (1.2 if i == 0 else 0))))
    if var == 2:  # bayas de color
        for i in range(7):
            a = r.uniform(0, TAU)
            bm = bm_blob(0.35, 1, 0.0, 1, seed + 50 + i)
            p.anadir_bm(bm, "coral", mat_trs((math.cos(a) * 2.6, math.sin(a) * 2.6, r.uniform(2.2, 4.4))))
    return p.objeto(col)


def _mechon(p, loc, alto, r, mat="hierba_clara", hojas=3, seg=4):
    for k in range(hojas):
        a = r.uniform(0, TAU)
        inc = r.uniform(0.25, 0.5)
        bm = bm_cilindro(0.32, 0.0, alto * r.uniform(0.8, 1.15), seg=seg, tapas=False)
        p.anadir_bm(bm, mat, mat_trs(loc, (inc * math.cos(a), inc * math.sin(a), a)))


def hierba_parche(col, var):
    seed = 60 + var
    r = random.Random(seed)
    p = Pieza(f"hierba_parche_{'ab'[var]}", seed)
    n = [9, 14][var]
    for i in range(n):
        a = r.uniform(0, TAU)
        d = math.sqrt(r.random()) * (2.6 if var == 0 else 4.0)
        _mechon(p, (math.cos(a) * d, math.sin(a) * d, -0.1), r.uniform(1.3, 2.3), r,
                "hierba_clara" if i % 3 else "follaje_claro")
    return p.objeto(col)


def flores(col, var):
    seed = 70 + var
    r = random.Random(seed)
    p = Pieza(f"flores_{'abc'[var]}", seed)
    color = ["crema", "dorado", "rosa"][var]
    for i in range(6):
        a = r.uniform(0, TAU)
        d = math.sqrt(r.random()) * 2.2
        x, y = math.cos(a) * d, math.sin(a) * d
        h = r.uniform(1.0, 1.9)
        p.anadir_bm(bm_cilindro(0.09, 0.07, h, seg=4, tapas=False), "follaje_claro", mat_trs((x, y, 0)))
        bm = bm_blob(0.42, 1, 0.0, 1, seed + i, (1, 1, 0.35))
        p.anadir_bm(bm, color, mat_trs((x, y, h)))
        bm = bm_blob(0.16, 1, 0.0, 1, seed + i, (1, 1, 0.6))
        p.anadir_bm(bm, "dorado" if var != 1 else "madera", mat_trs((x, y, h + 0.12)))
    _mechon(p, (0, 0, -0.1), 1.2, r, "hierba_clara", hojas=4)
    return p.objeto(col)


def tronco_caido(col, var):
    seed = 80 + var
    r = random.Random(seed)
    p = Pieza(f"tronco_caido_{'ab'[var]}", seed)
    L = [20.0, 14.0][var]
    R = [2.3, 1.8][var]
    pts, rads = [], []
    for i in range(9):
        t = i / 8
        pts.append((-L / 2 + L * t, math.sin(t * math.pi) * 1.2, R * 0.9 + math.sin(t * 3.1) * 0.2))
        rads.append(R * (1.05 - 0.15 * t) * (1 + 0.06 * math.sin(i * 2.3)))
    p.anadir_bm(bm_tubo(pts, rads, seg=12, tapas=False), "madera")
    # tapas con anillo claro (corte de madera)
    for idx, sgn in ((0, -1), (-1, 1)):
        loc = Vector(pts[idx])
        bm = bm_cilindro(rads[idx] * 0.98, rads[idx] * 0.98, 0.3, seg=12)
        p.anadir_bm(bm, "madera_clara", mat_trs(loc + Vector((sgn * -0.15, 0, 0)), (0, math.pi / 2, 0)))
    # rama rota y musgo
    p.anadir_bm(bm_tubo([(2, 0, R * 1.5), (3.5, 0.8, R * 2.6)], [0.7, 0.45], seg=8), "madera",
                mat_trs((0, 0, 0)))
    for i in range(3):
        bm = bm_blob(1.4, 2, 0.2, 1.0, seed + i, (1.3, 1.0, 0.35))
        p.anadir_bm(bm, "musgo", mat_trs((-5 + i * 4.5, 0.4, R * 1.75 + 0.1)))
    if var == 1:  # hongos pequenos al lado
        for i in range(3):
            x = -3 + i * 1.6
            p.anadir_bm(bm_cilindro(0.25, 0.2, 0.9 + i * 0.3, seg=6), "crema", mat_trs((x, R + 0.9, 0)))
            p.anadir_bm(bm_blob(0.7, 2, 0.05, 1, i, (1, 1, 0.5)), "coral", mat_trs((x, R + 0.9, 1.0 + i * 0.3)))
    return p.objeto(col)


def hongo_grande(col, var):
    seed = 90 + var
    r = random.Random(seed)
    p = Pieza(f"hongo_grande_{'ab'[var]}", seed)
    sets = [[(0, 0, 9.0, 4.2)], [(0, 0, 11.0, 4.8), (5.5, 2, 6.0, 2.8), (-3.5, 4, 4.0, 2.0)]][var]
    for (x, y, h, cap) in sets:
        lean = r.uniform(-0.6, 0.6)
        pts = [(x, y, 0), (x + lean * 0.3, y, h * 0.4), (x + lean, y, h * 0.85)]
        p.anadir_bm(bm_tubo(pts, [cap * 0.32, cap * 0.24, cap * 0.22], seg=10), "crema")
        bm = bm_blob(cap, 3, 0.06, 1.0, seed, (1, 1, 0.55), base_plana=-0.05)
        ob = obj_temporal(bm)
        decimar(ob, 0.45)
        ob.location = (x + lean, y, h * 0.8)
        p.anadir_obj_evaluado(ob, "coral")
        for k in range(6):  # lunares
            a = TAU * k / 6 + r.uniform(-.3, .3)
            el = r.uniform(0.35, 0.75)
            d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el) * 0.55)) * cap
            bm = bm_blob(cap * 0.16, 1, 0, 1, k, (1, 1, 0.4))
            n = d.normalized()
            rot = n.to_track_quat("Z", "Y").to_euler()
            p.anadir_bm(bm, "crema", mat_trs(Vector((x + lean, y, h * 0.8)) + d * 1.0, rot))
    return p.objeto(col)


def cactus(col, var):
    seed = 100 + var
    r = random.Random(seed)
    p = Pieza(f"cactus_{'ab'[var]}", seed)
    H = [11.0, 7.5][var]
    p.anadir_bm(bm_tubo([(0, 0, 0), (0, 0, H)], [1.6, 1.5], seg=10, tapas=False), "follaje")
    p.anadir_bm(bm_blob(1.5, 2, 0, 1, seed, (1, 1, 0.9)), "follaje", mat_trs((0, 0, H)))
    brazos = [(1, 4.5, 3.0), (-1, 6.5, 2.5)] if var == 0 else [(1, 3.0, 2.2)]
    for (s, z0, h) in brazos:
        pts = [(0, 0, z0), (s * 2.2, 0, z0 + 0.2), (s * 3.0, 0, z0 + 1.2), (s * 3.0, 0, z0 + h)]
        p.anadir_bm(bm_tubo(pts, [0.9, 0.9, 0.9, 0.85], seg=8, tapas=False), "follaje")
        p.anadir_bm(bm_blob(0.85, 1, 0, 1, seed, (1, 1, 0.9)), "follaje", mat_trs((s * 3.0, 0, z0 + h)))
    p.anadir_bm(bm_blob(0.6, 1, 0, 1, seed, (1, 1, 0.5)), "rosa" if var else "dorado", mat_trs((0, 0, H + 1.3)))
    p.anadir_bm(bm_blob(2.2, 2, 0.1, 1, seed, (1, 1, 0.3)), "arena_osc", mat_trs((0, 0, 0)))
    return p.objeto(col)


def palmera(col, var):
    seed = 110 + var
    r = random.Random(seed)
    p = Pieza(f"palmera_{'ab'[var]}", seed)
    H = [24.0, 19.0][var]
    curva = [4.5, -3.0][var]
    pts, rads = [], []
    for i in range(10):
        t = i / 9
        pts.append((curva * t * t, 0, H * t))
        rads.append(1.3 - 0.45 * t + 0.12 * (i % 2))  # anillos marcados
    p.anadir_bm(bm_tubo(pts, rads, seg=9, tapas=False), "madera_clara")
    top = Vector(pts[-1])
    for k in range(7):
        a = TAU * k / 7 + r.uniform(-0.15, 0.15)
        L = r.uniform(9, 11.5)
        bm = bmesh.new()
        n = 7
        prev = None
        for i in range(n + 1):
            t = i / n
            w = 1.6 * math.sin(math.pi * min(1, t * 1.1)) + 0.15
            d = L * t
            z = 1.5 * math.sin(t * math.pi * 0.9) - 4.5 * t * t
            c = Vector((math.cos(a) * d, math.sin(a) * d, z))
            lado = Vector((-math.sin(a), math.cos(a), 0)) * w
            v1 = bm.verts.new(c - lado + Vector((0, 0, -0.25 * w)))
            v2 = bm.verts.new(c + Vector((0, 0, 0.18)))
            v3 = bm.verts.new(c + lado + Vector((0, 0, -0.25 * w)))
            if prev:
                bm.faces.new((prev[0], v1, v2, prev[1]))
                bm.faces.new((prev[1], v2, v3, prev[2]))
            prev = (v1, v2, v3)
        sol = bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.18)
        p.anadir_bm(bm, "follaje_claro" if k % 2 else "follaje", mat_trs(top))
    for k in range(3):
        a = TAU * k / 3
        p.anadir_bm(bm_blob(0.7, 1, 0, 1, k), "madera", mat_trs(top + Vector((math.cos(a) * 0.9, math.sin(a) * 0.9, -0.8))))
    return p.objeto(col)


def duna(col, var):
    """Pieza de duna: monticulo asimetrico (cresta marcada a sotavento)."""
    p = Pieza(f"duna_{'ab'[var]}", 120 + var)
    Lx, Ly, H = [(40, 26, 7.0), (28, 18, 4.5)][var]
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=28, y_segments=18, size=0.5)
    for v in bm.verts:
        u, w = v.co.x * 2, v.co.y * 2  # -1..1
        x, y = u * Lx / 2, w * Ly / 2
        r = math.sqrt(u * u + w * w)
        m = max(0.0, 1 - r) ** 1.4
        cresta = 0.25 + 0.75 * (1 / (1 + math.exp(-6 * (0.25 - u))))  # cae fuerte en +x
        z = H * m * cresta * (1 + 0.08 * math.sin(y * 0.6 + u * 3))
        v.co = Vector((x, y, z - 0.3))
    p.anadir_bm(bm, "arena")
    return p.objeto(col)


def rampa_natural(col, var):
    p = Pieza(f"rampa_natural_{'ab'[var]}", 130 + var)
    if var == 0:  # rampa de tierra con hierba (16 largo, sube 6)
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=16, y_segments=8, size=0.5)
        for v in bm.verts:
            u, w = v.co.x * 2, v.co.y * 2
            x, y = u * 8, w * 5
            alto = 6.0 * (u + 1) / 2
            borde = max(0.0, 1 - abs(w) ** 6)
            v.co = Vector((x, y, alto * borde - 0.4 + 0.25 * math.sin(x * 0.7)))
        ob = obj_temporal(bm)
        so = ob.modifiers.new("s", "SOLIDIFY")
        so.thickness = 3.0
        sub = ob.modifiers.new("sub", "SUBSURF")
        sub.levels = 1
        aplicar_mods(ob)
        me = ob.data
        # cara superior hierba, laterales tierra
        bm2 = bmesh.new()
        bm2.from_mesh(me)
        p.mats = ["tierra", "hierba"]
        bm2.normal_update()
        for f in bm2.faces:
            f.material_index = 1 if f.normal.z > 0.55 else 0
        me2 = bpy.data.meshes.new("_r")
        bm2.to_mesh(me2)
        bm2.free()
        borrar_obj(ob)
        p.bm.from_mesh(me2)
        bpy.data.meshes.remove(me2)
    else:  # escalones de losas de roca redondeadas
        for i in range(4):
            bm = bm_blob(3.6 - i * 0.2, 2, 0.12, 1.0, 131 + i, (1.5, 1.1, 0.32))
            p.anadir_bm(bm, "roca" if i % 2 else "roca_clara", mat_trs((i * 3.6, 0.3 * (i % 2), 0.9 + i * 1.6)))
    return p.objeto(col)


def borrar_obj(o):
    from kit_base import borrar_obj as b
    b(o)


# ======================================================== recursos (3 tipos)
def _base_roca(p, seed, r=2.6):
    p.anadir_bm(bm_blob(r, 2, 0.2, 1.1, seed, (1.2, 1.0, 0.55), base_plana=-0.6), "roca", mat_trs((0, 0, 0.8)))


def recurso(col, tipo):
    seed = {"cristal": 200, "ambar": 210, "gema": 220}[tipo]
    r = random.Random(seed)
    p = Pieza(f"recurso_{tipo}", seed)
    _base_roca(p, seed)
    if tipo == "cristal":  # prismas hexagonales de punta (lo facetado es SOLO el cristal)
        for k in range(6):
            a = TAU * k / 6 + r.uniform(-.2, .2)
            h = r.uniform(2.2, 4.8) if k else 6.0
            rad = r.uniform(0.55, 0.85) if k else 1.0
            bm = bm_cilindro(rad, rad, h, seg=6, tapas=True)
            # punta
            top = [v for v in bm.verts if v.co.z > h - 0.01]
            c = bm.verts.new((0, 0, h + rad * 1.3))
            bm.faces.ensure_lookup_table()
            cap = [f for f in bm.faces if all(v.co.z > h - 0.01 for v in f.verts)]
            bmesh.ops.delete(bm, geom=cap, context="FACES_ONLY")
            top.sort(key=lambda v: math.atan2(v.co.y, v.co.x))
            for i in range(6):
                bm.faces.new((top[i], top[(i + 1) % 6], c))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            d = 0 if k == 0 else 1.3
            inc = 0 if k == 0 else 0.45
            p.anadir_bm(bm, "cristal", mat_trs((math.cos(a) * d, math.sin(a) * d, 0.9), (inc * -math.sin(a), inc * math.cos(a), 0)))
    elif tipo == "ambar":  # pepitas redondas medio incrustadas
        for k in range(7):
            a = TAU * k / 7
            d = 1.6 if k else 0
            rad = 1.6 if k == 0 else r.uniform(0.7, 1.1)
            p.anadir_bm(bm_blob(rad, 2, 0.12, 1.4, seed + k, (1, 1, 0.85)), "ambar",
                        mat_trs((math.cos(a) * d, math.sin(a) * d, 2.4 if k == 0 else 1.7)))
    else:  # gotas de agua solidificadas sobre piedra musgosa
        p.anadir_bm(bm_blob(2.0, 2, 0.15, 1, seed, (1.3, 1.1, 0.25)), "musgo", mat_trs((0, 0, 1.9)))
        for k in range(4):
            a = TAU * k / 4 + 0.4
            d = 1.4 if k else 0
            h = 2.8 if k == 0 else 1.7
            bm = bm_blob(1.0, 2, 0.0, 1, k, (1, 1, 1.0))
            for v in bm.verts:  # forma de gota
                if v.co.z > 0:
                    t = v.co.z
                    v.co.x *= (1 - t) ** 0.8
                    v.co.y *= (1 - t) ** 0.8
                    v.co.z = t * 2.2
            p.anadir_bm(bm, "gema", mat_trs((math.cos(a) * d, math.sin(a) * d, 1.6 + (0.6 if k == 0 else 0)), esc=h / 2.2))
    return p.objeto(col)


# ======================================================== cofres
def _cofre(p, loc=(0, 0, 0), rot=0.0, cuerpo="madera", banda="madera_osc", cierre="dorado",
           tapa_abierta=0.0, escala=1.0):
    M0 = mat_trs(loc, (0, 0, rot), escala)
    W, D, H = 4.4, 3.0, 2.4
    tmp = Pieza("_c")
    caja_biselada(tmp, cuerpo, (W, D, H), (0, 0, H / 2), bisel=0.3)
    # tapa: medio cilindro tumbado
    bm = bm_cilindro(D / 2, D / 2, W, seg=12)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x < -0.01 and False], context="VERTS")
    for v in bm.verts:
        # aplastar la mitad inferior contra z=0 del cilindro local (queda semicilindro)
        pass
    ob = obj_temporal(bm)
    ob.matrix_world = mat_trs((W / 2, 0, H), (0, -math.pi / 2, 0))
    bis = ob.modifiers.new("b", "BEVEL")
    bis.width = 0.2
    bis.segments = 2
    tmp.anadir_obj_evaluado(ob, cuerpo)
    for x in (-W * 0.3, W * 0.3):  # bandas
        caja_biselada(tmp, banda, (0.45, D + 0.2, H + 0.1), (x, 0, H / 2), bisel=0.1)
        bmb = bm_tubo([(x, -D / 2 - 0.1, H), (x, -D / 2 * 0.7, H + D / 2 * 0.72), (x, 0, H + D / 2 + 0.1),
                       (x, D / 2 * 0.7, H + D / 2 * 0.72), (x, D / 2 + 0.1, H)], 0.24, seg=6)
        tmp.anadir_bm(bmb, banda)
    caja_biselada(tmp, cierre, (0.9, 0.35, 1.1), (0, -D / 2 - 0.12, H * 0.92), bisel=0.12)
    tmp.anadir_bm(bm_blob(0.18, 1, 0, 1, 0), banda, mat_trs((0, -D / 2 - 0.32, H * 0.85)))
    me = bpy.data.meshes.new("_cm")
    tmp.bm.to_mesh(me)
    tmp.bm.free()
    for i, f in enumerate(me.polygons):
        pass
    # reasignar materiales de tmp a p
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    bm2.transform(M0)
    remap = [p._idx(m) for m in tmp.mats]
    for f in bm2.faces:
        f.material_index = remap[f.material_index]
    me2 = bpy.data.meshes.new("_cm2")
    bm2.to_mesh(me2)
    bm2.free()
    n0 = len(p.bm.faces)
    p.bm.from_mesh(me2)
    bpy.data.meshes.remove(me)
    bpy.data.meshes.remove(me2)


def cofre(col, tipo):
    seed = {"comun": 300, "musgoso": 310, "raro": 320, "enterrado": 330}[tipo]
    r = random.Random(seed)
    p = Pieza(f"cofre_{tipo}", seed)
    if tipo == "comun":
        _cofre(p)
    elif tipo == "musgoso":
        _cofre(p, cuerpo="madera_osc", banda="roca_osc", cierre="roca_clara")
        for k in range(4):
            p.anadir_bm(bm_blob(1.1, 2, 0.2, 1, seed + k, (1.3, 1.0, 0.4)), "musgo",
                        mat_trs((-1.5 + k * 1.0, r.uniform(-0.5, 0.5), 3.85 + r.uniform(-.2, .1))))
        for k in range(3):
            x = 2.6 + k * 0.5
            p.anadir_bm(bm_cilindro(0.18, 0.15, 0.6 + k * 0.25, seg=6), "crema", mat_trs((x, 1.2 - k, 0)))
            p.anadir_bm(bm_blob(0.45, 2, 0, 1, k, (1, 1, 0.5)), "coral", mat_trs((x, 1.2 - k, 0.65 + k * 0.25)))
        p.anadir_bm(bm_blob(2.6, 2, 0.15, 1, seed, (1.4, 1.1, 0.18)), "musgo", mat_trs((0, 0, 0)))
    elif tipo == "raro":
        _cofre(p, cuerpo="dorado", banda="madera_osc", cierre="cristal")
        # cristales decorativos sobre la tapa
        for k, (x, h) in enumerate(((-1.2, 1.4), (0.0, 2.0), (1.2, 1.2))):
            bm = bm_cilindro(0.35, 0.0, h, seg=6)
            p.anadir_bm(bm, "cristal", mat_trs((x, 0, 3.7), (0.25 * (k - 1), 0, 0)))
        p.anadir_bm(bm_cilindro(3.4, 3.6, 0.5, seg=16), "roca_clara", mat_trs((0, 0, -0.25)))
    else:  # enterrado: solo asoma una esquina de la tapa, montoncito de tierra
        _cofre(p, loc=(0.3, 0, -1.9), rot=0.35, escala=0.95)
        bm = bm_blob(4.2, 3, 0.12, 1.0, seed, (1.25, 1.05, 0.38), base_plana=-0.1)
        ob = obj_temporal(bm)
        decimar(ob, 0.35)
        p.anadir_obj_evaluado(ob, "tierra")
        # indicio sutil: anillo de 5 piedrecitas + destello dorado pequeno
        for k in range(5):
            a = TAU * k / 5 + 0.3
            p.anadir_bm(bm_blob(0.55, 1, 0.2, 1, k, (1.2, 1, 0.6)), "roca_clara",
                        mat_trs((math.cos(a) * 5.8, math.sin(a) * 5.8, 0.15)))
        for k in range(4):  # destello en cruz (4 puntas)
            a = TAU * k / 4
            bm = bm_cilindro(0.18, 0.0, 0.9, seg=4)
            p.anadir_bm(bm, "dorado", mat_trs((-1.6, -1.0, 1.9), (math.pi / 2, 0, a)))
        p.anadir_bm(bm_blob(0.25, 1, 0, 1, 0), "dorado", mat_trs((-1.6, -1.0, 1.9)))
    return p.objeto(col)


# ======================================================== estructuras
def puente_tramo(col, var):
    """Tramo modular de 16 studs (eje X), 7 de ancho. Se encadena en X."""
    seed = 400 + var
    r = random.Random(seed)
    p = Pieza(f"puente_tramo_{'ab'[var]}", seed)
    for i in range(10):
        x = -7.2 + i * 1.6
        caja_biselada(p, "madera_clara" if i % 3 == 0 else "madera", (1.4, 7.0 + r.uniform(-0.3, 0.3), 0.5),
                      (x, r.uniform(-0.2, 0.2), r.uniform(-0.05, 0.08)), (0, 0, r.uniform(-0.05, 0.05)), bisel=0.15)
    for y in (-2.8, 2.8):
        caja_biselada(p, "madera_osc", (16.0, 0.7, 0.7), (0, y, -0.55), bisel=0.2)
    if var == 1:  # postes + cuerda colgante
        for x in (-7.6, 7.6):
            for y in (-3.6, 3.6):
                p.anadir_bm(bm_tubo([(x, y, -1.5), (x, y, 4.2)], [0.45, 0.4], seg=8), "madera_osc")
                p.anadir_bm(bm_blob(0.5, 1, 0, 1, 0), "madera_osc", mat_trs((x, y, 4.3)))
        for y in (-3.6, 3.6):
            pts = [(-7.6 + 15.2 * t / 8, y, 3.8 - 1.0 * math.sin(math.pi * t / 8)) for t in range(9)]
            p.anadir_bm(bm_tubo(pts, 0.16, seg=6), "madera_clara")
    return p.objeto(col)


def _bloque(p, loc, tam, rot=(0, 0, 0), mat="roca_clara"):
    caja_biselada(p, mat, tam, loc, rot, bisel=min(tam) * 0.28, seg=3)


def ruina_arco(col, var):
    seed = 500 + var
    r = random.Random(seed)
    p = Pieza(f"ruina_arco_{'ab'[var]}", seed)
    sep = 9.0
    alturas = [4, 4] if var == 0 else [4, 2]
    for s, nb in zip((-1, 1), alturas):
        for i in range(nb):
            _bloque(p, (s * sep / 2 + r.uniform(-.2, .2), r.uniform(-.2, .2), 1.4 + i * 2.6), (3.0, 3.0, 2.5),
                    (0, 0, r.uniform(-.12, .12)), "roca_clara" if (i + s) % 2 else "roca")
    # dovelas del arco
    radio = sep / 2
    n = 7
    for k in range(n):
        if var == 1 and k > 3:
            continue
        a = math.pi - math.pi * k / (n - 1)
        x, z = radio * math.cos(a), 10.4 + radio * math.sin(a) * 0.95
        _bloque(p, (x, 0, z), (2.4, 2.8, 2.0), (0, -(a - math.pi / 2), 0), "roca")
    if var == 1:  # bloques caidos
        _bloque(p, (6.5, 3.5, 1.0), (2.4, 2.8, 2.0), (0.3, 0.2, 0.6), "roca")
        _bloque(p, (3.0, 4.5, 0.9), (2.4, 2.8, 2.0), (0.1, 0.4, 1.2), "roca_clara")
    # musgo y piedra-marca dorada (pista de cofre)
    p.anadir_bm(bm_blob(1.8, 2, 0.2, 1, seed, (1.3, 1, 0.35)), "musgo", mat_trs((-sep / 2, 0, 11.2)))
    p.anadir_bm(bm_cilindro(0.9, 0.9, 0.25, seg=12), "dorado", mat_trs((-sep / 2, -1.55, 3.0), (math.pi / 2, 0, 0)))
    return p.objeto(col)


def ruina_pilar(col, var=0):
    p = Pieza("ruina_pilar_a", 520)
    r = random.Random(520)
    for i in range(3):
        _bloque(p, (r.uniform(-.2, .2), r.uniform(-.2, .2), 1.3 + i * 2.5), (2.8, 2.8, 2.4), (0, 0, r.uniform(-.2, .2)),
                "roca_clara" if i % 2 else "roca")
    # flecha tallada dorada que apunta al cofre (+X local)
    bm = bm_cilindro(0.7, 0.0, 1.6, seg=3)
    p.anadir_bm(bm, "dorado", mat_trs((1.0, 0, 8.1), (0, math.pi / 2, 0)))
    p.anadir_bm(bm_blob(1.5, 2, 0.2, 1, 3, (1.2, 1, 0.3)), "musgo", mat_trs((0, 0, 7.3)))
    return p.objeto(col)


def valla(col, var):
    seed = 600 + var
    r = random.Random(seed)
    p = Pieza(f"valla_{'ab'[var]}", seed)
    for x in (-4, 4):
        inc = 0 if var == 0 else (0.25 if x > 0 else 0)
        p.anadir_bm(bm_tubo([(x, 0, -0.5), (x + inc * 3.5, 0, 3.6)], [0.38, 0.33], seg=8), "madera")
        p.anadir_bm(bm_blob(0.4, 1, 0, 1, 0), "madera", mat_trs((x + inc * 3.6, 0, 3.7)))
    for z in (1.4, 2.8):
        if var == 1 and z > 2:
            caja_biselada(p, "madera_clara", (5.0, 0.35, 0.55), (-1.5, 0, z), (0, -0.25, 0), bisel=0.12)
        else:
            caja_biselada(p, "madera_clara", (8.8, 0.35, 0.55), (0, 0.25, z), (0, 0, 0), bisel=0.12)
    return p.objeto(col)


def antorcha(col, var=0):
    p = Pieza("antorcha_a", 610)
    p.anadir_bm(bm_tubo([(0, 0, 0), (0.1, 0, 5.5)], [0.4, 0.32], seg=8), "madera")
    p.anadir_bm(bm_cilindro(0.55, 0.95, 0.9, seg=10), "roca_osc", mat_trs((0.1, 0, 5.4)))
    p.anadir_bm(bm_blob(0.75, 2, 0.15, 1.5, 1, (1, 1, 1.4)), "llama", mat_trs((0.1, 0, 6.8)))
    p.anadir_bm(bm_blob(0.45, 1, 0.1, 1, 2, (1, 1, 1.3)), "dorado", mat_trs((0.1, 0, 6.7)))
    return p.objeto(col)


def boca_cueva(col, var):
    """Montana rocosa con boca de cueva: metaballs -> malla, Boolean (tunel),
    Remesh voxel + Decimate. var b lleva marco de vigas."""
    seed = 700 + var
    r = random.Random(seed)
    mb = bpy.data.metaballs.new("_mb")
    mb.resolution = 1.6
    mb.threshold = 0.6
    masas = [((0, 0, 4), 14, (1.4, 1.0, 0.8)), ((-9, 6, 2), 10, (1.0, 1.0, 0.9)), ((10, 7, 3), 9, (1.1, 1.0, 1.0)),
             ((0, 9, 10), 9, (1.2, 1.0, 0.9)), ((4, -3, 9), 6, (1, 1, 1))]
    for (loc, rad, esc) in masas:
        e = mb.elements.new(type="ELLIPSOID")
        e.co = loc
        e.radius = rad
        e.size_x, e.size_y, e.size_z = [s * rad * 0.55 for s in esc]
    obm = bpy.data.objects.new("_mbo", mb)
    bpy.context.scene.collection.objects.link(obm)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obm.evaluated_get(dg))
    bpy.data.objects.remove(obm)
    bpy.data.metaballs.remove(mb)
    roca_o = bpy.data.objects.new("_roca", me)
    bpy.context.scene.collection.objects.link(roca_o)
    # tunel: tubo en arco que entra por -Y y se hunde
    tun = obj_temporal(bm_tubo([(0, -30, 3.2), (0, -12, 3.4), (0.5, 0, 2.5), (2, 10, 0.5), (3, 16, -4)],
                               [5.2, 5.0, 4.8, 4.4, 4.0], seg=16))
    bo = roca_o.modifiers.new("tunel", "BOOLEAN")
    bo.operation = "DIFFERENCE"
    bo.solver = "EXACT"
    bo.object = tun
    aplicar_mods(roca_o)
    borrar_obj(tun)
    # cortar por debajo del suelo
    bm = bmesh.new()
    bm.from_mesh(roca_o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -0.3),
                           plane_no=(0, 0, 1), clear_inner=True)
    bm.to_mesh(roca_o.data)
    bm.free()
    rm = roca_o.modifiers.new("remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = 0.9
    sm = roca_o.modifiers.new("suave", "SMOOTH")
    sm.iterations = 6
    sm.factor = 0.6
    aplicar_mods(roca_o)
    decimar(roca_o, 0.12)
    p = Pieza(f"boca_cueva_{'ab'[var]}", seed)
    # material por orientacion: arriba musgo/hierba, lados roca, interior oscuro
    bm = bmesh.new()
    bm.from_mesh(roca_o.data)
    bm.normal_update()
    p.mats = ["roca", "hierba", "roca_osc"]
    for f in bm.faces:
        c = f.calc_center_median()
        dentro = abs(c.x) < 6.5 and c.z < 9.5 and c.y > -16
        if f.normal.z > 0.6 and c.z > 3:
            f.material_index = 1
        elif dentro and f.normal.y < 0.5:
            f.material_index = 2
        else:
            f.material_index = 0
    me2 = bpy.data.meshes.new("_cv")
    bm.to_mesh(me2)
    bm.free()
    p.bm.from_mesh(me2)
    bpy.data.meshes.remove(me2)
    borrar_obj(roca_o)
    # orientar: la boca mira a -Y; en el suelo, z=0
    if var == 1:  # marco de vigas para que la boca se lea de lejos
        y0 = -12.0
        for x in (-4.6, 4.6):
            p.anadir_bm(bm_tubo([(x, y0, -0.5), (x * 0.95, y0, 7.6)], [0.6, 0.55], seg=8), "madera")
        p.anadir_bm(bm_tubo([(-5.6, y0, 7.6), (5.6, y0, 7.9)], [0.6, 0.6], seg=8), "madera")
        p.anadir_bm(bm_blob(0.6, 2, 0.1, 1.5, 1, (1, 1, 1.4)), "llama", mat_trs((5.6, y0 - 0.5, 6.4)))
    else:
        for k in range(4):
            a = r.uniform(0, TAU)
            p.anadir_bm(bm_blob(r.uniform(1.4, 2.4), 2, 0.2, 1, k, (1.2, 1, 0.7)), "roca_clara",
                        mat_trs((r.choice([-1, 1]) * r.uniform(7, 10), -12 - r.uniform(0, 4), 0.6)))
    return p.objeto(col)


# ======================================================== meta y portal
def meta_plataforma(col):
    p = Pieza("meta_plataforma", 800)
    R = 30.0
    p.anadir_bm(bm_cilindro(R, R + 1.5, 2.2, seg=48), "roca_clara", mat_trs((0, 0, -0.6)))
    p.anadir_bm(bm_cilindro(R - 3.5, R - 3.5, 0.3, seg=48), "tierra", mat_trs((0, 0, 1.5)))
    p.anadir_bm(bm_cilindro(12, 12, 0.35, seg=40), "roca", mat_trs((0, 0, 1.55)))
    # anillo de bloques redondeados en el borde
    n = 36
    r = random.Random(800)
    for k in range(n):
        a = TAU * k / n
        if k % 9 == 0:
            continue  # 4 aberturas
        _bloque(p, (math.cos(a) * (R - 1.0), math.sin(a) * (R - 1.0), 2.0), (2.8, 2.0, 1.2 + r.uniform(0, .5)),
                (0, 0, a), "roca" if k % 2 else "roca_clara")
    # posiciones de llegada 1/2/3 (podios)
    for i, (x, h) in enumerate(((0, 2.2), (-6, 1.5), (6, 1.0))):
        p.anadir_bm(bm_cilindro(2.4, 2.6, h, seg=20), "dorado" if i == 0 else "crema",
                    mat_trs((x, 18, 1.5)))
    return p.objeto(col)


def meta_arco(col):
    p = Pieza("meta_arco", 810)
    W, H = 26.0, 24.0
    for s in (-1, 1):
        x = s * W / 2
        for i in range(4):
            _bloque(p, (x, 0, 1.7 + i * 3.3), (4.4 - i * 0.2, 4.4 - i * 0.2, 3.0), (0, 0, 0.1 * (i % 2)),
                    "roca_clara" if i % 2 else "roca")
        p.anadir_bm(bm_tubo([(x, 0, 13.0), (x, 0, H + 1.5)], [1.4, 1.2], seg=10), "madera")
    pts = [(-W / 2 - 1, 0, H - 1), (-W / 4, 0, H + 1.4), (0, 0, H + 2.0), (W / 4, 0, H + 1.4), (W / 2 + 1, 0, H - 1)]
    p.anadir_bm(bm_tubo(pts, 1.3, seg=10), "madera")
    # cartel con emblema slime
    caja_biselada(p, "crema", (12.0, 1.0, 5.0), (0, -0.4, H - 3.2), bisel=0.5)
    caja_biselada(p, "madera_osc", (12.8, 0.6, 5.8), (0, 0.2, H - 3.2), bisel=0.3)
    bm = bm_blob(1.9, 3, 0.0, 1, 1, (1.2, 0.6, 0.85), base_plana=-0.9)
    p.anadir_bm(bm, "slime", mat_trs((0, -1.1, H - 3.6)))
    for x in (-0.6, 0.6):
        p.anadir_bm(bm_blob(0.32, 1, 0, 1, 0), "madera_osc", mat_trs((x, -2.0, H - 3.0)))
    # banderines dorados colgando del travesano
    for k in range(-4, 5):
        if k == 0:
            continue
        x = k * 2.6
        bm = bm_cilindro(0.9, 0.0, 2.2, seg=3)
        p.anadir_bm(bm, "dorado" if k % 2 else "coral", mat_trs((x, 0, H - 0.6 + 1.5 * (1 - (k / 5) ** 2)), (math.pi, 0, 0)))
    # antorchas en los pilares
    for s in (-1, 1):
        p.anadir_bm(bm_blob(0.9, 2, 0.15, 1.5, 1, (1, 1, 1.4)), "llama", mat_trs((s * W / 2, 0, H + 2.8)))
    return p.objeto(col)


def meta_banco(col):
    """Terminal de deposito: pedestal + barril-embudo + cristal grande."""
    p = Pieza("meta_banco", 820)
    p.anadir_bm(bm_cilindro(5.0, 5.6, 1.6, seg=24), "roca", mat_trs((0, 0, 0)))
    caja_biselada(p, "madera", (6.0, 6.0, 4.5), (0, 0, 3.8), bisel=0.6)
    for z in (2.2, 5.4):
        caja_biselada(p, "dorado", (6.3, 6.3, 0.5), (0, 0, z), bisel=0.2)
    p.anadir_bm(bm_cilindro(2.2, 3.6, 2.4, seg=16), "madera_osc", mat_trs((0, 0, 6.0)))
    bm = bm_cilindro(1.4, 1.4, 3.0, seg=6)
    p.anadir_bm(bm, "cristal", mat_trs((0, 0, 8.0)))
    p.anadir_bm(bm_cilindro(1.4, 0.0, 1.8, seg=6), "cristal", mat_trs((0, 0, 11.0)))
    caja_biselada(p, "crema", (3.0, 0.4, 1.6), (0, -3.15, 4.0), bisel=0.15)  # ranura
    caja_biselada(p, "madera_osc", (2.2, 0.5, 0.4), (0, -3.25, 4.0), bisel=0.1)
    return p.objeto(col)


def portal_salida(col):
    p = Pieza("portal_salida", 830)
    R = 7.5
    pts = [(R * math.cos(TAU * k / 28), 0, R + 1.2 + R * math.sin(TAU * k / 28)) for k in range(28)]
    p.anadir_bm(bm_tubo(pts, 1.3, seg=10, cerrado=True), "roca_clara")
    p.anadir_bm(bm_cilindro(R - 0.6, R - 0.6, 0.4, seg=32), "portal", mat_trs((0, 0.2, R + 1.2), (math.pi / 2, 0, 0)))
    for k in range(8):
        a = TAU * k / 8
        p.anadir_bm(bm_cilindro(0.5, 0.0, 1.6, seg=6), "cristal",
                    mat_trs(((R + 1.2) * math.cos(a), 0, R + 1.2 + (R + 1.2) * math.sin(a)), (0, -a + math.pi / 2, 0)))
    p.anadir_bm(bm_cilindro(5.0, 6.0, 1.2, seg=24), "roca", mat_trs((0, 0, -0.2)))
    return p.objeto(col)
