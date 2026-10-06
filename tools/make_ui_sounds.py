#!/usr/bin/env python3
"""Sonidos suaves de la interfaz, estilo menú de videojuego. Síntesis pura (sin muestras de terceros).

Diseño v2 (limpio): solo tonos de seno con ataque suave y caída natural, un parcial de marimba muy bajo,
filtro paso bajo y fundido final para que NUNCA haya chasquidos ni sonidos metálicos o "glitch".

  menu-open.wav            abre un menú (dos notas que suben)
  menu-hover.wav           toque muy suave (escribir en el buscador)
  menu-click.wav           pop redondo
  menu-move-0..5.wav       moverse entre opciones: nota que sube en la escala pentatónica menor (cada opción suena distinta)
  menu-select.wav          confirmar: dos notas cálidas
  menu-back.wav            cancelar / volver: dos notas que bajan

Uso:  python tools/make_ui_sounds.py [carpeta_de_salida]
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100


def smooth(x, n=5):
    """Paso bajo suave (promedio móvil): quita toda aspereza digital."""
    k = np.hanning(n * 2 + 1)
    k /= k.sum()
    return np.convolve(x, k, mode="same")


def finish(x, fade_ms=14.0):
    """Fundido de salida (coseno) para que el final llegue siempre exactamente a cero."""
    n = min(len(x), int(fade_ms / 1000 * SR))
    x = x.copy()
    x[-n:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, n)))
    return x


def write(path, mono, pan=0.0, peak=0.38):
    mono = finish(smooth(np.asarray(mono, np.float64)))
    mono = np.tanh(mono / (np.abs(mono).max() + 1e-9) * 1.0) * (peak / np.tanh(1.0))
    gl, gr = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    pcm = np.empty(len(mono) * 2, np.int16)
    pcm[0::2] = np.round(mono * gl * 32767)
    pcm[1::2] = np.round(mono * gr * 32767)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"{path}  {path.stat().st_size / 1024:.0f} KB")


def note(f, dur, decay, attack=0.010, mar=0.10):
    """Nota redonda: seno + un parcial de marimba (x4) muy bajo; ataque suave de 10 ms (sin clic)."""
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + mar * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * decay * 2.2)
    env = np.exp(-t * decay) * np.sin(0.5 * np.pi * np.minimum(1, t / attack)) ** 2
    return s * env


def mix_at(buf, sig, at, vol=1.0):
    i = int(at * SR)
    buf[i:i + len(sig)] += vol * sig[: len(buf) - i]


out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
out.mkdir(parents=True, exist_ok=True)

# abrir: dos notas que suben (La4 → Mi5), como una burbuja amable
a = np.zeros(int(0.34 * SR))
mix_at(a, note(440.00, 0.26, 11), 0.00)
mix_at(a, note(659.25, 0.26, 11), 0.08, 0.9)
write(out / "menu-open.wav", a, -0.1)

# pasar el mouse al escribir: toque casi imperceptible
write(out / "menu-hover.wav", note(880, 0.07, 46, attack=0.006, mar=0.0) * 0.55, 0.1, peak=0.22)

# clic: pop redondo, un tono grave que cae suavemente
t = np.arange(int(0.12 * SR)) / SR
pop = np.sin(2 * np.pi * np.cumsum(520 - 180 * t / 0.12) / SR) * np.exp(-t * 26) * np.sin(0.5 * np.pi * np.minimum(1, t / 0.008)) ** 2
write(out / "menu-click.wav", pop)

# moverse entre opciones: escala pentatónica menor de La (cada opción suena distinta)
penta = [440.00, 523.25, 587.33, 659.25, 783.99, 880.00]
for k, f in enumerate(penta):
    write(out / f"menu-move-{k}.wav", note(f, 0.16, 20, attack=0.009), pan=(k - 2.5) * 0.08, peak=0.30)

# confirmar: dos notas cálidas que suben (Re5 → La5)
s = np.zeros(int(0.62 * SR))
mix_at(s, note(587.33, 0.36, 8, attack=0.010), 0.00)
mix_at(s, note(880.00, 0.44, 7, attack=0.010), 0.09, 0.95)
write(out / "menu-select.wav", s, peak=0.40)

# volver / cancelar: dos notas que bajan, más suaves
b = np.zeros(int(0.46 * SR))
mix_at(b, note(523.25, 0.24, 13, attack=0.010), 0.00)
mix_at(b, note(392.00, 0.28, 12, attack=0.010), 0.08, 0.9)
write(out / "menu-back.wav", b, peak=0.34)
