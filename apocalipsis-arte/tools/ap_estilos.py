# Estilos de pintura compartidos por las piezas del mapa apocalíptico (regiones -> parametros de pintura a mano).
import numpy as np
import ap_lib as A

smooth = A.smoothstep


def _crack(pos, scale, seed, w=0.012):
    n = A.fbm(pos * scale + seed * 3.7, 3, 100 + seed)
    return np.abs(n - 0.5) < w


def _stain(pos, scale, seed, lo=0.60, hi=0.78):
    return smooth(lo, hi, A.fbm(pos * scale + seed * 5.3, 3, 120 + seed))


def _hash(ix, iy, seed):
    h = ((ix * 73856093) ^ (iy * 19349663) ^ (seed * 83492791)) & 0x7fffffff
    h = (((h >> 13) ^ h) * 1274126177) & 0x7fffffff
    return ((h >> 8) & 0xffff).astype(np.float32) / 65535.0


def voro_borde(u, v, escala, seed):
    """Distancia aproximada (en unidades de u, v) al borde de celda de Voronoi mas cercano."""
    pu, pv = u * escala, v * escala
    cu, cv = np.floor(pu).astype(np.int64), np.floor(pv).astype(np.int64)
    d1 = np.full(pu.shape, 1e9, np.float32)
    d2 = np.full(pu.shape, 1e9, np.float32)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            gx, gy = cu + ox, cv + oy
            fx = gx + 0.12 + 0.76 * _hash(gx, gy, seed)
            fy = gy + 0.12 + 0.76 * _hash(gx, gy, seed + 7)
            d = ((pu - fx) ** 2 + (pv - fy) ** 2).astype(np.float32)
            m = d < d1
            d2 = np.where(m, d1, np.minimum(d2, d))
            d1 = np.where(m, d, d1)
    return (np.sqrt(d2) - np.sqrt(d1)) / (2.0 * escala)


def grietas(u, v, escala, seed, ancho, torsion=0.35):
    """Grietas de verdad: bordes de Voronoi torcidos con ruido (lineas quebradas, no isolineas) y de ancho variable.
    escala: celdas por stud; ancho en studs."""
    q = np.stack([u * escala * 1.7, v * escala * 1.7, np.zeros_like(u)], 1)
    wu = (A.fbm(q, 3, 400 + seed) - 0.5) * 2.0 * torsion / escala
    wv = (A.fbm(q + 17.0, 3, 410 + seed) - 0.5) * 2.0 * torsion / escala
    e = voro_borde(u + wu, v + wv, escala, seed)
    return e < ancho * (0.45 + 1.1 * A.fbm(q * 2.3 + 5.0, 2, 420 + seed))


def zonas(u, v, escala, seed, umbral=0.5):
    """Manchas grandes donde se concentran las grietas (no todo el suelo cuarteado por igual)."""
    return A.fbm(np.stack([u * escala, v * escala, np.zeros_like(u)], 1) + 3.0, 2, 430 + seed) > umbral


def asfalto_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    top = nrm[:, 2] > 0.7
    # asfalto cuarteado en zonas + alguna grieta larga que cruza el carril
    cr = top & zonas(x, y, 0.05, 1, 0.52) & grietas(x, y, 0.28, 1, 0.06)
    col[cr] = col[cr] * 0.42
    cr2 = top & zonas(x, y, 0.03, 2, 0.45) & grietas(x, y, 0.07, 2, 0.05, 0.5)
    col[cr2] = col[cr2] * 0.50
    # manchas de aceite y remiendos algo mas oscuros
    st = top & (_stain(pos, 0.35, 3) > 0.4)
    col[st] = col[st] * 0.72
    return col


def lineas_calle(P, msk, pos, nrm, col):
    col = asfalto_x(P, msk, pos, nrm, col)
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    top = nrm[:, 2] > 0.7
    wear = A.fbm(pos * 1.6 + 9.0, 3, 131)
    yel = np.array([0.80, 0.66, 0.20], np.float32)
    wht = np.array([0.80, 0.79, 0.72], np.float32)
    dash = top & (np.abs(y) < 0.40) & (((x + 30.0) % 9.0) < 5.0) & (wear > 0.38)
    col[dash] = col[dash] * 0.25 + yel * 0.75
    for sgn in (-1, 1):
        e = top & (np.abs(y - sgn * 16.4) < 0.28) & (wear > 0.33)
        col[e] = col[e] * 0.25 + wht * 0.75
    return col


def cruce_x(P, msk, pos, nrm, col):
    col = asfalto_x(P, msk, pos, nrm, col)
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    top = nrm[:, 2] > 0.7
    wear = A.fbm(pos * 1.6 + 9.0, 3, 133)
    wht = np.array([0.80, 0.79, 0.72], np.float32)
    yel = np.array([0.80, 0.66, 0.20], np.float32)
    # pasos de cebra en las cuatro bocas
    z_ew = top & (np.abs(y) < 17.5) & (np.abs(x) > 19.5) & (np.abs(x) < 24.5) & (((y + 40.0) % 3.0) < 1.5)
    z_ns = top & (np.abs(x) < 17.5) & (np.abs(y) > 19.5) & (np.abs(y) < 24.5) & (((x + 40.0) % 3.0) < 1.5)
    for m in (z_ew, z_ns):
        mm_ = m & (wear > 0.36)
        col[mm_] = col[mm_] * 0.25 + wht * 0.75
    # lineas centrales que mueren antes del cruce
    d1 = top & (np.abs(y) < 0.4) & (np.abs(x) > 26.0) & (((np.abs(x) + 30.0) % 9.0) < 5.0) & (wear > 0.38)
    d2 = top & (np.abs(x) < 0.4) & (np.abs(y) > 26.0) & (((np.abs(y) + 30.0) % 9.0) < 5.0) & (wear > 0.38)
    for m in (d1, d2):
        col[m] = col[m] * 0.25 + yel * 0.75
    return col


def acera_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    top = nrm[:, 2] > 0.7
    # losas de 6 studs y grietas con musgo
    j = top & ((((x + 60.0) % 6.0) < 0.14) | (((y + 60.0) % 6.0) < 0.14))
    col[j] = col[j] * 0.50
    cr = top & zonas(x, y, 0.08, 4, 0.5) & grietas(x, y, 0.45, 4, 0.045)
    col[cr] = col[cr] * 0.45
    ms = top & ((cr | j) & (A.fbm(pos * 0.9 + 3.0, 2, 141) > 0.55))
    col[ms] = col[ms] * 0.45 + np.array([0.22, 0.34, 0.12], np.float32) * 0.55
    st = top & (_stain(pos, 0.5, 5) > 0.35)
    col[st] = col[st] * 0.80
    return col


def bordillo_x(P, msk, pos, nrm, col):
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    side = np.abs(nrm[:, 2]) < 0.5
    # franjas de pintura roja/blanca desgastada
    stripe = side & (((x + 60.0) % 6.0) < 3.0) & (A.fbm(pos * 1.4, 2, 143) > 0.45)
    col[stripe] = col[stripe] * 0.4 + np.array([0.62, 0.20, 0.17], np.float32) * 0.6
    return col


STYLES = {
    'asfalto': dict(base='#3c3d40', var=0.10, stroke=(3, 3, 1), stroke_scale=4.0, blotch=0.12, ao=0.55, ao_tint='#101114', light=0.20,
                    grime=0.30, grime_col='#1a1a1c', dust=0.22, dust_col='#7d7a70', edge_col='#6e6d6a', edge=0.5, edge_th=0.05, seed=3),
    'acera': dict(base='#85837a', var=0.09, stroke=(2, 2, 1), stroke_scale=3.5, blotch=0.10, ao=0.55, ao_tint='#1a1a1c', light=0.22,
                  grime=0.30, grime_col='#3a362e', dust=0.20, dust_col='#a29d8c', edge_col='#b3afa0', edge=0.7, edge_th=0.05, seed=5),
    'bordillo': dict(base='#9a978c', var=0.08, stroke=(2, 1, 2), stroke_scale=3.0, blotch=0.10, ao=0.55, ao_tint='#1a1a1c', light=0.22,
                     grime=0.35, grime_col='#3a362e', edge_col='#c3bfb1', edge=0.8, edge_th=0.05, seed=7),
    'tierra': dict(base='#5a4633', var=0.14, stroke=(1, 1, 1), stroke_scale=3.0, blotch=0.15, ao=0.6, ao_tint='#140e08', light=0.22,
                   grime=0.25, grime_col='#2a1d12', dust=0.20, dust_col='#8a6d4c', seed=9),
    'hierro': dict(base='#6d4a36', var=0.12, stroke=(1, 4, 1), stroke_scale=6.0, blotch=0.12, ao=0.6, ao_tint='#140d08', light=0.24,
                   rust=0.45, grime=0.25, edge_col='#a07250', edge=0.6, seed=11),
    'tapa': dict(base='#47474a', var=0.08, stroke=(1, 1, 1), stroke_scale=5.0, ao=0.55, edge_col='#8a8a8c', edge=0.7, rust=0.2, seed=13),
}
EXTRAS = {'asfalto': lineas_calle, 'acera': acera_x, 'bordillo': bordillo_x}
