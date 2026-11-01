#!/usr/bin/env python3
"""Sonidos arcade de «+1 de lanzamiento por segundo», sintetizados por codigo (numpy/scipy): WAV mono 44,1 kHz 16 bit, sin muestras ajenas.
Uso: python3 sonidos.py -> wav/*.wav, manifiesto.json. PROVISIONALES: la IA que los genero NO puede oirlos; hay que escucharlos y ajustar."""
import json, wave
from pathlib import Path
import numpy as np
from scipy import signal

SR = 44100
HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(11)
def t_(d): return np.arange(int(SR * d)) / SR
def noise(d): return rng.standard_normal(int(SR * d))
def bp(x, lo, hi): return signal.sosfilt(signal.butter(3, [lo, hi], "bandpass", fs=SR, output="sos"), x)
def lp(x, f): return signal.sosfilt(signal.butter(3, f, "lowpass", fs=SR, output="sos"), x)
def env(d, a=0.003, dec=0.1): t = t_(d); return np.minimum(t / a, 1) * np.exp(-t / dec)
def tone(d, f, dec=0.15, a=0.003, wave_="sine"):
    t = t_(d); ph = 2 * np.pi * f * t
    s = np.sin(ph) if wave_ == "sine" else (signal.square(ph) * 0.5 if wave_ == "square" else np.sin(ph) + 0.3 * np.sin(2 * ph))
    return s * env(d, a, dec)
def sweep(d, f0, f1, dec=None, a=0.005):
    t = t_(d); f = f0 + (f1 - f0) * (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(d, a, dec or d / 2)
def at(base, x, start):
    i = int(start * SR); n = min(len(x), len(base) - i)
    if n > 0: base[i:i + n] += x[:n]
    return base
def seq(total, parts):
    x = np.zeros(int(SR * total))
    for s, y in parts: at(x, y, s)
    return x
def norm(x, peak=0.85):
    x = x - np.mean(x); x = x / (np.max(np.abs(x)) or 1) * peak
    f = int(SR * 0.005); x[-f:] *= np.linspace(1, 0, f); x[:8] *= np.linspace(0, 1, 8); return x

N = lambda f: 440 * 2 ** ((f - 69) / 12)  # nota MIDI -> Hz
S = {}
S["lanzamiento"] = seq(1.4, [(0, sweep(0.35, 120, 40, 0.1) * 1.4), (0, bp(noise(0.25), 400, 5000) * env(0.25, 0.002, 0.07) * 0.9),
                              (0.05, bp(noise(1.2), 300, 2500) * np.linspace(0.9, 0, int(SR * 1.2)) * 0.5), (0.1, sweep(1.0, 300, 1400, 0.5) * 0.35)])
S["boost"] = seq(0.6, [(0, bp(noise(0.5), 500, 4000) * env(0.5, 0.05, 0.2) * 0.7), (0, sweep(0.5, 200, 700, 0.25) * 0.4)])
S["aro"] = seq(0.55, [(0.00, tone(0.3, N(76), 0.12, wave_="tri")), (0.07, tone(0.3, N(83), 0.12, wave_="tri")), (0.14, tone(0.4, N(88), 0.2, wave_="tri"))])
S["orbe"] = seq(0.2, [(0, tone(0.12, N(88), 0.04, wave_="tri") * 0.8), (0.05, tone(0.15, N(95), 0.05, wave_="tri"))])
S["golpe"] = seq(0.25, [(0, sweep(0.14, 220, 70, 0.05) * 1.2), (0, bp(noise(0.1), 800, 6000) * env(0.1, 0.001, 0.03) * 0.8)])
S["cofre"] = seq(0.9, [(i * 0.09, tone(0.4, N(n), 0.18, wave_="tri") * 0.8) for i, n in enumerate([72, 76, 79, 84, 88])] + [(0.45, tone(0.45, N(91), 0.3) * 0.5)])
S["aterrizaje"] = seq(0.6, [(0, sweep(0.35, 130, 45, 0.12) * 1.3), (0, bp(noise(0.25), 150, 2500) * env(0.25, 0.003, 0.06) * 0.7)])
S["huevo_agita"] = seq(0.7, [(i * 0.1, bp(noise(0.06), 800, 3500) * env(0.06, 0.002, 0.02) * 0.8) for i in range(6)])
S["huevo_abre"] = seq(1.1, [(0, sweep(0.12, 180, 400, 0.06) * 1.2), (0.0, bp(noise(0.12), 1500, 9000) * env(0.12, 0.001, 0.03)),
                             (0.12, tone(0.6, N(84), 0.25, wave_="tri") * 0.7), (0.2, tone(0.6, N(88), 0.25, wave_="tri") * 0.7), (0.3, tone(0.8, N(91), 0.4, wave_="tri") * 0.7)])
S["mitico"] = seq(1.8, [(i * 0.12, tone(0.9, N(n), 0.35, wave_="tri") * 0.7) for i, n in enumerate([67, 72, 76, 79, 84, 88, 91])] + [(0.9, bp(noise(0.8), 3000, 9000) * env(0.8, 0.01, 0.3) * 0.25)])
S["rebirth"] = seq(2.2, [(0, sweep(1.4, 150, 1800, 0.9) * 0.8)] + [(1.3, tone(0.9, N(n), 0.5, wave_="tri") * 0.6) for n in (72, 76, 79)] + [(1.3, bp(noise(0.9), 2000, 8000) * env(0.9, 0.01, 0.35) * 0.25)])
S["clic"] = seq(0.1, [(0, tone(0.05, 1800, 0.012, 0.001, "square") * 0.6)])
S["error"] = seq(0.35, [(0, tone(0.15, 200, 0.06, 0.002, "square") * 0.7), (0.12, tone(0.2, 150, 0.08, 0.002, "square") * 0.7)])
S["combo"] = seq(0.25, [(0, tone(0.18, N(84), 0.06, wave_="tri")), (0.06, tone(0.18, N(91), 0.08, wave_="tri"))])

(HERE / "wav").mkdir(exist_ok=True)
man = {}
for k, x in S.items():
    y = norm(x)
    with wave.open(str(HERE / "wav" / f"{k}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype("<i2").tobytes())
    man[k] = {"archivo": f"wav/{k}.wav", "segundos": round(len(y) / SR, 2), "roblox_asset_id": None}
(HERE / "manifiesto.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
print(len(man), "sonidos")
