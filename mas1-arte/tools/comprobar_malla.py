# Comprobaciones de malla de una mascota/ala ya construida: piezas sueltas (nada flota) y caras coplanares solapadas (parpadeo en Roblox).
#   MALLA_BLEND=mascotas-altas-v02/aguila-legendaria/AguilaLegendaria.blend blender -b --factory-startup -P comprobar_malla.py
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *

ruta = os.path.abspath(os.path.join(HERE, '..', os.environ['MALLA_BLEND']))
bpy.ops.wm.open_mainfile(filepath=ruta)
ob = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(('Ref', 'Plat', 'Regla'))][0]
rig = [o for o in bpy.data.objects if o.type == 'ARMATURE']
if rig:
    rig[0].animation_data_clear()
    for pb in rig[0].pose.bones:
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
sueltas, n_islas = piezas_sueltas(ob)
pares, ej = caras_coplanares(ob)
informe = {'blend': os.environ['MALLA_BLEND'], 'malla': ob.name, 'triangulos': A.tris([ob]), 'islas': n_islas, 'piezas_sueltas': sueltas,
           'pares_coplanares_solapados': pares, 'ejemplos': ej}
destino = os.path.join(os.path.dirname(ruta), 'COMPROBACION_MALLA.json')
json.dump(informe, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('MALLA', ob.name, 'tris', informe['triangulos'], 'sueltas', len(sueltas), 'coplanares solapados', pares)
