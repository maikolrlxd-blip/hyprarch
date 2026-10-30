# Fila con los enemigos voladores v02 (todos en voxel) juntos, por zonas (globo, nube gruñona, nubarrón, cometa, ovni y meteorito, de izquierda a
# derecha vistos de frente) en la misma escena y luz: en reposo (Idle) y golpeados (Hit). Carga cada enemigo de su .blend (malla + rig
# con sus clips).
# blender -b --factory-startup --python-exit-code 1 -P hoja_enemigos.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_pet import *

D = os.path.abspath(os.path.join(HERE, '..', 'enemigos-v02'))
PIEZAS = (('globo', 'GloboGrunon'), ('nube-grunona', 'NubeGrunona'), ('nubarron', 'NubarronTormenta'), ('cometa', 'CometaEnfadada'),
          ('ovni', 'OvniEnfadado'), ('meteorito', 'MeteoritoFurioso'))
A.clean_scene()
bpy.context.scene.render.fps = 30
CR, CC, CM = A.collection('Ref'), A.collection('Camaras'), A.collection('Enemigos')
PREV = os.path.join(D, '_fila')
os.makedirs(PREV, exist_ok=True)
E = Escena(CR, CC, PREV, 'full', radio=20.0, maniqui=(15.0, -1.6), regla=(-15.0, -1.2), objetivo=(0.0, 0.0, 2.0))
E.res = (2000, 760)
E.reiniciar_render()

rigs = []
n = len(PIEZAS)
for i, (sub, nombre) in enumerate(PIEZAS):
    with bpy.data.libraries.load(os.path.join(D, sub, nombre + '.blend'), link=False) as (src, dst):
        dst.objects = [o for o in src.objects if o in (nombre, nombre + '_Rig')]
    for o in dst.objects:
        CM.objects.link(o)
        if o.type == 'ARMATURE':
            o.location = (((n - 1) / 2.0 - i) * 5.0, 0.0, 0.0)          # vista de frente (+Y) el +X queda a la izquierda
            rigs.append(o)
    for img in bpy.data.images:                                       # las texturas del .blend apuntan a su carpeta: se resuelven aquí
        if img.source == 'FILE' and not os.path.exists(bpy.path.abspath(img.filepath)):
            cand = os.path.join(D, sub, 'texturas', os.path.basename(img.filepath))
            if os.path.exists(cand):
                img.filepath = cand
                img.reload()


def poner(clip, t):
    for rig in rigs:
        A.set_action(rig, rig.animation_data.nla_tracks[clip].strips[0].action)
    bpy.context.scene.frame_set(int(round(t * 30)))
    bpy.context.view_layer.update()


items = []
poner('Idle', 0.0)
items.append((E.foto('Enemigos-fila-reposo', 178, 8, 42.0, target=(1.2, 0.0, 2.2)), 'REPOSO (IDLE): GLOBO - NUBE GRUNONA - NUBARRON - COMETA - OVNI - METEORITO'))
poner('Hit', 0.07)
items.append((E.foto('Enemigos-fila-golpe', 166, 12, 42.0, target=(1.2, 0.0, 2.2)), 'GOLPEADOS (HIT) - CIERRAN LOS OJOS Y SALEN HACIA ATRAS'))
W.contact_sheet(items, 1, os.path.join(D, '_fila.png'), title='ENEMIGOS VOLADORES V02 (VOXEL) - DE LA PRADERA AL ESPACIO - RENDERS DE BLENDER (SIN PROBAR EN ROBLOX)')
a_jpg(os.path.join(D, '_fila.png'), os.path.join(D, 'Enemigos-v02-hoja.jpg'), 0.6)
print('HOJA LISTA')
