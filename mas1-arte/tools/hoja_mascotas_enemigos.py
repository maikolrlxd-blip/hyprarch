# Fila con las seis mascotas de enemigos (versión amable) juntas, por rareza (nube, globo, nubarrón, ovni, meteorito y cometa, de izquierda a
# derecha vistos de frente) en la misma escena y luz: volando (Fly) y celebrando (Celebrate). Carga cada mascota de su .blend (malla + rig
# con sus clips).
# blender -b --factory-startup --python-exit-code 1 -P hoja_mascotas_enemigos.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_pet import *

D = os.path.abspath(os.path.join(HERE, '..', 'mascotas-enemigos-v01'))
PIEZAS = (('nube', 'MascotaNube'), ('globo', 'MascotaGlobo'), ('nubarron', 'MascotaNubarron'), ('ovni', 'MascotaOvni'),
          ('meteorito', 'MascotaMeteorito'), ('cometa', 'MascotaCometa'))
A.clean_scene()
bpy.context.scene.render.fps = 30
CR, CC, CM = A.collection('Ref'), A.collection('Camaras'), A.collection('Mascotas')
PREV = os.path.join(D, '_fila')
os.makedirs(PREV, exist_ok=True)
E = Escena(CR, CC, PREV, 'full', radio=16.0, maniqui=(13.0, -1.6), regla=(-12.0, -1.2), objetivo=(0.0, 0.0, 1.6))
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
            o.location = (((n - 1) / 2.0 - i) * 3.8, 0.0, 0.0)          # vista de frente (+Y) el +X queda a la izquierda
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
poner('Fly', 0.25)
items.append((E.foto('Mascotas-fila-vuelo', 178, 8, 40.0, target=(1.8, 0.0, 1.7)), 'VOLANDO (FLY): NUBE Y GLOBO (POCO COMUNES) - NUBARRON Y OVNI (RAROS) - METEORITO Y COMETA (EPICOS)'))
poner('Celebrate', 0.85)
items.append((E.foto('Mascotas-fila-celebra', 166, 12, 40.0, target=(1.8, 0.0, 1.9)), 'CELEBRAN (CELEBRATE) - SALTAN CON UNA VUELTA ENTERA Y LOS OJOS ENTORNADOS'))
W.contact_sheet(items, 1, os.path.join(D, '_fila.png'), title='MASCOTAS DE ENEMIGOS V01 (VERSION AMABLE) - SALEN DE LOS HUEVOS ALADOS - RENDERS DE BLENDER (SIN PROBAR EN ROBLOX)')
a_jpg(os.path.join(D, '_fila.png'), os.path.join(D, 'Mascotas-enemigos-v01-hoja.jpg'), 0.6)
print('HOJA LISTA')
