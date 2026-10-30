# Huevos voladores con alas por rareza para «+1 de lanzamiento por segundo». Idea de Maikol (29/10/2026): los cofres voladores dan alas y los
# huevos voladores con alas dan mascotas; cuanto más raro el huevo, más rara la mascota. Mismo modelo para las cinco rarezas: cáscara facetada
# low-poly (torno de 16 lados con los anillos girados medio lado, como el cofre facetado de Codex), un patrón por rareza pintado por caras,
# grieta en zigzag que deja ver el interior claro y una tapa que salta al eclosionar; alas en abanico vertical (como las del cofre) que
# crecen con la rareza y adornos en las raras. Rig de 7 huesos (Root, Body, Cap, Wing_R/L, Tip_R/L) y clips Fly (0,6 s, bucle), Glide
# (2,0 s, bucle) y Hatch (1,5 s, sin bucle: tiembla, salta la tapa y se queda abierto).
# La v01 de voxeles (celda 0,2) se descartó antes de enseñarla: a ese tamaño el huevo se leía como una roca.
# v02 (30/10, Maikol: «huevos más distintos» tras la crítica del director, y la rareza épico nueva de mas1-juego/src/Mascotas.lua): seis
# huevos que cambian de tamaño (cáscara de 2,0 a 3,0 studs de alto), de forma (redondo, clásico, alto y puntiagudo, ancho...) y de alas
# (de 3 a 6 primarias, cresta en el legendario y doble par en el mítico), no solo de color. Colores de rareza de siempre: común crema,
# poco común verde, raro azul, épico morado, legendario dorado, mítico carmesí. Salida en huevos-alados-v02 (la v01 sigue en v01).
# blender -b --factory-startup --python-exit-code 1 -P build_huevos_alados.py
#   HUEVO_FASE=geo (colores planos, rápido) | check (solo comprobaciones) | full (por defecto);  HUEVO_SOLO=<clave> para hacer una sola rareza
# Ejes: +Y delante, +Z arriba, +X derecha; origen en el suelo bajo el huevo. Sin probar en Roblox.
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_ave import *
from mas1_pet import _ciclo

FASE = os.environ.get('HUEVO_FASE', 'full')
SOLO = os.environ.get('HUEVO_SOLO')
BASE_OUT = os.path.abspath(os.path.join(HERE, '..', 'huevos-alados-v02'))
HUESOS_HUEVO = ('Root', 'Body', 'Cap', 'Wing_R', 'Tip_R', 'Wing_L', 'Tip_L')

# alas: k = escala; coberteras (elevación, largo, posición en el brazo), secundarias (igual) y primarias (elevación, largo); extra =
# 'cresta' (dos plumas altas, legendario) o 'doble' (segundo par por encima, mítico). tam = (radio, media altura, punta) de la cáscara.
ALAS_5 = dict(prim=((12, 0.98), (0, 1.12), (-12, 1.16), (-24, 1.06), (-36, 0.92)),
              sec=((-42, 0.86, 0.32), (-54, 0.74, 0.20), (-66, 0.60, 0.08)), cob=((-6, 0.60, 0.05), (-26, 0.52, 0.14)))
ALAS_6 = dict(prim=((16, 0.95), (4, 1.10), (-8, 1.18), (-20, 1.16), (-32, 1.04), (-44, 0.90)),
              sec=((-44, 0.88, 0.34), (-56, 0.76, 0.22), (-68, 0.62, 0.10)), cob=((-4, 0.62, 0.04), (-20, 0.56, 0.12), (-36, 0.48, 0.20)))
VARIANTES = [
    dict(clave='comun', nombre='HuevoAladoComun', titulo='COMUN', patron='manchas', adorno=None, tam=(0.80, 1.02, 0.10),
         alas=dict(k=0.72, prim=((8, 0.95), (-10, 1.05), (-28, 0.92)), sec=((-48, 0.72, 0.22),), cob=((-8, 0.55, 0.06),), extra=None),
         pal={'cascara': '#f4ead2', 'patron': '#b8885a', 'interior': '#fff3b0', 'ala_base': '#efe2c4', 'ala_medio': '#dcbf8c',
              'ala_punta': '#a8703c', 'oro': '#ffc42e'}),
    dict(clave='poco-comun', nombre='HuevoAladoPocoComun', titulo='POCO COMUN', patron='zigzag', adorno=None, tam=(0.88, 1.14, 0.14),
         alas=dict(k=0.82, prim=((12, 0.95), (-2, 1.08), (-16, 1.08), (-30, 0.94)), sec=((-44, 0.80, 0.28), (-58, 0.66, 0.12)),
                   cob=((-6, 0.58, 0.05), (-26, 0.50, 0.14)), extra=None),
         pal={'cascara': '#c4eca8', 'patron': '#3f9e4c', 'interior': '#f3ffb8', 'ala_base': '#f0fae6', 'ala_medio': '#bfeaa3',
              'ala_punta': '#3f9e4c', 'oro': '#ffc42e'}),
    dict(clave='raro', nombre='HuevoAladoRaro', titulo='RARO', patron='rayas', adorno='gema', tam=(0.92, 1.36, 0.22),
         alas=dict(k=0.95, extra=None, **ALAS_5),
         pal={'cascara': '#7cc6ff', 'patron': '#ffffff', 'interior': '#d8f4ff', 'ala_base': '#ffffff', 'ala_medio': '#cfe9ff',
              'ala_punta': '#2b6fc4', 'oro': '#5fe0ff'}),
    dict(clave='epico', nombre='HuevoAladoEpico', titulo='EPICO', patron='espiral', adorno='pico', tam=(1.02, 1.36, 0.14),
         alas=dict(k=1.04, extra=None, **ALAS_6),
         pal={'cascara': '#7a3fe0', 'patron': '#b98cff', 'interior': '#ead8ff', 'ala_base': '#efe6ff', 'ala_medio': '#b48cff',
              'ala_punta': '#6a2fd0', 'oro': '#5fe0ff'}),
    dict(clave='legendario', nombre='HuevoAladoLegendario', titulo='LEGENDARIO', patron='rombos', adorno='joya', tam=(1.06, 1.44, 0.14),
         alas=dict(k=1.10, extra='cresta', **ALAS_6),
         pal={'cascara': '#fff4d6', 'patron': '#f2b630', 'interior': '#fff1a8', 'ala_base': '#fff8e6', 'ala_medio': '#f6dc94',
              'ala_punta': '#f2a81c', 'oro': '#ffc42e'}),
    dict(clave='mitico', nombre='HuevoAladoMitico', titulo='MITICO', patron='estrellas', adorno='corona', tam=(1.12, 1.50, 0.12),
         alas=dict(k=1.16, extra='doble', **ALAS_6),
         pal={'cascara': '#d6245e', 'patron': '#ffd24a', 'interior': '#ffe0ec', 'ala_base': '#fff0f5', 'ala_medio': '#ff8fb6',
              'ala_punta': '#ffd24a', 'oro': '#fff3a0'}),
]

# ---------------------------------------------------------------- cáscara: torno de N lados y M bandas; el anillo 8 es la grieta en zigzag
R_HUEVO, H_HUEVO, PUNTA, CZ = 0.98, 1.32, 0.14, 1.42
N, M = 16, 12
K_GRIETA, DZ_GRIETA, A_GRIETA = 8, 0.50, 0.11
HOLGURA, HUNDIR = 0.05, 0.03          # rendija de la grieta (se ve el interior claro) y cuanto se hunde el borde
DELTA = 2 * math.pi / N


def r_de(dz):
    return R_HUEVO * (1.0 - PUNTA * dz) * math.sqrt(max(0.0, 1.0 - dz * dz))


def dz_anillo(k, j):
    if k == K_GRIETA:
        return DZ_GRIETA + (A_GRIETA if j % 2 == 0 else -A_GRIETA)
    return -math.cos(k * math.pi / M)


def pos_anillo(k, j, dr=0.0, dzz=0.0):
    """Vértice j del anillo k. Los anillos impares van girados medio lado (malla de triángulos) y todo gira medio lado más para que los
    rombos del legendario queden simétricos respecto al frente."""
    th = (j + 0.5 * (k % 2) + 0.5) * DELTA
    dz = dz_anillo(k, j)
    r = r_de(dz) + dr
    return Vector((r * math.cos(th), r * math.sin(th), CZ + dz * H_HUEVO + dzz))


def _h(i, j, k, seed):
    h = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (seed * 2654435761)
    return ((h >> 3) & 0xffff) / 65535.0


def patron_de(tipo):
    """Región de cada triángulo de la cáscara según (banda b, tipo 'up'/'down'/'fan', índice j). Rombo (k, j) = triángulo 'down' j de la
    banda k + triángulo 'up' j de la banda k+1 (comparten la base)."""
    def liso(b, kind, j):
        return 'cascara'                                            # manchas y estrellas van encima (destellos())

    def zigzag(b, kind, j):
        if b == 5 or (b == 4 and kind == 'down') or (b == 6 and kind == 'up'):
            return 'patron'                                         # banda ancha con dientes arriba y abajo
        if b == 8 or (b == 9 and kind == 'up'):
            return 'patron'                                         # banda de la tapa, justo encima de la grieta
        return 'cascara'

    def rayas(b, kind, j):
        return 'patron' if b in (2, 4, 6, 8, 10) else 'cascara'

    def espiral(b, kind, j):
        return 'patron' if 0 < b < M - 1 and (j + b) % 4 < 2 else 'cascara'        # franjas en diagonal que suben girando (galaxia)

    def rombos(b, kind, j):
        if b in (0, M - 1):
            return 'patron'                                         # polos dorados
        for k, todos in ((2, False), (5, True), (9, False)):     # en el ecuador la fila entera (banda de rombos que se tocan)
            if (todos or j % 2 == 0) and ((b == k and kind == 'down') or (b == k + 1 and kind == 'up')):
                return 'patron'
        return 'cascara'

    return dict(manchas=liso, zigzag=zigzag, rayas=rayas, espiral=espiral, rombos=rombos, estrellas=liso)[tipo]


def normal_huevo(th, dz):
    """Normal de la superficie lisa del huevo (torno) en el ángulo th (radianes) y altura relativa dz."""
    e = 1e-3
    drdz = (r_de(dz + e) - r_de(dz - e)) / (2 * e * H_HUEVO)
    return Vector((math.cos(th), math.sin(th), -drdz)).normalized()


def destellos(MBS, tipo):
    """Rombos pequeños medio hundidos en la cáscara: manchas marrones del común (girados al azar) o estrellas claras y doradas del mítico
    (girados 45°). Se reparten con semilla fija lejos de la grieta, de las raíces de las alas, del emblema y entre sí."""
    import random
    rnd = random.Random(7 if tipo == 'manchas' else 11)
    puestos = []
    objetivo = 24 if tipo == 'manchas' else 16
    intentos = 0
    while len(puestos) < objetivo and intentos < 4000:
        intentos += 1
        th = rnd.uniform(0, 2 * math.pi)
        dz = rnd.uniform(-0.82, 0.92)
        if abs(dz - DZ_GRIETA) < 0.20:
            continue                                                # la grieta
        if abs(math.cos(th)) > 0.86 and -0.25 < dz < 0.45:
            continue                                                # raíces de las alas
        if tipo == 'estrellas' and math.sin(th) > 0.80 and -0.40 < dz < 0.10:
            continue                                                # emblema dorado del frente
        p = Vector((r_de(dz) * math.cos(th), r_de(dz) * math.sin(th), CZ + dz * H_HUEVO))
        if any((p - q).length < 0.36 for q in puestos):
            continue
        puestos.append(p)
        n = normal_huevo(th, dz)
        x = Vector((0, 0, 1)).cross(n)
        x = x.normalized() if x.length > 1e-6 else Vector((1, 0, 0))
        y = n.cross(x)
        Rm = Matrix((x, y, n)).transposed().to_4x4()
        if tipo == 'manchas':
            tam, giro, mat = rnd.uniform(0.13, 0.24), rnd.uniform(0, 90), 'patron'
        else:
            tam, giro = rnd.choice((0.17, 0.21, 0.26)), 45.0
            mat = 'oro' if len(puestos) % 4 == 0 else 'patron'
        mb = MBS['Cap' if dz > DZ_GRIETA else 'Body']
        antes = mb.mark()
        mb.box((0, 0, 0), (tam, tam * (0.8 if tipo == 'manchas' else 1.0), 0.08), mat)
        mb.xform_since(antes, tr(p) @ Rm @ rz(giro))
    return len(puestos)


def cascara(MBS, pat):
    """Cáscara de dos piezas (cuerpo bandas 0-7, tapa bandas 8-11) con el borde de la grieta hundido, una rendija entre las dos y el
    interior hueco (borde y cuenco) del color 'interior'."""
    def anillo(mb, k, **kw):
        if k == 0 or k == M:
            return [mb.bm.verts.new((0.0, 0.0, CZ + (-1 if k == 0 else 1) * H_HUEVO))]
        return [mb.bm.verts.new(pos_anillo(k, j, **kw)) for j in range(N)]

    def banda(mb, b, L, U):
        if len(L) == 1:
            for j in range(N):
                mb.face([L[0], U[(j + 1) % N], U[j]], pat(b, 'fan', j))
            return
        if len(U) == 1:
            for j in range(N):
                mb.face([L[j], L[(j + 1) % N], U[0]], pat(b, 'fan', j))
            return
        for j in range(N):
            j1 = (j + 1) % N
            if b % 2 == 0:              # el anillo de arriba va medio lado por delante
                mb.face([L[j], L[j1], U[j]], pat(b, 'up', j))
                mb.face([U[j], L[j1], U[j1]], pat(b, 'down', j))
            else:
                mb.face([L[j], L[j1], U[j1]], pat(b, 'up', j))
                mb.face([U[j], L[j], U[j1]], pat(b, 'down', j))

    mb = MBS['Body']
    R_ = [anillo(mb, k) for k in range(K_GRIETA)] + [anillo(mb, K_GRIETA, dr=-HUNDIR)]
    for b in range(K_GRIETA):
        banda(mb, b, R_[b], R_[b + 1])
    borde = R_[K_GRIETA]
    dentro = [mb.bm.verts.new(Vector((v.co.x * 0.84, v.co.y * 0.84, v.co.z - 0.05))) for v in borde]
    fondo = mb.bm.verts.new((0.0, 0.0, CZ + DZ_GRIETA * H_HUEVO - 0.34))
    for j in range(N):
        j1 = (j + 1) % N
        mb.face([borde[j], borde[j1], dentro[j1], dentro[j]], 'interior')
        mb.face([dentro[j], dentro[j1], fondo], 'interior')

    mb = MBS['Cap']
    R_ = [anillo(mb, K_GRIETA, dr=-HUNDIR, dzz=HOLGURA)] + [anillo(mb, k) for k in range(K_GRIETA + 1, M + 1)]
    for i in range(len(R_) - 1):
        banda(mb, K_GRIETA + i, R_[i], R_[i + 1])
    borde = R_[0]
    dentro = [mb.bm.verts.new(Vector((v.co.x * 0.84, v.co.y * 0.84, v.co.z + 0.05))) for v in borde]
    techo = mb.bm.verts.new((0.0, 0.0, CZ + DZ_GRIETA * H_HUEVO + 0.24))
    for j in range(N):
        j1 = (j + 1) % N
        mb.face([borde[j], dentro[j], dentro[j1], borde[j1]], 'interior')
        mb.face([dentro[j1], dentro[j], techo], 'interior')


def dv(s, e):
    """Ángulo en el marco del ala (abanico vertical) de una pluma que sale hacia fuera con elevación e (grados, + hacia arriba)."""
    return e if s > 0 else 180.0 - e


def construir_huevo(var):
    A.clean_scene()
    A.REGIONS.clear()
    bpy.context.scene.render.fps = 30
    CM = A.collection('Mascota')
    CR = A.collection('Ref')
    CC = A.collection('Camaras')
    PAL = dict(var['pal'])
    MBS = {b: A.MB('G_' + b) for b in HUESOS_HUEVO}
    cascara(MBS, patron_de(var['patron']))
    if var['patron'] in ('manchas', 'estrellas'):
        destellos(MBS, var['patron'])

    # ---------------------------------------------------------------- alas: abanico vertical (marco del ala girado 90° en X: el plano de
    # las plumas es el XZ del mundo) de plumas puntiagudas como las del cofre: coberteras delante, secundarias colgando del brazo y
    # primarias desde la muñeca; crecen con la rareza. Cada pluma va a su propia profundidad (0,035 de paso, grosor 0,09): sin caras coplanares
    al = var['alas']
    k = al['k']
    S_HOMBRO = Vector((r_de(0.10) - 0.18, -0.05, CZ + 0.10 * H_HUEVO))     # hombro metido en la cáscara, algo por encima del ecuador
    MARCOS = {}
    prof = lambda n: -0.20 + 0.035 * n
    for s, lado in ((1, 'R'), (-1, 'L')):
        W_, T_ = 'Wing_' + lado, 'Tip_' + lado
        Sv = Vector((s * S_HOMBRO.x, S_HOMBRO.y, S_HOMBRO.z))
        M1, M2, Hm = marco_ala(Sv, s, 0.42 * k, 14.0, 12.0, 6.0, 6.0)
        M1v, M2v = M1 @ rx(90), M2 @ rx(90)
        MARCOS[lado] = (Hm, Sv)
        n = 0
        for e, L_, u in al['cob']:                                                                     # coberteras
            pluma(MBS[W_], M1v, (s * u * k, 0.03), dv(s, e), L_ * k, 0.30 * k, 0.09, prof(n),
                  [(0.65, 'ala_base'), (1.0, 'ala_medio')], afilar=0.9, punta=0.55)
            n += 1
        for e, L_, u in al['sec']:                                                                     # secundarias
            pluma(MBS[W_], M1v, (s * u * k, -0.02), dv(s, e), L_ * k, 0.38 * k, 0.09, prof(n),
                  [(0.50, 'ala_base'), (0.78, 'ala_medio'), (1.0, 'ala_punta')], afilar=0.9, punta=0.62)
            n += 1
        for i, (e, L_) in enumerate(al['prim']):                                                       # primarias
            pluma(MBS[T_], M2v, (s * 0.02 * i, -0.02 * i), dv(s, e), L_ * k, 0.40 * k, 0.09, prof(n),
                  [(0.42, 'ala_base'), (0.70, 'ala_medio'), (1.0, 'ala_punta')], afilar=0.9, punta=0.66)
            n += 1
        if al['extra'] == 'cresta':                    # legendario: dos plumas altas que salen del hombro hacia arriba, con la punta dorada
            for e, L_ in ((44, 1.30), (60, 1.10)):                  # largas y abiertas: un segundo nivel dorado (no orejas)
                pluma(MBS[W_], M1v, (s * 0.06 * k, 0.12 * k), dv(s, e), L_ * k, 0.34 * k, 0.09, prof(n),
                      [(0.40, 'ala_base'), (0.75, 'ala_medio'), (1.0, 'oro')], afilar=0.9, punta=0.6)
                n += 1
        if al['extra'] == 'doble':                     # mítico: segundo par de alas, más pequeño, por encima del primero
            for e, L_ in ((36, 0.78), (52, 0.88), (68, 0.76)):
                pluma(MBS[W_], M1v, (s * 0.04 * k, 0.30 * k), dv(s, e), L_ * k, 0.32 * k, 0.09, prof(n),
                      [(0.45, 'ala_base'), (0.75, 'ala_medio'), (1.0, 'ala_punta')], afilar=0.9, punta=0.62)
                n += 1

    # ---------------------------------------------------------------- adornos por rareza
    if var['adorno'] in ('gema', 'pico', 'corona'):
        z_e = CZ - 0.09 * H_HUEVO
        rombo(MBS['Body'], (0, r_de((z_e - CZ) / H_HUEVO) * 0.97, z_e), 0.46 if var['adorno'] == 'corona' else 0.34, 0.14, 'oro', 'Y')
    if var['adorno'] == 'joya':                                     # joya dorada en relieve encima del rombo del frente
        rombo(MBS['Body'], (0, R_HUEVO * 0.975, CZ), 0.30, 0.14, 'oro', 'Y')
    if var['adorno'] in ('corona', 'pico'):                         # corona de tres plumas (mítico) o un cristal solo (épico) en lo alto
        plumas = ((-0.17, -26, 0.62), (0.0, 0.0, 0.80), (0.17, 26, 0.62)) if var['adorno'] == 'corona' else ((0.0, 0.0, 0.70),)
        for j, (x_, abre, L_) in enumerate(plumas):
            Mc = tr((x_, 0.0, CZ + H_HUEVO - 0.14)) @ ry(-90 + abre) @ rx(90)
            pluma(MBS['Cap'], Mc, (0, 0), 0, L_, 0.26, 0.12, (j - 1) * 0.05, [(0.5, 'ala_medio'), (1.0, 'oro')], afilar=0.9, punta=0.6)

    # ---------------------------------------------------------------- rig y malla única
    z_tapa = CZ + DZ_GRIETA * H_HUEVO
    HUESOS = [('Root', (0, 0, CZ), None, 0.5), ('Body', (0, 0, CZ), 'Root', 0.5), ('Cap', (0, 0, z_tapa), 'Body', 0.4)]
    for lado in ('R', 'L'):
        Hm, Sv = MARCOS[lado]
        HUESOS.append(('Wing_' + lado, tuple(Sv), 'Body', 0.4))
        HUESOS.append(('Tip_' + lado, tuple(Hm), 'Wing_' + lado, 0.4))
    ob, rig = armar(var['nombre'], MBS, HUESOS, CM)
    return ob, rig, HUESOS, PAL, CR, CC


def claves(c, t, wing=0.0, tip=0.0, wyaw=0.0, tyaw=0.0, bodyz=0.0, roll=0.0, pitch=0.0, cap_z=0.0, cap_rx=0.0):
    for s, lado in ((1, 'R'), (-1, 'L')):
        c.k('Wing_' + lado, t, rot=(0, s * wing, -s * wyaw))
        c.k('Tip_' + lado, t, rot=(0, s * tip, -s * tyaw))
    c.k('Body', t, loc=(0, 0, bodyz), rot=(pitch, roll, 0))
    c.k('Cap', t, loc=(0, 0, cap_z), rot=(cap_rx, 0, 0))
    c.k('Root', t)


def clips_huevo(rig, esc=1.0):
    """esc = media altura de la cáscara / 1,32 (la del huevo v01): la tapa salta más en los huevos grandes."""
    acts = {}
    # Fly: el aleteo de las mascotas (recoger -> extender -> impulsar -> recoger) en 0,6 s y el huevo sube y baja
    fases = sorted({round(x[0], 3) for x in ALETEO} | {0.19, 0.37, 0.53, 0.69, 0.84, 0.95})
    c = A.Clip(rig, 'Fly', 0.6, loop=True, fps=30)
    for f in fases + [1.0]:
        E, tipR, wy, ty = _ciclo(ALETEO, f % 1.0 if f < 1.0 else 0.0)
        claves(c, 0.6 * f, wing=-E, tip=tipR, wyaw=wy, tyaw=ty, bodyz=0.12 * math.sin(2 * math.pi * (f - 0.15)),
               pitch=3 * math.cos(2 * math.pi * f), roll=2 * math.sin(2 * math.pi * f))
    acts['Fly'] = c.build(list(HUESOS_HUEVO))
    # Glide: alas abiertas y algo levantadas, el huevo se mece
    c = A.Clip(rig, 'Glide', 2.0, loop=True, fps=30)
    for i in range(9):
        t = 2.0 * i / 8
        p = 2 * math.pi * t / 2.0
        claves(c, t, wing=-(12 + 4 * math.sin(p)), tip=-4 + 5 * math.sin(p - 0.9), wyaw=3, bodyz=0.08 * math.sin(p), roll=4 * math.sin(p + 0.5))
    acts['Glide'] = c.build(list(HUESOS_HUEVO))
    # Hatch: tiembla, salta la tapa (se inclina hacia atrás y enseña el interior por delante) y se queda abierto con las alas arriba
    c = A.Clip(rig, 'Hatch', 1.5, loop=False, fps=30)
    for t, roll, cz, crx, E, tp in ((0.00, 0, 0, 0, 10, -4), (0.10, 10, 0, 0, 14, -8), (0.20, -10, 0, 0, 6, 0), (0.30, 12, 0.02, 0, 16, -8),
                                    (0.40, -12, 0.02, 0, 6, 0), (0.50, 6, 0.06, 4, 20, -6), (0.62, 0, 0.62, 30, 42, -16),
                                    (0.80, 0, 0.50, 24, 34, -10), (1.50, 0, 0.50, 24, 30, -8)):
        claves(c, t, wing=-E, tip=tp, roll=roll, cap_z=cz * esc, cap_rx=crx, bodyz=(0.04 if t >= 0.62 else 0.0) * esc)
    acts['Hatch'] = c.build(list(HUESOS_HUEVO))
    return acts, {'Fly': 0.6, 'Glide': 2.0, 'Hatch': 1.5}


def pose_huevo(rig, cap_z=0.0, cap_rx=0.0, wing=0.0):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
    rig.pose.bones['Cap'].location = (0, 0, cap_z)
    rig.pose.bones['Cap'].rotation_euler = Euler((math.radians(cap_rx), 0, 0), 'XYZ')
    for s, lado in ((1, 'R'), (-1, 'L')):
        rig.pose.bones['Wing_' + lado].rotation_euler = Euler((0, math.radians(s * wing), 0), 'XYZ')
    bpy.context.view_layer.update()


resumen = []
for var in VARIANTES:
    if SOLO and var['clave'] != SOLO:
        continue
    OUT = os.path.join(BASE_OUT, var['clave'])
    PREV = os.path.join(OUT, 'previews')
    for d in ('', 'texturas', 'clips', 'previews'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    R_HUEVO, H_HUEVO, PUNTA = var['tam']                         # la cáscara de cada rareza (las funciones de arriba las leen de aquí)
    CZ = H_HUEVO + 0.10
    ESC = H_HUEVO / 1.32
    ob, rig, HUESOS, PAL, CR, CC = construir_huevo(var)
    TRIS = A.tris([ob])
    mn = Vector([min(v.co[a] for v in ob.data.vertices) for a in range(3)])
    mx = Vector([max(v.co[a] for v in ob.data.vertices) for a in range(3)])
    BOUNDS = dict(envergadura=round(mx.x - mn.x, 2), alto=round(mx.z - mn.z, 2), largo=round(mx.y - mn.y, 2), z_min=round(mn.z, 2))
    SUELTAS, N_ISLAS = piezas_sueltas(ob)
    COPL, EJ = caras_coplanares(ob)
    A.log(var['clave'], 'triangulos', TRIS, BOUNDS, 'sueltas', len(SUELTAS), 'de', N_ISLAS, 'coplanares', COPL, EJ[:4])
    if FASE == 'check':
        continue
    E = Escena(CR, CC, PREV, 'geo' if FASE == 'geo' else 'full', radio=7.5, maniqui=(-4.0, 0.4), regla=(4.4, 0.4), objetivo=(-0.3, 0.0, CZ))
    shot = E.foto
    pref = 'Huevo-' + var['clave']
    if FASE == 'geo':
        planos(ob, PAL)
        pose_huevo(rig)
        shot('_geo_frente', 180, 8, 13.0, scale=True)
        shot('_geo_34', 148, 16, 12.0)
        shot('_geo_lateral', 90, 6, 12.0)
        pose_huevo(rig, 0.50 * ESC, 24, -30)
        shot('_geo_abierto', 160, 22, 11.0)
        continue
    # ------------------------------------------------------------ textura pintada
    Pn = hornear(ob, 3.0)
    E.reiniciar_render()
    BASE = dict(var=0.05, stroke=(1.0, 1.0, 1.0), stroke_scale=3.5, face_var=0.06, ao=0.5, ao_tint='#2b2455', light=0.24,
                hue_var=0.02, blotch=0.04, edge=0.45, edge_th=0.04, edge_break=0.3)

    def reg(name, **kw):
        if name not in A.REGIONS:
            return None
        k = dict(BASE)
        k.update(kw)
        if 'edge_col' not in k:
            k['edge_col'] = claro(PAL[name])
        return Pn.region(name, PAL[name], **k)
    reg('cascara', ao_tint='#7f8bb0', grad=0.25, seed=1)
    reg('patron', ao_tint='#7f8bb0', seed=2)
    reg('interior', ao=0.10, light=0.05, var=0.02, face_var=0.0, edge=0.0, seed=3)
    reg('oro', edge_col='#ffffff', var=0.03, ao=0.25, light=0.12, grad=0.4, seed=5)
    WING = dict(stroke=(6.0, 1.0, 1.0), stroke_scale=3.0, var=0.06, blotch=0.05, edge=0.6)
    reg('ala_base', seed=21, **WING)
    reg('ala_medio', seed=22, **WING)
    reg('ala_punta', ao=0.25, light=0.10, seed=25, **WING)
    guardar_textura(Pn, ob, OUT, var['nombre'])
    # ------------------------------------------------------------ clips, renders y exportación
    acts, CLIPS = clips_huevo(rig, ESC)
    rig.animation_data_clear()
    pose_huevo(rig)
    shots = []
    shots.append((shot(pref + '-frente', 180, 8, 13.0, scale=True), 'FRENTE (REGLA 6 STUDS) - ' + var['titulo']))
    shots.append((shot(pref + '-tres-cuartos', 148, 16, 12.0), '3/4'))
    shots.append((shot(pref + '-lateral', 90, 6, 12.0), 'LATERAL'))
    shots.append((shot(pref + '-espalda', 0, 12, 12.0), 'ESPALDA'))
    en(rig, acts, 'Fly', 0.0)
    shots.append((shot(pref + '-aleteo-alto', 150, 10, 12.0), 'VUELO: ALAS ARRIBA'))
    en(rig, acts, 'Fly', 0.6 * 0.46)
    shots.append((shot(pref + '-aleteo-bajo', 150, 10, 12.0), 'VUELO: ALAS ABAJO'))
    en(rig, acts, 'Hatch', 0.3)
    shots.append((shot(pref + '-eclosion-tiembla', 160, 14, 12.0), 'ECLOSION: TIEMBLA'))
    en(rig, acts, 'Hatch', 1.0)
    shots.append((shot(pref + '-eclosion-abierto', 160, 24, 11.0), 'ECLOSION: ABIERTO'))
    W.contact_sheet(shots, 4, os.path.join(PREV, '_hoja.png'), title='HUEVO ALADO %s V02 - RENDERS DE BLENDER' % var['titulo'])
    a_jpg(os.path.join(PREV, '_hoja.png'), os.path.join(PREV, pref + '-hoja.jpg'), 0.5)
    E.reiniciar_render()
    exportar_pet(OUT, var['nombre'], ob, rig, acts, CLIPS, lambda: pose_huevo(rig), {
        'pieza': 'Huevo volador con alas %s v02 (da mascotas; idea de Maikol del 29/10; v02 con forma, tamaño y alas por rareza)' % var['titulo'], 'rareza': var['titulo'],
        'triangulos': TRIS, 'limites_studs': BOUNDS, 'huesos': [h[0] for h in HUESOS], 'paleta': PAL, 'patron': var['patron'],
        'adorno': var['adorno'], 'escala_alas': var['alas']['k'], 'primarias': len(var['alas']['prim']), 'extra_alas': var['alas']['extra'],
        'cascara_radio_mediaaltura_punta': var['tam'], 'piezas_sueltas': SUELTAS, 'caras_coplanares_solapadas': COPL},
        sin_bucle=('Hatch',))
    resumen.append((var['clave'], TRIS, BOUNDS, len(SUELTAS), COPL))
A.log('RESUMEN', resumen)
A.log('listo')
