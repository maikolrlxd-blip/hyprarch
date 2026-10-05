// Pantallas de menú y diálogos (DOM). Toda la lógica de negocio vive en Meta/App; aquí solo se pinta.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const D = VS.data, M = VS.Meta, U = VS.util, t = (k, v) => VS.t(k, v), ic = (id, col, cls) => VS.iconImg(id, col, cls);

  const UI = (VS.UI = { toastT: 0 });
  const $ = (s) => g.document.querySelector(s);

  UI.show = (html, cls) => { $('#screen').innerHTML = `<div class="scr ${cls || 'bg'}">${html}</div>`; };
  UI.clear = () => { $('#screen').innerHTML = ''; };
  UI.toast = function (msg) {
    const el = $('#toast');
    el.textContent = msg; el.classList.add('on');
    clearTimeout(UI.toastT);
    UI.toastT = setTimeout(() => el.classList.remove('on'), 1800);
  };
  const streakTxt = (n) => (n === 1 ? t('login_streak1') : t('login_streak', { n }));
  const coinPill = (s) => `<span class="pill">${ic('coin', '#fc3')}<span id="coinv">${U.fmtNum(s.coins)}</span></span>`;
  const topbar = (s, title) => `<div class="topbar"><button class="btn small" data-a="home">‹ ${t('back')}</button><h2 class="title">${title}</h2>${coinPill(s)}</div>`;

  // ---------------------------------------------------------------- inicio
  UI.home = function (s, shipImg) {
    const stage = D.stages[s.selStage], ship = D.ships[s.selShip], sid = s.selStage;
    const idx = D.stageOrder.indexOf(sid), unlocked = M.stageUnlocked(s, sid);
    const best = s.best[sid];
    const bestTxt = best ? `${t('best')}: ${U.fmtTime(best.time)}${best.won ? ' ✓' : ''}` : '';
    const claim = M.claimable(s);
    UI.show(`
      <div class="home wrap" style="align-items:center">
        ${coinPill(s)}
        <button class="btn small gear iconbtn" data-a="settings" aria-label="${t('settings')}">${ic('gear', '#fff')}</button>
        <h1 class="logo">VOID<br>SURVIVORS</h1>
        <p class="tag">${t('app.tag')}</p>
        <div class="shipshow"><img src="${shipImg}" alt=""></div>
        <div class="name" style="text-align:center">${t('sh.' + s.selShip + '.n')}</div>
        <div class="stagesel">
          <button class="btn arrow" data-a="stage" data-v="-1" ${idx === 0 ? 'disabled' : ''}>‹</button>
          <div class="card">
            <b>${t('stage')} ${idx + 1}: ${t('st.' + sid + '.n')}</b>
            <small>${unlocked ? bestTxt || t('st.' + sid + '.d') : ic('lock', '#fff') + ' ' + t('unlock_stage')}</small>
          </div>
          <button class="btn arrow" data-a="stage" data-v="1" ${idx === D.stageOrder.length - 1 ? 'disabled' : ''}>›</button>
        </div>
        <div class="seg diffseg">${D.difficulty.map((_, d) => {
          const ok = unlocked && d <= M.maxDiff(s, sid);
          return `<button class="btn ${s.selDiff === d && ok ? 'on' : ''} ${ok ? '' : 'off'}" data-a="diff" data-v="${d}">${ok ? '' : ic('lock', '#fff') + ' '}${t('diff.' + d)}</button>`;
        }).join('')}</div>
        <button class="btn big play ${unlocked ? '' : 'off'}" data-a="play">${t('play')}</button>
        <div class="nav">
          <button class="btn" data-a="ships">${ic('ship', '#5df')}${t('ships')}</button>
          <button class="btn" data-a="upgrades">${ic('up', '#6f9')}${t('upgrades')}${M.canAffordUpgrade(s) ? '<span class="badge">!</span>' : ''}</button>
          <button class="btn" data-a="missions">${ic('mission', '#fc3')}${t('missions')}${claim ? `<span class="badge">${claim}</span>` : ''}</button>
          <button class="btn" data-a="trophies">${ic('trophy', '#f9f')}${t('trophies')}</button>
        </div>
      </div>`);
  };

  // ---------------------------------------------------------------- naves
  UI.ships = function (s, shipImgs) {
    const rows = D.shipOrder.map((id) => {
      const sh = D.ships[id], owned = M.shipOwned(s, id), sel = s.selShip === id;
      const w0 = sh.weapons.map((w) => ic(w, D.weapons[w].color)).join('');
      let action;
      if (sel) action = `<span class="pill" style="color:var(--good)">${ic('check', '#5f9')} ${t('selected')}</span>`;
      else if (owned) action = `<button class="btn small" data-a="selship" data-v="${id}">${t('select')}</button>`;
      else if (sh.unlock) action = `<span class="desc">${ic('lock', '#fff')} ${t('unlock_clear', { s: t('st.' + sh.unlock.clear + '.n') })}</span>`;
      else action = `<button class="btn small gold ${s.coins >= sh.cost ? '' : 'off'}" data-a="buyship" data-v="${id}">${ic('coin', '#620')} ${U.fmtNum(sh.cost)}</button>`;
      const bar = (v, max) => `<div class="bar"><i style="width:${Math.min(100, (v / max) * 100)}%"></i></div>`;
      return `<div class="card ${sel ? 'sel' : ''} ${owned ? '' : 'lockedc'}">
        <div class="row"><div class="ico"><img src="${shipImgs[id]}" alt="" style="width:46px;height:46px"></div>
          <div class="grow"><div class="name">${t('sh.' + id + '.n')}</div><div class="desc">${t('sh.' + id + '.d')}</div></div></div>
        <div class="stats3"><span>${t('stat.hp')}</span>${bar(sh.hp, 170)}<span>${t('stat.speed')}</span>${bar(sh.speed, 190)}<span>${t('stat.armor')}</span>${bar(sh.armor, 4)}</div>
        <div class="row" style="margin-top:10px"><span class="desc">${t('start_weapon')}: ${w0}</span><span style="flex:1"></span>${action}</div>
      </div>`;
    }).join('');
    UI.show(`<div class="wrap">${topbar(s, t('ships'))}<div class="list">${rows}</div></div>`);
  };

  // ---------------------------------------------------------------- mejoras permanentes
  const ICONS = { hp: ['plating', '#9d6'], dmg: ['power', '#f66'], speed: ['thrusters', '#4cf'], magnet: ['magnet', '#c8f'], xp: ['scholar', '#6fd'], coin: ['coin', '#fc3'], armor: ['barrier', '#8af'], regen: ['regen', '#f9a'], reroll: ['lens', '#fa6'], revive: ['heart', '#f66'], choice: ['fortune', '#ff6'] };
  UI.upgrades = function (s) {
    const rows = D.metaOrder.map((id) => {
      const u = D.metaUpgrades[id], lv = M.level(s, id), maxed = lv >= u.max, cost = D.metaCost(id, lv);
      const pips = Array.from({ length: u.max }, (_, i) => `<i class="${i < lv ? 'on' : ''}"></i>`).join('');
      const btn = maxed ? `<span class="pill" style="color:var(--good)">${t('max')}</span>` : `<button class="btn small gold ${s.coins >= cost ? '' : 'off'}" data-a="buyupg" data-v="${id}">${ic('coin', '#620')} ${U.fmtNum(cost)}</button>`;
      return `<div class="card row"><div class="ico">${ic(ICONS[id][0], ICONS[id][1])}</div>
        <div class="grow"><div class="name">${t('u.' + id + '.n')}</div><div class="desc">${t('u.' + id + '.d')}</div><div class="pips">${pips}</div></div>${btn}</div>`;
    }).join('');
    UI.show(`<div class="wrap">${topbar(s, t('upgrades'))}<div class="list">${rows}</div></div>`);
  };

  // ---------------------------------------------------------------- misiones
  UI.missions = function (s) {
    const L = D.loginRewards, streakDay = ((Math.max(1, s.login.streak) - 1) % L.length);
    const days = L.map((r, i) => `<div class="day ${i < streakDay || (i === streakDay && s.login.claimed) ? 'past' : ''} ${i === streakDay ? 'today' : ''}">${t('login_day', { n: i + 1 })}<b>${ic('coin', '#fc3')} ${r}</b></div>`).join('');
    const login = `<div class="card"><div class="row"><div class="grow"><div class="name">${t('daily_login')}</div><div class="desc">${streakTxt(s.login.streak)}</div></div>
      ${s.login.claimed ? `<span class="pill" style="color:var(--good)">${ic('check', '#5f9')}</span>` : `<button class="btn gold" data-a="claimlogin">${t('collect')} +${M.loginReward(s)}</button>`}</div>
      <div class="sp"></div><div class="streak">${days}</div></div>`;
    const ms = s.missions.list.map((m, i) => {
      const done = m.progress >= m.goal, tpl = D.missionTpl.find((x) => x.id === m.id);
      const goalTxt = m.id === 'time' ? U.fmtTime(m.goal) : m.goal;
      const act = m.claimed ? `<span class="pill" style="color:var(--dim)">${t('claimed')}</span>` : done ? `<button class="btn small gold" data-a="claimmission" data-v="${i}">${t('claim')} +${m.reward}</button>` : `<span class="pill">${ic('coin', '#fc3')} ${m.reward}</span>`;
      const prog = m.id === 'time' ? U.fmtTime(m.progress) : m.progress;
      return `<div class="card"><div class="row"><div class="grow"><div class="name">${t('m.' + m.id, { n: goalTxt })}</div>
        <div class="desc">${prog} / ${goalTxt}</div><div class="sp"></div><div class="bar ${done ? 'done' : ''}"><i style="width:${Math.min(100, (m.progress / m.goal) * 100)}%"></i></div></div>${act}</div></div>`;
    }).join('');
    UI.show(`<div class="wrap">${topbar(s, t('missions'))}${login}<div class="name" style="margin-top:6px">${t('daily')} <span class="desc">· ${t('resets')}</span></div>${ms}</div>`);
  };

  // ---------------------------------------------------------------- logros
  UI.trophies = function (s) {
    const list = D.achievements.slice().sort((a, b) => (s.ach[a.id] ? 1 : 0) - (s.ach[b.id] ? 1 : 0) || (M.achReady(s, b) ? 1 : 0) - (M.achReady(s, a) ? 1 : 0));
    const rows = list.map((a) => {
      const v = M.achProgress(s, a), ready = M.achReady(s, a), done = !!s.ach[a.id];
      const act = done ? `<span class="pill" style="color:var(--good)">${ic('check', '#5f9')}</span>` : ready ? `<button class="btn small gold" data-a="claimach" data-v="${a.id}">${t('claim')} +${a.reward}</button>` : `<span class="pill">${ic('coin', '#fc3')} ${a.reward}</span>`;
      const fmt = a.stat === 'bestTime' ? U.fmtTime : (x) => U.fmtNum(x);
      return `<div class="card ${done ? 'lockedc' : ''}"><div class="row"><div class="ico">${ic('trophy', done ? '#5f9' : '#f9f')}</div>
        <div class="grow"><div class="name">${t('a.' + a.id)}</div><div class="desc">${t('a.' + a.id + '.d')}</div><div class="sp"></div>
        <div class="bar ${done || ready ? 'done' : ''}"><i style="width:${(v / a.goal) * 100}%"></i></div><div class="desc">${fmt(v)} / ${fmt(a.goal)}</div></div>${act}</div></div>`;
    }).join('');
    UI.show(`<div class="wrap">${topbar(s, t('trophies'))}<div class="list">${rows}</div></div>`);
  };

  // ---------------------------------------------------------------- ajustes
  UI.settings = function (s, privacyUrl) {
    const st = s.settings, sw = (k, label) => `<div class="switch"><span>${label}</span><button class="tog ${st[k] ? 'on' : ''}" data-a="tog" data-v="${k}" aria-label="${label}"></button></div>`;
    const S = s.stats;
    UI.show(`<div class="wrap">${topbar(s, t('settings'))}
      <div class="card">${sw('sound', t('sound'))}${sw('music', t('music'))}${sw('vibe', t('vibration'))}${sw('shake', t('shake'))}${sw('numbers', t('numbers'))}
        <div class="switch"><span>${t('language')}</span><div class="seg"><button class="btn ${VS.i18n.lang === 'es' ? 'on' : ''}" data-a="lang" data-v="es">ES</button><button class="btn ${VS.i18n.lang === 'en' ? 'on' : ''}" data-a="lang" data-v="en">EN</button></div></div></div>
      <div class="card"><div class="name">${t('stats')}</div><div class="res">
        <span>${t('total_runs')}</span><span>${S.runs}</span><span>${t('total_wins')}</span><span>${S.wins}</span><span>${t('total_kills')}</span><span>${U.fmtNum(S.kills)}</span>
        <span>${t('play_time')}</span><span>${Math.floor(S.playtime / 60)} min</span></div></div>
      <button class="btn ghost" data-a="url" data-v="${privacyUrl}">${t('privacy')}</button>
      <button class="btn red" data-a="reset">${t('reset')}</button>
      <div class="desc" style="text-align:center">v${VS.VERSION || '1.0.0'}</div></div>`);
  };

  // ---------------------------------------------------------------- subida de nivel
  function diffText(id, level) {
    const L = D.weapons[id].levels, a = L[level - 2], b = L[level - 1], out = [];
    for (const k in b) {
      if (a[k] === b[k] || !(('stat.' + k) in VS.i18nDict.en)) continue;
      const f = (v) => (k === 'cd' || k === 'tick' || k === 'spin' ? v.toFixed(2).replace(/0$/, '') : Math.round(v));
      out.push(`${t('stat.' + k)} ${f(a[k])}→${f(b[k])}`);
    }
    return out.slice(0, 3).join(' · ');
  }
  UI.levelup = function (sim) {
    const cards = sim.choices.map((c, i) => {
      let icon, name, tag = '', desc;
      if (c.kind === 'weapon' && c.evo) { const def = D.weapons[c.id]; icon = ic(c.id, '#ffd24a'); name = t('w.' + c.id + '.evo'); tag = `<span class="tagnew" style="color:#fc3">${t('evolution')}</span>`; desc = diffText(c.id, c.level); }
      else if (c.kind === 'weapon') { const def = D.weapons[c.id]; icon = ic(c.id, def.color); name = t('w.' + c.id + '.n'); tag = c.level === 1 ? `<span class="tagnew">${t('stat.new')}</span>` : `<span class="lvl">${t('level')} ${c.level}${c.level === def.max ? ' · ' + t('max') : ''}</span>`; desc = c.level === 1 ? t('w.' + c.id + '.d') : diffText(c.id, c.level); }
      else if (c.kind === 'passive') { const def = D.passives[c.id]; icon = ic(c.id, def.color); name = t('p.' + c.id + '.n'); tag = `<span class="lvl">${t('level')} ${c.level}${c.level === def.max ? ' · ' + t('max') : ''}</span>`; desc = t('p.' + c.id + '.d'); }
      else if (c.kind === 'heal') { icon = ic('heart', '#f66'); name = t('heal'); desc = t('heal.d'); }
      else { icon = ic('coin', '#fc3'); name = t('bonus_coins'); desc = t('coins.d'); }
      return `<button class="choice ${c.kind}${c.evo ? ' evo' : ''}" data-a="choose" data-v="${i}"><div class="ico">${icon}</div><div class="grow"><div class="name">${name} ${tag}</div><div class="desc">${desc}</div></div></button>`;
    }).join('');
    const rr = sim.rerolls > 0 ? `<button class="btn" data-a="reroll">${ic('lens', '#fa6')} ${t('reroll')} (${sim.rerolls})</button>` : '';
    UI.show(`<div class="wrap" style="margin:auto 0"><h3 class="lv-title">${t('levelup')}</h3><p class="lv-sub">${t('choose_upgrade')}</p>${cards}<div style="text-align:center">${rr}</div></div>`, 'dim');
  };

  // ---------------------------------------------------------------- pausa
  UI.pause = function (sim, s) {
    const st = s.settings, tog = (k, l) => `<div class="switch"><span>${l}</span><button class="tog ${st[k] ? 'on' : ''}" data-a="tog" data-v="${k}" data-r="pause"></button></div>`;
    const items = sim.weapons.map((w) => `<div class="row">${ic(w.id, D.weapons[w.id].color)}<span class="grow">${t('w.' + w.id + (w.level >= 7 ? '.evo' : '.n'))}</span><b>${t('level')} ${w.level}</b></div>`).join('') +
      Object.keys(sim.passives).map((id) => `<div class="row">${ic(id, D.passives[id].color)}<span class="grow">${t('p.' + id + '.n')}</span><b>${t('level')} ${sim.passives[id]}</b></div>`).join('');
    UI.show(`<div class="wrap" style="margin:auto 0"><h3 class="lv-title" style="color:#fff">${t('pause')}</h3>
      <div class="card">${items}</div><div class="card">${tog('sound', t('sound'))}${tog('music', t('music'))}</div>
      <button class="btn big play" data-a="resume">${t('resume')}</button><button class="btn red" data-a="quit">${t('quit')}</button></div>`, 'dim');
  };

  // ---------------------------------------------------------------- revivir (anuncio) y resultados
  UI.revive = function (canAd) {
    UI.show(`<div class="wrap" style="margin:auto 0;text-align:center"><div class="big-num lose">${t('defeat')}</div><div class="sp"></div>
      ${canAd ? `<button class="btn big gold" data-a="revivead">${ic('ad', '#310')} ${t('revive_ad')}</button>` : ''}
      <button class="btn big" data-a="giveup">${t('continue')}</button></div>`, 'dim');
  };

  UI.results = function (s, run, sum, adOk, flags) {
    flags = flags || {};
    const won = run.won, unlocks = sum.newShips.map((id) => `<div class="newb">${t('new_unlock')}: ${t('sh.' + id + '.n')}</div>`).join('');
    UI.show(`<div class="wrap" style="margin:auto 0"><div class="big-num ${won ? 'win' : 'lose'}">${won ? t('victory') : t('defeat')}</div>
      ${sum.newBest ? `<div class="newb">${t('new_best')}</div>` : ''}${unlocks}
      <div class="card"><div class="res"><span>${t('stage')}</span><span>${t('st.' + run.stage + '.n')}</span><span>${t('time')}</span><span>${U.fmtTime(run.time)}</span>
        <span>${t('kills')}</span><span>${run.kills}</span><span>${t('level')}</span><span>${run.level}</span>
        ${won ? `<span>${t('win_bonus')}</span><span>+${sum.bonus}</span>` : ''}
        <span>${t('coins_earned')}</span><span style="color:var(--gold)" id="gained">+${sum.total}</span></div></div>
      ${flags.upgradeCta ? `<button class="btn big gold cta" data-a="upgrades">${ic('up', '#310')} ${t('upgrade_cta')}</button>` : ''}
      ${flags.askRate ? `<div class="card"><div class="name">${t('rate_title')}</div><div class="desc">${t('rate_d')}</div><div class="sp"></div><div class="row"><button class="btn gold small" data-a="rate">${t('rate_btn')}</button><button class="btn ghost small" data-a="ratelater">${t('later')}</button></div></div>` : ''}
      ${adOk ? `<button class="btn gold" data-a="doublead" id="dblbtn">${ic('ad', '#310')} ${t('double_ad')}</button>` : ''}
      <div class="row" style="justify-content:center"><button class="btn big play" data-a="play" style="min-width:0">${t('retry')}</button><button class="btn big" data-a="home">${t('home')}</button></div></div>`, 'dim');
  };

  // Ventana de recompensa diaria al abrir la app.
  UI.loginPopup = function (s) {
    UI.show(`<div class="wrap" style="margin:auto 0;text-align:center"><h3 class="lv-title">${t('daily_login')}</h3>
      <div class="card"><div class="desc">${streakTxt(s.login.streak)}</div><div class="big-num" style="color:var(--gold);margin:10px 0">+${M.loginReward(s)}</div></div>
      <button class="btn big gold" data-a="claimlogin" data-r="home">${t('collect')}</button></div>`, 'dim');
  };
})(typeof window !== 'undefined' ? window : globalThis);
