import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Avatar } from './avatar.js';

export const ROOM = 12; // metros por lado
const HALF = ROOM / 2 - 0.6;

export class World {
  constructor(canvas) {
    this.avatars = new Map();
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0b0b14);
    this.scene.fog = new THREE.Fog(0x0b0b14, 18, 40);
    this.camera = new THREE.PerspectiveCamera(55, 1, 0.1, 100);
    this.camera.position.set(0, 7, 11);
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.target.set(0, 0.8, 0);
    this.controls.maxPolarAngle = Math.PI * 0.49;
    this.controls.minDistance = 3; this.controls.maxDistance = 22;
    this.#buildRoom();
    this.clock = new THREE.Clock();
    new ResizeObserver(() => this.#resize(canvas)).observe(canvas);
    this.#resize(canvas);
    this.renderer.setAnimationLoop(() => this.#frame());
  }

  #resize(canvas) {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
  }

  #buildRoom() {
    const s = this.scene;
    s.add(new THREE.HemisphereLight(0x9ab8ff, 0x201030, 0.9));
    const sun = new THREE.DirectionalLight(0xffffff, 1.3);
    sun.position.set(5, 10, 4); sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 30 });
    s.add(sun);
    const neon = new THREE.PointLight(0x00ffe0, 18, 12); neon.position.set(0, 2.5, 0); s.add(neon);

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(ROOM, ROOM), new THREE.MeshStandardMaterial({ color: 0x1b1b30, roughness: 0.8 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; s.add(floor);
    const grid = new THREE.GridHelper(ROOM, ROOM, 0x00ffe0, 0x2a2a55); grid.position.y = 0.01; s.add(grid);

    const wallMat = new THREE.MeshStandardMaterial({ color: 0x2a2a50, roughness: 0.6, emissive: 0x05051a });
    for (const [x, z, ry] of [[0, -ROOM / 2, 0], [0, ROOM / 2, 0], [-ROOM / 2, 0, Math.PI / 2], [ROOM / 2, 0, Math.PI / 2]]) {
      const w = new THREE.Mesh(new THREE.BoxGeometry(ROOM, 0.5, 0.2), wallMat);
      w.position.set(x, 0.25, z); w.rotation.y = ry; w.castShadow = w.receiveShadow = true; s.add(w);
    }
    // Utileria: plataforma central, bancas y pilares neon
    const pad = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 0.12, 40), new THREE.MeshStandardMaterial({ color: 0x00ffe0, emissive: 0x00a090, roughness: 0.3 }));
    pad.position.y = 0.06; pad.receiveShadow = true; s.add(pad);
    const benchMat = new THREE.MeshStandardMaterial({ color: 0x4a3a6a, roughness: 0.7 });
    for (const [x, z, ry] of [[-4, -3, 0.3], [4, 3.5, -0.4]]) {
      const b = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.4, 0.5), benchMat);
      b.position.set(x, 0.2, z); b.rotation.y = ry; b.castShadow = b.receiveShadow = true; s.add(b);
    }
    for (const [x, z, c] of [[-5, 5, 0xff4fd8], [5, -5, 0x4f9bff], [-5, -5, 0xffd84f], [5, 5, 0x4fff9b]]) {
      const p = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 2.4, 12), new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.8 }));
      p.position.set(x, 1.2, z); p.castShadow = true; s.add(p);
      const l = new THREE.PointLight(c, 5, 5); l.position.set(x, 2.2, z); s.add(l);
    }
  }

  setAgents(defs) {
    const keep = new Set(defs.map(d => d.id));
    for (const [id, av] of this.avatars) if (!keep.has(id)) { this.scene.remove(av.group); this.avatars.delete(id); }
    defs.forEach((d, i) => {
      const old = this.avatars.get(d.id);
      if (old && old.name === d.name && old.color === d.color) return;
      if (old) { this.scene.remove(old.group); }
      const av = new Avatar(d);
      const a = (i / defs.length) * Math.PI * 2;
      av.position.set(old ? old.position.x : Math.cos(a) * 3, 0, old ? old.position.z : Math.sin(a) * 3);
      av.lookAt(new THREE.Vector3(0, 0, 0));
      this.scene.add(av.group); this.avatars.set(d.id, av);
    });
  }

  clamp(x, z) { return [Math.max(-HALF, Math.min(HALF, x)), Math.max(-HALF, Math.min(HALF, z))]; }

  // Resuelve el "target" que devuelve el modelo: nombre de otro personaje, 'centro' o 'x,z'.
  resolveTarget(self, target) {
    const t = String(target || '').trim().toLowerCase();
    for (const av of this.avatars.values()) {
      if (av !== self && av.name.toLowerCase() === t) return { x: av.position.x, z: av.position.z, stop: 1.4, who: av };
    }
    const m = t.match(/^(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)$/);
    if (m) { const [x, z] = this.clamp(+m[1], +m[2]); return { x, z, stop: 0.15 }; }
    return { x: 0, z: 0, stop: 0.5 };
  }

  #frame() {
    const dt = Math.min(this.clock.getDelta(), 0.1);
    const list = [...this.avatars.values()];
    for (const a of list) a.update(dt);
    // separacion para que no se atraviesen
    for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++) {
      const dx = list[j].position.x - list[i].position.x, dz = list[j].position.z - list[i].position.z;
      const d = Math.hypot(dx, dz), min = 0.7;
      if (d > 0.001 && d < min) {
        const push = (min - d) / 2 / d;
        list[i].position.x -= dx * push; list[i].position.z -= dz * push;
        list[j].position.x += dx * push; list[j].position.z += dz * push;
      }
    }
    for (const a of list) { const [x, z] = this.clamp(a.position.x, a.position.z); a.position.x = x; a.position.z = z; }
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
