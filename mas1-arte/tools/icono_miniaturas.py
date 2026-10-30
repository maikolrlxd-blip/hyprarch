# Icono (512 x 512) y miniaturas (1920 x 1080) de «+1 de lanzamiento por segundo», montados en Blender con el arte del proyecto: un
# avatar de bloques que vuela con las alas avanzadas v0.2, el mapa v01 (Mar de Nubes), los huevos alados v03 y mascotas, con el
# titulo en letras gordas con contorno pegadas a la camara. Son renders de Blender PROVISIONALES: el icono y las miniaturas de
# verdad se suben a Roblox (no se ha subido nada).
# blender -b --factory-startup --python-exit-code 1 -P icono_miniaturas.py   ->   mas1-arte/icono-miniaturas-v01/
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *

ARTE = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ARTE, 'icono-miniaturas-v01')
os.makedirs(OUT, exist_ok=True)
A.clean_scene()
CM, CC = A.collection('Escena'), A.collection('Camaras')
mats = {}


def mat(h, brillo=0.0):
    k = (h, brillo)
    if k not in mats:
        m = bpy.data.materials.new('m_%s_%s' % (h, brillo))
        m.use_nodes = True
        b = m.node_tree.nodes.get('Principled BSDF')
        b.inputs['Base Color'].default_value = (*lin(h), 1)
        b.inputs['Roughness'].default_value = 0.55
        if brillo:
            b.inputs['Emission Color'].default_value = (*lin(h), 1)
            b.inputs['Emission Strength'].default_value = brillo
        mats[k] = m
    return mats[k]


def cargar(ruta, nombres=None):
    """Trae objetos de otro .blend (sin tocarlo) y arregla las texturas que apuntan a su carpeta."""
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        elegidos = [n for n in src.objects if nombres is None or n in nombres]
        dst.objects = elegidos or list(src.objects)   # si se llaman distinto, todo el archivo
    obs = [o for o in dst.objects if o is not None]
    for o in obs:
        CM.objects.link(o)
    base = os.path.dirname(ruta)
    for img in bpy.data.images:
        if img.source == 'FILE' and not os.path.exists(bpy.path.abspath(img.filepath)):
            cand = os.path.join(base, 'texturas', os.path.basename(img.filepath))
            if os.path.exists(cand):
                img.filepath = cand
                img.reload()
    return obs


def pieza_rig(sub, nombre, pos, rot_z=0.0, escala=1.0, clip='Fly', t=0.25):
    """Una pieza con rig (huevo, mascota, alas): la pone en pos, girada y en un instante de un clip."""
    obs = cargar(os.path.join(ARTE, sub, nombre + '.blend'), [nombre, nombre + '_Rig'])
    rig = next((o for o in obs if o.type == 'ARMATURE'), None)
    raiz = rig or obs[0]
    raiz.location, raiz.rotation_euler, raiz.scale = pos, (0, 0, math.radians(rot_z)), (escala,) * 3
    if rig and rig.animation_data and clip in rig.animation_data.nla_tracks:
        A.set_action(rig, rig.animation_data.nla_tracks[clip].strips[0].action)
        rig.animation_data.nla_tracks[clip].strips[0].action.use_fake_user = True
        rig['_t'] = t
    return raiz


def caja(padre, c, s, h, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c, rotation=[math.radians(r) for r in rot])
    o = bpy.context.active_object
    o.scale = s
    o.data.materials.append(mat(h))
    for col in o.users_collection:
        col.objects.unlink(o)
    CM.objects.link(o)
    o.parent = padre
    return o


def avatar(pos, cabeceo=-70, alabeo=0):
    """Avatar de bloques (colores clasicos) en postura de vuelo de superheroe, con las alas avanzadas a la espalda."""
    e = bpy.data.objects.new('Avatar', None)
    CM.objects.link(e)
    caja(e, (0, 0, 3.0), (2, 1, 2), '#2f7de1')                                     # torso
    caja(e, (0, 0, 4.6), (1.2, 1.2, 1.2), '#f5cd30')                               # cabeza
    for x in (-0.28, 0.28):
        caja(e, (x, 0.61, 4.75), (0.18, 0.04, 0.26), '#1d1626')                    # ojos
    caja(e, (0, 0.61, 4.38), (0.5, 0.04, 0.1), '#1d1626')                          # sonrisa
    for s in (-1, 1):
        caja(e, (s * 1.5, 0.3, 4.4), (1, 1, 2), '#f5cd30', rot=(-70, 0, 0))       # brazos hacia delante
        caja(e, (s * 0.5, 0, 1.0), (1, 1, 2), '#4caf50')                            # piernas
    alas = pieza_rig('alas-avanzadas-v02', 'AlasAvanzadas_v02', (0, -0.6, 3.6), rot_z=180, escala=0.95, clip='Glide', t=0.5)
    alas.parent = e
    e.location = pos
    e.rotation_euler = (math.radians(cabeceo), math.radians(alabeo), 0)
    return e


FUENTE_TITULO = r'C:\Windows\Fonts\ariblk.ttf'   # Arial Black: con la letra de Blender el «+1» se leia «+I»
FUENTE = bpy.data.fonts.load(FUENTE_TITULO) if os.path.exists(FUENTE_TITULO) else None


def titulo(cam, lineas, y0, tam, color='#ffd23f', borde='#1c1530', dist=12):
    """Lineas de titulo pegadas a la camara (siempre de cara): relleno de color con un contorno oscuro detras."""
    for i, (txt, f) in enumerate(lineas):
        for capa, (h, z, k) in enumerate(((borde, -0.6, 1.0), (color, 0.0, 1.0))):   # el contorno bien detras: su bisel no tapa el relleno
            cu = bpy.data.curves.new('t', 'FONT')
            cu.body, cu.align_x, cu.align_y, cu.size = txt, 'CENTER', 'CENTER', tam * f * (0.85 if FUENTE else 1.0)
            if FUENTE:
                cu.font = FUENTE
            cu.extrude, cu.bevel_depth = 0.02 * tam, (0.07 if capa == 0 else 0.0) * tam * f
            o = bpy.data.objects.new('titulo', cu)
            o.data.materials.append(mat(h, 0.6 if capa == 1 else 0.0))
            CM.objects.link(o)
            o.parent = cam
            o.location = (0, y0 - i * tam * 1.05, -dist + z)


sol(CC, 'Sol', 2.3, (-0.4, 0.5, -0.75))   # menos que en el mapa: el blanco de las nubes se quemaba
sol(CC, 'Relleno', 0.9, (0.6, -0.3, -0.4), 20.0)
mapa = cargar(os.path.join(ARTE, 'mapa-v01', 'Mapa-v01.blend'))
PRADERA = r'C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\mas-1-lanzamiento\art\zona-inicial-v01\Pradera-inicio-ambiente-v01.blend'
if os.path.exists(PRADERA):   # la Pradera de Codex detras (solo se lee su archivo, sin tocarlo)
    cargar(PRADERA)
fotos = []


def foto(nombre, res, loc, objetivo, lente, lineas, y0, tam, t=0.25):
    A.setup_render(res, 'CYCLES', 48)
    A.setup_world(lin('#9fd3ff'), 1.0)
    for o in bpy.data.objects:
        if o.type == 'ARMATURE' and '_t' in o:
            bpy.context.scene.frame_set(int(round(o['_t'] * 30)))
    cam = A.camera(CC, 'cam_' + nombre, loc, objetivo, lens=lente)
    cam.data.clip_end = 3000
    for o in list(bpy.data.objects):
        if o.name.startswith('titulo'):
            bpy.data.objects.remove(o)
    titulo(cam, lineas, y0, tam)
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 92
    ruta = os.path.join(OUT, nombre + '.jpg')
    A.render(ruta, cam)
    fotos.append(ruta)


# escena: el avatar con alas volando sobre el Mar de Nubes hacia el arco, con mascotas detras y un aro delante
avatar((0, 150, 22), cabeceo=-72, alabeo=-12)
pieza_rig('mascotas-enemigos-v01/nube', 'MascotaNube', (-8, 147, 26), rot_z=0, escala=1.6)   # al otro lado de la camara: no tapan
pieza_rig('mascotas-enemigos-v01/meteorito', 'MascotaMeteorito', (-11, 153, 19), rot_z=0, escala=1.5)
pieza_rig('mascotas-altas-v02/grifo-mitico', 'GrifoMitico', (-5, 143, 31), rot_z=0, escala=1.2)
for i, (sub, nombre) in enumerate((('raro', 'HuevoAladoRaro'), ('legendario', 'HuevoAladoLegendario'), ('mitico', 'HuevoAladoMitico'))):
    pieza_rig('huevos-alados-v03/' + sub, nombre, (-14 + i * 14, 205, 14 + 3 * i), rot_z=180, escala=1.8)

foto('Icono-512', (1024, 1024), (8, 166, 27), (0, 151, 22.5), 28, [('+1', 1.0)], 4.0, 3.6)
foto('Miniatura-1-vuelo', (1920, 1080), (13, 171, 29), (-1, 150, 22), 30, [('+1 DE LANZAMIENTO', 1.0), ('POR SEGUNDO', 0.8)], 3.2, 1.0)
foto('Miniatura-2-huevos', (1920, 1080), (0, 168, 19), (0, 210, 18), 32, [('HUEVOS ALADOS', 1.0), ('MASCOTAS MITICAS', 0.75)], 3.1, 1.1)
im = bpy.data.images.load(os.path.join(OUT, 'Icono-512.jpg'))   # el icono, a 512
im.scale(512, 512)
im.filepath_raw = os.path.join(OUT, 'Icono-512.jpg')
im.file_format = 'JPEG'
im.save()
A.log('listo', fotos)
