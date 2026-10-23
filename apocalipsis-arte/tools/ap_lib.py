# Utilidades comunes para el arte del juego "apocalipsis" (Blender 5.2, sin interfaz: blender -b -P script.py).
# Convenciones: 1 unidad de Blender = 1 stud. Delante = +Y, arriba = +Z (el FBX lo convierte a Roblox: -Z delante, +Y arriba).
# Estilo: geometria facetada (sombreado plano) + textura pintada a mano: se hornean mapas de datos con Cycles
# (region, posicion, normal, oclusion, bordes) y la pintura se compone en numpy (pinceladas, desgaste, suciedad, luz pintada).
import bpy, bmesh, math, os, json, time
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion

T0 = time.time()


def log(*a):
    print('[AP %6.1fs]' % (time.time() - T0), *a, flush=True)


# ------------------------------------------------------------------ escena
def clean_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.armatures, bpy.data.actions,
                 bpy.data.cameras, bpy.data.lights, bpy.data.curves, bpy.data.node_groups):
        for d in list(coll):
            try:
                coll.remove(d)
            except Exception:
                pass
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.render.fps = 60
    sc.render.fps_base = 1.0
    if sc.world is None:
        sc.world = bpy.data.worlds.new('Mundo')
    return sc


def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    p = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in p.children]:
        p.children.link(c)
    return c


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


# ------------------------------------------------------------------ materiales de region (solo para hornear)
REGIONS = []          # nombres de region en orden global -> id = indice + 1


def region_mat(name):
    if name not in REGIONS:
        REGIONS.append(name)
    m = bpy.data.materials.get('R_' + name)
    if m is None:
        m = bpy.data.materials.new('R_' + name)
        rid = REGIONS.index(name) + 1
        rng = np.random.default_rng(rid * 7919)
        m.diffuse_color = (*rng.uniform(0.2, 0.9, 3), 1.0)
    return m


def region_id(name):
    return REGIONS.index(name) + 1


# ------------------------------------------------------------------ constructor de mallas facetadas
def _offset_polyline(path, d, closed=False):
    pts = [Vector((p[0], p[1])) for p in path]
    n = len(pts)
    left, right = [], []
    for i in range(n):
        if closed:
            a, b = pts[i - 1], pts[(i + 1) % n]
        else:
            a = pts[i - 1] if i > 0 else pts[i]
            b = pts[i + 1] if i < n - 1 else pts[i]
        t = (b - a)
        if t.length < 1e-9:
            t = Vector((1, 0))
        t.normalize()
        nrm = Vector((-t.y, t.x))
        # miter
        if 0 < i < n - 1 or closed:
            t1 = (pts[i] - a).normalized() if (pts[i] - a).length > 1e-9 else t
            n1 = Vector((-t1.y, t1.x))
            miter = (nrm + n1)
            if miter.length > 1e-6:
                miter.normalize()
                k = d / max(0.35, miter.dot(n1))
                nrm, dd = miter, k
            else:
                dd = d
        else:
            dd = d
        left.append(tuple(pts[i] + nrm * dd))
        right.append(tuple(pts[i] - nrm * dd))
    return left, right


class MB:
    """Constructor de una pieza (un objeto) con bmesh. Cada cara lleva un material de region."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.mat_names = []

    def mi(self, mat):
        if mat not in self.mat_names:
            self.mat_names.append(mat)
        return self.mat_names.index(mat)

    def face(self, verts, mat):
        f = self.bm.faces.new(verts)
        f.material_index = self.mi(mat)
        return f

    def _bevel_edges(self, edges, off):
        if off > 0 and edges:
            bmesh.ops.bevel(self.bm, geom=list(edges), offset=off, offset_type='OFFSET', segments=1,
                            profile=0.5, affect='EDGES', clamp_overlap=True)

    # caja centrada en c con tamano s; bevel en aristas de un eje ('x','y','z') o 'all'
    def box(self, c, s, mat, bevel=0.0, edges='all', mats=None):
        cx, cy, cz = c
        hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        V = {}
        for ix in (0, 1):
            for iy in (0, 1):
                for iz in (0, 1):
                    V[ix, iy, iz] = self.bm.verts.new((cx + (2 * ix - 1) * hx, cy + (2 * iy - 1) * hy, cz + (2 * iz - 1) * hz))
        quads = {
            '-x': (V[0, 0, 0], V[0, 0, 1], V[0, 1, 1], V[0, 1, 0]),
            '+x': (V[1, 0, 0], V[1, 1, 0], V[1, 1, 1], V[1, 0, 1]),
            '-y': (V[0, 0, 0], V[1, 0, 0], V[1, 0, 1], V[0, 0, 1]),
            '+y': (V[0, 1, 0], V[0, 1, 1], V[1, 1, 1], V[1, 1, 0]),
            '-z': (V[0, 0, 0], V[0, 1, 0], V[1, 1, 0], V[1, 0, 0]),
            '+z': (V[0, 0, 1], V[1, 0, 1], V[1, 1, 1], V[0, 1, 1]),
        }
        fs = {k: self.face(q, (mats or {}).get(k, mat)) for k, q in quads.items()}
        if bevel > 0:
            es = set()
            for f in fs.values():
                for e in f.edges:
                    d = e.verts[1].co - e.verts[0].co
                    ax = 'x' if abs(d.x) > 1e-9 else ('y' if abs(d.y) > 1e-9 else 'z')
                    if edges == 'all' or ax in edges:
                        es.add(e)
            self._bevel_edges(es, bevel)
        return fs

    # poligono 2D (u,v) extruido entre w0 y w1. plane: 'YZ' (perfil lateral, grosor en X), 'XY' (planta, alto en Z), 'XZ' (frente, fondo en Y)
    def prism(self, pts, w0, w1, mat, plane='YZ', bevel=0.0, cap_mat=None, side_mat=None, cap0=True, cap1=True):
        return self.loft([pts, pts], [w0, w1], mat, plane, bevel, cap_mat, side_mat, cap0, cap1)

    # seccion variable: secs = lista de poligonos (mismo numero de puntos) en las posiciones ws del eje de extrusion
    def loft(self, secs, ws, mat, plane='YZ', bevel=0.0, cap_mat=None, side_mat=None, cap0=True, cap1=True, side_mats=None):
        def P(u, v, w):
            if plane == 'YZ':
                return (w, u, v)
            if plane == 'XY':
                return (u, v, w)
            return (u, w, v)  # XZ
        # orientar todos los poligonos en sentido antihorario (area positiva)
        def area(p):
            return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2
        if area(secs[0]) < 0:
            secs = [s[::-1] for s in secs]
        if ws[-1] < ws[0]:
            secs, ws = secs[::-1], ws[::-1]
        rings = [[self.bm.verts.new(P(u, v, w)) for (u, v) in s] for s, w in zip(secs, ws)]
        n = len(secs[0])
        flip = (plane == 'XZ')
        def F(vs, m):
            return self.face(vs[::-1] if flip else vs, m)
        c0 = F(rings[0][::-1], cap_mat or mat) if cap0 else None
        c1 = F(rings[-1], cap_mat or mat) if cap1 else None
        sides = []
        for k in range(len(rings) - 1):
            a, b = rings[k], rings[k + 1]
            for i in range(n):
                m = side_mats[k] if side_mats else (side_mat or mat)
                sides.append(F((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]), m))
        if bevel > 0:
            es = set()
            if c0:
                es |= set(c0.edges[:])
            if c1:
                es |= set(c1.edges[:])
            self._bevel_edges(es, bevel)
        return c0, c1, sides

    def new_verts_since(self, before):
        return [v for v in self.bm.verts if v not in before]

    def mark(self):
        return set(self.bm.verts)

    def xform_since(self, before, M):
        vs = self.new_verts_since(before)
        bmesh.ops.transform(self.bm, matrix=M, verts=vs)
        return vs

    # caja alineada con el segmento p0->p1 (seccion w x h); 'up' orienta el lado alto
    def seg_box(self, p0, p1, w, h, mat, bevel=0.0, extend=0.0):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        L = d.length + 2 * extend
        q = d.normalized().to_track_quat('Y', 'Z')
        mk = self.mark()
        self.box((0, L / 2 - extend, 0), (w, L, h), mat, bevel=bevel, edges='y')
        self.xform_since(mk, Matrix.Translation(p0) @ q.to_matrix().to_4x4())

    def band(self, path, width, w0, w1, mat, plane='YZ', bevel=0.0):
        l, r = _offset_polyline(path, width / 2)
        return self.prism(l + r[::-1], w0, w1, mat, plane, bevel)

    # cilindro facetado de p0 a p1
    def cyl(self, p0, p1, r0, segs, mat, r1=None, cap0=True, cap1=True, rot=None, cap_mat=None, bevel=0.0, inset_cap1=0.0, inset_depth=0.0, inset_mat=None):
        p0, p1 = Vector(p0), Vector(p1)
        d = (p1 - p0).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        u = d.cross(up).normalized()
        w = d.cross(u).normalized()
        rot = (math.pi / segs) if rot is None else rot
        r1 = r0 if r1 is None else r1
        ra, rb = [], []
        for i in range(segs):
            a = rot + 2 * math.pi * i / segs
            off = u * math.cos(a) + w * math.sin(a)
            ra.append(self.bm.verts.new(p0 + off * r0))
            rb.append(self.bm.verts.new(p1 + off * r1))
        sides = [self.face((ra[i], ra[(i + 1) % segs], rb[(i + 1) % segs], rb[i]), mat) for i in range(segs)]
        c0 = self.face(ra[::-1], cap_mat or mat) if cap0 else None
        c1 = self.face(rb, cap_mat or mat) if cap1 else None
        if bevel > 0:
            es = set()
            if c0:
                es |= set(c0.edges[:])
            if c1:
                es |= set(c1.edges[:])
            self._bevel_edges(es, bevel)
        if c1 is not None and inset_cap1 > 0:
            res = bmesh.ops.inset_individual(self.bm, faces=[c1], thickness=inset_cap1, depth=0.0)
            bmesh.ops.translate(self.bm, vec=-d * inset_depth, verts=c1.verts[:])
            if inset_mat:
                c1.material_index = self.mi(inset_mat)
        return sides, c0, c1

    # revolucion de un perfil [(radio, t)] alrededor del eje p0->p1 (t en [0,1] a lo largo del eje)
    def lathe(self, p0, p1, prof, segs, mat, rot=None, close0=True, close1=True, mats=None):
        p0, p1 = Vector(p0), Vector(p1)
        axis = p1 - p0
        d = axis.normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        u = d.cross(up).normalized()
        w = d.cross(u).normalized()
        rot = (math.pi / segs) if rot is None else rot
        rings = []
        for (r, t) in prof:
            ring = []
            for i in range(segs):
                a = rot + 2 * math.pi * i / segs
                off = u * math.cos(a) + w * math.sin(a)
                ring.append(self.bm.verts.new(p0 + axis * t + off * r))
            rings.append(ring)
        fs = []
        for k in range(len(rings) - 1):
            m = mats[k] if mats else mat
            for i in range(segs):
                fs.append(self.face((rings[k][i], rings[k][(i + 1) % segs], rings[k + 1][(i + 1) % segs], rings[k + 1][i]), m))
        if close0:
            fs.append(self.face(rings[0][::-1], mats[0] if mats else mat))
        if close1:
            fs.append(self.face(rings[-1], mats[-1] if mats else mat))
        return fs

    # roca/forma organica: icosfera deformada
    def rock(self, c, r, mat, subdiv=1, seed=0, jitter=0.25, squash=(1, 1, 1)):
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=r, matrix=Matrix.Translation(Vector(c)))
        rng = np.random.default_rng(seed)
        for v in res['verts']:
            dv = v.co - Vector(c)
            k = 1.0 + rng.uniform(-jitter, jitter)
            v.co = Vector(c) + Vector((dv.x * squash[0], dv.y * squash[1], dv.z * squash[2])) * k
        fs = {f for v in res['verts'] for f in v.link_faces}
        for f in fs:
            f.material_index = self.mi(mat)
        return list(fs)

    def transform_last(self, verts, mat4):
        bmesh.ops.transform(self.bm, matrix=mat4, verts=verts)

    def finish(self, coll, origin=(0, 0, 0), triangulate=True, recalc=False):
        bm = self.bm
        if recalc:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if triangulate:
            # las caras nuevas de bmesh tienen normal (0,0,0): sin calcularla, el triangulado proyecta los poligonos
            # concavos (empunaduras, culatas) en un plano equivocado y crea triangulos fuera del contorno, invertidos (negros)
            bm.normal_update()
            bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='EAR_CLIP')
        o = Vector(origin)
        for v in bm.verts:
            v.co -= o
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = False
        ob = bpy.data.objects.new(self.name, me)
        ob.location = o
        coll.objects.link(ob)
        for mn in self.mat_names:
            me.materials.append(region_mat(mn))
        return ob


def tris(objs):
    n = 0
    for o in objs:
        if o.type == 'MESH':
            n += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return n


def set_origin(ob, point):
    """Mueve el origen del objeto a 'point' (coordenadas de mundo) sin mover la geometria."""
    point = Vector(point)
    off = point - ob.location
    ob.data.transform(Matrix.Translation(-off))
    ob.location = point


# ------------------------------------------------------------------ UV
def select_only(objs, active=None):
    vl = bpy.context.view_layer
    vl.update()
    for o in bpy.data.objects:
        if o is not None and vl.objects.get(o.name) is not None:
            o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def uv_unwrap(objs, angle=52.0, margin=0.006, weights=None):
    for o in objs:
        if not o.data.uv_layers:
            o.data.uv_layers.new(name='UVMap')
    select_only(objs)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    if weights:
        for o in objs:
            k = weights.get(o.name, 1.0)
            if k != 1.0:
                uv = o.data.uv_layers.active.data
                arr = np.empty(len(uv) * 2, np.float32)
                uv.foreach_get('uv', arr)
                uv.foreach_set('uv', arr * k)
    select_only(objs)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='SELECT')
    try:
        bpy.ops.uv.pack_islands(rotate=True, margin=margin, shape_method='CONCAVE')
    except TypeError:
        bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


# ------------------------------------------------------------------ horneado de mapas de datos (Cycles)
NRM_SMOOTH = False      # True: la luz pintada usa la normal suavizada (formas organicas); False: facetada


def _nodes_clear(mat):
    if hasattr(mat, 'use_nodes'):
        try:
            mat.use_nodes = True
        except Exception:
            pass
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt


def _bake_tree(mat, pas, img, rid, R, ao_dist, bevel_r, pos_ref=None):
    nt = _nodes_clear(mat)
    N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial')
    em = N.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0
    L.new(em.outputs['Emission'], out.inputs['Surface'])
    if pas == 'ID':
        em.inputs['Color'].default_value = (rid / 255.0, 0.0, 0.0, 1.0)
    elif pas == 'POS':
        tc = N.new('ShaderNodeTexCoord')
        if pos_ref is not None:
            tc.object = pos_ref
        mul = N.new('ShaderNodeVectorMath'); mul.operation = 'MULTIPLY_ADD'
        L.new(tc.outputs['Object'], mul.inputs[0])
        mul.inputs[1].default_value = (0.5 / R, 0.5 / R, 0.5 / R)
        mul.inputs[2].default_value = (0.5, 0.5, 0.5)
        L.new(mul.outputs['Vector'], em.inputs['Color'])
    elif pas == 'NRM':
        geo = N.new('ShaderNodeNewGeometry')
        mul = N.new('ShaderNodeVectorMath'); mul.operation = 'MULTIPLY_ADD'
        L.new(geo.outputs['Normal' if NRM_SMOOTH else 'True Normal'], mul.inputs[0])
        mul.inputs[1].default_value = (0.5, 0.5, 0.5)
        mul.inputs[2].default_value = (0.5, 0.5, 0.5)
        L.new(mul.outputs['Vector'], em.inputs['Color'])
    elif pas == 'AO':
        ao = N.new('ShaderNodeAmbientOcclusion')
        ao.samples = 24
        ao.inputs['Distance'].default_value = ao_dist
        L.new(ao.outputs['AO'], em.inputs['Color'])
    elif pas == 'EDGE':
        geo = N.new('ShaderNodeNewGeometry')
        bev = N.new('ShaderNodeBevel')
        bev.samples = 8
        bev.inputs['Radius'].default_value = bevel_r
        dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
        L.new(bev.outputs['Normal'], dot.inputs[0])
        L.new(geo.outputs['True Normal'], dot.inputs[1])
        inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'
        inv.inputs[0].default_value = 1.0
        L.new(dot.outputs['Value'], inv.inputs[1])
        L.new(inv.outputs['Value'], em.inputs['Color'])
    tex = N.new('ShaderNodeTexImage')
    tex.image = img
    N.active = tex
    tex.select = True


def bake_maps(objs, size, R, ao_dist, bevel_r, samples=16, explode=None, passes=('ID', 'POS', 'NRM', 'AO', 'EDGE'), pos_ref=None):
    """Hornea mapas de datos de todas las piezas en una sola textura. R = radio que abarca las coordenadas locales.
    explode: {obj: offset} para separar piezas moviles durante la oclusion (no tapan a otras)."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    try:
        sc.cycles.use_denoising = False
    except Exception:
        pass
    sc.render.bake.margin = 10
    try:
        sc.render.bake.margin_type = 'EXTEND'
    except Exception:
        pass
    # materiales temporales por region
    orig = {}
    for o in objs:
        orig[o.name] = [s.material for s in o.material_slots]
    regs = sorted({m.name[2:] for o in objs for m in orig[o.name] if m})
    bake_mats = {r: bpy.data.materials.new('BK_' + r) for r in regs}
    for o in objs:
        for i, s in enumerate(o.material_slots):
            s.material = bake_mats[orig[o.name][i].name[2:]]
    moved = {}
    out = {}
    for pas in passes:
        img = bpy.data.images.new('bake_' + pas, size, size, alpha=False, float_buffer=True)
        img.colorspace_settings.name = 'Non-Color'
        for r, m in bake_mats.items():
            _bake_tree(m, pas, img, region_id(r), R, ao_dist, bevel_r, pos_ref)
        if pas == 'AO' and explode:
            for o, off in explode.items():
                moved[o.name] = o.location.copy()
                o.location = o.location + Vector(off)
        bpy.context.view_layer.update()
        select_only(objs)
        t = time.time()
        # los pases de datos no necesitan muestreo; la oclusion y los bordes si
        sc.cycles.samples = 1 if pas in ('ID', 'POS', 'NRM') else (samples if pas == 'AO' else max(4, samples // 2))
        bpy.ops.object.bake(type='EMIT', margin=10, use_clear=True, target='IMAGE_TEXTURES')
        if pas == 'AO' and explode:
            for o in explode:
                o.location = moved[o.name]
        arr = np.empty(size * size * 4, np.float32)
        img.pixels.foreach_get(arr)
        out[pas] = arr.reshape(size, size, 4)[:, :, :3].copy()
        bpy.data.images.remove(img)
        log('horneado', pas, '%.1fs' % (time.time() - t))
    # cobertura (pixeles dentro de islas) = donde ID > 0 antes del margen: se calcula aparte
    for o in objs:
        for i, s in enumerate(o.material_slots):
            s.material = orig[o.name][i]
    for m in bake_mats.values():
        bpy.data.materials.remove(m)
    return out


# ------------------------------------------------------------------ ruido 3D en numpy
def _hash(ix, iy, iz, seed):
    h = (ix.astype(np.uint32) * np.uint32(73856093)) ^ (iy.astype(np.uint32) * np.uint32(19349663)) ^ \
        (iz.astype(np.uint32) * np.uint32(83492791)) ^ np.uint32(seed * 2654435761 % 4294967296)
    h ^= h >> np.uint32(13)
    h *= np.uint32(1274126177)
    h ^= h >> np.uint32(16)
    return h.astype(np.float32) / np.float32(4294967295.0)


def vnoise(p, seed=0):
    """Ruido de valor 3D suave en [0,1]. p: (...,3)"""
    f = np.floor(p)
    t = p - f
    t = t * t * (3 - 2 * t)
    i = f.astype(np.int64)
    ix, iy, iz = i[..., 0], i[..., 1], i[..., 2]
    tx, ty, tz = t[..., 0], t[..., 1], t[..., 2]
    def h(a, b, c):
        return _hash(ix + a, iy + b, iz + c, seed)
    x00 = h(0, 0, 0) * (1 - tx) + h(1, 0, 0) * tx
    x10 = h(0, 1, 0) * (1 - tx) + h(1, 1, 0) * tx
    x01 = h(0, 0, 1) * (1 - tx) + h(1, 0, 1) * tx
    x11 = h(0, 1, 1) * (1 - tx) + h(1, 1, 1) * tx
    y0 = x00 * (1 - ty) + x10 * ty
    y1 = x01 * (1 - ty) + x11 * ty
    return y0 * (1 - tz) + y1 * tz


def fbm(p, octaves=3, seed=0, lac=2.03, gain=0.5):
    s, a, tot = 0.0, 1.0, 0.0
    q = p
    for k in range(octaves):
        s = s + a * vnoise(q, seed + k * 101)
        tot += a
        a *= gain
        q = q * lac
    return s / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ pintura
class Paint:
    """Compone la textura pintada a partir de los mapas horneados.
    recipes: {region: dict(...)} ver paint_region."""

    def __init__(self, maps, R, light=(-0.35, -0.55, 0.76)):
        self.m = maps
        self.R = R
        self.ids = np.rint(maps['ID'][:, :, 0] * 255).astype(np.int32)
        self.pos = (maps['POS'] - 0.5) * 2 * R          # coordenadas locales en studs
        self.nrm = maps['NRM'] * 2 - 1
        nn = np.linalg.norm(self.nrm, axis=2, keepdims=True)
        self.nrm = self.nrm / np.maximum(nn, 1e-6)
        self.ao = np.clip(maps['AO'][:, :, 0], 0, 1)
        self.edge = np.clip(maps['EDGE'][:, :, 0], 0, 1)
        self.img = np.zeros(maps['ID'].shape, np.float32)
        L = np.array(light, np.float32)
        L /= np.linalg.norm(L)
        self.light = L
        H, W = self.ids.shape
        self.H, self.W = H, W

    def mask(self, region):
        return self.ids == region_id(region)

    def region(self, region, base, **k):
        msk = self.mask(region)
        if not msk.any():
            return msk
        col = paint_region(self, msk, hexrgb(base) if isinstance(base, str) else np.array(base, np.float32), **k)
        self.img[msk] = col
        return msk

    def save(self, path, out_size=None):
        img = np.clip(self.img, 0, 1)
        if out_size and out_size != self.W:
            f = self.W // out_size
            img = img.reshape(out_size, f, out_size, f, 3).mean(axis=(1, 3))
        h, w = img.shape[:2]
        rgba = np.ones((h, w, 4), np.float32)
        rgba[:, :, :3] = img
        im = bpy.data.images.new(os.path.basename(path), w, h, alpha=False)
        im.colorspace_settings.name = 'sRGB'
        im.pixels.foreach_set(rgba.ravel())
        im.filepath_raw = path
        im.file_format = 'PNG'
        im.save()
        return im


def paint_region(P, msk, base, var=0.07, stroke=(1.0, 1.0, 1.0), stroke_scale=6.0, tone_steps=0,
                 ao=0.55, ao_tint='#2a2030', light=0.28, face_var=0.04, edge_col=None, edge=0.0, edge_th=0.06,
                 edge_break=0.5, grime=0.0, grime_col='#4a3a2a', rust=0.0, hue_var=0.03, seed=1, extra=None,
                 grad=0.0, grad_axis=2, dust=0.0, dust_col='#8c806a', blotch=0.05):
    pos = P.pos[msk]
    nrm = P.nrm[msk]
    aov = P.ao[msk]
    edg = P.edge[msk]
    n = pos.shape[0]
    col = np.tile(base, (n, 1)).astype(np.float32)
    # manchas grandes (variacion de pintura a mano)
    if blotch > 0:
        bl = fbm(pos * stroke_scale * 0.45 + 31.0, 2, seed + 13)
        col *= (1.0 + blotch * 2.0 * (bl - 0.5))[:, None]
    # pinceladas: ruido alargado en la direccion del trazo
    st = np.array(stroke, np.float32)
    q = pos * stroke_scale / st
    nv = fbm(q, 3, seed)
    if tone_steps:
        nv = np.floor(nv * tone_steps) / tone_steps + 0.5 / tone_steps
    col *= (1.0 + var * 2.0 * (nv - 0.5))[:, None]
    # leve variacion de tono (calido/frio)
    hv = fbm(pos * stroke_scale * 0.35 + 17.0, 2, seed + 7)
    col[:, 0] *= 1.0 + hue_var * (hv - 0.5) * 2
    col[:, 2] *= 1.0 - hue_var * (hv - 0.5) * 2
    # variacion por faceta (normales cuantizadas)
    if face_var > 0:
        qn = np.rint(nrm * 6).astype(np.int64)
        fv = _hash(qn[:, 0], qn[:, 1], qn[:, 2], seed + 3)
        col *= (1.0 + face_var * (fv - 0.5) * 2)[:, None]
    # degradado pintado a lo largo de un eje (claro arriba)
    if grad > 0 and n > 10:
        z = pos[:, grad_axis]
        lo, hi = np.percentile(z, 3), np.percentile(z, 97)
        g = np.clip((z - lo) / max(hi - lo, 1e-5), 0, 1)
        col *= (1.0 - grad * 0.5 + grad * g)[:, None]
    # luz pintada (suave, desde arriba-delante-izquierda)
    lam = nrm @ P.light
    shade = 1.0 - light + light * (0.5 + 0.5 * lam)
    up = np.clip(nrm[:, 2], -1, 1)
    shade *= 1.0 + 0.06 * up
    col *= shade[:, None]
    # oclusion pintada con tinte
    tint = hexrgb(ao_tint)
    d = (1.0 - aov) * ao
    col *= (1.0 - d[:, None] * (1.0 - tint[None, :] * 1.6))
    # polvo claro en caras de arriba y rincones
    if dust > 0:
        dn = fbm(pos * stroke_scale * 1.3 + 41.0, 3, seed + 17)
        dm = np.clip(smoothstep(0.35, 0.9, nrm[:, 2]) * 0.7 + (1 - aov) * 0.6, 0, 1) * smoothstep(0.45, 0.75, dn) * dust
        dc = hexrgb(dust_col)
        col = col * (1 - dm[:, None]) + dc[None, :] * dm[:, None]
    # suciedad en rincones
    if grime > 0:
        gn = fbm(pos * stroke_scale * 0.8 + 3.3, 3, seed + 11)
        g = np.clip((1 - aov) * 1.6 + (gn - 0.55) * 1.2, 0, 1) * grime
        gc = hexrgb(grime_col)
        col = col * (1 - g[:, None]) + gc[None, :] * g[:, None]
    # oxido en manchas (cerca de bordes y rincones)
    if rust > 0:
        rn = fbm(pos * stroke_scale * 1.7 + 9.1, 3, seed + 21)
        r = smoothstep(0.62, 0.78, rn + 0.25 * edg + 0.25 * (1 - aov)) * rust
        rc = np.array([0.45, 0.24, 0.12], np.float32)
        rc2 = np.array([0.62, 0.36, 0.17], np.float32)
        rr = rc * (1 - rn[:, None]) + rc2 * rn[:, None]
        col = col * (1 - r[:, None]) + rr * r[:, None]
    # desgaste en bordes convexos (bordes con oclusion alta)
    if edge > 0 and edge_col is not None:
        ec = hexrgb(edge_col)
        en = vnoise(pos * stroke_scale * 2.6 + 5.0, seed + 31)
        em = smoothstep(edge_th, edge_th * 2.5, edg) * smoothstep(0.55, 0.85, aov)
        em = em * smoothstep(edge_break - 0.25, edge_break + 0.15, en + 0.35 * em)
        em = np.clip(em * edge, 0, 1)
        col = col * (1 - em[:, None]) + ec[None, :] * em[:, None]
    if extra is not None:
        col = extra(P, msk, pos, nrm, col)
    return np.clip(col, 0, 1)


# ------------------------------------------------------------------ material final (una textura por asset, mate)
def final_material(name, img_path):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = _nodes_clear(mat)
    N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial')
    bsdf = N.new('ShaderNodeBsdfPrincipled')
    img = bpy.data.images.load(img_path, check_existing=True)
    img.colorspace_settings.name = 'sRGB'
    tex = N.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Linear'
    L.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 1.0
    for k in ('Specular IOR Level', 'Specular'):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.0
    bsdf.inputs['Metallic'].default_value = 0.0
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def assign_final(objs, mat):
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
        for p in o.data.polygons:
            p.material_index = 0


# ------------------------------------------------------------------ rig y animacion
def make_armature(name, bones, coll, show_names=False):
    """bones: [(nombre, cabeza(x,y,z), padre o None, largo)] todos apuntando a +Y con giro 0
    (ejes del hueso = ejes del armature, asi la animacion se escribe en ejes del arma)."""
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    coll.objects.link(ob)
    select_only([ob])
    bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    for (bn, head, parent, ln) in bones:
        b = arm.edit_bones.new(bn)
        b.head = Vector(head)
        b.tail = Vector(head) + Vector((0, ln, 0))
        b.roll = 0.0
        if parent:
            b.parent = eb[parent]
            b.use_connect = False
        eb[bn] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in ob.pose.bones:
        pb.rotation_mode = 'XYZ'
    arm.display_type = 'STICK'
    ob.show_in_front = True
    return ob


def skin_rigid(ob, arm_ob, bone):
    vg = ob.vertex_groups.get(bone) or ob.vertex_groups.new(name=bone)
    vg.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
    mod = ob.modifiers.get('Armature') or ob.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm_ob
    mw = ob.matrix_world.copy()
    ob.parent = arm_ob
    ob.matrix_world = mw


def _fcurves(ob):
    ad = ob.animation_data
    act = ad.action
    if hasattr(act, 'fcurves'):
        try:
            return list(act.fcurves)
        except Exception:
            pass
    from bpy_extras import anim_utils
    cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
    return list(cb.fcurves) if cb else []


class Clip:
    """Escribe un clip: keys {hueso: [(t_seg, loc(x,y,z), rot_grados(x,y,z), interp)]}."""

    def __init__(self, arm_ob, name, length, loop=False, fps=60):
        self.arm = arm_ob
        self.name = name
        self.length = length
        self.loop = loop
        self.fps = fps
        self.keys = {}

    def k(self, bone, t, loc=(0, 0, 0), rot=(0, 0, 0), interp='BEZIER'):
        self.keys.setdefault(bone, []).append((t, loc, rot, interp))
        return self

    def build(self, all_bones):
        ob = self.arm
        ob.animation_data_create()
        act = bpy.data.actions.new(self.name)
        act.use_fake_user = True
        ob.animation_data.action = act
        sc = bpy.context.scene
        last = int(round(self.length * self.fps))
        for bn in all_bones:
            pb = ob.pose.bones[bn]
            ks = sorted(self.keys.get(bn, []), key=lambda x: x[0])
            if not ks:
                ks = [(0.0, (0, 0, 0), (0, 0, 0), 'BEZIER'), (self.length, (0, 0, 0), (0, 0, 0), 'BEZIER')]
            if ks[0][0] > 0:
                ks.insert(0, (0.0, ks[0][1], ks[0][2], 'BEZIER'))
            if ks[-1][0] < self.length:
                ks.append((self.length, ks[-1][1], ks[-1][2], 'BEZIER'))
            for (t, loc, rot, interp) in ks:
                f = t * self.fps
                pb.location = Vector(loc)
                pb.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
                pb.keyframe_insert('location', frame=f, group=bn)
                pb.keyframe_insert('rotation_euler', frame=f, group=bn)
        # interpolaciones
        fcs = _fcurves(ob)
        for fc in fcs:
            bn = fc.data_path.split('"')[1]
            spec = {round(t * self.fps, 3): ip for (t, _, _, ip) in self.keys.get(bn, [])}
            for kp in fc.keyframe_points:
                ip = spec.get(round(kp.co.x, 3), 'BEZIER')
                if ip in ('CONSTANT', 'LINEAR', 'BEZIER'):
                    kp.interpolation = ip
                else:  # 'EXPO_OUT', 'BACK_OUT', 'SINE_INOUT', etc.
                    tp, ease = ip.split('_')
                    kp.interpolation = tp
                    kp.easing = {'OUT': 'EASE_OUT', 'IN': 'EASE_IN', 'INOUT': 'EASE_IN_OUT'}[ease]
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
            if self.loop:
                pass
            fc.update()
        act.use_frame_range = True
        act.frame_start = 0
        act.frame_end = last
        try:
            act.use_cyclic = self.loop
        except Exception:
            pass
        # reposo de la pose
        for pb in ob.pose.bones:
            pb.location = (0, 0, 0)
            pb.rotation_euler = (0, 0, 0)
        return act


def stash_actions(arm_ob, actions):
    """Guarda cada clip en una pista NLA silenciada (para que queden ordenados en el .blend)."""
    ad = arm_ob.animation_data_create()
    for act in actions:
        tr = ad.nla_tracks.new()
        tr.name = act.name
        st = tr.strips.new(act.name, 0, act)
        tr.mute = True
    ad.action = None


def set_action(arm_ob, act):
    ad = arm_ob.animation_data_create()
    ad.action = act
    try:
        if act.slots and ad.action_slot is None:
            ad.action_slot = act.slots[0]
    except Exception:
        pass
    sc = bpy.context.scene
    sc.frame_start = int(act.frame_start)
    sc.frame_end = int(act.frame_end)


# ------------------------------------------------------------------ exportacion
def export_fbx(path, objs, anim=False, all_actions=False):
    select_only(objs)
    kw = dict(filepath=path, use_selection=True, object_types={'MESH', 'ARMATURE', 'EMPTY'},
              global_scale=0.01, apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True,
              bake_space_transform=False, axis_forward='-Z', axis_up='Y', path_mode='COPY', embed_textures=True,
              mesh_smooth_type='FACE', use_mesh_modifiers=False, add_leaf_bones=False,
              primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL',
              bake_anim=anim)
    if anim:
        kw.update(bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False,
                  bake_anim_use_all_actions=all_actions, bake_anim_force_startend_keying=True,
                  bake_anim_step=1.0, bake_anim_simplify_factor=0.0)
    bpy.ops.export_scene.fbx(**kw)


def export_glb(path, objs, anim=False):
    select_only(objs)
    kw = dict(filepath=path, export_format='GLB', use_selection=True, export_apply=False, export_yup=True,
              export_animations=anim)
    try:
        bpy.ops.export_scene.gltf(**kw)
    except TypeError:
        kw.pop('export_animations', None)
        bpy.ops.export_scene.gltf(**kw)


# ------------------------------------------------------------------ escena de comprobacion y render
def setup_world(color=(0.52, 0.56, 0.6), strength=0.9):
    w = bpy.context.scene.world
    nt = _nodes_clear(w)
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (*color, 1)
    bg.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def add_lights(coll, scale=1.0):
    sun = bpy.data.lights.new('Sol', 'SUN')
    sun.energy = 3.2
    sun.angle = math.radians(8)
    so = bpy.data.objects.new('Sol', sun)
    so.rotation_euler = Euler((math.radians(50), math.radians(10), math.radians(-35)))
    coll.objects.link(so)
    fill = bpy.data.lights.new('Relleno', 'SUN')
    fill.energy = 0.9
    fo = bpy.data.objects.new('Relleno', fill)
    fo.rotation_euler = Euler((math.radians(70), 0, math.radians(150)))
    coll.objects.link(fo)
    return [so, fo]


def camera(coll, name, loc, target, lens=50.0, ortho=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.02
    cd.clip_end = 2000
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho
    co = bpy.data.objects.new(name, cd)
    co.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    coll.objects.link(co)
    return co


def setup_render(res=(1280, 720), engine='EEVEE', samples=32):
    sc = bpy.context.scene
    if engine == 'EEVEE':
        for e in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
            try:
                sc.render.engine = e
                break
            except Exception:
                continue
        try:
            sc.eevee.taa_render_samples = samples
        except Exception:
            pass
    elif engine == 'WORKBENCH':
        sc.render.engine = 'BLENDER_WORKBENCH'
    else:
        sc.render.engine = 'CYCLES'
        sc.cycles.device = 'CPU'
        sc.cycles.samples = samples
        try:
            sc.cycles.use_denoising = True
        except Exception:
            pass
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'Standard'
        sc.view_settings.look = 'None'
    except Exception:
        pass


def render(path, cam):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    log('render', os.path.basename(path), '%.1fs' % (time.time() - t))


def flat_mat(name, rgb, rough=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = _nodes_clear(m)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    for k in ('Specular IOR Level', 'Specular'):
        if k in b.inputs:
            b.inputs[k].default_value = 0.1
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(b.outputs['BSDF'], o.inputs['Surface'])
    m.diffuse_color = (*rgb, 1)
    return m


def reference_figure(coll, x=0.0, y=0.0, h=5.2, name='Ref_R15'):
    """Maniqui gris tipo R15 (bloques) de altura h, con los pies en z=0."""
    k = h / 5.2
    gray = flat_mat('Ref_Gris', (0.55, 0.56, 0.58))
    dark = flat_mat('Ref_Oscuro', (0.33, 0.34, 0.36))
    parts = [
        ('Pierna_I', (-0.5, 0, 1.0), (0.95, 0.95, 2.0), dark), ('Pierna_D', (0.5, 0, 1.0), (0.95, 0.95, 2.0), dark),
        ('TorsoInf', (0, 0, 2.2), (1.95, 0.95, 0.4), dark), ('TorsoSup', (0, 0, 3.2), (1.95, 0.95, 1.6), gray),
        ('Brazo_I', (-1.5, 0, 3.0), (0.95, 0.95, 2.0), gray), ('Brazo_D', (1.5, 0, 3.0), (0.95, 0.95, 2.0), gray),
        ('Cabeza', (0, 0, 4.6), (1.2, 1.2, 1.2), gray),
    ]
    obs = []
    for (n, c, s, m) in parts:
        mb = MB(name + '_' + n)
        mb.box((c[0] * k + x, c[1] * k + y, c[2] * k), (s[0] * k, s[1] * k, s[2] * k), 'ref', bevel=0.06 * k)
        o = mb.finish(coll)
        o.data.materials.clear()
        o.data.materials.append(m)
        obs.append(o)
    return obs


def ruler(coll, x, y, h=6.0, w=0.25):
    """Regla de h studs con bandas de 1 stud alternas."""
    a = flat_mat('Regla_A', (0.85, 0.85, 0.82))
    b = flat_mat('Regla_B', (0.85, 0.25, 0.18))
    obs = []
    for i in range(int(h)):
        mb = MB('Regla_%d' % i)
        mb.box((x, y, i + 0.5), (w, w, 1.0), 'ref')
        o = mb.finish(coll)
        o.data.materials.clear()
        o.data.materials.append(a if i % 2 == 0 else b)
        obs.append(o)
    return obs


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
