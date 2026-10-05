import * as THREE from 'three';
import { glowTexture, haloSprite, rng } from './fx.js';

export const ISLAND_RADIUS = 6.2;
const TAU = Math.PI * 2;
const PALETTE = [0xff3fd0, 0x2fe6ff, 0x9d6bff, 0x8dff6a]; // magenta, cian, violeta, lima

// ---------- shaders ----------
const NOISE = /* glsl */`
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
float noise(vec2 p){
  vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
}
float fbm(vec2 p){ float v = 0.0, a = 0.5; for (int i = 0; i < 4; i++) { v += a*noise(p); p *= 2.0; a *= 0.5; } return v; }
`;

const SKY_FRAG = /* glsl */`
varying vec3 vDir; uniform float uTime;
${NOISE}
void main(){
  vec3 d = normalize(vDir); float h = d.y;
  vec3 top = vec3(0.015, 0.008, 0.10), mid = vec3(0.14, 0.035, 0.28);
  vec3 hor = vec3(0.60, 0.16, 0.55) * 0.5, low = vec3(0.02, 0.06, 0.16);
  vec3 col = mix(mid, top, smoothstep(0.1, 0.9, h));
  col = mix(hor, col, smoothstep(-0.02, 0.22, h));
  col = mix(col, low, smoothstep(0.0, -0.5, h));
  // cortinas de aurora
  vec2 uv = d.xz / (abs(d.y) + 0.35);
  float band = fbm(uv * vec2(1.4, 0.8) + vec2(uTime * 0.03, 0.0));
  float curtain = smoothstep(0.30, 0.85, sin(uv.x * 2.1 + band * 5.0 + uTime * 0.25) * 0.5 + 0.5);
  float mask = smoothstep(0.04, 0.35, h) * smoothstep(0.95, 0.45, h);
  vec3 aur = mix(vec3(0.10, 1.0, 0.62), vec3(0.85, 0.22, 1.0), smoothstep(0.2, 0.8, h + band * 0.35));
  col += aur * curtain * mask * (0.30 + 0.45 * band);
  // nebulosa tenue
  col += vec3(0.5, 0.1, 0.6) * pow(fbm(uv * 2.5 + 7.0), 3.0) * 0.35 * smoothstep(0.0, 0.5, h);
  gl_FragColor = vec4(col, 1.0);
}`;

const STAR_VERT = /* glsl */`
attribute float aSize; attribute float aPhase; uniform float uTime; uniform float uPx; varying float vA;
void main(){
  vA = 0.55 + 0.45 * sin(uTime * 1.7 + aPhase);
  gl_PointSize = aSize * uPx * (0.7 + 0.5 * vA);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;
const STAR_FRAG = /* glsl */`
varying float vA;
void main(){
  float d = length(gl_PointCoord - 0.5) * 2.0; if (d > 1.0) discard;
  gl_FragColor = vec4(vec3(0.85, 0.9, 1.0), (1.0 - d) * vA);
}`;

const PLANET_VERT = /* glsl */`
varying vec3 vN; varying vec3 vP;
void main(){ vN = normalize(normalMatrix * normal); vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const PLANET_FRAG = /* glsl */`
varying vec3 vN; varying vec3 vP; uniform vec3 uA; uniform vec3 uB; uniform float uBands;
${NOISE}
void main(){
  float b = sin(vP.y * uBands + noise(vP.xz * 0.35) * 3.0) * 0.5 + 0.5;
  vec3 base = mix(uA, uB, b);
  float l = max(dot(normalize(vN), normalize(vec3(0.6, 0.45, 0.7))), 0.0);
  float rim = pow(1.0 - max(normalize(vN).z, 0.0), 3.0);
  gl_FragColor = vec4(base * (0.18 + 0.95 * l) + vec3(0.5, 0.4, 1.0) * rim * 0.35, 1.0);
}`;
const RING_VERT = /* glsl */`varying float vR; void main(){ vR = length(position.xy); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const RING_FRAG = /* glsl */`
varying float vR; uniform float uIn; uniform float uOut;
void main(){
  float t = (vR - uIn) / (uOut - uIn);
  float bands = 0.55 + 0.45 * sin(t * 38.0) * sin(t * 11.0 + 1.0);
  float a = smoothstep(0.0, 0.08, t) * smoothstep(1.0, 0.85, t) * bands * 0.8;
  gl_FragColor = vec4(mix(vec3(1.0, 0.75, 0.9), vec3(0.6, 0.8, 1.0), t), a);
}`;
const FLY_VERT = /* glsl */`
attribute vec3 aSeed; attribute vec3 aColor; uniform float uTime; uniform float uPx; varying vec3 vC; varying float vA;
void main(){
  vec3 p = position;
  p.x += sin(uTime * (0.3 + aSeed.x * 0.5) + aSeed.y * 20.0) * 0.9;
  p.y += sin(uTime * (0.4 + aSeed.y * 0.5) + aSeed.z * 20.0) * 0.5;
  p.z += cos(uTime * (0.3 + aSeed.z * 0.5) + aSeed.x * 20.0) * 0.9;
  vec4 mv = modelViewMatrix * vec4(p, 1.0);
  vA = 0.35 + 0.65 * pow(sin(uTime * (1.2 + aSeed.x * 2.0) + aSeed.z * 30.0) * 0.5 + 0.5, 2.0);
  vC = aColor;
  gl_PointSize = (14.0 + aSeed.y * 14.0) * uPx / max(-mv.z, 0.5) * 6.0;
  gl_Position = projectionMatrix * mv;
}`;
const FLY_FRAG = /* glsl */`
varying vec3 vC; varying float vA;
void main(){ float d = length(gl_PointCoord - 0.5) * 2.0; if (d > 1.0) discard; gl_FragColor = vec4(vC, pow(1.0 - d, 2.0) * vA); }`;

// ---------- texturas procedurales ----------
function islandTextures(R) {
  const S = 1024, px = S / 2 / R; // px por metro
  const base = document.createElement('canvas'); base.width = base.height = S;
  const emi = document.createElement('canvas'); emi.width = emi.height = S;
  const b = base.getContext('2d'), e = emi.getContext('2d');
  const r = rng(11);

  const g = b.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2);
  g.addColorStop(0, '#2cc79a'); g.addColorStop(0.55, '#1f9f88'); g.addColorStop(0.9, '#2a6fa0'); g.addColorStop(1, '#4a3a9a');
  b.fillStyle = g; b.fillRect(0, 0, S, S);
  for (let i = 0; i < 9000; i++) { // pasto: manchitas
    const a = r() * TAU, d = Math.sqrt(r()) * S / 2 * 0.97;
    const x = S / 2 + Math.cos(a) * d, y = S / 2 + Math.sin(a) * d;
    b.fillStyle = `hsla(${135 + r() * 55}, ${60 + r() * 30}%, ${28 + r() * 32}%, ${0.18 + r() * 0.3})`;
    b.beginPath(); b.ellipse(x, y, 2 + r() * 5, 1 + r() * 3, r() * TAU, 0, TAU); b.fill();
  }
  for (let i = 0; i < 260; i++) { // florecitas
    const a = r() * TAU, d = Math.sqrt(r()) * S / 2 * 0.92;
    b.fillStyle = ['#ff8fe0', '#ffe78f', '#9ff3ff', '#d6b0ff'][i % 4];
    b.beginPath(); b.arc(S / 2 + Math.cos(a) * d, S / 2 + Math.sin(a) * d, 2 + r() * 2.5, 0, TAU); b.fill();
  }

  const rune = (ctx, strong) => {
    ctx.save(); ctx.translate(S / 2, S / 2);
    ctx.lineCap = 'round';
    const ring = (rad, w, dash, col) => { ctx.strokeStyle = col; ctx.lineWidth = w; ctx.setLineDash(dash); ctx.beginPath(); ctx.arc(0, 0, rad * px, 0, TAU); ctx.stroke(); };
    ring(2.05, 3, [], strong ? '#9ffff0' : 'rgba(159,255,240,0.35)');
    ring(3.0, 5, [18, 14], strong ? '#7fe7ff' : 'rgba(127,231,255,0.35)');
    ring(4.1, 3, [4, 12], strong ? '#d9a8ff' : 'rgba(217,168,255,0.3)');
    ring(5.7, 7, [], strong ? '#61fff0' : 'rgba(97,255,240,0.3)');
    ctx.setLineDash([]); ctx.fillStyle = strong ? '#ffd0f4' : 'rgba(255,208,244,0.4)';
    for (let i = 0; i < 12; i++) { // rombos entre anillos
      ctx.save(); ctx.rotate(i / 12 * TAU); ctx.translate(0, -4.9 * px); ctx.rotate(Math.PI / 4);
      ctx.fillRect(-7, -7, 14, 14); ctx.restore();
    }
    for (let i = 0; i < 6; i++) { // rayos desde el centro
      ctx.save(); ctx.rotate(i / 6 * TAU + 0.26); ctx.strokeStyle = strong ? '#8ffff0' : 'rgba(143,255,240,0.25)'; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(0, -2.15 * px); ctx.lineTo(0, -2.9 * px); ctx.stroke(); ctx.restore();
    }
    ctx.restore();
  };
  rune(b, false); rune(e, true);

  const mk = c => { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; };
  return { map: mk(base), emissive: mk(emi) };
}


export class Environment {
  constructor(scene) {
    this.scene = scene; this.t = 0; this.updaters = [];
    this.skyGroup = new THREE.Group(); scene.add(this.skyGroup);
    this.px = Math.min(devicePixelRatio || 1, 2);
    this.#sky(); this.#island(); this.#heart(); this.#crystals(); this.#mushrooms(); this.#grass(); this.#rocks(); this.#fireflies(); this.#lights();
  }

  update(dt, camera) {
    this.t += dt;
    this.skyGroup.position.copy(camera.position); // el cielo siempre queda "en el infinito"
    this.skyUniform.uTime.value = this.t;
    this.starUniform.uTime.value = this.t;
    this.flyUniform.uTime.value = this.t;
    for (const u of this.updaters) u(this.t, dt);
  }

  #sky() {
    this.skyUniform = { uTime: { value: 0 } };
    const dome = new THREE.Mesh(new THREE.SphereGeometry(200, 32, 20), new THREE.ShaderMaterial({
      uniforms: this.skyUniform, side: THREE.BackSide, depthWrite: false,
      vertexShader: 'varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: SKY_FRAG }));
    dome.renderOrder = -10; this.skyGroup.add(dome);

    const r = rng(3), n = 1400, pos = new Float32Array(n * 3), size = new Float32Array(n), ph = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const y = r() * 1.05 - 0.05, a = r() * TAU, rr = Math.sqrt(1 - Math.min(y * y, 1));
      pos[i * 3] = Math.cos(a) * rr * 190; pos[i * 3 + 1] = y * 190; pos[i * 3 + 2] = Math.sin(a) * rr * 190;
      size[i] = 1.2 + Math.pow(r(), 4) * 5; ph[i] = r() * 50;
    }
    const sg = new THREE.BufferGeometry();
    sg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    sg.setAttribute('aSize', new THREE.BufferAttribute(size, 1)); sg.setAttribute('aPhase', new THREE.BufferAttribute(ph, 1));
    this.starUniform = { uTime: { value: 0 }, uPx: { value: this.px } };
    const stars = new THREE.Points(sg, new THREE.ShaderMaterial({ uniforms: this.starUniform, vertexShader: STAR_VERT, fragmentShader: STAR_FRAG,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
    stars.frustumCulled = false; this.skyGroup.add(stars);

    // planeta con anillos + luna
    const planet = new THREE.Group(); planet.position.set(-70, 38, -120); planet.rotation.z = 0.35;
    planet.add(new THREE.Mesh(new THREE.SphereGeometry(20, 40, 28), new THREE.ShaderMaterial({
      uniforms: { uA: { value: new THREE.Color(0xff6aa8) }, uB: { value: new THREE.Color(0x7a4cff) }, uBands: { value: 0.55 } },
      vertexShader: PLANET_VERT, fragmentShader: PLANET_FRAG })));
    const ring = new THREE.Mesh(new THREE.RingGeometry(27, 44, 96), new THREE.ShaderMaterial({
      uniforms: { uIn: { value: 27 }, uOut: { value: 44 } }, vertexShader: RING_VERT, fragmentShader: RING_FRAG,
      transparent: true, side: THREE.DoubleSide, depthWrite: false }));
    ring.rotation.x = Math.PI / 2 - 0.35; planet.add(ring);
    planet.add(haloSprite(0xb98cff, 90, 0.35));
    this.skyGroup.add(planet);
    const moon = new THREE.Mesh(new THREE.SphereGeometry(6, 28, 20), new THREE.ShaderMaterial({
      uniforms: { uA: { value: new THREE.Color(0xbdf7ff) }, uB: { value: new THREE.Color(0x56c9e0) }, uBands: { value: 1.6 } },
      vertexShader: PLANET_VERT, fragmentShader: PLANET_FRAG }));
    moon.position.set(95, 62, -105); moon.add(haloSprite(0x7fe9ff, 36, 0.4));
    this.skyGroup.add(moon);
    this.updaters.push(t => { planet.rotation.y = t * 0.01; moon.rotation.y = t * 0.03; });
  }

  #island() {
    const R = ISLAND_RADIUS, { map, emissive } = islandTextures(R);
    this.islandMat = new THREE.MeshStandardMaterial({ map, emissiveMap: emissive, emissive: 0xffffff, emissiveIntensity: 0.9, roughness: 0.9 });
    const top = new THREE.Mesh(new THREE.CircleGeometry(R, 72), this.islandMat);
    top.rotation.x = -Math.PI / 2; top.receiveShadow = true; this.scene.add(top);

    const rock = new THREE.MeshStandardMaterial({ color: 0x5a4496, roughness: 0.92, flatShading: true, emissive: 0x241455, emissiveIntensity: 0.7 });
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(R, R * 0.93, 0.7, 72, 1, true), rock);
    rim.position.y = -0.35; rim.receiveShadow = true; this.scene.add(rim);

    // parte de abajo: cono invertido y desigual
    const DEPTH = 8.5;
    const cone = new THREE.ConeGeometry(R * 0.93, DEPTH, 30, 6, true); cone.rotateX(Math.PI); cone.translate(0, -DEPTH / 2, 0); // base y=0, punta y=-8.5
    const p = cone.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      const keep = y > -DEPTH + 0.01 ? 1 : 0; // la punta queda fija
      const k = 1 + keep * (0.2 * Math.sin(x * 1.7 + y) * Math.cos(z * 1.3 - y * 0.8) + 0.1 * Math.sin(y * 3.1 + x * 0.7));
      p.setXYZ(i, x * k, y + keep * 0.3 * Math.sin(x * 2 + z * 2), z * k);
    }
    cone.computeVertexNormals();
    const under = new THREE.Mesh(cone, rock); under.position.y = -0.7; under.castShadow = true; this.scene.add(under);

    // brillo del borde
    this.rimMat = new THREE.MeshBasicMaterial({ color: 0x61fff0, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending });
    const edge = new THREE.Mesh(new THREE.TorusGeometry(R * 0.995, 0.045, 8, 120), this.rimMat);
    edge.rotation.x = Math.PI / 2; edge.position.y = 0.02; this.scene.add(edge);
    const edgeGlow = new THREE.Mesh(new THREE.TorusGeometry(R * 0.995, 0.22, 8, 120), new THREE.MeshBasicMaterial({
      color: 0x61fff0, transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false }));
    edgeGlow.rotation.x = Math.PI / 2; edgeGlow.position.y = 0.02; this.scene.add(edgeGlow);

    // cristales colgando bajo la isla
    const rr = rng(21);
    for (let i = 0; i < 9; i++) {
      const a = rr() * TAU, d = 1.5 + rr() * 3.6, h = 1 + rr() * 1.6, col = PALETTE[i % 4];
      const c = new THREE.Mesh(new THREE.ConeGeometry(0.16 + rr() * 0.12, h, 5), new THREE.MeshBasicMaterial({ color: col }));
      c.rotation.x = Math.PI; c.position.set(Math.cos(a) * d, -2.4 - rr() * 1.6, Math.sin(a) * d);
      c.add(haloSprite(col, 1.6, 0.55)); this.scene.add(c);
      const ph = rr() * 9; this.updaters.push(t => { c.children[0].material.opacity = 0.35 + 0.3 * Math.sin(t * 1.6 + ph); });
    }

    this.updaters.push(t => {
      this.islandMat.emissiveIntensity = 0.75 + 0.35 * Math.sin(t * 1.3);
      this.rimMat.opacity = 0.7 + 0.3 * Math.sin(t * 2.0);
    });
    // toda la isla "respira" suavemente
    this.island = [top, rim, under, edge, edgeGlow];
  }

  #heart() {
    const g = new THREE.Group(); g.position.y = 2.2; this.scene.add(g);
    const crystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.62, 0), new THREE.MeshStandardMaterial({
      color: 0x9ffcff, emissive: 0x20d9ff, emissiveIntensity: 1.6, roughness: 0.12, metalness: 0.25, flatShading: true, transparent: true, opacity: 0.93 }));
    crystal.scale.set(1, 1.8, 1); crystal.castShadow = true; g.add(crystal);
    g.add(haloSprite(0x4fe9ff, 4.2, 0.85));
    const rings = [0, 1, 2].map(i => {
      const m = new THREE.Mesh(new THREE.TorusGeometry(0.95 + i * 0.22, 0.014, 6, 80), new THREE.MeshBasicMaterial({
        color: [0xff7ae8, 0x7ae8ff, 0xc5a0ff][i], transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending }));
      m.rotation.set(i * 1.0, i * 0.6, i * 0.3); g.add(m); return m;
    });
    const motes = [];
    for (let i = 0; i < 7; i++) { const m = haloSprite(PALETTE[i % 4], 0.5, 0.9); g.add(m); motes.push(m); }
    // base brillante
    const pad = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.15, 0.14, 40), new THREE.MeshStandardMaterial({
      color: 0x1d3a6b, emissive: 0x2fe6ff, emissiveIntensity: 0.7, roughness: 0.4 }));
    pad.position.y = 0.07; pad.receiveShadow = true; this.scene.add(pad);
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.5, 2.0, 24, 1, true), new THREE.MeshBasicMaterial({
      color: 0x4fe9ff, transparent: true, opacity: 0.18, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    beam.position.y = 1.15; this.scene.add(beam);

    this.updaters.push(t => {
      g.position.y = 2.2 + Math.sin(t * 1.1) * 0.18;
      crystal.rotation.y = t * 0.7;
      crystal.material.emissiveIntensity = 1.3 + 0.5 * Math.sin(t * 2.2);
      rings.forEach((m, i) => { m.rotation.x += 0.004 * (i + 1); m.rotation.y += 0.006 * (3 - i); });
      motes.forEach((m, i) => { const a = t * (0.6 + i * 0.07) + i * 0.9, rad = 1.2 + (i % 3) * 0.25;
        m.position.set(Math.cos(a) * rad, Math.sin(a * 1.3 + i) * 0.7, Math.sin(a) * rad); });
      pad.material.emissiveIntensity = 0.55 + 0.3 * Math.sin(t * 2.2);
    });
  }

  #crystals() {
    const r = rng(33);
    for (let k = 0; k < 4; k++) {
      const ang = (k + 0.5) / 4 * TAU, col = PALETTE[k], cl = new THREE.Group();
      cl.position.set(Math.cos(ang) * 4.7, 0, Math.sin(ang) * 4.7); this.scene.add(cl);
      const mats = [];
      for (let i = 0; i < 4; i++) {
        const h = i === 0 ? 2.1 : 0.8 + r() * 1.0, w = i === 0 ? 0.32 : 0.14 + r() * 0.12;
        const m = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 1.0, roughness: 0.2, metalness: 0.2, flatShading: true, transparent: true, opacity: 0.92 });
        const c = new THREE.Mesh(new THREE.OctahedronGeometry(w, 0), m); c.scale.y = h / w * 0.9; c.castShadow = true;
        const a = r() * TAU, d = i === 0 ? 0 : 0.28 + r() * 0.3;
        c.position.set(Math.cos(a) * d, h * 0.42, Math.sin(a) * d); c.rotation.set((r() - 0.5) * 0.5, r() * TAU, (r() - 0.5) * 0.5);
        cl.add(c); mats.push(m);
      }
      const halo = haloSprite(col, 4.2, 0.55); halo.position.set(0, 1.1, 0); cl.add(halo);
      const light = new THREE.PointLight(col, 7, 7.5); light.position.set(0, 1.4, 0); cl.add(light);
      const ph = k * 1.7; this.updaters.push(t => { const v = 0.5 + 0.5 * Math.sin(t * 1.5 + ph); mats.forEach(m => m.emissiveIntensity = 0.7 + v * 0.9); light.intensity = 4 + v * 5; });
    }
  }

  #mushrooms() {
    const r = rng(44), stem = new THREE.MeshStandardMaterial({ color: 0xf2e6ff, roughness: 0.8 });
    const spots = [];
    while (spots.length < 11) {
      const a = r() * TAU, d = 2.3 + r() * 3.3, x = Math.cos(a) * d, z = Math.sin(a) * d;
      const near = [...Array(4)].some((_, k) => Math.hypot(x - Math.cos((k + 0.5) / 4 * TAU) * 4.7, z - Math.sin((k + 0.5) / 4 * TAU) * 4.7) < 1.1);
      if (!near) spots.push([x, z]);
    }
    spots.forEach(([x, z], i) => {
      const col = [0xff5fd2, 0x4fe9ff, 0xb085ff][i % 3], s = 0.7 + r() * 0.9, g = new THREE.Group();
      g.position.set(x, 0, z); g.scale.setScalar(s);
      const st = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.075, 0.34, 8), stem); st.position.y = 0.17; g.add(st);
      const capM = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 1.1, roughness: 0.5 });
      const cap = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 10, 0, TAU, 0, Math.PI / 2), capM); cap.position.y = 0.32; cap.castShadow = true; g.add(cap);
      for (let d = 0; d < 4; d++) { const dot = new THREE.Mesh(new THREE.SphereGeometry(0.03, 6, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }));
        const a = d / 4 * TAU; dot.position.set(Math.cos(a) * 0.11, 0.4 + (d % 2) * 0.02, Math.sin(a) * 0.11); g.add(dot); }
      const h = haloSprite(col, 1.3, 0.5); h.position.y = 0.36; g.add(h);
      this.scene.add(g);
      const ph = r() * 9; this.updaters.push(t => { const v = Math.sin(t * 1.4 + ph); capM.emissiveIntensity = 0.9 + 0.5 * v; h.material.opacity = 0.4 + 0.25 * v; g.rotation.z = Math.sin(t * 0.8 + ph) * 0.03; });
    });
  }

  #grass() {
    const n = 900, geo = new THREE.ConeGeometry(0.03, 0.17, 4); geo.translate(0, 0.085, 0);
    const mesh = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ roughness: 0.8 }), n);
    const r = rng(55), m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), c = new THREE.Color();
    for (let i = 0; i < n; i++) {
      const a = r() * TAU, d = 1.3 + Math.sqrt(r()) * 4.7, s = 0.6 + r() * 1.1;
      e.set((r() - 0.5) * 0.4, r() * TAU, (r() - 0.5) * 0.4); q.setFromEuler(e);
      m.compose(new THREE.Vector3(Math.cos(a) * d, 0, Math.sin(a) * d), q, new THREE.Vector3(s, s * (0.8 + r() * 0.8), s));
      mesh.setMatrixAt(i, m);
      mesh.setColorAt(i, c.setHSL(0.30 + r() * 0.2, 0.7, 0.38 + r() * 0.22));
    }
    this.scene.add(mesh);
  }

  #rocks() {
    const r = rng(66), rockM = new THREE.MeshStandardMaterial({ color: 0x6a52a8, roughness: 0.9, flatShading: true, emissive: 0x2d1b66, emissiveIntensity: 0.7 });
    for (let i = 0; i < 9; i++) {
      const a = (i + r() * 0.6) / 9 * TAU, d = 9.5 + r() * 7, s = 0.5 + r() * 1.3, y = -2 + r() * 8;
      const g = new THREE.Group(); g.position.set(Math.cos(a) * d, y, Math.sin(a) * d); this.scene.add(g);
      const body = new THREE.Mesh(new THREE.IcosahedronGeometry(s, 0), rockM); body.scale.y = 0.7; g.add(body);
      const down = new THREE.Mesh(new THREE.ConeGeometry(s * 0.7, s * 1.8, 6), rockM); down.rotation.x = Math.PI; down.position.y = -s * 1.1; g.add(down);
      const col = PALETTE[i % 4];
      const cr = new THREE.Mesh(new THREE.OctahedronGeometry(s * 0.2, 0), new THREE.MeshBasicMaterial({ color: col })); cr.scale.y = 2.4; cr.position.y = s * 0.7; g.add(cr);
      cr.add(haloSprite(col, s * 3.2, 0.6));
      const ph = r() * 9, sp = 0.3 + r() * 0.4, y0 = y;
      this.updaters.push(t => { g.position.y = y0 + Math.sin(t * sp + ph) * 0.5; g.rotation.y = t * 0.08 + ph; });
    }
  }

  #fireflies() {
    const n = 160, r = rng(77), pos = new Float32Array(n * 3), seed = new Float32Array(n * 3), col = new Float32Array(n * 3), c = new THREE.Color();
    for (let i = 0; i < n; i++) {
      const a = r() * TAU, d = Math.sqrt(r()) * 8;
      pos.set([Math.cos(a) * d, 0.4 + r() * 4.2, Math.sin(a) * d], i * 3); seed.set([r(), r(), r()], i * 3);
      c.setHSL([0.16, 0.5, 0.88, 0.33][i % 4], 1, 0.62); col.set([c.r, c.g, c.b], i * 3);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('aSeed', new THREE.BufferAttribute(seed, 3)); geo.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
    this.flyUniform = { uTime: { value: 0 }, uPx: { value: this.px } };
    const pts = new THREE.Points(geo, new THREE.ShaderMaterial({ uniforms: this.flyUniform, vertexShader: FLY_VERT, fragmentShader: FLY_FRAG,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
    pts.frustumCulled = false; this.scene.add(pts);
  }

  #lights() {
    this.scene.add(new THREE.HemisphereLight(0x9a86ff, 0x0b4a55, 0.95));
    const moon = new THREE.DirectionalLight(0xcdbfff, 1.25);
    moon.position.set(-7, 11, 6); moon.castShadow = true; moon.shadow.mapSize.set(1024, 1024);
    Object.assign(moon.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8, near: 1, far: 30 });
    moon.shadow.bias = -0.0005; this.scene.add(moon);
    const heart = new THREE.PointLight(0x4fe9ff, 16, 11); heart.position.set(0, 2.4, 0); this.scene.add(heart);
    this.updaters.push(t => { heart.intensity = 13 + 4 * Math.sin(t * 2.2); });
    this.scene.fog = new THREE.Fog(0x2a1250, 26, 80);
  }
}
