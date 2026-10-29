# Escritor de GIF animado sin dependencias externas (solo numpy): paleta global por k-medias y compresion LZW de giflib.
# frames: lista de arrays (alto, ancho, 3) uint8 o float 0..1; retardo en centesimas de segundo; bucle infinito.
import struct
import numpy as np


def _paleta(frames, n=256, muestras=60000, iters=12, semilla=3):
    rng = np.random.default_rng(semilla)
    px = np.concatenate([f.reshape(-1, 3) for f in frames]).astype(np.float32)
    px = px[rng.choice(len(px), min(muestras, len(px)), replace=False)]
    c = px[rng.choice(len(px), n, replace=False)].copy()
    for _ in range(iters):
        d = (px ** 2).sum(1)[:, None] - 2 * px @ c.T + (c ** 2).sum(1)[None, :]
        a = d.argmin(1)
        for k in range(n):
            m = a == k
            if m.any():
                c[k] = px[m].mean(0)
    return np.clip(np.rint(c), 0, 255).astype(np.uint8)


def _indices(frame, pal):
    px = frame.reshape(-1, 3).astype(np.float32)
    pf = pal.astype(np.float32)
    pn = (pf ** 2).sum(1)[None, :]
    out = np.empty(len(px), np.uint8)
    for i in range(0, len(px), 16384):
        blk = px[i:i + 16384]
        d = (blk ** 2).sum(1)[:, None] - 2 * blk @ pf.T + pn
        out[i:i + 16384] = d.argmin(1)
    return out


def _lzw(ind):
    """LZW de GIF (profundidad de codigo minima 8), con la misma logica que giflib."""
    CLEAR, EOI = 256, 257
    bits, running, maxcode1 = 9, 258, 512
    tabla = {}
    out = bytearray()
    estado = [0, 0]                                       # bitbuf, nbits

    def put(code):
        nonlocal bits, maxcode1
        estado[0] |= code << estado[1]
        estado[1] += bits
        while estado[1] >= 8:
            out.append(estado[0] & 0xFF)
            estado[0] >>= 8
            estado[1] -= 8
        if running >= maxcode1 and code <= 4095:
            bits += 1
            maxcode1 = 1 << bits

    put(CLEAR)
    datos = ind.tolist()
    cur = datos[0]
    for pix in datos[1:]:
        key = (cur << 8) | pix
        nxt = tabla.get(key)
        if nxt is not None:
            cur = nxt
            continue
        put(cur)
        cur = pix
        if running >= 4095:
            put(CLEAR)
            running, bits, maxcode1 = 258, 9, 512
            tabla.clear()
        else:
            tabla[key] = running
            running += 1
    put(cur)
    put(EOI)
    if estado[1] > 0:
        out.append(estado[0] & 0xFF)
    return bytes(out)


def escribir_gif(path, frames, retardo_cs=4):
    fr = []
    for f in frames:
        f = np.asarray(f)
        if f.dtype != np.uint8:
            f = np.clip(np.rint(f * 255), 0, 255).astype(np.uint8)
        fr.append(f)
    h, w = fr[0].shape[:2]
    pal = _paleta(fr)
    with open(path, 'wb') as g:
        g.write(b'GIF89a' + struct.pack('<HHBBB', w, h, 0xF7, 0, 0) + pal.tobytes())
        g.write(b'\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00')
        for f in fr:
            g.write(b'\x21\xF9\x04\x04' + struct.pack('<H', retardo_cs) + b'\x00\x00')
            g.write(b'\x2C' + struct.pack('<HHHHB', 0, 0, w, h, 0) + b'\x08')
            datos = _lzw(_indices(f, pal))
            for i in range(0, len(datos), 255):
                blk = datos[i:i + 255]
                g.write(bytes([len(blk)]) + blk)
            g.write(b'\x00')
        g.write(b'\x3B')
    return path
