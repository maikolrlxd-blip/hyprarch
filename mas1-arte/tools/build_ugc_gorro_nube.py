# Accesorio UGC de prueba para el Marketplace de Roblox: «Gorro Nubecita», la mascota nube amable del juego sentada en la cabeza
# como un gorro (Maikol, 30/10: «crea un accesorio nuevo, lo que más creas que va a vender»; lo de cabeza y lo kawaii es lo que más
# se vende). Sale de mascotas-enemigos-v01/nube (malla ya validada): se fija en la pose neutra (sin huesos: los accesorios
# rígidos no se animan), se escala a ANCHO studs, se apoya con la base en z = 0 (ahí va la HatAttachment) y se exporta en FBX con
# su textura. Requisitos Roblox (Hat, cuerpo Classic): caja 3 × 4 × 3, una malla cerrada, ≤ 4.000 triángulos, material Plastic.
# Tamaño (Maikol: «piensa en qué tan bien se ve el tamaño»): la v1 medía 2,8 de ancho = 2,3 cabezas, un paraguas que tapaba la
# foto de perfil. Se compara 1,6 / 2,0 / 2,4 / 2,8 sobre un avatar R15 de bloques (cabeza 1,2, torso 2 × 2 × 1, brazos y
# piernas 1 × 2 × 1) y se exporta GORRO_ANCHO: 1,6, el que eligió Maikol («el de 1,6 es el que mejor se ve»; así cabe también en
# las cajas de los cuerpos Rthro: Normal 1,87 y Slender 1,78). NO se ha subido ni publicado nada.
# blender -b --factory-startup --python-exit-code 1 -P build_ugc_gorro_nube.py   ->   mas1-arte/ugc-gorro-nube-v01/
import sys, os, shutil, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *
import bmesh
import numpy as np

ARTE = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ARTE, 'ugc-gorro-nube-v01')
os.makedirs(OUT, exist_ok=True)
ANCHO = float(os.environ.get('GORRO_ANCHO', '1.6'))
COMPARAR = (1.6, 2.0, 2.4, 2.8)
ACLARAR = float(os.environ.get('GORRO_ACLARAR', '0.4'))   # cuánto se acercan a blanco los tonos de nube de la textura
HUNDIR = 0.1                                 # se hunde un poco en la cabeza (que es redondeada): sin rendija entre nube y cabeza
CABEZA_TOP = 5.2                              # piernas 2 + torso 2 + cabeza 1,2
A.clean_scene()
CM, CC, CV = A.collection('UGC'), A.collection('Camaras'), A.collection('Avatar')
with bpy.data.libraries.load(os.path.join(ARTE, 'mascotas-enemigos-v01', 'nube', 'MascotaNube.blend'), link=False) as (src, dst):
    dst.objects = ['MascotaNube', 'MascotaNube_Rig']
ob = next(o for o in dst.objects if o.type == 'MESH')
rig = next(o for o in dst.objects if o.type == 'ARMATURE')
for o in (ob, rig):
    CM.objects.link(o)
rig.animation_data_clear()
for pb in rig.pose.bones:                      # pose neutra
    pb.location, pb.rotation_quaternion, pb.rotation_euler = (0, 0, 0), (1, 0, 0, 0), (0, 0, 0)
bpy.context.view_layer.update()
A.select_only([ob])
for m in list(ob.modifiers):                   # la malla se queda fija en la pose neutra, sin huesos
    if m.type == 'ARMATURE':
        bpy.ops.object.modifier_apply(modifier=m.name)
mw = ob.matrix_world.copy()
ob.parent = None
ob.matrix_world = mw
bpy.data.objects.remove(rig)
ob.vertex_groups.clear()
ob.data.transform(ob.matrix_world)
ob.matrix_world = Matrix.Identity(4)
co = [v.co.copy() for v in ob.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)])
mx = Vector([max(c[i] for c in co) for i in range(3)])
k = ANCHO / (mx.x - mn.x)
centro = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
ob.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-centro))   # base en z = 0, centrado: ahí la HatAttachment
ob.name = ob.data.name = 'GorroNubecita'
co = [v.co.copy() for v in ob.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)])
mx = Vector([max(c[i] for c in co) for i in range(3)])
tam = [round(mx[i] - mn[i], 3) for i in range(3)]   # x ancho, y fondo, z alto (Blender)
tris = A.tris([ob])


def revisar(o):
    """Aristas que no tienen exactamente 2 caras (malla abierta o no-manifold) e islas sueltas: Roblox pide una malla cerrada."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    abiertas = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    vistos, islas = set(), 0
    for v in bm.verts:
        if v.index in vistos:
            continue
        islas += 1
        pila = [v]
        while pila:
            w = pila.pop()
            if w.index not in vistos:
                vistos.add(w.index)
                pila.extend(e.other_vert(w) for e in w.link_edges)
    bm.free()
    return abiertas, islas


abiertas, islas = revisar(ob)


def separar_contactos(me):
    """Aristas con 4 caras = dos vóxeles que se tocan solo por una arista (malla cerrada pero no-manifold). En un extremo de la
    arista, las caras de uno de los dos sólidos pasan a un vértice nuevo: la arista queda en dos, cada una con sus 2 caras."""
    bm = bmesh.new()
    bm.from_mesh(me)
    capas = list(bm.loops.layers.uv.values()) + list(bm.loops.layers.color.values()) + list(bm.loops.layers.float_color.values())
    separadas = 0
    for _ in range(20):
        malas = [e for e in bm.edges if len(e.link_faces) == 4]
        if not malas:
            break
        e, hecho = malas[0], False
        for v in e.verts:
            f0 = e.link_faces[0]
            fan, pila = {f0}, [f0]             # caras del sólido de f0 alrededor de v (unidas por aristas buenas que tocan v)
            while pila:
                for ed in pila.pop().edges:
                    if v in ed.verts and len(ed.link_faces) == 2:
                        for g in ed.link_faces:
                            if g not in fan:
                                fan.add(g)
                                pila.append(g)
            if len(fan) == len(v.link_faces):  # los dos sólidos siguen unidos por otro lado: aquí no se puede
                continue
            nv = bm.verts.new(v.co)
            for f in list(fan):
                vs = [nv if l.vert is v else l.vert for l in f.loops]
                datos = [[l[c] if not hasattr(l[c], 'uv') else l[c].uv.copy() for c in capas] for l in f.loops]
                datos = [[x.copy() if hasattr(x, 'copy') else x for x in d] for d in datos]
                g = bm.faces.new(vs, f)            # f de ejemplo: material y suavizado
                for l, d in zip(g.loops, datos):
                    for c, x in zip(capas, d):
                        if hasattr(l[c], 'uv'):
                            l[c].uv = x
                        else:
                            l[c] = x
                bm.faces.remove(f)
            separadas += 1
            hecho = True
            break
        if not hecho:
            break
    for e in [e for e in bm.edges if not e.link_faces]:   # las aristas viejas del vértice movido quedan sueltas
        bm.edges.remove(e)
    for v in [v for v in bm.verts if not v.link_edges]:
        bm.verts.remove(v)
    bm.to_mesh(me)
    me.update()
    bm.free()
    return separadas


bm = bmesh.new()
bm.from_mesh(ob.data)
A.log('aristas raras', [(len(e.link_faces), tuple(round(c, 3) for c in (e.verts[0].co + e.verts[1].co) / 2)) for e in bm.edges
                        if len(e.link_faces) != 2])
bm.free()
separadas = separar_contactos(ob.data) if abiertas else 0
abiertas, islas = revisar(ob)
assert tris <= 4000 and tam[0] <= 3 and tam[2] <= 4 and tam[1] <= 3, (tris, tam)
img = next((n.image for s in ob.material_slots if s.material and s.material.node_tree for n in s.material.node_tree.nodes
            if n.type == 'TEX_IMAGE' and n.image), None)
tex, tex_px = None, None
if img:
    origen = bpy.path.abspath(img.filepath)
    if not os.path.exists(origen):
        origen = os.path.join(ARTE, 'mascotas-enemigos-v01', 'nube', 'texturas', os.path.basename(img.filepath))
    tex_px = list(img.size)
    tex = os.path.join(OUT, 'GorroNubecita_textura_%d.png' % tex_px[0])
    shutil.copyfile(origen, tex)
    if ACLARAR > 0:
        # Studio (30/10): con la luz de Roblox la nube salía gris-lavanda, porque su sombra se suma a la pintada en la textura.
        # Se aclaran los blancos y lavandas de ESTA copia (la mascota del juego no se toca). La cara (oscura) y las mejillas
        # (rosa: más rojo que azul) se quedan igual.
        im2 = bpy.data.images.load(tex)
        px = np.array(im2.pixels[:]).reshape(-1, 4)
        r, g, b = px[:, 0], px[:, 1], px[:, 2]
        nube = (b >= r) & (b >= g) & (0.2126 * r + 0.7152 * g + 0.0722 * b > 0.35)
        px[nube, :3] += (1 - px[nube, :3]) * ACLARAR
        im2.pixels[:] = px.ravel()
        im2.filepath_raw, im2.file_format = tex, 'PNG'
        im2.save()
        for s in ob.material_slots:                # el FBX incrusta la imagen del material: que sea la aclarada
            if s.material and s.material.node_tree:
                for n in s.material.node_tree.nodes:
                    if n.type == 'TEX_IMAGE' and n.image:
                        n.image = im2
# Probado en Studio (30/10): con axis_forward Z el 3D Importer deja el +Y de Blender (la cara) hacia +Z de Roblox, que es la NUCA del
# avatar (los personajes miran a -Z). El FBX sale girado 180° en vertical para que la cara mire al frente; el .blend no se toca.
GIRO = Matrix.Rotation(math.pi, 4, 'Z')
ob.data.transform(GIRO)
fbx(os.path.join(OUT, 'GorroNubecita.fbx'), [ob], False)
ob.data.transform(GIRO.inverted())
A.save_blend(os.path.join(OUT, 'GorroNubecita.blend'))
if os.path.exists(os.path.join(OUT, 'GorroNubecita.blend1')):
    os.remove(os.path.join(OUT, 'GorroNubecita.blend1'))

# ---- previsualización: avatar R15 de bloques con los colores clásicos, varios tamaños uno al lado del otro ----
AMARILLO, AZUL, VERDE, NEGRO = '#f5cd30', '#0d69ac', '#a4bd47', '#1b1b1f'


def material(color):
    m = bpy.data.materials.get('av' + color)
    if not m:
        m = bpy.data.materials.new('av' + color)
        m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*lin(color), 1)
        b.inputs['Roughness'].default_value = 0.55
    return m


def colgar(o, raiz, color):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    CV.objects.link(o)
    o.parent = raiz
    o.data.materials.append(material(color))
    return o


def pieza(raiz, loc, dims, color, cilindro=False):
    if cilindro:                               # cabeza clásica: cilindro de cantos muy redondeados
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.5, depth=1, location=loc)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.data.transform(Matrix.Diagonal((*dims, 1)))
    b = o.modifiers.new('Bisel', 'BEVEL')
    b.width, b.segments = (0.2, 6) if cilindro else (0.05, 3)
    if cilindro:
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    return colgar(o, raiz, color)


def cara(raiz):
    for ex in (-0.19, 0.19):                   # ojos y sonrisa de la cara por defecto, pegados al cilindro
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=(ex, 0.56, 4.72))
        o = bpy.context.active_object
        o.data.transform(Matrix.Diagonal((0.07, 0.04, 0.11, 1)))
        colgar(o, raiz, NEGRO)
    cu = bpy.data.curves.new('Sonrisa', 'CURVE')
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = '3D', 0.028, 3
    sp = cu.splines.new('POLY')
    pts = []
    for i in range(11):
        t = -1 + i / 5
        xx = 0.22 * t
        pts.append((xx, math.sqrt(0.6 ** 2 - xx ** 2) + 0.004, 4.45 + 0.08 * t * t))
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    o = bpy.data.objects.new('Sonrisa', cu)
    CV.objects.link(o)
    colgar(o, raiz, NEGRO)


def avatar(x, giro, ancho):
    raiz = bpy.data.objects.new('Avatar_%.1f' % ancho, None)
    CV.objects.link(raiz)
    raiz.location, raiz.rotation_euler = (x, 0, 0), (0, 0, math.radians(giro))
    for lx in (-0.5, 0.5):
        pieza(raiz, (lx, 0, 1), (1, 1, 2), VERDE)
    pieza(raiz, (0, 0, 3), (2, 1, 2), AZUL)
    for lx in (-1.5, 1.5):
        pieza(raiz, (lx, 0, 3), (1, 1, 2), AMARILLO)
    pieza(raiz, (0, 0, 4.6), (1.2, 1.2, 1.2), AMARILLO, cilindro=True)
    cara(raiz)
    g = bpy.data.objects.new('Gorro_%.1f' % ancho, ob.data)   # la misma malla, escalada
    CV.objects.link(g)
    g.parent = raiz
    g.scale = (ancho / ANCHO,) * 3
    g.location = (0, 0, CABEZA_TOP - HUNDIR)
    return raiz


fuente = bpy.data.fonts.load(r'C:\Windows\Fonts\ariblk.ttf')


def rotulo(texto, x, color):
    cu = bpy.data.curves.new('Rotulo', 'FONT')
    cu.body, cu.font, cu.size, cu.align_x = texto, fuente, 0.62, 'CENTER'
    o = bpy.data.objects.new('Rotulo', cu)
    CV.objects.link(o)
    o.location, o.rotation_euler = (x, 0.6, -1.15), (math.radians(90), 0, math.radians(180))   # de cara a la cámara (+Y)
    o.data.materials.append(material(color))
    return o


# en pantalla de izquierda a derecha (la cámara mira desde +Y, así que la derecha de la imagen es -X)
avatares = {}
for i, w in enumerate(COMPARAR):
    x = 7.5 - 5 * i
    avatares[w] = avatar(x, 22, w)
    rotulo(('%.1f' % w).replace('.', ','), x, '#1f5fbf' if abs(w - ANCHO) < 1e-6 else '#6b7b8b')   # el elegido, en azul


def solo(raiz):
    for r in avatares.values():
        for o in [r] + list(r.children_recursive):
            o.hide_render = raiz is not None and r is not raiz
    for o in CV.objects:
        if o.type == 'FONT':
            o.hide_render = raiz is not None


sol(CC, 'Sol', 3.0, (-0.4, 0.5, -0.75))
sol(CC, 'Relleno', 0.9, (0.6, -0.3, -0.4), 20.0)
A.setup_world(lin('#bde4ff'), 1.0)
for f in ('GorroNubecita-frente.jpg',):        # la v1 se veía sobre un bloque amarillo: fuera
    if os.path.exists(os.path.join(OUT, f)):
        os.remove(os.path.join(OUT, f))
ob.hide_render = True                          # el original queda en el origen: solo se ven las copias puestas
A.setup_render((1600, 820), 'CYCLES', 48)
bpy.context.scene.render.image_settings.file_format = 'JPEG'
solo(None)
A.render(os.path.join(OUT, 'GorroNubecita-tamanos.jpg'), A.camera(CC, 'Tamanos', (0, 32, 5.6), (0, 0, 3.0), lens=50))
xe = 7.5 - 5 * COMPARAR.index(ANCHO) if ANCHO in COMPARAR else None
if xe is not None:
    solo(avatares[ANCHO])
    A.setup_render((1200, 1200), 'CYCLES', 48)
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    # el avatar está girado 22° (su frente mira a (-0,37, 0,93)): de 3/4 la cámara va unos 37° hacia el otro lado
    A.render(os.path.join(OUT, 'GorroNubecita-avatar.jpg'), A.camera(CC, 'Avatar', (xe + 3.0, 10.5, 5.2), (xe, 0, 3.4), lens=50))
    # como la foto de perfil de Roblox: casi de frente, cabeza y gorro
    A.render(os.path.join(OUT, 'GorroNubecita-cabeza.jpg'), A.camera(CC, 'Cabeza', (xe - 0.4, 5.3, 5.9), (xe, 0, 5.45), lens=50))
    # foto de catálogo: el gorro solo, como lo enseña el Marketplace
    for o in [avatares[ANCHO]] + list(avatares[ANCHO].children_recursive):
        o.hide_render = not o.name.startswith('Gorro')
    A.render(os.path.join(OUT, 'GorroNubecita-34.jpg'),
             A.camera(CC, 'Catalogo', (xe + 0.6 * ANCHO, 1.65 * ANCHO, CABEZA_TOP + 0.75 * ANCHO), (xe, 0, CABEZA_TOP + 0.21 * ANCHO), lens=50))
A.write_json(os.path.join(OUT, 'datos.json'), {
    'accesorio': 'Gorro Nubecita (Hat, rigido)', 'ancho_elegido': ANCHO, 'comparados': list(COMPARAR), 'triangulos': tris,
    'tamano_studs_x_y_z_blender': tam, 'limites_hat_classic': [3, 4, 3], 'aristas_abiertas_o_no_manifold': abiertas, 'contactos_separados': separadas, 'islas': islas,
    'attachment': 'HatAttachment en la base, centrada; se hunde %.2f en la cabeza' % HUNDIR,
    'textura': os.path.basename(tex) if tex else None, 'textura_px': tex_px, 'textura_aclarada': ACLARAR,
    'fbx': 'GorroNubecita.fbx (global_scale 0.01, axis_forward Z, girado 180 grados: en Studio la cara mira a -Z, el frente del avatar)', 'subido_a_roblox': False})
A.log('listo', 'ancho', ANCHO, 'tris', tris, 'tam', tam, 'abiertas', abiertas, 'separadas', separadas, 'islas', islas, 'textura', tex_px)
