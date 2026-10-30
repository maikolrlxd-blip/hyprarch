# Fila con los seis huevos alados v03 juntos (de común a mítico, de izquierda a derecha vistos de frente) en la misma escena y luz:
# cerrados, volando (alas arriba) y abiertos (Hatch al segundo 1,0). Carga cada huevo de su .blend (malla + rig con sus clips).
# blender -b --factory-startup --python-exit-code 1 -P hoja_huevos_alados.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_pet import *

D = os.path.abspath(os.path.join(HERE, '..', 'huevos-alados-v03'))
PIEZAS = (('comun', 'HuevoAladoComun'), ('poco-comun', 'HuevoAladoPocoComun'), ('raro', 'HuevoAladoRaro'), ('epico', 'HuevoAladoEpico'),
          ('legendario', 'HuevoAladoLegendario'), ('mitico', 'HuevoAladoMitico'))
A.clean_scene()
bpy.context.scene.render.fps = 30
CR, CC, CM = A.collection('Ref'), A.collection('Camaras'), A.collection('Huevos')
PREV = os.path.join(D, '_fila')
os.makedirs(PREV, exist_ok=True)
E = Escena(CR, CC, PREV, 'full', radio=22.0, maniqui=(21.0, -1.6), regla=(-18.0, -1.2), objetivo=(0.0, 0.0, 1.6))
E.res = (2000, 760)
E.reiniciar_render()

rigs = []
for i, (sub, nombre) in enumerate(PIEZAS):
    with bpy.data.libraries.load(os.path.join(D, sub, nombre + '.blend'), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in (nombre, nombre + '_Rig')]
    for o in dst.objects:
        CM.objects.link(o)
        if o.type == 'ARMATURE':
            o.location = ((2.5 - i) * 6.6, -0.4 * abs(i - 2.5), 0.0)   # vista de frente (+Y) el +X queda a la izquierda: común a la izquierda
            rigs.append(o)
    for img in bpy.data.images:                                       # las texturas del .blend apuntan a su carpeta: se resuelven aquí
        if img.source == 'FILE' and not os.path.exists(bpy.path.abspath(img.filepath)):
            cand = os.path.join(D, sub, 'texturas', os.path.basename(img.filepath))
            if os.path.exists(cand):
                img.filepath = cand
                img.reload()


def poner(clip, t):
    for rig in rigs:
        if clip is None:
            if rig.animation_data:
                rig.animation_data.action = None
            for pb in rig.pose.bones:
                pb.location = (0, 0, 0)
                pb.rotation_euler = (0, 0, 0)
            continue
        pista = rig.animation_data.nla_tracks[clip]
        A.set_action(rig, pista.strips[0].action)
    bpy.context.scene.frame_set(int(round(t * 30)))
    bpy.context.view_layer.update()


items = []
poner(None, 0.0)
items.append((E.foto('Huevos-alados-fila-cerrados', 177, 8, 63.0, target=(0.9, -0.6, 2.0)), 'CERRADOS: COMUN - POCO COMUN - RARO - EPICO - LEGENDARIO - MITICO'))
poner('Fly', 0.0)
items.append((E.foto('Huevos-alados-fila-vuelo', 180, 6, 63.0, target=(0.9, -0.6, 2.1)), 'VOLANDO (CLIP FLY) - ALAS ARRIBA'))
poner('Hatch', 1.0)
items.append((E.foto('Huevos-alados-fila-abiertos', 178, 20, 63.0, target=(0.9, -0.6, 2.1)), 'ECLOSION (CLIP HATCH A 1 S) - LA TAPA SALTA Y DENTRO BRILLA'))
W.contact_sheet(items, 1, os.path.join(D, '_fila.png'), title='HUEVOS ALADOS V03 POR RAREZA - SILUETA PROPIA: TAMANO ALAS Y EXTRAS (COPETE CUERNOS CRESTA HALO) - RENDERS DE BLENDER (SIN PROBAR EN ROBLOX)')
a_jpg(os.path.join(D, '_fila.png'), os.path.join(D, 'Huevos-alados-v03-hoja.jpg'), 0.6)
print('HOJA LISTA')
