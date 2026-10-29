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
def pluma(mb, M, raiz, ang, largo, ancho, grosor, zc, bandas, afilar=0.86, chaflan=0.12, lado_mat=None):
    """Una pluma plana de punta achaflanada. raiz=(x, y) y ang (grados, contra el reloj desde +X) en el plano plano del marco; M es la matriz
    del marco. bandas=[(fraccion_final, region), ...] de la raiz a la punta: se corta la pluma en bandas de color (sin caras internas).
    zc = altura del centro en el marco, grosor en Z. Los vecinos que se solapan deben tener zc distintos (mas de 0,04) para no
    tener caras coplanares (parpadeo en Roblox)."""
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
def piezas_sueltas(ob, tol=0.05, minimo_verts=1):
    """Islas de vertices conectados -> grafo por cajas con margen `tol`. Devuelve las islas (caja min/max, numero de vertices) que no
    quedan unidas al cuerpo principal (la isla con mas vertices). Vacio = nada flota."""
    me = ob.data
    n = len(me.vertices)
    co = np.empty(n * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(n, 3)
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
    raiz = {}
    for i in range(n):
        raiz.setdefault(find(i), []).append(i)
    islas = []
    for r, idx in raiz.items():
        p = co[idx]
        islas.append((p.min(0) - tol, p.max(0) + tol, len(idx)))
    m = len(islas)
    par = list(range(m))

    def f2(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for i in range(m):
        for j in range(i + 1, m):
            a, b = islas[i], islas[j]
            if all(a[0][k] <= b[1][k] and b[0][k] <= a[1][k] for k in range(3)):
                x, y = f2(i), f2(j)
                if x != y:
                    par[x] = y
    grupos = {}
    for i in range(m):
        grupos.setdefault(f2(i), []).append(i)
    principal = max(grupos.values(), key=lambda g: sum(islas[i][2] for i in g))
    fuera = []
    for g in grupos.values():
        if g is principal:
            continue
        lo = np.min([islas[i][0] for i in g], axis=0) + tol
        hi = np.max([islas[i][1] for i in g], axis=0) - tol
        fuera.append({'caja_min': [round(float(v), 2) for v in lo], 'caja_max': [round(float(v), 2) for v in hi],
                      'vertices': int(sum(islas[i][2] for i in g))})
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
