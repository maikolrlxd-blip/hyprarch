// Graba clips verticales (salida 1080x1920) de gameplay real para redes y para el vídeo de la ficha.
// Uso: node tools/make-clips.js   (necesita Playwright, Chromium y ffmpeg). Salida: store/video/*.mp4 (sin audio)
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
let chromium; try { chromium = require('playwright').chromium; } catch (e) { chromium = require('/opt/node22/lib/node_modules/playwright').chromium; }
const root = path.join(__dirname, '..'), out = path.join(root, 'store/video'), tmp = path.join(out, '.tmp');
fs.mkdirSync(tmp, { recursive: true });
const url = 'file://' + path.join(root, 'index.html');
const BOT = fs.readFileSync(path.join(__dirname, 'store-assets.js'), 'utf8').match(/const BOT = `([\s\S]*?)`;/)[1];

async function clip(browser, name, setup, secs) {
  const ctx = await browser.newContext({ viewport: { width: 405, height: 720 }, deviceScaleFactor: 1, hasTouch: true, locale: 'es-ES',
    recordVideo: { dir: tmp, size: { width: 405, height: 720 } } });
  const p = await ctx.newPage();
  await p.goto(url); await p.waitForTimeout(500);
  await p.addScriptTag({ content: BOT });
  await p.evaluate(() => { // guardado con progreso para que se vean más cosas
    const s = VS.Save.data; s.tutorial.started = true; s.tutorial.done = true; s.stats.runs = 20; s.login.claimed = true; s.cleared.s1 = true; s.diffUnlocked.s1 = 1;
    s.ships.wraith = true; s.meta = { hp: 6, dmg: 6, speed: 3, magnet: 4, xp: 4, armor: 2, regen: 3 };
    VS.Input.vector = () => VS.App.sim ? window.__botVec(VS.App.sim) : { x: 0, y: 0 };
    VS.App.home();
  });
  await p.waitForTimeout(400);
  await setup(p);
  await p.waitForTimeout(secs * 1000);
  const vid = p.video(); await ctx.close();
  const src = await vid.path(), dst = path.join(out, name + '.mp4');
  execSync(`ffmpeg -y -loglevel error -i "${src}" -vf "fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -crf 22 -movflags +faststart "${dst}"`);
  console.log('ok', dst, (fs.statSync(dst).size / 1e6).toFixed(1) + ' MB');
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
  const start = async (p, ship, stage, ff) => {
    await p.evaluate(([ship, stage]) => { const s = VS.Save.data; s.selShip = ship; s.selStage = stage; s.selDiff = 0; }, [ship, stage]);
    await p.click('[data-a=play]'); await p.waitForTimeout(200);
    if (ff) await p.evaluate((t) => window.__ff(t), ff);
  };
  await clip(b, 'clip-horda', (p) => start(p, 'falcon', 's1', 150), 22);
  await clip(b, 'clip-jefe', (p) => start(p, 'wraith', 's2', 100), 24);
  await clip(b, 'clip-evolucion', async (p) => {
    await start(p, 'falcon', 's1', 60);
    await p.evaluate(() => { const s = VS.App.sim; s.weapons[0].level = 6; s.passives.overclock = 1; s.recompute(); s.addXp(s.xpNeed + 1); });
    await p.waitForTimeout(1500);
    const evo = p.locator('.choice.evo');
    if (await evo.count()) { await evo.click({ force: true }); } else { await p.locator('.choice').first().click({ force: true }); }
  }, 16);
  await b.close();
  fs.rmSync(tmp, { recursive: true, force: true });
})();
