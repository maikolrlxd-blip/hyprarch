# Utilidades comunes del arte de «+1 de lanzamiento por segundo» (Blender 5.2, sin interfaz).
# Se apoya en apocalipsis-arte/tools/ap_lib.py (geometria, horneado, pintura, rig, clips, render).
# Convencion de mis piezas: +Y delante, +Z arriba, +X derecha, 1 unidad = 1 stud; FBX con global_scale 0.01 y axis_forward='Z'
# (equivale al '-Z' de Codex porque sus modelos miran a -Y; ver COORDINACION.md).
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'apocalipsis-arte', 'tools'))
import ap_lib as A
import ap_armas as W
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Euler, Matrix

FBX_FORWARD = 'Z'


def lin(h):
    """#rrggbb (sRGB) -> color lineal para los materiales planos de los renders de geometria."""
    return tuple(float(v) ** 2.2 for v in A.hexrgb(h))


# ------------------------------------------------------------------ volumenes escalonados (voxeles) sobre una rejilla comun
# (direccion, esquinas (a,b,c) en medias celdas; el orden da la normal hacia fuera)
_CARAS = [
    ((1, 0, 0), [(1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)]),
    ((-1, 0, 0), [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]),
    ((0, 1, 0), [(-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)]),
    ((0, -1, 0), [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)]),
    ((0, 0, 1), [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]),
    ((0, 0, -1), [(-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1)]),
]


class Vox:
    """Union de volumenes de celdas cubicas de lado `cell` en una sola rejilla: solo se crean las caras expuestas de la piel.
    Cada celda recuerda su hueso y su region (texto, o funcion f(centro_de_celda, normal) -> region para pintar por zonas)."""

    def __init__(self, cell, origin=(0.0, 0.0, 0.0)):
        self.cell = cell
        self.o = Vector(origin)
        self.cells = {}

    def idx(self, p):
        return tuple(int(round((p[a] - self.o[a]) / self.cell)) for a in range(3))

    def pos(self, ijk):
        return Vector([self.o[a] + ijk[a] * self.cell for a in range(3)])

    def _rango(self, c, r):
        ci = self.idx(c)
        n = [int(math.ceil(r[a] / self.cell)) + 1 for a in range(3)]
        return [range(ci[a] - n[a], ci[a] + n[a] + 1) for a in range(3)]

    def elipsoide(self, c, r, bone, mat, exp=2.0, cortar=None):
        """Celdas cuyo centro cae dentro del elipsoide (exp > 2 lo vuelve mas cuadrado, como los cuerpos de Codex)."""
        c = Vector(c)
        for i in self._rango(c, r)[0]:
            for j in self._rango(c, r)[1]:
                for k in self._rango(c, r)[2]:
                    p = self.pos((i, j, k))
                    if sum((abs(p[a] - c[a]) / r[a]) ** exp for a in range(3)) <= 1.0 and (cortar is None or cortar(p)):
                        self.cells[(i, j, k)] = (bone, mat)

    def caja(self, c, size, bone, mat):
        lo = [c[a] - size[a] / 2 for a in range(3)]
        hi = [c[a] + size[a] / 2 for a in range(3)]
        a0 = self.idx(lo)
        a1 = self.idx(hi)
        for i in range(a0[0], a1[0] + 1):
            for j in range(a0[1], a1[1] + 1):
                for k in range(a0[2], a1[2] + 1):
                    p = self.pos((i, j, k))
                    if all(lo[a] - 1e-6 <= p[a] <= hi[a] + 1e-6 for a in range(3)):
                        self.cells[(i, j, k)] = (bone, mat)

    def borrar_caja(self, c, size):
        lo = [c[a] - size[a] / 2 for a in range(3)]
        hi = [c[a] + size[a] / 2 for a in range(3)]
        for ijk in list(self.cells):
            p = self.pos(ijk)
            if all(lo[a] <= p[a] <= hi[a] for a in range(3)):
                del self.cells[ijk]

    def pintar_caja(self, c, size, mat, solo_hueso=None):
        """Cambia la region de las celdas ya creadas dentro de la caja (marcas, parches)."""
        lo = [c[a] - size[a] / 2 for a in range(3)]
        hi = [c[a] + size[a] / 2 for a in range(3)]
        for ijk, (b, m) in list(self.cells.items()):
            p = self.pos(ijk)
            if all(lo[a] <= p[a] <= hi[a] for a in range(3)) and (solo_hueso is None or b == solo_hueso):
                self.cells[ijk] = (b, mat)

    def construir(self, mbs, disolver=True):
        """Crea las caras expuestas en el MB de cada hueso (mbs: {hueso: A.MB}). Si disolver, une las caras coplanares contiguas
        de una misma region (menos triangulos, mismo aspecto escalonado)."""
        vc = {}
        h = self.cell / 2
        n_mal = 0
        for ijk, (bone, mat) in self.cells.items():
            mb = mbs[bone]
            p = self.pos(ijk)
            for d, esquinas in _CARAS:
                vecino = self.cells.get((ijk[0] + d[0], ijk[1] + d[1], ijk[2] + d[2]))
                if vecino is not None and vecino[0] == bone:
                    continue            # solo se descarta entre celdas del mismo hueso: cada hueso conserva su piel cerrada y, al girar
                                        # la cabeza o la cola, la union no se abre (Roblox no dibuja las caras traseras)
                region = mat(p, Vector(d)) if callable(mat) else mat
                vs = []
                for (a, b, c3) in esquinas:
                    key = (id(mb), 2 * ijk[0] + a, 2 * ijk[1] + b, 2 * ijk[2] + c3)
                    v = vc.get(key)
                    if v is None:
                        v = mb.bm.verts.new(self.o + Vector((key[1], key[2], key[3])) * h)
                        vc[key] = v
                    vs.append(v)
                f = mb.face(vs, region)
                f.normal_update()
                if f.normal.dot(Vector(d)) <= 0:
                    n_mal += 1
        if n_mal:
            raise RuntimeError('caras con la normal hacia dentro: %d' % n_mal)
        if disolver:
            for mb in mbs.values():
                if mb.bm.faces:
                    bmesh.ops.dissolve_limit(mb.bm, angle_limit=math.radians(1.0), verts=mb.bm.verts[:], edges=mb.bm.edges[:],
                                             delimit={'MATERIAL'})


# ------------------------------------------------------------------ piezas sueltas (bloques, losas) en el MB de un hueso
def bloque(mb, c, size, mat, bevel=0.0):
    mb.box(c, size, mat, bevel=bevel)


def losa(mb, poly, z0, z1, mat, side_mat=None):
    """Poligono (x, y) extruido en z: plumas planas y gruesas con la punta cuadrada, como las alas de las mascotas de Codex."""
    mb.prism(poly, z0, z1, mat, plane='XY', side_mat=side_mat)


# ------------------------------------------------------------------ armado comun: rig, piel rigida por hueso, union en una malla
def armar(nombre, mbs, huesos, coll, escala=1.0):
    """mbs: {hueso: MB}; huesos: [(nombre, cabeza, padre, largo)]. Devuelve (objeto unico, rig)."""
    rig = A.make_armature(nombre + '_Rig', huesos, coll)
    partes = []
    for bone, mb in mbs.items():
        if not mb.bm.faces:
            mb.bm.free()
            continue
        o = mb.finish(coll)
        A.skin_rigid(o, rig, bone)
        partes.append(o)
    A.select_only(partes)
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = nombre
    ob.data.name = nombre
    if escala != 1.0:
        ob.data.transform(Matrix.Scale(escala, 4))
        ob.data.update()
    return ob, rig


# ------------------------------------------------------------------ exportacion
def fbx(path, objs, anim):
    A.select_only(objs)
    kw = dict(filepath=path, use_selection=True, object_types={'MESH', 'ARMATURE', 'EMPTY'}, global_scale=0.01,
              apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True, bake_space_transform=False, axis_forward=FBX_FORWARD,
              axis_up='Y', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', use_mesh_modifiers=False,
              add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL', bake_anim=anim)
    if anim:
        kw.update(bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False,
                  bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0)
    bpy.ops.export_scene.fbx(**kw)


def glb_con_clips(path, ob, rig, acts):
    rig.animation_data_clear()
    ad = rig.animation_data_create()
    for nombre, act in acts.items():
        tr = ad.nla_tracks.new()
        tr.name = nombre
        tr.strips.new(nombre, 1, act)
    A.select_only([ob, rig])
    try:
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True,
                                  export_animations=True, export_animation_mode='NLA_TRACKS')
    except TypeError:
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_animations=True)


def a_jpg(png, jpg, escala=0.5):
    im = bpy.data.images.load(png, check_existing=False)
    im.scale(int(im.size[0] * escala), int(im.size[1] * escala))
    im.filepath_raw = jpg
    im.file_format = 'JPEG'
    im.save()
    bpy.data.images.remove(im)
    os.remove(png)


def sol(coll, name, energy, direction, angle=6.0):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy = energy
    ld.angle = math.radians(angle)
    lo = bpy.data.objects.new(name, ld)
    lo.rotation_euler = Vector(direction).normalized().to_track_quat('-Z', 'Y').to_euler()
    coll.objects.link(lo)
