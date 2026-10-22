# -*- coding: utf-8 -*-
"""
Slime Rush - Arboles cartoon v0.5.0 generados 100% con Blender (bpy 5.0.1).

Uso (desde la carpeta arboles-v05):
    python3 generar_arboles_blender.py                 # todo: arboles, exportes, renders
    python3 generar_arboles_blender.py --rapido        # renders de prueba a baja resolucion
    python3 generar_arboles_blender.py --solo roble    # solo un arbol (roble|torcido|musgoso)
    python3 generar_arboles_blender.py --sin-escenas   # sin render conjunto ni mini bosque

Pipeline por arbol (todo dentro de Blender):
  Tronco: curvas Bezier con radio por punto (tronco, raices, ramas, bultos de musgo)
          -> malla -> Remesh voxel (une todo en una sola superficie organica)
          -> Smooth -> surcos retorcidos + nudos (desplazamiento por normal con mathutils.noise)
          -> Decimate -> color por vertice (corteza, surcos oscuros, parches de musgo).
  Copa:   Metaball (lobulos gordos + nucleo interior que rellena) -> malla
          -> Displace suave -> Decimate -> color por vertice (gradiente, grietas oscuras).
  LOD1:   Decimate (collapse) del LOD0.
Unidades: 1 unidad de Blender = 1 stud (intencion; no verificado en Roblox Studio).
"""
import bpy, bmesh, math, random, json, os, sys, time
from mathutils import Vector, noise

AQUI = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[1:]
RAPIDO = "--rapido" in ARGS
SIN_ESCENAS = "--sin-escenas" in ARGS
SOLO = ARGS[ARGS.index("--solo") + 1] if "--solo" in ARGS else None
VERSION = "v05"

# ---------------------------------------------------------------- utilidades

def srgb2lin(c):
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def link(obj, col=None):
    (col or bpy.context.scene.collection).objects.link(obj)
    return obj


def bake(obj):
    """Aplica todos los modificadores usando el mesh evaluado del depsgraph."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    if old and old.users == 0 and isinstance(old, bpy.types.Mesh):
        bpy.data.meshes.remove(old)
    return obj


def tri_count(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    ev.to_mesh_clear()
    return n


def decimate_to(obj, target):
    cur = tri_count(obj)
    if cur > target:
        m = obj.modifiers.new("Decimate", "DECIMATE")
        m.decimate_type = "COLLAPSE"
        m.ratio = target / cur
        m.use_collapse_triangulate = True
        bake(obj)
    return obj


def limpiar(obj):
    """Quita vertices sueltos, caras degeneradas y recalcula normales."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-4)
    sueltos = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=sueltos, context="VERTS")
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = True


def auditar(obj):
    """Mide en el mesh evaluado: triangulos, vertices sueltos, triangulos degenerados."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    tris = len(me.loop_triangles)
    degen = sum(1 for t in me.loop_triangles if t.area < 1e-6)
    usados = set()
    for p in me.polygons:
        usados.update(p.vertices)
    sueltos = len(me.vertices) - len(usados)
    bm = bmesh.new()
    bm.from_mesh(me)
    no_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    ev.to_mesh_clear()
    return {"triangulos": tris, "vertices": len(me.vertices) if False else len(obj.data.vertices),
            "degenerados": degen, "vertices_sueltos": sueltos, "aristas_no_manifold": no_manifold}


def material(nombre, usa_vcol=True, color=(0.5, 0.5, 0.5)):
    mat = bpy.data.materials.get(nombre)
    if mat:
        return mat
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.0
    if usa_vcol:
        ca = nt.nodes.new("ShaderNodeVertexColor")
        ca.layer_name = "Col"
        nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (*srgb2lin(color), 1)
    mat.diffuse_color = (*srgb2lin(color), 1)
    return mat


def pintar(obj, funcion):
    """funcion(co, normal) -> (r,g,b) sRGB. Escribe atributo de color por vertice 'Col'."""
    me = obj.data
    if "Col" in me.color_attributes:
        me.color_attributes.remove(me.color_attributes["Col"])
    ca = me.color_attributes.new("Col", "BYTE_COLOR", "POINT")
    for v in me.vertices:
        c = funcion(v.co, v.normal)
        ca.data[v.index].color_srgb = (c[0], c[1], c[2], 1.0)
    me.color_attributes.active_color = ca
    me.color_attributes.render_color_index = me.color_attributes.find("Col")


# ---------------------------------------------------------------- tronco

def tubo_mesh(puntos, res_bevel=5, res_u=8):
    """puntos: lista de (Vector, radio). Devuelve un mesh (curva Bezier con bevel convertida)."""
    cu = bpy.data.curves.new("tubo", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_mode = "ROUND"
    cu.bevel_depth = 1.0
    cu.bevel_resolution = res_bevel
    cu.resolution_u = res_u
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(puntos) - 1)
    sp.radius_interpolation = "BSPLINE"
    for bp, (co, r) in zip(sp.bezier_points, puntos):
        bp.co = co
        bp.radius = r
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    ob = link(bpy.data.objects.new("tmp_tubo", cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return me


def esfera_mesh(centro, escala, seg=(16, 10)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * escala[0], v.co.y * escala[1], v.co.z * escala[2])) + centro
    me = bpy.data.meshes.new("esf")
    bm.to_mesh(me)
    bm.free()
    return me


def unir_mallas(nombre, mallas):
    bm = bmesh.new()
    for me in mallas:
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    return me


def eje_info(eje, p):
    """Punto mas cercano en la polilinea del tronco: (distancia, centro, radio, t_altura)."""
    mejor = None
    for i in range(len(eje) - 1):
        a, ra = eje[i]
        b, rb = eje[i + 1]
        ab = b - a
        t = clamp((p - a).dot(ab) / ab.length_squared)
        c = a + ab * t
        d = (p - c).length
        if mejor is None or d < mejor[0]:
            mejor = (d, c, ra + (rb - ra) * t, (i + t) / (len(eje) - 1))
    return mejor


def construir_tronco(spec, rng):
    nombre = spec["nombre"]
    T0 = time.time()
    mallas = []
    eje = spec["tronco"]
    mallas.append(tubo_mesh(eje, res_bevel=6, res_u=10))
    for raiz in spec["raices"]:
        mallas.append(tubo_mesh(raiz, res_bevel=4))
    for rama in spec["ramas"]:
        mallas.append(tubo_mesh(rama, res_bevel=4))
    bultos = spec.get("bultos_musgo", [])
    for (c, e) in bultos:
        mallas.append(esfera_mesh(c, e))
    me = unir_mallas(nombre + "_tronco_raw", mallas)
    print("  tubos:", len(me.vertices), "vertices", "%.1fs" % (time.time() - T0))
    ob = link(bpy.data.objects.new(nombre + "_Tronco", me))

    # Remesh voxel: fusiona tronco+raices+ramas+musgo en una superficie cerrada y organica
    rm = ob.modifiers.new("Remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = spec.get("voxel", 0.22)
    sm = ob.modifiers.new("Smooth", "SMOOTH")
    sm.factor = 1.0
    sm.iterations = 6
    bake(ob)
    print("  remesh tronco:", len(ob.data.vertices), "vertices", "%.1fs" % (time.time() - T0))

    # Surcos retorcidos + nudos (desplazamiento a lo largo de la normal)
    nsurcos = spec.get("surcos", 9)
    giro = spec.get("giro", 0.07)
    semilla = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    me = ob.data
    nv = len(me.vertices)
    cos = [0.0] * (nv * 3)
    nos = [0.0] * (nv * 3)
    me.vertices.foreach_get("co", cos)
    me.vertices.foreach_get("normal", nos)   # leer normales UNA vez (si no, se recalculan por vertice)
    nuevos = [0.0] * (nv * 3)
    for i in range(nv):
        p = Vector(cos[3 * i:3 * i + 3])
        n = Vector(nos[3 * i:3 * i + 3])
        d, c, r, th = eje_info(eje, p)
        disp = 0.0
        w = 1.0 - smooth((d - r * 0.9) / (r * 0.7))   # 1 sobre el tronco principal
        w *= smooth(p.z / 2.5)                          # se desvanece al tocar el suelo
        if w > 0:
            ang = math.atan2(p.y - c.y, p.x - c.x)
            s_ = math.sin(ang * nsurcos + p.z * giro * 2 * math.pi / 6.0
                          + 1.5 * noise.noise(p * 0.12 + semilla))
            surco = -(1.0 - abs(s_)) ** 3            # surcos estrechos
            disp += w * surco * spec.get("prof_surco", 0.7) * (r / 4.0) ** 0.5
        # nudos / bultos grandes y pequenos en todo el tronco, raices y ramas
        disp += 1.1 * max(0.0, noise.noise(p * 0.11 + semilla * 2)) ** 1.5
        disp += 0.12 * noise.noise(p * 0.45 + semilla)
        q = p + n * disp
        nuevos[3 * i:3 * i + 3] = (q.x, q.y, q.z)
    me.vertices.foreach_set("co", nuevos)
    me.update()
    sm = ob.modifiers.new("Smooth", "SMOOTH")
    sm.factor = 0.5
    sm.iterations = 1
    bake(ob)
    decimate_to(ob, spec["tris_tronco"])
    limpiar(ob)
    ob.data.materials.append(material("SR_Corteza_Mate", True, (0.40, 0.25, 0.14)))

    musgo_on = spec.get("musgo", 0.0)
    corteza = (0.42, 0.26, 0.14)
    corteza_clara = (0.52, 0.34, 0.19)
    corteza_osc = (0.24, 0.13, 0.07)
    musgo_a = (0.47, 0.70, 0.20)
    musgo_b = (0.62, 0.82, 0.28)

    def color_tronco(p, n):
        d, c, r, th = eje_info(eje, p)
        ang = math.atan2(p.y - c.y, p.x - c.x)
        s = math.sin(ang * nsurcos + p.z * giro * 2 * math.pi / 6.0 + 1.5 * noise.noise(p * 0.12 + semilla))
        w = 1.0 - smooth((d - r * 0.9) / (r * 0.7))
        base = lerp(corteza, corteza_clara, clamp(0.5 + 0.5 * noise.noise(p * 0.2 + semilla)) * 0.7)
        if w > 0:
            base = lerp(base, corteza_osc, w * (1.0 - abs(s)) ** 4 * 0.9)
        base = lerp(base, corteza_osc, 0.35 * (1 - smooth(p.z / 3.0)))   # oscurece la base
        col = base
        if musgo_on > 0:
            m = 0.0
            for (bc, be) in bultos:
                q = Vector(((p.x - bc.x) / be[0], (p.y - bc.y) / be[1], (p.z - bc.z) / be[2]))
                m = max(m, 1.0 - smooth((q.length - 0.9) / 0.5))
            altura = 1.0 - smooth((p.z - spec["musgo_altura"]) / 6.0)
            mira_arriba = smooth((n.z + 0.35) / 0.8)
            mancha = noise.noise(p * 0.16 + semilla * 3) + 0.25 * noise.noise(p * 0.6)
            m = max(m, smooth((mancha - (0.35 - musgo_on)) / 0.12) * altura * mira_arriba)
            if m > 0:
                mc = lerp(musgo_a, musgo_b, clamp(0.5 + noise.noise(p * 0.5)))
                col = lerp(col, mc, m)
        return col

    pintar(ob, color_tronco)
    print("  tronco listo %.1fs" % (time.time() - T0))
    return ob


# ---------------------------------------------------------------- copa

def construir_copa(spec, rng):
    """Copa = union de lobulos esfericos gordos + nucleo interior, fusionados con Remesh voxel.
    El remesh deja una sola superficie cerrada (sin huecos, sin caras internas) con grietas
    redondeadas entre lobulos (estilo nube/cartoon)."""
    nombre = spec["nombre"]
    T0 = time.time()
    lobulos = []
    mallas = []
    for (C, R, nlob, rlob) in spec["copas"]:
        C = Vector(C)
        # nucleo interior: masa que rellena todo el volumen
        mallas.append(esfera_mesh(C + Vector((0, 0, -R[2] * 0.05)), (R[0] * 0.70, R[1] * 0.70, R[2] * 0.68), seg=(32, 20)))
        golden = math.pi * (3 - math.sqrt(5))
        for i in range(nlob):
            z = 1 - 2 * (i + 0.5) / nlob
            rr = math.sqrt(1 - z * z)
            a_ = i * golden + rng.uniform(-0.3, 0.3)
            dirv = Vector((math.cos(a_) * rr, math.sin(a_) * rr, z))
            if z < -0.82:          # el fondo central lo cubre el nucleo (entrada de las ramas)
                continue
            f = rng.uniform(0.66, 0.80)
            pos = C + Vector((dirv.x * R[0] * f, dirv.y * R[1] * f, dirv.z * R[2] * f))
            pos += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.5, 0.5)))
            r = rlob * rng.uniform(0.82, 1.2) * (0.92 if z < -0.3 else 1.0)
            esc = (r, r, r * rng.uniform(0.82, 0.95))
            mallas.append(esfera_mesh(pos, esc, seg=(24, 14)))
            lobulos.append((pos, r))
    me = unir_mallas(nombre + "_copa_raw", mallas)
    cop = link(bpy.data.objects.new(nombre + "_Copa", me))
    rm = cop.modifiers.new("Remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = spec.get("voxel_copa", 0.3)
    sm = cop.modifiers.new("Smooth", "SMOOTH")
    sm.factor = 1.0
    sm.iterations = spec.get("suavizado_copa", 4)
    # ondulacion suave para que no sean esferas perfectas
    tex = bpy.data.textures.new("ruido_copa_" + nombre, "CLOUDS")
    tex.noise_scale = 5.0
    dm = cop.modifiers.new("Displace", "DISPLACE")
    dm.texture = tex
    dm.strength = 0.7
    dm.mid_level = 0.5
    bake(cop)
    print("  copa remesh:", len(cop.data.vertices), "vertices %.1fs" % (time.time() - T0))
    decimate_to(cop, spec["tris_copa"])
    limpiar(cop)
    cop.data.materials.append(material("SR_Hojas_Mate", True, (0.30, 0.60, 0.20)))

    hoja_osc = (0.10, 0.30, 0.09)
    hoja_med = (0.25, 0.56, 0.16)
    hoja_cla = (0.56, 0.82, 0.28)
    me = cop.data
    zs = [v.co.z for v in me.vertices]
    zmin, zmax = min(zs), max(zs)
    exteriores = lobulos
    semilla = Vector((rng.uniform(0, 50), rng.uniform(0, 50), 0))
    tonos = [rng.uniform(-0.13, 0.13) for _ in exteriores]

    def color_copa(p, n):
        # lobulo dominante (d1) y segundo (d2): donde d1~d2 hay costura/grieta -> mas oscuro
        d1, d2, bi = 1e9, 1e9, 0
        for i, (c, r) in enumerate(exteriores):
            q = (p - c).length / r
            if q < d1:
                d1, d2, bi = q, d1, i
            elif q < d2:
                d2 = q
        costura = 1.0 - smooth((d2 - d1) / 0.22)
        hundido = smooth((d1 - 1.05) / 0.35)        # zonas que solo cubre el nucleo
        h = (p.z - zmin) / (zmax - zmin)
        luz = 0.30 + 0.40 * h + 0.30 * n.z + tonos[bi] + 0.05 * noise.noise(p * 0.3 + semilla)
        luz -= 0.30 * costura + 0.35 * hundido
        luz = clamp(luz)
        if luz < 0.5:
            return lerp(hoja_osc, hoja_med, smooth(luz / 0.5))
        return lerp(hoja_med, hoja_cla, smooth((luz - 0.5) / 0.5))

    pintar(cop, color_copa)
    return cop


# ---------------------------------------------------------------- especificaciones

def V(x, y, z):
    return Vector((x, y, z))


def raiz(rng, ang, largo, r0, z0=2.6, sube=1.4):
    d = V(math.cos(ang), math.sin(ang), 0)
    lado = V(-d.y, d.x, 0) * rng.uniform(-0.25, 0.25)
    pts = [
        (V(0, 0, z0 + 1.0) + d * 0.5, r0),
        (d * (largo * 0.30) + lado * largo * 0.3 + V(0, 0, z0 * 0.55 + sube * 0.3), r0 * 0.78),
        (d * (largo * 0.62) + lado * largo * 0.6 + V(0, 0, sube * 0.45), r0 * 0.50),
        (d * largo + lado * largo + V(0, 0, -0.5), r0 * 0.22),
    ]
    return pts


def spec_roble(rng):
    eje = [(V(0, 0, -0.6), 5.0), (V(0, 0, 3), 4.4), (V(0.6, 0.3, 9), 3.8), (V(1.4, -0.4, 15), 3.6),
           (V(0.8, -0.8, 21), 3.5), (V(0.2, -0.4, 26), 3.3)]
    raices = []
    angs = [0.2, 1.25, 2.1, 3.0, 3.9, 4.8, 5.6]
    largos = [12, 8, 13, 9, 11, 7.5, 10]
    for a, l in zip(angs, largos):
        raices.append(raiz(rng, a + rng.uniform(-0.15, 0.15), l, rng.uniform(1.9, 2.5)))
    top = V(0.2, -0.4, 26)
    ramas = []
    for a, l, h, r in [(0.3, 13, 9, 2.4), (1.6, 11, 11, 2.2), (2.8, 14, 8, 2.5), (4.1, 12, 10, 2.3), (5.2, 10, 12, 2.0)]:
        d = V(math.cos(a), math.sin(a), 0)
        ramas.append([(top + V(0, 0, -3), r * 1.1), (top + d * l * 0.4 + V(0, 0, h * 0.35), r * 0.85),
                      (top + d * l * 0.8 + V(0, 0, h * 0.8), r * 0.6), (top + d * l + V(0, 0, h * 1.2), r * 0.45)])
    ramas.append([(top + V(0, 0, -2), 2.4), (top + V(0.5, 0.3, 8), 1.9), (top + V(-0.3, 0.6, 15), 1.4)])
    bultos = [(V(4.0, 1.0, 1.6), (2.6, 2.2, 1.3)), (V(-3.0, 3.2, 1.2), (2.2, 2.4, 1.1)),
              (V(1.5, -4.0, 3.5), (2.0, 1.5, 2.2)), (V(-4.2, -1.5, 6.5), (1.4, 1.8, 2.2))]
    return {
        "nombre": "RobleAbuelo", "archivo": "arbol_roble_abuelo",
        "tronco": eje, "raices": raices, "ramas": ramas, "bultos_musgo": bultos,
        "musgo": 0.12, "musgo_altura": 9.0, "surcos": 10, "giro": 0.35,
        "copas": [((0.5, -0.3, 40.0), (21.0, 19.0, 11.0), 34, 8.2)],
        "tris_tronco": 8500, "tris_copa": 12500, "lod1": 6500,
    }


def spec_torcido(rng):
    eje = [(V(0, 0, -0.6), 4.0), (V(0, 0, 3), 3.5), (V(1.8, 0.6, 12), 3.0), (V(3.6, 0.0, 22), 2.8),
           (V(2.2, -1.0, 32), 2.6), (V(-0.5, -0.6, 40), 2.4), (V(-1.5, 0.3, 46), 2.1)]
    raices = []
    for a, l in zip([0.5, 1.7, 2.9, 4.0, 5.3], [10, 7, 11, 8, 9.5]):
        raices.append(raiz(rng, a + rng.uniform(-0.2, 0.2), l, rng.uniform(1.6, 2.1), z0=2.2))
    top = V(-1.5, 0.3, 46)
    ramas = [
        [(top + V(0, 0, -2), 2.0), (top + V(-3, 1, 4), 1.6), (top + V(-5, 2, 9), 1.2)],
        [(top + V(0, 0, -2), 2.0), (top + V(4, -1, 4), 1.6), (top + V(7, -1, 8), 1.2)],
        [(top + V(0, 0, -1), 1.9), (top + V(0.5, 1, 7), 1.5), (top + V(1, 0, 12), 1.1)],
        # rama lateral baja que sostiene la copa secundaria
        [(V(3.0, 0.2, 26), 2.0), (V(7.0, 2.0, 29), 1.6), (V(11.0, 3.5, 31), 1.2)],
    ]
    return {
        "nombre": "Torcido", "archivo": "arbol_torcido",
        "tronco": eje, "raices": raices, "ramas": ramas, "bultos_musgo": [],
        "musgo": 0.0, "musgo_altura": 0, "surcos": 8, "giro": 0.55,
        "copas": [((-0.5, 0.5, 55.0), (13.0, 12.0, 9.5), 24, 6.2),
                  ((12.0, 4.0, 33.0), (7.5, 7.0, 5.0), 11, 4.4)],
        "tris_tronco": 8000, "tris_copa": 12000, "lod1": 6000,
    }


def spec_musgoso(rng):
    eje = [(V(0, 0, -0.6), 5.6), (V(0, 0, 3), 5.0), (V(-0.8, 0.5, 8), 4.3), (V(-0.2, 1.2, 13), 4.0),
           (V(0.6, 0.6, 18), 3.8)]
    raices = []
    for a, l in zip([0.0, 0.9, 1.8, 2.6, 3.5, 4.3, 5.1, 5.8], [14, 9, 12, 8, 15, 10, 8.5, 11]):
        raices.append(raiz(rng, a + rng.uniform(-0.15, 0.15), l, rng.uniform(2.1, 2.7), z0=2.8))
    top = V(0.6, 0.6, 18)
    ramas = []
    for a, l, h, r in [(0.1, 18, 9, 2.6), (1.3, 15, 11, 2.3), (2.4, 19, 8, 2.6), (3.5, 16, 10, 2.4),
                       (4.6, 18, 9, 2.5), (5.6, 14, 12, 2.2)]:
        d = V(math.cos(a), math.sin(a), 0)
        ramas.append([(top + V(0, 0, -3), r * 1.15), (top + d * l * 0.35 + V(0, 0, h * 0.3), r * 0.9),
                      (top + d * l * 0.75 + V(0, 0, h * 0.65), r * 0.65), (top + d * l + V(0, 0, h * 1.0), r * 0.45)])
    bultos = [(V(4.5, 1.5, 1.5), (3.0, 2.6, 1.5)), (V(-4.0, 3.5, 1.4), (2.8, 2.6, 1.3)),
              (V(-1.0, -5.0, 1.8), (2.6, 2.2, 1.6)), (V(2.0, 4.6, 6.0), (2.0, 1.4, 2.8)),
              (V(-4.6, -1.0, 9.0), (1.4, 2.4, 2.6)), (V(10.0, -2.0, 0.9), (2.0, 1.8, 0.9)),
              (V(3.5, -3.0, 13.0), (1.6, 1.6, 2.0))]
    return {
        "nombre": "Musgoso", "archivo": "arbol_musgoso",
        "tronco": eje, "raices": raices, "ramas": ramas, "bultos_musgo": bultos,
        "musgo": 0.30, "musgo_altura": 16.0, "surcos": 11, "giro": 0.25,
        "copas": [((0.5, 0.5, 32.0), (26.0, 23.0, 9.5), 40, 8.0)],
        "tris_tronco": 9000, "tris_copa": 13500, "lod1": 7000,
    }


SPECS = {"roble": (spec_roble, 11), "torcido": (spec_torcido, 23), "musgoso": (spec_musgoso, 37)}


# ---------------------------------------------------------------- escena / render

def figura_roblox(col, pos=(0, 0, 0), rot=0.0):
    """Maniqui tipo Roblox R6 de ~6 unidades de alto (bloques)."""
    piezas = [
        ("Pierna_I", (-0.6, 0, 1.2), (1.15, 1.15, 2.4), (0.20, 0.62, 0.20)),
        ("Pierna_D", (0.6, 0, 1.2), (1.15, 1.15, 2.4), (0.20, 0.62, 0.20)),
        ("Torso", (0, 0, 3.6), (2.4, 1.2, 2.4), (0.10, 0.40, 0.85)),
        ("Brazo_I", (-1.8, 0, 3.6), (1.15, 1.15, 2.4), (0.98, 0.82, 0.20)),
        ("Brazo_D", (1.8, 0, 3.6), (1.15, 1.15, 2.4), (0.98, 0.82, 0.20)),
        ("Cabeza", (0, 0, 5.4), (1.2, 1.2, 1.2), (0.98, 0.82, 0.20)),
    ]
    objs = []
    for n, c, s, color in piezas:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.08, segments=2, affect="EDGES")
        for v in bm.verts:
            v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
        me = bpy.data.meshes.new("Figura_" + n)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("FiguraEscala6_" + n, me)
        ob.location = Vector(c)
        ob.data.materials.append(material("Figura_" + n.split("_")[0] + str(color), False, color))
        col.objects.link(ob)
        objs.append(ob)
    padre = bpy.data.objects.new("FiguraEscala6", None)
    col.objects.link(padre)
    for o in objs:
        o.parent = padre
    padre.location = Vector(pos)
    padre.rotation_euler = (0, 0, rot)
    return padre


def preparar_escena(muestras=32, res=(1600, 1000)):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 12 if RAPIDO else muestras
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = (res[0] // 2, res[1] // 2) if RAPIDO else res
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new("Cielo")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*srgb2lin((0.66, 0.84, 0.98)), 1)
    bg.inputs["Strength"].default_value = 0.9
    sc.world = w
    sol = bpy.data.lights.new("Sol", "SUN")
    sol.energy = 3.2
    sol.angle = math.radians(6)
    sol.color = srgb2lin((1.0, 0.96, 0.88))
    so = link(bpy.data.objects.new("Sol", sol))
    so.rotation_euler = (math.radians(42), math.radians(8), math.radians(-35))
    # suelo
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=600)
    me = bpy.data.meshes.new("Suelo")
    bm.to_mesh(me)
    bm.free()
    suelo = link(bpy.data.objects.new("Suelo", me))
    suelo.data.materials.append(material("Suelo_Cesped", False, (0.38, 0.62, 0.26)))
    return sc


def camara(objetivo, direccion, dist, lente=35, nombre="Cam"):
    cam = bpy.data.cameras.new(nombre)
    cam.lens = lente
    cam.clip_end = 2000
    co = link(bpy.data.objects.new(nombre, cam))
    d = Vector(direccion).normalized()
    co.location = Vector(objetivo) + d * dist
    co.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = co
    return co


def render(ruta):
    bpy.context.scene.render.filepath = ruta
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("  render", os.path.basename(ruta), "%.1fs" % (time.time() - t))


# ---------------------------------------------------------------- flujo por arbol

def exportar(objs, ruta_base):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=ruta_base + ".glb", export_format="GLB", use_selection=True,
                              export_apply=True, export_vertex_color="ACTIVE")
    bpy.ops.export_scene.fbx(filepath=ruta_base + ".fbx", use_selection=True, apply_unit_scale=True,
                             object_types={"MESH"}, mesh_smooth_type="FACE", colors_type="SRGB")


def hacer_arbol(clave):
    fn, seed = SPECS[clave]
    reset()
    rng = random.Random(seed)
    spec = fn(rng)
    t0 = time.time()
    col0 = bpy.data.collections.new(spec["nombre"] + "_LOD0")
    bpy.context.scene.collection.children.link(col0)
    tronco = construir_tronco(spec, rng)
    copa = construir_copa(spec, rng)
    for o in (tronco, copa):
        bpy.context.scene.collection.objects.unlink(o)
        col0.objects.link(o)
        o.name = o.name + "_LOD0"
    # LOD1
    col1 = bpy.data.collections.new(spec["nombre"] + "_LOD1")
    bpy.context.scene.collection.children.link(col1)
    lod0_total = tri_count(tronco) + tri_count(copa)
    lod1 = []
    for o in (tronco, copa):
        c = o.copy()
        c.data = o.data.copy()
        c.name = o.name.replace("_LOD0", "_LOD1")
        col1.objects.link(c)
        decimate_to(c, max(400, int(tri_count(o) * spec["lod1"] / lod0_total)))
        limpiar(c)
        lod1.append(c)
    print(spec["nombre"], "construido en %.1fs" % (time.time() - t0))

    met = {"arbol": spec["nombre"], "LOD0": {}, "LOD1": {}}
    for o in (tronco, copa):
        met["LOD0"][o.name] = auditar(o)
    for o in lod1:
        met["LOD1"][o.name] = auditar(o)
    for lod in ("LOD0", "LOD1"):
        met[lod]["total_triangulos"] = sum(v["triangulos"] for v in met[lod].values())
    zmax = max((copa.matrix_world @ Vector(b)).z for b in copa.bound_box)
    xs = [(o.matrix_world @ Vector(b)) for o in (tronco, copa) for b in o.bound_box]
    met["altura"] = round(zmax, 2)
    met["ancho_x"] = round(max(p.x for p in xs) - min(p.x for p in xs), 2)
    met["ancho_y"] = round(max(p.y for p in xs) - min(p.y for p in xs), 2)

    base = os.path.join(AQUI, spec["archivo"] + "_" + VERSION)
    col1.hide_viewport = True
    col1.hide_render = True
    exportar([tronco, copa], base + "_lod0")
    col1.hide_viewport = False
    exportar(lod1, base + "_lod1")
    col1.hide_viewport = True

    # escena de preview con figura de escala
    preparar_escena()
    colf = bpy.data.collections.new("Escena_Preview")
    bpy.context.scene.collection.children.link(colf)
    ancho = max(met["ancho_x"], met["ancho_y"])
    figura_roblox(colf, pos=(ancho * 0.32, -ancho * 0.42, 0), rot=math.radians(20))
    alto = met["altura"]
    bpy.ops.wm.save_as_mainfile(filepath=base + ".blend")
    camara((0, 0, alto * 0.42), (0.85, -1.0, 0.32), dist=max(alto, ancho) * 1.75)
    render(os.path.join(AQUI, "preview_%s_%s_lod0_tres_cuartos_con_figura.png" % (VERSION, spec["archivo"].replace("arbol_", ""))))
    if not RAPIDO:
        # LOD1 con la misma camara
        col0.hide_render = True
        col1.hide_render = False
        render(os.path.join(AQUI, "preview_%s_%s_lod1_tres_cuartos.png" % (VERSION, spec["archivo"].replace("arbol_", ""))))
        col0.hide_render = False
        col1.hide_render = True
        # vista desde abajo (jugador) para comprobar que la copa no es un plato plano
        camara((0, 0, alto * 0.62), (0.9, -1.0, -0.12), dist=ancho * 1.05, lente=24, nombre="CamAbajo")
        bpy.context.scene.camera.location.z = 4.5
        bpy.context.scene.camera.rotation_euler = (Vector((0, 0, alto * 0.62)) - bpy.context.scene.camera.location).to_track_quat("-Z", "Y").to_euler()
        render(os.path.join(AQUI, "preview_%s_%s_lod0_vista_jugador_desde_abajo.png" % (VERSION, spec["archivo"].replace("arbol_", ""))))
    return met


def cargar_arbol(clave, col, pos, rot=0.0, escala=1.0):
    fn, seed = SPECS[clave]
    spec = fn(random.Random(seed))
    ruta = os.path.join(AQUI, spec["archivo"] + "_" + VERSION + ".blend")
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n.endswith("_LOD0")]
    padre = bpy.data.objects.new("Arbol_" + clave, None)
    col.objects.link(padre)
    for o in dst.objects:
        o = o.copy()
        col.objects.link(o)
        o.parent = padre
    padre.location = Vector(pos)
    padre.rotation_euler = (0, 0, rot)
    padre.scale = (escala, escala, escala)
    return padre


def camino(col, puntos, ancho=7.0):
    bm = bmesh.new()
    prev = None
    filas = []
    for i, p in enumerate(puntos):
        a = puntos[max(0, i - 1)]
        b = puntos[min(len(puntos) - 1, i + 1)]
        t = (Vector(b) - Vector(a)).normalized()
        nrm = Vector((-t.y, t.x, 0))
        w = ancho * (1 + 0.15 * math.sin(i * 1.7))
        filas.append((bm.verts.new(Vector(p) + nrm * w / 2 + Vector((0, 0, 0.04))),
                      bm.verts.new(Vector(p) - nrm * w / 2 + Vector((0, 0, 0.04)))))
    for i in range(len(filas) - 1):
        bm.faces.new((filas[i][0], filas[i][1], filas[i + 1][1], filas[i + 1][0]))
    me = bpy.data.meshes.new("Camino")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Camino", me)
    ob.data.materials.append(material("Camino_Tierra", False, (0.66, 0.52, 0.32)))
    col.objects.link(ob)
    return ob


def escenas():
    # render conjunto de los 3
    reset()
    preparar_escena(res=(1800, 1000))
    col = bpy.data.collections.new("Conjunto")
    bpy.context.scene.collection.children.link(col)
    cargar_arbol("roble", col, (-48, 0, 0), 0.3)
    cargar_arbol("torcido", col, (0, 10, 0), 0.0)
    cargar_arbol("musgoso", col, (52, -4, 0), 0.8)
    figura_roblox(col, pos=(-22, -22, 0), rot=math.radians(15))
    figura_roblox(col, pos=(22, -26, 0), rot=math.radians(-25))
    camara((2, 0, 26), (0.12, -1.0, 0.18), dist=150, lente=35)
    render(os.path.join(AQUI, "preview_%s_conjunto_3_arboles_con_figuras.png" % VERSION))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "escena_%s_conjunto_3_arboles.blend" % VERSION))

    # mini bosque de 5 con camino
    reset()
    preparar_escena(res=(1800, 1000))
    col = bpy.data.collections.new("MiniBosque")
    bpy.context.scene.collection.children.link(col)
    pts = [(-8 + 14 * math.sin(i * 0.22), -110 + i * 9, 0) for i in range(26)]
    camino(col, pts)
    cargar_arbol("roble", col, (-48, -40, 0), 1.1)
    cargar_arbol("musgoso", col, (45, -15, 0), 2.0)
    cargar_arbol("torcido", col, (-36, 20, 0), 0.6)
    cargar_arbol("roble", col, (40, 50, 0), 3.5, 0.9)
    cargar_arbol("torcido", col, (-60, 78, 0), 4.0, 1.05)
    figura_roblox(col, pos=(-3, -62, 0), rot=math.radians(10))
    camara((0, 0, 14), (0.25, -1.0, 0.42), dist=150, lente=30)
    render(os.path.join(AQUI, "preview_%s_mini_bosque_5_arboles_camino.png" % VERSION))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "escena_%s_mini_bosque.blend" % VERSION))


if __name__ == "__main__":
    claves = [SOLO] if SOLO else ["roble", "torcido", "musgoso"]
    metricas = {}
    ruta_m = os.path.join(AQUI, "metricas_blender.json")
    if os.path.exists(ruta_m):
        metricas = json.load(open(ruta_m))
    for k in claves:
        metricas[k] = hacer_arbol(k)
        json.dump(metricas, open(ruta_m, "w"), indent=2, ensure_ascii=False)
    if not SIN_ESCENAS and not SOLO:
        escenas()
    metricas["_generado_con"] = "Blender (bpy) " + bpy.app.version_string
    json.dump(metricas, open(ruta_m, "w"), indent=2, ensure_ascii=False)
    print(json.dumps(metricas, indent=1))
