// Iconos vectoriales dibujados en canvas y cacheados como data URL (sin depender de fuentes ni imágenes).
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const TAU = Math.PI * 2, cache = {};

  const DRAW = {
    pulse(c) { [[-14, 0, 5], [0, 0, 6.5], [16, 0, 8]].forEach(([x, y, r]) => { c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); }); },
    orbit(c) { c.lineWidth = 3; c.beginPath(); c.arc(0, 0, 15, 0, TAU); c.stroke(); [0, Math.PI].forEach((a) => { c.save(); c.rotate(a); c.translate(15, 0); c.beginPath(); c.moveTo(0, -9); c.lineTo(5, 0); c.lineTo(0, 9); c.lineTo(-5, 0); c.closePath(); c.fill(); c.restore(); }); c.beginPath(); c.arc(0, 0, 4, 0, TAU); c.fill(); },
    chain(c) { c.beginPath(); c.moveTo(6, -24); c.lineTo(-10, 4); c.lineTo(0, 4); c.lineTo(-6, 24); c.lineTo(12, -6); c.lineTo(2, -6); c.closePath(); c.fill(); },
    missile(c) { c.rotate(-Math.PI / 4); c.beginPath(); c.moveTo(0, -24); c.lineTo(8, -8); c.lineTo(8, 12); c.lineTo(16, 20); c.lineTo(-16, 20); c.lineTo(-8, 12); c.lineTo(-8, -8); c.closePath(); c.fill(); },
    nova(c) { c.lineWidth = 3.5; [8, 16, 24].forEach((r, i) => { c.globalAlpha = 1 - i * 0.28; c.beginPath(); c.arc(0, 0, r, 0, TAU); c.stroke(); }); c.globalAlpha = 1; c.beginPath(); c.arc(0, 0, 4, 0, TAU); c.fill(); },
    aura(c) { c.lineWidth = 3; c.setLineDash([6, 5]); c.beginPath(); c.arc(0, 0, 22, 0, TAU); c.stroke(); c.setLineDash([]); c.globalAlpha = 0.45; c.beginPath(); c.arc(0, 0, 14, 0, TAU); c.fill(); c.globalAlpha = 1; c.beginPath(); c.arc(0, 0, 5, 0, TAU); c.fill(); },
    power(c) { c.beginPath(); for (let i = 0; i < 16; i++) { const a = (i / 16) * TAU, r = i % 2 ? 11 : 24; i ? c.lineTo(Math.cos(a) * r, Math.sin(a) * r) : c.moveTo(Math.cos(a) * r, Math.sin(a) * r); } c.closePath(); c.fill(); },
    overclock(c) { c.lineWidth = 4; c.beginPath(); c.arc(0, 0, 16, 0.4, TAU - 0.9); c.stroke(); c.beginPath(); c.moveTo(14, -22); c.lineTo(22, -6); c.lineTo(4, -8); c.closePath(); c.fill(); c.beginPath(); c.moveTo(0, 0); c.lineTo(0, -10); c.lineWidth = 3; c.stroke(); },
    thrusters(c) { [-9, 5].forEach((y) => { c.beginPath(); c.moveTo(-18, y + 12); c.lineTo(0, y - 4); c.lineTo(18, y + 12); c.lineTo(18, y + 20); c.lineTo(0, y + 4); c.lineTo(-18, y + 20); c.closePath(); c.fill(); }); },
    plating(c) { c.beginPath(); c.moveTo(0, -24); c.lineTo(20, -16); c.lineTo(18, 6); c.quadraticCurveTo(14, 18, 0, 25); c.quadraticCurveTo(-14, 18, -18, 6); c.lineTo(-20, -16); c.closePath(); c.fill(); c.fillStyle = 'rgba(0,0,0,.35)'; c.fillRect(-3, -14, 6, 24); c.fillRect(-10, -6, 20, 6); },
    magnet(c) { c.lineWidth = 9; c.beginPath(); c.arc(0, -2, 14, Math.PI, 0); c.lineTo(14, 16); c.moveTo(-14, -2); c.lineTo(-14, 16); c.stroke(); c.fillStyle = '#fff'; c.fillRect(-19, 14, 10, 8); c.fillRect(9, 14, 10, 8); },
    barrier(c) { c.lineWidth = 5; c.beginPath(); for (let i = 0; i < 6; i++) { const a = (i / 6) * TAU - Math.PI / 2; i ? c.lineTo(Math.cos(a) * 22, Math.sin(a) * 22) : c.moveTo(Math.cos(a) * 22, Math.sin(a) * 22); } c.closePath(); c.stroke(); c.beginPath(); c.arc(0, 0, 7, 0, TAU); c.fill(); },
    scholar(c) { c.fillRect(-14, -14, 28, 28); c.lineWidth = 3; for (let i = -1; i <= 1; i += 2) for (let k = -1; k <= 1; k++) { c.beginPath(); c.moveTo(i * 14, k * 8); c.lineTo(i * 22, k * 8); c.stroke(); c.beginPath(); c.moveTo(k * 8, i * 14); c.lineTo(k * 8, i * 22); c.stroke(); } c.fillStyle = 'rgba(0,0,0,.4)'; c.fillRect(-7, -7, 14, 14); },
    regen(c) { c.fillRect(-6, -22, 12, 44); c.fillRect(-22, -6, 44, 12); },
    lens(c) { c.lineWidth = 3.5; c.beginPath(); c.arc(0, 0, 14, 0, TAU); c.stroke(); [[-24, -10], [10, 24]].forEach(([a, b]) => { c.beginPath(); c.moveTo(a, 0); c.lineTo(b, 0); c.stroke(); c.beginPath(); c.moveTo(0, a); c.lineTo(0, b); c.stroke(); }); c.beginPath(); c.arc(0, 0, 4, 0, TAU); c.fill(); },
    fortune(c) { for (let i = 0; i < 4; i++) { c.save(); c.rotate((i / 4) * TAU); c.beginPath(); c.arc(0, -11, 9.5, 0, TAU); c.fill(); c.restore(); } c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.arc(0, 0, 4, 0, TAU); c.fill(); },
    coin(c) { c.beginPath(); c.arc(0, 0, 21, 0, TAU); c.fill(); c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.arc(0, 0, 11, 0, TAU); c.fill(); },
    heart(c) { c.beginPath(); c.moveTo(0, 20); c.bezierCurveTo(-30, 0, -20, -22, 0, -8); c.bezierCurveTo(20, -22, 30, 0, 0, 20); c.fill(); },
    skull(c) { c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(-16, -16); c.lineTo(16, 16); c.moveTo(16, -16); c.lineTo(-16, 16); c.stroke(); },
    clock(c) { c.lineWidth = 4; c.beginPath(); c.arc(0, 0, 20, 0, TAU); c.stroke(); c.beginPath(); c.moveTo(0, -12); c.lineTo(0, 0); c.lineTo(10, 6); c.stroke(); },
    gear(c) { c.beginPath(); for (let i = 0; i < 16; i++) { const a = (i / 16) * TAU, r = i % 2 ? 17 : 23; c.lineTo(Math.cos(a) * r, Math.sin(a) * r); } c.closePath(); c.fill(); c.globalCompositeOperation = 'destination-out'; c.beginPath(); c.arc(0, 0, 8, 0, TAU); c.fill(); },
    ship(c) { c.beginPath(); c.moveTo(0, -24); c.lineTo(20, 20); c.lineTo(0, 9); c.lineTo(-20, 20); c.closePath(); c.fill(); },
    up(c) { c.beginPath(); c.moveTo(0, -22); c.lineTo(20, 2); c.lineTo(8, 2); c.lineTo(8, 22); c.lineTo(-8, 22); c.lineTo(-8, 2); c.lineTo(-20, 2); c.closePath(); c.fill(); },
    mission(c) { c.lineWidth = 4; c.strokeRect(-16, -20, 32, 40); c.beginPath(); c.moveTo(-8, -6); c.lineTo(8, -6); c.moveTo(-8, 4); c.lineTo(8, 4); c.moveTo(-8, 14); c.lineTo(2, 14); c.stroke(); },
    trophy(c) { c.beginPath(); c.moveTo(-14, -20); c.lineTo(14, -20); c.lineTo(11, 4); c.quadraticCurveTo(0, 16, -11, 4); c.closePath(); c.fill(); c.fillRect(-3, 8, 6, 8); c.fillRect(-11, 16, 22, 5); c.lineWidth = 3.5; c.beginPath(); c.arc(-16, -9, 6, Math.PI / 2, -Math.PI / 2); c.stroke(); c.beginPath(); c.arc(16, -9, 6, -Math.PI / 2, Math.PI / 2); c.stroke(); },
    lock(c) { c.fillRect(-14, -2, 28, 22); c.lineWidth = 5; c.beginPath(); c.arc(0, -6, 9, Math.PI, 0); c.stroke(); },
    check(c) { c.lineWidth = 7; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(-16, 2); c.lineTo(-5, 14); c.lineTo(17, -12); c.stroke(); },
    pause(c) { c.fillRect(-14, -18, 9, 36); c.fillRect(5, -18, 9, 36); },
    ad(c) { c.beginPath(); c.moveTo(-14, -18); c.lineTo(20, 0); c.lineTo(-14, 18); c.closePath(); c.fill(); },
  };

  VS.icon = function (id, color, size) {
    const key = id + color + (size || 64);
    if (cache[key]) return cache[key];
    const fn = DRAW[id];
    if (!fn || !g.document) return '';
    const s = size || 64, c = g.document.createElement('canvas');
    c.width = c.height = s;
    const x = c.getContext('2d');
    x.translate(s / 2, s / 2); x.scale(s / 64, s / 64);
    x.fillStyle = x.strokeStyle = color || '#fff';
    x.shadowColor = color || '#fff'; x.shadowBlur = 5;
    fn(x);
    return (cache[key] = c.toDataURL());
  };
  VS.iconImg = (id, color, cls) => `<img class="ic ${cls || ''}" alt="" src="${VS.icon(id, color)}">`;
})(typeof window !== 'undefined' ? window : globalThis);
