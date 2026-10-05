// Meta-progresión: mejoras permanentes, naves, misiones diarias, logros y racha de login.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const U = VS.util, D = VS.data;

  const Meta = (VS.Meta = {});

  Meta.level = (s, id) => s.meta[id] || 0;
  Meta.upgradeCost = (s, id) => D.metaCost(id, Meta.level(s, id));

  Meta.buyUpgrade = function (s, id) {
    const u = D.metaUpgrades[id], lv = Meta.level(s, id);
    if (!u || lv >= u.max) return false;
    const c = D.metaCost(id, lv);
    if (s.coins < c) return false;
    s.coins -= c;
    s.meta[id] = lv + 1;
    return true;
  };

  // Bonos que el simulador usa al empezar la partida.
  Meta.bonuses = function (s) {
    const L = (id) => Meta.level(s, id), P = D.metaUpgrades;
    return {
      hp: L('hp') * P.hp.per, dmg: L('dmg') * P.dmg.per, speed: L('speed') * P.speed.per,
      magnet: L('magnet') * P.magnet.per, xp: L('xp') * P.xp.per, coin: L('coin') * P.coin.per,
      armor: L('armor') * P.armor.per, regen: L('regen') * P.regen.per,
      rerolls: L('reroll'), revives: L('revive'), choice: L('choice'),
    };
  };

  // ---- Naves ----
  Meta.shipUnlockedByRule = (s, id) => {
    const u = D.ships[id].unlock;
    return !!(u && u.clear && s.cleared[u.clear]);
  };
  Meta.shipOwned = (s, id) => !!s.ships[id] || (D.ships[id].cost === 0 && !D.ships[id].unlock) || Meta.shipUnlockedByRule(s, id);
  Meta.buyShip = function (s, id) {
    const sh = D.ships[id];
    if (!sh || Meta.shipOwned(s, id) || !sh.cost || s.coins < sh.cost) return false;
    s.coins -= sh.cost;
    s.ships[id] = true;
    return true;
  };
  Meta.normalizeOwnership = function (s) {
    for (const id of D.shipOrder) if (Meta.shipOwned(s, id)) s.ships[id] = true;
    if (!s.ships[s.selShip]) s.selShip = 'falcon';
  };
  Meta.stageUnlocked = (s, id) => !D.stages[id].unlock || !!s.cleared[D.stages[id].unlock];

  // ---- Misiones diarias ----
  Meta.ensureDaily = function (s, today) {
    today = today || U.today();
    if (s.missions.day === today && s.missions.list.length) return false;
    const rand = U.rng(U.hash('missions' + today));
    const pool = D.missionTpl.slice();
    const list = [];
    for (let slot = 0; slot < 3; slot++) {
      const tpl = pool.splice(Math.floor(rand() * pool.length), 1)[0];
      list.push({ id: tpl.id, tier: slot, goal: tpl.goals[slot], reward: tpl.reward[slot], progress: 0, claimed: false });
    }
    s.missions = { day: today, list };
    return true;
  };

  // ---- Racha de login ----
  Meta.updateLogin = function (s, today) {
    today = today || U.today();
    if (s.login.last === today) return false;
    const gap = s.login.last ? U.daysBetween(s.login.last, today) : 99;
    s.login.streak = gap === 1 ? s.login.streak + 1 : 1;
    s.login.last = today;
    s.login.claimed = false;
    return true;
  };
  Meta.loginReward = (s) => D.loginRewards[(Math.max(1, s.login.streak) - 1) % D.loginRewards.length];
  Meta.claimLogin = function (s) {
    if (s.login.claimed) return 0;
    s.login.claimed = true;
    const r = Meta.loginReward(s);
    s.coins += r;
    return r;
  };

  // ---- Estadísticas derivadas (para logros) ----
  Meta.statValue = function (s, stat) {
    if (stat === 'shipsOwned') return D.shipOrder.filter((id) => Meta.shipOwned(s, id)).length;
    if (stat === 'metaLevels') return Object.values(s.meta).reduce((a, b) => a + b, 0);
    if (stat.startsWith('win_')) return s.cleared[stat.slice(4)] ? 1 : 0;
    return s.stats[stat] || 0;
  };
  Meta.achProgress = (s, a) => Math.min(a.goal, Meta.statValue(s, a.stat));
  Meta.achReady = (s, a) => !s.ach[a.id] && Meta.statValue(s, a.stat) >= a.goal;
  Meta.claimAch = function (s, id) {
    const a = D.achievements.find((x) => x.id === id);
    if (!a || !Meta.achReady(s, a)) return 0;
    s.ach[id] = true;
    s.coins += a.reward;
    return a.reward;
  };
  Meta.claimMission = function (s, idx) {
    const m = s.missions.list[idx];
    if (!m || m.claimed || m.progress < m.goal) return 0;
    m.claimed = true;
    s.coins += m.reward;
    return m.reward;
  };
  // Cuántas recompensas hay por reclamar (para la insignia del menú).
  Meta.claimable = (s) =>
    s.missions.list.filter((m) => !m.claimed && m.progress >= m.goal).length +
    D.achievements.filter((a) => Meta.achReady(s, a)).length +
    (s.login.claimed ? 0 : 1);

  // ---- Resultado de una partida ----
  // run: { won, time, kills, coins, level, bossKills, stage, ship, maxWeaponLevel }
  Meta.applyRun = function (s, run) {
    const st = s.stats;
    const stage = D.stages[run.stage];
    const bonus = run.won ? Math.round(150 * stage.coinMul) : 0;
    const total = Math.round(run.coins) + bonus;
    const before = D.shipOrder.filter((id) => Meta.shipOwned(s, id));
    st.kills += run.kills; st.runs += 1; st.bossKills += run.bossKills; st.coinsEarned += total;
    st.bestTime = Math.max(st.bestTime, Math.floor(run.time));
    st.maxLevel = Math.max(st.maxLevel, run.level);
    st.maxWeaponLevel = Math.max(st.maxWeaponLevel, run.maxWeaponLevel || 0);
    st.playtime += run.time;
    if (run.won) { st.wins += 1; s.cleared[run.stage] = true; }
    const b = s.best[run.stage] || { time: 0, kills: 0, won: false };
    const newBest = run.won ? !b.won || run.time < b.time : (!b.won && run.time > b.time);
    if (newBest) s.best[run.stage] = { time: Math.floor(run.time), kills: run.kills, won: run.won || b.won };
    else if (run.won && !b.won) s.best[run.stage].won = true;
    s.coins += total;
    // misiones
    const day = Meta.ensureDaily(s);
    const vals = { kills: run.kills, coins: total, runs: 1, bossKills: run.bossKills, time: run.time, level: run.level, wins: run.won ? 1 : 0 };
    for (const m of s.missions.list) {
      const tpl = D.missionTpl.find((t) => t.id === m.id);
      if (m.claimed) continue;
      if (tpl.kind === 'sum') m.progress = Math.min(m.goal, m.progress + (vals[tpl.stat] || 0));
      else m.progress = Math.min(m.goal, Math.max(m.progress, Math.floor(vals[tpl.stat] || 0)));
    }
    Meta.normalizeOwnership(s);
    const after = D.shipOrder.filter((id) => Meta.shipOwned(s, id));
    return { total, bonus, newBest, newShips: after.filter((id) => !before.includes(id)) };
  };
})(typeof window !== 'undefined' ? window : globalThis);
