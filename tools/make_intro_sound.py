#!/usr/bin/env python3
"""Compone el sonido de la animación de entrada (síntesis pura, sin muestras de terceros).

Diseño v2 (limpio y musical): SOLO tonos de seno y notas de marimba suaves, en La menor pentatónica, con ataques y
finales suavizados. Sin ruido, sin "glitch", sin chasquidos, sin barridos agudos. La reverberación es una cola
oscura y corta (no hay siseo).

Está sincronizado con hyprarch-intro (los tiempos son los mismos):
  0.05 línea de horizonte  ·  0.55 zumbido grave de la rejilla  ·  0.9-2.5 sale el sol
  1.2-1.9 el robotito se materializa (arpegio)  ·  1.9-2.9 título (una nota por letra)  ·  3.0-4.0 subtítulo (toquecitos)
  3.1 destello suave  ·  3.9-5.3 entra Claudito (arco)  ·  5.3 campanita  ·  5.6 golpe grave final  ·  6.4 fin

Uso:  python tools/make_intro_sound.py [salida.wav]
Requiere numpy. Genera un WAV estéreo de 44,1 kHz (~1,2 MB).
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 6.8
N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N, np.float32)
R = np.zeros(N, np.float32)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def soft_edges(sig, attack=0.012, release=0.030):
    """Entrada y salida con curva de coseno: ninguna nota empieza ni termina con un salto."""
    sig = np.asarray(sig, np.float32).copy()
    a, r = min(len(sig) // 2, max(1, int(attack * SR))), min(len(sig) // 2, max(1, int(release * SR)))
    sig[:a] *= 0.5 * (1 - np.cos(np.linspace(0, np.pi, a)))
    sig[-r:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, r)))
    return sig


def add(sig, start, vol=1.0, pan=0.0):
    """Suma `sig` en el instante `start` (s) con volumen y paneo (-1 izquierda … 1 derecha)."""
    i = int(start * SR)
    if i >= N:
        return
    sig = soft_edges(sig[: N - i])
    gl = vol * np.sqrt((1 - pan) / 2)
    gr = vol * np.sqrt((1 + pan) / 2)
    L[i:i + len(sig)] += sig * gl
    R[i:i + len(sig)] += sig * gr


def marimba(freq, dur, decay=7.0, mar=0.12):
    """Nota redonda: seno + parcial de marimba (x4) muy bajo y caída natural."""
    t = tt(dur)
    s = np.sin(2 * np.pi * freq * t) + mar * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * decay * 2.2)
    return s * np.exp(-t * decay)


def glide(f0, f1, dur):
    """Seno que sube o baja de tono de forma suave."""
    t = tt(dur)
    f = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(np.pi * t / dur))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


# ---------------------------------------------------------------- 0.05 línea de horizonte: deslizamiento suave hacia arriba
z = glide(180, 440, 0.9) * np.sin(np.pi * np.linspace(0, 1, int(0.9 * SR))) ** 2
add(z, 0.05, 0.16, -0.3)
add(z * 0.5, 0.05, 0.08, 0.3)

# ---------------------------------------------------------------- 0.55-4.2 zumbido grave de la rejilla (crece y se queda)
t = tt(3.9)
hum = np.sin(2 * np.pi * 55 * t) + 0.45 * np.sin(2 * np.pi * 110 * t) + 0.20 * np.sin(2 * np.pi * 165 * t)
hum *= np.minimum(1, t / 1.6) ** 2 * np.minimum(1, (3.9 - t) / 0.9)
add(hum, 0.55, 0.26)

# ---------------------------------------------------------------- 0.9-2.5 sale el sol: acorde de La menor que sube y se abre
t = tt(1.9)
rise = np.zeros_like(t)
for f0, amp in ((110, 1.0), (165, 0.8), (220, 0.7), (330, 0.5)):
    ramp = f0 * (1 + 0.5 * (t / 1.9) ** 2)
    rise += amp * np.sin(2 * np.pi * np.cumsum(ramp) / SR) * (0.8 + 0.2 * np.sin(2 * np.pi * 3.5 * t))
rise *= (t / 1.9) ** 1.4 * np.minimum(1, (1.9 - t) / 0.30)
add(rise / 3, 0.9, 0.30, -0.15)

# ---------------------------------------------------------------- 1.2-1.9 el robotito se materializa: arpegio ascendente
for i, f in enumerate((392.00, 523.25, 659.25, 783.99)):
    add(marimba(f, 0.6, 5.5), 1.2 + i * 0.17, 0.13, -0.2 + 0.13 * i)

# ---------------------------------------------------------------- 1.9-2.9 título: una nota por letra (pentatónica)
for i, f in enumerate((392.0, 440.0, 523.25, 587.33, 659.25, 783.99, 880.0, 1046.5)):
    add(marimba(f, 0.30, 9.0), 1.9 + i * (1.0 / 9.0), 0.17, np.sin(i) * 0.40)

# ---------------------------------------------------------------- 3.0-4.0 subtítulo: toquecitos suaves (marimba aguda, muy bajos)
for i in range(17):
    add(marimba((784.0, 880.0, 987.77)[i % 3], 0.10, 30.0, 0.0), 3.0 + i * (1.0 / 18.0), 0.045, np.sin(i * 1.7) * 0.4)

# ---------------------------------------------------------------- 3.1-3.9 destello suave: dos campanitas agudas que se apagan despacio
for f, at, pan in ((1567.98, 3.10, -0.2), (2093.00, 3.22, 0.2)):
    add(marimba(f, 0.9, 3.4, 0.0), at, 0.045, pan)

# ---------------------------------------------------------------- 4.0 saludo del robotito: dos notas amables
add(marimba(784.0, 0.5, 6.0), 4.0, 0.12, -0.1)
add(marimba(1046.5, 0.7, 5.0), 4.12, 0.12, 0.1)

# ---------------------------------------------------------------- 3.9-5.3 entra Claudito: arco suave de tono que sube y baja (viaja de derecha a centro)
arc = np.concatenate([glide(220, 660, 0.7), glide(660, 440, 0.7)])
n = len(arc)
arc = arc * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
pan = np.linspace(0.9, 0.0, n)
i0 = int(3.9 * SR)
arc = soft_edges(arc)
L[i0:i0 + n] += (arc * 0.10 * np.sqrt((1 - pan) / 2)).astype(np.float32)[: N - i0]
R[i0:i0 + n] += (arc * 0.10 * np.sqrt((1 + pan) / 2)).astype(np.float32)[: N - i0]

# ---------------------------------------------------------------- 5.3 campanita de llegada (3 notas que suben)
for k, f in enumerate((659.25, 783.99, 1046.5)):
    add(marimba(f, 1.4, 2.4, 0.18), 5.30 + k * 0.115, 0.19, -0.1 + 0.1 * k)

# ---------------------------------------------------------------- 5.6 golpe grave final (resuelve la tensión), suave
t = tt(1.1)
hit = np.sin(2 * np.pi * (48 + 34 * np.exp(-t * 12)) * t) * np.exp(-t * 3.4)
add(hit, 5.6, 0.40)

# ---------------------------------------------------------------- reverberación: cola oscura y corta, sin siseo
ir_n = int(0.7 * SR)
ir = rng.standard_normal(ir_n).astype(np.float32)
ir = np.convolve(ir, np.hanning(41) / np.hanning(41).sum(), mode="same")           # oscurece la cola (paso bajo fuerte)
ir *= np.exp(-np.arange(ir_n) / (0.16 * SR)).astype(np.float32)
ir[:int(0.020 * SR)] *= np.linspace(0, 1, int(0.020 * SR))


def reverb(x, wet=0.16):
    n = len(x) + len(ir)
    size = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return x + wet * y / (np.abs(y).max() + 1e-6) * np.abs(x).max()


L, R = reverb(L), reverb(R * 0.98)

# ---------------------------------------------------------------- final: desvanecido, limitador suave y escritura
fade = np.ones(N, np.float32)
fn = int(0.6 * SR)
fade[-fn:] = (0.5 * (1 + np.cos(np.linspace(0, np.pi, fn)))).astype(np.float32)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max(), 1e-6)
gain = 0.62 / peak
pcm = np.empty(N * 2, np.int16)
pcm[0::2] = np.round(np.tanh(L * gain * 1.2) / np.tanh(1.2) * 32767 * 0.9)
pcm[1::2] = np.round(np.tanh(R * gain * 1.2) / np.tanh(1.2) * 32767 * 0.9)

out = Path(sys.argv[1] if len(sys.argv) > 1 else "intro.wav")
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"{out}  {out.stat().st_size / 1024:.0f} KB  {DUR:.1f} s")
