# Versiones MASCOTA de los seis enemigos voladores para «+1 de lanzamiento por segundo» (Maikol, 30/10: los enemigos también se consiguen
# como mascotas, y las mascotas solo salen de los huevos alados). Misma pieza voxel que el enemigo v02, pero con la cara amable (sin ceño,
# sonrisa, mejillas rosas y los mismos ojos pequeños con brillo, como las mascotas de Codex y Antigravity), más pequeña según su rareza
# (tabla del director en mas1-juego/src/Mascotas.lua) y con los clips de mascota Fly (1,0 s), Glide (2,0 s) y Celebrate (2,0 s) en bucle
# y Blink (solo párpados). Reutiliza construir() de los scripts de enemigos (se importan sin construir nada) cambiando su cara.
# blender -b --factory-startup --python-exit-code 1 -P build_mascotas_enemigos.py
#   MASCOTA_FASE=geo | check | full (por defecto);  MASCOTA_SOLO=<id de Mascotas.lua: nube, globo, nubarron, ovni, meteorito, cometa>
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo la pieza. Sin probar en Roblox.
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for v in ('NUBE_SOLO', 'ESPACIO_SOLO', 'CIELO_SOLO'):
    os.environ[v] = '-'                                          # al importarlos, los scripts de enemigos no construyen nada
import build_enemigo_nube as bn
import build_enemigo_espacio as be
import build_enemigo_cielo as bc
from mas1_enemigo import *

FASE = os.environ.get('MASCOTA_FASE', 'full')
SOLO = os.environ.get('MASCOTA_SOLO')
BASE_OUT = os.path.abspath(os.path.join(HERE, '..', 'mascotas-enemigos-v01'))
CARA_MASCOTA = {'pupila': '#1d1626', 'ojo': '#ffffff', 'boca': '#3a1a2a', 'mejilla': '#ff9fb5'}

bn.cara_nube = lambda MBS: cara_amable(MBS, bn.OJO[0], bn.OJO[2], frente_de(MBS['Body']), tam=bn.OJO_TAM)[0]
be.cara = cara_amable
bc.cara = cara_amable


def aleteo_nube(a, p):
    """Las nubecitas laterales aletean como alas; el rayo del nubarrón se balancea detrás."""
    f = 9 * a * math.sin(p)
    return {'Puff_R': ((0, 0, 0.06 * a * math.sin(p)), (0, -f, 0)), 'Puff_L': ((0, 0, 0.06 * a * math.sin(p)), (0, f, 0)),
            'Bolt': ((0, 0, 0), (0, 10 * math.sin(p - 0.8), 0))}


def vuelo_de(mid):
    """vuelo(modo, t, p) -> (cuerpo, extra) de cada mascota: sube y baja inclinada hacia delante, con sus piezas propias en marcha."""
    def vuelo(modo, t, p):
        a = {'fly': 1.0, 'glide': 0.45, 'celebrate': 0.8}[modo]
        dur = 1.0 if modo == 'fly' else 2.0
        if mid in ('nube', 'nubarron'):
            ex = aleteo_nube(a, p)
        elif mid == 'globo':
            ex = {'String': ((0, 0, 0), (8 * a * math.sin(p - 0.9), 12 * a * math.sin(p - 0.7), 0))}
        elif mid == 'cometa':
            ex = {'Tail_%d' % (k + 1): ((0, 0, 0), (4 * a * math.sin(2 * p - 0.8 * k), 14 * a * math.sin(p - 0.7 * (k + 1)), 0)) for k in range(3)}
        elif mid == 'ovni':
            ex = {'Rim': ((0, 0, 0), (0, 0, 360.0 * t / dur)), 'Alien': ((0, 0, 0.05 * math.sin(2 * p)), (0, 0, 8 * a * math.sin(p))),
                  'Antenna': ((0, 0, 0), (10 * math.sin(2 * p + 0.6), 8 * math.sin(p + 1.1), 0))}
        else:                                                                           # meteorito: la cola de fuego tiembla
            ex = {'Tail': ((0, 0, 0), (6 * math.sin(3 * p), 0, 7 * math.sin(2 * p + 0.5)))}
        if modo == 'celebrate':
            return ((0, 0, 0), (0, 0, 0)), ex
        return ((0, 0, 0.16 * a * math.sin(p - 0.3)), (-6 * a + 2 * math.sin(p), 3 * a * math.sin(p + 0.5), 0)), ex
    return vuelo


# id de Mascotas.lua, script, clave del enemigo, nombre del modelo, escala respecto al enemigo, rareza
MASCOTAS = [('nube', bn, 'nube-grunona', 'MascotaNube', 0.62, 'POCO COMUN'), ('globo', bc, 'globo', 'MascotaGlobo', 0.75, 'POCO COMUN'),
            ('nubarron', bn, 'nubarron', 'MascotaNubarron', 0.70, 'RARO'), ('ovni', be, 'ovni', 'MascotaOvni', 0.70, 'RARO'),
            ('meteorito', be, 'meteorito', 'MascotaMeteorito', 0.95, 'EPICO'), ('cometa', bc, 'cometa', 'MascotaCometa', 0.80, 'EPICO')]

resumen = []
for mid, mod, clave, nombre, k, rareza in MASCOTAS:
    if SOLO and mid != SOLO:
        continue
    var = dict(next(v for v in mod.VARIANTES if v['clave'] == clave))
    var['nombre'] = nombre
    var['pal'] = dict(var['pal'], **CARA_MASCOTA)
    OUT = os.path.join(BASE_OUT, mid)
    PREV = os.path.join(OUT, 'previews')
    for d in ('', 'texturas', 'clips', 'previews'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    ob, rig, HUESOS, PAL, CR, CC, DY = mod.construir_nube(var) if mod is bn else mod.construir(var)
    escalar(ob, rig, k)
    TRIS = A.tris([ob])
    mn = Vector([min(v.co[a] for v in ob.data.vertices) for a in range(3)])
    mx = Vector([max(v.co[a] for v in ob.data.vertices) for a in range(3)])
    BOUNDS = dict(ancho=round(mx.x - mn.x, 2), alto=round(mx.z - mn.z, 2), fondo=round(mx.y - mn.y, 2), z_min=round(mn.z, 2))
    SUELTAS, N_ISLAS = piezas_sueltas(ob)
    COPL, EJ = caras_coplanares(ob)
    A.log(mid, 'triangulos', TRIS, BOUNDS, 'sueltas', len(SUELTAS), 'de', N_ISLAS, 'coplanares', COPL, EJ[:4])
    if FASE == 'check':
        continue
    objetivo = Vector(var.get('objetivo', (-0.3, 0.0, 2.0))) * k
    cara_t = Vector(var.get('cara', (0, 0.9, 2.3))) * k
    E = Escena(CR, CC, PREV, 'geo' if FASE == 'geo' else 'full', radio=6.0, maniqui=(-3.0, 0.4), regla=(3.2, 0.4), objetivo=tuple(objetivo))
    shot = E.foto
    pref = 'Mascota-' + mid
    if FASE == 'geo':
        planos(ob, PAL)
        pose0(rig)
        shot('_geo_frente', 180, 8, 11.0, scale=True)
        shot('_geo_34', 148, 14, 10.0)
        shot('_geo_cara', 180, 4, 4.5, target=tuple(cara_t))
        continue
    Pn = hornear(ob, 3.0)
    E.reiniciar_render()
    BASE = dict(var=0.04, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.05, ao=0.55, ao_tint='#6f6ab8', light=0.22,
                hue_var=0.02, blotch=0.05, edge=0.45, edge_th=0.05, edge_break=0.3)
    PLANO = dict(edge=0.0, var=0.0, ao=0.1, light=0.0, face_var=0.0)
    for i, name in enumerate(list(A.REGIONS)):
        if name not in PAL:
            continue                                                           # regiones de la escena (plataforma, maniquí)
        kw = dict(BASE)
        if name in ('pupila', 'boca', 'mejilla', 'brillo'):
            kw.update(PLANO)
        elif name == 'ojo':
            kw.update(PLANO, edge_col='#ffffff')
        elif name == 'parpado':
            kw.update(PLANO, ao=0.0)                                           # escondido: sin oclusión
        elif name in ('luz', 'emisor', 'lava', 'fuego_claro', 'rayo', 'rayo_claro'):
            kw.update(edge_col='#ffffff', var=0.02, ao=0.10, light=0.08)
        elif name in ('fuego', 'fuego_osc'):
            kw.update(stroke=(6.0, 1.0, 1.0), var=0.05, ao=0.15)
        elif name == 'nube':
            kw.update(grad=0.2)
        kw.setdefault('edge_col', claro(PAL[name]))
        Pn.region(name, PAL[name], seed=1 + i, **kw)
    guardar_textura(Pn, ob, OUT, nombre)
    acts, CLIPS = clips_mascota(rig, DY, k, vuelo_de(mid))
    rig.animation_data_clear()
    pose0(rig)
    shots = []
    shots.append((shot(pref + '-frente', 180, 8, 11.0, scale=True), 'FRENTE (REGLA 6 STUDS) - MASCOTA %s (%s)' % (var['titulo'], rareza)))
    shots.append((shot(pref + '-tres-cuartos', 148, 14, 10.0), '3/4'))
    shots.append((shot(pref + '-cara', 180, 4, 4.5, target=tuple(cara_t)), 'CARA AMABLE'))
    shots.append((shot(pref + '-lateral', 90, 6, 10.0), 'LATERAL'))
    en(rig, acts, 'Fly', 0.25)
    shots.append((shot(pref + '-vuelo', 150, 10, 10.0), 'VUELO (FLY)'))
    en(rig, acts, 'Glide', 0.5)
    shots.append((shot(pref + '-planeo', 150, 10, 10.0), 'PLANEO (GLIDE)'))
    en(rig, acts, 'Celebrate', 0.85)
    shots.append((shot(pref + '-celebra', 160, 12, 11.0), 'CELEBRA (CELEBRATE)'))
    rig.animation_data_clear()                                     # Blink solo mueve los párpados: el resto vuelve a la pose neutra
    pose0(rig, DY * k, 1.0)
    shots.append((shot(pref + '-parpadeo', 180, 4, 4.5, target=tuple(cara_t)), 'PARPADEO (BLINK)'))
    W.contact_sheet(shots, 4, os.path.join(PREV, '_hoja.png'), title='MASCOTA %s V01 (%s) - VERSION AMABLE DEL ENEMIGO - RENDERS DE BLENDER' % (var['titulo'], rareza))
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, pref + '-hoja.jpg'), 0.5)
    E.reiniciar_render()
    exportar_pet(OUT, nombre, ob, rig, acts, CLIPS, lambda: pose0(rig), {
        'pieza': 'Mascota %s v01: versión amable del enemigo (sale de los huevos alados)' % var['titulo'], 'id_mascota': mid,
        'rareza': rareza, 'escala_respecto_al_enemigo': k, 'triangulos': TRIS, 'limites_studs': BOUNDS, 'huesos': [h[0] for h in HUESOS],
        'paleta': PAL, 'parpadeo_dy_studs': round(DY * k, 3), 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPL},
        sin_bucle=('Blink',))
    resumen.append((mid, TRIS, BOUNDS, len(SUELTAS), COPL))
A.log('RESUMEN', resumen)
A.log('listo')
