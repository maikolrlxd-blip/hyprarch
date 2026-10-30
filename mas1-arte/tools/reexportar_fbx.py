# Reexporta los FBX (rig + un FBX por clip) de una pieza con huesos ya construida, desde su .blend, con la regla de ejes probada en
# Studio el 30/10 (mas1-arte/pruebas-studio/2026-10-30-ejes/): sin bake_space_transform el 3D Importer mete el esqueleto girado 90°
# (cabeceo) y la mascota/ala sale tumbada; con bake_space_transform=True y axis_forward 'Z' sale como en Blender, mirando al frente
# (-Z de Roblox), y los clips se reproducen bien. La regla vive en mas1_lib.fbx(); este script solo la aplica a lo ya exportado.
# No toca el .blend, el GLB ni los renders; apunta la regla en 'ejes' de datos.json cuando escribe en la carpeta de la pieza
# (validar_asset.py lee el eje de ahí).
#   PIEZA=mascotas-altas-v02/aguila-legendaria NOMBRE=AguilaLegendaria [SALIDA=<carpeta>] \
#   blender -b --factory-startup --python-exit-code 1 -P reexportar_fbx.py
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *

ARTE = os.path.abspath(os.path.join(HERE, '..'))
D = os.path.join(ARTE, os.environ['PIEZA'])
NOMBRE = os.environ['NOMBRE']
SALIDA = os.path.abspath(os.environ.get('SALIDA') or D)

bpy.ops.wm.open_mainfile(filepath=os.path.join(D, NOMBRE + '.blend'))
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mallas = [o for o in bpy.data.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == rig for m in o.modifiers)]
ob = next((o for o in mallas if o.name == NOMBRE), None) or next(o for o in mallas if 'Contorno' not in o.name)
# el .blend guarda la pose neutra y los clips en pistas NLA silenciadas (una por clip, con su nombre)
clips = {tr.name: tr.strips[0].action for tr in rig.animation_data.nla_tracks if tr.strips} if rig.animation_data else {}
previos = sorted(f[len(NOMBRE) + 1:-4] for f in os.listdir(os.path.join(D, 'clips')) if f.startswith(NOMBRE + '_') and f.endswith('.fbx'))
assert sorted(clips) == previos, ('los clips del .blend no son los exportados', sorted(clips), previos)

os.makedirs(os.path.join(SALIDA, 'clips'), exist_ok=True)
rig.animation_data_clear()                     # como al construir: sin acción ni NLA, con la pose neutra que guarda el .blend
fbx(os.path.join(SALIDA, NOMBRE + '_Rig.fbx'), [ob, rig], False)
for c, act in clips.items():
    A.set_action(rig, act)
    fbx(os.path.join(SALIDA, 'clips', '%s_%s.fbx' % (NOMBRE, c)), [ob, rig], True, todos_huesos=(c != 'Blink'))

if SALIDA == os.path.abspath(D):
    ruta = os.path.join(D, 'datos.json')
    txt = open(ruta, encoding='utf-8').read()
    txt = re.sub(r' bake_space_transform=\S+', '', txt)
    txt = re.sub(r'axis_forward=\S+ axis_up=Y', 'axis_forward=%s axis_up=Y bake_space_transform=True' % FBX_FORWARD, txt)
    open(ruta, 'w', encoding='utf-8').write(txt)
A.log('REEXPORTADO', NOMBRE, 'eje', FBX_FORWARD, 'malla', ob.name, 'clips', sorted(clips), '->', SALIDA)
