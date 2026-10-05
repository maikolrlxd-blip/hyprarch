// Pruebas de lógica sin DOM: node tools/test.js
const assert = require('assert');
const load = require('./loadsim');
const VS = load();
const { Meta: M, Save, data: D, util: U } = VS;
let n = 0;
const ok = (name, fn) => { fn(); n++; console.log('  ✓ ' + name); };
const fresh = () => Save.defaults();
const J = JSON.stringify;
const same = (a, b) => assert.strictEqual(J(a), J(b));
const differ = (a, b) => assert.notStrictEqual(J(a), J(b));

console.log('Meta-progresión');
ok('misiones diarias deterministas por fecha, 3 distintas', () => {
  const a = fresh(), b = fresh(), c = fresh();
  M.ensureDaily(a, '2026-10-05'); M.ensureDaily(b, '2026-10-05'); M.ensureDaily(c, '2026-10-06');
  same(a.missions.list, b.missions.list);
  assert.strictEqual(new Set(a.missions.list.map((m) => m.id)).size, 3);
  differ(a.missions.list.map((m) => m.id), c.missions.list.map((m) => m.id));
  assert.strictEqual(M.ensureDaily(a, '2026-10-05'), false); // no se regeneran el mismo día
});
ok('racha de login: consecutivo suma, hueco reinicia', () => {
  const s = fresh();
  assert.ok(M.updateLogin(s, '2026-10-01')); assert.strictEqual(s.login.streak, 1);
  assert.ok(M.updateLogin(s, '2026-10-02')); assert.strictEqual(s.login.streak, 2);
  assert.strictEqual(M.updateLogin(s, '2026-10-02'), false);
  M.updateLogin(s, '2026-10-05'); assert.strictEqual(s.login.streak, 1);
  const r = M.claimLogin(s); assert.strictEqual(r, D.loginRewards[0]); assert.strictEqual(M.claimLogin(s), 0);
  assert.strictEqual(s.coins, D.loginRewards[0]);
});
ok('racha de 8 días vuelve al día 1 del ciclo', () => {
  const s = fresh(); s.login.streak = 8; assert.strictEqual(M.loginReward(s), D.loginRewards[0]);
});
ok('comprar mejoras: coste, límite y saldo', () => {
  const s = fresh(); s.coins = 100;
  assert.ok(M.buyUpgrade(s, 'hp')); assert.strictEqual(s.coins, 100 - D.metaCost('hp', 0)); assert.strictEqual(M.level(s, 'hp'), 1);
  s.coins = 0; assert.strictEqual(M.buyUpgrade(s, 'hp'), false);
  s.coins = 1e9; for (let i = 0; i < 20; i++) M.buyUpgrade(s, 'choice');
  assert.strictEqual(M.level(s, 'choice'), 1);
  assert.strictEqual(M.bonuses(s).choice, 1);
});
ok('comprar naves y desbloqueo por victoria', () => {
  const s = fresh(); s.coins = 1500;
  assert.ok(M.buyShip(s, 'comet')); assert.ok(M.shipOwned(s, 'comet')); assert.strictEqual(M.buyShip(s, 'comet'), false);
  assert.ok(!M.shipOwned(s, 'wraith')); assert.strictEqual(M.buyShip(s, 'wraith'), false);
  const sum = M.applyRun(s, { won: true, time: 420, kills: 1000, coins: 200, level: 20, bossKills: 3, stage: 's1', ship: 'falcon', maxWeaponLevel: 4 });
  same(sum.newShips, ['wraith']); assert.ok(M.shipOwned(s, 'wraith')); assert.ok(M.stageUnlocked(s, 's2'));
});
ok('applyRun: monedas, bonus de victoria, récords y estadísticas', () => {
  const s = fresh();
  const r1 = M.applyRun(s, { won: false, time: 100, kills: 50, coins: 30, level: 5, bossKills: 0, stage: 's1', ship: 'falcon', maxWeaponLevel: 2 });
  assert.strictEqual(r1.total, 30); assert.strictEqual(s.coins, 30); assert.ok(r1.newBest);
  const r2 = M.applyRun(s, { won: false, time: 60, kills: 20, coins: 10, level: 3, bossKills: 0, stage: 's1', ship: 'falcon' });
  assert.ok(!r2.newBest); assert.strictEqual(s.best.s1.time, 100);
  const r3 = M.applyRun(s, { won: true, time: 430, kills: 1500, coins: 100, level: 25, bossKills: 3, stage: 's1', ship: 'falcon', maxWeaponLevel: 6 });
  assert.strictEqual(r3.bonus, 150); assert.strictEqual(s.stats.runs, 3); assert.strictEqual(s.stats.wins, 1);
  assert.strictEqual(s.stats.bossKills, 3); assert.strictEqual(s.stats.maxWeaponLevel, 6); assert.ok(s.cleared.s1);
  assert.ok(s.best.s1.won);
  const r4 = M.applyRun(s, { won: false, time: 300, kills: 10, coins: 0, level: 3, bossKills: 0, stage: 's1', ship: 'falcon' });
  assert.ok(s.best.s1.won, 'una derrota posterior no borra la victoria');
});
ok('misiones avanzan con las partidas y se reclaman una sola vez', () => {
  const s = fresh(); M.ensureDaily(s, '2026-10-05');
  s.missions.list = [{ id: 'kills', tier: 0, goal: 300, reward: 120, progress: 0, claimed: false }, { id: 'time', tier: 1, goal: 270, reward: 200, progress: 0, claimed: false }, { id: 'runs', tier: 2, goal: 4, reward: 220, progress: 0, claimed: false }];
  const run = { won: false, time: 280, kills: 200, coins: 5, level: 8, bossKills: 0, stage: 's1', ship: 'falcon' };
  M.applyRun(s, run); M.applyRun(s, run);
  assert.strictEqual(s.missions.list[0].progress, 300); // 400 recortado a la meta
  assert.strictEqual(s.missions.list[1].progress, 270);
  assert.strictEqual(s.missions.list[2].progress, 2);
  const c0 = s.coins;
  assert.strictEqual(M.claimMission(s, 0), 120); assert.strictEqual(M.claimMission(s, 0), 0); assert.strictEqual(M.claimMission(s, 2), 0);
  assert.strictEqual(s.coins, c0 + 120);
});
ok('logros: listos al cumplir meta, reclamables una vez', () => {
  const s = fresh(); const a = D.achievements.find((x) => x.id === 'kills1');
  assert.ok(!M.achReady(s, a)); s.stats.kills = 100; assert.ok(M.achReady(s, a));
  assert.strictEqual(M.claimAch(s, 'kills1'), a.reward); assert.strictEqual(M.claimAch(s, 'kills1'), 0);
  assert.ok(M.claimable(fresh()) === 0);
});

console.log('Guardado');
ok('Save: carga datos parciales/antiguos, guarda, tolera JSON corrupto y resetea', () => {
  const vm = require('vm'), fs = require('fs'), path = require('path');
  const store = {};
  const ctx = vm.createContext({ Math, console, Date, localStorage: { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = v; } } });
  ctx.globalThis = ctx;
  for (const f of ['util', 'data', 'save', 'meta']) vm.runInContext(fs.readFileSync(path.join(__dirname, '../js', f + '.js'), 'utf8'), ctx);
  const S = ctx.VS.Save;
  store.void_survivors_save = JSON.stringify({ coins: 777, ships: { falcon: true, comet: true }, settings: { sound: 0 }, futuro: 1 });
  const d = S.load();
  assert.strictEqual(d.coins, 777); assert.ok(d.ships.comet); assert.strictEqual(d.settings.sound, 0); assert.strictEqual(d.settings.music, 1);
  assert.ok('kills' in d.stats);
  d.coins = 5; S.save(); assert.strictEqual(JSON.parse(store.void_survivors_save).coins, 5);
  store.void_survivors_save = '{not json'; assert.strictEqual(S.load().coins, 0);
  S.reset(); assert.strictEqual(JSON.parse(store.void_survivors_save).coins, 0);
});

console.log('Simulación');
const mkSim = (o) => new VS.Sim(Object.assign({ ship: 'falcon', stage: 's1', meta: M.bonuses(fresh()), rand: U.rng(7), events: true }, o));
ok('cada nave y fase se simulan 40 s sin NaN y con eventos válidos', () => {
  for (const ship of D.shipOrder) for (const stage of D.stageOrder) {
    const sim = mkSim({ ship, stage });
    for (let i = 0; i < 40 * 60; i++) {
      if (sim.state === 'levelup') sim.choose(0);
      sim.update(1 / 60, { x: Math.cos(i / 90), y: Math.sin(i / 70) });
      sim.events.length = 0;
    }
    for (const v of [sim.p.x, sim.p.y, sim.p.hp, sim.xp]) assert.ok(Number.isFinite(v), `${ship}/${stage}: valor no finito`);
    for (const e of sim.enemies) assert.ok(Number.isFinite(e.x) && Number.isFinite(e.y) && Number.isFinite(e.hp));
  }
});
ok('las 6 armas funcionan a nivel 1 y 6', () => {
  for (const w of Object.keys(D.weapons)) for (const lv of [1, 6]) {
    const sim = mkSim({ ship: 'falcon' });
    sim.weapons = []; const wp = sim.addWeapon(w); wp.level = lv;
    let dealt = 0;
    for (let i = 0; i < 25 * 60; i++) { sim.update(1 / 60, { x: 0.3, y: 0 }); sim.events.length = 0; if (sim.state === 'levelup') sim.choose(0); }
    assert.ok(sim.dmgDone > 0, `${w} nivel ${lv} no hizo daño`);
  }
});
ok('subir de nivel congela la simulación hasta elegir; reroll gasta un cambio', () => {
  const s = fresh(); s.meta.reroll = 2; s.meta.choice = 1;
  const sim = mkSim({ meta: M.bonuses(s) });
  sim.addXp(sim.xpNeed + 1); sim.update(1 / 60, null);
  assert.strictEqual(sim.state, 'levelup'); assert.strictEqual(sim.choices.length, 4);
  const t0 = sim.t; sim.update(1 / 60, null); assert.strictEqual(sim.t, t0);
  assert.ok(sim.reroll()); assert.strictEqual(sim.rerolls, 1);
  sim.choose(0); assert.strictEqual(sim.state, 'running');
});
ok('las opciones nunca repiten ni superan los huecos de armas/pasivos', () => {
  const sim = mkSim();
  for (let k = 0; k < 60; k++) {
    sim.addXp(sim.xpNeed + 1); sim.update(1 / 60, null);
    if (sim.state === 'levelup') {
      const keys = sim.choices.map((c) => c.kind + c.id); assert.strictEqual(new Set(keys).size, keys.length);
      sim.choose(Math.floor(Math.random() * sim.choices.length));
    }
  }
  assert.ok(sim.weapons.length <= D.MAX_WEAPONS); assert.ok(Object.keys(sim.passives).length <= D.MAX_PASSIVES);
  for (const w of sim.weapons) assert.ok(w.level <= D.weapons[w.id].max);
});
ok('resurrección: consume una vida y devuelve a running', () => {
  const s = fresh(); s.meta.revive = 1;
  const sim = mkSim({ meta: M.bonuses(s) });
  sim.p.hp = -1; sim.update(1 / 60, null); assert.strictEqual(sim.state, 'running'); assert.strictEqual(sim.revives, 0); assert.ok(sim.p.hp > 0 && sim.p.inv > 2);
  sim.p.hp = -1; sim.update(1 / 60, null); assert.strictEqual(sim.state, 'dead');
  assert.ok(sim.adRevive()); assert.strictEqual(sim.state, 'running'); assert.ok(!sim.adRevive());
});
ok('derrotar al jefe final gana la partida', () => {
  const sim = mkSim();
  const boss = sim.spawn('jugg', 100, 100, { final: true });
  sim.damage(boss, 1e9, 0, 0, true); assert.strictEqual(sim.state, 'won');
  assert.ok(sim.result().won);
});
ok('el director genera jefes en su momento y respeta el tope de enemigos', () => {
  const sim = mkSim({ stage: 's3' });
  let maxEn = 0, bosses = 0;
  sim.weapons = [];
  for (let i = 0; i < 130 * 60; i++) { sim.p.hp = sim.st.maxHp; sim.update(1 / 60, null); for (const e of sim.events) if (e.type === 'boss') bosses++; sim.events.length = 0; maxEn = Math.max(maxEn, sim.enemies.length); }
  assert.ok(bosses >= 1, 'debe haber aparecido el primer jefe'); assert.ok(maxEn < D.stages.s3.cap + 120, 'tope razonable: ' + maxEn);
});

console.log(`\n${n} pruebas OK`);
