# Cadena comun para las piezas del mapa: cada pieza = UN objeto con su origen en el centro de la base,
# geometria facetada -> UV -> horneado -> pintura a mano (numpy) -> FBX/GLB individual + vista previa a escala.
import os, math, json
import numpy as np
import bpy
from mathutils import Vector, Matrix
import ap_lib as A
import ap_armas as W

FAR = 4000.0


class Cat:
    def __init__(self, name, out_dir, styles, extras=None):
        self.name = name
        self.out = out_dir
        self.styles = styles
        self.extras = extras or {}
        self.pieces = []          # [(nombre, objeto, info)]
        for d in ('', 'texturas', 'previews', 'fbx'):
            os.makedirs(os.path.join(out_dir, d), exist_ok=True)
        A.clean_scene()
        self.C = A.collection('Piezas_' + name)
        self.CR = A.collection('Ref_' + name)
        self.CC = A.collection('Camaras_' + name)
        A.setup_world((0.52, 0.56, 0.60), 0.9)
        A.add_lights(self.CC)

    def piece(self, name, builder, size=1024, R=None, ao_dist=0.6, bevel_r=0.06, samples=14, extra=None, uvw=None, angle=56,
              margin=0.004, ref=None):
        """builder(coleccion) -> objeto terminado (MB.finish). Se crea en el origen con la base centrada en (0,0,0).
        ref: donde poner el maniqui de escala en la vista previa (encima de la pieza, p. ej. en la acera); si no, al lado."""
        A.REGIONS.clear()
        ob = builder(self.C)
        ob.name = name
        ob.location = (0, 0, 0)
        A.uv_unwrap([ob], angle=angle, margin=margin, weights=uvw)
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        rr = R or max(max(abs(v.x), abs(v.y), abs(v.z)) for v in bb) * 1.05 + 0.5
        rp = bpy.data.objects.new('RefPos', None)
        self.C.objects.link(rp)
        maps = A.bake_maps([ob], size, R=rr, ao_dist=ao_dist, bevel_r=bevel_r, samples=samples, pos_ref=rp)
        bpy.data.objects.remove(rp, do_unlink=True)
        P = A.Paint(maps, R=rr, light=(-0.30, 0.35, 0.89))
        for reg in list(A.REGIONS):
            st = dict(self.styles.get(reg, dict(base='#808080')))
            base = st.pop('base')
            ex = (extra or {}).get(reg) or self.extras.get(reg)
            if ex is not None:
                st['extra'] = ex
            P.region(reg, base, **st)
        tex = os.path.join(self.out, 'texturas', name + '_Color.png')
        P.save(tex, size)
        mat = A.final_material('M_' + name, tex)
        A.assign_final([ob], mat)
        mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
        mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
        info = dict(tris=A.tris([ob]), dims=[round(v, 2) for v in (mx - mn)], tex=size, regiones=list(A.REGIONS))
        if ref is not None:
            info['ref'] = list(ref)
        A.export_fbx(os.path.join(self.out, 'fbx', name + '.fbx'), [ob])
        A.export_glb(os.path.join(self.out, 'fbx', name + '.glb'), [ob])
        ob.location = (FAR * (len(self.pieces) + 1), 0, 0)      # apartarla para que no afecte a la oclusion de las siguientes
        bpy.context.view_layer.update()
        self.pieces.append((name, ob, info))
        A.log('pieza', name, info['tris'], 'tris', info['dims'])
        return ob

    def previews(self, res=(960, 540), samples=24, dist_k=None):
        """Una vista 3/4 por pieza con maniqui R15 de 5,2 studs y regla de 6, mas una hoja de contacto.
        El encuadre envuelve pieza + maniqui (nada cortado) y el suelo queda por debajo de la pieza (sin pelear con ella)."""
        A.setup_render(res, 'CYCLES', samples)
        figs = A.reference_figure(self.CR, 0, 0, 5.2)
        rul = A.ruler(self.CR, 0, 0, 6)
        gr = W.backdrop(self.CR, 0.0, 600.0, (0.40, 0.42, 0.40))
        half_v = math.atan(36.0 * res[1] / res[0] / 2 / 50.0)       # medio campo vertical con objetivo de 50 mm
        dv = Vector((0.9, -1.0, 0.45)).normalized()
        items = []
        for (name, ob, info) in self.pieces:
            home = ob.location.copy()
            ob.location = (0, 0, 0)
            bpy.context.view_layer.update()
            bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
            mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
            mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
            if 'ref' in info:
                off = Vector(info['ref'])
            else:
                off = Vector((mx.x + 2.2, mn.y + 3.0 if (mx.y - mn.y) > 8 else 0.0, 0.0))
            for o in figs:
                o.location = off
            for o in rul:
                o.location = off + Vector((2.6, 0.2, 0))
            gr.location.z = min(0.0, mn.z) - 0.02
            bpy.context.view_layer.update()
            cmn = Vector((min(mn.x, off.x - 1.0), min(mn.y, off.y - 0.6), min(mn.z, off.z)))
            cmx = Vector((max(mx.x, off.x + 2.9), max(mx.y, off.y + 0.8), max(mx.z, off.z + 6.0)))
            r = (cmx - cmn).length / 2
            cam = W.look_cam(self.CC, 'Cam_' + name, (cmn + cmx) / 2, dv, r / math.sin(half_v) * 0.92, 50)
            for (n2, o2, _) in self.pieces:
                o2.hide_render = (n2 != name)
            p = os.path.join(self.out, 'previews', name + '.png')
            A.render(p, cam)
            items.append((p, name))
            ob.location = home
            bpy.data.objects.remove(cam, do_unlink=True)
        for (n2, o2, _) in self.pieces:
            o2.hide_render = False
        for f in list(self.CR.objects):
            bpy.data.objects.remove(f, do_unlink=True)
        cols = 3 if len(items) > 4 else 2
        W.contact_sheet(items, cols, os.path.join(self.out, 'previews', '_hoja_' + self.name + '.png'),
                        title='%s - piezas a escala (maniqui R15 5,2 studs y regla de 6)' % self.name)
        return items

    def finish(self):
        A.save_blend(os.path.join(self.out, self.name + '.blend'))
        A.write_json(os.path.join(self.out, 'datos.json'), {n: i for (n, o, i) in self.pieces})
