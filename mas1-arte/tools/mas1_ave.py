# Piezas comunes de las mascotas voladoras del proyecto +1 (aguila, grifo, fenix), version 02:
# alas de plumas en abanico (arco con dihedro, tres capas, bandas de color sin caras internas), colas de abanico, escamas sobre la piel
# de voxeles, rombos dorados y una comprobacion automatica de piezas sueltas (nada puede flotar fuera del cuerpo).
# Convencion: +Y delante, +Z arriba, +X derecha; 1 unidad = 1 stud. Las plumas se construyen planas (plano XY) y despues se colocan con
# una matriz de marco (dihedro y barrido del ala); asi todas las rotaciones son propias y las normales salen bien.
from mas1_pet import *


def rz(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'Z')


def ry(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'Y')


def rx(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'X')


def tr(v):
    return Matrix.Translation(Vector(v))


# ------------------------------------------------------------------ plumas
def pluma(mb, M, raiz, ang, largo, ancho, grosor, zc, bandas, afilar=0.86, chaflan=0.12, lado_mat=None, punta=None):
    """Una pluma plana de punta achaflanada. raiz=(x, y) y ang (grados, contra el reloj desde +X) en el plano plano del marco; M es la matriz
    del marco. bandas=[(fraccion_final, region), ...] de la raiz a la punta: se corta la pluma en bandas de color (sin caras internas).
    zc = altura del centro en el marco, grosor en Z. Los vecinos que se solapan deben tener zc distintos (mas de 0,04) para no
    tener caras coplanares (parpadeo en Roblox). punta = fraccion del largo donde empieza la punta afilada (pluma en flecha, como las del
    cofre de Codex); None = punta achaflanada de siempre."""
    a = math.radians(ang)
    d = Vector((math.cos(a), math.sin(a), 0.0))
    n = Vector((-d.y, d.x, 0.0))
    R = Vector((raiz[0], raiz[1], 0.0))

    def ancho_en(t):
        return ancho * (1.0 - (1.0 - afilar) * t)

    c = min(chaflan, 0.4 * ancho_en(1.0))
    w1 = ancho_en(1.0)
    P = lambda t, k: R + d * (t * largo) + n * (k * ancho_en(t) / 2.0)
    tc = max(0.0, 1.0 - c / largo)
    poly = [P(0.0, -1), P(tc, -1), P(1.0, -1.0 + 2.0 * c / w1), P(1.0, 1.0 - 2.0 * c / w1), P(tc, 1), P(0.0, 1)]
    if punta is not None:
        poly = [P(0.0, -1), P(punta, -1), P(1.0, 0.0), P(punta, 1), P(0.0, 1)]
    poly = [(p.x, p.y) for p in poly]
    antes = mb.mark()
    mb.prism(poly, zc - grosor / 2.0, zc + grosor / 2.0, bandas[0][1], plane='XY', side_mat=lado_mat or bandas[0][1])
    bm = mb.bm
    bm.normal_update()
    cortes = [f for (f, _) in bandas[:-1]]
    for fr in cortes:
        vs = [v for v in bm.verts if v not in antes]
        geom = list(vs) + list({e for v in vs for e in v.link_edges}) + list({f for v in vs for f in v.link_faces})
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=R + d * (fr * largo), plane_no=d)
    vs = [v for v in bm.verts if v not in antes]
    bm.normal_update()
    caras = {f for v in vs for f in v.link_faces}
    lim = [f for (f, _) in bandas]
    for f in caras:
        cen = f.calc_center_median()
        t = ((cen - R).dot(d)) / largo
        k = 0
        while k < len(lim) - 1 and t > lim[k] + 1e-6:
            k += 1
        # las paredes largas (laterales) toman el color de su banda; la punta y la raiz tambien
        f.material_index = mb.mi(bandas[k][1] if (lado_mat is None or abs(f.normal.z) > 0.5) else lado_mat)
    if M is not None:
        mb.xform_since(antes, M)


def marco_ala(S, s, A, d1, sw1, d2, sw2):
    """Marcos del ala: M1 en el hombro (dihedro d1 hacia arriba y barrido sw1 hacia atras) y M2 en la muñeca (d2 y sw2 extra).
    Devuelve (M1, M2, muneca_en_mundo)."""
    M1 = tr(S) @ rz(-s * sw1) @ ry(-s * d1)
    M2 = M1 @ tr((s * A, 0, 0)) @ rz(-s * sw2) @ ry(-s * d2)
    H = M2 @ Vector((0, 0, 0))
    return M1, M2, Vector(H)


def dir_ala(s, th):
    """Angulo (contra el reloj desde +X) de una pluma que sale del ala hacia fuera y se barre th grados hacia atras."""
    return -th if s > 0 else 180.0 + th


def rombo(mb, c, tam, grosor, mat, eje='Y', rot=45.0, M=None):
    """Cubo girado (rombo): adorno dorado de las mascotas raras. eje = la direccion en la que mira; M = marco opcional (ala)."""
    antes = mb.mark()
    if eje == 'Y':
        mb.box((0, 0, 0), (tam, grosor, tam), mat)
        L = tr(c) @ ry(rot)
    elif eje == 'X':
        mb.box((0, 0, 0), (grosor, tam, tam), mat)
        L = tr(c) @ rx(rot)
    else:
        mb.box((0, 0, 0), (tam, tam, grosor), mat)
        L = tr(c) @ rz(rot)
    mb.xform_since(antes, (M @ L) if M is not None else L)


def caja_marco(mb, M, c, size, mat, bevel=0.0):
    """Caja colocada en un marco (hueso del ala, cola...)."""
    antes = mb.mark()
    mb.box(c, size, mat, bevel=bevel)
    mb.xform_since(antes, M)


def cubo_girado(mb, c, size, mat, rot=(0, 0, 0)):
    antes = mb.mark()
    mb.box((0, 0, 0), size, mat)
    M = tr(c) @ rz(rot[2]) @ ry(rot[1]) @ rx(rot[0])
    mb.xform_since(antes, M)


# ------------------------------------------------------------------ patas que cuelgan y parpados (lo que pidio Maikol: pies que guindan al volar, ojos que parpadean)
def colgar_pata(mb, pivote, angulo=-35.0, abrir=0.0):
    """Gira toda la pieza de un hueso de pata alrededor de su pivote (cadera/rodilla): angulo < 0 lleva el pie hacia atras y los dedos
    apuntan hacia abajo; abrir separa un poco la pata hacia fuera (grados, con signo del lado). La pata queda colgando en la pose neutra."""
    M = tr(pivote) @ ry(abrir) @ rx(angulo) @ tr(Vector(pivote) * -1)
    bmesh.ops.transform(mb.bm, matrix=M, verts=mb.bm.verts[:])


def parpado(mb, ojo_c, ojo_tam, frente, piel, linea, holgura=0.06):
    """Parpado de un ojo en su hueso Lid: un bloque del color de la piel (un poco mayor que el ojo) escondido justo detras del ojo, tocando su
    cara trasera (asi no flota), con una raya oscura de ojo cerrado. Para parpadear el hueso avanza `dy` en +Y y el bloque tapa el ojo y su
    brillo (frente = la cara mas adelantada del ojo). En Roblox un hueso no se escala, por eso es un bloque que avanza.
    Devuelve dy (studs)."""
    cx, cy, cz = ojo_c
    w, d, h = ojo_tam
    fondo = 0.10

    def lejos(c, half, rejilla=0.2):
        # las caras del bloque no deben caer en un plano de cara de voxel (multiplos impares de 0,1): serian coplanares y parpadearian
        while any(abs(((c + sg * half) - rejilla / 2) / rejilla - round(((c + sg * half) - rejilla / 2) / rejilla)) * rejilla < 0.012
                  for sg in (-1, 1)):
            half -= 0.004
        return half
    y_esc = cy - d / 2.0 - fondo / 2.0                    # escondido detras del ojo
    mb.box((cx, y_esc, cz), (2 * lejos(cx, (w + holgura) / 2), fondo, 2 * lejos(cz, (h + holgura) / 2)), piel)
    mb.box((cx, y_esc, cz - 0.02), (2 * lejos(cx, (w - 0.02) / 2), fondo + 0.03, 2 * lejos(cz - 0.02, 0.025)), linea)   # raya de ojo cerrado
    y_cerrado = frente + 0.025 - fondo / 2.0              # cerrado: el bloque queda 0,025 por delante de la cara mas adelantada del ojo
    return y_cerrado - y_esc


# ------------------------------------------------------------------ escamas (plaquitas) sobre las caras expuestas de los voxeles
def escamas(V, MBS, bone, mat, normal, filtro, alto=0.08, patron=None, tam=None):
    """Plaquitas de `alto` studs sobre las caras expuestas (mirando a `normal`) de las celdas de `bone` que cumplan filtro(p).
    patron(i, j, k) -> True/False elige cuales (tresbolillo). Quedan pegadas a la piel escalonada: nada flota."""
    n = tuple(normal)
    cnt = 0
    h = V.cell / 2.0
    t = V.cell * (tam if tam else 0.84)
    for ijk, (b, m) in V.cells.items():
        if b != bone:
            continue
        if (ijk[0] + n[0], ijk[1] + n[1], ijk[2] + n[2]) in V.cells:
            continue
        p = V.pos(ijk)
        if not filtro(p):
            continue
        if patron is not None and not patron(*ijk):
            continue
        size = [t, t, t]
        for a in range(3):
            if n[a] != 0:
                size[a] = alto
        c = Vector(p) + Vector(n) * (h + alto / 2.0 - 0.005)
        MBS[bone].box(c, size, mat)
        cnt += 1
    return cnt


def tresbolillo(i, j, k):
    return (i + j + k) % 2 == 0


def dispersas(prob=0.5, seed=0):
    """Plaquitas repartidas al azar (siempre las mismas): el aspecto irregular de las escamas de Roba un huevo."""
    def f(i, j, k):
        h = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (seed * 2654435761)
        return ((h >> 3) & 0xffff) % 100 < int(prob * 100)
    return f


# ------------------------------------------------------------------ comprobacion de piezas sueltas
def piezas_sueltas(ob, paso=0.04, tol=0.06):
    """Islas de vertices conectados; dos islas cuentan como unidas si sus superficies se tocan o se cruzan (puntos muestreados cada `paso`
    studs a menos de `tol`). Devuelve (las islas o grupos de islas que no quedan unidos al cuerpo principal, numero de islas).
    Vacio = nada flota. Mas fiel que comparar cajas: un bloque girado cuya caja roza otra pieza sin tocarla se detecta."""
    from mathutils.kdtree import KDTree
    me = ob.data
    me.calc_loop_triangles()
    n = len(me.vertices)
    co = np.empty(n * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(n, 3).astype(np.float64)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b:
            parent[a] = b
    isla_v = np.array([find(i) for i in range(n)])
    raices = sorted(set(isla_v.tolist()))
    idx_isla = {r: k for k, r in enumerate(raices)}
    m = len(raices)
    nt = len(me.loop_triangles)
    tris = np.empty(nt * 3, np.int32)
    me.loop_triangles.foreach_get('vertices', tris)
    tris = tris.reshape(nt, 3)
    P = co[tris]
    lab_t = np.array([idx_isla[isla_v[t[0]]] for t in tris])
    area = 0.5 * np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1)
    ns = np.maximum(1, np.ceil(area / (paso * paso)).astype(int))
    ti = np.repeat(np.arange(nt), ns)
    rng = np.random.default_rng(7)
    r1, r2 = rng.random(len(ti)), rng.random(len(ti))
    fl = r1 + r2 > 1
    r1[fl], r2[fl] = 1 - r1[fl], 1 - r2[fl]
    pts = P[ti, 0] + r1[:, None] * (P[ti, 1] - P[ti, 0]) + r2[:, None] * (P[ti, 2] - P[ti, 0])
    lab = lab_t[ti]
    pts = np.concatenate([pts, co])                       # y los propios vertices (islas diminutas)
    lab = np.concatenate([lab, np.array([idx_isla[r] for r in isla_v])])
    kd = KDTree(len(pts))
    for i, p in enumerate(pts):
        kd.insert((p[0], p[1], p[2]), i)
    kd.balance()
    par = list(range(m))

    def f2(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for i, p in enumerate(pts):
        li = lab[i]
        for (_, j, _) in kd.find_range((p[0], p[1], p[2]), tol):
            lj = lab[j]
            if lj != li:
                x, y = f2(li), f2(lj)
                if x != y:
                    par[x] = y
    cuenta = np.bincount(lab, minlength=m)
    grupos = {}
    for k in range(m):
        grupos.setdefault(f2(k), []).append(k)
    principal = max(grupos.values(), key=lambda g: int(sum(cuenta[k] for k in g)))
    fuera = []
    for g in grupos.values():
        if g is principal:
            continue
        sel = np.isin(lab, g)
        lo, hi = pts[sel].min(0), pts[sel].max(0)
        fuera.append({'caja_min': [round(float(v), 2) for v in lo], 'caja_max': [round(float(v), 2) for v in hi], 'puntos': int(sel.sum())})
    return fuera, m


# ------------------------------------------------------------------ caras coplanares solapadas (parpadeo, «z-fighting», en Roblox)
def _recorta(sujeto, clip):
    """Sutherland-Hodgman: poligono convexo `sujeto` recortado por el triangulo convexo `clip` (ambos Nx2)."""
    def dentro(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-12

    def cruce(p, q, a, b):
        r = q - p
        s_ = b - a
        den = r[0] * s_[1] - r[1] * s_[0]
        if abs(den) < 1e-15:
            return q
        t = ((a[0] - p[0]) * s_[1] - (a[1] - p[1]) * s_[0]) / den
        return p + t * r
    orient = (clip[1][0] - clip[0][0]) * (clip[2][1] - clip[0][1]) - (clip[1][1] - clip[0][1]) * (clip[2][0] - clip[0][0])
    c = clip if orient > 0 else clip[::-1]
    out = [np.array(v) for v in sujeto]
    for i in range(3):
        a, b = c[i], c[(i + 1) % 3]
        ent = out
        out = []
        if not ent:
            break
        prev = ent[-1]
        for cur in ent:
            if dentro(cur, a, b):
                if not dentro(prev, a, b):
                    out.append(cruce(prev, cur, a, b))
                out.append(cur)
            elif dentro(prev, a, b):
                out.append(cruce(prev, cur, a, b))
            prev = cur
    return out


def _area(poly):
    if len(poly) < 3:
        return 0.0
    s_ = 0.0
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        s_ += p[0] * q[1] - q[0] * p[1]
    return abs(s_) / 2.0


def caras_coplanares(ob, eps=0.008, area_min=0.002, maximo=40):
    """Pares de triangulos con la misma orientacion, a menos de `eps` studs de distancia sobre su normal y con area solapada mayor que
    `area_min` studs^2: posible parpadeo (z-fighting) en Roblox. Las caras espalda con espalda (normales opuestas) no cuentan.
    Devuelve (numero de pares, ejemplos)."""
    me = ob.data
    me.calc_loop_triangles()
    nt = len(me.loop_triangles)
    nv = len(me.vertices)
    co = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(nv, 3).astype(np.float64)
    tris = np.empty(nt * 3, np.int32)
    me.loop_triangles.foreach_get('vertices', tris)
    tris = tris.reshape(nt, 3)
    P = co[tris]
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ok = ln > 1e-9
    n[ok] /= ln[ok][:, None]
    d = np.einsum('ij,ij->i', n, P[:, 0])
    claves = {}
    for i in range(nt):
        if not ok[i]:
            continue
        k = (int(round(n[i, 0] * 20)), int(round(n[i, 1] * 20)), int(round(n[i, 2] * 20)), int(math.floor(d[i] / (2 * eps))))
        claves.setdefault(k, []).append(i)
    pares = 0
    ej = []
    for k, idx in claves.items():
        grupo = list(idx) + claves.get((k[0], k[1], k[2], k[3] + 1), [])
        if len(grupo) < 2:
            continue
        for a in idx:
            for b_ in grupo:
                if b_ <= a and b_ in idx:
                    continue
                if np.dot(n[a], n[b_]) < 0.98 or abs(d[a] - d[b_]) > eps:
                    continue
                u = P[a, 1] - P[a, 0]
                u /= np.linalg.norm(u)
                v = np.cross(n[a], u)
                A2 = np.stack([P[a] @ u, P[a] @ v], axis=1)
                B2 = np.stack([P[b_] @ u, P[b_] @ v], axis=1)
                if _area(_recorta(A2, B2)) > area_min:
                    pares += 1
                    if len(ej) < maximo:
                        c = (P[a].mean(0) + P[b_].mean(0)) / 2
                        mats = [me.materials[me.polygons[me.loop_triangles[t].polygon_index].material_index].name for t in (a, b_)]
                        ej.append({'centro': [round(float(x), 2) for x in c], 'normal': [round(float(x), 2) for x in n[a]],
                                   'dist': round(float(abs(d[a] - d[b_])), 4), 'materiales': mats})
    return pares, ej
