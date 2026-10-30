# Mapa de «+1 de lanzamiento por segundo», v01 (solo lo visual; Maikol, 30/10: «primero todo lo visual» y «el mapa cuando termines»):
# las cuatro zonas que siguen a la Pradera del Despegue de Codex a lo largo del recorrido recto (+Y): Mar de Nubes, Tormenta, Cielo alto
# y Espacio. Mismo lenguaje que la Pradera (bloques gordos con el borde suave y una textura de paleta de 256 × 256) y en cada zona: suelo
# donde aterrizar (carril de 66 studs como el prado de la Pradera, con el techo en z = 0), decorado a los lados, arco de entrada con el
# nombre en letras de bloques, marca de multiplicador en el suelo (x3 a x6, provisionales: los números los decide el juego), flechas y
# tres aros que suben. Cada zona sale en piezas separadas (FBX y GLB) para montarlas en Studio. Sin código y sin probar en Roblox.
# blender -b --factory-startup --python-exit-code 1 -P build_mapa.py      MAPA_FASE=check | full (por defecto)
# Ejes: +Y = sentido del vuelo, +Z arriba, +X a la derecha del jugador; 1 unidad = 1 stud. La Pradera de Codex ocupa hasta y ≈ 169.
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *
from mas1_ave import cubo_girado

FASE = os.environ.get('MAPA_FASE', 'full')
OUT = os.path.abspath(os.path.join(HERE, '..', 'mapa-v01'))
PRADERA = r'C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\mas-1-lanzamiento\art\zona-inicial-v01\Pradera-inicio-ambiente-v01.blend'
ANCHO, LARGO, Y_INICIO = 66.0, 360.0, 172.0

PAL = {
    'blanco': '#ffffff', 'letra': '#2a3f7a', 'azul': '#3a7bd5', 'aro_azul': '#5fc8ff', 'aro_oro': '#ffc42e',
    'nube': '#f4f6ff', 'nube_b': '#e8ebfb', 'nube_sombra': '#d3d6f5', 'nube_lila': '#b9bdf0',
    'nube_osc': '#7a86a8', 'nube_osc_b': '#6e799b', 'nube_osc2': '#56607f', 'nube_osc3': '#3f4762', 'rayo': '#ffd23f', 'rayo_claro': '#fff6b0',
    'nube_rosa': '#f6dcff', 'nube_rosa_b': '#eccff9', 'nube_rosa2': '#e3c3f7', 'aurora_a': '#5cf2c8', 'aurora_b': '#6fb4ff', 'aurora_c': '#c77dff',
    'cristal': '#9ff3ff', 'cristal_rosa': '#ffb3e6', 'metal': '#cfd6e6', 'metal_osc': '#7c86a1',
    'roca': '#6a607e', 'roca_b': '#605670', 'roca_osc': '#4a4359', 'crater': '#332d40', 'planeta_a': '#ff9a5c', 'planeta_a2': '#e2723d',
    'planeta_b': '#7fd1ff', 'planeta_b2': '#4d9fd6', 'anillo': '#ffe3a3', 'estrella': '#fff6c2', 'luz': '#ffe14d',
    'cesped': '#6cc04a', 'cesped2': '#57a83c', 'tierra': '#8a5a34', 'tronco': '#6e4526', 'hoja': '#3f9e4c',
}

# letras de bloques de 5 × 7 (las que hacen falta para los nombres y los multiplicadores)
FUENTE = {
    'A': '.###.|#...#|#...#|#####|#...#|#...#|#...#', 'B': '####.|#...#|#...#|####.|#...#|#...#|####.',
    'C': '.####|#....|#....|#....|#....|#....|.####', 'D': '####.|#...#|#...#|#...#|#...#|#...#|####.',
    'E': '#####|#....|#....|####.|#....|#....|#####', 'I': '#####|..#..|..#..|..#..|..#..|..#..|#####',
    'L': '#....|#....|#....|#....|#....|#....|#####', 'M': '#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#',
    'N': '#...#|##..#|#.#.#|#..##|#...#|#...#|#...#', 'O': '.###.|#...#|#...#|#...#|#...#|#...#|.###.',
    'P': '####.|#...#|#...#|####.|#....|#....|#....', 'R': '####.|#...#|#...#|####.|#.#..|#..#.|#...#',
    'S': '.####|#....|#....|.###.|....#|....#|####.', 'T': '#####|..#..|..#..|..#..|..#..|..#..|..#..',
    'U': '#...#|#...#|#...#|#...#|#...#|#...#|.###.', 'x': '.....|.....|#...#|.#.#.|..#..|.#.#.|#...#',
    '3': '####.|....#|....#|.###.|....#|....#|####.', '4': '#..#.|#..#.|#..#.|#####|...#.|...#.|...#.',
    '5': '#####|#....|####.|....#|....#|#...#|.###.', '6': '.###.|#....|#....|####.|#...#|#...#|.###.',
}


def ancho_texto(s, px):
    return (len(s) * 6 - 1) * px


def texto_cartel(mb, s, x0, y_frente, z0, px, mat):
    """Letras de bloques en el plano XZ, legibles desde -Y (el jugador llega desde atrás): cada píxel es un bloque de px que sale hacia -Y."""
    for i, ch in enumerate(s):
        if ch == ' ':
            continue
        for fila, linea in enumerate(FUENTE[ch].split('|')):
            for col, c in enumerate(linea):
                if c == '#':
                    mb.box((x0 + (i * 6 + col + 0.5) * px, y_frente - px * 0.4, z0 + (6 - fila + 0.5) * px), (px, px * 0.8, px), mat)


def texto_suelo(mb, s, xc, y0, px, alto, mat):
    """Letras planas en el suelo (plano XY), legibles al llegar volando desde -Y: la fila de arriba de la letra queda más lejos (+Y)."""
    x0 = xc - ancho_texto(s, px) / 2
    for i, ch in enumerate(s):
        if ch == ' ':
            continue
        for fila, linea in enumerate(FUENTE[ch].split('|')):
            for col, c in enumerate(linea):
                if c == '#':
                    mb.box((x0 + (i * 6 + col + 0.5) * px, y0 + (6 - fila + 0.5) * px, alto / 2), (px * 0.98, px * 0.98, alto), mat)


def flecha(mb, y, mat):
    """Flecha plana en el suelo que apunta hacia +Y (como las de la Pradera)."""
    for s in (1, -1):
        cubo_girado(mb, (s * 1.6, y, 0.12), (5.2, 1.6, 0.24), mat, rot=(0, 0, -s * 45))     # punta en +Y: «^» y el palo detrás
    mb.box((0, y - 3.4, 0.10), (1.6, 5.0, 0.20), mat)


def nube(mb, c, w, d, h, rnd, arriba, abajo):
    """Nube de bloques: una base y de tres a cinco bultos encima, con el borde muy achaflanado (redondeada, no un bloque de hielo)."""
    x, y, z = c
    mb.box((x, y, z + h * 0.25), (w, d, h * 0.5), abajo, bevel=0.3 * min(w, d, h * 0.5))
    for _ in range(rnd.randint(3, 5)):
        bw, bd, bh = w * rnd.uniform(0.35, 0.62), d * rnd.uniform(0.35, 0.62), h * rnd.uniform(0.45, 0.85)
        mb.box((x + rnd.uniform(-0.3, 0.3) * w, y + rnd.uniform(-0.3, 0.3) * d, z + h * 0.5 + bh * 0.5 - 0.35), (bw, bd, bh), arriba,
               bevel=0.32 * min(bw, bd, bh))


def torre(mb, c, h, rnd, arriba, abajo):
    """Torre de nubes apiladas que se estrechan hacia arriba."""
    x, y, z = c
    w = rnd.uniform(16, 24)
    pisos = max(3, int(h / 12))
    for i in range(pisos):
        f = 1.0 - 0.55 * i / pisos
        nube(mb, (x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2), z + i * h / pisos), w * f, w * f * rnd.uniform(0.8, 1.1), h / pisos + 3,
             rnd, arriba, abajo)


def isla(mb, c, rnd):
    """Islita flotante de césped con un árbol de bloques (como los de la Pradera)."""
    x, y, z = c
    mb.box((x, y, z), (12, 10, 2.4), 'cesped', bevel=0.4)
    for i, (w, d) in enumerate(((10, 8), (7, 6), (4, 3.5))):
        mb.box((x, y, z - 2.4 - i * 2.0), (w, d, 2.0), 'tierra', bevel=0.3)
    mb.box((x + 1.5, y, z + 3.2), (1.4, 1.4, 4.2), 'tronco')
    for i, (w, d, dz) in enumerate(((7, 6, 5.8), (5, 4.5, 7.6), (3, 2.6, 9.0))):
        mb.box((x + 1.5, y, z + dz), (w, d, 1.9), 'hoja' if i != 1 else 'cesped2', bevel=0.3)


def aro(mb, c, R, a, mat):
    """Aro vertical de cara al vuelo (eje +Y), como los de la Pradera."""
    perfil = [(R + a * math.cos(2 * math.pi * k / 10), a * math.sin(2 * math.pi * k / 10)) for k in range(11)]
    mb.lathe(c, Vector(c) + Vector((0, 1, 0)), perfil, 28, mat, close0=False, close1=False)


def suelo_baldosas(mb, y0, mats):
    """Carril de aterrizaje: baldosas de 22 × 24 con los dos tonos de la zona, techo en z = 0 y 2 studs de grosor."""
    for i in range(3):
        for j in range(int(LARGO / 24)):
            mb.box((-ANCHO / 2 + 11 + 22 * i, y0 + 12 + 24 * j, -1.0), (22, 24, 2.0), mats[(i + j) % 2])


def arco(mb, y, nombre, poste, adorno, cartel, letra):
    """Arco de entrada de la zona con el nombre en letras de bloques en el cartel (de cara al jugador que llega)."""
    px = 0.8 if len(nombre) > 10 else 0.95
    an = ancho_texto(nombre, px) + 6
    for s in (1, -1):
        mb.box((s * (ANCHO / 2 + 4), y, 14), (6, 6, 28), poste, bevel=0.6)
        mb.box((s * (ANCHO / 2 + 4), y, 29), (8, 8, 2.4), adorno, bevel=0.5)
    mb.box((0, y, 30.6), (ANCHO + 18, 5, 4), poste, bevel=0.6)
    mb.box((0, y - 2.0, 30.6 + 7.0), (an, 1.6, 10.0), cartel, bevel=0.3)
    mb.box((0, y - 2.0, 30.6 + 12.6), (an + 2, 2.2, 1.4), adorno, bevel=0.2)
    texto_cartel(mb, nombre, -ancho_texto(nombre, px) / 2, y - 2.8, 30.6 + 7.0 - 3.5 * px, px, letra)


# ---------------------------------------------------------------- zonas
def lado(s):
    return 'LadoDer' if s > 0 else 'LadoIzq'                       # +X queda a la derecha del jugador


def zona_nubes(P, y0, rnd):
    suelo_baldosas(P['Suelo'], y0, ('nube', 'nube_b'))
    for s in (1, -1):
        for j in range(18):                                            # nubes del borde del carril
            nube(P['Suelo'], (s * (ANCHO / 2 + 5), y0 + 10 + j * 20, -1.5), rnd.uniform(10, 14), rnd.uniform(12, 18), rnd.uniform(4, 6), rnd,
                 'nube', 'nube_sombra')
        for j in range(12):                                            # mar de nubes más bajo, hacia fuera
            nube(P[lado(s)], (s * rnd.uniform(60, 150), y0 + j * 30 + rnd.uniform(0, 20), -9), rnd.uniform(26, 40), rnd.uniform(22, 34),
                 rnd.uniform(5, 8), rnd, 'nube', 'nube_lila')
        for j in range(5):                                             # torres de cúmulos
            torre(P[lado(s)], (s * rnd.uniform(75, 125), y0 + 30 + j * 70, -6), rnd.uniform(40, 75), rnd, 'nube', 'nube_sombra')
        for j in range(2):                                             # islitas flotantes
            isla(P[lado(s)], (s * rnd.uniform(46, 58), y0 + 90 + j * 150, rnd.uniform(16, 26)), rnd)


def zona_tormenta(P, y0, rnd):
    suelo_baldosas(P['Suelo'], y0, ('nube_osc', 'nube_osc_b'))
    for s in (1, -1):
        for j in range(18):
            nube(P['Suelo'], (s * (ANCHO / 2 + 5), y0 + 10 + j * 20, -1.5), rnd.uniform(10, 14), rnd.uniform(12, 18), rnd.uniform(4, 7), rnd,
                 'nube_osc', 'nube_osc2')
        for j in range(12):
            nube(P[lado(s)], (s * rnd.uniform(60, 150), y0 + j * 30 + rnd.uniform(0, 20), -9), rnd.uniform(26, 40), rnd.uniform(22, 34),
                 rnd.uniform(6, 10), rnd, 'nube_osc2', 'nube_osc3')
        for j in range(5):                                             # nubarrones altos y oscuros
            x, y = s * rnd.uniform(70, 120), y0 + 30 + j * 70
            torre(P[lado(s)], (x, y, -6), rnd.uniform(60, 95), rnd, 'nube_osc', 'nube_osc3')
            if j % 2 == 0:                                             # rayo que cae del nubarrón al mar de nubes
                rayo = [(1.6, 32), (-2.8, 20), (-0.4, 20), (-2.2, 4), (3.6, 22), (1.0, 22), (3.0, 32)]
                P[lado(s)].prism([(x - s * 14 + 2.2 * u, v) for u, v in rayo], y - 1.0, y + 1.0, 'rayo', plane='XZ', side_mat='rayo_claro')


def zona_cielo(P, y0, rnd):
    suelo_baldosas(P['Suelo'], y0, ('nube_rosa', 'nube_rosa_b'))
    for s in (1, -1):
        for j in range(18):
            nube(P['Suelo'], (s * (ANCHO / 2 + 5), y0 + 10 + j * 20, -1.5), rnd.uniform(9, 12), rnd.uniform(10, 16), rnd.uniform(3, 5), rnd,
                 'nube_rosa', 'nube_rosa2')
        for j in range(9):                                             # cristales clavados en el borde y flotando
            alto = rnd.uniform(8, 18)
            cubo_girado(P[lado(s)], (s * rnd.uniform(44, 70), y0 + 20 + j * 40, alto / 2 - 1), (3.2, 3.2, alto),
                        'cristal' if j % 2 == 0 else 'cristal_rosa', rot=(rnd.uniform(-12, 12), rnd.uniform(-12, 12), 45))
            cubo_girado(P[lado(s)], (s * rnd.uniform(60, 110), y0 + 40 + j * 38, rnd.uniform(25, 55)), (4, 4, 9),
                        'cristal_rosa' if j % 2 == 0 else 'cristal', rot=(rnd.uniform(-30, 30), rnd.uniform(-30, 30), 45))
        for banda, (mat, zb) in enumerate((('aurora_a', 52), ('aurora_b', 64), ('aurora_c', 76))):   # auroras: cintas que ondulan
            prev = None
            for j in range(25):
                y = y0 + j * 15
                p = Vector((s * (95 + 14 * math.sin(j * 0.45 + banda)), y, zb + 9 * math.sin(j * 0.6 + banda * 1.3)))
                if prev is not None:
                    P[lado(s)].seg_box(prev, p, 0.8, 9.0, mat, extend=0.6)
                prev = p


def zona_espacio(P, y0, rnd):
    suelo_baldosas(P['Suelo'], y0, ('roca', 'roca_b'))
    for j in range(5):                                                 # cráteres (borde de bloques) en el carril
        cx, cy, r = rnd.uniform(-22, 22), y0 + 40 + j * 70, rnd.uniform(4, 7)
        for k in range(10):
            a = 2 * math.pi * k / 10
            cubo_girado(P['Suelo'], (cx + r * math.cos(a), cy + r * math.sin(a), 0.5), (3.0, 1.6, 1.0), 'crater', rot=(0, 0, math.degrees(a) + 90))
    for s in (1, -1):
        for j in range(16):                                            # rocas del borde y asteroides flotando
            P['Suelo'].rock((s * (ANCHO / 2 + rnd.uniform(3, 9)), y0 + 10 + j * 22, rnd.uniform(-1, 1)), rnd.uniform(3, 6), 'roca_osc',
                            subdiv=1, seed=int(rnd.random() * 1e6), jitter=0.2)
            P[lado(s)].rock((s * rnd.uniform(50, 140), y0 + rnd.uniform(0, LARGO), rnd.uniform(10, 70)), rnd.uniform(2, 7),
                            'roca' if j % 2 else 'roca_osc', subdiv=1, seed=int(rnd.random() * 1e6), jitter=0.25)
        for j in range(60):                                            # estrellas
            cubo_girado(P[lado(s)], (s * rnd.uniform(150, 210), y0 + rnd.uniform(-20, LARGO + 20), rnd.uniform(5, 160)), (1.2, 1.2, 1.2), 'estrella',
                        rot=(45, 45, 0))
    for s, (c, r, a1, a2) in ((1, ((150, y0 + 120, 85), 34, 'planeta_a', 'planeta_a2')), (-1, ((-140, y0 + 260, 110), 26, 'planeta_b', 'planeta_b2'))):
        P[lado(s)].rock(c, r, a1, subdiv=3, seed=7 + s, jitter=0.0)    # planetas de bandas con anillo
        P[lado(s)].rock((c[0], c[1], c[2] + r * 0.3), r * 0.93, a2, subdiv=2, seed=11 + s, jitter=0.0, squash=(1.0, 1.0, 0.45))
        perfil = [(r * 1.35, -0.8), (r * 1.85, -0.8), (r * 1.85, 0.8), (r * 1.35, 0.8), (r * 1.35, -0.8)]
        eje = Vector((0.25 * s, 0.15, 1.0)).normalized()
        P[lado(s)].lathe(Vector(c), Vector(c) + eje, perfil, 40, 'anillo', close0=False, close1=False)


ZONAS = [
    dict(clave='mar-de-nubes', nombre='MAR DE NUBES', marca='x3', crea=zona_nubes, cielo='#9fd3ff',
         arco=('blanco', 'azul', 'blanco', 'letra'), aro='aro_azul', flecha='azul'),
    dict(clave='tormenta', nombre='TORMENTA', marca='x4', crea=zona_tormenta, cielo='#3d4766',
         arco=('nube_osc3', 'rayo', 'nube_osc', 'rayo'), aro='rayo', flecha='rayo_claro'),
    dict(clave='cielo-alto', nombre='CIELO ALTO', marca='x5', crea=zona_cielo, cielo='#b7a3f0',
         arco=('metal', 'aurora_c', 'blanco', 'letra'), aro='aurora_c', flecha='aurora_b'),
    dict(clave='espacio', nombre='ESPACIO', marca='x6', crea=zona_espacio, cielo='#0d1024',
         arco=('metal_osc', 'luz', 'metal', 'letra'), aro='aro_oro', flecha='estrella'),
]
PIEZAS = ('Suelo', 'LadoIzq', 'LadoDer', 'Arco', 'Marcas', 'Aros')   # los lados por separado: menos de 10.000 triángulos por malla


def imagen_paleta(ruta):
    """Paleta de 256 × 256: un cuadro de 16 × 16 píxeles por color (como la de la Pradera). Devuelve {región: índice}."""
    import numpy as np
    px = np.ones((256, 256, 4), np.float32)
    for i, nm in enumerate(PAL):
        r, c = divmod(i, 16)
        px[r * 16:(r + 1) * 16, c * 16:(c + 1) * 16, :3] = A.hexrgb(PAL[nm])
    img = bpy.data.images.new('Mapa_paleta_256', 256, 256)
    img.pixels = px.ravel()
    img.filepath_raw = ruta
    img.file_format = 'PNG'
    img.save()
    return {nm: i for i, nm in enumerate(PAL)}


def paletizar(ob, idx):
    """UV de cada cara al centro del cuadro de su color en la paleta."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    uv = me.uv_layers.active.data
    nombres = [s.material.name[2:] for s in ob.material_slots]
    for p in me.polygons:
        r, c = divmod(idx[nombres[p.material_index]], 16)
        for li in p.loop_indices:
            uv[li].uv = ((c + 0.5) / 16.0, (r + 0.5) / 16.0)


A.clean_scene()
A.REGIONS.clear()
for d in ('', 'exports', 'texturas', 'previews'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
CM, CC = A.collection('Mapa'), A.collection('Camaras')
rnd = random.Random(30)
objetos, resumen = {}, []
for i, Z in enumerate(ZONAS):
    y0 = Y_INICIO + i * LARGO
    P = {k: A.MB('%s_%s' % (Z['clave'], k)) for k in PIEZAS}
    Z['crea'](P, y0, rnd)
    poste, adorno, cartel, letra = Z['arco']
    arco(P['Arco'], y0 + 2, Z['nombre'], poste, adorno, cartel, letra)
    texto_suelo(P['Marcas'], Z['marca'], 0, y0 + 26, 2.2, 0.24, Z['flecha'])         # del color de las flechas: el blanco no se ve en las nubes
    for j in range(5):
        flecha(P['Marcas'], y0 + 70 + j * 60, Z['flecha'])
    for j, (dy, z) in enumerate(((80, 14), (170, 20), (260, 26))):
        aro(P['Aros'], (rnd.uniform(-12, 12), y0 + dy, z), 6.0, 0.6, Z['aro'])
    for k in PIEZAS:
        ob = P[k].finish(CM)
        ob.name = 'Mapa_%s_%s' % (Z['clave'].replace('-', '_'), k)
        objetos[(Z['clave'], k)] = ob
        resumen.append((Z['clave'], k, A.tris([ob])))
A.log('triangulos por pieza', resumen, 'total', sum(t for _, _, t in resumen))
if FASE == 'check':
    A.log('listo')
    raise SystemExit

idx = imagen_paleta(os.path.join(OUT, 'texturas', 'Mapa_paleta_256.png'))
mat = A.final_material('Mapa_paleta', os.path.join(OUT, 'texturas', 'Mapa_paleta_256.png'))
for ob in objetos.values():
    paletizar(ob, idx)
    A.assign_final([ob], mat)
for (clave, k), ob in objetos.items():                                 # una pieza por archivo, para montarlas por separado en Studio
    fbx(os.path.join(OUT, 'exports', '%s_%s.fbx' % (clave, k)), [ob], False)
    A.select_only([ob])
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'exports', '%s_%s.glb' % (clave, k)), use_selection=True, export_format='GLB',
                              export_animations=False)
A.save_blend(os.path.join(OUT, 'Mapa-v01.blend'))

# ---------------------------------------------------------------- renders (con la Pradera de Codex delante, solo para ver cómo empalma)
if os.path.exists(PRADERA):
    CP = A.collection('Pradera_Codex')
    with bpy.data.libraries.load(PRADERA, link=False) as (src, dst):
        dst.objects = list(src.objects)
    for o in dst.objects:
        if o is not None and o.type == 'MESH':
            CP.objects.link(o)
sol(CC, 'Sol', 3.2, (-0.4, 0.5, -0.75))
sol(CC, 'Relleno', 0.8, (0.6, -0.3, -0.4), 20.0)
A.setup_render((1600, 900), 'CYCLES', 32)
fotos = []


def foto(nombre, loc, objetivo, lente, cielo, rotulo):
    A.setup_world(lin(cielo), 1.0)
    cam = A.camera(CC, 'cam_' + nombre, loc, objetivo, lens=lente)
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 90
    ruta = os.path.join(OUT, 'previews', nombre + '.jpg')
    A.render(ruta, cam)
    fotos.append((ruta, rotulo))


foto('Mapa-general', (-520, -140, 420), (0, 760, 0), 32, '#9fd3ff', 'MAPA COMPLETO: PRADERA (CODEX) - MAR DE NUBES - TORMENTA - CIELO ALTO - ESPACIO')
for i, Z in enumerate(ZONAS):
    y0 = Y_INICIO + i * LARGO
    foto('Zona-%s-entrada' % Z['clave'], (18, y0 - 75, 30), (0, y0 + 40, 24), 26, Z['cielo'], 'ENTRADA %s - ARCO Y CARTEL' % Z['nombre'])
    foto('Zona-%s-dentro' % Z['clave'], (0, y0 + 14, 16), (0, y0 + 200, 8), 24, Z['cielo'], 'DENTRO DE %s (MARCA %s)' % (Z['nombre'], Z['marca'].upper()))
    foto('Zona-%s-lado' % Z['clave'], (-170, y0 + 60, 70), (10, y0 + 200, 0), 30, Z['cielo'], '%s DESDE UN LADO' % Z['nombre'])
W.contact_sheet(fotos, 3, os.path.join(OUT, '_hoja.png'), title='MAPA V01 - ZONAS DESPUES DE LA PRADERA - SOLO LO VISUAL - RENDERS DE BLENDER (SIN PROBAR EN ROBLOX)')
a_jpg(os.path.join(OUT, '_hoja.png'), os.path.join(OUT, 'Mapa-v01-hoja.jpg'), 0.5)
A.write_json(os.path.join(OUT, 'datos.json'), {
    'pieza': 'Mapa v01: zonas después de la Pradera del Despegue (solo lo visual)', 'sin_probar_en_roblox': True,
    'zonas': [dict(clave=Z['clave'], nombre=Z['nombre'], marca_provisional=Z['marca'], y_inicio=Y_INICIO + i * LARGO,
                   y_fin=Y_INICIO + (i + 1) * LARGO) for i, Z in enumerate(ZONAS)],
    'carril_ancho_studs': ANCHO, 'zona_largo_studs': LARGO, 'triangulos': {'%s_%s' % (c, k): t for c, k, t in resumen},
    'textura': 'texturas/Mapa_paleta_256.png (un material para todas las piezas)',
    'ejes': 'Blender +Y = sentido del vuelo, +Z arriba; FBX global_scale=0.01, axis_forward=%s, axis_up=Y' % FBX_FORWARD})
A.log('listo')
