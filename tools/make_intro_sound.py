#!/usr/bin/env python3
"""Compone el sonido de la animación de entrada (síntesis pura, sin muestras de terceros).

Está sincronizado con hyprarch-intro (los tiempos son los mismos):
  0.05 línea de horizonte  ·  0.55 zumbido de la rejilla  ·  0.9-2.5 sale el sol
  1.9-2.9 título (un tic por letra + glitch)  ·  3.0-4.0 subtítulo (teclas)  ·  3.1 destello
  3.9-5.3 entra Claudito (whoosh)  ·  5.3 campanita  ·  5.6 golpe grave final  ·  6.4 fin

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


def add(sig, start, vol=1.0, pan=0.0):
    """Suma `sig` en el instante `start` (s) con volumen y paneo (-1 izquierda … 1 derecha)."""
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i].astype(np.float32)
    gl = vol * np.sqrt((1 - pan) / 2)
    gr = vol * np.sqrt((1 + pan) / 2)
    L[i:i + len(sig)] += sig * gl
    R[i:i + len(sig)] += sig * gr


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, attack, release, power=1.0):
    e = np.ones(n, np.float32)
    a, r = max(1, int(attack * SR)), max(1, int(release * SR))
    e[:a] = np.linspace(0, 1, a) ** power
    e[-r:] *= np.linspace(1, 0, r) ** power
    return e


def tone(freq, dur, harmonics=(1.0,), attack=0.005, release=0.1, detune=0.0):
    t = tt(dur)
    s = np.zeros_like(t)
    for k, amp in enumerate(harmonics, start=1):
        s += amp * np.sin(2 * np.pi * freq * k * (1 + detune) * t)
    return (s / max(1e-6, sum(harmonics))) * env(len(t), attack, release)


def chirp(f0, f1, dur, exp=True):
    t = tt(dur)
    k = (f1 / f0) ** (t / dur) if exp else (f0 + (f1 - f0) * t / dur) / f0
    if exp:
        phase = 2 * np.pi * f0 * dur / np.log(f1 / f0) * (k - 1)
    else:
        phase = 2 * np.pi * (f0 * t + (f1 - f0) * t ** 2 / (2 * dur))
    return np.sin(phase)


def lowpass_noise(dur, cutoff_sweep):
    """Ruido con filtro paso bajo móvil (promedio de ventana variable aproximado con mezcla de varias ventanas)."""
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32)
    wins = (4, 16, 64, 256)
    smoothed = []
    for w in wins:
        k = np.ones(w, np.float32) / w
        smoothed.append(np.convolve(x, k, mode="same"))
    pos = np.clip(cutoff_sweep(np.linspace(0, 1, n)), 0, 1) * (len(wins) - 1)
    lo = np.floor(pos).astype(int)
    hi = np.minimum(lo + 1, len(wins) - 1)
    fr = pos - lo
    for i in range(len(wins)):
        out += smoothed[i] * ((lo == i) * (1 - fr) + (hi == i) * fr)
    return out / (np.abs(out).max() + 1e-6)


# ---------------------------------------------------------------- 0.05 línea de horizonte: zap ascendente
z = chirp(180, 2600, 0.8) * env(int(0.8 * SR), 0.02, 0.5, 1.5)
add(z, 0.05, 0.18, -0.3)
add(z * 0.5, 0.05, 0.10, 0.3)

# ---------------------------------------------------------------- 0.55-4.2 zumbido grave de la rejilla (crece y se queda)
t = tt(3.9)
hum = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110 * t * (1 + 0.002 * np.sin(2 * np.pi * 0.7 * t)))
       + 0.25 * np.sin(2 * np.pi * 165 * t))
hum *= np.minimum(1, t / 1.6) ** 2 * np.minimum(1, (3.9 - t) / 0.9)
add(hum, 0.55, 0.30)

# ---------------------------------------------------------------- 0.9-2.5 sale el sol: acorde que sube (La menor) + soplido
t = tt(1.9)
rise = np.zeros_like(t)
for f0, amp in ((110, 1.0), (165, 0.8), (220, 0.7), (330, 0.5)):
    ramp = f0 * (1 + 0.5 * (t / 1.9) ** 2)
    rise += amp * np.sin(2 * np.pi * np.cumsum(ramp) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t))
rise *= (t / 1.9) ** 1.6 * np.minimum(1, (1.9 - t) / 0.25)
add(rise / 3, 0.9, 0.34, -0.15)
sw = lowpass_noise(1.9, lambda x: 0.2 + 0.7 * x)
sw *= (t / 1.9) ** 2.2 * np.minimum(1, (1.9 - t) / 0.3)
add(sw, 0.9, 0.16, 0.2)

# ---------------------------------------------------------------- 1.9-2.9 título: un tic por letra (escala pentatónica)
notes = [392.0, 440.0, 523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
for i, f in enumerate(notes):
    at = 1.9 + i * (1.0 / 9.0)
    b = tone(f, 0.14, harmonics=(1.0, 0.0, 0.35, 0.0, 0.12), attack=0.002, release=0.12)
    b2 = tone(f * 2, 0.05, attack=0.001, release=0.04)
    b[:len(b2)] += 0.5 * b2
    add(b, at, 0.20, np.sin(i) * 0.45)


def glitch(start, dur, vol, crush=24):
    n = int(dur * SR)
    x = np.sign(rng.standard_normal(n)) * (rng.random(n) ** 2)
    hold = rng.integers(2, 40)
    x = np.repeat(x[::hold], hold)[:n]                   # sample & hold = aspecto digital
    x = np.round(x * crush) / crush
    add((x * env(n, 0.002, dur * 0.6)).astype(np.float32), start, vol, rng.uniform(-0.6, 0.6))


for gt in (1.95, 2.05, 2.22, 2.4, 2.58, 2.74, 2.9):         # ráfagas mientras aparece el título
    glitch(gt, rng.uniform(0.02, 0.06), 0.16)
glitch(4.6, 0.10, 0.20)                                      # glitches sueltos (iguales a los de la animación)
glitch(5.1, 0.07, 0.17)

# ---------------------------------------------------------------- 3.1-3.9 destello que barre el título (brillo agudo)
t = tt(0.8)
sp = np.zeros_like(t)
for _ in range(14):
    f = rng.uniform(2200, 6500)
    c = rng.uniform(0.05, 0.75)
    sp += np.sin(2 * np.pi * f * t) * np.exp(-((t - c) ** 2) / 0.004)
add(sp / 6, 3.1, 0.10, 0.0)

# ---------------------------------------------------------------- 3.0-4.0 subtítulo: teclas
for i in range(17):
    at = 3.0 + i * (1.0 / 18.0)
    n = int(0.03 * SR)
    click = (rng.standard_normal(n) * np.exp(-np.arange(n) / (0.004 * SR))).astype(np.float32)
    click += 0.8 * np.sin(2 * np.pi * (1500 + 400 * (i % 3)) * tt(0.03)) * np.exp(-np.arange(n) / (0.006 * SR))
    add(click, at, rng.uniform(0.05, 0.09), rng.uniform(-0.5, 0.5))

# ---------------------------------------------------------------- 1.2-2.2 el robotito se materializa: barrido digital ascendente + destello
mat = chirp(300, 2800, 0.9) * env(int(0.9 * SR), 0.03, 0.4, 1.4)
add(mat, 1.2, 0.13, 0.15)
glit = np.zeros(int(0.12 * SR), np.float32)
add(tone(1568.0, 0.35, harmonics=(1.0, 0.4), attack=0.002, release=0.3), 1.95, 0.10, 0.1)

# ---------------------------------------------------------------- 4.0 saludo del robotito: dos notas amables
add(tone(784.0, 0.25, harmonics=(1.0, 0.3), attack=0.004, release=0.2), 4.0, 0.12, -0.1)
add(tone(1046.5, 0.45, harmonics=(1.0, 0.3), attack=0.004, release=0.4), 4.12, 0.12, 0.1)
del glit

# ---------------------------------------------------------------- 3.9-5.3 entra Claudito: whoosh en arco + vuelo
t = tt(1.4)
who = lowpass_noise(1.4, lambda x: 0.15 + 0.8 * np.sin(np.pi * x))
who *= np.sin(np.pi * np.clip(t / 1.4, 0, 1)) ** 1.5
pan = np.linspace(0.9, 0.0, len(t))
n = len(t)
i0 = int(3.9 * SR)
L[i0:i0 + n] += (who * 0.20 * np.sqrt((1 - pan) / 2)).astype(np.float32)[: N - i0]
R[i0:i0 + n] += (who * 0.20 * np.sqrt((1 + pan) / 2)).astype(np.float32)[: N - i0]
add(chirp(260, 880, 1.4) * np.sin(np.pi * t / 1.4) ** 2, 3.9, 0.07, 0.4)

# ---------------------------------------------------------------- 5.3 campanita de llegada (3 notas que suben)
for k, f in enumerate((659.25, 783.99, 1046.5)):
    at = 5.30 + k * 0.115
    bell = tone(f, 1.4, harmonics=(1.0, 0.45, 0.2), attack=0.003, release=1.2, detune=0.0)
    b2 = tone(f * 2.01, 1.0, attack=0.003, release=0.9)
    bell[:len(b2)] += 0.35 * b2
    add(bell * np.exp(-tt(1.4) * 2.2), at, 0.20, -0.1 + 0.1 * k)

# ---------------------------------------------------------------- 5.6 golpe grave final (resuelve la tensión)
t = tt(1.1)
hit = np.sin(2 * np.pi * (48 + 40 * np.exp(-t * 14)) * t) * np.exp(-t * 3.2)
add(hit, 5.6, 0.45)

# ---------------------------------------------------------------- reverberación suave (cola de ruido que decae)
ir_n = int(0.9 * SR)
ir = (rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.20 * SR))).astype(np.float32)
ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))


def reverb(x, wet=0.22):
    n = len(x) + len(ir)
    size = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return x + wet * y / (np.abs(y).max() + 1e-6) * np.abs(x).max()


L, R = reverb(L), reverb(R * 0.98)

# ---------------------------------------------------------------- final: desvanecido, normalización y escritura
fade = np.ones(N, np.float32)
fn = int(0.5 * SR)
fade[-fn:] = np.linspace(1, 0, fn) ** 1.5
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max(), 1e-6)
gain = 0.78 / peak
pcm = np.empty(N * 2, np.int16)
pcm[0::2] = np.clip(L * gain, -1, 1) * 32767
pcm[1::2] = np.clip(R * gain, -1, 1) * 32767

out = Path(sys.argv[1] if len(sys.argv) > 1 else "intro.wav")
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"{out}  {out.stat().st_size / 1024:.0f} KB  {DUR:.1f} s")
