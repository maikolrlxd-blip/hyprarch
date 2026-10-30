# Tramo común de los enemigos voladores del proyecto +1 (ovni, meteorito, globo, cometa): cara enfadada (ojos diminutos con brillo,
# párpados en Lid_R/L, cejas en Brow, morro gruñón) colocada sobre la superficie por rayos, claves y clips Idle (2,0 s, bucle),
# Hit (0,5 s), Defeat (1,0 s) y Blink (8 fotogramas, solo párpados). Las nubes llevan su propia versión en build_enemigo_nube.py.
# En Roblox un hueso no se escala: el golpe mueve piezas; encoger o desvanecer al derrotarlos lo hace el juego.
# Versión mascota (Maikol, 30/10: los enemigos también salen de los huevos como mascotas): cara_amable(), escalar() y clips_mascota().
from mas1_ave import *
from mathutils.bvhtree import BVHTree
import mas1_pet

BASICOS = ('Root', 'Body', 'Brow', 'Lid_R', 'Lid_L')
# golpe: (t, cuerpo hacia atrás, inclinación hacia atrás, cejas arriba, párpados); derrota: (t, y, z, inclinación, vuelta, párpados)
GOLPE = ((0.0, 0, 0, 0, 0), (0.07, -0.40, 16, 0.09, 1), (0.20, 0.08, -5, 0.03, 1), (0.32, -0.03, 2, 0.0, 0.3), (0.5, 0, 0, 0, 0))
DERROTA = ((0.0, 0, 0, 0, 0, 0), (0.08, -0.40, 0.05, 16, 0, 1), (0.30, -0.6, 0.15, 10, 120, 1), (0.55, -0.8, -0.30, 20, 240, 1),
           (0.80, -0.9, -0.90, 30, 330, 1), (1.0, -1.0, -1.30, 34, 360, 1))


def _h(i, seed):
    h = (i * 73856093) ^ (seed * 2654435761)
    return ((h >> 3) & 0xffff) / 65535.0


def _h3(i, j, k, seed):
    h = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (seed * 2654435761)
    return ((h >> 3) & 0xffff) / 65535.0


def torno_facetado(mb, perfil, n, region):
    """Superficie de revolución facetada (como la cáscara de los huevos): perfil = [(r, z)] de abajo arriba, con r = 0 en los polos;
    los anillos impares van girados medio lado y cada banda se parte en triángulos. region(banda, centro) -> nombre de región."""
    anillos = []
    for k, (r, z) in enumerate(perfil):
        if r < 1e-6:
            anillos.append([mb.bm.verts.new((0.0, 0.0, z))])
            continue
        o = 0.5 * (k % 2)
        anillos.append([mb.bm.verts.new((r * math.cos((j + o) * 2 * math.pi / n), r * math.sin((j + o) * 2 * math.pi / n), z))
                        for j in range(n)])

    def tri(b, vs):
        c = sum((v.co for v in vs), Vector()) / len(vs)
        mb.face(vs, region(b, c))
    for b in range(len(anillos) - 1):
        L, U = anillos[b], anillos[b + 1]
        for j in range(n):
            j1 = (j + 1) % n
            if len(L) == 1:
                tri(b, [L[0], U[j1], U[j]])
            elif len(U) == 1:
                tri(b, [L[j], L[j1], U[0]])
            elif b % 2 == 0:            # el anillo de arriba va medio lado por delante
                tri(b, [L[j], L[j1], U[j]])
                tri(b, [U[j], L[j1], U[j1]])
            else:
                tri(b, [L[j], L[j1], U[j1]])
                tri(b, [U[j], L[j], U[j1]])


def frente_de(mb):
    """y de la cara delantera de lo que ya hay en el MB, mirando desde delante (+Y) en (x, z)."""
    bm = mb.bm.copy()
    bm.normal_update()
    arbol = BVHTree.FromBMesh(bm)

    def f(x, z):
        hit = arbol.ray_cast(Vector((x, 9.0, z)), Vector((0, -1, 0)))
        return hit[0].y if hit[0] is not None else 0.0
    return f


def cara(MBS, ojo_x, z_ojos, frente_en, tam=(0.20, 0.15, 0.26), sep_ceja=0.28, z_boca=None, boca=1.0):
    """Ojos diminutos con brillo, párpados, cejas enfadadas (hueso Brow) y morro gruñón sobre una superficie cuyo frente en (x, z) da
    frente_en(x, z) (y de la superficie). Los párpados van en la región 'parpado' (del color de la piel, pintada sin oclusión).
    Devuelve (dy del párpado, centro de la ceja)."""
    dy = 0.0
    y_ojo = max(frente_en(s * ojo_x, z_ojos) for s in (-1, 1)) + tam[1] / 2 - 0.05
    for s, lado in ((1, 'R'), (-1, 'L')):
        c = (s * ojo_x, y_ojo, z_ojos)
        MBS['Body'].box(c, tam, 'pupila')
        frente = y_ojo + tam[1] / 2
        MBS['Body'].box((s * (ojo_x - 0.04), frente + 0.015, z_ojos + 0.06), (0.07, 0.04, 0.08), 'ojo')
        dy = parpado(MBS['Lid_' + lado], c, tam, frente + 0.035, 'parpado', 'boca')
    z_c = z_ojos + sep_ceja
    y_c = max(frente_en(s * ojo_x, z_c) for s in (-1, 1)) + 0.02
    for s in (1, -1):
        cubo_girado(MBS['Brow'], (s * (ojo_x + 0.01), y_c, z_c), (0.40, 0.14, 0.12), 'ceja', rot=(0, -s * 22, 0))
    z_b = z_boca if z_boca is not None else z_ojos - 0.30
    y_b = max(frente_en(x, z_b) for x in (-0.27, 0.0, 0.27))
    frown = [(-0.27, -0.05), (-0.14, 0.04), (0.14, 0.04), (0.27, -0.05), (0.20, -0.10), (0.10, -0.04), (-0.10, -0.04), (-0.20, -0.10)]
    MBS['Body'].prism([(boca * x, z_b + boca * z) for x, z in frown], y_b - 0.06, y_b + 0.07, 'boca', plane='XZ')
    return dy, (0.0, y_c, z_c)


def cara_amable(MBS, ojo_x, z_ojos, frente_en, tam=(0.20, 0.15, 0.26), sep_ceja=0.28, z_boca=None, boca=1.0):
    """Cara de la versión mascota (como las mascotas de Codex y Antigravity): los mismos ojos diminutos con brillo y párpados, sin cejas,
    sonrisa y mejillas rosas. Mismos argumentos y resultado que cara() para poder cambiar una por otra; el hueso Brow queda vacío."""
    dy = 0.0
    y_ojo = max(frente_en(s * ojo_x, z_ojos) for s in (-1, 1)) + tam[1] / 2 - 0.05
    for s, lado in ((1, 'R'), (-1, 'L')):
        c = (s * ojo_x, y_ojo, z_ojos)
        MBS['Body'].box(c, tam, 'pupila')
        frente = y_ojo + tam[1] / 2
        MBS['Body'].box((s * (ojo_x - 0.04), frente + 0.015, z_ojos + 0.06), (0.07, 0.04, 0.08), 'ojo')
        dy = parpado(MBS['Lid_' + lado], c, tam, frente + 0.035, 'parpado', 'boca')
        xm, zm = s * (ojo_x + 0.13), z_ojos - 0.19                 # mejilla: plaquita rosa debajo y por fuera del ojo
        while min(abs((zm + d - 0.1) / 0.2 - round((zm + d - 0.1) / 0.2)) * 0.2 for d in (-0.045, 0.045)) < 0.03:
            zm -= 0.01                                             # sus caras de arriba y abajo, lejos de los planos de voxel (z = 0,1 + 0,2 n)
        MBS['Body'].box((xm, frente_en(xm, zm), zm), (0.17, 0.08, 0.09), 'mejilla')   # sale 0,04 de la superficie
    z_b = z_boca if z_boca is not None else z_ojos - 0.30
    y_b = max(frente_en(x, z_b) for x in (-0.27, 0.0, 0.27))
    sonrisa = [(-0.27, 0.05), (-0.14, -0.04), (0.14, -0.04), (0.27, 0.05), (0.20, 0.10), (0.10, 0.04), (-0.10, 0.04), (-0.20, 0.10)]
    MBS['Body'].prism([(boca * x, z_b + boca * z) for x, z in sonrisa], y_b - 0.06, y_b + 0.07, 'boca', plane='XZ')
    z_c = z_ojos + sep_ceja
    return dy, (0.0, max(frente_en(s * ojo_x, z_c) for s in (-1, 1)) + 0.02, z_c)


def escalar(ob, rig, k):
    """Escala la pieza entera desde el origen (malla y huesos en reposo): la mascota queda más pequeña que el enemigo sin rehacerla."""
    if abs(k - 1.0) < 1e-6:
        return
    ob.data.transform(Matrix.Scale(k, 4))
    ob.data.update()
    A.select_only([rig])
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in rig.data.edit_bones:
        eb.head = eb.head * k
        eb.tail = eb.tail * k
    bpy.ops.object.mode_set(mode='OBJECT')


# celebrar: (t, salto, vuelta, balanceo, párpados): coge impulso, salta dando una vuelta entera con los ojos entornados de alegría,
# aterriza y se menea contento
CELEBRAR = ((0.0, 0, 0, 0, 0), (0.25, -0.10, 0, 0, 0), (0.55, 0.60, 180, 0, 0.5), (0.85, 0.70, 360, 0, 0.5), (1.15, 0.0, 360, 0, 0),
            (1.35, -0.06, 360, 8, 0), (1.60, 0.04, 360, -8, 0), (1.85, 0.0, 360, 4, 0), (2.0, 0.0, 360, 0, 0))


def clips_mascota(rig, dy, k, vuelo):
    """Clips de la versión mascota, como las mascotas aladas: Fly 1,0 s, Glide 2,0 s y Celebrate 2,0 s en bucle y Blink.
    vuelo(modo, t, p) -> (cuerpo (loc, rot), extra) con modo 'fly' | 'glide' | 'celebrate' y p la fase en radianes. Las traslaciones se
    escriben a tamaño de enemigo y se multiplican por k (escala de la mascota)."""
    huesos = [b.name for b in rig.data.bones]

    def esc(loc):
        return tuple(k * v for v in loc)
    acts = {}
    for nombre, dur in (('Fly', 1.0), ('Glide', 2.0)):
        c = A.Clip(rig, nombre, dur, loop=True, fps=30)
        for i in range(13):
            t = dur * i / 12
            (bl, br), ex = vuelo(nombre.lower(), t, 2 * math.pi * t / dur)
            claves(c, rig, t, dy * k, body=(esc(bl), br), extra={b: (esc(l), r) for b, (l, r) in ex.items()})
        acts[nombre] = c.build(huesos)
    c = A.Clip(rig, 'Celebrate', 2.0, loop=True, fps=30)
    for t, z, giro, balanceo, lid in CELEBRAR:
        (bl, br), ex = vuelo('celebrate', t, 2 * math.pi * t / 2.0)
        cuerpo = (esc((bl[0], bl[1], bl[2] + z)), (br[0], br[1] + balanceo, br[2] + giro))
        claves(c, rig, t, dy * k, body=cuerpo, lid=lid, extra={b: (esc(l), r) for b, (l, r) in ex.items()})
    acts['Celebrate'] = c.build(huesos)
    mas1_pet.PARPADO_DY['dy'] = dy * k
    acts['Blink'] = clip_parpadeo(rig)
    return acts, {'Fly': 1.0, 'Glide': 2.0, 'Celebrate': 2.0, 'Blink': DUR_PARPADEO}


def claves(c, rig, t, dy, body=((0, 0, 0), (0, 0, 0)), brow=0.0, lid=0.0, extra=None):
    """Una clave de todos los huesos: los básicos y, para cada hueso propio del enemigo, lo que diga extra {hueso: (loc, rot)} o reposo."""
    c.k('Root', t)
    c.k('Body', t, loc=body[0], rot=body[1])
    if 'Brow' in rig.pose.bones:
        c.k('Brow', t, loc=(0, 0, brow))
    for lado in ('R', 'L'):
        c.k('Lid_' + lado, t, loc=(0, dy * lid, 0))
    for b in rig.pose.bones:
        if b.name not in BASICOS:
            loc, rot = (extra or {}).get(b.name, ((0, 0, 0), (0, 0, 0)))
            c.k(b.name, t, loc=loc, rot=rot)


def clips_enemigo(rig, dy, idle, golpe=None, derrota=None):
    """idle(t, p) -> (cuerpo (loc, rot), cejas, extra) con p la fase en radianes; golpe(i, rx) y derrota(i, rz) -> extra de la clave i
    de GOLPE / DERROTA. Devuelve (acciones, duraciones)."""
    huesos = [b.name for b in rig.data.bones]
    acts = {}
    c = A.Clip(rig, 'Idle', 2.0, loop=True, fps=30)
    for i in range(13):
        t = 2.0 * i / 12
        body, brow, ex = idle(t, 2 * math.pi * t / 2.0)
        claves(c, rig, t, dy, body=body, brow=brow, extra=ex)
    acts['Idle'] = c.build(huesos)
    c = A.Clip(rig, 'Hit', 0.5, loop=False, fps=30)                  # golpe: sale hacia atrás, cierra los ojos y sube las cejas
    for i, (t, by, rx_, brow, lid) in enumerate(GOLPE):
        claves(c, rig, t, dy, body=((0, by, 0), (rx_, 0, 0)), brow=brow, lid=lid, extra=golpe(i, rx_) if golpe else None)
    acts['Hit'] = c.build(huesos)
    c = A.Clip(rig, 'Defeat', 1.0, loop=False, fps=30)               # derrota: golpe, vuelta entera y caída (el juego lo encoge y desvanece)
    for i, (t, by, bz, rx_, rz_, lid) in enumerate(DERROTA):
        claves(c, rig, t, dy, body=((0, by, bz), (rx_, 0, rz_)), brow=0.06, lid=lid, extra=derrota(i, rz_) if derrota else None)
    acts['Defeat'] = c.build(huesos)
    mas1_pet.PARPADO_DY['dy'] = dy
    acts['Blink'] = clip_parpadeo(rig)
    return acts, {'Idle': 2.0, 'Hit': 0.5, 'Defeat': 1.0, 'Blink': DUR_PARPADEO}


def pose0(rig, dy=0.0, lid=0.0):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
    for lado in ('R', 'L'):
        rig.pose.bones['Lid_' + lado].location = (0, dy * lid, 0)
    bpy.context.view_layer.update()
