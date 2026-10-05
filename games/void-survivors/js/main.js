// Orquestación: bucle de juego, HUD, eventos -> audio/vibración/fx y acciones de los menús.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  VS.VERSION = '1.0.0';
  // Debe apuntar a la política de privacidad publicada (ver store/PRIVACY.md y store/README.md).
  const PLAY_URL = 'https://play.google.com/store/apps/details?id=com.hyprarch.games.voidsurvivors';
  const PRIVACY_URL = 'https://github.com/maikolrlxd-blip/hyprarch/blob/main/games/void-survivors/store/PRIVACY.md';

  const D = VS.data, M = VS.Meta, S = VS.Save, UI = VS.UI, A = VS.Audio, I = VS.Input, U = VS.util, t = (k, v) => VS.t(k, v);
  const $ = (s) => g.document.querySelector(s);
  const STEP = 1 / 60;

  const App = (VS.App = { mode: 'boot', sim: null });
  let renderer, menuSim, acc = 0, last = 0, hudT = 0, paused = false, wonT = 0, deadT = 0;
  let levelShown = false, deadShown = false, finishing = false, itemsSig = '', hintKey = '', lastSum = null, resetArmed = 0;
  const shipImgs = {};

  const save = () => S.save();
  const shipImg = (id) => shipImgs[id] || (shipImgs[id] = renderer.shipSpr(id).c.toDataURL());
  const allShipImgs = () => { const o = {}; D.shipOrder.forEach((id) => (o[id] = shipImg(id))); return o; };

  // ------------------------------------------------------------------ arranque
  App.init = function () {
    S.load();
    const s = S.data;
    M.normalizeOwnership(s);
    VS.i18n.set(s.settings.lang || VS.i18n.detect());
    A.sfxOn = !!s.settings.sound; A.musOn = !!s.settings.music;
    renderer = App.renderer = new VS.Renderer($('#game'));
    I.attach($('#game'));
    menuSim = new VS.Sim({ ship: 'falcon', stage: s.selStage, meta: M.bonuses(S.defaults()), events: false });
    g.addEventListener('resize', () => { renderer.resize(); if (App.sim) App.sim.viewR = renderer.viewR; });
    g.addEventListener('pointerdown', () => A.init());
    g.addEventListener('keydown', (e) => { A.init(); if (e.code === 'Escape' || e.code === 'KeyP') App.togglePause(); });
    g.document.addEventListener('click', onClick);
    g.document.addEventListener('visibilitychange', () => {
      if (g.document.hidden) { A.suspend(); if (App.mode === 'game' && App.sim && App.sim.state === 'running') App.pause(); } else A.resume();
    });
    g.__onBack = App.back;
    $('#pausebtn').innerHTML = VS.iconImg('pause', '#fff');
    $('#killsStat').innerHTML = VS.iconImg('skull', '#f66') + '<span id="kv">0</span>';
    $('#coinsStat').innerHTML = VS.iconImg('coin', '#fc3') + '<span id="cv">0</span>';
    M.ensureDaily(s);
    const newDay = M.updateLogin(s);
    save();
    last = performance.now();
    requestAnimationFrame(loop);
    if (!s.tutorial.started && s.stats.runs === 0) { s.tutorial.started = true; save(); App.start(); return; } // primera vez: directo al juego
    App.home();
    if (newDay && !s.login.claimed) UI.loginPopup(s);
  };

  function onClick(e) {
    const el = e.target.closest('[data-a]');
    if (!el || el.disabled) return;
    A.init();
    App.act(el.dataset.a, el.dataset.v, el);
  }

  // ------------------------------------------------------------------ pantallas
  App.home = function () {
    App.mode = 'menu'; paused = false;
    I.enabled = false; I.release();
    $('#hud').classList.add('hidden');
    UI.home(S.data, shipImg(S.data.selShip));
    if (A.mode !== 'menu') A.startMusic('menu', 0);
  };
  const refresh = (name) => {
    const s = S.data;
    if (name === 'ships') UI.ships(s, allShipImgs());
    else if (name === 'upgrades') UI.upgrades(s);
    else if (name === 'missions') UI.missions(s);
    else if (name === 'trophies') UI.trophies(s);
    else if (name === 'settings') UI.settings(s, PRIVACY_URL);
  };
  let curScreen = '';
  const go = (name) => { curScreen = name; refresh(name); const sc = $('#screen .scr'); if (sc) sc.scrollTop = 0; };

  App.back = function () {
    if (App.mode === 'game' && App.sim) {
      if (App.sim.state === 'running' && !paused) { App.pause(); return true; }
      if (paused) { App.resume(); return true; }
      return true;
    }
    if (App.mode === 'results') { curScreen = ''; App.home(); return true; }
    if (App.mode === 'menu' && curScreen) { curScreen = ''; App.home(); return true; }
    return false;
  };

  // ------------------------------------------------------------------ acciones de la interfaz
  App.act = function (a, v, el) {
    const s = S.data;
    const click = () => A.sfx('click');
    switch (a) {
      case 'play': click(); App.start(); break;
      case 'home': click(); curScreen = ''; App.home(); break;
      case 'stage': {
        const i = D.stageOrder.indexOf(s.selStage) + (+v);
        if (i >= 0 && i < D.stageOrder.length) { s.selStage = D.stageOrder[i]; s.selDiff = Math.min(s.selDiff, M.maxDiff(s, s.selStage)); save(); click(); App.home(); }
        break;
      }
      case 'diff': if (+v <= M.maxDiff(s, s.selStage) && M.stageUnlocked(s, s.selStage)) { s.selDiff = +v; save(); click(); App.home(); } else { A.sfx('deny'); UI.toast(t('diff_lock', { d: t('diff.' + Math.max(0, +v - 1)) })); } break;
      case 'url': App.openUrl(v); break;
      case 'rate': s.rated = true; save(); App.openUrl(PLAY_URL); { const c = el && el.closest('.card'); if (c) c.remove(); } break;
      case 'ratelater': s.askedAt = s.stats.runs; save(); { const c = el && el.closest('.card'); if (c) c.remove(); } break;
      case 'ships': click(); go('ships'); break;
      case 'upgrades': click(); go('upgrades'); break;
      case 'missions': click(); go('missions'); break;
      case 'trophies': click(); go('trophies'); break;
      case 'settings': click(); go('settings'); break;
      case 'selship': s.selShip = v; save(); A.sfx('select'); refresh('ships'); break;
      case 'buyship':
        if (M.buyShip(s, v)) { s.selShip = v; save(); A.sfx('buy'); } else { A.sfx('deny'); UI.toast(t('not_enough')); }
        refresh('ships'); break;
      case 'buyupg':
        if (M.buyUpgrade(s, v)) { save(); A.sfx('buy'); } else { A.sfx('deny'); UI.toast(t('not_enough')); }
        { const sc = $('#screen .scr'), y = sc ? sc.scrollTop : 0; refresh('upgrades'); const n = $('#screen .scr'); if (n) n.scrollTop = y; }
        break;
      case 'claimlogin': {
        const r = M.claimLogin(s); save();
        if (r) { A.sfx('buy'); UI.toast('+' + r); }
        if (el && el.dataset.r === 'home') App.home(); else refresh('missions');
        break;
      }
      case 'claimmission': { const r = M.claimMission(s, +v); save(); if (r) { A.sfx('buy'); UI.toast('+' + r); } refresh('missions'); break; }
      case 'claimach': { const r = M.claimAch(s, v); save(); if (r) { A.sfx('buy'); UI.toast('+' + r); } refresh('trophies'); break; }
      case 'tog': {
        s.settings[v] = s.settings[v] ? 0 : 1;
        if (v === 'sound') A.setSfx(s.settings.sound); if (v === 'music') A.setMusic(s.settings.music);
        save(); A.sfx('click');
        if (el && el.dataset.r === 'pause') UI.pause(App.sim, s); else refresh('settings');
        break;
      }
      case 'lang': s.settings.lang = v; VS.i18n.set(v); save(); refresh('settings'); break;
      case 'reset':
        if (performance.now() - resetArmed < 4000) { S.reset(); M.normalizeOwnership(S.data); M.ensureDaily(S.data); M.updateLogin(S.data); save(); VS.i18n.set(VS.i18n.detect()); A.setSfx(1); A.setMusic(1); curScreen = ''; App.home(); }
        else { resetArmed = performance.now(); UI.toast(t('reset_confirm')); }
        break;
      case 'pause': App.pause(); break;
      case 'resume': App.resume(); break;
      case 'quit': paused = false; finish(); break;
      case 'choose': if (App.sim && App.sim.state === 'levelup') { App.sim.choose(+v); UI.clear(); levelShown = false; I.release(); A.sfx('click'); } break;
      case 'reroll': if (App.sim && App.sim.reroll()) { A.sfx('select'); UI.levelup(App.sim); } break;
      case 'revivead': VS.Ads.rewarded((ok) => { if (ok && App.sim && App.sim.adRevive()) { UI.clear(); deadShown = false; deadT = 0; } }); break;
      case 'giveup': finish(); break;
      case 'doublead':
        VS.Ads.rewarded((ok) => {
          if (!ok || !lastSum || lastSum.doubled) return;
          lastSum.doubled = true; s.coins += lastSum.total; s.stats.coinsEarned += lastSum.total; save();
          const gEl = $('#gained'), b = $('#dblbtn'); if (gEl) gEl.textContent = '+' + lastSum.total * 2; if (b) b.remove(); A.sfx('buy');
        });
        break;
    }
  };

  // Abre un enlace fuera del juego (en Android, mediante el puente nativo; el WebView no abre pestañas).
  App.openUrl = function (url) {
    try {
      if (g.AndroidNative && g.AndroidNative.openUrl) g.AndroidNative.openUrl(url);
      else g.open(url, '_blank', 'noopener');
    } catch (e) { /* sin navegador */ }
  };

  App.pause = function () {
    if (App.mode !== 'game' || !App.sim || App.sim.state !== 'running' || paused) return;
    paused = true; I.release(); UI.pause(App.sim, S.data);
  };
  App.resume = function () { if (!paused) return; paused = false; UI.clear(); };
  App.togglePause = function () { if (App.mode !== 'game') return; paused ? App.resume() : App.pause(); };

  // ------------------------------------------------------------------ partida
  App.start = function () {
    const s = S.data;
    if (!M.stageUnlocked(s, s.selStage)) { A.sfx('deny'); UI.toast(t('unlock_stage')); return; }
    curScreen = '';
    const diff = Math.min(s.selDiff || 0, M.maxDiff(s, s.selStage));
    const sim = (App.sim = new VS.Sim({ ship: s.selShip, stage: s.selStage, difficulty: diff, assist: s.stats.runs < D.ASSIST.runs && diff === 0, meta: M.bonuses(s), viewR: renderer.viewR }));
    for (const k of ['parts', 'texts', 'bolts', 'booms', 'banners']) renderer[k].length = 0;
    renderer.cam.x = renderer.cam.y = 0; renderer.shake = renderer.vig = 0;
    App.mode = 'game'; paused = false; acc = 0; wonT = 0; deadT = 0; levelShown = deadShown = finishing = false; itemsSig = ''; hintKey = '';
    I.enabled = true; I.release();
    $('#hud').classList.remove('hidden');
    $('#hint').classList.remove('on'); $('#hint').textContent = '';
    UI.clear();
    A.startMusic('battle', D.stages[s.selStage].music);
    A.intensity = 0;
    hudT = 0; updateHud(sim, true);
  };

  function finish() {
    if (finishing || !App.sim) return;
    finishing = true;
    const s = S.data, sim = App.sim, run = sim.result();
    const sum = M.applyRun(s, run);
    s.tutorial.done = true;
    save();
    lastSum = sum; sum.doubled = false;
    renderer.banners.length = 0;
    App.mode = 'results';
    I.enabled = false; I.release();
    $('#hud').classList.add('hidden');
    const early = s.stats.runs <= 6;
    UI.results(s, run, sum, VS.Ads.available() && sum.total > 0, {
      upgradeCta: early && M.canAffordUpgrade(s),
      askRate: !s.rated && (run.won || s.stats.runs >= 4) && (s.askedAt === undefined || s.stats.runs - s.askedAt >= 8),
    });
    A.startMusic('menu', 0);
  }

  // ------------------------------------------------------------------ eventos de la simulación
  function vibrate(ms) {
    if (!S.data.settings.vibe) return;
    try {
      if (g.AndroidNative && g.AndroidNative.vibrate) g.AndroidNative.vibrate(ms); // WebView: puente nativo
      else if (g.navigator && g.navigator.vibrate) g.navigator.vibrate(ms);
    } catch (e) { /* sin vibración */ }
  }
  function handle(ev, sim) {
    renderer.event(ev, sim, { numbers: S.data.settings.numbers, shake: S.data.settings.shake });
    switch (ev.type) {
      case 'shoot': A.sfx(ev.k === 'missile' ? 'missile' : 'shoot'); break;
      case 'kill': A.sfx('kill'); if (ev.boss) { A.sfx('boom'); vibrate(80); } break;
      case 'gem': A.sfx('gem'); break;
      case 'coin': A.sfx('coin'); break;
      case 'heal': case 'magnet': A.sfx('heal'); break;
      case 'bolt': A.sfx('bolt'); break;
      case 'boom': A.sfx('boom'); break;
      case 'nova': A.sfx('nova'); break;
      case 'hurt': A.sfx('hurt'); vibrate(35); break;
      case 'levelup': A.sfx('levelup'); break;
      case 'chest': A.sfx('chest'); break;
      case 'evolve': A.sfx('win'); vibrate(80); break;
      case 'warn': A.sfx('warn'); break;
      case 'boss': A.sfx('boss'); vibrate(120); break;
      case 'won': A.sfx('win'); vibrate(200); break;
      case 'dead': A.sfx('dead'); vibrate(200); break;
      case 'revive': A.sfx('levelup'); break;
    }
  }

  // ------------------------------------------------------------------ HUD
  function updateHud(sim, force) {
    $('#xpfill').style.width = Math.min(100, (sim.xp / sim.xpNeed) * 100) + '%';
    $('#lvl').textContent = t('level') + ' ' + sim.level;
    const hp = Math.max(0, sim.p.hp);
    $('#hpfill').style.width = Math.min(100, (hp / sim.st.maxHp) * 100) + '%';
    const mx = Math.round(sim.st.maxHp);
    $('#hptxt').textContent = Math.min(Math.ceil(hp), mx) + ' / ' + mx;
    $('#clock').textContent = U.fmtTime(sim.t);
    $('#kv').textContent = sim.kills;
    $('#cv').textContent = sim.coins;
    const sig = sim.weapons.map((w) => w.id + w.level).join() + '|' + JSON.stringify(sim.passives);
    if (force || sig !== itemsSig) {
      itemsSig = sig;
      $('#items').innerHTML = sim.weapons.map((w) => `<div class="it">${VS.iconImg(w.id, D.weapons[w.id].color)}<b>${w.level}</b></div>`).join('') +
        Object.keys(sim.passives).map((id) => `<div class="it">${VS.iconImg(id, D.passives[id].color)}<b>${sim.passives[id]}</b></div>`).join('');
    }
    // consejos del tutorial (solo la primera partida)
    const h = $('#hint');
    if (!S.data.tutorial.done) {
      const key = sim.t < 4 ? 'hint.move' : sim.t < 8 ? 'hint.auto' : sim.t < 14 ? 'hint.gems' : sim.t < 19 ? 'hint.boss' : '';
      if (key !== hintKey) { hintKey = key; h.textContent = key ? t(key) : ''; h.classList.toggle('on', !!key); }
    } else if (hintKey) { hintKey = ''; h.classList.remove('on'); }
  }

  // ------------------------------------------------------------------ bucle
  function loop(now) {
    requestAnimationFrame(loop);
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    if (App.mode === 'game' && App.sim) {
      const sim = App.sim;
      if (!paused && sim.state === 'running') {
        acc += dt;
        let n = 0;
        while (acc >= STEP && n < 4) { sim.update(STEP, I.vector()); acc -= STEP; n++; }
        if (n === 4) acc = 0;
      }
      for (let i = 0; i < sim.events.length; i++) handle(sim.events[i], sim);
      sim.events.length = 0;
      const frozen = paused || sim.state === 'levelup';
      renderer.update(frozen ? 0 : dt, sim);
      A.intensity = sim.bossAlive ? 2 : sim.t < 90 ? 0 : sim.t < 240 ? 1 : 2;

      if (sim.state === 'levelup' && !levelShown) { levelShown = true; I.release(); updateHud(sim, true); renderer.banners.length = 0; UI.levelup(sim); }
      if (sim.state === 'dead') {
        deadT += dt;
        if (!deadShown && deadT > 0.9) {
          deadShown = true;
          if (VS.Ads.available() && !sim.adRevived) UI.revive(true); else finish();
        }
      }
      if (sim.state === 'won') { wonT += dt; if (wonT > 2) finish(); }
      hudT -= dt;
      if (hudT <= 0 && sim.state !== 'levelup') { hudT = 0.1; updateHud(sim, false); }
      renderer.draw(sim, I, { menu: false });
    } else {
      renderer.cam.x += dt * 25; renderer.cam.y += dt * 9;
      renderer.update(dt, menuSim);
      renderer.draw(menuSim, null, { menu: true });
    }
  }

  g.addEventListener('DOMContentLoaded', App.init);
})(typeof window !== 'undefined' ? window : globalThis);
