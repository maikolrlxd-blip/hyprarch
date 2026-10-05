// Render 2D: sprites prerenderizados con brillo, cámara, partículas y efectos. Solo dibuja; no modifica la simulación.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const D = VS.data, U = VS.util;
  const TAU = Math.PI * 2, SS = 3; // SS = supermuestreo de los sprites

  function mk(w, h) {
    const c = g.document.createElement('canvas');
    c.width = Math.ceil(w); c.height = Math.ceil(h);
    return c;
  }
  function shade(hex, f) { // aclara (f>0) u oscurece (f<0) un color #rgb / #rrggbb
    let h = hex.replace('#', '');
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    const n = parseInt(h, 16), ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    return 'rgb(' + ch.map((v) => Math.round(f >= 0 ? v + (255 - v) * f : v * (1 + f))).join(',') + ')';
  }

  // ---- Formas de enemigos y naves (dibujadas centradas en 0,0 con radio r) ----
  const SHAPES = {
    diamond(c, r, col) { c.beginPath(); c.moveTo(0, -r * 1.25); c.lineTo(r, 0); c.lineTo(0, r * 1.25); c.lineTo(-r, 0); c.closePath(); fillStroke(c, col); },
    hex(c, r, col) { poly(c, 6, r, 0); fillStroke(c, col); c.fillStyle = shade(col, -0.5); c.beginPath(); c.arc(0, 0, r * 0.4, 0, TAU); c.fill(); },
    tri(c, r, col) { c.beginPath(); c.moveTo(0, -r * 1.35); c.lineTo(r, r); c.lineTo(-r, r); c.closePath(); fillStroke(c, col); },
    orb(c, r, col) { c.beginPath(); c.arc(0, 0, r, 0, TAU); fillStroke(c, col); c.fillStyle = shade(col, -0.4); [[-0.35, -0.2], [0.4, -0.1], [0, 0.4]].forEach(([x, y]) => { c.beginPath(); c.arc(x * r, y * r, r * 0.28, 0, TAU); c.fill(); }); },
    cannon(c, r, col) { c.fillStyle = shade(col, -0.3); c.fillRect(-r * 0.22, -r * 1.4, r * 0.44, r * 1.1); c.beginPath(); c.arc(0, 0, r, 0, TAU); fillStroke(c, col); c.fillStyle = '#fff'; c.beginPath(); c.arc(0, 0, r * 0.28, 0, TAU); c.fill(); },
    box(c, r, col) { c.beginPath(); c.roundRect(-r, -r, r * 2, r * 2, r * 0.25); fillStroke(c, col); c.fillStyle = shade(col, -0.45); c.fillRect(-r * 0.5, -r * 0.5, r, r); },
    hive(c, r, col) { poly(c, 6, r, Math.PI / 6); fillStroke(c, col); c.fillStyle = shade(col, -0.5); for (let i = 0; i < 6; i++) { const a = (i / 6) * TAU; c.beginPath(); c.arc(Math.cos(a) * r * 0.55, Math.sin(a) * r * 0.55, r * 0.17, 0, TAU); c.fill(); } c.beginPath(); c.arc(0, 0, r * 0.3, 0, TAU); c.fill(); },
    sentinel(c, r, col) { poly(c, 8, r, Math.PI / 8); fillStroke(c, col); c.fillStyle = shade(col, -0.55); c.beginPath(); c.arc(0, 0, r * 0.5, 0, TAU); c.fill(); c.fillStyle = '#fff'; c.beginPath(); c.arc(0, 0, r * 0.2, 0, TAU); c.fill(); for (let i = 0; i < 4; i++) { c.save(); c.rotate((i / 4) * TAU); c.fillStyle = shade(col, -0.2); c.fillRect(-r * 0.12, -r * 1.3, r * 0.24, r * 0.5); c.restore(); } },
    jugg(c, r, col) { c.beginPath(); c.moveTo(0, -r * 1.1); c.lineTo(r * 1.05, -r * 0.2); c.lineTo(r * 0.8, r); c.lineTo(-r * 0.8, r); c.lineTo(-r * 1.05, -r * 0.2); c.closePath(); fillStroke(c, col); c.fillStyle = shade(col, -0.55); c.fillRect(-r * 0.45, -r * 0.2, r * 0.9, r * 0.45); c.fillStyle = '#ff0'; c.fillRect(-r * 0.3, -r * 0.1, r * 0.2, r * 0.15); c.fillRect(r * 0.1, -r * 0.1, r * 0.2, r * 0.15); },
  };
  function poly(c, n, r, off) { c.beginPath(); for (let i = 0; i < n; i++) { const a = off + (i / n) * TAU - Math.PI / 2; i ? c.lineTo(Math.cos(a) * r, Math.sin(a) * r) : c.moveTo(Math.cos(a) * r, Math.sin(a) * r); } c.closePath(); }
  function fillStroke(c, col) {
    const gr = c.createLinearGradient(0, -20, 0, 20);
    gr.addColorStop(0, shade(col, 0.25)); gr.addColorStop(1, shade(col, -0.35));
    c.fillStyle = gr; c.fill(); c.lineWidth = 1.3; c.strokeStyle = shade(col, 0.55); c.stroke();
  }

  const SHIPS = {
    falcon(c, r, col) { c.beginPath(); c.moveTo(0, -r * 1.2); c.lineTo(r * 0.95, r * 0.9); c.lineTo(0, r * 0.4); c.lineTo(-r * 0.95, r * 0.9); c.closePath(); fillStroke(c, col); cockpit(c, r); },
    comet(c, r, col) { c.beginPath(); c.moveTo(0, -r * 1.4); c.lineTo(r * 0.55, r * 0.5); c.lineTo(r * 1.0, r * 1.0); c.lineTo(0, r * 0.5); c.lineTo(-r * 1.0, r * 1.0); c.lineTo(-r * 0.55, r * 0.5); c.closePath(); fillStroke(c, col); cockpit(c, r); },
    bulwark(c, r, col) { poly(c, 6, r * 1.1, 0); fillStroke(c, col); c.fillStyle = shade(col, -0.5); c.beginPath(); c.arc(0, 0, r * 0.55, 0, TAU); c.fill(); cockpit(c, r); },
    wraith(c, r, col) { c.beginPath(); c.moveTo(0, -r * 1.3); c.lineTo(r * 1.25, r * 0.6); c.lineTo(r * 0.3, r * 0.3); c.lineTo(0, r * 0.95); c.lineTo(-r * 0.3, r * 0.3); c.lineTo(-r * 1.25, r * 0.6); c.closePath(); fillStroke(c, col); cockpit(c, r); },
    nova(c, r, col) { c.beginPath(); c.arc(0, 0, r, 0, TAU); fillStroke(c, col); c.strokeStyle = shade(col, 0.7); c.lineWidth = 1.5; c.beginPath(); c.arc(0, 0, r * 1.2, 0, TAU); c.stroke(); c.fillStyle = shade(col, -0.5); c.beginPath(); c.moveTo(0, -r * 0.9); c.lineTo(r * 0.4, r * 0.1); c.lineTo(-r * 0.4, r * 0.1); c.fill(); cockpit(c, r); },
  };
  function cockpit(c, r) { c.fillStyle = 'rgba(255,255,255,.85)'; c.beginPath(); c.ellipse(0, -r * 0.1, r * 0.2, r * 0.38, 0, 0, TAU); c.fill(); }

  // Crea un sprite con halo: fn(ctx, r, color) dibuja centrado.
  function sprite(fn, r, col, glow, flash) {
    const pad = (glow || 0) + 4, s = Math.ceil((r + pad) * 2 * SS), c = mk(s, s), x = c.getContext('2d');
    x.translate(s / 2, s / 2); x.scale(SS, SS);
    if (glow) { x.shadowColor = col; x.shadowBlur = glow; }
    fn(x, r, col);
    if (flash) { x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-atop'; x.fillStyle = 'rgba(255,255,255,.85)'; x.fillRect(0, 0, s, s); }
    return { c, half: s / SS / 2 };
  }

  class Renderer {
    constructor(canvas) {
      this.cv = canvas; this.ctx = canvas.getContext('2d');
      this.W = 0; this.H = 0; this.zoom = 1; this.cam = { x: 0, y: 0 };
      this.parts = []; this.texts = []; this.bolts = []; this.booms = []; this.banners = [];
      this.shake = 0; this.vig = 0; this.t = 0; this.stars = [];
      for (let i = 0; i < 80; i++) this.stars.push({ x: Math.random(), y: Math.random(), z: Math.random() * 0.8 + 0.2 });
      this.sprites = {}; this.shipSprites = {};
      this.resize();
    }

    resize() {
      const dpr = Math.min(g.devicePixelRatio || 1, 2.5);
      this.W = g.innerWidth; this.H = g.innerHeight;
      this.cv.width = Math.round(this.W * dpr); this.cv.height = Math.round(this.H * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.zoom = Math.max(0.6, Math.min(this.W, this.H) / 520);
      this.viewR = Math.hypot(this.W, this.H) / this.zoom / 2 + 50;
    }

    spr(e) {
      const key = e.type + (e.elite ? '*' : '');
      let s = this.sprites[key];
      if (!s) {
        const def = D.enemies[e.type], r = def.r * (e.elite ? 1.45 : 1), col = e.elite ? '#ffd24a' : def.color;
        const fn = (c, rr, cc) => SHAPES[def.shape](c, rr, e.elite ? def.color : cc);
        s = this.sprites[key] = { n: sprite(fn, r, col, def.boss ? 14 : 7, false), f: sprite(fn, r, col, def.boss ? 14 : 7, true) };
      }
      return s;
    }
    shipSpr(id) {
      let s = this.shipSprites[id];
      if (!s) { const sh = D.ships[id]; s = this.shipSprites[id] = sprite(SHIPS[id], 13, sh.color, 10, false); }
      return s;
    }
    gemSpr(v) {
      const k = v >= 10 ? 'g3' : v >= 3 ? 'g2' : 'g1';
      if (!this.sprites[k]) {
        const col = k === 'g3' ? '#c6f' : k === 'g2' ? '#6f9' : '#5cf', r = k === 'g3' ? 6.5 : k === 'g2' ? 5.2 : 4;
        this.sprites[k] = sprite((c, rr, cc) => { c.beginPath(); c.moveTo(0, -rr * 1.25); c.lineTo(rr, 0); c.lineTo(0, rr * 1.25); c.lineTo(-rr, 0); c.closePath(); fillStroke(c, cc); }, r, col, 8, false);
      }
      return this.sprites[k];
    }
    simple(k, fn, r, col, glow) { return this.sprites[k] || (this.sprites[k] = sprite(fn, r, col, glow, false)); }

    // ---- efectos a partir de eventos de la simulación ----
    event(ev, sim, opts) {
      const P = sim.p;
      switch (ev.type) {
        case 'kill': {
          const n = ev.boss ? 50 : ev.elite ? 22 : 8;
          for (let i = 0; i < n; i++) this.burst(ev.x, ev.y, ev.color, ev.boss ? 260 : 130, 0.35 + Math.random() * 0.4, 1.5 + Math.random() * 2.5);
          if (ev.boss || ev.elite) this.booms.push({ x: ev.x, y: ev.y, r: ev.r * 2.5, t: 0, max: 0.5, color: ev.color });
          break;
        }
        case 'dmg':
          if (opts.numbers && this.texts.length < 30 && (ev.crit || Math.random() < 0.45))
            this.texts.push({ x: ev.x + (Math.random() - 0.5) * 10, y: ev.y, v: Math.round(ev.v), t: 0, crit: ev.crit });
          break;
        case 'hurt': this.vig = 0.5; if (opts.shake) this.shake = Math.max(this.shake, 0.25); break;
        case 'shake': if (opts.shake) this.shake = Math.max(this.shake, ev.v); break;
        case 'bolt': this.bolts.push({ pts: ev.pts, t: 0, max: 0.25 }); break;
        case 'boom': this.booms.push({ x: ev.x, y: ev.y, r: ev.r, t: 0, max: 0.3, color: ev.color || '#fa6' }); for (let i = 0; i < 10; i++) this.burst(ev.x, ev.y, ev.color || '#fa6', 140, 0.3 + Math.random() * 0.3, 2); break;
        case 'nova': this.shake = Math.max(this.shake, opts.shake ? 0.12 : 0); break;
        case 'levelup': this.banners.push({ txt: VS.t('levelup'), t: 0, max: 1.2, col: '#ff6', size: 1 }); for (let i = 0; i < 24; i++) this.burst(P.x, P.y, '#ff6', 200, 0.5, 2); break;
        case 'warn': this.banners.push({ txt: VS.t('warn.' + ev.key), t: 0, max: 1.6, col: '#f96', size: 1 }); break;
        case 'boss': this.banners.push({ txt: ev.final ? VS.t('warn.final') : VS.t('warn.boss') + ' ' + VS.t('boss.' + ev.id), t: 0, max: 2.4, col: '#f44', size: 1.25 }); if (opts.shake) this.shake = Math.max(this.shake, 0.4); break;
        case 'revive': for (let i = 0; i < 40; i++) this.burst(P.x, P.y, '#fff', 300, 0.7, 2.5); break;
        case 'dead': for (let i = 0; i < 50; i++) this.burst(P.x, P.y, '#5df', 260, 0.9, 3); break;
      }
    }
    burst(x, y, color, speed, life, size) {
      if (this.parts.length > 700) return;
      const a = Math.random() * TAU, s = speed * (0.3 + Math.random() * 0.7);
      this.parts.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s, life, max: life, size, color });
    }

    update(dt, sim) {
      this.t += dt;
      this.shake = Math.max(0, this.shake - dt); this.vig = Math.max(0, this.vig - dt);
      const P = sim.p;
      this.cam.x += (P.x + P.mx * 40 - this.cam.x) * Math.min(1, dt * 6);
      this.cam.y += (P.y + P.my * 40 - this.cam.y) * Math.min(1, dt * 6);
      for (let i = this.parts.length - 1; i >= 0; i--) {
        const p = this.parts[i];
        p.x += p.vx * dt; p.y += p.vy * dt; p.vx *= 1 - 3 * dt; p.vy *= 1 - 3 * dt; p.life -= dt;
        if (p.life <= 0) { this.parts[i] = this.parts[this.parts.length - 1]; this.parts.pop(); }
      }
      for (const arr of [this.texts, this.bolts, this.booms, this.banners]) {
        for (let i = arr.length - 1; i >= 0; i--) { arr[i].t += dt; if (arr[i].t > (arr[i].max || 0.7)) arr.splice(i, 1); }
      }
      // estela de misiles y propulsor
      if (sim.state === 'running') {
        for (const s of sim.shots) if (s.kind === 'missile' && Math.random() < 0.8) this.parts.push({ x: s.x, y: s.y, vx: -s.vx * 0.1, vy: -s.vy * 0.1, life: 0.3, max: 0.3, size: 2.4, color: '#fb6' });
        if ((P.mx || P.my) && Math.random() < 0.7) this.parts.push({ x: P.x - Math.cos(P.ang) * 10, y: P.y - Math.sin(P.ang) * 10, vx: -P.mx * 40, vy: -P.my * 40, life: 0.25, max: 0.25, size: 2.2, color: '#fa5' });
      }
    }

    // ---- dibujo ----
    draw(sim, input, opts) {
      const c = this.ctx, W = this.W, H = this.H, z = this.zoom, st = sim.stage;
      // fondo
      const bg = c.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, st.color[0]); bg.addColorStop(1, st.color[1]);
      c.fillStyle = bg; c.fillRect(0, 0, W, H);
      const sx = this.shake > 0 ? (Math.random() - 0.5) * 16 * this.shake : 0, sy = this.shake > 0 ? (Math.random() - 0.5) * 16 * this.shake : 0;
      // estrellas con parallax
      c.fillStyle = '#fff';
      for (const s of this.stars) {
        const x = (((s.x * W - this.cam.x * z * 0.15 * s.z) % W) + W) % W, y = (((s.y * H - this.cam.y * z * 0.15 * s.z) % H) + H) % H;
        c.globalAlpha = 0.25 + s.z * 0.5; c.fillRect(x, y, s.z * 2, s.z * 2);
      }
      c.globalAlpha = 1;
      c.save();
      c.translate(W / 2 + sx, H / 2 + sy); c.scale(z, z); c.translate(-this.cam.x, -this.cam.y);
      this.drawGrid(c, st, z);
      const vx0 = this.cam.x - W / z / 2 - 40, vx1 = this.cam.x + W / z / 2 + 40, vy0 = this.cam.y - H / z / 2 - 40, vy1 = this.cam.y + H / z / 2 + 40;
      const vis = (x, y) => x > vx0 && x < vx1 && y > vy0 && y < vy1;

      // gemas y recogibles
      for (const gm of sim.gems) if (vis(gm.x, gm.y)) { const s = this.gemSpr(gm.v); c.drawImage(s.c, gm.x - s.half, gm.y - s.half, s.half * 2, s.half * 2); }
      for (const dr of sim.drops) if (vis(dr.x, dr.y)) this.drawDrop(c, dr);
      // aura / anillos
      for (const w of sim.weapons) if (w.id === 'aura' && w.R) {
        const gr = c.createRadialGradient(sim.p.x, sim.p.y, w.R * 0.2, sim.p.x, sim.p.y, w.R);
        gr.addColorStop(0, 'rgba(100,255,160,.02)'); gr.addColorStop(1, 'rgba(100,255,160,.22)');
        c.fillStyle = gr; c.beginPath(); c.arc(sim.p.x, sim.p.y, w.R, 0, TAU); c.fill();
        c.strokeStyle = 'rgba(120,255,170,.5)'; c.lineWidth = 1.5; c.setLineDash([6, 8]); c.lineDashOffset = -this.t * 30; c.stroke(); c.setLineDash([]);
      }
      for (const r of sim.rings) {
        c.globalAlpha = Math.max(0, 1 - r.r / r.maxR) * 0.9; c.strokeStyle = r.color; c.lineWidth = 6; c.shadowColor = r.color; c.shadowBlur = 12;
        c.beginPath(); c.arc(r.x, r.y, r.r, 0, TAU); c.stroke(); c.shadowBlur = 0; c.globalAlpha = 1;
      }
      // enemigos
      const P = sim.p;
      for (const e of sim.enemies) {
        if (!vis(e.x, e.y)) continue;
        const sp = this.spr(e), img = e.flash > 0 ? sp.f : sp.n;
        const rot = ROT[D.enemies[e.type].shape];
        const a = rot ? (e.st === 2 && e.beh === 'dash' ? Math.atan2(e.dy, e.dx) : Math.atan2(P.y - e.y, P.x - e.x)) + Math.PI / 2 : 0;
        const sc = e.beh === 'dash' && e.st === 1 ? 1 + Math.sin(this.t * 40) * 0.12 : 1;
        c.save(); c.translate(e.x, e.y); if (rot) c.rotate(a);
        c.drawImage(img.c, -img.half * sc, -img.half * sc, img.half * 2 * sc, img.half * 2 * sc);
        c.restore();
        if (e.elite && !e.boss && e.hp < e.max) this.hpBar(c, e.x, e.y - e.r - 6, e.r * 2, e.hp / e.max, '#fc4');
        if (e.beh === 'dash' && e.st === 1) { c.strokeStyle = 'rgba(255,255,80,.5)'; c.lineWidth = 2; c.beginPath(); c.moveTo(e.x, e.y); c.lineTo(e.x + e.dx * 220, e.y + e.dy * 220); c.stroke(); }
        if (e.beh === 'jugg' && e.st === 1) { c.strokeStyle = 'rgba(255,60,60,.55)'; c.lineWidth = 6; c.beginPath(); c.moveTo(e.x, e.y); c.lineTo(e.x + e.dx * 380, e.y + e.dy * 380); c.stroke(); }
      }
      // disparos enemigos
      const bs = this.simple('eb', (cc, r, col) => { cc.beginPath(); cc.arc(0, 0, r, 0, TAU); cc.fillStyle = col; cc.fill(); cc.fillStyle = '#fff'; cc.beginPath(); cc.arc(0, 0, r * 0.45, 0, TAU); cc.fill(); }, 5, '#f4a', 8);
      for (const b of sim.eshots) if (vis(b.x, b.y)) { const k = b.r / 5; c.drawImage(bs.c, b.x - bs.half * k, b.y - bs.half * k, bs.half * 2 * k, bs.half * 2 * k); }
      // armas orbitales
      for (const w of sim.weapons) if (w.id === 'orbit') for (const b of w.blades) {
        c.save(); c.translate(b.x, b.y); c.rotate(b.a * 3);
        c.fillStyle = '#fd5'; c.shadowColor = '#fd5'; c.shadowBlur = 10;
        c.beginPath(); c.moveTo(0, -b.r * 1.3); c.lineTo(b.r * 0.55, 0); c.lineTo(0, b.r * 1.3); c.lineTo(-b.r * 0.55, 0); c.closePath(); c.fill();
        c.restore();
      }
      c.shadowBlur = 0;
      // disparos propios
      for (const s of sim.shots) {
        if (!vis(s.x, s.y)) continue;
        if (s.kind === 'pulse') { c.save(); c.translate(s.x, s.y); c.rotate(Math.atan2(s.vy, s.vx)); c.fillStyle = '#7ff'; c.shadowColor = '#6ff'; c.shadowBlur = 8; c.beginPath(); c.roundRect(-8, -2.2, 16, 4.4, 2); c.fill(); c.restore(); }
        else { c.save(); c.translate(s.x, s.y); c.rotate(s.ang); c.fillStyle = '#fb7'; c.shadowColor = '#f94'; c.shadowBlur = 8; c.beginPath(); c.moveTo(8, 0); c.lineTo(-6, -4.5); c.lineTo(-3, 0); c.lineTo(-6, 4.5); c.closePath(); c.fill(); c.restore(); }
      }
      c.shadowBlur = 0;
      // rayos
      for (const b of this.bolts) {
        c.globalAlpha = 1 - b.t / 0.25; c.strokeStyle = '#bdf'; c.shadowColor = '#9bf'; c.shadowBlur = 12; c.lineWidth = 3;
        c.beginPath();
        b.pts.forEach((p, i) => {
          if (i === 0) { c.moveTo(p.x, p.y); return; }
          const q = b.pts[i - 1], n = 4;
          for (let k = 1; k <= n; k++) { const f = k / n, jx = k < n ? (Math.random() - 0.5) * 14 : 0, jy = k < n ? (Math.random() - 0.5) * 14 : 0; c.lineTo(q.x + (p.x - q.x) * f + jx, q.y + (p.y - q.y) * f + jy); }
        });
        c.stroke(); c.shadowBlur = 0; c.globalAlpha = 1;
      }
      // explosiones
      for (const b of this.booms) {
        const k = b.t / b.max; c.globalAlpha = (1 - k) * 0.7; c.fillStyle = b.color;
        c.beginPath(); c.arc(b.x, b.y, b.r * (0.4 + 0.6 * k), 0, TAU); c.fill(); c.globalAlpha = 1;
      }
      // jugador
      if (sim.state !== 'dead' && !(opts && opts.menu)) this.drawPlayer(c, sim);
      // partículas
      for (const p of this.parts) { c.globalAlpha = Math.max(0, p.life / p.max); c.fillStyle = p.color; c.fillRect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size); }
      c.globalAlpha = 1;
      // números de daño
      c.textAlign = 'center';
      for (const t of this.texts) {
        c.globalAlpha = 1 - t.t / 0.7; c.font = `800 ${t.crit ? 15 : 11}px system-ui,sans-serif`;
        c.lineWidth = 3; c.strokeStyle = 'rgba(0,0,0,.6)'; c.fillStyle = t.crit ? '#ffd24a' : '#fff';
        const y = t.y - t.t * 30; c.strokeText(t.v, t.x, y); c.fillText(t.v, t.x, y);
      }
      c.globalAlpha = 1;
      c.restore();

      // viñeta de daño
      if (this.vig > 0) {
        const gr = c.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.hypot(W, H) / 2);
        gr.addColorStop(0, 'rgba(255,0,0,0)'); gr.addColorStop(1, `rgba(255,30,30,${this.vig})`);
        c.fillStyle = gr; c.fillRect(0, 0, W, H);
      }
      // flecha hacia el jefe fuera de pantalla + barra de vida
      const boss = sim.enemies.find((e) => e.boss);
      if (boss) this.drawBoss(c, sim, boss);
      // banners
      for (const b of this.banners) {
        const k = b.t / b.max, a = k < 0.15 ? k / 0.15 : k > 0.75 ? (1 - k) / 0.25 : 1;
        c.globalAlpha = Math.max(0, a); c.textAlign = 'center'; c.fillStyle = b.col; c.strokeStyle = 'rgba(0,0,0,.7)'; c.lineWidth = 6;
        c.font = `900 ${Math.min(W * 0.1, 44) * b.size}px system-ui,sans-serif`;
        const y = H * 0.3 + (1 - Math.min(1, k * 6)) * 16; c.strokeText(b.txt, W / 2, y); c.fillText(b.txt, W / 2, y); c.globalAlpha = 1;
      }
      // joystick
      if (input && input.active && input.show) {
        c.globalAlpha = 0.35; c.strokeStyle = '#fff'; c.lineWidth = 3; c.beginPath(); c.arc(input.ox, input.oy, input.max, 0, TAU); c.stroke();
        c.globalAlpha = 0.6; c.fillStyle = '#fff'; c.beginPath(); c.arc(input.ox + input.x * input.max, input.oy + input.y * input.max, input.max * 0.38, 0, TAU); c.fill(); c.globalAlpha = 1;
      }
    }

    drawGrid(c, st, z) {
      const s = 120, x0 = Math.floor((this.cam.x - this.W / z / 2) / s) * s, x1 = this.cam.x + this.W / z / 2;
      const y0 = Math.floor((this.cam.y - this.H / z / 2) / s) * s, y1 = this.cam.y + this.H / z / 2;
      c.strokeStyle = st.grid; c.globalAlpha = 0.5; c.lineWidth = 1 / z * 1.2; c.beginPath();
      for (let x = x0; x <= x1; x += s) { c.moveTo(x, y0); c.lineTo(x, y1 + s); }
      for (let y = y0; y <= y1; y += s) { c.moveTo(x0, y); c.lineTo(x1 + s, y); }
      c.stroke(); c.globalAlpha = 1;
    }

    hpBar(c, x, y, w, f, col) {
      c.fillStyle = 'rgba(0,0,0,.55)'; c.fillRect(x - w / 2, y, w, 3);
      c.fillStyle = col; c.fillRect(x - w / 2, y, w * Math.max(0, f), 3);
    }

    drawDrop(c, d) {
      const b = Math.sin(this.t * 6 + d.x) * 1.2;
      if (d.kind === 'coin') { c.fillStyle = '#fc3'; c.shadowColor = '#fc3'; c.shadowBlur = 8; c.beginPath(); c.arc(d.x, d.y + b, 5, 0, TAU); c.fill(); c.shadowBlur = 0; c.fillStyle = '#a70'; c.beginPath(); c.arc(d.x, d.y + b, 2.4, 0, TAU); c.fill(); }
      else if (d.kind === 'heal') { c.fillStyle = '#4f7'; c.shadowColor = '#4f7'; c.shadowBlur = 10; c.fillRect(d.x - 7, d.y - 2.5 + b, 14, 5); c.fillRect(d.x - 2.5, d.y - 7 + b, 5, 14); c.shadowBlur = 0; }
      else if (d.kind === 'magnet') { c.strokeStyle = '#f5f'; c.shadowColor = '#f5f'; c.shadowBlur = 10; c.lineWidth = 4; c.beginPath(); c.arc(d.x, d.y + b, 6, Math.PI, 0); c.moveTo(d.x - 6, d.y + b); c.lineTo(d.x - 6, d.y + b + 6); c.moveTo(d.x + 6, d.y + b); c.lineTo(d.x + 6, d.y + b + 6); c.stroke(); c.shadowBlur = 0; }
      else if (d.kind === 'chest') { c.fillStyle = '#fc3'; c.shadowColor = '#fc3'; c.shadowBlur = 14; c.fillRect(d.x - 11, d.y - 8 + b, 22, 16); c.shadowBlur = 0; c.fillStyle = '#a60'; c.fillRect(d.x - 11, d.y - 2 + b, 22, 3); c.fillStyle = '#fff'; c.fillRect(d.x - 2, d.y - 3 + b, 4, 6); }
    }

    drawPlayer(c, sim) {
      const P = sim.p, s = this.shipSpr(sim.shipId);
      if (P.inv > 0 && Math.floor(this.t * 16) % 2 === 0 && P.inv < 3) c.globalAlpha = 0.45;
      c.save(); c.translate(P.x, P.y); c.rotate(P.ang + Math.PI / 2);
      c.drawImage(s.c, -s.half, -s.half, s.half * 2, s.half * 2);
      c.restore(); c.globalAlpha = 1;
      // radio de recogida muy tenue
      if (sim.state === 'running') { c.strokeStyle = 'rgba(255,255,255,.04)'; c.lineWidth = 1; c.beginPath(); c.arc(P.x, P.y, sim.st.magnet, 0, TAU); c.stroke(); }
    }

    drawBoss(c, sim, b) {
      const W = this.W, z = this.zoom, bw = Math.min(W * 0.8, 380), x = W / 2 - bw / 2, y = this.H - 46 - 22;
      c.fillStyle = 'rgba(0,0,0,.55)'; c.fillRect(x - 2, y - 2, bw + 4, 14);
      c.fillStyle = '#f44'; c.fillRect(x, y, bw * Math.max(0, b.hp / b.max), 10);
      c.fillStyle = '#fff'; c.font = '700 12px system-ui'; c.textAlign = 'center'; c.fillText(VS.t('boss.' + b.type).toUpperCase(), W / 2, y - 7);
      const sx = (b.x - this.cam.x) * z + W / 2, sy = (b.y - this.cam.y) * z + this.H / 2;
      if (sx < 20 || sx > W - 20 || sy < 20 || sy > this.H - 20) { // flecha en el borde
        const a = Math.atan2(sy - this.H / 2, sx - W / 2), m = 34, ex = U.clamp(W / 2 + Math.cos(a) * 1e4, m, W - m), ey = U.clamp(this.H / 2 + Math.sin(a) * 1e4, m + 70, this.H - m - 40);
        c.save(); c.translate(ex, ey); c.rotate(a); c.fillStyle = '#f44'; c.shadowColor = '#f44'; c.shadowBlur = 10;
        c.beginPath(); c.moveTo(14, 0); c.lineTo(-8, -10); c.lineTo(-8, 10); c.closePath(); c.fill(); c.restore();
      }
    }
  }
  const ROT = { tri: 1, cannon: 1, sentinel: 1, jugg: 1 };

  VS.Renderer = Renderer;
})(typeof window !== 'undefined' ? window : globalThis);
