# Exporta el FBX del rig (malla + huesos, pose del .blend, sin clips) de cualquier pieza con huesos, con la regla de ejes probada en
# Studio el 30/10 (pruebas-studio/2026-10-30-ejes/LEEME.md): bake_space_transform=True y axis_forward según hacia dónde mire la pieza
# en Blender, para que en Roblox mire a -Z (el frente de los personajes). Sirve para las piezas de Codex (frente -Y) sin tocar su
# carpeta: lee su .blend y escribe en SALIDA. El frente se deduce así: mascotas, los párpados (Lid_R) respecto al cuerpo o, si no hay,
# la cabeza respecto a la cola; alas, el lado contrario a donde queda la malla (las alas cuelgan por detrás de la espalda). Con
# FRENTE=+Y o FRENTE=-Y se da a mano (piezas que no son mascotas ni alas, como el cañón).
#   BLEND=<ruta .blend> SALIDA=<archivo .fbx> [FRENTE=+Y|-Y] blender -b --factory-startup --python-exit-code 1 -P exportar_rig_roblox.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *

bpy.ops.wm.open_mainfile(filepath=os.environ['BLEND'], load_ui=False)
SALIDA = os.environ['SALIDA']
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mallas = [o for o in bpy.data.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == rig for m in o.modifiers)]
rig.animation_data_clear()                     # la pose que guarda el .blend, sin acción ni NLA
bpy.context.view_layer.update()
huesos = {b.name: rig.matrix_world @ b.head_local for b in rig.data.bones}
centro = huesos.get('Body', huesos['Root'])
if os.environ.get('FRENTE') in ('+Y', '-Y'):   # piezas sin cara ni alas (el cañón de Codex apunta a +Y): el frente se da a mano
    frente_y = 1 if os.environ['FRENTE'] == '+Y' else -1
    criterio = 'FRENTE dado a mano'
elif 'Lid_R' in huesos:                        # los párpados están delante de los ojos: el frente seguro de cualquier mascota
    frente_y = 1 if huesos['Lid_R'].y > centro.y else -1
    criterio = 'párpados respecto al cuerpo'
elif 'Head' in huesos and 'Tail' in huesos:
    frente_y = 1 if huesos['Head'].y > huesos['Tail'].y else -1
    criterio = 'cabeza respecto a la cola'
else:
    ys = [(o.matrix_world @ v.co).y for o in mallas for v in o.data.vertices]
    frente_y = -1 if sum(ys) / len(ys) > huesos['Root'].y else 1
    criterio = 'alas: la malla queda detrás'
eje = 'Z' if frente_y > 0 else '-Z'            # con bake: +Y de Blender -> -Z de Roblox con 'Z'
A.select_only(mallas + [rig])
os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=SALIDA, use_selection=True, object_types={'MESH', 'ARMATURE', 'EMPTY'}, global_scale=0.01,
                         apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True, bake_space_transform=True, axis_forward=eje,
                         axis_up='Y', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', use_mesh_modifiers=False,
                         add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL', bake_anim=False)
A.log('RIG', os.path.basename(SALIDA), 'frente', '+Y' if frente_y > 0 else '-Y', '(' + criterio + ')', 'eje', eje, 'mallas', len(mallas))
