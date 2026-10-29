# Renderiza un clip de un .blend de mas1-arte desde una camara fija y lo guarda como GIF animado en bucle.
#   ANIM_BLEND=alas-avanzadas-v02/AlasAvanzadas_v02.blend ANIM_CLIP=Flap ANIM_N=12 ANIM_CAM=25,8,19,0,-0.8,-0.3 \
#   ANIM_OUT=alas-avanzadas-v02/previews/Alas-avanzadas-v02-Flap.gif [ANIM_RES=560x448] [ANIM_SAMPLES=24] [ANIM_LOOP=1]
#   blender -b --factory-startup -P animar_preview.py
# ANIM_CAM = azimut, elevacion, distancia, x, y, z del objetivo. ANIM_LOOP=0 para un clip que no es de bucle (incluye el ultimo fotograma).
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *
from gif_simple import escribir_gif

ROOT = os.path.abspath(os.path.join(HERE, '..'))
blend = os.path.join(ROOT, os.environ['ANIM_BLEND'])
clip = os.environ['ANIM_CLIP']
N = int(os.environ.get('ANIM_N', '12'))
az, el, dist, tx, ty, tz = [float(v) for v in os.environ['ANIM_CAM'].split(',')]
out = os.path.join(ROOT, os.environ['ANIM_OUT'])
w, h = [int(v) for v in os.environ.get('ANIM_RES', '560x448').split('x')]
muestras = int(os.environ.get('ANIM_SAMPLES', '24'))
bucle = os.environ.get('ANIM_LOOP', '1') != '0'

bpy.ops.wm.open_mainfile(filepath=blend)
rig = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act = bpy.data.actions[clip]
rig.animation_data_clear()
rig.animation_data_create()
A.set_action(rig, act)
dur = (act.frame_range[1] - act.frame_range[0]) / 30.0
CC = bpy.data.collections['Camaras']
A.setup_render((w, h), 'CYCLES', muestras)
a, e = math.radians(az), math.radians(el)
t = Vector((tx, ty, tz))
d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
cam = A.camera(CC, 'cam_anim', t + d * dist, t, lens=50.0)
tmp = os.path.join(os.path.dirname(out), '_anim')
os.makedirs(tmp, exist_ok=True)
frames = []
n_fotos = N if bucle else N + 1
for i in range(n_fotos):
    tt = dur * i / N
    f0 = act.frame_range[0] + tt * 30.0
    bpy.context.scene.frame_set(int(f0), subframe=f0 - int(f0))
    bpy.context.view_layer.update()
    p = os.path.join(tmp, 'f%03d.png' % i)
    A.render(p, cam)
    frames.append(W.load_png(p))
    os.remove(p)
os.rmdir(tmp)
retardo = max(2, int(round(100.0 * dur / N)))
escribir_gif(out, [np.rint(f * 255).astype(np.uint8) if f.dtype != np.uint8 else f for f in frames], retardo)
print('GIF LISTO', out, len(frames), 'fotogramas', retardo, 'cs')
