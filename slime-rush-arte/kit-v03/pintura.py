"""Texturas 'pintadas a mano' generadas por codigo: degradado + pinceladas con direccion + variacion de color + borde oscurecido.
Evita el aspecto de plastilina (un solo color liso). Requiere numpy y Pillow."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def _lowfreq(size, cells, rng):
    g = (rng.random((cells, cells)) * 255).astype("uint8")
    return np.asarray(Image.fromarray(g).resize((size, size), Image.BICUBIC), dtype=np.float32) / 255.0


def pintar(ruta, colores, semilla=1, size=512, trazos=1400, angulo=90.0, largo=(24, 70), ancho=(3, 9),
           variacion=0.10, bandas=None, motas=None, borde=0.22, lineas=None):
    """colores: lista de hex de arriba a abajo (degradado vertical). angulo: direccion de las pinceladas en grados.
    bandas: [(y0,y1,'#hex')] franjas horizontales (0..1). motas: ('#hex', cantidad, radio). lineas: ('#hex', cada_n_px, grosor, vertical?)."""
    rng = np.random.default_rng(semilla)
    cols = [_hex(c) for c in colores]
    t = np.linspace(0, 1, size, dtype=np.float32)[:, None]
    seg = t * (len(cols) - 1)
    i0 = np.clip(seg.astype(int), 0, len(cols) - 2)
    f = seg - i0
    base = np.zeros((size, size, 3), dtype=np.float32)
    for k in range(len(cols) - 1):
        m = (i0 == k)
        blend = cols[k][None, None, :] * (1 - f)[..., None] + cols[k + 1][None, None, :] * f[..., None]
        base += np.where(m[..., None], np.broadcast_to(blend, (size, size, 3)), 0)
    # variacion de color de baja frecuencia (manchas amplias, como pintura)
    n1, n2 = _lowfreq(size, 6, rng), _lowfreq(size, 16, rng)
    base *= (1.0 + (n1 - 0.5) * variacion * 2.2 + (n2 - 0.5) * variacion)[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype("uint8"), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    if bandas:
        for y0, y1, c in bandas:
            col = tuple(int(v) for v in _hex(c)) + (255,)
            d.rectangle((0, int(y0 * size), size, int(y1 * size)), fill=col)
    # pinceladas con direccion y variacion de tono
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    for _ in range(trazos):
        x, y = rng.integers(0, size), rng.integers(0, size)
        a = math.radians(angulo + rng.normal(0, 16))
        L = rng.uniform(*largo)
        w = int(rng.uniform(*ancho))
        x2, y2 = x + math.cos(a) * L, y + math.sin(a) * L
        c0 = arr[int(y) % size, int(x) % size]
        k = 1.0 + rng.normal(0, variacion * 1.2)
        col = tuple(int(np.clip(v * k, 0, 255)) for v in c0) + (int(rng.uniform(70, 150)),)
        d.line((x, y, x2, y2), fill=col, width=max(1, w))
    if lineas:
        c, cada, g, vert = lineas
        col = tuple(int(v) for v in _hex(c)) + (255,)
        for p in range(0, size, cada):
            if vert:
                d.rectangle((p, 0, p + g, size), fill=col)
            else:
                d.rectangle((0, p, size, p + g), fill=col)
    if motas:
        c, n, r = motas
        col = tuple(int(v) for v in _hex(c)) + (255,)
        for _ in range(n):
            x, y = rng.integers(0, size), rng.integers(0, size)
            d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    img = img.convert("RGB").filter(ImageFilter.GaussianBlur(0.7))
    out = np.asarray(img, dtype=np.float32)
    if borde:  # oscurece apenas los bordes de la imagen (da volumen a las islas UV)
        yy, xx = np.mgrid[0:size, 0:size]
        e = np.minimum(np.minimum(xx, size - 1 - xx), np.minimum(yy, size - 1 - yy)) / (size * 0.12)
        out *= (1 - borde * np.clip(1 - e, 0, 1))[..., None]
    Image.fromarray(np.clip(out, 0, 255).astype("uint8")).save(ruta)
    return ruta
