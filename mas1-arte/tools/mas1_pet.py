# Tramo comun de las mascotas altas del proyecto +1 (aguila, grifo, fenix): rig de los ocho huesos de las mascotas de Codex
# (Root, Body, Head, Tail, Wing_R/L, Tip_R/L) mas patas que cuelgan (Leg_R/L, y LegB_R/L en el grifo) y parpados (Lid_R/L),
# clips Fly / Glide / Celebrate a 30 fps en bucle y Blink (parpadeo, sin bucle), pintura de plumas y exportacion.
# Convenio de pose (el ala derecha manda; la izquierda sale espejada): aleteo + baja la punta del ala, barrido + la lleva hacia atras.
from mas1_lib import *
import contorno_negro as CN

BONES = ('Root', 'Body', 'Head', 'Tail', 'Wing_R', 'Tip_R', 'Wing_L', 'Tip_L', 'Leg_R', 'Leg_L', 'Lid_R', 'Lid_L')
BONES_PATAS_TRASERAS = ('LegB_R', 'LegB_L')     # solo el grifo (patas de leon)
PARPADO_DY = {'dy': 0.18}                         # cuanto avanza el parpado (studs) para tapar el ojo; lo fija cada mascota


def claro(h, k=0.28):
    c = A.hexrgb(h)
    c = c + (1 - c) * k
    return '#%02x%02x%02x' % tuple(int(round(float(v) * 255)) for v in c)


def chevrones(col, per=0.34, k=0.16, desv=0.45):
    """Barras en V de plumas pequenas (pecho, muslos): bandas que bajan hacia los lados."""
    c = A.hexrgb(col)

    def extra(P, msk, pos, nrm, cl):
        s_ = np.sin((pos[:, 2] + desv * np.abs(pos[:, 0])) * 2 * math.pi / per)
        m = np.clip((s_ - 0.35) * 3.0, 0, 1) * k
        return cl * (1 - m[:, None]) + c[None, :] * m[:, None]
    return extra


def hacer_pose(rig):
    def pose(wing=0, tip=0, bodyz=0.0, pitch=0.0, head=(0, 0, 0), tailp=0.0, tailw=0.0, wyaw=0.0, tyaw=0.0, legs=(0.0, 0.0), legsb=(0.0, 0.0),
             lid=0.0):
        for pb in rig.pose.bones:
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (0, 0, 0)
            pb.location = (0, 0, 0)
        for s, lado in ((1, 'R'), (-1, 'L')):
            rig.pose.bones['Wing_' + lado].rotation_euler = Euler((0, math.radians(s * wing), math.radians(-s * wyaw)), 'XYZ')
            rig.pose.bones['Tip_' + lado].rotation_euler = Euler((0, math.radians(s * tip), math.radians(-s * tyaw)), 'XYZ')
        rig.pose.bones['Body'].location = (0, 0, bodyz)
        rig.pose.bones['Body'].rotation_euler = Euler((math.radians(pitch), 0, 0), 'XYZ')
        rig.pose.bones['Head'].rotation_euler = Euler([math.radians(a) for a in head], 'XYZ')
        rig.pose.bones['Tail'].rotation_euler = Euler((math.radians(tailp), 0, math.radians(tailw)), 'XYZ')
        for (nombre, valores) in (('Leg', legs), ('LegB', legsb)):
            for k, lado in enumerate(('R', 'L')):
                if nombre + '_' + lado in rig.pose.bones:
                    rig.pose.bones[nombre + '_' + lado].rotation_euler = Euler((math.radians(valores[k]), 0, 0), 'XYZ')
        for lado in ('R', 'L'):
            if 'Lid_' + lado in rig.pose.bones:
                rig.pose.bones['Lid_' + lado].location = (0, PARPADO_DY['dy'] * lid, 0)
        bpy.context.view_layer.update()
    return pose


def _claves(c, t, wing=0.0, tip=0.0, bodyz=0.0, pitch=0.0, head=(0, 0, 0), tailp=0.0, tailw=0.0, wyaw=0.0, tyaw=0.0, legs=(0.0, 0.0),
            legsb=(0.0, 0.0), lid=0.0, traseras=False):
    for s, lado in ((1, 'R'), (-1, 'L')):
        c.k('Wing_' + lado, t, rot=(0, s * wing, -s * wyaw))
        c.k('Tip_' + lado, t, rot=(0, s * tip, -s * tyaw))
    c.k('Body', t, loc=(0, 0, bodyz), rot=(pitch, 0, 0))
    c.k('Head', t, rot=head)
    c.k('Tail', t, rot=(tailp, 0, tailw))
    c.k('Root', t)
    for k, lado in enumerate(('R', 'L')):
        c.k('Leg_' + lado, t, rot=(legs[k], 0, 0))
        c.k('Lid_' + lado, t, loc=(0, PARPADO_DY['dy'] * lid, 0))
        if traseras:
            c.k('LegB_' + lado, t, rot=(legsb[k], 0, 0))


def _suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


# Aleteo de una mascota (Maikol, 29/10): recoger -> extender -> impulsar -> recoger, con flexion del tramo exterior y la punta con retraso.
# Claves (fase, elevacion E del ala interior respecto al reposo en grados, caida relativa de la punta, barrido del hombro, flexion de la muneca hacia atras):
#   arriba y extendida -> empuje (la punta se queda atras, mas arriba) -> abajo -> recoge (muneca flexionada, primarias colgando) -> extiende arriba
ALETEO = [(0.00, 26, -6, 4, 0), (0.10, 22, -14, 3, 0), (0.28, -2, -26, 2, 0), (0.46, -44, -10, 8, 8),
          (0.60, -12, 20, 24, 46), (0.78, 22, 14, 28, 56), (0.90, 28, 0, 10, 14)]


def _ciclo(knots, fase):
    """Interpolacion suave y periodica entre las claves (fase en [0,1))."""
    f = fase % 1.0
    ks = knots + [(knots[0][0] + 1.0,) + tuple(knots[0][1:])]
    for i in range(len(ks) - 1):
        a, b = ks[i], ks[i + 1]
        fa = f if f >= a[0] else f + 1.0
        if a[0] <= fa <= b[0] + 1e-9:
            u = _suave((fa - a[0]) / (b[0] - a[0]))
            return [a[j] + (b[j] - a[j]) * u for j in range(1, len(a))]
    return list(knots[0][1:])


def clips_pet(rig, amp=None, aleteo=None):
    """Fly 1,0 s, Glide 2,0 s y Celebrate 2,0 s en bucle (la ultima clave repite la primera) y Blink 0,3 s (sin bucle, solo parpados).
    Las patas cuelgan ya en la pose neutra (estan modeladas colgando); los clips las balancean como un pendulo que va detras del cuerpo.
    Blink solo anima Lid_R/L: el juego lo reproduce cada 3-5 s con prioridad Action encima del clip de vuelo.
    amp: multiplicadores {'ala', 'cola', 'cabeza', 'cuerpo', 'pliegue', 'patas'} (1.0 por defecto); aleteo: lista de claves ALETEO propia."""
    k = dict(ala=1.0, cola=1.0, cabeza=1.0, cuerpo=1.0, pliegue=1.0, patas=1.0)
    k.update(amp or {})
    a, co, ca, cu, pl, pa = k['ala'], k['cola'], k['cabeza'], k['cuerpo'], k['pliegue'], k['patas']
    kn = aleteo or ALETEO
    traseras = 'LegB_R' in rig.pose.bones
    huesos = list(BONES) + (list(BONES_PATAS_TRASERAS) if traseras else [])

    def ala(fase, f=1.0):
        E, tipR, wy, ty = _ciclo(kn, fase)
        return dict(wing=-a * f * E, tip=a * f * tipR, wyaw=wy * pl, tyaw=ty * pl)

    def f_fly(t):
        p = t / 1.0
        d = ala(p)
        d.update(bodyz=cu * 0.20 * math.sin(2 * math.pi * (p - 0.15)), pitch=3 * math.cos(2 * math.pi * p),
                 head=(-3 * ca * math.cos(2 * math.pi * p), 0, 0), tailp=co * 8 * math.sin(2 * math.pi * (p + 0.6)),
                 # patas: pendulo que va detras de la subida del cuerpo (cuando el cuerpo sube, los pies se quedan atras y abajo)
                 legs=(pa * 11 * math.sin(2 * math.pi * (p - 0.40)), pa * 11 * math.sin(2 * math.pi * (p - 0.47))),
                 legsb=(pa * 9 * math.sin(2 * math.pi * (p - 0.45)), pa * 9 * math.sin(2 * math.pi * (p - 0.52))), traseras=traseras)
        return d

    def f_glide(t):
        p = 2 * math.pi * t / 2.0
        return dict(wing=a * (-6 - 3.5 * math.sin(p)), tip=a * (-4 + 5 * math.sin(p - 0.9)), bodyz=cu * 0.07 * math.sin(p),
                    pitch=2 * math.sin(p + 0.5), head=(0, 4 * ca * math.sin(p), 6 * ca * math.sin(p - 0.6)), tailw=co * 5 * math.sin(p),
                    wyaw=3, tyaw=0,
                    # planeo: las patas se van hacia atras (mas rectas, aerodinamicas) y apenas se mecen
                    legs=(pa * (-16 + 3 * math.sin(p - 1.0)), pa * (-16 + 3 * math.sin(p - 1.3))),
                    legsb=(pa * (-12 + 2 * math.sin(p - 1.1)), pa * (-12 + 2 * math.sin(p - 1.4))), traseras=traseras)

    def f_celebrate(t):
        p = (t / 1.0) % 1.0
        q = 2 * math.pi * t / 2.0
        d = ala(p, 1.22)
        d.update(bodyz=cu * 0.34 * (0.5 + 0.5 * math.sin(2 * math.pi * (p - 0.15))), pitch=-6 + 6 * math.sin(2 * q),
                 head=(-8 * ca * math.sin(2 * q), 0, 26 * ca * math.sin(2 * q + 0.4)),
                 tailp=co * 14 * math.sin(2 * q + 0.5), tailw=co * 18 * math.sin(2 * q),
                 # patadita: las patas patalean alternadas
                 legs=(pa * 24 * math.sin(2 * q), pa * 24 * math.sin(2 * q + math.pi)),
                 legsb=(pa * 16 * math.sin(2 * q + 0.6), pa * 16 * math.sin(2 * q + 0.6 + math.pi)), traseras=traseras)
        return d

    acts = {}
    # claves: en la fase de cada clave de ALETEO (Fly: 1 ciclo, Celebrate: 2) mas las de relleno que dan fluidez a la cabeza y la cola
    fases = sorted({round(x[0], 3) for x in kn} | {0.19, 0.37, 0.53, 0.69, 0.84, 0.95})
    for nombre, dur, fn, ciclos in (('Fly', 1.0, f_fly, 1), ('Glide', 2.0, f_glide, 0), ('Celebrate', 2.0, f_celebrate, 2)):
        c = A.Clip(rig, nombre, dur, loop=True, fps=30)
        if ciclos == 0:
            ts = [dur * i / 8 for i in range(9)]
        else:
            ts = sorted({dur * (cy + f) / ciclos for cy in range(ciclos) for f in fases} | {dur})
        for t in ts:
            _claves(c, t, **fn(min(t, dur - 1e-9) if t >= dur else t))
        # cierre exacto del bucle: la ultima clave repite la primera
        acts[nombre] = c.build(huesos)
    acts['Blink'] = clip_parpadeo(rig)
    return acts, {'Fly': 1.0, 'Glide': 2.0, 'Celebrate': 2.0, 'Blink': DUR_PARPADEO}


DUR_PARPADEO = 8 / 30.0


def clip_parpadeo(rig):
    """Blink (8 fotogramas a 30 fps, sin bucle): los parpados avanzan y tapan el ojo (fotogramas 2-5) y vuelven (8). Claves en
    fotogramas enteros: el FBX se exporta sin canales constantes (solo Lid_R/L) y asi no se pierde ninguna clave al simplificar."""
    c = A.Clip(rig, 'Blink', DUR_PARPADEO, loop=False, fps=30)
    for f, cerrado in ((0, 0.0), (2, 1.0), (5, 1.0), (8, 0.0)):
        for lado in ('R', 'L'):
            c.k('Lid_' + lado, f / 30.0, loc=(0, PARPADO_DY['dy'] * cerrado, 0))
    return c.build(['Lid_R', 'Lid_L'])


def en(rig, acts, nombre, t):
    A.set_action(rig, acts[nombre])
    bpy.context.scene.frame_set(int(round(t * 30)))
    bpy.context.view_layer.update()


def exportar_pet(out, nombre, ob, rig, acts, clips, pose0, datos):
    """FBX del rig (pose neutra), un FBX por clip, GLB con los clips, .blend (con las pistas NLA silenciadas) y datos.json."""
    rig.animation_data_clear()
    pose0()
    fbx(os.path.join(out, nombre + '_Rig.fbx'), [ob, rig], False)
    for c in clips:
        A.set_action(rig, acts[c])
        fbx(os.path.join(out, 'clips', '%s_%s.fbx' % (nombre, c)), [ob, rig], True, todos_huesos=(c != 'Blink'))
    glb_con_clips(os.path.join(out, nombre + '.glb'), ob, rig, acts)
    for tr in rig.animation_data.nla_tracks:
        tr.mute = True
    pose0()
    A.save_blend(os.path.join(out, nombre + '.blend'))
    base = {'clips_30fps': {k: {'duracion_s': v, 'frames': int(round(v * 30)), 'bucle': k != 'Blink'} for k, v in clips.items()},
            'textura': 'texturas/%s_paleta_1024.png (1024, un material, una malla)' % nombre,
            'ejes': 'Blender +Y delante, +Z arriba, +X derecha; FBX axis_forward=%s axis_up=Y global_scale=0.01' % FBX_FORWARD,
            'sin_probar_en_roblox': True}
    base.update(datos)
    A.write_json(os.path.join(out, 'datos.json'), base)


# ------------------------------------------------------------------ escena de comprobacion (maniqui R15 de 5,2 studs, plataforma, luces) y fotos
class Escena:
    def __init__(self, CR, CC, prev, fase, radio=11.5, maniqui=(-6.0, 0.4), regla=(6.6, 0.4), objetivo=(-0.9, -0.3, 2.0)):
        self.CC, self.prev, self.fase, self.objetivo = CC, prev, fase, Vector(objetivo)
        self.figs = A.reference_figure(CR, x=maniqui[0], y=maniqui[1], h=5.2)
        mbp = A.MB('Plataforma')
        mbp.cyl((0, 0, -0.25), (0, 0, 0.0), radio, 48, 'ref', rot=0.0)
        plat = mbp.finish(CR)
        plat.data.materials.clear()
        plat.data.materials.append(A.flat_mat('Plataforma', (0.40, 0.48, 0.57)))
        self.rul = A.ruler(CR, regla[0], regla[1], h=6.0, w=0.25)
        for o in self.rul:
            o.hide_render = True
        sol(CC, 'Sol', 3.0, (-0.35, -0.55, -0.75))
        sol(CC, 'Relleno', 1.0, (0.55, -0.35, -0.45), 20.0)
        sol(CC, 'Contraluz', 0.9, (0.0, 0.7, -0.3), 12.0)
        A.setup_world((0.50, 0.60, 0.72), 1.15)
        self.res = (1100, 880) if fase in ('geo', 'check') else (1200, 960)
        self.muestras = 20 if fase in ('geo', 'check') else 48
        self.ext = 'png' if fase == 'geo' else 'jpg'
        A.setup_render(self.res, 'CYCLES', self.muestras)

    def formato(self):
        s = bpy.context.scene.render.image_settings
        s.file_format = 'JPEG' if self.ext == 'jpg' else 'PNG'
        if self.ext == 'jpg':
            s.quality = 92

    def reiniciar_render(self):
        A.setup_render(self.res, 'CYCLES', self.muestras)
        self.formato()

    def foto(self, name, az, el, dist, target=None, lens=50.0, scale=False):
        """az=180: camara delante de la mascota (+Y) mirando de frente; az=0: por detras; az=90: desde su derecha."""
        t = Vector(target) if target is not None else self.objetivo
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        cam = A.camera(self.CC, 'cam_' + name, t + d * dist, t, lens=lens)
        for o in self.rul:
            o.hide_render = not scale
        self.formato()
        path = os.path.join(self.prev, name + '.' + self.ext)
        A.render(path, cam)
        return path


def planos(ob, PAL):
    """Materiales planos por region para la fase de geometria."""
    for s in ob.material_slots:
        s.material = A.flat_mat('F_' + s.material.name[2:], lin(PAL[s.material.name[2:]]), 0.85)


def hornear(ob, R, ao_dist=0.5):
    """UV + mapas de datos de Cycles; devuelve el pintor (A.Paint). Deja libre la esquina superior derecha del atlas para el texel negro
    del contorno (las UV se encogen un 4 %)."""
    A.uv_unwrap([ob], angle=52.0, margin=0.004)
    CN.reservar_esquina_negra(ob, 0.96)
    maps = A.bake_maps([ob], 2048, R, ao_dist, 0.05, samples=16)
    return A.Paint(maps, R)


def rellenar_bordes(Pn, iters=10):
    """Sangrado de las islas UV: extiende el color de cada isla unos texeles hacia el fondo negro para que el filtrado y los mipmaps de Roblox
    no mezclen los bordes de las caras con negro (lineas oscuras entre caras al alejarse). Devuelve la mascara de texeles ocupados."""
    img = Pn.img
    occ = Pn.ids > 0
    for _ in range(iters):
        acc = np.zeros_like(img)
        cnt = np.zeros(occ.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(img, (dy, dx), axis=(0, 1))
            so = np.roll(occ, (dy, dx), axis=(0, 1))
            acc += sh * so[..., None]
            cnt += so
        nuevo = (~occ) & (cnt > 0)
        img[nuevo] = acc[nuevo] / cnt[nuevo][:, None]
        occ = occ | nuevo
    return occ


def guardar_textura(Pn, ob, out, nombre):
    rellenar_bordes(Pn)
    CN.pintar_esquina_negra(Pn.img, 0.03)
    tex = os.path.join(out, 'texturas', nombre + '_paleta_1024.png')
    Pn.save(tex, out_size=1024)
    A.assign_final([ob], A.final_material(nombre, tex))
    A.log('textura pintada', tex)


# ------------------------------------------------------------------ variante con contorno negro grueso (referencia: Steal an Egg)
def variante_contorno(ob, rig, E, nombre, out, vistas, acts, grosor=0.10):
    """Crea la variante con carcasa invertida, renderiza `vistas` (lista de (nombre, az, el, dist, objetivo, clip, t)) y exporta su rig.
    Devuelve (rutas de los renders, poligonos antes, poligonos despues). La mascota base queda intacta."""
    col = ob.users_collection[0]
    # objeto de exportacion (un solo material, UV de la carcasa en el texel negro)
    ob2 = ob.copy()
    ob2.data = ob.data.copy()
    ob2.name = nombre + '_Contorno'
    col.objects.link(ob2)
    ob2.parent = rig
    ob2.matrix_world = ob.matrix_world.copy()
    n0, n1 = CN.agregar_contorno(ob2, grosor)
    # objeto solo para los renders: la carcasa con su material especial de Cycles
    obp = ob2.copy()
    obp.data = ob2.data.copy()
    obp.name = nombre + '_ContornoVista'
    col.objects.link(obp)
    obp.parent = rig
    obp.matrix_world = ob.matrix_world.copy()
    n_carcasa = CN.separar_carcasa_para_vista(obp, CN.material_contorno_vista())
    A.log('contorno: %d -> %d poligonos (%d de carcasa)' % (n0, n1, n_carcasa))
    ob.hide_render = True
    ob2.hide_render = True
    rutas = []
    for (nom, az, el, dist, objetivo, clip, t) in vistas:
        if clip:
            en(rig, acts, clip, t)
        else:
            rig.animation_data_clear()
        rutas.append((E.foto(nom, az, el, dist, target=objetivo), nom))
    obp.hide_render = True
    ob.hide_render = False
    # exportacion de la variante (mismo rig y mismos clips que la base: solo cambia la malla)
    rig.animation_data_clear()
    for b in rig.pose.bones:
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    ob.hide_render = False
    fbx(os.path.join(out, nombre + '_Contorno_Rig.fbx'), [ob2, rig], False)
    return rutas, n0, n1


def anotar_contorno(out, nombre, n0, n1, grosor):
    """Añade a datos.json lo de la variante con contorno."""
    ruta = os.path.join(out, 'datos.json')
    d = json.load(open(ruta, encoding='utf-8'))
    d['contorno'] = {'archivo': nombre + '_Contorno_Rig.fbx', 'grosor_studs': grosor, 'poligonos_sin_contorno': n0, 'poligonos_con_contorno': n1,
                     'nota': 'Carcasa invertida dentro de la misma malla (mismo material: UV al texel negro de la esquina superior derecha del atlas). '
                             'Poner CastShadow = false en el MeshPart de esta variante: la carcasa cerrada ensombrecería a la mascota. '
                             'Los clips de la variante sin contorno sirven (mismos huesos). Sin probar en Roblox.'}
    A.write_json(ruta, d)


def hoja_contorno(rutas, out, nombre_hoja, titulo):
    W.contact_sheet([(p, lab.upper().replace('-', ' ')) for p, lab in rutas], 2, os.path.join(out, 'previews', '_hc.png'), title=titulo)
    a_jpg(os.path.join(out, 'previews', '_hc.png'), os.path.join(out, 'previews', nombre_hoja), 0.5)
