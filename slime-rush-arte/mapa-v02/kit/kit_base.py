"""Slime Rush - kit modular v0.2: utilidades comunes (Blender / bpy 5.0.1).

Todo se modela en Blender: bmesh + modificadores (Displace, Bevel, Subdivision,
Remesh, Boolean, Decimate) y se evalua con el depsgraph.
1 unidad Blender = 1 stud. Z arriba (el exportador glTF convierte a Y arriba).
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, noise

# ------------------------------------------------------------------ paleta
# 8 colores base del mundo (sRGB HEX). Los "tonos" son variaciones de valor
# del mismo matiz; las "senales" son colores de juego (recursos, cofres raros,
# portal) que deben destacar a proposito y NO forman parte de la paleta base.
PALETA_BASE = {
    "hierba":  "#78BE4A",
    "follaje": "#3F7A2C",
    "tierra":  "#C9935B",
    "roca":    "#9A9286",
    "arena":   "#EBCB86",
    "agua":    "#4DB6C9",
    "madera":  "#6E4A2F",
    "dorado":  "#FFD36E",
}
TONOS = {
    "hierba_clara": "#9CD25A",
    "follaje_claro": "#5C9E33",
    "musgo": "#8FC24A",
    "roca_osc": "#6F695F",
    "roca_clara": "#B9B2A4",
    "madera_osc": "#4F3420",
    "madera_clara": "#C9A274",
    "arena_osc": "#D6AE66",
    "tierra_osc": "#9C6B3F",
    "nieve": "#F2F5F7",          # bioma opcional de montana
    "crema": "#FFF1D6",
}
SENALES = {
    "cristal": "#B47CFF",        # recurso cristal de slime
    "ambar": "#FF9F2E",          # recurso ambar
    "gema": "#38E0D0",           # recurso gema de agua
    "coral": "#E0664A",          # sombreros de hongo / flores
    "rosa": "#F49AC1",           # flores
    "llama": "#FFB13B",          # antorchas (emisivo)
    "portal": "#7CF2C8",         # portal (emisivo)
    "slime": "#7BE36A",          # emblema slime
}
TODOS = {**PALETA_BASE, **TONOS, **SENALES}
EMISIVOS = {"llama": 6.0, "portal": 4.0}


def srgb_a_lineal(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def material(nombre):
    """Material mate (Principled, rugosidad alta, sin metal)."""
    mn = "SR_" + nombre
    if mn in bpy.data.materials:
        return bpy.data.materials[mn]
    m = bpy.data.materials.new(mn)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    col = srgb_a_lineal(TODOS[nombre]) + (1.0,)
    p.inputs["Base Color"].default_value = col
    p.inputs["Roughness"].default_value = 0.88
    p.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.25
    if nombre in EMISIVOS:
        p.inputs["Emission Color"].default_value = col
        p.inputs["Emission Strength"].default_value = EMISIVOS[nombre]
    m.diffuse_color = col
    return m


# ------------------------------------------------------------------ pieza
class Pieza:
    """Acumula geometria de varias partes (cada una con su material) en un
    solo bmesh y la convierte en un objeto Blender."""

    def __init__(self, nombre, seed=0):
        self.nombre = nombre
        self.bm = bmesh.new()
        self.mats = []
        self.rng = random.Random(seed)

    def _idx(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def anadir_bm(self, bm_parte, mat, matriz=Matrix()):
        """Copia un bmesh temporal (ya transformado por `matriz`)."""
        bmesh.ops.transform(bm_parte, matrix=matriz, verts=bm_parte.verts)
        me = bpy.data.meshes.new("_tmp")
        bm_parte.to_mesh(me)
        bm_parte.free()
        self.anadir_mesh(me, mat)
        bpy.data.meshes.remove(me)

    def anadir_mesh(self, me, mat, matriz=None):
        n0 = len(self.bm.faces)
        if matriz is not None:
            me = me.copy()
            me.transform(matriz)
        self.bm.from_mesh(me)
        self.bm.faces.ensure_lookup_table()
        i = self._idx(mat)
        for f in self.bm.faces[n0:]:
            f.material_index = i
        if matriz is not None:
            bpy.data.meshes.remove(me)

    def anadir_obj_evaluado(self, obj, mat):
        """Evalua un objeto temporal con sus modificadores y lo anade."""
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        me.transform(obj.matrix_world)
        self.anadir_mesh(me, mat)
        bpy.data.meshes.remove(me)
        borrar_obj(obj)

    def objeto(self, coleccion, suave=True):
        me = bpy.data.meshes.new(self.nombre)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(material(m))
        if suave:
            me.shade_smooth()
        ob = bpy.data.objects.new(self.nombre, me)
        coleccion.objects.link(ob)
        return ob


def borrar_obj(obj):
    me = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if me is not None and me.users == 0 and isinstance(me, bpy.types.Mesh):
        bpy.data.meshes.remove(me)


def obj_temporal(bm, nombre="_tmp"):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def aplicar_mods(obj):
    """Aplica todos los modificadores (via depsgraph, sin operadores)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


# ------------------------------------------------------------------ formas
def bm_blob(radio=1.0, subdiv=2, amp=0.18, freq=1.2, seed=0, escala=(1, 1, 1),
            base_plana=None):
    """Esfera 'masa redondeada' deformada con ruido suave de Blender."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radio)
    off = Vector((seed * 7.13, seed * 3.71, seed * 5.19))
    for v in bm.verts:
        d = v.co.normalized()
        n = noise.fractal(d * freq + off, 1.0, 2.0, 3)
        v.co = d * radio * (1.0 + amp * n)
        v.co = Vector((v.co.x * escala[0], v.co.y * escala[1], v.co.z * escala[2]))
        if base_plana is not None and v.co.z < base_plana:
            v.co.z = base_plana + (v.co.z - base_plana) * 0.15
    return bm


def bm_caja(sx, sy, sz):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    return bm


def bm_cilindro(r1, r2, alto, seg=10, tapas=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=tapas, cap_tris=False, segments=seg,
                          radius1=r1, radius2=r2, depth=alto)
    bmesh.ops.translate(bm, vec=(0, 0, alto / 2), verts=bm.verts)
    return bm


def bm_tubo(puntos, radios, seg=10, tapas=True, cerrado=False):
    """Barre un circulo por una polilinea (troncos, cuerdas, arcos)."""
    bm = bmesh.new()
    pts = [Vector(p) for p in puntos]
    n = len(pts)
    anillos = []
    prev_lado = None
    for i, p in enumerate(pts):
        if cerrado:
            t = (pts[(i + 1) % n] - pts[(i - 1) % n])
        elif i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        t.normalize()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        if prev_lado is None:
            lado = t.cross(ref).normalized()
        else:
            lado = (prev_lado - t * prev_lado.dot(t)).normalized()
        prev_lado = lado
        arriba = t.cross(lado).normalized()
        r = radios[i] if hasattr(radios, "__len__") else radios
        anillo = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            anillo.append(bm.verts.new(p + (lado * math.cos(a) + arriba * math.sin(a)) * r))
        anillos.append(anillo)
    m = n if cerrado else n - 1
    for i in range(m):
        a, b = anillos[i], anillos[(i + 1) % n]
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    if tapas and not cerrado:
        bm.faces.new(list(reversed(anillos[0])))
        bm.faces.new(anillos[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def mat_trs(loc=(0, 0, 0), rot=(0, 0, 0), esc=1.0):
    if not hasattr(esc, "__len__"):
        esc = (esc, esc, esc)
    S = Matrix.Diagonal((esc[0], esc[1], esc[2], 1.0))
    R = (Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y")
         @ Matrix.Rotation(rot[0], 4, "X"))
    return Matrix.Translation(loc) @ R @ S


def caja_biselada(pieza, mat, tam, loc=(0, 0, 0), rot=(0, 0, 0), bisel=0.25, seg=2):
    """Caja con bordes redondeados (modificador Bevel)."""
    ob = obj_temporal(bm_caja(*tam))
    ob.matrix_world = mat_trs(loc, rot)
    b = ob.modifiers.new("bisel", "BEVEL")
    b.width = bisel
    b.segments = seg
    b.limit_method = "NONE"
    pieza.anadir_obj_evaluado(ob, mat)


def decimar(obj, ratio):
    d = obj.modifiers.new("dec", "DECIMATE")
    d.ratio = ratio
    return aplicar_mods(obj)


def triangulos(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    ev.to_mesh_clear()
    return n


# ------------------------------------------------------------------ figura
def figura_escala(coleccion, loc=(0, 0, 0), rot_z=0.0, nombre="figura_6_studs"):
    """Figura tipo Roblox R6 de 6 studs exactos (piernas 2.4, torso 2.4,
    cabeza 1.2). Solo para renders: NO forma parte del kit exportado."""
    p = Pieza(nombre)
    caja_biselada(p, "dorado", (1.2, 1.2, 1.2), (0, 0, 5.4), bisel=0.12)
    caja_biselada(p, "agua", (2.4, 1.2, 2.4), (0, 0, 3.6), bisel=0.08)
    caja_biselada(p, "dorado", (1.0, 1.0, 2.4), (-1.75, 0, 3.6), bisel=0.08)
    caja_biselada(p, "dorado", (1.0, 1.0, 2.4), (1.75, 0, 3.6), bisel=0.08)
    caja_biselada(p, "follaje_claro", (1.1, 1.1, 2.4), (-0.6, 0, 1.2), bisel=0.08)
    caja_biselada(p, "follaje_claro", (1.1, 1.1, 2.4), (0.6, 0, 1.2), bisel=0.08)
    ob = p.objeto(coleccion, suave=False)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    return ob
