// Audio 100% procedural (WebAudio): efectos y un secuenciador de música con intensidad variable.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});

  const A = (VS.Audio = {
    ctx: null, master: null, sfxG: null, musG: null, noise: null,
    sfxOn: true, musOn: true, last: {}, gemPitch: 0, gemT: 0,
    mode: null, key: 0, intensity: 0, step: 0, nextT: 0, timer: null,
  });

  A.init = function () {
    if (A.ctx) { if (A.ctx.state === 'suspended') A.ctx.resume(); return; }
    try {
      const C = g.AudioContext || g.webkitAudioContext;
      if (!C) return;
      A.ctx = new C();
      A.master = A.ctx.createGain(); A.master.gain.value = 0.9; A.master.connect(A.ctx.destination);
      A.sfxG = A.ctx.createGain(); A.sfxG.gain.value = A.sfxOn ? 0.7 : 0; A.sfxG.connect(A.master);
      A.musG = A.ctx.createGain(); A.musG.gain.value = A.musOn ? 0.32 : 0; A.musG.connect(A.master);
      const len = A.ctx.sampleRate * 0.5, buf = A.ctx.createBuffer(1, len, A.ctx.sampleRate), d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      A.noise = buf;
      if (A.mode) A.startMusic(A.mode, A.key);
    } catch (e) { A.ctx = null; }
  };
  A.setSfx = (on) => { A.sfxOn = !!on; if (A.sfxG) A.sfxG.gain.value = on ? 0.7 : 0; };
  A.setMusic = (on) => { A.musOn = !!on; if (A.musG) A.musG.gain.value = on ? 0.32 : 0; };
  // pausa/reanuda al perder el foco (la app pasa a segundo plano)
  A.suspend = () => { if (A.ctx && A.ctx.state === 'running') A.ctx.suspend(); };
  A.resume = () => { if (A.ctx && A.ctx.state === 'suspended') A.ctx.resume(); };

  function tone(dst, t, f, dur, type, vol, f2) {
    const c = A.ctx, o = c.createOscillator(), gn = c.createGain();
    o.type = type; o.frequency.setValueAtTime(f, t);
    if (f2) o.frequency.exponentialRampToValueAtTime(Math.max(20, f2), t + dur);
    gn.gain.setValueAtTime(vol, t); gn.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(gn); gn.connect(dst); o.start(t); o.stop(t + dur + 0.02);
  }
  function noiseHit(dst, t, dur, vol, hp) {
    const c = A.ctx, s = c.createBufferSource(), f = c.createBiquadFilter(), gn = c.createGain();
    s.buffer = A.noise; f.type = 'highpass'; f.frequency.value = hp || 800;
    gn.gain.setValueAtTime(vol, t); gn.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    s.connect(f); f.connect(gn); gn.connect(dst); s.start(t); s.stop(t + dur + 0.02);
  }

  // Efectos. Cada uno tiene un intervalo mínimo para que las hordas no saturen el audio.
  const MIN = { shoot: 0.07, kill: 0.04, gem: 0.03, coin: 0.04, bolt: 0.1, hurt: 0.15, boom: 0.08, nova: 0.2, click: 0.03 };
  A.sfx = function (name, arg) {
    if (!A.ctx || !A.sfxOn || A.ctx.state !== 'running') return;
    const c = A.ctx, t = c.currentTime;
    if (MIN[name] && t - (A.last[name] || -9) < MIN[name]) return;
    A.last[name] = t;
    const o = A.sfxG;
    switch (name) {
      case 'shoot': tone(o, t, 780, 0.06, 'square', 0.035, 380); break;
      case 'missile': tone(o, t, 220, 0.18, 'sawtooth', 0.05, 520); break;
      case 'kill': noiseHit(o, t, 0.09, 0.07, 1400); tone(o, t, 180, 0.08, 'triangle', 0.05, 70); break;
      case 'gem': {
        A.gemPitch = t - A.gemT < 0.35 ? Math.min(A.gemPitch + 1, 12) : 0; A.gemT = t;
        tone(o, t, 660 * Math.pow(2, A.gemPitch / 12), 0.08, 'sine', 0.05);
        break;
      }
      case 'coin': tone(o, t, 988, 0.06, 'square', 0.04); tone(o, t + 0.05, 1319, 0.1, 'square', 0.04); break;
      case 'heal': tone(o, t, 520, 0.15, 'sine', 0.07, 880); break;
      case 'bolt': tone(o, t, 1400, 0.12, 'sawtooth', 0.04, 200); noiseHit(o, t, 0.08, 0.04, 3000); break;
      case 'boom': noiseHit(o, t, 0.25, 0.1, 300); tone(o, t, 120, 0.25, 'sawtooth', 0.07, 40); break;
      case 'nova': tone(o, t, 90, 0.5, 'sine', 0.12, 400); noiseHit(o, t, 0.3, 0.05, 600); break;
      case 'hurt': tone(o, t, 150, 0.25, 'sawtooth', 0.12, 50); noiseHit(o, t, 0.15, 0.08, 400); break;
      case 'levelup': [523, 659, 784, 1047].forEach((f, i) => tone(o, t + i * 0.07, f, 0.18, 'triangle', 0.08)); break;
      case 'chest': [392, 523, 659, 784, 1047].forEach((f, i) => tone(o, t + i * 0.06, f, 0.2, 'square', 0.05)); break;
      case 'select': tone(o, t, 600, 0.07, 'square', 0.05); tone(o, t + 0.06, 900, 0.09, 'square', 0.05); break;
      case 'click': tone(o, t, 480, 0.04, 'square', 0.04); break;
      case 'buy': [660, 880, 1320].forEach((f, i) => tone(o, t + i * 0.06, f, 0.12, 'square', 0.05)); break;
      case 'deny': tone(o, t, 160, 0.18, 'square', 0.07, 100); break;
      case 'warn': tone(o, t, 330, 0.35, 'sawtooth', 0.08, 220); tone(o, t + 0.4, 330, 0.35, 'sawtooth', 0.08, 220); break;
      case 'boss': [110, 104, 98].forEach((f, i) => tone(o, t + i * 0.3, f, 0.5, 'sawtooth', 0.12, f * 0.7)); break;
      case 'win': [523, 659, 784, 1047, 1319, 1568].forEach((f, i) => tone(o, t + i * 0.1, f, 0.3, 'triangle', 0.09)); break;
      case 'dead': tone(o, t, 330, 0.9, 'sawtooth', 0.1, 55); noiseHit(o, t, 0.6, 0.08, 200); break;
    }
  };

  // ---- Música ----
  const KEYS = [-3, 2, 4]; // la menor, re menor, mi menor (en semitonos respecto a A4... valores relativos a 440Hz)
  const CHORDS = [[0, 3, 7], [8, 12, 15], [3, 7, 10], [10, 14, 17]]; // i - VI - III - VII
  const hz = (semi) => 440 * Math.pow(2, semi / 12);

  A.startMusic = function (mode, key) {
    A.mode = mode; A.key = key || 0; A.step = 0;
    if (!A.ctx) return;
    A.stopTimer();
    A.nextT = A.ctx.currentTime + 0.1;
    A.timer = setInterval(A.schedule, 30);
  };
  A.stopMusic = function () { A.mode = null; A.stopTimer(); };
  A.stopTimer = function () { if (A.timer) { clearInterval(A.timer); A.timer = null; } };

  A.schedule = function () {
    const c = A.ctx;
    if (!c || c.state !== 'running' || !A.musOn) { if (c) A.nextT = Math.max(A.nextT, c.currentTime + 0.05); return; }
    const battle = A.mode === 'battle', bpm = battle ? 118 + A.intensity * 8 : 84, sd = 60 / bpm / 2;
    while (A.nextT < c.currentTime + 0.15) {
      const s = A.step, bar = Math.floor(s / 8) % 4, st = s % 8, t = A.nextT, ch = CHORDS[bar], root = KEYS[A.key] + ch[0];
      const dst = A.musG;
      // bajo
      if (st === 0 || st === 3 || st === 4 || (battle && st === 6)) tone(dst, t, hz(root - 24), sd * 1.6, 'sawtooth', 0.22, hz(root - 24) * 0.98);
      // arpegio
      const note = KEYS[A.key] + ch[(st + (bar % 2)) % 3] + (st % 2 ? 12 : 0);
      if (battle || st % 2 === 0) tone(dst, t, hz(note - 12), sd * 0.9, battle ? 'square' : 'triangle', battle ? 0.06 : 0.1);
      if (!battle && st === 0) tone(dst, t, hz(KEYS[A.key] + ch[2]), sd * 7, 'sine', 0.08);
      if (battle) {
        if (st % 4 === 0) { tone(dst, t, 140, 0.14, 'sine', 0.35, 40); } // bombo
        if (A.intensity >= 1 && st % 2 === 1) noiseHit(dst, t, 0.04, 0.08, 6000); // hi-hat
        if (A.intensity >= 2 && st === 4) noiseHit(dst, t, 0.12, 0.12, 1800); // caja
        if (A.intensity >= 1 && (st === 2 || st === 5)) tone(dst, t, hz(note), sd * 0.5, 'triangle', 0.07);
      }
      A.nextT += sd; A.step++;
    }
  };
})(typeof window !== 'undefined' ? window : globalThis);
