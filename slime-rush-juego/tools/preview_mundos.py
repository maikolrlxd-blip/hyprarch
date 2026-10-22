#!/usr/bin/env python3
"""Dibuja vistas cenitales de mundos generados (biomas, meta, apariciones, cofres, raros). Requiere lupa y Pillow.
Uso: python3 tools/preview_mundos.py 11 222 3333   ->  previews/mundos-semillas.png"""
import sys
from pathlib import Path
from lupa import LuaRuntime
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(f'package.path = "{root}/src/?.lua;" .. package.path')
World = L.eval('(require("World"))')
COL = {"mar": (24, 62, 120), "lago": (64, 140, 214), "pradera": (150, 205, 110), "bosque": (58, 128, 72), "desierto": (232, 206, 140),
       "roca": (150, 148, 140), "montana": (236, 238, 242)}
SC = 4
seeds = [int(a) for a in sys.argv[1:]] or [11, 222, 3333]
tiles = []
for seed in seeds:
    w = World.generate(seed)
    heights, biomes, n = World.grid(w)
    im = Image.new("RGB", (n * SC, n * SC))
    px = im.load()
    for iz in range(1, n + 1):
        for ix in range(1, n + 1):
            c = COL[biomes[iz][ix]]
            h = heights[iz][ix]
            k = 0.82 + 0.18 * max(0.0, min(1.0, (h + 10) / 90))  # relieve: mas alto = mas claro
            col = tuple(int(v * k) for v in c)
            for dy in range(SC):
                for dx in range(SC):
                    px[(ix - 1) * SC + dx, (iz - 1) * SC + dy] = col
    d = ImageDraw.Draw(im)
    s = SC / w.cfg.cell
    for i in range(1, len(w.nodes) + 1):
        nd = w.nodes[i]; d.point((nd.x * s, nd.z * s), fill=(255, 255, 255))
    ch = {"comun": ((240, 200, 60), 3), "musgoso": ((190, 230, 60), 3), "dorado": ((255, 170, 0), 6), "oculto": ((170, 70, 220), 4)}
    for i in range(1, len(w.chests) + 1):
        c = w.chests[i]; col, r = ch[c.kind]; x, z = c.x * s, c.z * s
        d.rectangle((x - r, z - r, x + r, z + r), fill=col, outline=(20, 20, 20))
    for i in range(1, len(w.rares) + 1):
        r_ = w.rares[i]
        if r_.active:
            x, z = r_.x * s, r_.z * s
            d.polygon([(x, z - 9), (x + 3, z - 3), (x + 9, z - 3), (x + 4, z + 2), (x + 6, z + 9), (x, z + 5), (x - 6, z + 9), (x - 4, z + 2), (x - 9, z - 3), (x - 3, z - 3)], fill=(255, 60, 200), outline=(20, 20, 20))
    for i in range(1, len(w.spawns) + 1):
        sp = w.spawns[i]; x, z = sp.x * s, sp.z * s
        d.ellipse((x - 5, z - 5, x + 5, z + 5), fill=(255, 120, 0), outline=(20, 20, 20))
    for i in range(1, len(w.spawns) + 1):
        sp = w.spawns[i]
        d.line((sp.x * s, sp.z * s, sp.boat.x * s, sp.boat.z * s), fill=(120, 200, 255), width=1)
        bx, bz = sp.boat.x * s, sp.boat.z * s
        d.polygon([(bx, bz - 4), (bx + 4, bz + 3), (bx - 4, bz + 3)], fill=(255, 255, 255), outline=(20, 20, 20))
    if w.volcano:
        v = w.volcano; vx, vz, vr = v.x * s, v.z * s, v.max_lava * s
        d.ellipse((vx - vr, vz - vr, vx + vr, vz + vr), outline=(255, 90, 40), width=2)
        d.polygon([(vx, vz - 10), (vx + 9, vz + 7), (vx - 9, vz + 7)], fill=(220, 40, 20), outline=(20, 20, 20))
    g = w.goal; gx, gz, gr = g.x * s, g.z * s, g.radius * s
    d.ellipse((gx - gr, gz - gr, gx + gr, gz + gr), outline=(255, 255, 255), width=3)
    d.ellipse((gx - 6, gz - 6, gx + 6, gz + 6), fill=(255, 255, 255), outline=(20, 20, 20))
    d.text((8, 6), f"semilla {seed}", fill=(0, 0, 0))
    tiles.append(im)
W_, pad = tiles[0].width, 12
leg_h = 56
out = Image.new("RGB", (W_ * len(tiles) + pad * (len(tiles) + 1), W_ + leg_h + pad * 2), (22, 26, 32))
for i, t in enumerate(tiles):
    out.paste(t, (pad + i * (W_ + pad), pad))
d = ImageDraw.Draw(out)
x = pad; y = W_ + pad * 2
for name, c in COL.items():
    d.rectangle((x, y, x + 14, y + 14), fill=c); d.text((x + 20, y), name, fill=(230, 235, 240)); x += 85
d.ellipse((x, y, x + 12, y + 12), outline=(255, 255, 255), width=2); d.text((x + 18, y), "meta", fill=(230, 235, 240)); x += 70
d.ellipse((x, y, x + 12, y + 12), fill=(255, 120, 0)); d.text((x + 18, y), "aparicion", fill=(230, 235, 240)); x += 90
d.polygon([(x + 6, y), (x + 13, y + 12), (x - 1, y + 12)], fill=(255, 255, 255), outline=(20, 20, 20)); d.text((x + 18, y), "bote", fill=(230, 235, 240)); x += 60
d.polygon([(x + 6, y), (x + 13, y + 12), (x - 1, y + 12)], fill=(220, 40, 20)); d.text((x + 18, y), "volcan (aro = alcance max. de la lava)", fill=(230, 235, 240)); x += 250
for nm, c in (("cofre", (240, 200, 60)), ("dorado", (255, 170, 0)), ("oculto", (170, 70, 220)), ("slime raro", (255, 60, 200))):
    d.rectangle((x, y, x + 12, y + 12), fill=c); d.text((x + 18, y), nm, fill=(230, 235, 240)); x += 20 + 8 * len(nm) + 14
d.text((pad, y + 24), "Puntos blancos = recursos. 1536 x 1536 studs, 24 jugadores. Mismo codigo, solo cambia la semilla.", fill=(150, 160, 175))
out.save(root / "previews" / "mundos-semillas.png")
print("listo:", root / "previews" / "mundos-semillas.png", out.size)
