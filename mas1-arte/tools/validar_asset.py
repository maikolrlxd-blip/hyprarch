# Reimporta los FBX/GLB de una pieza del proyecto +1 y comprueba geometria, huesos, pesos, UV, textura y movimiento de cada clip.
#   ASSET_DIR=alas-avanzadas-v02 ASSET_NAME=AlasAvanzadas_v02 ASSET_CLIPS=Deploy,Flap,Glide ASSET_LOOPS=Flap,Glide \
#   blender -b --factory-startup --python-exit-code 1 -P validar_asset.py
# Espera <dir>/datos.json (triangulos, huesos, ejes), <NAME>_Rig.fbx, clips/<NAME>_<Clip>.fbx y <NAME>.glb; escribe <dir>/VALIDACION.json.
import sys, os, json, math
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HERE, '..', os.environ['ASSET_DIR']))
NAME = os.environ['ASSET_NAME']
CLIPS = os.environ['ASSET_CLIPS'].split(',')
LOOPS = [c for c in os.environ.get('ASSET_LOOPS', '').split(',') if c]
datos = json.load(open(os.path.join(D, 'datos.json'), encoding='utf-8'))
EJE = datos['ejes'].split('axis_forward=')[1].split()[0]
informe = {'archivos': {}, 'fallos': []}


def fallo(msg):
    informe['fallos'].append(msg)


def limpio():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def revisar_fbx(ruta, clip):
    base = os.path.basename(ruta)
    limpio()
    bpy.ops.import_scene.fbx(filepath=ruta, axis_forward=EJE, axis_up='Y')
    r = {}
    mallas = [o for o in bpy.data.objects if o.type == 'MESH']
    rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    r['mallas'], r['armaduras'] = len(mallas), len(rigs)
    if len(mallas) != 1 or len(rigs) != 1:
        fallo('%s: %d mallas y %d armaduras (se esperaba 1 y 1)' % (base, len(mallas), len(rigs)))
        informe['archivos'][base] = r
        return
    m = mallas[0]
    r['triangulos'] = sum(len(p.vertices) - 2 for p in m.data.polygons)
    if r['triangulos'] != datos['triangulos']:
        fallo('%s: %d triangulos, esperados %d' % (base, r['triangulos'], datos['triangulos']))
    r['materiales'] = len(m.data.materials)
    r['uv'] = [u.name for u in m.data.uv_layers]
    imgs = [i for i in bpy.data.images if i.size[0] > 0]
    r['texturas'] = [(i.name, tuple(i.size)) for i in imgs]
    if not imgs or max(i.size[0] for i in imgs) != 1024:
        fallo('%s: la textura 1024 no llega incrustada' % base)
    huesos = [b.name for b in rigs[0].data.bones]
    r['huesos'] = huesos
    if sorted(huesos) != sorted(datos['huesos']):
        fallo('%s: huesos %s' % (base, huesos))
    sin_peso = multiples = 0
    for v in m.data.vertices:
        n = len([g for g in v.groups if g.weight > 0.001])
        sin_peso += (n == 0)
        multiples += (n > 1)
    r['vertices'], r['vertices_sin_peso'], r['vertices_con_varios_huesos'] = len(m.data.vertices), sin_peso, multiples
    if sin_peso:
        fallo('%s: %d vertices sin peso' % (base, sin_peso))
    mn = Vector([min((m.matrix_world @ v.co)[a] for v in m.data.vertices) for a in range(3)])
    mx = Vector([max((m.matrix_world @ v.co)[a] for v in m.data.vertices) for a in range(3)])
    r['caja_importada'] = [round(mx[a] - mn[a], 4) for a in range(3)]
    if clip:
        r['acciones'] = []
        for act in bpy.data.actions:
            fcs = []
            try:
                fcs = list(act.fcurves)
            except Exception:
                from bpy_extras import anim_utils
                for slot in act.slots:
                    cb = anim_utils.action_get_channelbag_for_slot(act, slot)
                    if cb:
                        fcs += list(cb.fcurves)
            rot = [fc for fc in fcs if 'rotation' in fc.data_path or 'location' in fc.data_path]   # el parpadeo (Blink) solo mueve huesos
            f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
            mov = cierre = 0.0
            quats = {}
            for fc in rot:
                vals = [fc.evaluate(f) for f in range(f0, f1 + 1)]
                mov = max(mov, max(vals) - min(vals))
                if fc.data_path.endswith('rotation_quaternion'):
                    quats.setdefault(fc.data_path, {})[fc.array_index] = (vals[0], vals[-1])
                    continue
                d = abs(vals[0] - vals[-1])
                if 'rotation_euler' in fc.data_path:
                    d = d % (2 * math.pi)
                    d = min(d, 2 * math.pi - d)                    # 0 y 360 grados son el mismo giro
                cierre = max(cierre, d)
            for comps in quats.values():                           # q y -q son la misma orientacion (una vuelta entera cambia el signo)
                q0 = [comps.get(i, (0.0, 0.0))[0] for i in range(4)]
                q1 = [comps.get(i, (0.0, 0.0))[1] for i in range(4)]
                cierre = max(cierre, min(max(abs(a - b) for a, b in zip(q0, q1)), max(abs(a + b) for a, b in zip(q0, q1))))
            esperado = int(round(datos['clips_30fps'][clip]['duracion_s'] * 30)) + 1
            # envergadura (extension en X) de la malla deformada en cada fotograma, en studs (el FBX va a escala 0.01): razon plegada/extendida
            spans = []
            for f in range(f0, f1 + 1, 2):
                bpy.context.scene.frame_set(f)
                e = m.evaluated_get(bpy.context.evaluated_depsgraph_get())
                me = e.to_mesh()
                xs = [(e.matrix_world @ v.co).x for v in me.vertices]
                e.to_mesh_clear()
                spans.append((max(xs) - min(xs)) * 100.0)
            r['acciones'].append({'nombre': act.name, 'frames': [f0, f1], 'curvas_de_rotacion': len(rot), 'mov_max_rad': round(mov, 3),
                                  'diferencia_primer_ultimo': round(cierre, 4), 'envergadura_studs': [round(min(spans), 2), round(max(spans), 2)],
                                  'razon_plegada_extendida': round(min(spans) / max(spans), 3)})
            if f1 - f0 + 1 != esperado:
                fallo('%s: %d fotogramas, esperados %d' % (base, f1 - f0 + 1, esperado))
            if mov < 0.05:
                fallo('%s: la accion casi no se mueve' % base)
            if clip in LOOPS and cierre > 0.01:
                fallo('%s: el bucle no cierra (diferencia %.3f rad entre el primer y el ultimo fotograma)' % (base, cierre))
    informe['archivos'][base] = r


revisar_fbx(os.path.join(D, NAME + '_Rig.fbx'), None)
for c in CLIPS:
    revisar_fbx(os.path.join(D, 'clips', '%s_%s.fbx' % (NAME, c)), c)
if 'contorno' in datos:
    # variante con contorno: misma malla mas la carcasa (el doble de poligonos), los mismos huesos y ningun vertice sin peso
    limpio()
    ruta = os.path.join(D, datos['contorno']['archivo'])
    bpy.ops.import_scene.fbx(filepath=ruta, axis_forward=EJE, axis_up='Y')
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    rs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    c = {'mallas': len(ms), 'armaduras': len(rs)}
    if len(ms) == 1 and len(rs) == 1:
        m = ms[0]
        c['triangulos'] = sum(len(p.vertices) - 2 for p in m.data.polygons)
        c['huesos'] = sorted(b.name for b in rs[0].data.bones)
        c['vertices_sin_peso'] = sum(1 for v in m.data.vertices if not [g for g in v.groups if g.weight > 0.001])
        c['texturas'] = [(i.name, tuple(i.size)) for i in bpy.data.images if i.size[0] > 0]
        if c['triangulos'] != datos['contorno']['poligonos_con_contorno']:
            fallo('%s: %d triangulos, esperados %d' % (datos['contorno']['archivo'], c['triangulos'], datos['contorno']['poligonos_con_contorno']))
        if c['vertices_sin_peso']:
            fallo('%s: %d vertices de la carcasa sin peso' % (datos['contorno']['archivo'], c['vertices_sin_peso']))
        if c['huesos'] != sorted(datos['huesos']):
            fallo('%s: huesos %s' % (datos['contorno']['archivo'], c['huesos']))
        if not c['texturas'] or max(t[1][0] for t in c['texturas']) != 1024:
            fallo('%s: la textura 1024 no llega incrustada' % datos['contorno']['archivo'])
    else:
        fallo('%s: %d mallas y %d armaduras' % (datos['contorno']['archivo'], len(ms), len(rs)))
    informe['archivos'][datos['contorno']['archivo']] = c
limpio()
bpy.ops.import_scene.gltf(filepath=os.path.join(D, NAME + '.glb'))
mallas = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'Icosphere']      # Icosphere = forma de hueso que anade el importador
g = {'mallas': [(o.name, sum(len(p.vertices) - 2 for p in o.data.polygons)) for o in mallas],
     'armaduras': len([o for o in bpy.data.objects if o.type == 'ARMATURE']), 'acciones': sorted(a.name for a in bpy.data.actions)}
informe['archivos'][NAME + '.glb'] = g
if len(mallas) != 1:
    fallo('GLB: %d mallas' % len(mallas))
for c in CLIPS:
    if not any(c in a for a in g['acciones']):
        fallo('GLB: falta la animacion %s' % c)
informe['correcto'] = not informe['fallos']
json.dump(informe, open(os.path.join(D, 'VALIDACION.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('VALIDACION', 'CORRECTA' if informe['correcto'] else 'CON FALLOS', informe['fallos'])
