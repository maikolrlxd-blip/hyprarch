"""Kit v03 playa/desierto: botes, cactus, palmera, piezas de playa. Blender (bpy) -> GLB con animaciones.
Uso: python3 kit_v03.py   (genera texturas, modelos/*.glb, renders/*.png)"""
import math, os, sys, random
import bpy, bmesh
from mathutils import Vector, Euler
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pintura
TEX, MOD, REN = (os.path.join(HERE, d) for d in ("texturas", "modelos", "renders"))
for d in (TEX, MOD, REN): os.makedirs(d, exist_ok=True)

TEXTURAS = {
 "arena":   (["#e8cf95", "#dcbf80", "#c9a96b"], dict(semilla=11, largo=(10, 30), ancho=(2, 5), variacion=0.08, motas=("#b99a5c", 500, 2))),
 "madera":  (["#9a6a3c", "#7e5430", "#684425"], dict(semilla=12, angulo=0, largo=(60, 160), ancho=(2, 5), variacion=0.10, lineas=("#4a2c14", 48, 2, False))),
 "casco":   (["#2f7fa8", "#256a92", "#1d5578"], dict(semilla=13, angulo=0, largo=(60, 140), ancho=(3, 7), variacion=0.10, bandas=[(0.0, 0.08, "#f2e9d0")])),
 "casco2":  (["#c8553d", "#b04630", "#8f3826"], dict(semilla=14, angulo=0, largo=(60, 140), ancho=(3, 7), variacion=0.10, bandas=[(0.0, 0.08, "#f2e9d0")])),
 "vela":    (["#f4ecd6", "#eadfc2", "#dccfae"], dict(semilla=15, angulo=70, largo=(40, 100), ancho=(3, 7), variacion=0.07, lineas=("#c9bb98", 64, 2, False))),
 "metal":   (["#8c9399", "#737a80", "#5d6368"], dict(semilla=16, largo=(20, 60), ancho=(2, 4), variacion=0.07)),
 "cactus":  (["#6fae4e", "#58963f", "#437a30"], dict(semilla=17, angulo=90, largo=(40, 110), ancho=(3, 7), variacion=0.10, lineas=("#2f5a22", 40, 3, True))),
 "palma_t": (["#9c6e43", "#845a35", "#6b4528"], dict(semilla=18, angulo=90, largo=(30, 90), ancho=(3, 7), variacion=0.10, lineas=("#4a2e18", 36, 3, False))),
 "fronda":  (["#5fae45", "#479637", "#2f7a2c"], dict(semilla=19, angulo=60, largo=(30, 80), ancho=(3, 6), variacion=0.12, lineas=("#2a6624", 56, 3, True))),
 "coco":    (["#7a5230", "#5e3d22", "#47301a"], dict(semilla=20, largo=(20, 50), ancho=(3, 6), variacion=0.08)),
 "concha":  (["#f6dcc8", "#ecc3a8", "#d9a98c"], dict(semilla=21, angulo=90, largo=(20, 50), ancho=(2, 4), variacion=0.08, lineas=("#c28f72", 28, 2, True))),
 "estrella":(["#f08a4b", "#e06f35", "#c05526"], dict(semilla=22, largo=(15, 40), ancho=(2, 4), variacion=0.08, motas=("#f6c08a", 260, 2))),
 "flor":    (["#f2c94c", "#e9a93a", "#d98a2c"], dict(semilla=23, largo=(15, 40), ancho=(2, 4), variacion=0.08)),
}
for n, (cols, kw) in TEXTURAS.items():
    p = os.path.join(TEX, n + ".png")
    if not os.path.exists(p): pintura.pintar(p, cols, **kw)

# ---------- utilidades ----------
def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)

_mats = {}
def mat(n, doble=False):
    if n in _mats and _mats[n].name in bpy.data.materials: return _mats[n]
    m = bpy.data.materials.new(n); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(TEX, n + ".png")); t.image.pack()
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1.0
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs: b.inputs[k].default_value = 0.0
    if doble: m.use_backface_culling = False
    _mats[n] = m; return m

class MB:
    """Constructor de malla facetada: listas de vertices y caras (cada cara con material)."""
    def __init__(s): s.v = []; s.f = []; s.m = []
    def add(s, verts, faces, mt):
        o = len(s.v); s.v += [tuple(x) for x in verts]
        for f in faces: s.f.append([i + o for i in f]); s.m.append(mt)
    def lathe(s, perfil, lados, mt, jit=0.0, rng=None, rot=0.0):
        """perfil: [(radio, y)] de abajo a arriba. Revolucion con lados facetados."""
        rng = rng or random.Random(1); vs = []; 
        for r, y in perfil:
            for i in range(lados):
                a = rot + 2 * math.pi * i / lados
                rr = r * (1 + rng.uniform(-jit, jit))
                vs.append((rr * math.cos(a), rr * math.sin(a), y))
        fs = []
        for k in range(len(perfil) - 1):
            for i in range(lados):
                a, b = k * lados + i, k * lados + (i + 1) % lados
                fs.append([a, b, b + lados, a + lados])
        fs.append(list(reversed(range(lados))))
        s.add(vs, fs, mt)
    def box(s, c, d, mt, rot=0.0):
        cx, cy, cz = c; dx, dy, dz = d[0] / 2, d[1] / 2, d[2] / 2
        P = [(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),(-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]
        cr, sr = math.cos(rot), math.sin(rot)
        P = [(cx + x * cr - y * sr, cy + x * sr + y * cr, cz + z) for x, y, z in P]
        s.add(P, [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]], mt)
    def loft(s, secciones, mt, cerrar=True):
        """secciones: lista de listas de puntos (mismo numero por seccion)."""
        n = len(secciones[0]); vs = [p for sec in secciones for p in sec]; fs = []
        for k in range(len(secciones) - 1):
            for i in range(n - 1):
                a = k * n + i; fs.append([a, a + 1, a + n + 1, a + n])
        if cerrar:
            fs.append(list(range(n))[::-1]); fs.append([len(vs) - n + i for i in range(n)])
        s.add(vs, fs, mt)
    def blade(s, base, dir, largo, ancho, mt, curva=0.0, seg=4):
        """hoja plana con punta, doble cara, curvada hacia abajo."""
        base = Vector(base); d = Vector(dir).normalized(); side = d.cross(Vector((0, 0, 1)))
        if side.length < 1e-4: side = Vector((1, 0, 0))
        side.normalize(); vs = []; 
        for i in range(seg + 1):
            t = i / seg; w = ancho * (1 - t) ** 0.7 * (0.6 + 0.4 * math.sin(math.pi * min(1, t * 1.3)))
            p = base + d * (largo * t) + Vector((0, 0, -curva * t * t * largo))
            vs += [p - side * w / 2, p + side * w / 2]
        fs = []
        for i in range(seg):
            a = 2 * i; fs.append([a, a + 1, a + 3, a + 2]); fs.append([a + 2, a + 3, a + 1, a])
        s.add(vs, fs, mt)
    def build(s, nombre, mats=None):
        mats = list(dict.fromkeys(s.m))
        me = bpy.data.meshes.new(nombre); me.from_pydata(s.v, [], s.f)
        for m in mats: me.materials.append(mat(m, True))
        idx = {m: i for i, m in enumerate(mats)}
        me.update()
        for p, mt in zip(me.polygons, s.m): p.material_index = idx[mt]; p.use_smooth = False
        # UV por proyeccion en caja
        bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.new("UV")
        for f in bm.faces:
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for l in f.loops:
                c = l.vert.co; a, b = [(1, 2), (0, 2), (0, 1)][ax]
                l[uv].uv = (c[a] * 0.9, c[b] * 0.9)
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(nombre, me); bpy.context.collection.objects.link(ob); return ob

def vacio(nombre, loc=(0,0,0)):
    e = bpy.data.objects.new(nombre, None); bpy.context.collection.objects.link(e); e.location = loc; return e

def clip(ob, nombre, frames, curvas, bucle=True):
    """curvas: {prop_index: [(frame, valor)]} prop = ('rotation_euler'|'location', idx). Crea Action y tira NLA."""
    ob.animation_data_create(); act = bpy.data.actions.new(nombre)
    ob.animation_data.action = act
    for (prop, i), kfs in curvas.items():
        for fr, v in kfs:
            getattr(ob, prop)[i] = v; ob.keyframe_insert(prop, index=i, frame=fr)
    if hasattr(act, "fcurves"):
        for fc in act.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "BEZIER"
            if bucle: fc.modifiers.new("CYCLES")
    tr = ob.animation_data.nla_tracks.new(); tr.name = nombre
    st = tr.strips.new(nombre, 1, act); ob.animation_data.action = None

def exportar(nombre):
    ruta = os.path.join(MOD, nombre + ".glb")
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", export_animations=True,
        export_nla_strips=True, export_apply=False, export_yup=True, use_selection=False)
    return ruta

def tris():
    dg = bpy.context.evaluated_depsgraph_get(); t = 0
    for o in bpy.data.objects:
        if o.type == "MESH":
            e = o.evaluated_get(dg).to_mesh(); e.calc_loop_triangles(); t += len(e.loop_triangles)
    return t

def ola(ob, amp, per, fase=0.0, n=48):
    """cabeceo + balanceo + subida suave, bucle perfecto"""
    z0 = ob.location.z
    kz = [(1 + int(i * (n) / 8), z0 + amp * math.sin(2 * math.pi * i / 8 + fase)) for i in range(9)]
    kx = [(1 + int(i * n / 8), 0.035 * math.sin(2 * math.pi * i / 8 + fase + 1.2)) for i in range(9)]
    ky = [(1 + int(i * n / 8), 0.05 * math.sin(2 * math.pi * i / 8 + fase)) for i in range(9)]
    clip(ob, "Flotar", n, {("location", 2): kz, ("rotation_euler", 0): kx, ("rotation_euler", 1): ky})
    bpy.context.scene.frame_end = n + 1

# ---------- modelos ----------
R = random.Random(7)

def casco(b, largo, ancho, alto, tex, quilla=0.25):
    """casco por secciones, 5 puntos por seccion (quilla, 2 pantoques, 2 bordas)."""
    N = 7; sec = []
    for k in range(N):
        t = k / (N - 1); x = -largo / 2 + largo * t
        w = ancho / 2 * (math.sin(math.pi * (0.1 + 0.85 * t)) ** 0.6) * (1 if t < 0.85 else 0.55 + (1 - t) * 3)
        w = max(w, 0.05); h = alto * (1 + 0.4 * t ** 2)
        sec.append([(x, 0, quilla * (1 - t * 0.2)), (x, -w * 0.75, h * 0.35), (x, -w, h), (x, w, h), (x, w * 0.75, h * 0.35), (x, 0, quilla * (1 - t * 0.2))])
    # secciones cerradas como lazo: ultimo punto repite el primero
    sec = [s for s in sec]
    b.loft(sec, tex, cerrar=False)
    # cubierta interior
    b.loft([[ (x, -w * 0.9, h * 0.97), (x, w * 0.9, h * 0.97)] for (x, _, _), (_, w, h) in
            [ (s[2], (0, abs(s[2][1]), s[2][2])) for s in sec]][:], "madera", cerrar=False)

def bote_remos():
    b = MB(); casco(b, 4.2, 1.6, 0.7, "madera", quilla=0.05)
    for x in (-0.8, 0.3, 1.2): b.box((x, 0, 0.55), (0.35, 1.4, 0.07), "madera")
    b.box((1.9, 0, 0.9), (0.2, 0.2, 0.4), "metal")     # farol
    root = vacio("BoteRemos"); ob = b.build("BoteRemos_casco", ["madera"]); ob.parent = root
    r = MB(); r.box((0, 0, 0), (1.9, 0.08, 0.08), "madera"); r.box((0.95, 0, 0), (0.5, 0.3, 0.04), "madera")
    for sg in (-1, 1):
        o = r.build("Remo" + ("I" if sg < 0 else "D"), ["madera"]) if False else None
    return root

def lancha():
    b = MB(); casco(b, 6.0, 2.2, 0.9, "casco", quilla=0.05)
    b.box((0.4, 0, 1.4), (1.8, 1.6, 1.0), "casco2")          # cabina
    b.box((0.4, 0, 2.0), (2.1, 1.9, 0.12), "metal")          # techo
    b.box((-2.6, 0, 0.9), (0.5, 0.6, 0.7), "metal")          # motor
    b.box((-2.8, 0, 0.25), (0.2, 0.2, 0.8), "metal")
    root = vacio("Lancha"); ob = b.build("Lancha_casco", ["casco", "casco2", "metal", "madera"]); ob.parent = root
    return root

def velero():
    b = MB(); casco(b, 5.2, 1.9, 0.8, "casco2", quilla=0.05)
    b.box((0, 0, 3.0), (0.14, 0.14, 5.6), "madera")          # mastil
    b.add([(0.1, 0, 5.4), (0.1, 0, 1.2), (2.2, 0, 1.2)], [[0, 1, 2], [2, 1, 0]], "vela")
    b.add([(-0.1, 0, 5.2), (-0.1, 0, 1.2), (-1.8, 0, 1.2)], [[0, 2, 1], [1, 2, 0]], "vela")
    b.box((0.5, 0, 1.15), (2.6, 0.1, 0.1), "madera")
    root = vacio("Velero"); ob = b.build("Velero_casco", ["casco2", "madera", "vela"]); ob.parent = root
    return root

def saguaro(seed=1):
    r = random.Random(seed); b = MB()
    b.lathe([(0.45, 0), (0.62, 0.4), (0.55, 2.5), (0.5, 4.2), (0.3, 4.8), (0.0, 4.9)], 8, "cactus", 0.04, r)
    # costillas: ya vienen del facetado a 8 lados
    def tubo(pts, rad, mt):
        sec = []
        for (x, y, z), rr in zip(pts, rad):
            sec.append([(x, y + rr * math.cos(t), z + rr * math.sin(t)) if False else (x + rr * math.cos(t) * 0.0, y + rr * math.cos(t), z + rr * math.sin(t)) for t in [2 * math.pi * i / 7 for i in range(7)] + [0]])
        b.loft(sec, mt, cerrar=False)
    for sg, h in ((-1, 2.0), (1, 2.9)):
        # codo horizontal (a lo largo de X) y luego sube; se hace con dos tubos facetados
        sec = []
        for k in range(4):
            x = sg * (0.4 + 0.35 * k); sec.append([(x, 0.22 * math.cos(t), h + 0.22 * math.sin(t)) for t in [2 * math.pi * i / 7 for i in range(7)] + [0]])
        b.loft(sec, "cactus", cerrar=False)
        xs = sg * 1.45; sec = []
        for k in range(5):
            z = h + 0.35 * k * 1.0; rr = 0.24 if k < 4 else 0.1
            sec.append([(xs + rr * math.cos(t), rr * math.sin(t), z) for t in [2 * math.pi * i / 7 for i in range(7)] + [0]])
        b.loft(sec, "cactus", cerrar=False)
        b.lathe([(0.0, 0.0)], 3, "cactus") if False else None
    root = vacio("Saguaro%d" % seed); ob = b.build("Saguaro_%d_cuerpo" % seed, ["cactus"]); ob.parent = root
    return root

def cactus_barril():
    r = random.Random(3); b = MB()
    b.lathe([(0.3, 0), (0.85, 0.3), (0.95, 0.9), (0.7, 1.5), (0.35, 1.7), (0, 1.75)], 10, "cactus", 0.03, r)
    b.lathe([(0.12, 1.7), (0.16, 1.9), (0, 2.0)], 5, "flor")
    root = vacio("CactusBarril"); ob = b.build("CactusBarril_cuerpo", ["cactus", "flor"]); ob.parent = root; return root

def nopal():
    b = MB(); r = random.Random(5)
    def pala(c, rz, w, h):
        a = math.radians(rz); ca, sa = math.cos(a), math.sin(a)
        pts = []
        for k in range(8):
            t = 2 * math.pi * k / 8; x = w * math.cos(t) * 0.5; z = h * (0.5 + 0.5 * math.sin(t))
            pts.append((c[0] + x * ca, c[1] + x * sa, c[2] + z))
        for t in (0.09, -0.09):
            pass
        n = len(pts); fr = [(x - 0.09 * sa, y + 0.09 * ca, z) for x, y, z in pts]; bk = [(x + 0.09 * sa, y - 0.09 * ca, z) for x, y, z in pts]
        b.add(fr + bk, [list(range(n)), [2 * n - 1 - i for i in range(n)]] +
              [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)], "cactus")
    pala((0, 0, 0), 0, 1.5, 1.7); pala((0.4, 0, 1.4), 25, 1.2, 1.4); pala((-0.5, 0.1, 1.2), -20, 1.1, 1.3)
    root = vacio("Nopal"); ob = b.build("Nopal_cuerpo", ["cactus"]); ob.parent = root; return root

def palmera():
    r = random.Random(9); b = MB(); alto = 7.0
    # tronco curvo con anillos
    perfil_segs = 9; sec = []
    for k in range(perfil_segs + 1):
        t = k / perfil_segs; cx = 0.9 * t * t * 1.2; z = alto * t; rad = 0.42 - 0.18 * t + (0.08 if k % 2 == 0 else 0)
        sec.append([(cx + rad * math.cos(a), rad * math.sin(a), z) for a in [2 * math.pi * i / 7 for i in range(7)] + [0]])
    b.loft(sec, "palma_t", cerrar=False)
    top = (0.9 * 1.2, 0, alto)
    for i in range(9):
        a = 2 * math.pi * i / 9 + r.uniform(-.2, .2)
        b.blade((top[0], top[1], top[2] - 0.1), (math.cos(a), math.sin(a), 0.55), 3.8 + r.uniform(0, .6), 1.25, "fronda", curva=0.9, seg=5)
    for i in range(3):
        a = 2.1 * i
        b.lathe([(0.0, 0), (0.3, 0.2), (0.28, 0.5), (0.0, 0.62)], 6, "coco", 0.03, r)
    root = vacio("Palmera"); ob = b.build("Palmera_cuerpo", ["palma_t", "fronda", "coco"]); ob.parent = root; return root

def piezas_playa():
    out = []
    b = MB(); r = random.Random(11)
    # concha de abanico
    for k in range(9):
        a0 = -0.9 + 1.8 * k / 9; a1 = -0.9 + 1.8 * (k + 1) / 9
        b.add([(0, 0, 0), (0.8 * math.sin(a0), 0.8 * math.cos(a0), 0.25), (0.8 * math.sin(a1), 0.8 * math.cos(a1), 0.25 + (0.04 if k % 2 else 0))], [[0, 1, 2], [2, 1, 0]], "concha")
    o = b.build("Concha", ["concha"]); rt = vacio("Concha"); o.parent = rt; out.append(rt)
    b = MB()
    b.add([(0, 0, 0.1)] + [((0.25 if i % 2 else 0.9) * math.cos(2 * math.pi * i / 10), (0.25 if i % 2 else 0.9) * math.sin(2 * math.pi * i / 10), 0.0) for i in range(10)],
          [[0, 1 + i, 1 + (i + 1) % 10] for i in range(10)] + [[1 + (i + 1) % 10, 1 + i, 0] for i in range(10)], "estrella")
    o = b.build("EstrellaMar", ["estrella"]); rt = vacio("EstrellaMar"); o.parent = rt; out.append(rt)
    b = MB(); b.lathe([(0.45, 0), (0.5, 1.5), (0.4, 3.0), (0.3, 3.4)], 7, "palma_t", 0.08, R, 0)
    b.lathe([(0.4, 0), (0.1, 0.0)], 7, "palma_t") if False else None
    o = b.build("TroncoVarado", ["palma_t"]); o.rotation_euler = (0, math.pi / 2, 0.3); rt = vacio("TroncoVarado"); o.parent = rt; out.append(rt)
    b = MB()
    b.box((0, 0, 0.55), (4.0, 1.2, 0.12), "madera")
    for x in (-1.6, -0.4, 0.8, 1.7):
        b.box((x, -0.55, -0.2), (0.22, 0.22, 1.5), "madera"); b.box((x, 0.55, -0.2), (0.22, 0.22, 1.5), "madera")
    for x in [-1.9 + 0.38 * i for i in range(11)]: b.box((x, 0, 0.62), (0.3, 1.25, 0.05), "madera")
    o = b.build("Muelle", ["madera"]); rt = vacio("Muelle"); o.parent = rt; out.append(rt)
    return out

def mecer(ob, amp=0.04, n=72):
    ks = lambda f: [(1 + int(i * n / 4), f * math.sin(2 * math.pi * i / 4)) for i in range(5)]
    clip(ob, "Mecer", n, {("rotation_euler", 0): ks(amp), ("rotation_euler", 1): ks(amp * 0.7)})
    bpy.context.scene.frame_end = n + 1

def atracar(ob, n=90):
    """llega desde -X (lejos) y se frena en 0 con un cabeceo; luego queda."""
    x0 = ob.location.x
    clip(ob, "Atracar", n, {("location", 0): [(1, x0 - 14), (60, x0 + 0.4), (n, x0)],
                            ("rotation_euler", 1): [(1, 0.0), (45, 0.07), (70, -0.04), (n, 0.0)]}, bucle=False)

# ---------- ensamblado y salida ----------
def escena_luz():
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24
    sc.render.resolution_x = 900; sc.render.resolution_y = 600
    w = bpy.data.worlds.new("w"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.78, 0.88, 0.95, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    sc.world = w
    s = bpy.data.lights.new("sol", "SUN"); s.energy = 3.5; o = bpy.data.objects.new("sol", s); bpy.context.collection.objects.link(o); o.rotation_euler = (math.radians(50), 0, math.radians(35))
    cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam); bpy.context.collection.objects.link(co); sc.camera = co
    return co

def figura6():
    b = MB()  # figura de referencia: 6 studs
    b.lathe([(1.2, 0), (1.6, 1.5), (1.5, 3.2), (1.0, 4.5)], 8, "casco2"); b.lathe([(0.9, 4.5), (1.0, 5.2), (0.0, 6.0)], 8, "flor")
    ob = b.build("Figura6", ["casco2", "flor"]); return ob

def render_hoja(nombre, objs, dist=14, alt=7):
    cam = bpy.context.scene.camera
    bpy.context.scene.frame_set(60)
    cam.location = (dist, -dist, alt); d = Vector((0, 0, 1.5)) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.filepath = os.path.join(REN, nombre + ".png"); bpy.ops.render.render(write_still=True)

def main():
    informe = {}
    lote = {
        "bote_remos": (bote_remos, "Flotar"), "lancha": (lancha, "Flotar"), "velero": (velero, "Flotar"),
        "saguaro1": (lambda: saguaro(1), "Mecer"), "saguaro2": (lambda: saguaro(2), "Mecer"),
        "cactus_barril": (cactus_barril, "Mecer"), "nopal": (nopal, "Mecer"), "palmera": (palmera, "Mecer"),
    }
    for nombre, (fn, anim) in lote.items():
        limpiar(); _mats.clear()
        root = fn()
        if anim == "Flotar":
            ola(root, 0.12, 48); atracar(root)
        else:
            mecer(root, 0.03 if "palm" not in nombre else 0.025)
        informe[nombre] = tris(); exportar(nombre)
        co = escena_luz(); f = figura6()
        f.location = (-4.5 if 'palm' not in nombre else -5.5, 1.5, 0); 
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.02))
        pl = bpy.context.object; pl.data.materials.append(mat("arena"))
        render_hoja(nombre, [root], dist=12 if "palm" not in nombre else 17, alt=6)
    piezas = None
    limpiar(); _mats.clear(); piezas = piezas_playa()
    for i, p in enumerate(piezas): p.location = (i * 5 - 7, 0, 0)
    informe["piezas_playa"] = tris(); exportar("piezas_playa")
    co = escena_luz(); bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.02)); bpy.context.object.data.materials.append(mat("arena"))
    render_hoja("piezas_playa", piezas, dist=14, alt=6)
    print("TRIANGULOS", informe)

main()
