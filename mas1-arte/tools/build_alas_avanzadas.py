"""Alas AVANZADAS (oscuras con turquesa y pinchos) para '+1 de lanzamiento por segundo'. Blender (bpy), Cycles CPU.
Una malla, un material (atlas 512), 5 huesos (Raiz, AlaI_1, AlaI_2, AlaD_1, AlaD_2), clips Deploy / Flap / Glide.
Uso: python3 tools/build_alas_avanzadas.py -> alas-avanzadas/*"""
import bpy, bmesh, math, os, json
import numpy as np
from PIL import Image, ImageFilter
from mathutils import Vector, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "alas-avanzadas")
TEX, PRE, CLI = (os.path.join(OUT, d) for d in ("texturas", "previews", "clips"))
for d in (OUT, TEX, PRE, CLI): os.makedirs(d, exist_ok=True)
ESC = 0.8

def hexrgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)

def atlas():
    """512x512 pintado a mano. u 0-0.7: pluma (azul noche, raya turquesa al centro, borde claro); 0.7-0.8: placa metal; 0.8-1: pinchos (hueso/turquesa)."""
    rng = np.random.default_rng(7); N = 512; img = np.zeros((N, N, 3), np.float32)
    u = np.linspace(0, 1, N)[None, :]; v = np.linspace(0, 1, N)[:, None]
    azul = hexrgb("#1d2347")[None, None, :]; azul2 = hexrgb("#2c3566")[None, None, :]
    img[:] = azul * (1 - v[..., None] * 0.6) + azul2 * (v[..., None] * 0.6)           # mas claro hacia la punta (v=1)
    centro = np.abs(u - 0.35) < 0.05; img[np.broadcast_to(centro, (N, N))] = hexrgb("#1fe5cf")      # raya turquesa
    halo = (np.abs(u - 0.35) >= 0.05) & (np.abs(u - 0.35) < 0.075); img[np.broadcast_to(halo, (N, N))] = hexrgb("#139e91")
    borde = (u < 0.03) | ((u > 0.67) & (u <= 0.7)); img[np.broadcast_to(borde, (N, N))] = hexrgb("#9fb4ff")
    placa = (u > 0.7) & (u <= 0.8); img[np.broadcast_to(placa, (N, N))] = hexrgb("#4a4f66") * (1 - 0.25 * v[..., None] * np.ones((1, N, 1)))[np.broadcast_to(placa, (N, N))] if False else hexrgb("#4a4f66")
    pinchos = u > 0.8; img[np.broadcast_to(pinchos, (N, N))] = hexrgb("#e8f4ff")
    punta = (u > 0.8) & (v > 0.7); img[np.broadcast_to(punta, (N, N))] = hexrgb("#1fe5cf")
    for _ in range(1500):                                                       # pinceladas largas
        x, y = rng.integers(0, 360), rng.integers(0, N - 30); l = rng.integers(20, 60); t = rng.integers(2, 5)
        img[y:y + l, x:x + t] *= rng.uniform(0.85, 1.18)
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.7))
    p = os.path.join(TEX, "alas_avanzadas.png"); im.save(p); return p

class MB:
    def __init__(s): s.v, s.f, s.uv, s.g = [], [], [], []
    def add(s, verts, faces, uvs, grupo):
        o = len(s.v); s.v += verts
        for fa, uu in zip(faces, uvs): s.f.append([i + o for i in fa]); s.uv.append(uu); s.g.append(grupo)
        s.vg = getattr(s, "vg", []); s.vg += [grupo] * len(verts)

def pluma(mb, raiz, ang, L, ancho, grueso, grupo, lado, prof):
    """Pluma de 5 vertices (pentagono extruido): planta en XZ, grosor en Y."""
    d = Vector((lado * math.cos(math.radians(ang)), 0, math.sin(math.radians(ang))))      # direccion de la pluma
    n = Vector((-d.z * lado, 0, d.x * lado)); n.normalize()                                  # perpendicular en XZ (ancho)
    base = Vector(raiz) * ESC; L *= ESC; ancho *= ESC; grueso *= ESC
    pts = [base - n * ancho / 2, base + n * ancho / 2, base + n * ancho / 2 + d * L * 0.78, base + d * L, base - n * ancho / 2 + d * L * 0.78]
    uv2 = [(0.0, 0.0), (0.7, 0.0), (0.7, 0.78), (0.35, 1.0), (0.0, 0.78)]
    y0, y1 = prof * ESC - grueso / 2, prof * ESC + grueso / 2
    a = [(p.x, y1, p.z) for p in pts]; b = [(p.x, y0, p.z) for p in pts]
    verts = a + b
    caras = [[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]] + [[i, (i + 1) % 5, 5 + (i + 1) % 5, 5 + i] for i in range(5)]
    uvs = [uv2, uv2[::-1][::1]] + [[(0.9, 0.0), (0.9, 0.1), (0.95, 0.1), (0.95, 0.0)]] * 5
    uvs[1] = [uv2[4], uv2[3], uv2[2], uv2[1], uv2[0]][::-1][::-1]
    if lado < 0:  # espejo: invertir orientacion de caras para que las normales miren fuera
        caras = [c[::-1] for c in caras]; uvs = [u[::-1] for u in uvs]
    mb.add(verts, caras, uvs, grupo)

def pincho(mb, raiz, ang, L, base, grupo, lado, prof):
    d = Vector((lado * math.cos(math.radians(ang)), 0, math.sin(math.radians(ang)))); n = Vector((-d.z * lado, 0, d.x * lado)); n.normalize()
    r = Vector(raiz) * ESC; L *= ESC; base *= ESC; y = prof * ESC; h = base / 2
    q = [r - n * h + Vector((0, h, 0)), r + n * h + Vector((0, h, 0)), r + n * h - Vector((0, h, 0)), r - n * h - Vector((0, h, 0))]
    tip = r + d * L
    verts = [(p.x, p.y + y, p.z) for p in q] + [(tip.x, y, tip.z)]
    caras = [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [3, 2, 1, 0]]
    uvs = [[(0.85, 0.0), (0.95, 0.0), (0.9, 1.0)]] * 4 + [[(0.85, 0.0), (0.95, 0.0), (0.95, 0.1), (0.85, 0.1)]]
    if lado < 0: caras = [c[::-1] for c in caras]; uvs = [u[::-1] for u in uvs]
    mb.add(verts, caras, uvs, grupo)

def placa(mb, centro, tam, grupo, lado, prof):
    cx, cy, cz = (Vector(centro) * ESC); sx, sy, sz = [t * ESC / 2 for t in tam]
    P = [(cx - sx, cy - sy, cz - sz), (cx + sx, cy - sy, cz - sz), (cx + sx, cy + sy, cz - sz), (cx - sx, cy + sy, cz - sz),
         (cx - sx, cy - sy, cz + sz), (cx + sx, cy - sy, cz + sz), (cx + sx, cy + sy, cz + sz), (cx - sx, cy + sy, cz + sz)]
    caras = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    uvs = [[(0.72, 0.1), (0.78, 0.1), (0.78, 0.9), (0.72, 0.9)]] * 6
    mb.add(P, caras, uvs, grupo)

def construir():
    mb = MB()
    for lado, suf in ((-1, "I"), (1, "D")):
        g1, g2 = f"Ala{suf}_1", f"Ala{suf}_2"
        raiz_in, raiz_out = (-lado * 0.0 + lado * 0.6, 0, 0.3), (lado * 2.6, 0, 0.8)
        # plumas internas (hueso 1) y externas (hueso 2), cada capa un poco mas atras para dar volumen escalonado
        for k, (ang, L) in enumerate(((80, 3.2), (62, 3.9), (44, 4.6))):
            pluma(mb, raiz_in, ang, L, 1.0, 0.38, g1, lado, 0.05 * k)
        for k, (ang, L) in enumerate(((50, 4.4), (32, 5.2), (14, 5.6), (-6, 5.0), (-26, 4.0))):
            pluma(mb, raiz_out, ang, L, 0.95, 0.36, g2, lado, -0.15 - 0.07 * k)
        pincho(mb, raiz_out, 66, 2.4, 0.9, g2, lado, 0.1)                 # espolon del "muneca"
        placa(mb, (lado * 0.9, 0.05, 0.2), (1.2, 0.8, 1.0), g1, lado, 0)  # placa del hombro
        placa(mb, (lado * 2.7, 0.02, 0.8), (0.8, 0.7, 0.8), g2, lado, 0)  # placa de la articulacion
    return mb

def crear_objetos(mb, ruta_tex):
    me = bpy.data.meshes.new("AlasAvanzadas"); me.from_pydata([tuple(v) for v in mb.v], [], mb.f); me.update()
    bm = bmesh.new(); bm.from_mesh(me); uvl = bm.loops.layers.uv.new("UV")
    for f, uu in zip(bm.faces, mb.uv):
        for l, uv in zip(f.loops, uu): l[uvl].uv = uv
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    m = bpy.data.materials.new("AlasAvanzadas"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(ruta_tex); t.image.pack(); nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1.0
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs: b.inputs[k].default_value = 0.0
    m.use_backface_culling = False; me.materials.append(m)
    ob = bpy.data.objects.new("AlasAvanzadas", me); bpy.context.collection.objects.link(ob)
    for g in sorted(set(mb.g)): ob.vertex_groups.new(name=g)
    for i, g in enumerate(mb.vg): ob.vertex_groups[g].add([i], 1.0, "REPLACE")
    # armadura
    arm = bpy.data.armatures.new("Rig"); ao = bpy.data.objects.new("Rig", arm); bpy.context.collection.objects.link(ao)
    bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode="EDIT")
    def hueso(nombre, cabeza, cola, padre=None):
        b = arm.edit_bones.new(nombre); b.head = Vector(cabeza) * ESC; b.tail = Vector(cola) * ESC
        if padre: b.parent = arm.edit_bones[padre]
    hueso("Raiz", (0, 0, 0), (0, 0, 0.8))
    for lado, suf in ((-1, "I"), (1, "D")):
        hueso(f"Ala{suf}_1", (lado * 0.5, 0, 0.2), (lado * 2.6, 0, 0.8), "Raiz")
        hueso(f"Ala{suf}_2", (lado * 2.6, 0, 0.8), (lado * 7.0, 0, 1.6), f"Ala{suf}_1")
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.parent = ao; mod = ob.modifiers.new("Armature", "ARMATURE"); mod.object = ao
    return ob, ao

def clips(ao):
    acciones = {}
    def nueva(nombre, frames, f):
        act = bpy.data.actions.new(nombre); ao.animation_data_create(); ao.animation_data.action = act
        for pb in ao.pose.bones: pb.rotation_mode = "XYZ"
        for fr in frames:
            for pb in ao.pose.bones: pb.rotation_euler = (0, 0, 0)
            f(fr)
            for pb in ao.pose.bones: pb.keyframe_insert("rotation_euler", frame=fr)
        if hasattr(act, "fcurves"):
            for fc in act.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = "BEZIER"
        acciones[nombre] = act
    B = ao.pose.bones
    def giro(pb, grados): pb.rotation_euler = (0, math.radians(grados), 0)
    # Roblox: Y de Blender es el eje delante/atras; girar sobre Y levanta o baja cada ala
    def deploy(fr):
        t = min(1.0, fr / 24.0); e = 1 - (1 - t) ** 3                              # abrir: 1 s a 24 fps, con salida suave
        plegado = 1 - e
        giro(B["AlaI_1"], 80 * plegado); giro(B["AlaD_1"], -80 * plegado); giro(B["AlaI_2"], 70 * plegado); giro(B["AlaD_2"], -70 * plegado)
    def flap(fr):
        t = fr / 18.0 * 2 * math.pi; a1 = 38 * math.sin(t); a2 = 38 * math.sin(t - 0.9) + 8   # el extremo va con retraso
        giro(B["AlaI_1"], -a1); giro(B["AlaD_1"], a1); giro(B["AlaI_2"], -a2); giro(B["AlaD_2"], a2)
    def glide(fr):
        t = fr / 48.0 * 2 * math.pi; a = 4 * math.sin(t); giro(B["AlaI_1"], -a); giro(B["AlaD_1"], a); giro(B["AlaI_2"], -a * 1.4); giro(B["AlaD_2"], a * 1.4)
    nueva("Deploy", [1, 6, 12, 18, 24], deploy); nueva("Flap", [1, 5, 9, 14, 19], flap); nueva("Glide", [1, 13, 25, 37, 49], glide)
    ao.animation_data.action = None
    return acciones

def exportar(ob, ao, acciones):
    base = os.path.join(OUT, "AlasAvanzadas")
    for o in bpy.data.objects: o.select_set(False)
    ob.select_set(True); ao.select_set(True); bpy.context.view_layer.objects.active = ao
    ao.animation_data_create()
    ao.animation_data.action = acciones["Glide"]
    kw = dict(use_selection=True, global_scale=0.01, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", embed_textures=False, path_mode="COPY", add_leaf_bones=False)
    bpy.ops.export_scene.fbx(filepath=base + "_Rig.fbx", bake_anim=False, **kw)
    for nombre, act in acciones.items():
        ao.animation_data.action = act
        bpy.ops.export_scene.fbx(filepath=os.path.join(CLI, f"AlasAvanzadas_{nombre}.fbx"), bake_anim=True, bake_anim_use_all_actions=False,
            bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=0.0, **kw)
    # GLB con todos los clips (pistas NLA)
    for nombre, act in acciones.items():
        tr = ao.animation_data.nla_tracks.new(); tr.name = nombre; tr.strips.new(nombre, 1, act)
    ao.animation_data.action = None
    bpy.ops.export_scene.gltf(filepath=base + ".glb", export_format="GLB", use_selection=True, export_animations=True, export_nla_strips=True)

def figura(coll):
    """Figura de 6 studs de alto (bloques) para escala, de espaldas a la camara; las alas salen del centro de la espalda."""
    mat = bpy.data.materials.new("fig"); mat.diffuse_color = (0.95, 0.62, 0.3, 1)
    def caja(c, s):
        bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.scale = s; o.data.materials.append(mat)
    caja((0, 0.9, -0.2), (2.0, 1.0, 2.0)); caja((0, 0.9, 1.5), (1.4, 1.0, 1.2)); caja((-0.5, 0.9, -2.0), (0.9, 1.0, 2.0)); caja((0.5, 0.9, -2.0), (0.9, 1.0, 2.0))
    caja((-1.5, 0.9, -0.2), (0.9, 0.9, 2.0)); caja((1.5, 0.9, -0.2), (0.9, 0.9, 2.0))

def render(ao, accion, frame, nombre, loc, mirar):
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24
    sc.render.resolution_x, sc.render.resolution_y = 900, 600; sc.view_settings.view_transform = "Standard"
    if not sc.world:
        w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.80, 0.98, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9; sc.world = w
        sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 2.8; so = bpy.data.objects.new("sol", sol); bpy.context.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(-25))
        cam = bpy.data.cameras.new("c"); cam.lens = 34; co = bpy.data.objects.new("c", cam); bpy.context.collection.objects.link(co); sc.camera = co
    co = sc.camera; co.location = loc; co.rotation_euler = (Vector(mirar) - co.location).to_track_quat("-Z", "Y").to_euler()
    ao.animation_data_create(); ao.animation_data.action = accion; sc.frame_set(frame)
    sc.render.filepath = os.path.join(PRE, nombre + ".png"); bpy.ops.render.render(write_still=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
mb = construir(); ruta = atlas(); ob, ao = crear_objetos(mb, ruta); acc = clips(ao)
dg = bpy.context.evaluated_depsgraph_get(); e = ob.evaluated_get(dg).to_mesh(); e.calc_loop_triangles(); tr = len(e.loop_triangles)
figura(bpy.context.collection)
render(ao, acc["Glide"], 1, "Alas-avanzadas-espalda", (0, -16, 3.5), (0, 0, 1.5))
render(ao, acc["Flap"], 5, "Alas-avanzadas-flap-arriba", (9, -15, 5), (0, 0, 2.5))
render(ao, acc["Deploy"], 1, "Alas-avanzadas-plegadas", (9, -15, 5), (0, 0, 2.5))
render(ao, acc["Glide"], 1, "Alas-avanzadas-tres-cuartos", (14, -9, 6), (0, 0, 2.5))
# exportar sin la figura de escala
for o in list(bpy.data.objects):
    if o.name not in (ob.name, ao.name) and o.type == "MESH": bpy.data.objects.remove(o)
exportar(ob, ao, acc)
json.dump({"triangulos": tr, "huesos": [b.name for b in ao.data.bones], "clips": {"Deploy": 1.0, "Flap": 0.75, "Glide": 2.0}, "envergadura_studs": round(2 * 7.0 * ESC + 1.0, 1),
           "exportacion": "FBX global_scale=0.01, -Z delante / Y arriba (1 unidad = 1 stud)"}, open(os.path.join(OUT, "datos.json"), "w"), indent=1, ensure_ascii=False)
print("tris", tr)
