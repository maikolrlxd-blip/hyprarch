#!/usr/bin/env python3
"""Sonidos suaves de la interfaz (menú del personajito): menu-open, menu-hover, menu-click. Síntesis pura.

Uso:  python tools/make_ui_sounds.py [carpeta_de_salida]
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100


def write(path, mono, pan=0.0):
    mono = np.asarray(mono, np.float32)
    mono = mono / (np.abs(mono).max() + 1e-6) * 0.55
    gl, gr = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    pcm = np.empty(len(mono) * 2, np.int16)
    pcm[0::2] = mono * gl * 32767
    pcm[1::2] = mono * gr * 32767
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"{path}  {path.stat().st_size / 1024:.0f} KB")


def tone(f, dur, decay, attack=0.004, h2=0.3):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + h2 * np.sin(2 * np.pi * f * 2 * t)
    e = np.exp(-t * decay) * np.minimum(1, t / attack)
    return s * e


out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
out.mkdir(parents=True, exist_ok=True)

# abrir: dos notas que suben, como una burbuja ("bloop")
a = np.zeros(int(0.26 * SR))
for f, at in ((523.25, 0.0), (783.99, 0.07)):
    n = tone(f, 0.20, 16)
    i = int(at * SR)
    a[i:i + len(n)] += n[: len(a) - i]
write(out / "menu-open.wav", a, -0.1)

# pasar el mouse: un "tic" muy suave y corto
write(out / "menu-hover.wav", tone(1320, 0.05, 70, attack=0.002, h2=0.1) * 0.6, 0.1)

# clic: un "pop" agradable que baja un poco
t = np.arange(int(0.11 * SR)) / SR
pop = np.sin(2 * np.pi * np.cumsum(900 - 500 * t / 0.11) / SR) * np.exp(-t * 32) * np.minimum(1, t / 0.002)
write(out / "menu-click.wav", pop)
