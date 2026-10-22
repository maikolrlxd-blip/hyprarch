"""Slime Rush - generador procedural de arboles cartoon v0.5.0.

Reproducible: mismas semillas -> misma geometria.
Uso (Python 3.11 con el modulo `bpy` 4.2 instalado por pip):
    python3 generar_arboles.py            # genera GLB/FBX + metricas
    python3 generar_arboles.py --render   # ademas renderiza los PNG (Cycles CPU)

Unidades: 1 unidad Blender = 1 stud (la figura de escala mide 6 unidades).
"""
import bpy
import bmesh
import math
import random
import json
import os
import sys
from mathutils import Vector, Matrix, noise

OUT = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.5.0"

# ---------------------------------------------------------------- materiales
# Colores mate cartoon (sRGB) -> se convierten a lineal para Blender/glTF.
PALETA = {
    "corteza":      "#6e4a2f",
    "corteza_osc":  "#4f3420",
    "musgo":        "#8fc24a",
    "hoja_nucleo":  "#2c4f1d",   # masa interior oscura: tapa huecos
    "hoja_osc":     "#3d7228",
    "hoja_media":   "#5c9e33",
    "hoja_clara":   "#84c442",
}
ORDEN_MAT = list(PALETA.keys())
M = {k: i for i, k in enumerate(ORDEN_MAT)}


def srgb_a_lineal(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def material(nombre, hexcol, rough=0.92):
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb_a_lineal(hexcol), 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.15
    return m


# ---------------------------------------------------------------- primitivas
def bezier(p0, p1, p2, p3, n):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        u = 1 - t
        pts.append(p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3)
    return pts


def marcos(pts):
    """Marcos por transporte paralelo a lo largo de la espina."""
    tans = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        tans.append((b - a).normalized())
    ref = Vector((1, 0, 0)) if abs(tans[0].x) < 0.9 else Vector((0, 1, 0))
    n = (ref - tans[0] * ref.dot(tans[0])).normalized()
    out = []
    for i, t in enumerate(tans):
        if i > 0:
            n = (n - t * n.dot(t)).normalized()
        out.append((t, n, t.cross(n).normalized()))
    return out


class Superficie:
    """Evalua la superficie exacta de un tubo en coordenadas continuas (s, theta)."""

    def __init__(self, pts, radios, surco_n, giro, ruido, semilla, amp_fn, aplastar):
        self.pts, self.radios, self.fr = pts, radios, marcos(pts)
        self.surco_n, self.giro, self.ruido = surco_n, giro, ruido
        self.sem = Vector((semilla, 0, 0))
        self.amp_fn, self.aplastar = amp_fn, aplastar

    def anillo_base(self, s):
        f = s * (len(self.pts) - 1)
        i = min(max(int(f), 0), len(self.pts) - 2)
        a = f - i
        p = self.pts[i].lerp(self.pts[i + 1], a)
        n = self.fr[i][1].lerp(self.fr[i + 1][1], a).normalized()
        b = self.fr[i][2].lerp(self.fr[i + 1][2], a).normalized()
        r = self.radios[i] * (1 - a) + self.radios[i + 1] * a
        return p, n, b, r

    def eval(self, s, th, extra=0.0):
        """Punto de la superficie + `extra` (fraccion del radio) hacia fuera."""
        p, n, b, r = self.anillo_base(s)
        d = n * math.cos(th) + b * math.sin(th)
        amp = self.amp_fn(s)
        surco = amp * (0.5 + 0.5 * math.cos(self.surco_n * th + self.giro * s))
        nz = self.ruido * noise.noise(p * 0.35 + d * 1.3 + self.sem)
        off = d * (r * (1.0 - amp * 0.5 + surco + nz + extra))
        if self.aplastar != 1.0:   # seccion ovalada (raices anchas y bajas)
            off.z *= self.aplastar
        return p + off, d


def tubo(bm, pts, radios, lados, mat, surco_amp=0.0, surco_n=6, giro=0.0,
         ruido=0.06, semilla=0.0, tapa_ini=True, tapa_fin=True, amp_fn=None, aplastar=1.0):
    """Tubo organico: anillos con surcos retorcidos y ruido suave. Devuelve su Superficie."""
    sup = Superficie(pts, radios, surco_n, giro, ruido, semilla,
                     amp_fn or (lambda s: surco_amp), aplastar)
    total = len(pts)
    anillos = []
    for i in range(total):
        s = i / (total - 1)
        anillos.append([bm.verts.new(sup.eval(s, 2 * math.pi * j / lados)[0])
                        for j in range(lados)])
    caras = []
    for i in range(total - 1):
        a, c = anillos[i], anillos[i + 1]
        for j in range(lados):
            k = (j + 1) % lados
            caras.append(bm.faces.new((a[j], a[k], c[k], c[j])))
    fr = sup.fr
    if tapa_ini:
        cv = bm.verts.new(pts[0] - fr[0][0] * radios[0] * 0.15)
        a = anillos[0]
        for j in range(lados):
            caras.append(bm.faces.new((cv, a[(j + 1) % lados], a[j])))
    if tapa_fin:
        cv = bm.verts.new(pts[-1] + fr[-1][0] * radios[-1] * 0.4)
        a = anillos[-1]
        for j in range(lados):
            caras.append(bm.faces.new((a[j], a[(j + 1) % lados], cv)))
    for f in caras:
        f.material_index = mat
    return sup


def parche_musgo(bm, sup, s0, th0, hs, hth, semilla, segs=20, anillos=4, grosor=0.09):
    """Cojin de musgo pegado a la superficie de un tubo: contorno organico suave,
    grosor maximo en el centro y ~0 en el borde (no deja cuchillas)."""
    centro = bm.verts.new(sup.eval(s0, th0, 0.015 + grosor)[0])
    off = Vector((semilla * 1.9, semilla * 0.7, 3.3))
    rings = []
    for ri in range(1, anillos + 1):
        rho = ri / anillos
        ring = []
        for k in range(segs):
            phi = 2 * math.pi * k / segs
            borde = 1.0 + 0.32 * noise.noise(Vector((math.cos(phi), math.sin(phi), 0)) * 1.4 + off)
            u, v = math.cos(phi) * rho * borde, math.sin(phi) * rho * borde
            ss = min(0.995, max(0.005, s0 + v * hs))
            alto = 0.015 + grosor * (1 - rho * rho) ** 0.7
            ring.append(bm.verts.new(sup.eval(ss, th0 + u * hth, alto)[0]))
        rings.append(ring)
    caras = []
    r0 = rings[0]
    for k in range(segs):
        caras.append(bm.faces.new((centro, r0[k], r0[(k + 1) % segs])))
    for a, c in zip(rings, rings[1:]):
        for k in range(segs):
            kk = (k + 1) % segs
            caras.append(bm.faces.new((a[k], c[k], c[kk], a[kk])))
    for f in caras:
        f.material_index = M["musgo"]


def blob(bm, centro, radios, mat, subdiv=2, rot=None, bulto=0.12, freq=1.7,
         semilla=0.0, nube=0.0):
    """Masa redondeada (icoesfera deformada). `nube` anade lobulos tipo nube."""
    ret = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0,
                                     matrix=Matrix.Identity(4), calc_uvs=False)
    vs = ret["verts"]
    rot = rot or Matrix.Identity(3)
    off = Vector((semilla * 3.1, semilla * 1.7, semilla * 2.3))
    for v in vs:
        p = v.co.normalized()
        d = 1.0 + bulto * noise.noise(p * freq + off)
        if nube:
            # lobulos redondos (hinchados): 1 - |ruido| da crestas suaves hacia fuera
            d += nube * (0.55 - abs(noise.noise(p * 2.6 + off * 1.3)))
        q = Vector((p.x * radios[0], p.y * radios[1], p.z * radios[2])) * d
        v.co = centro + rot @ q
    caras = set()
    for v in vs:
        caras.update(v.link_faces)
    for f in caras:
        f.material_index = mat
    return list(caras)


def orient_a(normal):
    """Matriz 3x3 cuyo eje Z apunta a `normal`."""
    z = normal.normalized()
    x = Vector((1, 0, 0)) if abs(z.x) < 0.9 else Vector((0, 1, 0))
    x = (x - z * x.dot(z)).normalized()
    y = z.cross(x)
    return Matrix((x, y, z)).transposed()


# ---------------------------------------------------------------- arbol
def construir_arbol(P, lod=0):
    rnd = random.Random(P["semilla"])
    S = P["semilla"] * 0.731
    bm = bmesh.new()
    hi = lod == 0
    # resoluciones por LOD
    R = dict(
        tr_anillos=40 if hi else 24, tr_lados=28 if hi else 16,
        rz_anillos=16 if hi else 10, rz_lados=14 if hi else 10,
        ra_anillos=14 if hi else 10, ra_lados=14 if hi else 10,
        nucleo=3 if hi else 2, lob_grande=3 if hi else 2, lob_chico=2 if hi else 1,
        musgo_seg=20 if hi else 12, musgo_an=4 if hi else 3,
    )

    # --- tronco: espina curvada y retorcida
    H = P["alto_tronco"]
    r0 = P["radio_base"]
    rt = P["radio_alto"]
    curva = P["curva"]
    esp = []
    n = R["tr_anillos"]
    for i in range(n):
        t = i / (n - 1)
        z = -1.5 + t * (H + 1.5)
        x = sum(a * math.sin(math.pi * f * t + ph) for a, f, ph in curva["x"]) - sum(
            a * math.sin(ph) for a, f, ph in curva["x"])
        y = sum(a * math.sin(math.pi * f * t + ph) for a, f, ph in curva["y"]) - sum(
            a * math.sin(ph) for a, f, ph in curva["y"])
        esp.append(Vector((x, y, z)))

    def radio_tronco(t):
        z = -1.5 + t * (H + 1.5)
        base = rt + (r0 - rt) * (1 - t) ** 1.4
        return base + r0 * P["ensanche"] * math.exp(-max(z, 0) / (0.09 * H))

    radios = [radio_tronco(i / (n - 1)) for i in range(n)]
    nraices = len(P["raices"])

    def amp_surco(s):
        z = -1.5 + s * (H + 1.5)
        return 0.20 + 0.30 * math.exp(-max(z, 0) / (0.08 * H))

    sup_tronco = tubo(bm, esp, radios, R["tr_lados"], M["corteza"], surco_n=max(5, nraices),
                      giro=P["giro"], ruido=0.07, semilla=S, amp_fn=amp_surco)

    def punto_tronco(t):
        f = t * (n - 1)
        i = min(int(f), n - 2)
        a = f - i
        return esp[i].lerp(esp[i + 1], a), radios[i] * (1 - a) + radios[i + 1] * a

    # --- raices: anchas, asimetricas, se hunden en el suelo
    raices_info = []
    for k, (ang, largo, grosor) in enumerate(P["raices"]):
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        p0 = Vector((0, 0, r0 * 1.1 * grosor + 0.6)) + d * r0 * 0.2
        L = r0 * largo
        p1 = p0 + d * L * 0.35 + Vector((0, 0, 0.25 * r0))
        lat = Vector((-d.y, d.x, 0)) * rnd.uniform(-0.25, 0.25) * L
        p2 = p0 + d * L * 0.75 + lat * 0.5 + Vector((0, 0, -0.1 * r0))
        p3 = p0 + d * L + lat + Vector((0, 0, -1.6 - 0.35 * r0))
        pts = bezier(p0, p1, p2, p3, R["rz_anillos"])
        rr = [r0 * 0.66 * grosor * (1 - 0.66 * (i / (len(pts) - 1)) ** 0.75)
              for i in range(len(pts))]
        sup = tubo(bm, pts, rr, R["rz_lados"], M["corteza"], surco_amp=0.14, surco_n=3,
             giro=1.5, ruido=0.08, semilla=S + k, tapa_ini=True, tapa_fin=True,
             aplastar=0.62)
        raices_info.append(sup)

    # --- copas (una o varias masas) y ramas gruesas hacia ellas
    lobulos_info = []
    ramas_info = []
    for ci, C in enumerate(P["copas"]):
        cen = Vector(C["centro"])
        Rx, Ry, Rzt, Rzb = C["radios"]
        # nucleo oscuro que rellena el interior: nada de huecos negros
        blob(bm, cen + Vector((0, 0, -0.08 * Rzt)), (Rx * 0.80, Ry * 0.80, (Rzt + Rzb) * 0.42),
             M["hoja_nucleo"], subdiv=R["nucleo"], bulto=0.10, semilla=S + 10 + ci)
        # lobulos en la superficie de la envolvente (Fibonacci con jitter)
        N = C["lobulos"]
        golden = math.pi * (3 - math.sqrt(5))
        for i in range(N):
            zz = 1 - 2 * (i + 0.5) / N
            zz = max(-0.92, zz)
            rr = math.sqrt(max(0.0, 1 - zz * zz))
            th = golden * i + ci * 1.3 + rnd.uniform(-0.25, 0.25)
            dirv = Vector((rr * math.cos(th), rr * math.sin(th), zz))
            rz = Rzt if zz > 0 else Rzb
            env = Vector((dirv.x * Rx, dirv.y * Ry, dirv.z * rz))
            base_r = C["r_lobulo"] * rnd.uniform(0.82, 1.12)
            if zz < -0.35:
                base_r *= 0.82
            pos = cen + env * rnd.uniform(0.70, 0.80)
            if zz > 0.45:
                mat = M["hoja_clara"]
            elif zz > -0.15:
                mat = M["hoja_media"]
            else:
                mat = M["hoja_osc"]
            # achatado hacia la envolvente y un poco mas plano en vertical
            esc = (base_r * rnd.uniform(1.0, 1.15), base_r * rnd.uniform(0.95, 1.1),
                   base_r * rnd.uniform(0.72, 0.85))
            rot = Matrix.Rotation(th, 3, "Z")
            grande = base_r >= C["r_lobulo"] * 0.9 or zz > (0.0 if hi else -0.4)
            blob(bm, pos, esc, mat, subdiv=R["lob_grande"] if grande else R["lob_chico"],
                 rot=rot, bulto=0.10, semilla=S + 20 + i + ci * 50,
                 nube=0.16 if (grande and hi) else 0.0)
            lobulos_info.append((pos, base_r, zz, ci))

        # ramas gruesas: del tronco a la parte baja de la copa
        for k in range(C["ramas"]):
            t0 = rnd.uniform(*C["rama_t"])
            p0, rad0 = punto_tronco(t0)
            ang = 2 * math.pi * k / C["ramas"] + rnd.uniform(-0.4, 0.4) + ci
            d = Vector((math.cos(ang), math.sin(ang), 0))
            fin = cen + Vector((d.x * Rx * 0.55, d.y * Ry * 0.55, -Rzb * 0.25))
            p1 = p0 + d * (fin - p0).length * 0.30 + Vector((0, 0, 1.0))
            p2 = fin - Vector((0, 0, (fin.z - p0.z) * 0.45))
            pts = bezier(p0, p1, p2, fin, R["ra_anillos"])
            rr0 = rad0 * C["rama_grosor"]
            rr = [rr0 * (1 - 0.55 * i / (len(pts) - 1)) for i in range(len(pts))]
            ramas_info.append(tubo(bm, pts, rr, R["ra_lados"], M["corteza"], surco_amp=0.12,
                                   surco_n=4, giro=2.0, ruido=0.07, semilla=S + 40 + k,
                                   tapa_ini=True, tapa_fin=True))

    # --- nudos en el tronco
    for k in range(P["nudos"]):
        t = rnd.uniform(0.15, 0.7)
        p, rad = punto_tronco(t)
        a = rnd.uniform(0, 2 * math.pi)
        d = Vector((math.cos(a), math.sin(a), 0))
        s = rad * rnd.uniform(0.22, 0.32)
        blob(bm, p + d * rad * 0.88, (s, s * 0.8, s * 0.55), M["corteza_osc"],
             subdiv=2 if hi else 1, rot=orient_a(d), bulto=0.15, semilla=S + 70 + k)

    # --- musgo: cojines pegados a tronco, lomo de raices y ramas
    seg = R["musgo_seg"]
    an = R["musgo_an"]
    la = math.radians(P["musgo_lado"])
    for k in range(P["musgo_tronco"]):
        s0 = rnd.uniform(0.06, 0.45)
        th0 = la + rnd.uniform(-1.4, 1.4)
        # theta del tronco es relativo a su marco: se compensa buscando la direccion
        mejor = max(range(24), key=lambda j: sup_tronco.eval(s0, 2 * math.pi * j / 24)[1].dot(
            Vector((math.cos(th0), math.sin(th0), 0))))
        th = 2 * math.pi * mejor / 24
        parche_musgo(bm, sup_tronco, s0, th, rnd.uniform(0.06, 0.12), rnd.uniform(0.5, 0.9),
                     S + 200 + k, seg, an, 0.08)
    def arriba(sup, s0):
        j = max(range(24), key=lambda j: sup.eval(s0, 2 * math.pi * j / 24)[1].z)
        return 2 * math.pi * j / 24
    for k in range(P["musgo_raices"]):
        sup = raices_info[k % nraices]
        s0 = rnd.uniform(0.2, 0.5)
        parche_musgo(bm, sup, s0, arriba(sup, s0), rnd.uniform(0.12, 0.2), rnd.uniform(0.7, 1.0),
                     S + 300 + k, seg, an, 0.10)
    for k in range(P["musgo_ramas"]):
        sup = ramas_info[k % len(ramas_info)]
        s0 = rnd.uniform(0.25, 0.6)
        parche_musgo(bm, sup, s0, arriba(sup, s0), rnd.uniform(0.12, 0.2), rnd.uniform(0.6, 0.9),
                     S + 400 + k, seg, an, 0.10)

    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    return bm


# ---------------------------------------------------------------- variantes
ARBOLES = {
    "roble_abuelo": dict(
        nombre="Roble Abuelo", semilla=11,
        alto_tronco=30.0, radio_base=4.6, radio_alto=3.0, ensanche=0.55, giro=4.0,
        curva={"x": [(1.2, 1.0, 0.0)], "y": [(0.8, 1.6, 0.6)]},
        raices=[(10, 2.6, 1.0), (75, 2.0, 0.85), (140, 2.9, 1.05), (205, 1.8, 0.8),
                (260, 2.4, 0.95), (320, 1.9, 0.8)],
        copas=[dict(centro=(0.8, 0.4, 37.0), radios=(24.0, 22.0, 11.0, 7.5), lobulos=30,
                    r_lobulo=9.0, ramas=5, rama_t=(0.62, 0.8), rama_grosor=0.55, hojas=12)],
        nudos=5, musgo_tronco=5, musgo_raices=3, musgo_ramas=0, musgo_lado=-40,
    ),
    "torcido": dict(
        nombre="Torcido", semilla=23,
        alto_tronco=46.0, radio_base=3.8, radio_alto=2.3, ensanche=0.6, giro=8.0,
        curva={"x": [(4.5, 1.3, 0.0)], "y": [(2.5, 2.2, 0.9)]},
        raices=[(20, 2.6, 1.1), (85, 1.9, 0.95), (150, 2.4, 1.05), (210, 2.9, 1.15),
                (290, 2.1, 1.0)],
        copas=[dict(centro=(2.0, 1.5, 53.0), radios=(14.0, 13.0, 10.0, 6.5), lobulos=24,
                    r_lobulo=6.8, ramas=3, rama_t=(0.8, 0.9), rama_grosor=0.55, hojas=9),
               dict(centro=(-8.5, -3.0, 37.0), radios=(9.0, 8.5, 5.5, 4.0), lobulos=14,
                    r_lobulo=5.0, ramas=1, rama_t=(0.55, 0.62), rama_grosor=0.6, hojas=6)],
        nudos=6, musgo_tronco=1, musgo_raices=1, musgo_ramas=0, musgo_lado=-30,
    ),
    "musgoso": dict(
        nombre="Musgoso", semilla=37,
        alto_tronco=25.0, radio_base=4.6, radio_alto=3.0, ensanche=0.6, giro=5.0,
        curva={"x": [(1.6, 1.2, 0.3)], "y": [(-1.2, 1.0, 0.0)]},
        raices=[(0, 3.1, 1.05), (60, 2.2, 0.9), (110, 2.8, 1.0), (170, 1.9, 0.8),
                (230, 3.2, 1.1), (300, 2.3, 0.9)],
        copas=[dict(centro=(9.0, 3.0, 33.0), radios=(17.0, 15.0, 8.5, 6.0), lobulos=22,
                    r_lobulo=7.5, ramas=3, rama_t=(0.62, 0.8), rama_grosor=0.55, hojas=7),
               dict(centro=(-10.0, -4.0, 31.0), radios=(15.0, 14.0, 8.0, 5.5), lobulos=20,
                    r_lobulo=7.0, ramas=3, rama_t=(0.58, 0.75), rama_grosor=0.55, hojas=7)],
        nudos=4, musgo_tronco=9, musgo_raices=6, musgo_ramas=5, musgo_lado=-60,
    ),
}


# ---------------------------------------------------------------- escena
def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def bm_a_objeto(bm, nombre, coleccion=None):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    for p in me.polygons:
        p.use_smooth = True
    for k in ORDEN_MAT:
        me.materials.append(material(k, PALETA[k], rough=0.95 if "hoja" in k or k == "musgo" else 0.9))
    ob = bpy.data.objects.new(nombre, me)
    (coleccion or bpy.context.scene.collection).objects.link(ob)
    return ob


def metricas(bm):
    bm.verts.ensure_lookup_table()
    tris = len(bm.faces)
    degen = sum(1 for f in bm.faces if f.calc_area() < 1e-6)
    sueltos = sum(1 for v in bm.verts if not v.link_faces)
    xs = [v.co for v in bm.verts]
    lo = Vector((min(p.x for p in xs), min(p.y for p in xs), min(p.z for p in xs)))
    hi = Vector((max(p.x for p in xs), max(p.y for p in xs), max(p.z for p in xs)))
    return dict(triangulos=tris, vertices=len(bm.verts), degenerados=degen,
                vertices_sueltos=sueltos,
                bbox_min=[round(c, 2) for c in lo], bbox_max=[round(c, 2) for c in hi],
                alto_sobre_suelo=round(hi.z, 2), ancho_x=round(hi.x - lo.x, 2),
                ancho_y=round(hi.y - lo.y, 2))


def exportar(ob, ruta_sin_ext, fbx=True):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=ruta_sin_ext + ".glb", export_format="GLB",
                              use_selection=True, export_apply=True, export_yup=True,
                              export_normals=True, export_texcoords=False)
    if fbx:
        bpy.ops.export_scene.fbx(filepath=ruta_sin_ext + ".fbx", use_selection=True,
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z",
                                 axis_up="Y", mesh_smooth_type="FACE")


def figura_escala(x, y, rot=0.0):
    """Maniqui tipo Roblox clasico (bloques), 6 studs de alto."""
    piezas = [  # (centro, tamano, color)
        ((-0.5, 0, 1.1), (1.0, 1.0, 2.2), "#2f6b2f"),
        ((0.5, 0, 1.1), (1.0, 1.0, 2.2), "#2f6b2f"),
        ((0, 0, 3.3), (2.0, 1.0, 2.2), "#2a64c8"),
        ((-1.5, 0, 3.3), (1.0, 1.0, 2.2), "#f2cf3a"),
        ((1.5, 0, 3.3), (1.0, 1.0, 2.2), "#f2cf3a"),
        ((0, 0, 5.25), (1.5, 1.5, 1.5), "#f2cf3a"),
    ]
    obs = []
    for i, (c, s, col) in enumerate(piezas):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        o = bpy.context.active_object
        o.scale = s
        o.location = c
        mat = material("figura_" + col, col, 0.7)
        o.data.materials.append(mat)
        obs.append(o)
    # piernas 2.2 + torso 2.2 + cuello 0.1 + cabeza 1.5 = 6.0 studs
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    f = bpy.context.active_object
    f.name = "Figura_6studs"
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    f.rotation_euler = (0, 0, rot)
    f.location = (x, y, 0)
    return f


def preparar_render(ancho, alto, muestras=48):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = muestras
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x = ancho
    sc.render.resolution_y = alto
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new("cielo")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*srgb_a_lineal("#a9d3f0"), 1)
    bg.inputs["Strength"].default_value = 1.15
    sol = bpy.data.lights.new("sol", "SUN")
    sol.energy = 3.2
    sol.angle = math.radians(6)
    so = bpy.data.objects.new("sol", sol)
    so.rotation_euler = (math.radians(48), 0, math.radians(-35))
    sc.collection.objects.link(so)


def suelo(tam=3000, color="#5f8a3a"):
    bpy.ops.mesh.primitive_plane_add(size=tam, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = "suelo"
    g.data.materials.append(material("suelo", color, 1.0))
    return g


def camara(objetivo, dist, azim, elev, lente=40):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lente
    cd.clip_end = 5000
    co = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(co)
    a, e = math.radians(azim), math.radians(elev)
    pos = Vector(objetivo) + Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * dist
    co.location = pos
    d = Vector(objetivo) - pos
    co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = co
    return co


def render(ruta):
    bpy.context.scene.render.filepath = ruta
    bpy.ops.render.render(write_still=True)


def camino(puntos, ancho=10.0, color="#b08a5a"):
    bm = bmesh.new()
    izq, der = [], []
    for i, p in enumerate(puntos):
        a = puntos[max(i - 1, 0)]
        b = puntos[min(i + 1, len(puntos) - 1)]
        t = (b - a).normalized()
        nrm = Vector((-t.y, t.x, 0))
        w = ancho * (0.85 + 0.15 * math.sin(i * 1.7))
        izq.append(bm.verts.new(p + nrm * w / 2 + Vector((0, 0, 0.06))))
        der.append(bm.verts.new(p - nrm * w / 2 + Vector((0, 0, 0.06))))
    for i in range(len(puntos) - 1):
        bm.faces.new((izq[i], der[i], der[i + 1], izq[i + 1]))
    me = bpy.data.meshes.new("camino")
    bm.to_mesh(me)
    me.materials.append(material("camino", color, 1.0))
    ob = bpy.data.objects.new("camino", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- main
def main():
    hacer_render = "--render" in sys.argv
    solo = [a for a in sys.argv if a.startswith("--solo=")]
    solo = solo[0].split("=")[1].split(",") if solo else None
    rapido = "--rapido" in sys.argv
    limpiar_escena()
    res = {}
    objs = {}
    for clave, P in ARBOLES.items():
        res[clave] = {"nombre": P["nombre"]}
        for lod in (0, 1):
            bm = construir_arbol(P, lod)
            res[clave][f"lod{lod}"] = metricas(bm)
            ob = bm_a_objeto(bm, f"Arbol_{clave}_v05_LOD{lod}")
            bm.free()
            exportar(ob, os.path.join(OUT, f"arbol_{clave}_v05_lod{lod}"), fbx=True)
            if lod == 0:
                objs[clave] = ob
            else:
                ob.hide_render = True
                ob.hide_set(True)
    with open(os.path.join(OUT, "metricas.json"), "w") as f:
        json.dump({"version": VERSION, "arboles": res}, f, indent=2, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if not hacer_render:
        return

    mu = 16 if rapido else 48
    preparar_render(1200, 1200, mu)
    suelo()
    fig = figura_escala(0, 0)
    # --- render individual de cada arbol con figura al lado (3/4)
    for clave, ob in objs.items():
        if solo and clave not in solo:
            continue
        for o in objs.values():
            o.hide_render = o is not ob
        m = res[clave]["lod0"]
        r0 = ARBOLES[clave]["radio_base"]
        # al lado del tronco, en el mismo plano de profundidad (perpendicular a la camara)
        fig.location = (0.766 * r0 * 3.6 + 0.643 * r0, 0.643 * r0 * 3.6 - 0.766 * r0, 0)
        fig.rotation_euler = (0, 0, math.radians(40))
        alto = m["alto_sobre_suelo"]
        cam = camara((0, 0, alto * 0.47), alto * 1.75, -50, 10, 40)
        render(os.path.join(OUT, f"preview_v05_{clave}_lod0_tres_cuartos_con_figura.png"))
        bpy.data.objects.remove(cam)
        # vista del jugador: a 5 studs del suelo, mirando hacia arriba a la copa (comprueba
        # que la parte inferior no es un plato plano ni deja ver huecos)
        cd = bpy.data.cameras.new("cam_abajo")
        cd.lens = 18
        cam = bpy.data.objects.new("cam_abajo", cd)
        bpy.context.scene.collection.objects.link(cam)
        cam.location = Vector((0.643, -0.766, 0)) * (m["ancho_x"] * 0.62) + Vector((0, 0, 5))
        dirc = Vector((0, 0, alto * 0.55)) - cam.location
        cam.rotation_euler = dirc.to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.camera = cam
        render(os.path.join(OUT, f"preview_v05_{clave}_lod0_vista_jugador_desde_abajo.png"))
        bpy.data.objects.remove(cam)
        # LOD1 para comparar
        if not rapido:
            l1 = bpy.data.objects[f"Arbol_{clave}_v05_LOD1"]
            ob.hide_render = True
            l1.hide_render = False
            cam = camara((0, 0, alto * 0.47), alto * 1.75, -50, 10, 40)
            render(os.path.join(OUT, f"preview_v05_{clave}_lod1_tres_cuartos.png"))
            bpy.data.objects.remove(cam)
            l1.hide_render = True
    if solo:
        return
    # --- conjunto de los 3
    pos = {"roble_abuelo": (-58, 0), "torcido": (0, 6), "musgoso": (60, -2)}
    for c, o in objs.items():
        o.hide_render = False
        o.location = (*pos[c], 0)
    fig.location = (-30, -22, 0)
    bpy.context.scene.render.resolution_x = 1800
    bpy.context.scene.render.resolution_y = 1000
    cam = camara((0, 0, 26), 175, -72, 10, 35)
    render(os.path.join(OUT, "preview_v05_conjunto_3_arboles_con_figura.png"))
    bpy.data.objects.remove(cam)

    # --- mini bosque: 5 arboles (3 modelos + 2 copias rotadas/escaladas) y camino
    copias = []
    for c, o in objs.items():
        o.location = (0, 0, 0)
    disp = [("roble_abuelo", (-62, 34), 0, 1.0), ("torcido", (-8, -38), 40, 1.0),
            ("musgoso", (40, 42), 200, 1.0), ("roble_abuelo", (92, -30), 130, 0.88),
            ("torcido", (-78, -48), 250, 0.92)]
    usados = set()
    for c, (x, y), rz, s in disp:
        if c in usados:
            o = objs[c].copy()
            bpy.context.scene.collection.objects.link(o)
            copias.append(o)
        else:
            o = objs[c]
            usados.add(c)
        o.location = (x, y, 0)
        o.rotation_euler = (0, 0, math.radians(rz))
        o.scale = (s, s, s)
        o.hide_render = False
    pts = [Vector((-170 + i * 10, 18 * math.sin(i * 0.22) - 2, 0)) for i in range(35)]
    camino(pts, 11.0)
    fig.location = (pts[19].x, pts[19].y, 0.06)
    fig.rotation_euler = (0, 0, math.radians(-60))
    cam = camara((5, 0, 16), 215, -78, 22, 32)
    render(os.path.join(OUT, "preview_v05_mini_bosque_5_arboles_camino.png"))


if __name__ == "__main__":
    main()
