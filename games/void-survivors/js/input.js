// Entrada: joystick flotante táctil/ratón + teclado (WASD / flechas).
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const keys = {};
  const I = (VS.Input = { x: 0, y: 0, active: false, show: true, ox: 0, oy: 0, max: 58, id: null, fixed: false, enabled: false });

  I.attach = function (el) {
    el.addEventListener('pointerdown', (e) => {
      if (!I.enabled || I.id !== null) return;
      I.id = e.pointerId; I.active = true;
      I.ox = e.clientX; I.oy = e.clientY;
      if (I.fixed) { I.ox = 90; I.oy = g.innerHeight - 110; }
      I.move(e);
      try { el.setPointerCapture(e.pointerId); } catch (err) { /* ok */ }
    });
    el.addEventListener('pointermove', (e) => { if (e.pointerId === I.id) I.move(e); });
    const up = (e) => { if (e.pointerId === I.id) I.release(); };
    el.addEventListener('pointerup', up);
    el.addEventListener('pointercancel', up);
    el.addEventListener('contextmenu', (e) => e.preventDefault());
    g.addEventListener('keydown', (e) => { keys[e.code] = 1; });
    g.addEventListener('keyup', (e) => { keys[e.code] = 0; });
    g.addEventListener('blur', () => { I.release(); for (const k in keys) keys[k] = 0; });
  };
  I.move = function (e) {
    let dx = e.clientX - I.ox, dy = e.clientY - I.oy;
    const d = Math.hypot(dx, dy);
    if (d > I.max) { // el origen sigue al dedo para no tener que volver al centro
      if (!I.fixed) { I.ox += (dx / d) * (d - I.max); I.oy += (dy / d) * (d - I.max); }
      dx = (dx / d) * I.max; dy = (dy / d) * I.max;
    }
    I.tx = dx / I.max; I.ty = dy / I.max;
    I.x = I.tx; I.y = I.ty;
  };
  I.release = function () { I.id = null; I.active = false; I.x = 0; I.y = 0; };
  // Vector final (combina joystick y teclado).
  I.vector = function () {
    let kx = (keys.ArrowRight || keys.KeyD ? 1 : 0) - (keys.ArrowLeft || keys.KeyA ? 1 : 0);
    let ky = (keys.ArrowDown || keys.KeyS ? 1 : 0) - (keys.ArrowUp || keys.KeyW ? 1 : 0);
    if (kx || ky) { const m = Math.hypot(kx, ky); return { x: kx / m, y: ky / m }; }
    // pequeña zona muerta
    const m = Math.hypot(I.x, I.y);
    if (m < 0.12) return { x: 0, y: 0 };
    return { x: I.x, y: I.y };
  };
})(typeof window !== 'undefined' ? window : globalThis);
