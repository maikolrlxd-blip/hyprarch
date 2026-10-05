// Guardado local versionado. Si localStorage no está disponible, funciona en memoria.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const KEY = 'void_survivors_save';
  const VERSION = 1;

  function defaults() {
    return {
      v: VERSION,
      coins: 0,
      ships: { falcon: true },
      selShip: 'falcon',
      selStage: 's1',
      cleared: {},
      best: {},
      meta: {},
      stats: { kills: 0, runs: 0, wins: 0, bossKills: 0, coinsEarned: 0, bestTime: 0, maxLevel: 0, maxWeaponLevel: 0, playtime: 0 },
      ach: {},
      missions: { day: '', list: [] },
      login: { last: '', streak: 0, claimed: true },
      settings: { sound: 1, music: 1, vibe: 1, shake: 1, numbers: 1, lang: '' },
      tutorial: { done: false },
    };
  }

  function merge(base, src) {
    if (!src || typeof src !== 'object') return base;
    for (const k of Object.keys(base)) {
      if (!(k in src)) continue;
      if (base[k] && typeof base[k] === 'object' && !Array.isArray(base[k])) base[k] = merge(base[k], src[k]);
      else base[k] = src[k];
    }
    // claves dinámicas (ships, cleared, best, meta, ach) que no están en defaults
    for (const k of ['ships', 'cleared', 'best', 'meta', 'ach']) if (src[k] && typeof src[k] === 'object') Object.assign(base[k], src[k]);
    return base;
  }

  const Save = (VS.Save = {
    data: defaults(),
    defaults,
    load() {
      try {
        const raw = g.localStorage && g.localStorage.getItem(KEY);
        if (raw) this.data = merge(defaults(), JSON.parse(raw));
      } catch (e) { this.data = defaults(); }
      this.data.v = VERSION;
      return this.data;
    },
    save() {
      try { g.localStorage && g.localStorage.setItem(KEY, JSON.stringify(this.data)); } catch (e) { /* sin almacenamiento */ }
    },
    reset() {
      this.data = defaults();
      this.save();
    },
  });
})(typeof window !== 'undefined' ? window : globalThis);
