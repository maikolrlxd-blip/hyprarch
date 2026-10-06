#!/usr/bin/env python3
"""Genera los fondos de pantalla de hyprarch (estilo cyberpunk / synthwave).

Sol con rayas, suelo de rejilla en perspectiva, estrellas, montañas de alambre,
resplandor (bloom), líneas de escaneo y viñeta. Todo procedural (numpy + Pillow).

Uso:  python tools/make_wallpaper.py [carpeta_de_salida]
Salida: hyprarch-verde.jpg y hyprarch-rojo.jpg (2560x1440)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2560, 1440


def rgb(hexstr):
    h = hexstr.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def blur(arr, radius):
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0


def render(accent, accent2, sky_top, sky_horizon, seed):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    A, B = rgb(accent), rgb(accent2)
    TOP, HOR = rgb(sky_top), rgb(sky_horizon)
    horizon = H * 0.58
    cx = W / 2.0

    # ---- cielo y suelo
    s = np.clip(yy / horizon, 0, 1)[..., None] ** 1.7
    sky = TOP * (1 - s) + HOR * s
    gnd_t = np.clip((yy - horizon) / (H - horizon), 0, 1)[..., None]
    ground = HOR * 0.22 * (1 - gnd_t) + TOP * 0.55 * gnd_t
    img = np.where((yy >= horizon)[..., None], ground, sky).astype(np.float32)

    # ---- estrellas
    stars = np.zeros((H, W), np.float32)
    for _ in range(520):
        x = rng.integers(0, W)
        y = int(rng.random() ** 1.6 * horizon * 0.86)
        br = rng.random() * 0.8 + 0.2
        stars[y:y + 2, x:x + 2] = max(br, stars[y, x])
    img += stars[..., None] * np.array([0.8, 1.0, 0.9], np.float32) * 0.75

    # ---- sol con rayas
    R = H * 0.21
    sy = horizon - R * 0.30
    dist = np.sqrt((xx - cx) ** 2 + (yy - sy) ** 2)
    tcol = np.clip((yy - (sy - R)) / (2 * R), 0, 1)[..., None]
    # verde brillante arriba -> verde más oscuro abajo (mezclar verde y rojo daría amarillo)
    sun_col = A * (1 - 0.55 * tcol)
    rim = np.exp(-(((dist - R) / (R * 0.05)) ** 2))[..., None] * B * 0.9 * (yy < horizon)[..., None]   # aro carmesí
    alpha = np.clip((R - dist) / 2.0, 0, 1)
    # rayas: empiezan a media altura del sol y se engrosan hacia el horizonte
    u = (yy - (sy - R * 0.55)) / (R * 0.85)
    bars = np.abs(((u * 6.0) % 1.0) - 0.5) * 2.0
    thick = np.clip(u, 0, 1) ** 1.25 * 0.85
    slat = smoothstep(thick - 0.04, thick + 0.04, bars)
    alpha = alpha * np.where(u > 0, slat, 1.0) * (yy < horizon + 2)
    glow_sun = np.exp(-dist / (R * 0.8))[..., None] * (A * 0.35 + B * 0.18) * 0.5
    img += glow_sun * (yy < horizon + 40)[..., None]
    img = img * (1 - alpha[..., None]) + sun_col * alpha[..., None]
    img += rim * (yy < horizon)[..., None] * 0.9

    # ---- montañas de alambre (capa PIL)
    mtn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(mtn)
    ac8 = tuple(int(c * 255) for c in A)
    for side in (-1, 1):
        pts = [(cx + side * W * 0.0, horizon)]
        n = 26
        for i in range(n + 1):
            f = i / n
            x = cx + side * (f * W * 0.58)
            h = (np.sin(f * 7.0 + seed) * 0.5 + 0.5) * 0.55 + rng.random() * 0.35
            h *= (0.22 + 0.9 * np.sin(min(f * 1.15, 1) * np.pi / 2)) * H * 0.2
            pts.append((x, horizon - h))
        pts.append((cx + side * (W * 0.58), horizon))
        d.polygon(pts, fill=(2, 4, 3, 255))
        d.line(pts[1:-1], fill=ac8 + (210,), width=2)
    mtn_a = np.asarray(mtn, dtype=np.float32) / 255.0
    img = img * (1 - mtn_a[..., 3:4]) + mtn_a[..., :3] * mtn_a[..., 3:4]

    # ---- suelo: rejilla en perspectiva
    dy = np.maximum(yy - horizon, 1.0)
    below = (yy > horizon).astype(np.float32)
    KX, KZ = 2.4, 760.0
    xs = (xx - cx) / dy * KX
    zs = KZ / dy
    dpx_x = np.abs(((xs + 0.5) % 1.0) - 0.5) * dy / KX
    dpx_z = np.abs(((zs + 0.5) % 1.0) - 0.5) * dy * dy / KZ
    line = np.maximum(
        np.clip(1.0 - dpx_x / 1.6, 0, 1),
        np.clip(1.0 - dpx_z / 2.0, 0, 1),
    )
    fade = np.clip((yy - horizon) / (H * 0.07), 0, 1) ** 0.8
    grid = (line * fade * below)[..., None] * (A * 0.95 + 0.05) * 0.86

    # ---- horizonte: línea fina carmesí + resplandor suave + reflejo del sol
    hline = np.exp(-(((yy - horizon) / 2.2) ** 2))[..., None] * (B * 1.0 + 0.1)
    hz = np.exp(-(((yy - horizon) / (H * 0.014)) ** 2))[..., None] * (A * 0.5 + B * 0.2) * 0.42
    refl = (np.exp(-(((xx - cx) / (W * 0.05)) ** 2)) * np.exp(-(yy - horizon) / (H * 0.10)) * below)[..., None] * A * 0.22

    bright = np.clip(grid * 1.1 + hline * 0.9 + (alpha[..., None] * sun_col) * 0.5 + rim * 0.5, 0, 1)
    bloom = blur(bright, 8) * 0.38 + blur(bright, 30) * 0.42 + blur(bright, 80) * 0.30
    img = img + grid + hline + hz + refl + bloom

    # ---- zonas tranquilas: franja oscura arriba (detrás de la barra) y rincón inferior derecho (detrás de Hyro)
    top = 1 - 0.55 * (1 - smoothstep(0.0, H * 0.075, yy))[..., None]
    corner = 1 - 0.42 * np.exp(-(((xx - W * 0.97) / (W * 0.13)) ** 2 + ((yy - H * 0.97) / (H * 0.17)) ** 2))[..., None]
    img *= top * corner

    # ---- líneas de escaneo, viñeta y grano
    img *= (1 - 0.055 * ((yy.astype(np.int32) % 3) == 0))[..., None]
    r = np.sqrt(((xx - cx) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1 - 0.42 * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None]
    img += rng.normal(0, 0.008, img.shape).astype(np.float32)

    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def render_cine(seed=5):
    """Modo cine: sala oscura con un haz de proyector ámbar, pantalla tenue, polvo en la luz y bandas de cine."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx = W / 2.0
    warm = np.array([1.0, 0.70, 0.36], np.float32)

    # sala: degradado casi negro, algo más cálido abajo
    t = (yy / H)[..., None]
    img = (np.array([0.020, 0.014, 0.010], np.float32) * (1 - t) + np.array([0.040, 0.028, 0.018], np.float32) * t)

    # haz del proyector: nace arriba al centro y se abre hacia la pantalla
    apex_y = -0.06 * H
    d = np.maximum(yy - apex_y, 1.0)
    half = W * (0.035 + 0.30 * (d / H))
    cone = np.exp(-(((xx - cx) / half) ** 2) * 1.6) * np.clip(1.0 - (d / (H * 1.25)), 0, 1) ** 1.3
    img += cone[..., None] * warm * 0.16

    # pantalla: rectángulo tenue donde llega la luz, con borde suave
    sx0, sx1, sy0, sy1 = W * 0.27, W * 0.73, H * 0.47, H * 0.80
    scr = smoothstep(sx0, sx0 + 18, xx) * (1 - smoothstep(sx1 - 18, sx1, xx)) * smoothstep(sy0, sy0 + 18, yy) * (1 - smoothstep(sy1 - 18, sy1, yy))
    glow = blur(np.repeat(scr[..., None], 3, axis=2) * warm, 60)
    img += scr[..., None] * warm * 0.11 + glow * 0.30

    # polvo flotando en el haz
    dust = np.zeros((H, W), np.float32)
    for _ in range(420):
        y = int(rng.random() ** 0.8 * H * 0.78)
        x = int(np.clip(rng.normal(cx, W * (0.03 + 0.20 * (y / H))), 0, W - 2))
        dust[y:y + 2, x:x + 2] = max(dust[y, x], rng.random() * 0.8 + 0.2)
    dust = blur(np.repeat(dust[..., None], 3, axis=2), 1.2)[..., 0]
    img += (dust * cone)[..., None] * warm * 1.1

    # zonas tranquilas: franja superior (barra) y rincón inferior derecho (Hyro)
    top = 1 - 0.55 * (1 - smoothstep(0.0, H * 0.075, yy))[..., None]
    corner = 1 - 0.42 * np.exp(-(((xx - W * 0.97) / (W * 0.13)) ** 2 + ((yy - H * 0.97) / (H * 0.17)) ** 2))[..., None]
    img *= top * corner

    # bandas de cine (letterbox), viñeta y grano
    bars = smoothstep(H * 0.075, H * 0.085, yy) * (1 - smoothstep(H * 0.915, H * 0.925, yy))
    img *= bars[..., None]
    r = np.sqrt(((xx - cx) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1 - 0.50 * np.clip(r - 0.30, 0, 1) ** 1.4)[..., None]
    img += rng.normal(0, 0.010, img.shape).astype(np.float32)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def render_fresco(seed=9):
    """Fondo fresco y limpio: cielo azul profundo con cintas de aurora suaves (menta y cielo), pocas estrellas y un
    horizonte apenas insinuado. Todo desenfocado y aireado; sin rejilla ni elementos recargados."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    top, bot = np.array([0.020, 0.035, 0.075], np.float32), np.array([0.030, 0.062, 0.110], np.float32)
    t = (yy / H)[..., None]
    img = top * (1 - t) + bot * t
    cols = (np.array([0.30, 0.95, 0.78], np.float32), np.array([0.46, 0.66, 1.0], np.float32), np.array([0.62, 0.50, 1.0], np.float32))
    ribbons = np.zeros((H, W, 3), np.float32)
    for k, c in enumerate(cols):
        yc = H * (0.26 + 0.11 * k) + np.sin(xx / W * (2.6 + k * 0.7) * np.pi + k * 1.7) * H * (0.07 - 0.01 * k) \
            + np.sin(xx / W * 7.0 + k) * H * 0.012
        thick = H * (0.045 + 0.012 * k)
        band = np.exp(-(((yy - yc) / thick) ** 2))
        shimmer = 0.45 + 0.55 * np.sin(xx / W * (5.0 + k) * np.pi + k * 2.1) ** 2
        fine = 0.75 + 0.25 * np.sin(xx / W * 90 + yy / H * 14 + k)              # rayitas verticales finas (cortina de luz)
        ribbons += (band * shimmer * fine)[..., None] * c * (0.62 - 0.08 * k)
        edge = np.exp(-(((yy - (yc + thick * 0.55)) / (thick * 0.18)) ** 2))   # borde inferior más brillante, como una cortina real
        ribbons += (edge * shimmer)[..., None] * c * 0.30
    ribbons = blur(np.clip(ribbons, 0, 1), 9) * 0.85 + blur(np.clip(ribbons, 0, 1), 34) * 0.75 + blur(np.clip(ribbons, 0, 1), 100) * 0.55
    img = img + ribbons * 0.60
    # estrellas sueltas
    stars = np.zeros((H, W), np.float32)
    for _ in range(170):
        x, y = rng.integers(0, W), int(rng.random() ** 1.4 * H * 0.7)
        stars[y:y + 2, x:x + 2] = rng.random() * 0.7 + 0.25
    img += stars[..., None] * np.array([0.85, 0.95, 1.0], np.float32) * 0.55
    # niebla suave en el horizonte
    hz = np.exp(-(((yy - H * 0.80) / (H * 0.14)) ** 2))[..., None]
    img += hz * np.array([0.05, 0.10, 0.16], np.float32) * 0.9
    # zonas tranquilas (barra y rincón del personaje) y viñeta
    topz = 1 - 0.40 * (1 - smoothstep(0.0, H * 0.08, yy))[..., None]
    corner = 1 - 0.35 * np.exp(-(((xx - W * 0.97) / (W * 0.13)) ** 2 + ((yy - H * 0.97) / (H * 0.17)) ** 2))[..., None]
    img *= topz * corner
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1 - 0.30 * np.clip(r - 0.4, 0, 1) ** 1.5)[..., None]
    img += rng.normal(0, 0.006, img.shape).astype(np.float32)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


THEMES = {
    "fresco": None,        # composición propia: render_fresco()
    "verde": dict(accent="#39ff14", accent2="#ff1f4b", sky_top="#020403", sky_horizon="#0a2a14", seed=7),
    "rojo": dict(accent="#ff1f4b", accent2="#39ff14", sky_top="#040203", sky_horizon="#2a0a12", seed=11),
    "gamer": dict(accent="#00e5ff", accent2="#b026ff", sky_top="#04010c", sky_horizon="#1a0838", seed=21),
    "estudio": dict(accent="#4fd1c5", accent2="#7aa2ff", sky_top="#02080a", sky_horizon="#0a2a2e", seed=31),
    "trabajo": dict(accent="#5ec2ff", accent2="#8b9cff", sky_top="#03060a", sky_horizon="#0a1830", seed=41),
    "cine": None,          # composición propia: render_cine()
}

if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    only = set(sys.argv[2:])               # opcional: nombres de temas a generar (por defecto, todos)
    out.mkdir(parents=True, exist_ok=True)
    for name, params in THEMES.items():
        if only and name not in only:
            continue
        path = out / f"hyprarch-{name}.jpg"
        img = render_cine() if name == "cine" else (render_fresco() if name == "fresco" else render(**params))
        img.save(path, quality=90, optimize=True, subsampling=0)
        print(f"{path}  {path.stat().st_size / 1024:.0f} KB")
