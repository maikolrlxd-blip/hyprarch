# Mapa v01 de «+1 de lanzamiento por segundo» hecho con piezas nativas de Roblox (Part y WedgePart), sin mallas: se abre en Studio sin
# subir nada a Roblox (Maikol, 30/10: «te doy permiso para roblox studio» y «primero todo lo visual»). Misma distribución que build_mapa.py
# (mismas funciones de zona y misma semilla), con lo que Roblox hace bien: las nubes son bolas sobre una base plana redonda, lo que brilla
# es Neon (rayos, auroras, aros, estrellas, cristales y luces) y solo el carril choca (CanCollide); el decorado no.
# Escribe un modelo para insertar en una place (Mapa-v01.rbxmx) y una place de prueba (Mapa-v01-prueba.rbxlx: el modelo, un
# SpawnLocation al principio del carril y una Atmosphere). Para comprobarlo sin Studio vuelve a leer el XML como lo leería Roblox, rehace
# las piezas en Blender con las reglas de Roblox (la cuña sube hacia +Z local, el cilindro va a lo largo de X) y saca renders con las
# mismas cámaras que el mapa; también busca caras planas solapadas en el mismo plano (parpadeo en Roblox). Sin probar en Studio.
# blender -b --factory-startup --python-exit-code 1 -P mapa_roblox.py
#   MAPA_RBX_FASE=xml (solo los archivos) | check (y la comprobación de caras, sin renders) | full (por defecto)
# Ejes: Blender (x, y, z) -> Roblox (x, z, -y). El vuelo (+Y en Blender) va hacia -Z en Roblox, como la Pradera de Codex exportada con
# axis_forward='-Z'; el origen es el de la Pradera. 1 unidad = 1 stud.
import sys, os, math, random, json
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_mapa as bm                                   # solo funciones y tablas: la construcción de build_mapa va bajo __main__
from mas1_lib import *

FASE = os.environ.get('MAPA_RBX_FASE', 'full')
OUT = os.path.join(bm.OUT, 'roblox')
MR = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))           # vector de Blender -> vector de Roblox
MRt = MR.transposed()
NEON = {'rayo', 'rayo_claro', 'aurora_a', 'aurora_b', 'aurora_c', 'estrella', 'luz', 'aro_azul', 'aro_oro', 'cristal', 'cristal_rosa'}
TRANSP = {'aurora_a': 0.3, 'aurora_b': 0.3, 'aurora_c': 0.3, 'cristal': 0.1, 'cristal_rosa': 0.1}
NEON_COLOR = {'cristal': '#41d9ff', 'cristal_rosa': '#ff6ad5', 'aurora_a': '#22e3b2', 'aurora_b': '#4a8dff', 'aurora_c': '#b25cff'}   # en Neon el pastel sale casi blanco
MATERIAL = {'SmoothPlastic': 272, 'Neon': 288}
FORMA = {'Ball': 0, 'Block': 1, 'Cylinder': 2}
ZONA_RBX = {'mar-de-nubes': 'MarDeNubes', 'tormenta': 'Tormenta', 'cielo-alto': 'CieloAlto', 'espacio': 'Espacio'}


class Grabadora:
    """Hace de A.MB para las funciones de zona de build_mapa: apunta primitivas (en coordenadas de Blender) en vez de hacer malla."""

    def __init__(self, nombre):
        self.nombre, self.prims, self.en_nube, self.en_torre = nombre, [], None, False

    def mark(self):
        return len(self.prims)

    def box(self, c, s, mat, bevel=0.0, edges='all', mats=None):
        t = 'caja'
        if self.en_nube is not None:                       # dentro de nube(): la primera caja es la base y las demás, los bultos
            t = 'nube_base' if self.en_nube == 0 else 'nube_bulto'
            self.en_nube += 1
        self.prims.append(dict(t=t, c=Vector(c), R=Matrix.Identity(3), s=Vector(s), mat=mat, torre=self.en_torre))

    def xform_since(self, antes, M):
        for p in self.prims[antes:]:
            p['c'] = M @ p['c']
            p['R'] = M.to_3x3() @ p['R']

    def seg_box(self, p0, p1, w, h, mat, bevel=0.0, extend=0.0):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        L = d.length + 2 * extend
        mk = self.mark()
        self.box((0, L / 2 - extend, 0), (w, L, h), mat)
        self.xform_since(mk, Matrix.Translation(p0) @ d.normalized().to_track_quat('Y', 'Z').to_matrix().to_4x4())

    def prism(self, pts, w0, w1, mat, plane='YZ', bevel=0.0, cap_mat=None, side_mat=None, cap0=True, cap1=True):
        self.prims.append(dict(t='prisma', pts=[tuple(p) for p in pts], w0=w0, w1=w1, plano=plane, mat=mat))

    def lathe(self, p0, p1, prof, segs, mat, rot=None, close0=True, close1=True, mats=None):
        self.prims.append(dict(t='torno', p0=Vector(p0), p1=Vector(p1), prof=list(prof), segs=segs, rot=rot, mat=mat))

    def rock(self, c, r, mat, subdiv=1, seed=0, jitter=0.25, squash=(1, 1, 1)):
        self.prims.append(dict(t='roca', c=Vector(c), r=r, mat=mat, seed=seed, jitter=jitter, squash=tuple(squash)))


_nube, _torre = bm.nube, bm.torre


def nube_marcada(mb, *a, **k):
    mb.en_nube = 0
    _nube(mb, *a, **k)
    mb.en_nube = None


def torre_marcada(mb, *a, **k):
    mb.en_torre = True
    _torre(mb, *a, **k)
    mb.en_torre = False


def tramos(linea):
    """[(columna, largo)] de cada tramo seguido de '#' en una fila de letra: un bloque por tramo en vez de uno por píxel."""
    out, col = [], 0
    while col < len(linea):
        if linea[col] == '#':
            n = 1
            while col + n < len(linea) and linea[col + n] == '#':
                n += 1
            out.append((col, n))
            col += n
        else:
            col += 1
    return out


def texto_cartel_tramos(mb, s, x0, y_frente, z0, px, mat):
    for i, ch in enumerate(s):
        if ch == ' ':
            continue
        for fila, linea in enumerate(bm.FUENTE[ch].split('|')):
            for col, n in tramos(linea):
                mb.box((x0 + (i * 6 + col + n / 2) * px, y_frente - px * 0.4, z0 + (6 - fila + 0.5) * px), (n * px, px * 0.8, px), mat)


def texto_suelo_tramos(mb, s, xc, y0, px, alto, mat):
    x0 = xc - bm.ancho_texto(s, px) / 2
    for i, ch in enumerate(s):
        if ch == ' ':
            continue
        for fila, linea in enumerate(bm.FUENTE[ch].split('|')):
            for col, n in tramos(linea):
                mb.box((x0 + (i * 6 + col + n / 2) * px, y0 + (6 - fila + 0.5) * px, alto / 2), ((n - 0.02) * px, px * 0.98, alto), mat)


def flecha_sin_solape(mb, y, mat):
    """Como bm.flecha, pero los dos brazos del «^» con alturas distintas (0,24 y 0,30): sin caras coplanares solapadas en la punta."""
    E = bm.FLECHA
    for s, alto, z0 in ((1, 0.24, 0.0), (-1, 0.30, 0.02)):
        bm.cubo_girado(mb, (s * 1.6 * E, y, z0 + alto / 2), (5.2 * E, 1.6 * E, alto), mat, rot=(0, 0, -s * 45))
    mb.box((0, y - 3.4 * E, 0.10), (1.6 * E, 5.0 * E, 0.20), mat)


bm.nube, bm.torre, bm.texto_cartel, bm.texto_suelo = nube_marcada, torre_marcada, texto_cartel_tramos, texto_suelo_tramos
bm.flecha = flecha_sin_solape

# ---------------------------------------------------------------- mismas zonas y misma semilla que build_mapa
rnd = random.Random(30)
ZG = []
for i, Z in enumerate(bm.ZONAS):
    P = {k: Grabadora(k) for k in bm.PIEZAS}
    bm.construir_zona(P, i, Z, rnd)
    ZG.append((Z, P))


# ---------------------------------------------------------------- primitivas de Blender -> piezas de Roblox
def a_rbx(v):
    return MR @ Vector(v)


def nombre_de(p, grupo):
    if grupo in ('Arco', 'Marcas', 'Aros'):
        return {'Arco': 'Arco', 'Marcas': 'Marca', 'Aros': 'Aro'}[grupo]
    t, mat = p['t'], p['mat']
    if t in ('nube_base', 'nube_bulto'):
        return 'Nube'
    if t == 'prisma':
        return 'Rayo'
    if t == 'torno':
        return 'Anillo'
    if t == 'roca':
        return 'Planeta' if p['jitter'] == 0 else 'Roca'
    for pre, n in (('aurora', 'Aurora'), ('cristal', 'Cristal'), ('estrella', 'Estrella'), ('crater', 'Crater'),
                   ('cesped', 'Isla'), ('tierra', 'Isla'), ('tronco', 'Isla'), ('hoja', 'Isla')):
        if mat.startswith(pre):
            return n
    return 'Baldosa' if grupo == 'Suelo' else 'Pieza'


def pieza(lista, clase, forma, pos, R, size, mat, nombre, colision=False):
    neon = mat in NEON
    lista.append(dict(clase=clase, forma=forma, pos=Vector(pos), R=Matrix(R), size=Vector(size),
                      color=NEON_COLOR.get(mat, bm.PAL[mat]) if neon else bm.PAL[mat],
                      material='Neon' if neon else 'SmoothPlastic', transp=TRANSP.get(mat, 0.0), nombre=nombre, colision=colision,
                      sombra=not neon))


def caja_b(lista, c, R_b, s, mat, nombre, colision=False):
    """Caja de Blender (centro, rotación con los ejes locales en columnas, tamaño) -> Part Block: R = MR·R_b·MRᵀ y tamaño (sx, sz, sy)."""
    pieza(lista, 'Part', 'Block', a_rbx(c), MR @ R_b @ MRt, (s[0], s[2], s[1]), mat, nombre, colision)


R_VERTICAL = Matrix(((0, -1, 0), (1, 0, 0), (0, 0, 1)))  # cilindro de Roblox (eje X local) puesto de pie: X local -> +Y del mundo


def disco_b(lista, c, diam, alto, mat, nombre):
    pieza(lista, 'Part', 'Cylinder', a_rbx(c), R_VERTICAL, (alto, diam, diam), mat, nombre)


def bola_b(lista, c, diam, mat, nombre):
    pieza(lista, 'Part', 'Ball', a_rbx(c), Matrix.Identity(3), (diam, diam, diam), mat, nombre)


def triangular(poly):
    """Recorte de orejas de un polígono simple 2D: lista de triángulos (índices)."""
    def cruz(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    area = sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly)))
    idx = list(range(len(poly)))
    if area > 0:                                           # la suma de arriba es -2·área: > 0 es sentido horario
        idx.reverse()
    tris = []
    while len(idx) > 3:
        for k in range(len(idx)):
            a, b, c = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            if cruz(poly[a], poly[b], poly[c]) <= 1e-9:
                continue
            if any(cruz(poly[a], poly[b], poly[q]) >= 0 and cruz(poly[b], poly[c], poly[q]) >= 0 and cruz(poly[c], poly[a], poly[q]) >= 0
                   for q in idx if q not in (a, b, c)):
                continue
            tris.append((a, b, c))
            idx.pop(k)
            break
        else:
            raise RuntimeError('polígono sin oreja')
    tris.append(tuple(idx))
    return tris


ERR_CUNA = [0.0]


def triangulo_rbx(lista, A3, B3, C3, grosor, mat, nombre):
    """Triángulo (puntos de Roblox) con grosor -> dos WedgePart rectángulas que comparten la altura sobre el lado más largo.
    La cuña de Roblox: base abajo (-Y), cara trasera vertical (+Z) y rampa de arriba-detrás a abajo-delante; el ángulo recto está
    abajo-detrás (K) y la sección tiene K, T = K + alto·Y y F = K - fondo·Z."""
    pts = [Vector(A3), Vector(B3), Vector(C3)]
    lados = [((pts[1] - pts[2]).length, 0), ((pts[0] - pts[2]).length, 1), ((pts[0] - pts[1]).length, 2)]
    a = max(lados)[1]                                      # vértice opuesto al lado más largo
    A_, B_, C_ = pts[a], pts[(a + 1) % 3], pts[(a + 2) % 3]
    BC = C_ - B_
    D = B_ + BC * ((A_ - B_).dot(BC) / BC.length_squared)  # pie de la altura: cae dentro porque BC es el lado más largo
    for Q in (B_, C_):
        alto, fondo = (A_ - D).length, (Q - D).length
        if alto < 0.02 or fondo < 0.02:
            continue
        Y = (A_ - D).normalized()
        Zl = (D - Q).normalized()
        X = Y.cross(Zl)
        R = Matrix((X, Y, Zl)).transposed()                # columnas = ejes locales
        pos = (A_ + Q) / 2                                 # centro de la caja = punto medio de la hipotenusa
        for local, real in (((0, -alto / 2, fondo / 2), D), ((0, alto / 2, fondo / 2), A_), ((0, -alto / 2, -fondo / 2), Q)):
            ERR_CUNA[0] = max(ERR_CUNA[0], (pos + R @ Vector(local) - real).length)
        pieza(lista, 'WedgePart', None, pos, R, (grosor, alto, fondo), mat, nombre)


def convertir(prims, grupo):
    lista, n_crater, n_aurora, n_nube = [], 0, 0, 0
    for p in prims:
        t, mat, nombre = p['t'], p['mat'], nombre_de(p, grupo)
        if t == 'caja' and mat == 'crater':               # los bloques del borde del cráter se solapan en las esquinas: uno sí y
            n_crater += 1                                  # otro no, 0,04 más arriba, para que tapas y bases no sean coplanares
            if n_crater % 2:
                p = dict(p, c=p['c'] + Vector((0, 0, 0.04)))
        if t == 'caja' and mat.startswith('aurora'):      # tramos seguidos de aurora casi rectos: anchos alternos (0,8 y 0,9)
            n_aurora += 1
            if n_aurora % 2:
                p = dict(p, s=Vector((p['s'][0] * 1.12, p['s'][1], p['s'][2])))
        if t == 'caja':
            choca = grupo == 'Suelo' and abs(p['s'][0] - 22) < 1e-6 and abs(p['s'][1] - 24) < 1e-6   # solo las baldosas del carril
            caja_b(lista, p['c'], p['R'], p['s'], mat, nombre, choca)
        elif t == 'nube_base':
            w, d, h = p['s']
            eje = Vector((1, 0, 0)) if w >= d else Vector((0, 1, 0))
            if p['torre']:                                 # piso de una torre: bolas a lo largo del lado largo (cúmulo, no pila de discos)
                D = 0.62 * min(w, d)
                n = max(2, round(max(w, d) / D * 1.2))
                for k in range(n):
                    f = k / (n - 1) - 0.5
                    bola_b(lista, p['c'] + eje * f * (max(w, d) - D), D, mat, nombre)
            else:                                          # base plana redonda: dos discos a lo largo del lado largo; el segundo es
                D = min(w, d)                              # 0,12 más alto para que sus tapas no sean coplanares con las del primero,
                dz = Vector((0, 0, 0.15 * (n_nube % 7)))   # y cada nube sube 0,15·(i mod 7): las bases de todas acababan en el
                n_nube += 1                                # mismo plano (borde -1,5, mar -9) y las vecinas se solapan
                for k, s in enumerate((-1, 1)):
                    disco_b(lista, p['c'] + dz + eje * s * (max(w, d) - D) / 2, D * (1 - 0.04 * k), h + 0.12 * k, mat, nombre)
        elif t == 'nube_bulto':                            # bulto: una bola del tamaño medio de la caja
            w, d, h = p['s']
            bola_b(lista, p['c'] + Vector((0, 0, -0.15 * h)), (w + d + h) / 3 * 1.1, mat, nombre)
        elif t == 'prisma':
            u0, u1 = p['w0'], p['w1']
            mid = (u0 + u1) / 2

            def P3(u, v):
                if p['plano'] == 'YZ':
                    return (mid, u, v)
                if p['plano'] == 'XY':
                    return (u, v, mid)
                return (u, mid, v)
            for a, b, c in triangular(p['pts']):
                triangulo_rbx(lista, *(a_rbx(P3(*p['pts'][k])) for k in (a, b, c)), abs(u1 - u0), mat, nombre)
        elif t == 'torno':                                 # aro o anillo de planeta: una corona de bloques
            axis = p['p1'] - p['p0']
            d = axis.normalized()
            up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
            u = d.cross(up).normalized()
            w = d.cross(u).normalized()
            rs, ts = [r for r, _ in p['prof']], [t_ for _, t_ in p['prof']]
            rm, ancho = (min(rs) + max(rs)) / 2, max(rs) - min(rs)
            grosor, tm = (max(ts) - min(ts)) * axis.length, (min(ts) + max(ts)) / 2
            N = 16 if rm < 12 else 36
            L = 2 * (rm + ancho / 2) * math.tan(math.pi / N)
            rot0 = math.pi / p['segs'] if p['rot'] is None else p['rot']
            corona = []
            for k in range(N):
                a = rot0 + 2 * math.pi * k / N
                er, et = u * math.cos(a) + w * math.sin(a), -u * math.sin(a) + w * math.cos(a)
                R_b = Matrix((et, er, -d)).transposed()
                caja_b(corona, p['p0'] + axis * tm + er * rm, R_b, (L, ancho, grosor * (1.06 if k % 2 else 1.0)), mat, nombre)
            if grupo == 'Aros':      # cada aro, un Model «Aro» con una pieza invisible «Centro»: el juego lee ahi centro y radio
                centro = dict(corona[0], pos=a_rbx(p['p0'] + axis * tm), R=Matrix.Identity(3), size=Vector((1, 1, 1)),
                              transp=1.0, colision=False, sombra=False, nombre='Centro', material='SmoothPlastic', color='#ffffff')
                lista.append(dict(modelo='Aro', hijos=corona + [centro], radio=rm))
            else:
                lista += corona
        elif t == 'roca':
            c, r = p['c'], p['r']
            if p['jitter'] == 0 and p['squash'] == (1, 1, 1):          # planeta
                bola_b(lista, c, 2 * r, mat, nombre)
            elif p['jitter'] == 0:                                    # banda del planeta (en build_mapa: radio 0,93 R a +0,3 R)
                R0 = r / 0.93
                disco_b(lista, c, 2 * math.sqrt(R0 ** 2 - (0.3 * R0) ** 2) * 1.03, 0.22 * R0, mat, nombre)
            else:                                                     # roca o asteroide: dos bloques girados
                g = random.Random(p['seed'])
                for k, (fx, fy, fz) in enumerate(((1.45, 1.2, 1.1), (1.0, 1.3, 0.95))):
                    R_b = Euler([math.radians(g.uniform(-40, 40)) for _ in range(3)]).to_matrix()
                    off = Vector((g.uniform(-1, 1), g.uniform(-1, 1), g.uniform(-0.5, 0.5))) * 0.35 * r * k
                    caja_b(lista, c + off, R_b, (fx * r, fy * r, fz * r), mat, nombre)
    return lista


def piezas_de(l):
    """Las piezas de una lista que puede llevar modelos (los aros): las de dentro de cada modelo cuentan."""
    for e in l:
        if 'modelo' in e:
            yield from e['hijos']
        else:
            yield e


modelo = []                                               # [(zona, [(grupo, [piezas o modelos])])]
for Z, P in ZG:
    modelo.append((Z, [(k, convertir(P[k].prims, k)) for k in bm.PIEZAS]))
todas = [q for _, gs in modelo for _, l in gs for q in piezas_de(l)]
for q in todas:
    R = q['R']
    assert max(abs(v) for fila in (R.transposed() @ R - Matrix.Identity(3)) for v in fila) < 1e-4 and abs(R.determinant() - 1) < 1e-4, q
    assert min(q['size']) >= 0.02 and max(q['size']) <= 2048, q
assert ERR_CUNA[0] < 1e-4, ERR_CUNA
A.log('piezas', len(todas), 'error de las cuñas', ERR_CUNA[0])


# ---------------------------------------------------------------- XML de Roblox (rbxmx / rbxlx, versión 4)
def num(v, dec=4):
    s = ('%.*f' % (dec, v)).rstrip('0').rstrip('.')
    return '0' if s in ('', '-0') else s


def color_u32(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return (0xFF << 24) | (r << 16) | (g << 8) | b


REF = [0]


def ref():
    REF[0] += 1
    return 'RBX%08X' % REF[0]


def props_parte(q):
    pos, R, s = q['pos'], q['R'], q['size']
    rr = ''.join('<R%d%d>%s</R%d%d>' % (i, j, num(R[i][j], 6), i, j) for i in range(3) for j in range(3))
    out = ['<bool name="Anchored">true</bool>']
    out += ['<token name="%sSurface">0</token>' % k for k in ('Back', 'Bottom', 'Front', 'Left', 'Right', 'Top')]
    out += ['<CoordinateFrame name="CFrame"><X>%s</X><Y>%s</Y><Z>%s</Z>%s</CoordinateFrame>' % (num(pos.x), num(pos.y), num(pos.z), rr),
            '<bool name="CanCollide">%s</bool>' % ('true' if q['colision'] else 'false'),
            '<bool name="CastShadow">%s</bool>' % ('true' if q['sombra'] else 'false'),
            '<Color3uint8 name="Color3uint8">%d</Color3uint8>' % color_u32(q['color']),
            '<token name="Material">%d</token>' % MATERIAL[q['material']],
            '<string name="Name">%s</string>' % q['nombre'],
            '<float name="Transparency">%s</float>' % num(q['transp']),
            '<Vector3 name="size"><X>%s</X><Y>%s</Y><Z>%s</Z></Vector3>' % (num(s.x), num(s.y), num(s.z))]
    if q['clase'] == 'Part':
        out.append('<token name="shape">%d</token>' % FORMA[q['forma']])
    return out


def item(clase, props, hijos=()):
    return ['<Item class="%s" referent="%s">' % (clase, ref()), '<Properties>'] + props + ['</Properties>'] + [l for h in hijos for l in h] + ['</Item>']


def item_entrada(e):
    if 'modelo' in e:
        return item('Model', ['<string name="Name">%s</string>' % e['modelo']], [item(q['clase'], props_parte(q)) for q in e['hijos']])
    return item(e['clase'], props_parte(e))


def item_modelo():
    zonas = []
    for Z, gs in modelo:
        carpetas = [item('Folder', ['<string name="Name">%s</string>' % k], [item_entrada(e) for e in l]) for k, l in gs]
        zonas.append(item('Model', ['<string name="Name">%s</string>' % ZONA_RBX[Z['clave']]], carpetas))
    return item('Model', ['<string name="Name">Mapa_v01</string>'], zonas)


CAB = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
       'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">', '<External>null</External>', '<External>nil</External>']
os.makedirs(os.path.join(OUT, 'previews'), exist_ok=True)
RUTA_MODELO = os.path.join(OUT, 'Mapa-v01.rbxmx')
with open(RUTA_MODELO, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(CAB + item_modelo() + ['</roblox>']) + '\n')
spawn = dict(pos=a_rbx((0, bm.Y_INICIO + 10, 0.5)), R=Matrix.Identity(3), size=Vector((6, 1, 6)), colision=True, sombra=True,
             color='#ffffff', material='SmoothPlastic', nombre='SpawnLocation', transp=0.0, clase='SpawnLocation')
atmos = ['<string name="Name">Atmosphere</string>', '<float name="Density">0.25</float>', '<float name="Offset">0.2</float>',
         '<Color3 name="Color"><R>0.78</R><G>0.87</G><B>1</B></Color3>', '<Color3 name="Decay"><R>0.55</R><G>0.68</G><B>0.95</B></Color3>',
         '<float name="Glare">0</float>', '<float name="Haze">0.8</float>']
lugar = item('Workspace', ['<string name="Name">Workspace</string>'],
             [item_modelo(), item('SpawnLocation', props_parte(spawn) + ['<bool name="Neutral">true</bool>', '<int name="Duration">0</int>'])])
luz = item('Lighting', ['<string name="Name">Lighting</string>'], [item('Atmosphere', atmos)])
RUTA_LUGAR = os.path.join(OUT, 'Mapa-v01-prueba.rbxlx')
with open(RUTA_LUGAR, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(CAB + lugar + luz + ['</roblox>']) + '\n')


# ---------------------------------------------------------------- comprobación: leer el XML como Roblox y contar
def leer(ruta):
    out = []
    for it in ET.parse(ruta).getroot().iter('Item'):
        if it.get('class') not in ('Part', 'WedgePart', 'SpawnLocation'):
            continue
        pr = it.find('Properties')
        cf = pr.find("CoordinateFrame[@name='CFrame']")
        sz = pr.find("Vector3[@name='size']")
        sh = pr.find("token[@name='shape']")
        out.append(dict(clase=it.get('class'), forma=int(sh.text) if sh is not None else None,
                        pos=Vector([float(cf.find(k).text) for k in 'XYZ']),
                        R=Matrix([[float(cf.find('R%d%d' % (i, j)).text) for j in range(3)] for i in range(3)]),
                        size=Vector([float(sz.find(k).text) for k in 'XYZ']),
                        color=int(pr.find("Color3uint8[@name='Color3uint8']").text), material=int(pr.find("token[@name='Material']").text),
                        transp=float(pr.find("float[@name='Transparency']").text), choca=pr.find("bool[@name='CanCollide']").text == 'true'))
    return out


leidas = leer(RUTA_MODELO)
assert len(leidas) == len(todas), (len(leidas), len(todas))
assert len(leer(RUTA_LUGAR)) == len(todas) + 1
cuenta = {}
for Z, gs in modelo:
    c = cuenta.setdefault(Z['clave'], {})
    for k, l in gs:
        c[k] = len(list(piezas_de(l)))
aros = sum(1 for _, gs in modelo for _, l in gs for e in l if 'modelo' in e)
assert aros == 3 * len(modelo), aros
por_tipo = {}
for q in todas:
    k = q['clase'] + ('/' + q['forma'] if q['forma'] else '') + ' ' + q['material']
    por_tipo[k] = por_tipo.get(k, 0) + 1
mn = Vector([min(q['pos'][a] for q in todas) for a in range(3)])
mx = Vector([max(q['pos'][a] for q in todas) for a in range(3)])
A.log('por zona', cuenta, 'por tipo', por_tipo, 'caja de centros', tuple(round(v) for v in mn), tuple(round(v) for v in mx),
      'chocan', sum(q['choca'] for q in leidas))
A.write_json(os.path.join(OUT, 'datos.json'), {
    'pieza': 'Mapa v01 en piezas nativas de Roblox (Part y WedgePart, sin mallas: no hace falta subir nada)', 'sin_probar_en_studio': True,
    'archivos': {'Mapa-v01.rbxmx': 'modelo Mapa_v01 para insertar en una place (zonas como Model, piezas por carpeta)',
                 'Mapa-v01-prueba.rbxlx': 'place de prueba: el modelo, un SpawnLocation al principio del carril y una Atmosphere'},
    'ejes': 'Blender (x, y, z) -> Roblox (x, z, -y): el vuelo va hacia -Z; origen = el de la Pradera de Codex; 1 unidad = 1 stud',
    'zonas_z_roblox': {Z['clave']: [-(bm.Y_INICIO + i * bm.LARGO), -(bm.Y_INICIO + (i + 1) * bm.LARGO)] for i, (Z, _) in enumerate(modelo)},
    'piezas_total': len(todas), 'piezas_por_zona': cuenta, 'piezas_por_tipo': por_tipo,
    'chocan': 'solo las baldosas del carril (CanCollide); todo lo demás es decorado sin colisión',
    'neon': sorted(NEON), 'transparencia': TRANSP})
if FASE == 'xml':
    A.log('listo')
    raise SystemExit

# ---------------------------------------------------------------- renders: las piezas leídas del XML, rehechas en Blender
A.clean_scene()
A.REGIONS.clear()
CM, CC = A.collection('Roblox'), A.collection('Camaras')


def geo_local(q):
    """Vértices, caras (con la normal hacia fuera) y si cada cara es plana en Roblox, en las coordenadas locales de la pieza.
    Las bolas y los lados de los cilindros son curvos en Roblox: sus facetas de aquí no cuentan para el parpadeo."""
    sx, sy, sz = q['size'] / 2
    if q['clase'] == 'WedgePart':                         # base abajo, cara trasera en +Z, rampa hacia -Z
        V = [(-sx, -sy, -sz), (sx, -sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (-sx, sy, sz), (sx, sy, sz)]
        return V, [(0, 1, 3, 2), (2, 3, 5, 4), (0, 4, 5, 1), (0, 2, 4), (1, 5, 3)], [True] * 5
    if q['forma'] == 0:                                   # bola
        r, V, F = sx, [], []
        nu, nv = 18, 10
        V.append((0, r, 0))
        for i in range(1, nv):
            ph = math.pi * i / nv
            V += [(r * math.sin(ph) * math.cos(2 * math.pi * j / nu), r * math.cos(ph), r * math.sin(ph) * math.sin(2 * math.pi * j / nu))
                  for j in range(nu)]
        V.append((0, -r, 0))
        F += [(0, 1 + (j + 1) % nu, 1 + j) for j in range(nu)]
        for i in range(nv - 2):
            a, b = 1 + i * nu, 1 + (i + 1) * nu
            F += [(a + j, a + (j + 1) % nu, b + (j + 1) % nu, b + j) for j in range(nu)]
        last = len(V) - 1
        F += [(last, 1 + (nv - 2) * nu + j, 1 + (nv - 2) * nu + (j + 1) % nu) for j in range(nu)]
        return V, F, [False] * len(F)
    if q['forma'] == 2:                                   # cilindro a lo largo de X
        r, n = min(sy, sz), 20
        V = [(x, r * math.cos(2 * math.pi * j / n), r * math.sin(2 * math.pi * j / n)) for x in (-sx, sx) for j in range(n)]
        F = [(j, (j + 1) % n, n + (j + 1) % n, n + j) for j in range(n)] + [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
        return V, F, [False] * n + [True, True]
    V = [(x, y, z) for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]
    return V, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], [True] * 6


mats = {}


def material(q):
    k = (q['color'], q['material'], q['transp'])
    if k not in mats:
        h = '#%06x' % (q['color'] & 0xFFFFFF)
        m = bpy.data.materials.new('rbx_%d' % len(mats))
        m.use_nodes = True
        b = m.node_tree.nodes.get('Principled BSDF')
        b.inputs['Base Color'].default_value = (*lin(h), 1)
        b.inputs['Roughness'].default_value = 0.6
        if q['material'] == MATERIAL['Neon']:
            b.inputs['Emission Color'].default_value = (*lin(h), 1)
            b.inputs['Emission Strength'].default_value = 2.0
        if q['transp'] > 0:
            b.inputs['Alpha'].default_value = 1 - q['transp']
        mats[k] = m
    return mats[k]


bms = {True: bmesh.new(), False: bmesh.new()}           # caras planas en Roblox / caras curvas (bolas y lados de cilindro)
slots = {True: [], False: []}
for q in leidas:
    V, F, planas = geo_local(q)
    Vw = [MRt @ (q['pos'] + q['R'] @ Vector(v)) for v in V]   # giro propio (det 1) y MRt (det 1): las normales siguen hacia fuera
    m = material(q)
    for plana in (True, False):
        caras = [fc for fc, pl in zip(F, planas) if pl == plana]
        if not caras:
            continue
        if m not in slots[plana]:
            slots[plana].append(m)
        vs = {}
        for fc in caras:
            for i in fc:
                if i not in vs:
                    vs[i] = bms[plana].verts.new(Vw[i])
            bms[plana].faces.new([vs[i] for i in fc]).material_index = slots[plana].index(m)
obs = {}
for plana, nombre in ((True, 'Mapa_v01_roblox_planas'), (False, 'Mapa_v01_roblox_curvas')):
    me = bpy.data.meshes.new(nombre)
    bms[plana].to_mesh(me)
    obs[plana] = bpy.data.objects.new(nombre, me)
    for m in slots[plana]:
        me.materials.append(m)
    CM.objects.link(obs[plana])
from mas1_ave import caras_coplanares
COPL, EJ = caras_coplanares(obs[True], maximo=100000)     # pares de caras planas solapadas en el mismo plano: parpadeo en Roblox
reparto = {}
for e in EJ:
    k = tuple(round(v, 1) for v in e['normal']) + (round(e['centro'][2], 1) if abs(e['normal'][2]) > 0.9 else None,)
    reparto[k] = reparto.get(k, 0) + 1
A.log('caras coplanares solapadas', COPL, 'reparto (normal, z si es horizontal)', sorted(reparto.items(), key=lambda kv: -kv[1])[:12], EJ[:4])
datos = json.load(open(os.path.join(OUT, 'datos.json'), encoding='utf-8'))
datos['caras_coplanares_solapadas'] = COPL
A.write_json(os.path.join(OUT, 'datos.json'), datos)
if FASE == 'check':
    A.log('listo')
    raise SystemExit
if os.path.exists(bm.PRADERA):
    CP = A.collection('Pradera_Codex')
    with bpy.data.libraries.load(bm.PRADERA, link=False) as (src, dst):
        dst.objects = list(src.objects)
    for o in dst.objects:
        if o is not None and o.type == 'MESH':
            CP.objects.link(o)
sol(CC, 'Sol', 3.2, (-0.4, 0.5, -0.75))
sol(CC, 'Relleno', 0.8, (0.6, -0.3, -0.4), 20.0)
A.setup_render((1280, 720), 'CYCLES', 24)
bpy.context.scene.render.image_settings.file_format = 'JPEG'
bpy.context.scene.render.image_settings.quality = 90
fotos = []


def foto(nombre, loc, objetivo, lente, cielo, rotulo):
    A.setup_world(lin(cielo), 1.0)
    cam = A.camera(CC, 'cam_' + nombre, loc, objetivo, lens=lente)
    cam.data.clip_end = 6000
    ruta = os.path.join(OUT, 'previews', nombre + '.jpg')
    A.render(ruta, cam)
    fotos.append((ruta, rotulo))


foto('Roblox-general', (-520, -140, 420), (0, 760, 0), 32, '#9fd3ff', 'MAPA EN PIEZAS DE ROBLOX (LEIDO DEL RBXMX) - PRADERA DE CODEX DELANTE')
for i, Z in enumerate(bm.ZONAS):
    y0 = bm.Y_INICIO + i * bm.LARGO
    foto('Roblox-%s-entrada' % Z['clave'], (18, y0 - 75, 30), (0, y0 + 40, 24), 26, Z['cielo'], 'ENTRADA %s' % Z['nombre'])
    foto('Roblox-%s-dentro' % Z['clave'], (0, y0 + 14, 16), (0, y0 + 200, 8), 24, Z['cielo'], 'DENTRO DE %s' % Z['nombre'])
W.contact_sheet(fotos, 3, os.path.join(OUT, '_hoja.png'),
                title='MAPA V01 EN PIEZAS DE ROBLOX (PART Y WEDGEPART) - RENDERS DE BLENDER DEL RBXMX LEIDO (SIN PROBAR EN STUDIO)')
a_jpg(os.path.join(OUT, '_hoja.png'), os.path.join(OUT, 'Mapa-v01-roblox-hoja.jpg'), 0.5)
A.log('listo')
