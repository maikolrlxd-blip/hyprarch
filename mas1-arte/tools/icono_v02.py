# Icono v02 (512 x 512) de «+1 de lanzamiento por segundo», con la crítica del director (30/10): el avatar de espaldas con las alas
# avanzadas abiertas y enormes, volando hacia un aro dorado, un «+1» enorme (~40 % del alto), orbes «+1» por el camino y el cielo en
# degradado. Usa las piezas de tools/icono_miniaturas.py (avatar de bloques, alas con su clip, título con contorno). Render de Blender
# PROVISIONAL: el icono de verdad lo sube Maikol a Roblox (no se ha subido nada).
#   blender -b --factory-startup --python-exit-code 1 -P icono_v02.py   ->   mas1-arte/icono-v02/   (ICONO_PRUEBA=1: rápido, para encuadrar)
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import icono_miniaturas as IM   # sus funciones; su escena solo se monta si se ejecuta él
from mas1_lib import *

OUT = os.path.join(IM.ARTE, 'icono-v02')
os.makedirs(OUT, exist_ok=True)
PRUEBA = os.environ.get('ICONO_PRUEBA') == '1'


def cielo(abajo, arriba):
    """Fondo en degradado vertical de la imagen (coordenadas de ventana): claro abajo, intenso arriba."""
    nt = bpy.context.scene.world.node_tree
    nt.nodes.clear()
    tc, sep = nt.nodes.new('ShaderNodeTexCoord'), nt.nodes.new('ShaderNodeSeparateXYZ')
    rampa = nt.nodes.new('ShaderNodeValToRGB')
    rampa.color_ramp.elements[0].color = (*lin(abajo), 1)
    rampa.color_ramp.elements[1].color = (*lin(arriba), 1)
    bg, out = nt.nodes.new('ShaderNodeBackground'), nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Window'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Y'], rampa.inputs['Fac'])
    nt.links.new(rampa.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def a_escena(o):
    for col in o.users_collection:
        col.objects.unlink(o)
    IM.CM.objects.link(o)
    return o


def aro(c, radio, grosor, color='#ffc83d', brillo=0.6):
    bpy.ops.mesh.primitive_torus_add(major_radius=radio, minor_radius=grosor, major_segments=72, minor_segments=18, location=c,
                                     rotation=(math.radians(90), 0, 0))
    o = a_escena(bpy.context.active_object)
    o.data.materials.append(IM.mat(color, brillo))
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def bola(c, r, color, brillo=0.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=24, ring_count=12, location=c)
    o = a_escena(bpy.context.active_object)
    o.data.materials.append(IM.mat(color, brillo))
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def nube(c, s):
    for dx, dz, r in ((0, 0, 1.0), (-1.1, -0.25, 0.75), (1.15, -0.2, 0.8), (0.45, 0.45, 0.7), (-0.5, 0.35, 0.65)):
        bola((c[0] + dx * s, c[1], c[2] + dz * s), r * s, '#ffffff')


cielo('#c9f4ff', '#2f6bff')
sol(IM.CC, 'Sol', 2.6, (0.3, 0.6, -0.7))            # desde detrás de la cámara: ilumina la espalda y las alas
sol(IM.CC, 'Contra', 1.4, (-0.2, -0.8, -0.3), 12)   # de cara a la cámara: borde de luz en la silueta
IM.avatar((0, 0, 0), cabeceo=-52, alabeo=0, escala_alas=1.75, clip_alas='Flap', t_alas=0.0)   # alas «arriba extendida»
aro((0, 22, 10.5), 9.5, 1.0)
aro((0, 22, 10.5), 8.1, 0.26, color='#7df9ff', brillo=1.5)   # brillo cian por dentro, como los aros del juego
for i in range(5):                                          # orbes «+1» camino del aro
    bola((math.sin(i * 1.3) * 1.4, 7 + i * 3.0, 6.5 + i * 0.8), 0.45, '#ffe14d', 2.0)
for c, s in (((-12, 20, -9), 3.4), ((13, 26, -10), 4.0), ((0, 36, -12), 5.0), ((-7, 6, -11), 2.6), ((8, 9, -10.5), 2.4)):
    nube(c, s)

res, muestras = ((512, 512), 12) if PRUEBA else ((1024, 1024), 64)
A.setup_render(res, 'CYCLES', muestras)
cielo('#c9f4ff', '#2f6bff')   # setup_render no toca el mundo, pero por si acaso
for o in bpy.data.objects:
    if o.type == 'ARMATURE' and '_t' in o:
        bpy.context.scene.frame_set(int(round(o['_t'] * 30)))
cam = A.camera(IM.CC, 'cam_icono', (2.6, -21.0, 0.6), (0, 6, 7.6), lens=46)   # de espaldas, de lejos: menos perspectiva
cam.data.clip_end = 500
IM.titulo(cam, [('+1', 1.0)], 2.4, 6.3)
bpy.context.scene.render.image_settings.file_format = 'PNG'
ruta = os.path.join(OUT, 'Icono-v02-prueba.png' if PRUEBA else 'Icono-v02-1024.png')
A.render(ruta, cam)
if not PRUEBA:
    im = bpy.data.images.load(ruta)
    im.scale(512, 512)
    im.filepath_raw = os.path.join(OUT, 'Icono-v02-512.png')
    im.file_format = 'PNG'
    im.save()
A.log('icono', ruta)
