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
ob.name = ob.data.name = 'GorroFuente'         # la malla de la mascota: de aquí sale la piel nueva y se hornea su textura


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


def islas_de_caras(bm):
    isla, n = {}, 0
    for f in bm.faces:
        if f in isla:
            continue
        pila = [f]
        isla[f] = n
        while pila:
            for e in pila.pop().edges:
                for h in e.link_faces:
                    if h not in isla:
                        isla[h] = n
                        pila.append(h)
        n += 1
    return isla


def piel_voxel(fuente):
    """El validador de UGC de Studio (31/10) avisaba de malla no-manifold: la mascota son 14 piezas cerradas que se cortan (el
    cuerpo, las dos nubecitas laterales y 11 cajitas de la cara). Aquí se mide qué celdas de la rejilla caen dentro del cuerpo o de
    una nubecita (todas comparten rejilla) y se crea UNA piel con solo las caras entre celda llena y vacía. Los contactos en
    diagonal (dos celdas que solo se tocan por una arista o un vértice) se rellenan con una celda. La cara (ojos, brillos,
    mejillas, boca) no entra como geometría: se hornea en la textura desde la malla original."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(fuente.data)
    isla = islas_de_caras(bm)
    cuenta = {}
    for i in isla.values():
        cuenta[i] = cuenta.get(i, 0) + 1
    grandes = [i for i, c in cuenta.items() if c > 100]
    largos = sorted(round(e.calc_length(), 5) for e in bm.edges if isla[e.link_faces[0]] in grandes and e.calc_length() > 1e-4)
    celda = next(x for x in largos if largos.count(x) >= 10)
    o = next(f for f in bm.faces if isla[f] in grandes).verts[0].co.copy()
    d = Vector((1.0, 0.0137, 0.0071)).normalized()   # rayo un poco inclinado: no roza aristas ni esquinas

    def idx(p):
        return tuple(int(round((p[a] - o[a]) / celda)) for a in range(3))

    llenas = set()
    for i in grandes:
        fs = [f for f in bm.faces if isla[f] == i]
        vs = list({v for f in fs for v in f.verts})
        ix = {v: n for n, v in enumerate(vs)}
        arbol = BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in fs])
        i0 = idx([min(v.co[a] for v in vs) for a in range(3)])
        i1 = idx([max(v.co[a] for v in vs) for a in range(3)])
        for ci in range(i0[0], i1[0]):
            for cj in range(i0[1], i1[1]):
                for ck in range(i0[2], i1[2]):
                    q, cortes = o + Vector(((ci + 0.5) * celda, (cj + 0.5) * celda, (ck + 0.5) * celda)), 0
                    while True:
                        hit = arbol.ray_cast(q, d)
                        if hit[0] is None:
                            break
                        cortes += 1
                        q = hit[0] + d * 1e-5
                    if cortes % 2:
                        llenas.add((ci, cj, ck))
    bm.free()
    E = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

    def mas(c, *ds):
        return tuple(c[a] + sum(x[a] for x in ds) for a in range(3))

    def por(v, s):
        return tuple(x * s for x in v)

    rellenas, cambio = 0, True
    while cambio:
        cambio = False
        for c in list(llenas):
            for a in range(3):
                for b in range(a + 1, 3):
                    for sa in (-1, 1):
                        for sb in (-1, 1):
                            da, db = por(E[a], sa), por(E[b], sb)
                            if mas(c, da, db) in llenas and mas(c, da) not in llenas and mas(c, db) not in llenas:
                                llenas.add(mas(c, da))
                                rellenas, cambio = rellenas + 1, True
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        dx, dy, dz = por(E[0], sx), por(E[1], sy), por(E[2], sz)
                        otras = (mas(c, dx), mas(c, dy), mas(c, dz), mas(c, dx, dy), mas(c, dx, dz), mas(c, dy, dz))
                        if mas(c, dx, dy, dz) in llenas and not any(x in llenas for x in otras):
                            llenas.add(mas(c, dx))
                            rellenas, cambio = rellenas + 1, True
    piel = bmesh.new()
    vert = {}

    def V(ijk):
        if ijk not in vert:
            vert[ijk] = piel.verts.new(o + Vector(ijk) * celda)
        return vert[ijk]

    for c in llenas:
        for a in range(3):
            b, cc = [x for x in range(3) if x != a]
            for s in (-1, 1):
                if mas(c, por(E[a], s)) in llenas:
                    continue
                p = list(c)
                if s > 0:
                    p[a] += 1
                p1, p2, p3 = list(p), list(p), list(p)
                p1[b] += 1
                p2[b] += 1
                p2[cc] += 1
                p3[cc] += 1
                piel.faces.new([V(tuple(p)), V(tuple(p1)), V(tuple(p2)), V(tuple(p3))])
    bmesh.ops.recalc_face_normals(piel, faces=piel.faces[:])
    me = bpy.data.meshes.new('GorroNubecita')
    piel.to_mesh(me)
    piel.free()
    nuevo = bpy.data.objects.new('GorroNubecita', me)
    CM.objects.link(nuevo)
    return nuevo, celda, len(llenas), rellenas


def no_manifold(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    r = (sum(1 for e in bm.edges if not e.is_manifold), sum(1 for v in bm.verts if not v.is_manifold),
         sum(1 for f in bm.faces if f.calc_area() < 1e-7))
    bm.free()
    return r


fuente = ob
ob, CELDA, CELDAS, RELLENAS = piel_voxel(fuente)
co = [v.co.copy() for v in ob.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)])
mx = Vector([max(c[i] for c in co) for i in range(3)])
tam = [round(mx[i] - mn[i], 3) for i in range(3)]   # x ancho, y fondo, z alto (Blender)
tris = 2 * len(ob.data.polygons)                    # todo quads planos: Roblox los parte en 2 triángulos sin degenerados
ARISTAS_NM, VERTICES_NM, CARAS_0 = no_manifold(ob)
abiertas, islas = revisar(ob)
A.log('piel', 'celda', round(CELDA, 4), 'celdas', CELDAS, 'rellenas', RELLENAS, 'tris', tris, 'no-manifold', ARISTAS_NM, VERTICES_NM,
      'area0', CARAS_0, 'islas', islas)
assert tris <= 4000 and tam[0] <= 3 and tam[2] <= 4 and tam[1] <= 3, (tris, tam)
assert ARISTAS_NM == 0 and VERTICES_NM == 0 and CARAS_0 == 0 and islas == 1, (ARISTAS_NM, VERTICES_NM, CARAS_0, islas)
img = next((n.image for s in fuente.material_slots if s.material and s.material.node_tree for n in s.material.node_tree.nodes
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
        for s in fuente.material_slots:            # el horneado lee la imagen del material de la fuente: que sea la aclarada
            if s.material and s.material.node_tree:
                for n in s.material.node_tree.nodes:
                    if n.type == 'TEX_IMAGE' and n.image:
                        n.image = im2


def hornear(piel, fuente, lado=2048):
    """Textura nueva de la piel (2048: el validador pedía más resolución que 1024): UV propias sin solapes, el color de la malla
    original (cara incluida) horneado desde fuera hacia dentro, y una oclusión suave en los huecos entre vóxeles (el validador
    avisaba de textura «poco compleja»: colores planos)."""
    A.select_only([piel])
    bpy.context.view_layer.objects.active = piel
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    sc = bpy.context.scene
    sc.render.engine, sc.cycles.device, sc.cycles.samples = 'CYCLES', 'CPU', 4
    color = bpy.data.images.new('GorroColor', lado, lado, alpha=False)
    mat = bpy.data.materials.new('GorroNubecita')
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes['Principled BSDF']
    nodo = nt.nodes.new('ShaderNodeTexImage')
    nodo.image = color
    nt.links.new(nodo.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.6
    nt.nodes.active = nodo
    piel.data.materials.append(mat)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    fuente.select_set(True)
    piel.select_set(True)
    bpy.context.view_layer.objects.active = piel
    # los brillos de los ojos sobresalen ~0,07 de la placa de la cara: el rayo tiene que salir de más fuera que ellos
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=True, cage_extrusion=0.09,
                        max_ray_distance=0.18, margin=8, use_clear=True)
    bpy.data.objects.remove(fuente)            # sin la fuente: si no, tapa toda la oclusión
    if not sc.world:
        sc.world = bpy.data.worlds.new('Mundo')
    sc.world.light_settings.distance = 0.12     # oclusión local: solo los huecos entre vóxeles
    ao = bpy.data.images.new('GorroAO', lado, lado, alpha=False)
    nodo.image = ao
    sc.cycles.samples = 64
    A.select_only([piel])
    bpy.ops.object.bake(type='AO', margin=8, use_clear=True)
    px = np.array(color.pixels[:]).reshape(-1, 4)
    oc = np.array(ao.pixels[:]).reshape(-1, 4)
    px[:, :3] *= 0.82 + 0.18 * oc[:, :1]
    final = bpy.data.images.new('GorroNubecita_textura_%d' % lado, lado, lado, alpha=False)
    final.pixels[:] = px.ravel()
    ruta = os.path.join(OUT, 'GorroNubecita_textura_%d.png' % lado)
    final.filepath_raw, final.file_format = ruta, 'PNG'
    final.save()
    nodo.image = final
    for im in (color, ao):
        bpy.data.images.remove(im)
    return ruta


tex1024 = tex
tex = hornear(ob, fuente)
tex_px = [2048, 2048]
if tex1024 and os.path.exists(tex1024):
    os.remove(tex1024)                         # la copia aclarada de 1024 solo era la fuente del horneado
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
    'tamano_studs_x_y_z_blender': tam, 'limites_hat_classic': [3, 4, 3], 'malla': 'piel de voxeles de una pieza (celda %.4f, %d celdas, %d rellenadas en contactos en diagonal)' % (CELDA, CELDAS, RELLENAS), 'aristas_no_manifold': ARISTAS_NM, 'vertices_no_manifold': VERTICES_NM, 'caras_area_cero': CARAS_0, 'islas': islas,
    'attachment': 'HatAttachment en la base, centrada; se hunde %.2f en la cabeza' % HUNDIR,
    'textura': os.path.basename(tex) if tex else None, 'textura_px': tex_px, 'textura_aclarada': ACLARAR,
    'fbx': 'GorroNubecita.fbx (global_scale 0.01, axis_forward Z, girado 180 grados: en Studio la cara mira a -Z, el frente del avatar)', 'subido_a_roblox': False})
A.log('listo', 'ancho', ANCHO, 'tris', tris, 'tam', tam, 'no-manifold', ARISTAS_NM, VERTICES_NM, 'islas', islas, 'textura', tex_px)
