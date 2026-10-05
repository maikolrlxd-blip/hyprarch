'use strict';
const $ = id => document.getElementById(id);
const native = window.AiNative; // puente de la app Android (puede faltar si se abre en un navegador)

// ---- cielo estrellado con estrellas fugaces ----
(() => {
  const cv = $('stars'), g = cv.getContext('2d');
  let w = 0, h = 0, stars = [], shooting = null, nextShot = 2000;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  function resize() {
    w = cv.width = innerWidth * dpr; h = cv.height = innerHeight * dpr;
    stars = Array.from({ length: Math.round(innerWidth * innerHeight / 5000) }, () => ({
      x: Math.random() * w, y: Math.random() * h, r: (0.4 + Math.random() * 1.4) * dpr, p: Math.random() * 6.28, s: 0.6 + Math.random() * 2 }));
  }
  addEventListener('resize', resize); resize();
  let last = performance.now();
  function frame(now) {
    const dt = Math.min(now - last, 50); last = now;
    g.clearRect(0, 0, w, h);
    for (const s of stars) {
      const a = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(now / 1000 * s.s + s.p));
      g.globalAlpha = a; g.fillStyle = '#e9e4ff'; g.beginPath(); g.arc(s.x, s.y, s.r, 0, 6.28); g.fill();
    }
    if (!shooting && (nextShot -= dt) <= 0) {
      shooting = { x: Math.random() * w * 0.8, y: Math.random() * h * 0.35, vx: (0.9 + Math.random() * 0.5) * dpr, vy: (0.45 + Math.random() * 0.3) * dpr, life: 0 };
      nextShot = 3500 + Math.random() * 5000;
    }
    if (shooting) {
      const s = shooting; s.life += dt; s.x += s.vx * dt * 0.9; s.y += s.vy * dt * 0.9;
      const k = 1 - s.life / 900;
      if (k <= 0) shooting = null; else {
        const grad = g.createLinearGradient(s.x, s.y, s.x - s.vx * 90, s.y - s.vy * 90);
        grad.addColorStop(0, `rgba(255,255,255,${k})`); grad.addColorStop(1, 'rgba(255,255,255,0)');
        g.globalAlpha = 1; g.strokeStyle = grad; g.lineWidth = 2 * dpr; g.beginPath(); g.moveTo(s.x, s.y); g.lineTo(s.x - s.vx * 90, s.y - s.vy * 90); g.stroke();
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();

// ---- acciones ----
function showError(msg) { const e = $('err'); e.textContent = msg; e.hidden = !msg; }
window.showError = showError;

$('solo').addEventListener('click', () => { location.href = 'src/renderer/index.html'; });
$('pc').addEventListener('click', () => {
  const open = $('pcPanel').hidden; $('pcPanel').hidden = !open; $('pc').classList.toggle('open', open);
  if (open) $('pcPanel').scrollIntoView({ behavior: 'smooth', block: 'center' });
});

function connect(url) {
  showError('');
  if (!native) return showError('Esta pantalla solo funciona dentro de la app de Android.');
  const err = native.connectPc(url);
  if (err) showError(err);
}
$('go').addEventListener('click', () => connect($('url').value));
$('again').addEventListener('click', () => connect(native.savedPc()));
$('scan').addEventListener('click', () => { showError(''); if (native) native.scanQr(); else showError('El escaner de QR solo esta en la app de Android.'); });
window.onQr = url => { $('url').value = url; connect(url); };

if (native) {
  const saved = native.savedPc();
  if (saved) { $('url').value = saved; $('again').hidden = false; }
  const pending = native.pendingError();
  if (pending) { showError(pending); $('pcPanel').hidden = false; $('pc').classList.add('open'); }
}
