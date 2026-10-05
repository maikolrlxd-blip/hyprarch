import * as THREE from 'three';

const WALK_SPEED = 1.6;
const ARRIVE_DIST = 0.15;

function textSprite(draw, w, h, scale) {
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  draw(canvas.getContext('2d'), w, h);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
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

export class Avatar {
  constructor({ id, name, color }) {
    this.id = id; this.name = name; this.color = color;
    this.group = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0.1 });
    const dark = new THREE.MeshStandardMaterial({ color: 0x15151f, roughness: 0.4 });
    const white = new THREE.MeshStandardMaterial({ color: 0xffffff });

    this.body = new THREE.Group(); // todo lo que rebota/baila
    this.group.add(this.body);
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.22, 0.4, 6, 12), mat);
    torso.position.y = 0.62; torso.castShadow = true; this.body.add(torso);
    this.head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 16), mat);
    this.head.position.y = 1.18; this.head.castShadow = true; this.body.add(this.head);
    for (const s of [-1, 1]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), white);
      eye.position.set(0.08 * s, 1.21, 0.18); this.body.add(eye);
      const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.022, 8, 8), dark);
      pupil.position.set(0.08 * s, 1.21, 0.215); this.body.add(pupil);
    }
    this.arms = [-1, 1].map(s => {
      const pivot = new THREE.Group(); pivot.position.set(0.3 * s, 0.9, 0);
      const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.32, 4, 8), mat);
      arm.position.y = -0.2; arm.castShadow = true; pivot.add(arm); this.body.add(pivot); return pivot;
    });
    this.legs = [-1, 1].map(s => {
      const pivot = new THREE.Group(); pivot.position.set(0.1 * s, 0.34, 0);
      const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.07, 0.22, 4, 8), dark);
      leg.position.y = -0.14; leg.castShadow = true; pivot.add(leg); this.body.add(pivot); return pivot;
    });

    this.label = textSprite((c, w, h) => {
      c.font = 'bold 44px system-ui, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillStyle = '#000a'; c.beginPath(); c.roundRect(10, 8, w - 20, h - 16, 24); c.fill();
      c.fillStyle = color; c.fillText(name, w / 2, h / 2 + 2);
    }, 256, 72, 0.9);
    this.label.position.y = 1.62; this.group.add(this.label);

    this.bubble = null; this.bubbleTimer = 0;
    this.target = null; this.stopDist = ARRIVE_DIST;
    this.action = 'idle'; this.actionTime = 0; this.t = Math.random() * 10;
  }

  get position() { return this.group.position; }

  say(text) {
    if (this.bubble) { this.group.remove(this.bubble); this.bubble.material.map.dispose(); this.bubble.material.dispose(); }
    this.bubble = textSprite((c, w, h) => {
      c.font = '34px system-ui, sans-serif';
      const lines = wrapLines(c, text, w - 60);
      const lh = 42, bh = lines.length * lh + 30;
      c.fillStyle = '#fffffff2'; c.beginPath(); c.roundRect(8, h - bh - 30, w - 16, bh, 24); c.fill();
      c.beginPath(); c.moveTo(w / 2 - 16, h - 31); c.lineTo(w / 2 + 16, h - 31); c.lineTo(w / 2, h - 6); c.fill();
      c.fillStyle = '#15151f'; c.textBaseline = 'top';
      lines.forEach((l, i) => c.fillText(l, 30, h - bh - 15 + i * lh));
    }, 512, 320, 2.4);
    this.bubble.position.y = 2.55;
    this.group.add(this.bubble);
    this.bubbleTimer = Math.max(4, text.length * 0.08);
  }

  walkTo(x, z, stopDist = ARRIVE_DIST) { this.target = new THREE.Vector3(x, 0, z); this.stopDist = stopDist; this.action = 'walk_to'; }
  perform(action) { if (['wave', 'dance', 'jump'].includes(action)) { this.action = action; this.actionTime = action === 'jump' ? 0.9 : 3; this.target = null; } }
  lookAt(p) { this.group.rotation.y = Math.atan2(p.x - this.position.x, p.z - this.position.z); }

  describe() {
    if (this.target) return 'caminando';
    return { wave: 'saludando', dance: 'bailando', jump: 'saltando' }[this.action] || 'quieto';
  }

  update(dt) {
    this.t += dt;
    if (this.bubble && (this.bubbleTimer -= dt) <= 0) {
      this.group.remove(this.bubble); this.bubble.material.map.dispose(); this.bubble.material.dispose(); this.bubble = null;
    }
    let walking = false;
    if (this.target) {
      const d = this.target.clone().sub(this.position); d.y = 0;
      const dist = d.length();
      if (dist <= this.stopDist) { this.target = null; this.action = 'idle'; }
      else {
        d.normalize();
        this.position.addScaledVector(d, Math.min(WALK_SPEED * dt, dist - this.stopDist));
        this.group.rotation.y = Math.atan2(d.x, d.z);
        walking = true;
      }
    }
    // Pose base
    this.body.position.y = 0; this.body.rotation.set(0, 0, 0);
    this.arms.forEach(a => a.rotation.set(0, 0, 0)); this.legs.forEach(l => l.rotation.set(0, 0, 0));
    const t = this.t;
    if (walking) {
      const s = Math.sin(t * 9);
      this.legs[0].rotation.x = s * 0.7; this.legs[1].rotation.x = -s * 0.7;
      this.arms[0].rotation.x = -s * 0.6; this.arms[1].rotation.x = s * 0.6;
      this.body.position.y = Math.abs(s) * 0.04;
    } else if (this.action === 'wave' && (this.actionTime -= dt) > 0) {
      this.arms[1].rotation.z = Math.PI * 0.8; this.arms[1].rotation.x = Math.sin(t * 12) * 0.5;
    } else if (this.action === 'dance' && (this.actionTime -= dt) > 0) {
      this.body.position.y = Math.abs(Math.sin(t * 6)) * 0.12; this.body.rotation.y = Math.sin(t * 3) * 0.6;
      this.arms[0].rotation.z = -Math.PI * 0.7 + Math.sin(t * 6) * 0.4; this.arms[1].rotation.z = Math.PI * 0.7 - Math.sin(t * 6) * 0.4;
      this.legs[0].rotation.x = Math.sin(t * 6) * 0.4; this.legs[1].rotation.x = -Math.sin(t * 6) * 0.4;
    } else if (this.action === 'jump' && (this.actionTime -= dt) > 0) {
      const p = 1 - this.actionTime / 0.9; this.body.position.y = Math.sin(p * Math.PI) * 0.7;
      this.arms.forEach((a, i) => a.rotation.z = (i ? 1 : -1) * Math.PI * 0.8);
    } else {
      if (!walking && this.action !== 'idle' && this.actionTime <= 0) this.action = 'idle';
      this.body.position.y = Math.sin(t * 1.8) * 0.01; // respiracion
      this.arms[0].rotation.z = 0.05; this.arms[1].rotation.z = -0.05;
    }
  }
}
