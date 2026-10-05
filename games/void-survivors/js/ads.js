// Capa de anuncios. Por defecto no hay proveedor: los botones de anuncio recompensado no se muestran.
// En Android se rellena desde la app nativa (ver ../android-template): el WebView expone window.AndroidAds
// con isReady() y showRewarded(callbackName). Con ?dev=1 se simula un anuncio para probar la interfaz.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});
  const dev = /[?&]dev=1/.test((g.location && g.location.search) || '');
  const Ads = (VS.Ads = {
    available() {
      if (g.AndroidAds && typeof g.AndroidAds.isReady === 'function') { try { return !!g.AndroidAds.isReady(); } catch (e) { return false; } }
      return dev;
    },
    // Muestra un anuncio recompensado. cb(true) si el jugador lo completó.
    rewarded(cb) {
      if (g.AndroidAds && typeof g.AndroidAds.showRewarded === 'function') {
        const name = '__adDone' + Date.now();
        g[name] = (ok) => { delete g[name]; cb(!!ok); };
        try { g.AndroidAds.showRewarded(name); } catch (e) { delete g[name]; cb(false); }
        return;
      }
      if (dev) { setTimeout(() => cb(true), 400); return; }
      cb(false);
    },
  });
})(typeof window !== 'undefined' ? window : globalThis);
