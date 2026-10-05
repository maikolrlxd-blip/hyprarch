#!/usr/bin/env python3
"""Sonidos suaves de la interfaz, estilo menú de videojuego. Síntesis pura (sin muestras de terceros).

  menu-open.wav            abre un menú (dos notas que suben)
  menu-hover.wav           tic suave (escribir en el buscador)
  menu-click.wav           pop agradable
  menu-move-0..5.wav       moverse entre opciones: blip que sube en la escala pentatónica (cada opción suena distinta)
  menu-select.wav          confirmar: dos notas brillantes con destello
  menu-back.wav            cancelar / volver: dos notas que bajan

Uso:  python tools/make_ui_sounds.py [carpeta_de_salida]
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100


def write(path, mono, pan=0.0, peak=0.55):
    mono = np.asarray(mono, np.float32)
    mono = mono / (np.abs(mono).max() + 1e-6) * peak
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


def tone(f, dur, decay, attack=0.004, h2=0.3, h3=0.0):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + h2 * np.sin(2 * np.pi * f * 2 * t) + h3 * np.sin(2 * np.pi * f * 3 * t)
    return s * np.exp(-t * decay) * np.minimum(1, t / attack)


def mix_at(buf, sig, at):
    i = int(at * SR)
    buf[i:i + len(sig)] += sig[: len(buf) - i]


out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
out.mkdir(parents=True, exist_ok=True)

# abrir: dos notas que suben, como una burbuja
a = np.zeros(int(0.26 * SR))
mix_at(a, tone(523.25, 0.20, 16), 0.0)
mix_at(a, tone(783.99, 0.20, 16), 0.07)
write(out / "menu-open.wav", a, -0.1)

# pasar el mouse al escribir: tic muy suave
write(out / "menu-hover.wav", tone(1320, 0.05, 70, attack=0.002, h2=0.1) * 0.6, 0.1)

# clic: pop que baja un poco
t = np.arange(int(0.11 * SR)) / SR
pop = np.sin(2 * np.pi * np.cumsum(900 - 500 * t / 0.11) / SR) * np.exp(-t * 32) * np.minimum(1, t / 0.002)
write(out / "menu-click.wav", pop)

# moverse entre opciones: escala pentatónica (Do mayor) que sube; cada opción suena distinta, como en los menús de juego
penta = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]
for k, f in enumerate(penta):
    blip = tone(f, 0.11, 34, attack=0.002, h2=0.25, h3=0.08)
    over = 0.35 * tone(f * 2, 0.05, 60, attack=0.001, h2=0.0)
    blip[:len(over)] += over
    write(out / f"menu-move-{k}.wav", blip, pan=(k - 2.5) * 0.08, peak=0.45)

# confirmar: dos notas brillantes que suben + destello agudo
s = np.zeros(int(0.5 * SR))
mix_at(s, tone(783.99, 0.28, 11, attack=0.003, h2=0.35, h3=0.1), 0.0)
mix_at(s, tone(1174.66, 0.34, 9, attack=0.003, h2=0.35, h3=0.1), 0.075)
mix_at(s, 0.35 * tone(2349.3, 0.26, 14, attack=0.002, h2=0.0), 0.075)
write(out / "menu-select.wav", s, peak=0.6)

# volver / cancelar: dos notas que bajan, más suaves
b = np.zeros(int(0.36 * SR))
mix_at(b, tone(659.25, 0.18, 18, attack=0.003, h2=0.2), 0.0)
mix_at(b, tone(493.88, 0.22, 16, attack=0.003, h2=0.2), 0.07)
write(out / "menu-back.wav", b, peak=0.5)
