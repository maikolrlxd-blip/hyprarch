// Genera los gráficos de la ficha de Google Play en store/graphics/ usando el propio juego.
// Uso: node tools/store-assets.js   (requiere Playwright + Chromium)
const fs = require('fs'), path = require('path');
let chromium;
try { chromium = require('playwright').chromium; } catch (e) { chromium = require('/opt/node22/lib/node_modules/playwright').chromium; }
const out = path.join(__dirname, '../store/graphics');
const url = 'file://' + path.join(__dirname, '../index.html') + '?dev=1';
fs.mkdirSync(out, { recursive: true });

// Bot (igual que en tools/bot.js) para avanzar la simulación hasta un momento interesante.
const BOT = `
window.__botVec = function (sim) {
  const pl = sim.p; let fx = 0, fy = 0, th = 0;
  for (const e of sim.enemies) { const dx = pl.x - e.x, dy = pl.y - e.y, d2 = dx*dx + dy*dy; if (d2 > 170*170) continue; const d = Math.sqrt(d2) || 1, w = (e.boss ? 2.5 : 1) * (e.speed / 70) * (1 - d / 190) * 2; fx += dx/d*w; fy += dy/d*w; th += w; }
  for (const b of sim.eshots) { const dx = pl.x - b.x, dy = pl.y - b.y, d2 = dx*dx + dy*dy; if (d2 > 110*110) continue; const d = Math.sqrt(d2) || 1; fx += dx/d*3; fy += dy/d*3; th += 3; }
  let best = null, bd = 1e9;
  for (const g of sim.gems) { const d = (g.x-pl.x)**2 + (g.y-pl.y)**2; if (d < bd) { bd = d; best = g; } }
  for (const g of sim.drops) { const d = ((g.x-pl.x)**2 + (g.y-pl.y)**2) * .6; if (d < bd) { bd = d; best = g; } }
  let ix = fx, iy = fy;
  if (best && th < 2.5) { const d = Math.sqrt(bd) || 1; ix = fx*.6 + (best.x-pl.x)/d*1.5; iy = fy*.6 + (best.y-pl.y)/d*1.5; } else { ix += -fy*.35; iy += fx*.35; }
  if (!ix && !iy) ix = 1; const m = Math.hypot(ix, iy) || 1; return { x: ix/m, y: iy/m };
};
window.__ff = function (secs) {          // avanza la simulación 'secs' segundos eligiendo mejoras al vuelo
  const sim = VS.App.sim; const target = sim.t + secs;
  while (sim.t < target && (sim.state === 'running' || sim.state === 'levelup')) {
    if (sim.state === 'levelup') { sim.choose(0); continue; }
    sim.update(1/60, window.__botVec(sim));
    for (const ev of sim.events) VS.App.renderer.event(ev, sim, { numbers: 1, shake: 0 });
    sim.events.length = 0;
  }
  const R = VS.App.renderer; R.update(0.016, sim);
  R.banners.length = 0; R.texts.length = 0; R.booms.length = 0; R.bolts.length = 0;
};`;

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 360, height: 640 }, deviceScaleFactor: 3, hasTouch: true, locale: 'es-ES' });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto(url); await p.waitForTimeout(600);
  await p.addScriptTag({ content: BOT });
  await p.evaluate(() => { // estado de guardado "bonito" para las capturas
    const s = VS.Save.data; s.coins = 4820; s.login.claimed = true; s.cleared.s1 = true; s.ships.comet = true; s.ships.wraith = true;
    s.meta = { hp: 4, dmg: 3, speed: 2, magnet: 3, xp: 2, coin: 2 }; s.stats.runs = 12; s.stats.kills = 6200;
    VS.Meta.ensureDaily(s); s.missions.list[0].progress = Math.floor(s.missions.list[0].goal * 0.7); VS.Meta.normalizeOwnership(s);
    VS.App.home();
  });
  await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(out, 'phone-1-home.png') });

  // Partida: pasa a la fase 2 con el Espectro para que se vea variedad
  await p.evaluate(() => { const s = VS.Save.data; s.selShip = 'wraith'; s.selStage = 's2'; });
  await p.click('[data-a=play]'); await p.waitForTimeout(300);
  await p.evaluate(() => window.__ff(48)); await p.waitForTimeout(100);
  await p.screenshot({ path: path.join(out, 'phone-2-battle.png') });
  await p.evaluate(() => window.__ff(75)); await p.waitForTimeout(100);
  await p.screenshot({ path: path.join(out, 'phone-3-horde.png') });
  await p.evaluate(() => window.__ff(60)); await p.waitForTimeout(100);
  await p.screenshot({ path: path.join(out, 'phone-4-boss.png') });
  // pantalla de subida de nivel
  await p.evaluate(() => { const sim = VS.App.sim; sim.addXp(sim.xpNeed + 1); sim.update(1/60, { x: 0, y: 0 }); });
  await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(out, 'phone-5-levelup.png') });
  await p.evaluate(() => { VS.App.act('quit'); }); await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(out, 'phone-8-results.png') });
  await p.evaluate(() => VS.App.home()); await p.waitForTimeout(200);
  await p.evaluate(() => VS.App.act('upgrades')); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(out, 'phone-6-upgrades.png') });
  await p.evaluate(() => VS.App.act('ships')); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(out, 'phone-7-ships.png') });

  // Icono 512x512 y gráfico de funciones 1024x500 dibujados con los sprites del juego
  const art = await p.evaluate(() => {
    const R = VS.App.renderer;
    const bgGrad = (c, w, h) => { const g = c.createLinearGradient(0, 0, w, h); g.addColorStop(0, '#2a1a7a'); g.addColorStop(0.55, '#10124a'); g.addColorStop(1, '#05060f'); c.fillStyle = g; c.fillRect(0, 0, w, h); };
    const stars = (c, w, h, n) => { c.fillStyle = '#fff'; for (let i = 0; i < n; i++) { c.globalAlpha = 0.2 + Math.random() * 0.7; const r = Math.random() * 2 + 0.5; c.fillRect(Math.random() * w, Math.random() * h, r, r); } c.globalAlpha = 1; };
    const sp = (c, spr, x, y, scale, rot) => { c.save(); c.translate(x, y); c.rotate(rot || 0); c.drawImage(spr.c, -spr.half * scale, -spr.half * scale, spr.half * 2 * scale, spr.half * 2 * scale); c.restore(); };
    // icono
    const ic = document.createElement('canvas'); ic.width = ic.height = 512; const c = ic.getContext('2d');
    bgGrad(c, 512, 512); stars(c, 512, 512, 70);
    const rg = c.createRadialGradient(256, 270, 20, 256, 270, 250); rg.addColorStop(0, 'rgba(90,220,255,.55)'); rg.addColorStop(1, 'rgba(90,220,255,0)'); c.fillStyle = rg; c.fillRect(0, 0, 512, 512);
    const fake = (type, e) => R.spr({ type, elite: !!e });
    for (let i = 0; i < 9; i++) { const a = (i / 9) * Math.PI * 2 + 0.3; sp(c, fake(i % 3 ? 'swarmer' : 'grunt').n, 256 + Math.cos(a) * 205, 262 + Math.sin(a) * 205, 3.1, a + Math.PI / 2); }
    sp(c, R.shipSpr('falcon'), 256, 262, 8.4, 0);
    // gráfico de funciones
    const fg = document.createElement('canvas'); fg.width = 1024; fg.height = 500; const f = fg.getContext('2d');
    bgGrad(f, 1024, 500); stars(f, 1024, 500, 140);
    const rg2 = f.createRadialGradient(780, 250, 10, 780, 250, 330); rg2.addColorStop(0, 'rgba(120,90,255,.5)'); rg2.addColorStop(1, 'rgba(120,90,255,0)'); f.fillStyle = rg2; f.fillRect(0, 0, 1024, 500);
    for (let i = 0; i < 26; i++) { const a = Math.random() * Math.PI * 2, d = 90 + Math.random() * 190; const t = ['swarmer', 'grunt', 'dasher', 'splitter', 'shooter'][i % 5]; sp(f, fake(t).n, 800 + Math.cos(a) * d * 1.05, 250 + Math.sin(a) * d * 0.85, 2.0 + Math.random(), a + Math.PI / 2); }
    sp(f, fake('jugg').n, 880, 150, 2.4, 0.3);
    sp(f, R.shipSpr('falcon'), 790, 270, 6.4, 0.25);
    f.textAlign = 'left'; f.font = '900 92px system-ui,sans-serif'; f.shadowColor = '#6cf'; f.shadowBlur = 24;
    const tg = f.createLinearGradient(0, 130, 0, 330); tg.addColorStop(0, '#fff'); tg.addColorStop(0.6, '#5df'); tg.addColorStop(1, '#c6f');
    f.fillStyle = tg; f.fillText('VOID', 54, 215); f.fillText('SURVIVORS', 54, 308); f.shadowBlur = 0;
    f.font = '600 23px system-ui,sans-serif'; f.fillStyle = '#9fb0ff'; f.fillText('ROGUELITE ESPACIAL  ·  SPACE ROGUELITE', 58, 360);
    return { icon: ic.toDataURL('image/png'), feature: fg.toDataURL('image/png') };
  });
  fs.writeFileSync(path.join(out, 'icon-512.png'), Buffer.from(art.icon.split(',')[1], 'base64'));
  fs.writeFileSync(path.join(out, 'feature-1024x500.png'), Buffer.from(art.feature.split(',')[1], 'base64'));
  console.log('listo en', out, errs.length ? 'ERRORES: ' + errs.join('; ') : 'sin errores');
  await b.close();
})();
