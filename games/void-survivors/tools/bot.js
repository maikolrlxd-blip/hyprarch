// Bot de prueba: huye de la densidad de enemigos, recoge gemas/monedas y elige mejoras con prioridades.
const load = require('./loadsim');
const VS = load();
const U = VS.util, D = VS.data;

function mulberry(seed) { return U.rng(seed); }

function botInput(sim, skill) {
  const p = sim.p;
  let fx = 0, fy = 0, threat = 0;
  for (const e of sim.enemies) {
    const dx = p.x - e.x, dy = p.y - e.y, d2 = dx * dx + dy * dy;
    if (d2 > 170 * 170) continue;
    const d = Math.sqrt(d2) || 1, w = (e.boss ? 2.5 : 1) * (e.speed / 70) * (1 - d / 190) * 2;
    fx += (dx / d) * w; fy += (dy / d) * w; threat += w;
  }
  for (const b of sim.eshots) {
    const dx = p.x - b.x, dy = p.y - b.y, d2 = dx * dx + dy * dy;
    if (d2 > 110 * 110) continue;
    const d = Math.sqrt(d2) || 1; fx += (dx / d) * 3; fy += (dy / d) * 3; threat += 3;
  }
  let best = null, bd = 1e9;
  for (const g of sim.gems) { const d = (g.x - p.x) ** 2 + (g.y - p.y) ** 2; if (d < bd) { bd = d; best = g; } }
  for (const g of sim.drops) { const d = ((g.x - p.x) ** 2 + (g.y - p.y) ** 2) * 0.6; if (d < bd) { bd = d; best = g; } }
  let ix = fx, iy = fy;
  if (best && threat < 2.5 * skill) {
    const d = Math.sqrt(bd) || 1;
    ix = fx * 0.6 + ((best.x - p.x) / d) * 1.5; iy = fy * 0.6 + ((best.y - p.y) / d) * 1.5;
  } else if (!best || threat >= 2.5 * skill) {
    // si se ve acorralado, rodea en lugar de pararse
    ix += -fy * 0.35; iy += fx * 0.35;
  }
  if (!ix && !iy) { ix = Math.cos(sim.t * 0.5); iy = Math.sin(sim.t * 0.5); }
  const m = Math.hypot(ix, iy) || 1;
  return { x: ix / m, y: iy / m };
}

const PREF = ['pulse', 'missile', 'chain', 'nova', 'orbit', 'aura'];
function botChoose(sim) {
  const c = sim.choices;
  let bi = 0, bs = -1;
  c.forEach((o, i) => {
    let s = 1;
    if (o.evo) s = 20;
    else if (o.kind === 'weapon') s = 5 + (o.level > 1 ? 3 : 0) - PREF.indexOf(o.id) * 0.3;
    else if (o.kind === 'passive') s = ({ power: 4, overclock: 5, lens: 3, magnet: 3, barrier: 3, regen: 3.5, plating: 3, regen: 3, thrusters: 2.5, magnet: 2, barrier: 3 })[o.id] || 1.5;
    if (s > bs) { bs = s; bi = i; }
  });
  sim.choose(bi);
}

function run(opts) {
  const s = VS.Save.defaults();
  Object.assign(s.meta, opts.meta || {});
  const sim = new VS.Sim({ ship: opts.ship || 'falcon', stage: opts.stage || 's1', meta: VS.Meta.bonuses(s), rand: mulberry(opts.seed || 1), events: false });
  const dt = 1 / 60, skill = opts.skill || 1;
  const stats = { maxEn: 0, ticks: 0 };
  let guard = 0;
  while ((sim.state === 'running' || sim.state === 'levelup') && sim.t < 700 && guard++ < 60 * 800) {
    if (sim.state === 'levelup') { botChoose(sim); continue; }
    sim.update(dt, botInput(sim, skill));
    stats.maxEn = Math.max(stats.maxEn, sim.enemies.length);
  }
  const r = sim.result();
  r.state = sim.state; r.maxEn = stats.maxEn; r.dmgTaken = Math.round(sim.dmgTaken);
  return r;
}
module.exports = { run, VS, botInput, botChoose };

if (require.main === module) {
  const n = +process.argv[2] || 5, stage = process.argv[3] || 's1', ship = process.argv[4] || 'falcon';
  const meta = process.argv[5] ? JSON.parse(process.argv[5]) : {};
  let wins = 0, tt = 0, tl = 0, tc = 0;
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const r = run({ seed: 100 + i, stage, ship, meta, skill: +process.env.SKILL || 1 });
    if (r.won) wins++;
    tt += r.time; tl += r.level; tc += r.coins;
    console.log(`seed ${100 + i}: ${r.state} t=${r.time.toFixed(0)}s lvl=${r.level} kills=${r.kills} coins=${r.coins} boss=${r.bossKills} maxEn=${r.maxEn} dmgTaken=${r.dmgTaken}`);
  }
  console.log(`\n${stage}/${ship}: wins ${wins}/${n}  avgTime ${(tt / n).toFixed(0)}s  avgLvl ${(tl / n).toFixed(1)}  avgCoins ${(tc / n).toFixed(0)}  (${Date.now() - t0}ms)`);
}
