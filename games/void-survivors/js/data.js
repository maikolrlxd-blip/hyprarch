// Datos del juego: todo el balance vive aquí.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const D = (VS.data = {});

  D.MAX_WEAPONS = 4;
  D.MAX_PASSIVES = 5;
  D.tune = { hpA: 0.42, hpB: 0.05, dmg: 1.5, xpA: 3.2, xpB: 0.28 };
  D.xpNeed = (lv) => Math.round(4 + lv * D.tune.xpA + lv * lv * D.tune.xpB);

  // ---- Armas: tabla de estadísticas por nivel (1..6) ----
  const lv = (base, rows) => rows.map((r) => Object.assign({}, base, r));
  D.weapons = {
    pulse: {
      color: '#6ff', max: 6, kind: 'shot',
      levels: lv({ cd: 0.6, n: 1, dmg: 10, pierce: 0, spd: 520 }, [
        {}, { cd: 0.55, dmg: 14 }, { cd: 0.52, n: 2, dmg: 14 }, { cd: 0.48, n: 2, dmg: 18, pierce: 1 },
        { cd: 0.44, n: 3, dmg: 18, pierce: 1 }, { cd: 0.4, n: 3, dmg: 26, pierce: 2 },
      ]),
    },
    orbit: {
      color: '#fd5', max: 6, kind: 'orbit',
      levels: lv({ n: 2, dmg: 15, R: 62, spin: 3.2 }, [
        {}, { dmg: 19 }, { n: 3, dmg: 19, R: 68 }, { n: 3, dmg: 25, spin: 3.8, R: 74 },
        { n: 4, dmg: 25, R: 80 }, { n: 5, dmg: 32, R: 90, spin: 4.2 },
      ]),
    },
    chain: {
      color: '#9bf', max: 6, kind: 'chain',
      levels: lv({ cd: 1.35, dmg: 16, jumps: 2, range: 150 }, [
        {}, { dmg: 22 }, { cd: 1.2, jumps: 3, dmg: 22 }, { cd: 1.1, dmg: 30, jumps: 4, range: 170 },
        { cd: 1.0, dmg: 36, jumps: 6 }, { cd: 0.85, dmg: 46, jumps: 8, range: 190 },
      ]),
    },
    missile: {
      color: '#f96', max: 6, kind: 'missile',
      levels: lv({ cd: 2.1, n: 1, dmg: 26, aoe: 48 }, [
        {}, { dmg: 34 }, { cd: 1.9, n: 2, dmg: 34 }, { cd: 1.8, n: 2, dmg: 44, aoe: 58 },
        { cd: 1.6, n: 3, dmg: 44 }, { cd: 1.4, n: 4, dmg: 56, aoe: 68 },
      ]),
    },
    nova: {
      color: '#f6f', max: 6, kind: 'nova',
      levels: lv({ cd: 3.6, dmg: 24, R: 140, knock: 260 }, [
        {}, { dmg: 32 }, { cd: 3.2, R: 165, dmg: 32 }, { cd: 3.0, dmg: 44, R: 185 },
        { cd: 2.6, dmg: 56, R: 205 }, { cd: 2.2, dmg: 72, R: 230, knock: 340 },
      ]),
    },
    aura: {
      color: '#6f9', max: 6, kind: 'aura',
      levels: lv({ R: 64, dmg: 8, tick: 0.45, slow: 0.25 }, [
        {}, { dmg: 11 }, { R: 76, dmg: 13 }, { R: 88, dmg: 17, tick: 0.4 },
        { R: 100, dmg: 21 }, { R: 115, dmg: 27, tick: 0.35 },
      ]),
    },
  };


  // ---- Evoluciones: arma al nivel máximo + el pasivo indicado => nivel 7 (versión evolucionada) ----
  const evolve = (id, passive, over) => {
    const w = D.weapons[id];
    w.evo = passive;
    w.levels.push(Object.assign({}, w.levels[w.levels.length - 1], over));
  };
  evolve('pulse', 'overclock', { cd: 0.3, n: 5, dmg: 30, pierce: 3, spd: 700 });
  evolve('orbit', 'lens', { n: 7, dmg: 40, R: 105, spin: 5 });
  evolve('chain', 'power', { cd: 0.7, dmg: 60, jumps: 12, range: 220 });
  evolve('missile', 'magnet', { cd: 1.0, n: 6, dmg: 70, aoe: 90 });
  evolve('nova', 'barrier', { cd: 1.6, dmg: 100, R: 280, knock: 420 });
  evolve('aura', 'regen', { R: 135, dmg: 36, tick: 0.3 });

  // ---- Pasivos: efecto por nivel (máx 5) ----
  D.passives = {
    power: { color: '#f66', max: 5, per: 0.12, fmt: '+12% dmg' },
    overclock: { color: '#fc4', max: 5, per: 0.08, fmt: '-8% cd' },
    thrusters: { color: '#4cf', max: 5, per: 0.08, fmt: '+8% vel' },
    plating: { color: '#9d6', max: 5, per: 0.12, fmt: '+12% HP' },
    magnet: { color: '#c8f', max: 5, per: 0.25, fmt: '+25% imán' },
    barrier: { color: '#8af', max: 5, per: 1, fmt: '+1 armadura' },
    scholar: { color: '#6fd', max: 5, per: 0.1, fmt: '+10% XP' },
    regen: { color: '#f9a', max: 5, per: 0.4, fmt: '+0.4 HP/s' },
    lens: { color: '#fa6', max: 5, per: 0.1, fmt: '+10% área' },
    fortune: { color: '#ff6', max: 5, per: 0.05, fmt: '+5% crit' },
  };

  // ---- Enemigos ----
  D.enemies = {
    swarmer:  { hp: 6,   speed: 98, dmg: 5,  r: 7,  xp: 1,  minT: 0,   w: 6,   beh: 'chase', color: '#f55', shape: 'diamond' },
    grunt:    { hp: 18,  speed: 70, dmg: 8,  r: 11, xp: 2,  minT: 0,   w: 5,   beh: 'chase', color: '#f94', shape: 'hex' },
    dasher:   { hp: 14,  speed: 80, dmg: 12, r: 9,  xp: 3,  minT: 50,  w: 2.2, beh: 'dash',  color: '#ff4', shape: 'tri' },
    splitter: { hp: 34,  speed: 60, dmg: 9,  r: 14, xp: 4,  minT: 80,  w: 2,   beh: 'chase', color: '#c6f', shape: 'orb', split: true },
    shooter:  { hp: 20,  speed: 65, dmg: 7,  r: 10, xp: 4,  minT: 100, w: 2,   beh: 'shoot', color: '#4df', shape: 'cannon' },
    tank:     { hp: 110, speed: 42, dmg: 16, r: 18, xp: 10, minT: 150, w: 1,   beh: 'chase', color: '#a86', shape: 'box' },
    hive:     { hp: 1400, speed: 32, dmg: 14, r: 34, xp: 60, beh: 'hive', boss: true, color: '#8f6', shape: 'hive' },
    sentinel: { hp: 2600, speed: 55, dmg: 12, r: 30, xp: 60, beh: 'sentinel', boss: true, color: '#6cf', shape: 'sentinel' },
    jugg:     { hp: 4200, speed: 48, dmg: 24, r: 38, xp: 120, beh: 'jugg', boss: true, color: '#f46', shape: 'jugg' },
  };

  // ---- Fases ----
  D.stages = {
    s1: {
      color: ['#070b1f', '#1a2a5a'], grid: '#1b2a55', duration: 420, cap: 260,
      rate0: 2.2, rateGrow: 2.2, hpMul: 1, dmgMul: 1, spdAdd: 0, coinMul: 1,
      eliteStart: 100, eliteEvery: 50, swarmStart: 75, swarmEvery: 55, w: {},
      bosses: [{ t: 120, type: 'hive' }, { t: 270, type: 'sentinel' }, { t: 420, type: 'jugg', final: true }],
      unlock: null, music: 0,
    },
    s2: {
      color: ['#10061f', '#4a1a6a'], grid: '#3a1f5a', duration: 450, cap: 300,
      rate0: 1.8, rateGrow: 2.95, hpMul: 1.5, dmgMul: 1.15, spdAdd: 0.04, coinMul: 1.7,
      eliteStart: 80, eliteEvery: 42, swarmStart: 60, swarmEvery: 45, w: { shooter: 2.2, dasher: 1.6 },
      bosses: [{ t: 110, type: 'sentinel' }, { t: 270, type: 'hive' }, { t: 450, type: 'jugg', final: true }],
      unlock: 's1', music: 1,
    },
    s3: {
      color: ['#1a0505', '#5a1a10'], grid: '#4a2218', duration: 480, cap: 340,
      rate0: 1.5, rateGrow: 3.2, hpMul: 1.5, dmgMul: 1.25, spdAdd: 0.08, coinMul: 2.8,
      eliteStart: 60, eliteEvery: 35, swarmStart: 50, swarmEvery: 38, w: { tank: 2.2, splitter: 1.8, shooter: 1.8 },
      bosses: [{ t: 100, type: 'jugg' }, { t: 260, type: 'sentinel' }, { t: 480, type: 'hive', final: true }],
      unlock: 's2', music: 2,
    },
  };
  D.stageOrder = ['s1', 's2', 's3'];
  // Dificultades por fase: se desbloquean ganando la anterior. Más difícil = más monedas.
  D.difficulty = [
    { hp: 1, dmg: 1, rate: 1, coin: 1 },
    { hp: 1.5, dmg: 1.25, rate: 1.2, coin: 1.8 },
    { hp: 2.2, dmg: 1.5, rate: 1.4, coin: 3 },
  ];
  D.ASSIST = { xpMul: 1.8, xpUntil: 150, hp: 0.85, dmg: 0.8, giftAt: 25, minCoins: 150, runs: 2 };

  // ---- Naves ----
  D.ships = {
    falcon: { hp: 100, speed: 150, dmg: 1, crit: 0.05, armor: 0, magnet: 0, area: 0, cd: 0, weapons: ['pulse'], color: '#5df', cost: 0 },
    comet:  { hp: 80,  speed: 182, dmg: 1, crit: 0.05, armor: 0, magnet: 0.35, area: 0, cd: 0, weapons: ['chain'], color: '#9bf', cost: 1500 },
    bulwark:{ hp: 160, speed: 126, dmg: 1.25, crit: 0.05, armor: 2, magnet: 0.5, area: 0, cd: 0, weapons: ['orbit', 'aura'], color: '#fd5', cost: 4000 },
    wraith: { hp: 90,  speed: 160, dmg: 1.1, crit: 0.2, armor: 0, magnet: 0, area: 0, cd: 0, weapons: ['missile'], color: '#f96', cost: 0, unlock: { clear: 's1' } },
    nova:   { hp: 110, speed: 150, dmg: 1, crit: 0.05, armor: 0, magnet: 0, area: 0.2, cd: 0.1, weapons: ['nova'], color: '#f6f', cost: 10000 },
  };
  D.shipOrder = ['falcon', 'comet', 'bulwark', 'wraith', 'nova'];

  // ---- Mejoras permanentes (se compran con monedas) ----
  D.metaUpgrades = {
    hp:     { max: 10, base: 90,  grow: 1.42, per: 0.06 },
    dmg:    { max: 10, base: 110, grow: 1.46, per: 0.04 },
    speed:  { max: 8,  base: 100, grow: 1.45, per: 0.03 },
    magnet: { max: 8,  base: 80,  grow: 1.4,  per: 0.1 },
    xp:     { max: 10, base: 120, grow: 1.45, per: 0.05 },
    coin:   { max: 10, base: 150, grow: 1.5,  per: 0.05 },
    armor:  { max: 5,  base: 200, grow: 1.9,  per: 1 },
    regen:  { max: 8,  base: 160, grow: 1.5,  per: 0.15 },
    reroll: { max: 3,  base: 400, grow: 2.2,  per: 1 },
    revive: { max: 2,  base: 3000, grow: 3,   per: 1 },
    choice: { max: 1,  base: 6000, grow: 1,   per: 1 },
  };
  D.metaOrder = ['hp', 'dmg', 'speed', 'magnet', 'xp', 'coin', 'armor', 'regen', 'reroll', 'revive', 'choice'];
  D.metaCost = (id, level) => Math.round(D.metaUpgrades[id].base * Math.pow(D.metaUpgrades[id].grow, level));

  // ---- Misiones diarias: plantillas ----
  // kind: sum = acumulado entre partidas, max = mejor partida
  D.missionTpl = [
    { id: 'kills',  kind: 'sum', stat: 'kills',    goals: [300, 500, 800],  reward: [120, 200, 320] },
    { id: 'coins',  kind: 'sum', stat: 'coins',    goals: [120, 250, 400],  reward: [120, 200, 300] },
    { id: 'runs',   kind: 'sum', stat: 'runs',     goals: [2, 3, 4],        reward: [100, 160, 220] },
    { id: 'boss',   kind: 'sum', stat: 'bossKills',goals: [1, 2, 3],        reward: [150, 260, 400] },
    { id: 'time',   kind: 'max', stat: 'time',     goals: [180, 270, 360],  reward: [120, 200, 320] },
    { id: 'level',  kind: 'max', stat: 'level',    goals: [12, 18, 24],     reward: [120, 200, 320] },
    { id: 'win',    kind: 'sum', stat: 'wins',     goals: [1, 1, 2],        reward: [250, 300, 500] },
  ];
  D.loginRewards = [100, 150, 200, 300, 400, 600, 1000];

  // ---- Logros: stat acumulada + objetivo ----
  D.achievements = [
    { id: 'kills1', stat: 'kills', goal: 100, reward: 100 },
    { id: 'kills2', stat: 'kills', goal: 1500, reward: 300 },
    { id: 'kills3', stat: 'kills', goal: 15000, reward: 1500 },
    { id: 'bosses', stat: 'bossKills', goal: 10, reward: 600 },
    { id: 'runs', stat: 'runs', goal: 25, reward: 400 },
    { id: 'survive', stat: 'bestTime', goal: 300, reward: 300 },
    { id: 'level20', stat: 'maxLevel', goal: 20, reward: 300 },
    { id: 'level35', stat: 'maxLevel', goal: 35, reward: 1000 },
    { id: 'win1', stat: 'win_s1', goal: 1, reward: 500 },
    { id: 'win2', stat: 'win_s2', goal: 1, reward: 1200 },
    { id: 'win3', stat: 'win_s3', goal: 1, reward: 3000 },
    { id: 'rich', stat: 'coinsEarned', goal: 10000, reward: 800 },
    { id: 'ships', stat: 'shipsOwned', goal: 3, reward: 500 },
    { id: 'maxw', stat: 'maxWeaponLevel', goal: 6, reward: 400 },
    { id: 'upg', stat: 'metaLevels', goal: 25, reward: 700 },
    { id: 'evolve', stat: 'evolved', goal: 1, reward: 500 },
    { id: 'evolve2', stat: 'evolved', goal: 25, reward: 1500 },
  ];
})(typeof window !== 'undefined' ? window : globalThis);
