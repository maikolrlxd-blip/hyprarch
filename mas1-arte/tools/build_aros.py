"""Aros de vuelo (3 niveles) para '+1 de lanzamiento por segundo': facetados, colores vivos, pintados a mano. Blender (bpy), Cycles CPU.
Uso: python3 tools/build_aros.py   -> aros/*.glb, aros/*.fbx, aros/texturas/*.png, aros/previews/*.png, aros/datos.json"""
import bpy, bmesh, math, os, json, random
import numpy as np
from PIL import Image, ImageFilter
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "aros")
TEX, PRE = os.path.join(OUT, "texturas"), os.path.join(OUT, "previews")
for d in (OUT, TEX, PRE): os.makedirs(d, exist_ok=True)

NIVELES = {  # nombre: (color A, color B, borde oscuro)
    "AroBronce": ("#ff7a1a", "#ffb347", "#5a2208"),
    "AroPlata": ("#2f9be8", "#d8f0ff", "#12385a"),
    "AroOro": ("#ffb000", "#fff06a", "#6a4300"),
}
def hexrgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)

def textura(nombre, a, b, borde, seed):
    rng = np.random.default_rng(seed); W, H, franjas = 512, 256, 8
    x = np.arange(W)[None, :] / W * franjas
    mezcla = ((np.floor(x) % 2) * np.ones((H, 1))).astype(np.float32)
    sep = (np.abs((x % 1.0) - 0.0) < 0.035) | (np.abs((x % 1.0) - 1.0) < 0.035)  # raya oscura entre franjas
    img = hexrgb(a)[None, None, :] * (1 - mezcla[..., None]) + hexrgb(b)[None, None, :] * mezcla[..., None]
    # degradado a lo largo del tubo (arriba claro, abajo oscuro) y pinceladas con direccion
    v = (np.arange(H)[:, None] / H); img *= (1.12 - 0.35 * v)[..., None]
    for _ in range(900):
        px, py = rng.integers(0, W), rng.integers(0, H); l = rng.integers(20, 70); t = rng.integers(2, 6)
        col = img[py % H, px % W] * rng.uniform(0.9, 1.1)
        img[py:py + t, px:px + l] = np.clip(0.6 * img[py:py + t, px:px + l] + 0.4 * col[None, None, :] if img[py:py + t, px:px + l].size else img[py:py + t, px:px + l], 0, 255)
    img[np.broadcast_to(sep, (H, W))] = hexrgb(borde)
    img[:12] = hexrgb(borde); img[-12:] = hexrgb(borde)           # contorno oscuro grueso arriba y abajo del mapa = bordes del tubo
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))
    ruta = os.path.join(TEX, nombre + ".png"); im.save(ruta); return ruta

def torus(nombre, R=5.0, r=0.65, seg=16, lados=6):
    me = bpy.data.meshes.new(nombre); verts, faces, uvs = [], [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg; c, s = math.cos(a), math.sin(a)
        for j in range(lados):
            b = 2 * math.pi * j / lados + math.pi / lados
            rr = R + r * math.cos(b); verts.append((rr * c, 0.0, rr * s + 0.0)); verts[-1] = (rr * c, r * math.sin(b), rr * s)
    for i in range(seg):
        for j in range(lados):
            a, b = i * lados + j, i * lados + (j + 1) % lados
            c2, d = ((i + 1) % seg) * lados + (j + 1) % lados, ((i + 1) % seg) * lados + j
            faces.append((a, b, c2, d))
    me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.new("UV")
    for f in bm.faces:
        for l in f.loops:
            i, j = divmod(l.vert.index, lados)
            # u: posicion a lo largo del aro (cada cara lleva una franja), v: alrededor del tubo
            cara_i = min(v.index // lados for v in f.verts); wrap = (max(v.index // lados for v in f.verts) - cara_i) > 1
            ii = i + (seg if (wrap and i == 0) else 0)
            jj = j + (lados if (min(v.index % lados for v in f.verts) == 0 and max(v.index % lados for v in f.verts) == lados - 1 and j == 0) else 0)
            l[uv].uv = (ii / seg, jj / lados)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    return bpy.data.objects.new(nombre, me)

def material(nombre, ruta):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(ruta); t.image.pack(); t.extension = "REPEAT"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 1.0
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs: b.inputs[k].default_value = 0.0
    return m

def tris(ob):
    dg = bpy.context.evaluated_depsgraph_get(); e = ob.evaluated_get(dg).to_mesh(); e.calc_loop_triangles(); return len(e.loop_triangles)

def render(ob, nombre, ruta):
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24
    sc.render.resolution_x, sc.render.resolution_y = 900, 600; sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.80, 0.98, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9; sc.world = w
    sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 2.6; so = bpy.data.objects.new("sol", sol); bpy.context.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(30))
    cam = bpy.data.cameras.new("c"); cam.lens = 38; co = bpy.data.objects.new("c", cam); bpy.context.collection.objects.link(co); sc.camera = co
    co.location = (4, -20, 7.5); co.rotation_euler = (Vector((2.5, 0, 5.2)) - co.location).to_track_quat("-Z", "Y").to_euler()
    # figura de 6 studs (referencia de escala)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(9.5, 0, 3)); f = bpy.context.object; f.scale = (2, 1, 6); f.name = "Figura6"
    mm = bpy.data.materials.new("fig"); mm.diffuse_color = (0.9, 0.5, 0.2, 1); f.data.materials.append(mm)
    sc.render.filepath = ruta; bpy.ops.render.render(write_still=True)

def exportar(ob, base):
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=base + ".glb", export_format="GLB", use_selection=True)
    bpy.ops.export_scene.fbx(filepath=base + ".fbx", use_selection=True, global_scale=0.01, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", embed_textures=False, path_mode="COPY")

datos = {}
for k, (nombre, (a, b, borde)) in enumerate(NIVELES.items()):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ruta = textura(nombre, a, b, borde, 100 + k)
    ob = torus(nombre); bpy.context.collection.objects.link(ob); ob.data.materials.append(material(nombre, ruta))
    ob.location = (0, 0, 5.5)   # el aro de pie, centro a 5,5 studs
    datos[nombre] = {"triangulos": tris(ob), "diametro_studs": 2 * (5.0 + 0.65), "grosor_studs": 1.3}
    exportar(ob, os.path.join(OUT, nombre)); render(ob, nombre, os.path.join(PRE, nombre + ".png"))
json.dump(datos, open(os.path.join(OUT, "datos.json"), "w"), indent=1, ensure_ascii=False); print(datos)
