import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';
import { Avatar } from './avatar.js';
import { Environment, ISLAND_RADIUS } from './environment.js';

export const ROOM = ISLAND_RADIUS * 2; // diametro de la isla, en metros
const WALK_RADIUS = ISLAND_RADIUS - 0.8;
const IDLE_BEFORE_ORBIT_MS = 6000;

export class World {
  constructor(canvas) {
    this.avatars = new Map();
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(55, 1, 0.1, 400);
    this.camera.position.set(0, 4.6, 12.5);
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.target.set(0, 1.9, 0);
    this.controls.enableDamping = true;
    this.controls.maxPolarAngle = Math.PI * 0.52;
    this.controls.minDistance = 3; this.controls.maxDistance = 24;
    // camara cinematografica: orbita sola y se detiene mientras la mueves
    this.controls.autoRotate = true; this.controls.autoRotateSpeed = 0.35;
    let resume;
    this.controls.addEventListener('start', () => { this.controls.autoRotate = false; clearTimeout(resume); });
    this.controls.addEventListener('end', () => { resume = setTimeout(() => { this.controls.autoRotate = true; }, IDLE_BEFORE_ORBIT_MS); });

    this.env = new Environment(this.scene);
    this.clock = new THREE.Clock();
    new ResizeObserver(() => this.#resize(canvas)).observe(canvas);
    this.#resize(canvas);
    this.renderer.setAnimationLoop(() => this.#frame());
  }

  #resize(canvas) {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.fov = h > w ? Math.min(78, 55 + (h / w - 1) * 22) : 55; // pantallas verticales: mas angular para que quepa la isla
    this.camera.updateProjectionMatrix();
  }

  setAgents(defs) {
    const keep = new Set(defs.map(d => d.id));
    for (const [id, av] of this.avatars) if (!keep.has(id)) { this.scene.remove(av.group); this.avatars.delete(id); }
    defs.forEach((d, i) => {
      const old = this.avatars.get(d.id);
      if (old && old.name === d.name && old.color === d.color) return;
      if (old) this.scene.remove(old.group);
      const av = new Avatar(d);
      const a = (i / defs.length) * Math.PI * 2;
      av.position.set(old ? old.position.x : Math.cos(a) * 3, 0, old ? old.position.z : Math.sin(a) * 3);
      av.lookAt(new THREE.Vector3(0, 0, 0));
      this.scene.add(av.group); this.avatars.set(d.id, av);
    });
  }

  setThinking(ids) { for (const [id, av] of this.avatars) av.setThinking(ids.has(id)); }

  // La isla es circular: se mantiene a todos dentro del borde.
  clamp(x, z) {
    const d = Math.hypot(x, z);
    return d > WALK_RADIUS ? [x * WALK_RADIUS / d, z * WALK_RADIUS / d] : [x, z];
  }

  // Resuelve el "target" que devuelve el modelo: nombre de otro personaje, 'centro' o 'x,z'.
  resolveTarget(self, target) {
    const t = String(target || '').trim().toLowerCase();
    for (const av of this.avatars.values()) {
      if (av !== self && av.name.toLowerCase() === t) return { x: av.position.x, z: av.position.z, stop: 1.4, who: av };
    }
    const m = t.match(/^(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)$/);
    if (m) { const [x, z] = this.clamp(+m[1], +m[2]); return { x, z, stop: 0.15 }; }
    return { x: 0, z: 0, stop: 1.6 }; // "centro": se queda junto al cristal, no encima
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
    this.env.update(dt, this.camera);
    this.renderer.render(this.scene, this.camera);
  }
}
