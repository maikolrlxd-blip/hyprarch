package com.hyprarch.game;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.window.OnBackInvokedDispatcher;

/** Carga el juego HTML5 empaquetado en assets/ dentro de un WebView a pantalla completa. */
public class MainActivity extends Activity {
    private WebView web;

    /**
     * Puente de anuncios que el juego espera (window.AndroidAds). Por defecto NO hay anuncios:
     * isReady() devuelve false y el juego oculta los botones de anuncio. Para activar AdMob,
     * implementa aquí isReady()/showRewarded() con el SDK y llama a window[callback](true|false).
     */
    public class AdsBridge {
        @JavascriptInterface public boolean isReady() { return false; }
        @JavascriptInterface public void showRewarded(String callbackName) { /* sin proveedor */ }
    }

    /** Vibración corta (el WebView no implementa navigator.vibrate). */
    public class NativeBridge {
        @JavascriptInterface public void vibrate(int ms) {
            Vibrator v = (Vibrator) getSystemService(VIBRATOR_SERVICE);
            if (v == null || !v.hasVibrator()) return;
            ms = Math.max(10, Math.min(ms, 400));
            if (Build.VERSION.SDK_INT >= 26) v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE));
            else v.vibrate(ms);
        }
    }

    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        web = new WebView(this);
        web.setBackgroundColor(Color.BLACK);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setLongClickable(false);
        web.setHapticFeedbackEnabled(false);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);                 // localStorage: partidas guardadas y récords
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);                  // no afecta a file:///android_asset
        web.addJavascriptInterface(new AdsBridge(), "AndroidAds");
        web.addJavascriptInterface(new NativeBridge(), "AndroidNative");
        setContentView(web);
        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::handleBack);
        }
        web.loadUrl("file:///android_asset/index.html");
    }

    /** El juego decide si consume el botón Atrás (pausa / volver al menú); si no, se cierra la app. */
    private void handleBack() {
        web.evaluateJavascript("(window.__onBack && window.__onBack()) ? '1' : '0'", v -> {
            if (!"\"1\"".equals(v)) finish();
        });
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        if (Build.VERSION.SDK_INT < 33) handleBack(); else super.onBackPressed();
    }

    @Override
    public void onWindowFocusChanged(boolean focus) {
        super.onWindowFocusChanged(focus);
        if (focus) web.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    @Override protected void onPause() { super.onPause(); web.onPause(); }
    @Override protected void onResume() { super.onResume(); web.onResume(); }
    @Override protected void onDestroy() { web.destroy(); super.onDestroy(); }
}
