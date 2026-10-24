#!/usr/bin/env python3
"""Sonidos de armas sintetizados por codigo (numpy/scipy): WAV mono 44.1 kHz 16 bit, sin muestras ajenas.
Uso: python3 sonidos.py   -> wav/*.wav, hoja.png (formas de onda + espectrogramas), manifiesto.json
Valores PROVISIONALES: hay que escucharlos y ajustarlos (la IA que los genero no puede oirlos)."""
import json, wave
from pathlib import Path
import numpy as np
from scipy import signal

SR = 44100
HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(7)

def t_(d): return np.arange(int(SR * d)) / SR
def noise(d): return rng.standard_normal(int(SR * d))
def bp(x, lo, hi, order=3): return signal.sosfilt(signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)
def lp(x, f, order=3): return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)
def hp(x, f, order=3): return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)
def env(d, attack=0.001, decay=0.1):
    t = t_(d); a = np.minimum(t / max(attack, 1e-5), 1.0); return a * np.exp(-t / decay)
def pad(x, d): out = np.zeros(int(SR * d)); out[:min(len(x), len(out))] = x[:len(out)]; return out
def at(base, x, start):  # mezcla x dentro de base desde 'start' s
    i = int(start * SR); n = min(len(x), len(base) - i)
    if n > 0: base[i:i + n] += x[:n]
    return base
def thump(d, f0, f1, decay):  # barrido grave
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t / (decay * 0.5)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / decay)
def click(d=0.02, f=3200, decay=0.004, level=1.0):  # clic mecanico: seno amortiguado + chasquido de ruido
    t = t_(d); return level * (np.sin(2 * np.pi * f * t) * np.exp(-t / decay) * 0.6 + bp(noise(d), 1500, 9000) * np.exp(-t / (decay * 0.7)) * 0.5)
def thud(d=0.12, f=110, decay=0.03): return thump(d, f * 1.6, f, decay)

def shot(d, thump_f, thump_decay, crack_decay, tail_decay, tail_lo, tail_hi, gain_crack, gain_thump, gain_tail):
    n = int(SR * d)
    crack = hp(noise(d), 1800) * env(d, 0.0004, crack_decay) * gain_crack
    body = thump(d, thump_f * 2.2, thump_f, thump_decay) * gain_thump
    tail = bp(noise(d), tail_lo, tail_hi) * env(d, 0.004, tail_decay) * gain_tail
    return crack + body + tail

def normalize(x, peak=0.9, fade=0.004):
    x = x - np.mean(x); m = np.max(np.abs(x)) or 1.0; x = x / m * peak
    f = int(SR * fade); x[-f:] *= np.linspace(1, 0, f); x[:8] *= np.linspace(0, 1, 8)  # sin clics al empezar/terminar
    return x

S = {}
S["pistola_disparo"] = shot(0.5, 130, 0.07, 0.012, 0.16, 300, 4500, 1.0, 1.1, 0.35)
S["escopeta_disparo"] = shot(1.0, 80, 0.16, 0.022, 0.42, 150, 3500, 1.0, 1.6, 0.55)
S["subfusil_disparo"] = shot(0.25, 150, 0.04, 0.009, 0.08, 400, 5500, 1.0, 0.8, 0.25)
S["clic_vacio"] = pad(click(0.03, 2600, 0.005), 0.12)

def seq(total, parts):
    x = np.zeros(int(SR * total))
    for start, s in parts: at(x, s, start)
    return x

S["pistola_equipar"] = seq(0.8, [(0.05, hp(noise(0.12), 500) * env(0.12, 0.003, 0.05) * 0.35), (0.35, click(0.03, 2000, 0.006) * 0.8), (0.55, click(0.03, 2800, 0.004) * 0.9)])
S["pistola_recarga"] = seq(1.7, [(0.30, click(0.04, 1800, 0.008) * 0.9), (0.38, thud(0.1, 140)), (0.85, thud(0.1, 120) * 0.8), (0.92, click(0.03, 2400, 0.005)), (1.30, click(0.04, 3000, 0.004)), (1.37, click(0.03, 1600, 0.006) * 0.8)])
S["subfusil_equipar"] = seq(0.9, [(0.05, hp(noise(0.15), 400) * env(0.15, 0.004, 0.07) * 0.4), (0.45, click(0.03, 1800, 0.006) * 0.8), (0.65, click(0.04, 2600, 0.005))])
S["subfusil_recarga"] = seq(1.95, [(0.35, click(0.04, 1500, 0.01) * 0.9), (0.42, thud(0.12, 130)), (1.05, thud(0.1, 115) * 0.9), (1.12, click(0.03, 2200, 0.005)), (1.55, click(0.05, 2800, 0.004)), (1.62, click(0.04, 1500, 0.007) * 0.9)])
S["escopeta_equipar"] = seq(1.0, [(0.05, hp(noise(0.2), 300) * env(0.2, 0.004, 0.08) * 0.45), (0.5, click(0.04, 1500, 0.008)), (0.62, thud(0.1, 100) * 0.8)])
S["escopeta_bombeo"] = seq(0.55, [(0.02, click(0.05, 1300, 0.01) * 0.9), (0.05, bp(noise(0.12), 400, 3000) * env(0.12, 0.002, 0.04) * 0.5), (0.28, click(0.05, 1700, 0.008)), (0.31, thud(0.1, 120) * 0.8)])
S["escopeta_cartucho"] = seq(0.2, [(0.0, click(0.03, 2200, 0.005) * 0.8), (0.03, thud(0.06, 220, 0.02) * 0.6)])
S["impacto_zombi"] = pad(thud(0.18, 90, 0.045) * 0.9 + bp(noise(0.18), 200, 1800) * env(0.18, 0.002, 0.05) * 0.35, 0.2)  # golpe sordo: sin sonido de carne
S["marcador_impacto"] = click(0.05, 1800, 0.012) * 0.9

wavs = HERE / "wav"; wavs.mkdir(exist_ok=True)
manifest = {}
for name, x in S.items():
    y = normalize(x)
    with wave.open(str(wavs / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype("<i2").tobytes())
    manifest[name] = {"duracion_s": round(len(y) / SR, 3), "pico": round(float(np.max(np.abs(y))), 3), "rms": round(float(np.sqrt(np.mean(y ** 2))), 4)}
(HERE / "manifiesto.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

# hoja de comprobacion visual: forma de onda + espectrograma
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
names = list(S); cols = 3; rows = -(-len(names) // cols)
fig, ax = plt.subplots(rows * 2, cols, figsize=(15, rows * 3.2))
for k, name in enumerate(names):
    r, c = (k // cols) * 2, k % cols
    y = normalize(S[name]); a, b = ax[r][c], ax[r + 1][c]
    a.plot(np.arange(len(y)) / SR, y, lw=0.4, color="#2a6"); a.set_title(name, fontsize=9); a.set_ylim(-1, 1); a.set_xticks([])
    b.specgram(y, NFFT=512, Fs=SR, noverlap=384, cmap="magma", vmin=-110); b.set_ylim(0, 12000)
for k in range(len(names), rows * cols): ax[(k // cols) * 2][k % cols].axis("off"); ax[(k // cols) * 2 + 1][k % cols].axis("off")
plt.tight_layout(); plt.savefig(HERE / "hoja.png", dpi=70)
print(json.dumps(manifest, indent=1, ensure_ascii=False))
