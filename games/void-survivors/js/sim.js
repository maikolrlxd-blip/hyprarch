// Simulador de la partida. No toca DOM ni canvas: emite eventos que el render/audio consumen.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const U = VS.util, D = VS.data;

  const CELL = 64, GW = 44, GH = 44;
  let NID = 1;

  class Sim {
    constructor(cfg) {
      this.rand = cfg.rand || Math.random;
      this.emit = cfg.events !== false;
      this.shipId = cfg.ship;
      this.ship = D.ships[cfg.ship];
      this.stageId = cfg.stage;
      this.stage = D.stages[cfg.stage];
      this.meta = cfg.meta;
      this.viewR = cfg.viewR || 560;
      this.t = 0;
      this.state = 'running'; // running | levelup | dead | won
      this.events = [];
      this.p = { x: 0, y: 0, r: 10, hp: 1, inv: 0, ang: -Math.PI / 2, mx: 0, my: 0, hurt: 0 };
      this.weapons = [];
      this.passives = {};
      this.enemies = []; this.shots = []; this.eshots = []; this.gems = []; this.drops = []; this.rings = [];
      this.level = 1; this.xp = 0; this.xpNeed = D.xpNeed(1); this.pending = 0; this.choices = null;
      this.kills = 0; this.coins = 0; this.bossKills = 0; this.dmgTaken = 0; this.dmgDone = 0;
      this.rerolls = this.meta.rerolls; this.revives = this.meta.revives; this.adRevived = false;
      this.spawnAcc = 0;
      this.eliteT = this.stage.eliteEvery;
      this.ringT = this.stage.swarmEvery;
      this.bossIdx = 0; this.bossAlive = 0;
      this.head = new Int32Array(GW * GH);
      this.nextArr = new Int32Array(1024);
      this.qbuf = []; this.ox = 0; this.oy = 0;
      this.st = {};
      this.recompute();
      this.p.hp = this.st.maxHp;
      for (const id of this.ship.weapons) this.addWeapon(id);
    }

    ev(type, o) {
      if (!this.emit || this.events.length > 400) return;
      o = o || {};
      o.type = type;
      this.events.push(o);
    }

    // ------------------------------------------------------------------ estadísticas
    recompute() {
      const s = this.ship, m = this.meta, ps = this.passives, L = (id) => ps[id] || 0, P = D.passives;
      const st = this.st, oldMax = st.maxHp || 0;
      st.maxHp = s.hp * (1 + m.hp + P.plating.per * L('plating'));
      st.dmg = s.dmg * (1 + m.dmg + P.power.per * L('power'));
      st.cd = Math.max(0.45, 1 - s.cd - P.overclock.per * L('overclock'));
      st.speed = s.speed * (1 + m.speed + P.thrusters.per * L('thrusters'));
      st.magnet = 85 * (1 + s.magnet + m.magnet + P.magnet.per * L('magnet'));
      st.armor = s.armor + m.armor + L('barrier');
      st.xp = 1 + m.xp + P.scholar.per * L('scholar');
      st.coin = 1 + m.coin;
      st.regen = m.regen + P.regen.per * L('regen');
      st.area = 1 + s.area + P.lens.per * L('lens');
      st.pspeed = 1 + 0.08 * L('lens');
      st.crit = s.crit + P.fortune.per * L('fortune');
      st.luck = L('fortune');
      if (oldMax && this.p) this.p.hp += st.maxHp - oldMax; // al subir HP máx se cura la diferencia
    }

    // ------------------------------------------------------------------ cuadrícula espacial
    buildGrid() {
      const p = this.p, E = this.enemies;
      this.ox = p.x - (GW * CELL) / 2;
      this.oy = p.y - (GH * CELL) / 2;
      this.head.fill(-1);
      if (this.nextArr.length < E.length) this.nextArr = new Int32Array(E.length * 2);
      for (let i = 0; i < E.length; i++) {
        const e = E[i];
        if (e.dead) continue;
        const cx = Math.floor((e.x - this.ox) / CELL), cy = Math.floor((e.y - this.oy) / CELL);
        if (cx < 0 || cy < 0 || cx >= GW || cy >= GH) continue;
        const c = cx + cy * GW;
        this.nextArr[i] = this.head[c];
        this.head[c] = i;
      }
      this.gridN = E.length;
    }

    // Rellena this.qbuf con los enemigos cuyo círculo toca (x,y,r). Devuelve cuántos.
    gather(x, y, r) {
      const buf = this.qbuf, E = this.enemies;
      let n = 0;
      const x0 = Math.max(0, Math.floor((x - r - 40 - this.ox) / CELL)), x1 = Math.min(GW - 1, Math.floor((x + r + 40 - this.ox) / CELL));
      const y0 = Math.max(0, Math.floor((y - r - 40 - this.oy) / CELL)), y1 = Math.min(GH - 1, Math.floor((y + r + 40 - this.oy) / CELL));
      for (let cy = y0; cy <= y1; cy++) {
        for (let cx = x0; cx <= x1; cx++) {
          for (let i = this.head[cx + cy * GW]; i !== -1; i = this.nextArr[i]) {
            const e = E[i];
            if (e.dead) continue;
            const dx = e.x - x, dy = e.y - y, rr = r + e.r;
            if (dx * dx + dy * dy < rr * rr) buf[n++] = e;
          }
        }
      }
      return n;
    }

    // Los k enemigos vivos más cercanos al jugador dentro de range.
    nearest(k, range, from) {
      const out = [], d2 = [], E = this.enemies, fx = from ? from.x : this.p.x, fy = from ? from.y : this.p.y;
      const lim = range * range;
      for (let i = 0; i < E.length; i++) {
        const e = E[i];
        if (e.dead) continue;
        const dx = e.x - fx, dy = e.y - fy, raw = dx * dx + dy * dy;
        if (raw > lim) continue;
        const d = raw * (e.boss ? 0.12 : e.elite ? 0.5 : 1); // jefes y élites tienen prioridad de puntería
        let j = out.length;
        if (j < k) { out.push(e); d2.push(d); } else if (d < d2[j - 1]) { j--; out[j] = e; d2[j] = d; } else continue;
        while (j > 0 && d2[j - 1] > d2[j]) {
          [d2[j - 1], d2[j]] = [d2[j], d2[j - 1]];
          [out[j - 1], out[j]] = [out[j], out[j - 1]];
          j--;
        }
      }
      return out;
    }

    // ------------------------------------------------------------------ bucle principal
    update(dt, inp) {
      if (this.state !== 'running') return;
      this.t += dt;
      this.movePlayer(dt, inp);
      this.buildGrid();
      this.director(dt);
      this.updateWeapons(dt);
      this.updateShots(dt);
      this.updateEnemies(dt);
      this.updateEShots(dt);
      this.updatePickups(dt);
      this.updateRings(dt);
      this.sweep();
      if (this.p.hp <= 0 && this.state === 'running') this.die();
      if (this.pending > 0 && this.state === 'running') this.openChoices();
    }

    movePlayer(dt, inp) {
      const p = this.p, st = this.st;
      let ix = inp ? inp.x : 0, iy = inp ? inp.y : 0;
      const mag = Math.hypot(ix, iy);
      if (mag > 1) { ix /= mag; iy /= mag; }
      p.mx = ix; p.my = iy;
      p.x += ix * st.speed * dt;
      p.y += iy * st.speed * dt;
      if (mag > 0.1) {
        let da = Math.atan2(iy, ix) - p.ang;
        while (da > Math.PI) da -= 2 * Math.PI;
        while (da < -Math.PI) da += 2 * Math.PI;
        p.ang += da * Math.min(1, dt * 12);
      }
      p.inv = Math.max(0, p.inv - dt);
      p.hurt = Math.max(0, p.hurt - dt);
      if (st.regen > 0 && p.hp < st.maxHp) p.hp = Math.min(st.maxHp, p.hp + st.regen * dt);
    }

    // ------------------------------------------------------------------ director de oleadas
    scale() {
      const tm = this.t / 60, s = this.stage;
      return {
        hp: (1 + D.tune.hpA * tm + D.tune.hpB * tm * tm) * s.hpMul,
        dmg: (1 + 0.05 * tm) * s.dmgMul * D.tune.dmg,
        spd: Math.min(0.3, 0.025 * tm) + s.spdAdd,
      };
    }

    pickType() {
      const t = this.t, w = this.stage.w;
      let tot = 0;
      const cand = [];
      for (const id in D.enemies) {
        const d = D.enemies[id];
        if (d.boss || d.minT > t) continue;
        let wt = d.w * (w[id] || 1);
        if (id === 'swarmer') wt *= Math.max(0.35, 1 - t / 500);
        cand.push([id, wt]);
        tot += wt;
      }
      let r = this.rand() * tot;
      for (const [id, wt] of cand) { r -= wt; if (r <= 0) return id; }
      return 'grunt';
    }

    ringPos(rad) {
      const a = this.rand() * Math.PI * 2, r = rad || this.viewR;
      return { x: this.p.x + Math.cos(a) * r, y: this.p.y + Math.sin(a) * r, a };
    }

    director(dt) {
      const st = this.stage, t = this.t;
      const rate = (st.rate0 + st.rateGrow * (t / 60)) * (this.bossAlive ? 0.55 : 1);
      this.spawnAcc += rate * dt;
      while (this.spawnAcc >= 1) {
        const type = this.pickType();
        if (this.enemies.length >= st.cap) { this.spawnAcc = Math.min(this.spawnAcc, 2); break; }
        if (type === 'swarmer') {
          const n = 3 + Math.floor(this.rand() * 4), c = this.ringPos();
          for (let i = 0; i < n; i++) this.spawn(type, c.x + (this.rand() - 0.5) * 60, c.y + (this.rand() - 0.5) * 60);
          this.spawnAcc -= n;
        } else {
          const c = this.ringPos();
          this.spawn(type, c.x, c.y);
          this.spawnAcc -= 1;
        }
      }
      if (t >= st.eliteStart) {
        this.eliteT -= dt;
        if (this.eliteT <= 0) {
          this.eliteT = st.eliteEvery;
          let type = this.pickType();
          if (type === 'swarmer') type = 'grunt';
          const c = this.ringPos();
          this.spawn(type, c.x, c.y, { elite: true });
          this.ev('warn', { key: 'elite' });
        }
      }
      if (t >= st.swarmStart) {
        this.ringT -= dt;
        if (this.ringT <= 0) {
          this.ringT = st.swarmEvery;
          const n = 20 + Math.floor(t / 30), rad = this.viewR * 0.95;
          for (let i = 0; i < n; i++) {
            const a = (i / n) * Math.PI * 2;
            this.spawn('swarmer', this.p.x + Math.cos(a) * rad, this.p.y + Math.sin(a) * rad);
          }
          this.ev('warn', { key: 'swarm' });
        }
      }
      const b = st.bosses[this.bossIdx];
      if (b && t >= b.t) {
        this.bossIdx++;
        const c = this.ringPos();
        this.spawn(b.type, c.x, c.y, { final: !!b.final });
        this.ev('boss', { id: b.type, final: !!b.final });
      }
    }

    spawn(type, x, y, o) {
      o = o || {};
      const def = D.enemies[type], m = this.scale();
      const elite = !!o.elite, boss = !!def.boss;
      const hpMul = boss ? m.hp * 0.55 + 0.45 : m.hp;
      const hp = def.hp * hpMul * (elite ? 6 : 1);
      const e = {
        id: NID++, type, x, y, r: def.r * (elite ? 1.45 : 1), hp, max: hp,
        speed: def.speed * (1 + m.spd) * (elite ? 0.9 : 1), dmg: def.dmg * m.dmg * (elite ? 1.3 : 1),
        xp: def.xp * (elite ? 6 : 1), beh: def.beh, flash: 0, kx: 0, ky: 0, slow: 0, orbitCd: 0,
        cool: 1 + this.rand() * 2, fire: 1 + this.rand() * 2, st: 0, timer: 0, dx: 0, dy: 0, ph: 0,
        elite, boss, final: !!o.final, dead: false, split: !!def.split, spawnT: 0,
      };
      if (boss) { this.bossAlive++; e.timer = 2; e.cool = 3; }
      this.enemies.push(e);
      return e;
    }

    // ------------------------------------------------------------------ armas
    addWeapon(id) {
      const w = { id, level: 1, cd: 0.2, angle: 0, tick: 0, blades: [] };
      this.weapons.push(w);
      return w;
    }

    updateWeapons(dt) {
      const st = this.st;
      for (const w of this.weapons) {
        const def = D.weapons[w.id], L = def.levels[w.level - 1];
        switch (def.kind) {
          case 'shot': this.wPulse(w, L, dt, st); break;
          case 'orbit': this.wOrbit(w, L, dt, st); break;
          case 'chain': this.wChain(w, L, dt, st); break;
          case 'missile': this.wMissile(w, L, dt, st); break;
          case 'nova': this.wNova(w, L, dt, st); break;
          case 'aura': this.wAura(w, L, dt, st); break;
        }
      }
    }

    wPulse(w, L, dt, st) {
      w.cd -= dt;
      if (w.cd > 0) return;
      const tg = this.nearest(L.n, 520);
      if (!tg.length) { w.cd = 0.1; return; }
      w.cd = L.cd * st.cd;
      const p = this.p;
      for (let k = 0; k < L.n; k++) {
        const e = tg[k % tg.length];
        let a = Math.atan2(e.y - p.y, e.x - p.x);
        if (tg.length < L.n) a += (k - (L.n - 1) / 2) * 0.14;
        const sp = L.spd * st.pspeed;
        this.shots.push({ x: p.x, y: p.y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, r: 5, dmg: L.dmg * st.dmg, pierce: L.pierce, life: 1.1, hits: [], kind: 'pulse', color: '#6ff' });
      }
      this.ev('shoot', { k: 'pulse' });
    }

    wOrbit(w, L, dt, st) {
      w.angle += L.spin * dt;
      const R = L.R * st.area, p = this.p, sz = 11 * Math.sqrt(st.area);
      w.blades.length = L.n;
      for (let i = 0; i < L.n; i++) {
        const a = w.angle + (i / L.n) * Math.PI * 2, bx = p.x + Math.cos(a) * R, by = p.y + Math.sin(a) * R;
        w.blades[i] = { x: bx, y: by, r: sz, a };
        const n = this.gather(bx, by, sz);
        for (let j = 0; j < n; j++) {
          const e = this.qbuf[j];
          if (e.orbitCd > 0) continue;
          e.orbitCd = 0.4;
          const kx = Math.cos(a + Math.PI / 2) * 60, ky = Math.sin(a + Math.PI / 2) * 60;
          this.damage(e, L.dmg * st.dmg, kx, ky);
        }
      }
    }

    wChain(w, L, dt, st) {
      w.cd -= dt;
      if (w.cd > 0) return;
      const first = this.nearest(1, 320);
      if (!first.length) { w.cd = 0.1; return; }
      w.cd = L.cd * st.cd;
      const visited = [first[0].id], pts = [{ x: this.p.x, y: this.p.y }];
      let cur = first[0];
      for (let j = 0; j <= L.jumps && cur; j++) {
        pts.push({ x: cur.x, y: cur.y });
        this.damage(cur, L.dmg * st.dmg * (1 - j * 0.04), 0, 0);
        let next = null, nd = Infinity;
        const n = this.gather(cur.x, cur.y, L.range * st.area);
        for (let k = 0; k < n; k++) {
          const e = this.qbuf[k];
          if (visited.includes(e.id)) continue;
          const d = (e.x - cur.x) ** 2 + (e.y - cur.y) ** 2;
          if (d < nd) { nd = d; next = e; }
        }
        if (next) visited.push(next.id);
        cur = next;
      }
      this.ev('bolt', { pts });
    }

    wMissile(w, L, dt, st) {
      w.cd -= dt;
      if (w.cd > 0) return;
      if (!this.enemies.length) { w.cd = 0.2; return; }
      w.cd = L.cd * st.cd;
      const tg = this.nearest(L.n * 2, 600), p = this.p;
      if (!tg.length) { w.cd = 0.2; return; }
      for (let k = 0; k < L.n; k++) {
        const a = p.ang + Math.PI + (k - (L.n - 1) / 2) * 0.6 + (this.rand() - 0.5) * 0.4;
        this.shots.push({ x: p.x, y: p.y, vx: Math.cos(a) * 160, vy: Math.sin(a) * 160, r: 6, dmg: L.dmg * st.dmg, pierce: 0, life: 2.8, hits: [], kind: 'missile', aoe: L.aoe * st.area, target: tg[k % tg.length], color: '#f96', ang: a, spd: 250 * st.pspeed });
      }
      this.ev('shoot', { k: 'missile' });
    }

    wNova(w, L, dt, st) {
      w.cd -= dt;
      if (w.cd > 0) return;
      if (!this.enemies.length) { w.cd = 0.3; return; }
      w.cd = L.cd * st.cd;
      this.rings.push({ x: this.p.x, y: this.p.y, r: 8, maxR: L.R * st.area, dmg: L.dmg * st.dmg, knock: L.knock, hit: [], color: '#f6f', cancel: w.level >= 4 });
      this.ev('nova', { x: this.p.x, y: this.p.y });
    }

    wAura(w, L, dt, st) {
      const R = L.R * st.area, p = this.p;
      w.R = R;
      w.tick -= dt;
      const doTick = w.tick <= 0;
      if (doTick) w.tick = L.tick;
      const n = this.gather(p.x, p.y, R);
      for (let i = 0; i < n; i++) {
        const e = this.qbuf[i];
        e.slow = Math.max(e.slow, 0.15);
        if (doTick) this.damage(e, L.dmg * st.dmg, 0, 0, false, true);
      }
    }

    updateRings(dt) {
      const R = this.rings;
      for (let i = R.length - 1; i >= 0; i--) {
        const r = R[i];
        r.r += (r.maxR / 0.55) * dt;
        const n = this.gather(r.x, r.y, r.r + 12);
        for (let j = 0; j < n; j++) {
          const e = this.qbuf[j];
          if (r.hit.includes(e.id)) continue;
          const dx = e.x - r.x, dy = e.y - r.y, d = Math.hypot(dx, dy) || 1;
          if (d + e.r < r.r - 18) continue; // ya quedó dentro del anillo
          r.hit.push(e.id);
          this.damage(e, r.dmg, (dx / d) * r.knock, (dy / d) * r.knock);
        }
        if (r.cancel) {
          for (const b of this.eshots) { if (Math.abs(Math.hypot(b.x - r.x, b.y - r.y) - r.r) < 20) b.life = 0; }
        }
        if (r.r >= r.maxR) R.splice(i, 1);
      }
    }

    // ------------------------------------------------------------------ proyectiles
    updateShots(dt) {
      const S = this.shots;
      for (let i = S.length - 1; i >= 0; i--) {
        const s = S[i];
        s.life -= dt;
        if (s.kind === 'missile') {
          if (!s.target || s.target.dead) { const t = this.nearest(1, 450, s); s.target = t[0] || null; }
          if (s.target) {
            let da = Math.atan2(s.target.y - s.y, s.target.x - s.x) - s.ang;
            while (da > Math.PI) da -= 2 * Math.PI;
            while (da < -Math.PI) da += 2 * Math.PI;
            s.ang += U.clamp(da, -6 * dt, 6 * dt);
          }
          const sp = Math.min(s.spd, Math.hypot(s.vx, s.vy) + 500 * dt);
          s.vx = Math.cos(s.ang) * sp; s.vy = Math.sin(s.ang) * sp;
        }
        s.x += s.vx * dt; s.y += s.vy * dt;
        let remove = s.life <= 0;
        if (!remove) {
          const n = this.gather(s.x, s.y, s.r);
          for (let j = 0; j < n; j++) {
            const e = this.qbuf[j];
            if (s.hits.includes(e.id)) continue;
            if (s.kind === 'missile') { this.explode(s); remove = true; break; }
            s.hits.push(e.id);
            this.damage(e, s.dmg, s.vx * 0.08, s.vy * 0.08);
            if (s.pierce-- <= 0) { remove = true; break; }
          }
        } else if (s.kind === 'missile') this.explode(s);
        if (remove) { S[i] = S[S.length - 1]; S.pop(); }
      }
    }

    explode(s) {
      const n = this.gather(s.x, s.y, s.aoe);
      const list = this.qbuf.slice(0, n);
      for (const e of list) {
        const dx = e.x - s.x, dy = e.y - s.y, d = Math.hypot(dx, dy) || 1;
        this.damage(e, s.dmg, (dx / d) * 120, (dy / d) * 120);
      }
      this.ev('boom', { x: s.x, y: s.y, r: s.aoe, color: '#fa6' });
    }

    updateEShots(dt) {
      const B = this.eshots, p = this.p;
      for (let i = B.length - 1; i >= 0; i--) {
        const b = B[i];
        b.x += b.vx * dt; b.y += b.vy * dt; b.life -= dt;
        let remove = b.life <= 0;
        if (!remove && (b.x - p.x) ** 2 + (b.y - p.y) ** 2 < (b.r + p.r * 0.8) ** 2) { this.hurt(b.dmg); remove = true; }
        if (remove) { B[i] = B[B.length - 1]; B.pop(); }
      }
    }

    shoot(e, ang, speed, dmg, r) {
      this.eshots.push({ x: e.x, y: e.y, vx: Math.cos(ang) * speed, vy: Math.sin(ang) * speed, r: r || 5, dmg, life: 6 });
    }

    // ------------------------------------------------------------------ enemigos
    updateEnemies(dt) {
      const p = this.p, E = this.enemies;
      const far = this.viewR * 2.2;
      for (let i = 0; i < E.length; i++) {
        const e = E[i];
        if (e.dead) continue;
        let dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;
        if (!e.boss && d > far) { const c = this.ringPos(); e.x = c.x; e.y = c.y; continue; }
        e.flash = Math.max(0, e.flash - dt); e.orbitCd -= dt; e.slow -= dt; e.spawnT += dt;
        const nx = dx / d, ny = dy / d;
        let mx = nx, my = ny, mul = e.slow > 0 ? 0.65 : 1;
        switch (e.beh) {
          case 'dash':
            if (e.st === 0) { e.cool -= dt; if (e.cool <= 0 && d < 280) { e.st = 1; e.timer = 0.55; e.dx = nx; e.dy = ny; } }
            else if (e.st === 1) { mul = 0; e.timer -= dt; if (e.timer <= 0) { e.st = 2; e.timer = 0.4; } }
            else { mx = e.dx; my = e.dy; mul = 4.6; e.timer -= dt; if (e.timer <= 0) { e.st = 0; e.cool = 2.4; } }
            break;
          case 'shoot':
            e.fire -= dt;
            if (d < 170) { mx = -nx; my = -ny; mul *= 0.9; } else if (d < 240) { mx = -ny; my = nx; mul *= 0.6; }
            if (e.fire <= 0 && d < 430) { e.fire = 2.6 + this.rand(); this.shoot(e, Math.atan2(dy, dx), 175, e.dmg, 5); }
            break;
          case 'hive':
            if (d < 120) mul = 0.1;
            e.timer -= dt;
            if (e.timer <= 0) {
              e.timer = 2.8 - (e.hp < e.max * 0.5 ? 0.8 : 0);
              for (let k = 0; k < 4; k++) this.spawn('swarmer', e.x + (this.rand() - 0.5) * 60, e.y + (this.rand() - 0.5) * 60);
              this.ev('boom', { x: e.x, y: e.y, r: 50, color: '#8f6' });
            }
            break;
          case 'sentinel':
            if (d < 260) { mx = -nx; my = -ny; mul *= 0.8; } else if (d < 330) { mx = -ny; my = nx; mul *= 0.7; }
            e.timer -= dt; e.cool -= dt;
            if (e.timer <= 0) { // anillo de balas
              e.timer = e.hp < e.max * 0.5 ? 1.9 : 2.5; e.ph++;
              const n = 14, off = (e.ph % 2) * (Math.PI / n);
              for (let k = 0; k < n; k++) this.shoot(e, off + (k / n) * Math.PI * 2, 150, e.dmg * 0.8, 6);
            }
            if (e.cool <= 0) { // ráfaga dirigida
              e.cool = 1.7; const a = Math.atan2(dy, dx);
              for (let k = -1; k <= 1; k++) this.shoot(e, a + k * 0.16, 230, e.dmg, 5);
            }
            break;
          case 'jugg':
            if (e.st === 0) { e.cool -= dt; if (e.cool <= 0) { e.st = 1; e.timer = 0.75; e.dx = nx; e.dy = ny; } }
            else if (e.st === 1) { mul = 0.1; e.timer -= dt; e.dx = nx; e.dy = ny; if (e.timer <= 0) { e.st = 2; e.timer = 0.6; } }
            else {
              mx = e.dx; my = e.dy; mul = 11; e.timer -= dt;
              if (e.timer <= 0) {
                e.st = 0; e.cool = e.hp < e.max * 0.5 ? 2.2 : 3.4;
                if (e.hp < e.max * 0.5) for (let k = 0; k < 12; k++) this.shoot(e, (k / 12) * Math.PI * 2, 170, e.dmg * 0.6, 6);
              }
            }
            break;
        }
        e.kx *= Math.exp(-7 * dt); e.ky *= Math.exp(-7 * dt);
        const kn = e.boss ? 0.12 : 1;
        e.x += (mx * e.speed * mul + e.kx * kn) * dt;
        e.y += (my * e.speed * mul + e.ky * kn) * dt;
        // contacto con el jugador
        const cr = p.r * 0.8 + e.r * 0.85;
        if (d < cr + 6 && p.inv <= 0) { const dd = Math.hypot(p.x - e.x, p.y - e.y); if (dd < cr) this.hurt(e.dmg); }
      }
      // separación suave entre enemigos
      for (let i = 0; i < E.length; i++) {
        const e = E[i];
        if (e.dead || e.boss) continue;
        const n = this.gather(e.x, e.y, e.r);
        for (let j = 0; j < n; j++) {
          const o = this.qbuf[j];
          if (o === e) continue;
          let dx = e.x - o.x, dy = e.y - o.y, d = Math.hypot(dx, dy);
          const min = e.r + o.r;
          if (d >= min) continue;
          if (d < 0.01) { dx = this.rand() - 0.5; dy = this.rand() - 0.5; d = Math.hypot(dx, dy) || 1; }
          const push = (min - d) * (o.boss ? 0.6 : 0.3);
          e.x += (dx / d) * push; e.y += (dy / d) * push;
        }
      }
    }

    // ------------------------------------------------------------------ daño y muertes
    damage(e, dmg, kx, ky, noCrit, quiet) {
      if (e.dead) return;
      let crit = false;
      if (!noCrit && this.rand() < this.st.crit) { dmg *= 2; crit = true; }
      e.hp -= dmg; e.flash = 0.09; e.kx += kx || 0; e.ky += ky || 0;
      this.dmgDone += dmg;
      if (!quiet) this.ev('dmg', { x: e.x, y: e.y - e.r, v: dmg, crit });
      if (e.hp <= 0) this.kill(e);
    }

    kill(e) {
      e.dead = true;
      this.kills++;
      const m = this.stage.coinMul * this.st.coin;
      this.ev('kill', { x: e.x, y: e.y, r: e.r, color: D.enemies[e.type].color, boss: e.boss, elite: e.elite });
      this.gems.push({ x: e.x, y: e.y, v: e.xp, pull: false, r: e.xp >= 10 ? 7 : e.xp >= 3 ? 5.5 : 4 });
      if (this.gems.length > 260) { const g0 = this.gems.shift(); this.gems[this.gems.length - 1].v += g0.v; }
      if (e.split) for (let k = 0; k < 2; k++) this.spawn('swarmer', e.x + (this.rand() - 0.5) * 24, e.y + (this.rand() - 0.5) * 24);
      const luck = 1 + this.st.luck * 0.15;
      if (e.boss) {
        this.bossAlive--; this.bossKills++;
        for (let k = 0; k < 14; k++) this.drops.push({ kind: 'coin', x: e.x + (this.rand() - 0.5) * 90, y: e.y + (this.rand() - 0.5) * 90, v: Math.max(1, Math.round(m * 2)) });
        if (e.final) { this.win(); return; }
        this.drops.push({ kind: 'chest', x: e.x, y: e.y });
        this.drops.push({ kind: 'heal', x: e.x + 20, y: e.y });
        this.ev('shake', { v: 0.6 });
      } else if (e.elite) {
        this.drops.push({ kind: 'chest', x: e.x, y: e.y });
        for (let k = 0; k < 4; k++) this.drops.push({ kind: 'coin', x: e.x + (this.rand() - 0.5) * 40, y: e.y + (this.rand() - 0.5) * 40, v: Math.max(1, Math.round(m)) });
      } else {
        const r = this.rand();
        if (r < 0.11 * luck) this.drops.push({ kind: 'coin', x: e.x, y: e.y, v: Math.max(1, Math.round(m)) });
        else if (r < 0.11 * luck + 0.006) this.drops.push({ kind: 'heal', x: e.x, y: e.y });
        else if (r < 0.11 * luck + 0.009) this.drops.push({ kind: 'magnet', x: e.x, y: e.y });
      }
    }

    hurt(dmg) {
      const p = this.p;
      if (p.inv > 0 || this.state !== 'running') return;
      const d = Math.max(dmg * 0.25, dmg - this.st.armor);
      p.hp -= d; p.inv = 0.55; p.hurt = 0.25; this.dmgTaken += d;
      this.ev('hurt', { v: d });
    }

    die() {
      if (this.revives > 0) { this.revives--; this.revive(0.5); this.ev('revive', {}); return; }
      this.state = 'dead';
      this.ev('dead', {});
    }

    revive(frac) {
      const p = this.p;
      p.hp = this.st.maxHp * frac; p.inv = 3;
      this.state = 'running';
      this.eshots.length = 0;
      this.rings.push({ x: p.x, y: p.y, r: 8, maxR: 320, dmg: 9999, knock: 500, hit: [], color: '#fff', cancel: true });
    }

    adRevive() {
      if (this.state !== 'dead' || this.adRevived) return false;
      this.adRevived = true;
      this.revive(0.6);
      this.ev('revive', {});
      return true;
    }

    win() {
      this.state = 'won';
      for (const e of this.enemies) if (!e.dead && !e.boss) e.dead = true;
      this.ev('won', {});
    }

    // ------------------------------------------------------------------ recogidas
    updatePickups(dt) {
      const p = this.p, st = this.st;
      const G = this.gems;
      for (let i = G.length - 1; i >= 0; i--) {
        const gm = G[i];
        const dx = p.x - gm.x, dy = p.y - gm.y, d = Math.hypot(dx, dy) || 1;
        if (d < st.magnet) gm.pull = true;
        if (gm.pull) {
          const sp = 260 + 700 * Math.max(0, 1 - d / 400);
          gm.x += (dx / d) * sp * dt; gm.y += (dy / d) * sp * dt;
        }
        if (d < p.r + gm.r + 5) {
          this.addXp(gm.v * st.xp);
          this.ev('gem', { v: gm.v });
          G[i] = G[G.length - 1]; G.pop();
        }
      }
      const Dr = this.drops;
      for (let i = Dr.length - 1; i >= 0; i--) {
        const dr = Dr[i];
        const dx = p.x - dr.x, dy = p.y - dr.y, d = Math.hypot(dx, dy) || 1;
        const rng = dr.kind === 'coin' ? st.magnet : 28;
        if (dr.pull || d < rng) { const sp = 300; dr.x += (dx / d) * sp * dt; dr.y += (dy / d) * sp * dt; }
        if (d < p.r + 14) {
          if (dr.kind === 'coin') { this.coins += dr.v; this.ev('coin', { v: dr.v }); }
          else if (dr.kind === 'heal') { p.hp = Math.min(st.maxHp, p.hp + st.maxHp * 0.3); this.ev('heal', {}); }
          else if (dr.kind === 'magnet') { for (const gm of this.gems) gm.pull = true; for (const o of Dr) o.pull = true; this.ev('magnet', {}); }
          else if (dr.kind === 'chest') { this.pending++; this.ev('chest', {}); }
          Dr[i] = Dr[Dr.length - 1]; Dr.pop();
        }
      }
    }

    addXp(v) {
      this.xp += v;
      while (this.xp >= this.xpNeed) {
        this.xp -= this.xpNeed;
        this.level++;
        this.xpNeed = D.xpNeed(this.level);
        this.pending++;
        this.ev('levelup', { level: this.level });
      }
    }

    sweep() {
      const E = this.enemies;
      let w = 0;
      for (let i = 0; i < E.length; i++) if (!E[i].dead) E[w++] = E[i];
      E.length = w;
    }

    // ------------------------------------------------------------------ subida de nivel
    makeChoices() {
      const opts = [];
      for (const w of this.weapons) if (w.level < D.weapons[w.id].max) opts.push({ kind: 'weapon', id: w.id, level: w.level + 1, wt: 3 });
      if (this.weapons.length < D.MAX_WEAPONS) {
        for (const id in D.weapons) if (!this.weapons.some((w) => w.id === id)) opts.push({ kind: 'weapon', id, level: 1, wt: 2.4 });
      }
      const pc = Object.keys(this.passives).length;
      for (const id in this.passives) if (this.passives[id] < D.passives[id].max) opts.push({ kind: 'passive', id, level: this.passives[id] + 1, wt: 2 });
      if (pc < D.MAX_PASSIVES) for (const id in D.passives) if (!(id in this.passives)) opts.push({ kind: 'passive', id, level: 1, wt: 1.6 });
      const n = 3 + this.meta.choice, out = [];
      while (out.length < n && opts.length) {
        let tot = 0;
        for (const o of opts) tot += o.wt;
        let r = this.rand() * tot, k = 0;
        for (; k < opts.length - 1; k++) { r -= opts[k].wt; if (r <= 0) break; }
        out.push(opts.splice(k, 1)[0]);
      }
      if (!out.length) { out.push({ kind: 'heal', level: 0 }, { kind: 'coins', level: 0 }); }
      return out;
    }

    openChoices() {
      this.state = 'levelup';
      this.choices = this.makeChoices();
      this.ev('choices', {});
    }

    reroll() {
      if (this.state !== 'levelup' || this.rerolls <= 0) return false;
      this.rerolls--;
      this.choices = this.makeChoices();
      return true;
    }

    choose(i) {
      if (this.state !== 'levelup') return;
      const c = this.choices[i];
      if (!c) return;
      if (c.kind === 'weapon') {
        const w = this.weapons.find((x) => x.id === c.id);
        if (w) w.level++; else this.addWeapon(c.id);
      } else if (c.kind === 'passive') {
        this.passives[c.id] = (this.passives[c.id] || 0) + 1;
        this.recompute();
      } else if (c.kind === 'heal') this.p.hp = Math.min(this.st.maxHp, this.p.hp + this.st.maxHp * 0.5);
      else if (c.kind === 'coins') this.coins += Math.round(50 * this.stage.coinMul);
      this.pending--;
      this.choices = null;
      this.state = 'running';
      this.p.inv = Math.max(this.p.inv, 0.5);
    }

    result() {
      return {
        won: this.state === 'won', time: this.t, kills: this.kills, coins: this.coins, level: this.level,
        bossKills: this.bossKills, stage: this.stageId, ship: this.shipId,
        maxWeaponLevel: this.weapons.reduce((m, w) => Math.max(m, w.level), 0),
      };
    }
  }

  VS.Sim = Sim;
})(typeof window !== 'undefined' ? window : globalThis);
