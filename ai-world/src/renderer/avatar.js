import * as THREE from 'three';
import { glowTexture, haloSprite } from './fx.js';

const WALK_SPEED = 1.6;
const ARRIVE_DIST = 0.15;
const ACCESSORY_BY_ID = { luna: 'ears', rex: 'antenna', sage: 'halo', nova: 'horns' };
const ACCESSORIES = ['ears', 'antenna', 'halo', 'horns', 'sprout'];
const MAX_SPARKS = 12;

function textSprite(draw, w, h, scale) {
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  draw(canvas.getContext('2d'), w, h);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false }));
  sprite.scale.set(scale, scale * h / w, 1);
  sprite.renderOrder = 10;
  return sprite;
}

function wrapLines(ctx, text, maxW) {
  const words = text.split(/\s+/); const lines = []; let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t;
  }
  if (cur) lines.push(cur);
  return lines;
}

function hashId(id) { let h = 0; for (const c of id) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; }

function disposeSprite(s) { s.material.map?.dispose(); s.material.dispose(); }

export class Avatar {
  constructor({ id, name, color }) {
    this.id = id; this.name = name; this.color = color;
    this.group = new THREE.Group();
    const base = new THREE.Color(color);
    const light = base.clone().lerp(new THREE.Color(0xffffff), 0.55);
    const shoe = base.clone().multiplyScalar(0.4);
    const mat = new THREE.MeshStandardMaterial({ color: base, emissive: base, emissiveIntensity: 0.22, roughness: 0.45, metalness: 0.05 });
    const lightMat = new THREE.MeshStandardMaterial({ color: light, emissive: light, emissiveIntensity: 0.15, roughness: 0.6 });
    const dark = new THREE.MeshStandardMaterial({ color: shoe, roughness: 0.5 });
    const ink = new THREE.MeshBasicMaterial({ color: 0x15101f });
    const white = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const blush = new THREE.MeshBasicMaterial({ color: 0xff7aa8, transparent: true, opacity: 0.55 });

    // aura bajo los pies
    this.aura = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 1.9), new THREE.MeshBasicMaterial({
      map: glowTexture(), color: base, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.aura.rotation.x = -Math.PI / 2; this.aura.position.y = 0.04; this.group.add(this.aura);
    this.ring = new THREE.Mesh(new THREE.RingGeometry(0.42, 0.5, 40), new THREE.MeshBasicMaterial({
      color: light, transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    this.ring.rotation.x = -Math.PI / 2; this.ring.position.y = 0.05; this.group.add(this.ring);

    this.body = new THREE.Group(); // todo lo que rebota/baila
    this.group.add(this.body);
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.22, 0.4, 6, 14), mat);
    torso.position.y = 0.62; torso.castShadow = true; this.body.add(torso);
    const belly = new THREE.Mesh(new THREE.SphereGeometry(0.15, 14, 10), lightMat);
    belly.scale.set(0.95, 1.2, 0.35); belly.position.set(0, 0.6, 0.2); this.body.add(belly);

    this.head = new THREE.Group(); this.head.position.y = 1.18; this.body.add(this.head);
    const skull = new THREE.Mesh(new THREE.SphereGeometry(0.24, 24, 18), mat); skull.castShadow = true; this.head.add(skull);
    this.eyes = [-1, 1].map(s => {
      const eye = new THREE.Group(); eye.position.set(0.095 * s, 0.03, 0.2); this.head.add(eye);
      const ball = new THREE.Mesh(new THREE.SphereGeometry(0.058, 14, 10), white); ball.scale.z = 0.6; eye.add(ball);
      const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.034, 12, 8), ink); pupil.position.z = 0.028; eye.add(pupil);
      const shine = new THREE.Mesh(new THREE.SphereGeometry(0.011, 6, 6), white); shine.position.set(0.012, 0.014, 0.058); eye.add(shine);
      return eye;
    });
    this.mouth = new THREE.Mesh(new THREE.SphereGeometry(0.034, 12, 8), ink);
    this.mouth.scale.set(1, 0.35, 0.5); this.mouth.position.set(0, -0.075, 0.225); this.head.add(this.mouth);
    for (const s of [-1, 1]) { const c = new THREE.Mesh(new THREE.SphereGeometry(0.04, 10, 8), blush); c.scale.set(1, 0.6, 0.3); c.position.set(0.15 * s, -0.04, 0.18); c.rotation.y = 0.5 * s; this.head.add(c); }
    this.#accessory(ACCESSORY_BY_ID[id] || ACCESSORIES[hashId(id) % ACCESSORIES.length], mat, lightMat, base, light);

    this.arms = [-1, 1].map(s => {
      const pivot = new THREE.Group(); pivot.position.set(0.3 * s, 0.9, 0);
      const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.32, 4, 10), mat);
      arm.position.y = -0.2; arm.castShadow = true; pivot.add(arm);
      const hand = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 8), lightMat); hand.position.y = -0.4; pivot.add(hand);
      this.body.add(pivot); return pivot;
    });
    this.legs = [-1, 1].map(s => {
      const pivot = new THREE.Group(); pivot.position.set(0.1 * s, 0.34, 0);
      const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.07, 0.22, 4, 10), dark);
      leg.position.y = -0.14; leg.castShadow = true; pivot.add(leg);
      const foot = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), dark); foot.scale.set(1, 0.6, 1.4); foot.position.set(0, -0.3, 0.04); pivot.add(foot);
      this.body.add(pivot); return pivot;
    });

    this.label = textSprite((c, w, h) => {
      c.font = 'bold 44px ui-rounded, system-ui, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
      const grad = c.createLinearGradient(0, 0, w, 0); grad.addColorStop(0, '#12081f'); grad.addColorStop(1, '#241046');
      c.fillStyle = grad; c.beginPath(); c.roundRect(10, 8, w - 20, h - 16, 28); c.fill();
      c.lineWidth = 4; c.strokeStyle = color; c.shadowColor = color; c.shadowBlur = 14; c.stroke();
      c.shadowBlur = 0; c.fillStyle = '#fff'; c.fillText(name, w / 2, h / 2 + 2);
    }, 256, 72, 0.95);
    this.label.position.y = 1.7; this.group.add(this.label);

    // puntitos "pensando..."
    this.dots = [0, 1, 2].map(i => {
      const d = haloSprite(light, 0.2, 1); d.position.set((i - 1) * 0.2, 1.95, 0); d.visible = false; this.group.add(d); return d;
    });
    this.thinking = false;

    this.sparks = [];
    this.sparkTex = glowTexture();
    this.sparkAcc = 0;

    this.bubble = null; this.bubbleTimer = 0;
    this.target = null; this.stopDist = ARRIVE_DIST;
    this.action = 'idle'; this.actionTime = 0; this.t = Math.random() * 10;
    this.nextBlink = 2 + Math.random() * 3; this.blink = 0;
  }

  #accessory(type, mat, lightMat, base, light) {
    const glowMat = new THREE.MeshBasicMaterial({ color: light });
    if (type === 'ears') {
      for (const s of [-1, 1]) {
        const ear = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.2, 4), mat); ear.position.set(0.14 * s, 0.23, 0); ear.rotation.z = -0.35 * s; this.head.add(ear);
        const inner = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.12, 4), lightMat); inner.position.set(0.14 * s, 0.21, 0.03); inner.rotation.z = -0.35 * s; this.head.add(inner);
      }
    } else if (type === 'antenna') {
      const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.2, 6), lightMat); stick.position.y = 0.32; this.head.add(stick);
      this.antenna = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 10), glowMat); this.antenna.position.y = 0.44; this.head.add(this.antenna);
      this.antenna.add(haloSprite(light, 0.5, 0.8));
    } else if (type === 'halo') {
      this.halo = new THREE.Mesh(new THREE.TorusGeometry(0.17, 0.018, 8, 32), glowMat); this.halo.rotation.x = Math.PI / 2; this.halo.position.y = 0.36; this.head.add(this.halo);
      this.halo.add(haloSprite(light, 0.6, 0.5));
    } else if (type === 'horns') {
      for (const s of [-1, 1]) { const h = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.2, 6), lightMat); h.position.set(0.13 * s, 0.24, 0); h.rotation.z = -0.5 * s; this.head.add(h); }
    } else { // sprout
      const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.016, 0.16, 6), new THREE.MeshStandardMaterial({ color: 0x5fe07a })); stem.position.y = 0.3; this.head.add(stem);
      for (const s of [-1, 1]) { const leaf = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 8), new THREE.MeshStandardMaterial({ color: 0x7dff8a, emissive: 0x2fbf50, emissiveIntensity: 0.5 })); leaf.scale.set(1, 0.3, 0.55); leaf.position.set(0.07 * s, 0.4, 0); leaf.rotation.z = 0.4 * s; this.head.add(leaf); }
    }
  }

  get position() { return this.group.position; }

  setThinking(on) { this.thinking = on; if (!on) this.dots.forEach(d => { d.visible = false; }); }

  say(text) {
    this.#clearBubble();
    const color = this.color;
    this.bubble = textSprite((c, w, h) => {
      c.font = 'bold 38px ui-rounded, system-ui, sans-serif';
      const lines = wrapLines(c, text, w - 70);
      const lh = 46, bh = lines.length * lh + 34;
      c.shadowColor = color; c.shadowBlur = 18;
      c.fillStyle = '#fffaf0f5'; c.beginPath(); c.roundRect(10, h - bh - 34, w - 20, bh, 26); c.fill();
      c.lineWidth = 5; c.strokeStyle = color; c.stroke();
      c.beginPath(); c.moveTo(w / 2 - 16, h - 36); c.lineTo(w / 2 + 16, h - 36); c.lineTo(w / 2, h - 8); c.closePath(); c.fillStyle = '#fffaf0'; c.fill();
      c.shadowBlur = 0; c.fillStyle = '#1b1030'; c.textBaseline = 'top';
      lines.forEach((l, i) => c.fillText(l, 35, h - bh - 16 + i * lh));
    }, 512, 320, 2.8);
    this.bubble.position.y = 2.75;
    this.group.add(this.bubble);
    this.bubbleTimer = Math.max(4, text.length * 0.08);
  }
  #clearBubble() { if (this.bubble) { this.group.remove(this.bubble); disposeSprite(this.bubble); this.bubble = null; } }

  walkTo(x, z, stopDist = ARRIVE_DIST) { this.target = new THREE.Vector3(x, 0, z); this.stopDist = stopDist; this.action = 'walk_to'; }
  perform(action) { if (['wave', 'dance', 'jump'].includes(action)) { this.action = action; this.actionTime = action === 'jump' ? 0.9 : 3; this.target = null; if (action === 'jump') this.#burst(8); } }
  lookAt(p) { this.group.rotation.y = Math.atan2(p.x - this.position.x, p.z - this.position.z); }

  describe() {
    if (this.target) return 'caminando';
    return { wave: 'saludando', dance: 'bailando', jump: 'saltando' }[this.action] || 'quieto';
  }

  #burst(n) { for (let i = 0; i < n; i++) this.#spark(); }
  #spark() {
    if (this.sparks.length >= MAX_SPARKS) return;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.sparkTex, color: Math.random() < 0.5 ? new THREE.Color(this.color) : 0xffffff,
      transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    s.position.set((Math.random() - 0.5) * 0.5, 0.2 + Math.random() * 0.8, (Math.random() - 0.5) * 0.5);
    s.userData = { life: 0, max: 0.8 + Math.random() * 0.6, vy: 0.5 + Math.random() * 0.8, vx: (Math.random() - 0.5) * 0.6, size: 0.18 + Math.random() * 0.2 };
    this.group.add(s); this.sparks.push(s);
  }

  update(dt) {
    this.t += dt;
    if (this.bubble && (this.bubbleTimer -= dt) <= 0) this.#clearBubble();
    let walking = false;
    if (this.target) {
      const d = this.target.clone().sub(this.position); d.y = 0;
      const dist = d.length();
      if (dist <= this.stopDist) { this.target = null; this.action = 'idle'; }
      else {
        d.normalize();
        this.position.addScaledVector(d, Math.min(WALK_SPEED * dt, dist - this.stopDist));
        // giro suave hacia donde camina
        const want = Math.atan2(d.x, d.z); let diff = want - this.group.rotation.y;
        diff = Math.atan2(Math.sin(diff), Math.cos(diff)); this.group.rotation.y += diff * Math.min(1, dt * 10);
        walking = true;
      }
    }
    // pose base
    const t = this.t;
    this.body.position.y = 0; this.body.rotation.set(0, 0, 0); this.body.scale.set(1, 1, 1);
    this.arms.forEach(a => a.rotation.set(0, 0, 0)); this.legs.forEach(l => l.rotation.set(0, 0, 0));
    this.head.rotation.set(0, 0, 0);
    let sparking = false;
    if (walking) {
      const s = Math.sin(t * 9);
      this.legs[0].rotation.x = s * 0.7; this.legs[1].rotation.x = -s * 0.7;
      this.arms[0].rotation.x = -s * 0.6; this.arms[1].rotation.x = s * 0.6;
      this.body.position.y = Math.abs(s) * 0.05; this.body.rotation.z = Math.sin(t * 9) * 0.04;
    } else if (this.action === 'wave' && (this.actionTime -= dt) > 0) {
      this.arms[1].rotation.z = Math.PI * 0.8; this.arms[1].rotation.x = Math.sin(t * 12) * 0.5; this.head.rotation.z = Math.sin(t * 3) * 0.1;
    } else if (this.action === 'dance' && (this.actionTime -= dt) > 0) {
      const b = Math.sin(t * 6);
      this.body.position.y = Math.abs(b) * 0.12; this.body.rotation.y = Math.sin(t * 3) * 0.6;
      this.body.scale.set(1 + (1 - Math.abs(b)) * 0.05, 1 - (1 - Math.abs(b)) * 0.06, 1);
      this.arms[0].rotation.z = -Math.PI * 0.7 + b * 0.4; this.arms[1].rotation.z = Math.PI * 0.7 - b * 0.4;
      this.legs[0].rotation.x = b * 0.4; this.legs[1].rotation.x = -b * 0.4; this.head.rotation.z = Math.sin(t * 3) * 0.2;
      sparking = true;
    } else if (this.action === 'jump' && (this.actionTime -= dt) > 0) {
      const p = 1 - this.actionTime / 0.9, h = Math.sin(p * Math.PI);
      this.body.position.y = h * 0.75;
      const sy = 1 + 0.16 * h - (p > 0.85 ? 0.18 * (p - 0.85) / 0.15 : 0); // estira al subir, aplasta al caer
      this.body.scale.set(1 / Math.sqrt(sy), sy, 1 / Math.sqrt(sy));
      this.arms.forEach((a, i) => { a.rotation.z = (i ? 1 : -1) * Math.PI * 0.8; });
    } else {
      if (this.action !== 'idle' && this.actionTime <= 0) this.action = 'idle';
      const br = Math.sin(t * 1.8);
      this.body.position.y = br * 0.012; this.body.scale.set(1 - br * 0.006, 1 + br * 0.012, 1);
      this.arms[0].rotation.z = 0.05 + br * 0.03; this.arms[1].rotation.z = -0.05 - br * 0.03;
      this.head.rotation.z = Math.sin(t * 0.7) * 0.05; this.head.rotation.y = Math.sin(t * 0.45) * 0.18;
    }

    // parpadeo
    if ((this.nextBlink -= dt) <= 0) { this.blink = 0.14; this.nextBlink = 2 + Math.random() * 4; }
    const closed = this.blink > 0 ? 1 : 0; this.blink = Math.max(0, this.blink - dt);
    this.eyes.forEach(e => { e.scale.y = closed ? 0.1 : 1; });
    // boca: se mueve mientras habla
    const speaking = !!this.bubble;
    this.mouth.scale.y = speaking ? 0.35 + Math.abs(Math.sin(t * 14)) * 0.9 : 0.35;
    // aura y accesorios
    const pulse = 0.5 + 0.5 * Math.sin(t * 2.4);
    this.aura.material.opacity = (speaking ? 0.8 : 0.45) + pulse * 0.2;
    this.ring.scale.setScalar(1 + pulse * (speaking ? 0.35 : 0.12)); this.ring.material.opacity = 0.35 + pulse * 0.4;
    if (this.halo) { this.halo.rotation.z += dt * 1.5; this.halo.position.y = 0.36 + Math.sin(t * 2) * 0.02; }
    if (this.antenna) this.antenna.position.x = Math.sin(t * 3) * 0.03;
    // "pensando..."
    if (this.thinking) this.dots.forEach((d, i) => { d.visible = true; d.position.y = 1.95 + Math.max(0, Math.sin(t * 6 - i * 0.9)) * 0.14; d.material.opacity = 0.55 + 0.45 * Math.sin(t * 6 - i * 0.9); });
    // chispas
    if (sparking && (this.sparkAcc += dt * 12) >= 1) { this.sparkAcc = 0; this.#spark(); }
    for (let i = this.sparks.length - 1; i >= 0; i--) {
      const s = this.sparks[i], u = s.userData; u.life += dt;
      const k = u.life / u.max;
      if (k >= 1) { this.group.remove(s); s.material.dispose(); this.sparks.splice(i, 1); continue; }
      s.position.y += u.vy * dt; s.position.x += u.vx * dt;
      s.material.opacity = 1 - k; s.scale.setScalar(u.size * (1 - k * 0.5));
    }
  }
}
