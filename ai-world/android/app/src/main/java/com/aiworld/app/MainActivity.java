package com.aiworld.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.animation.ObjectAnimator;
import android.graphics.Outline;
import android.view.View;
import android.view.ViewOutlineProvider;
import android.view.animation.AccelerateDecelerateInterpolator;
import android.animation.ValueAnimator;
import android.widget.ImageView;
import android.view.WindowManager;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;
import com.google.mlkit.vision.barcode.common.Barcode;

/**
 * Cliente movil de AI World. La app de PC es la que corre las IAs; esto solo muestra el
 * mundo (que la PC sirve por la red local) dentro de un WebView y recuerda a cual PC conectar.
 */
public class MainActivity extends Activity {
    private static final String PREFS = "aiworld";
    private static final String KEY_URL = "url";

    private WebView web;
    private View connect;
    private EditText urlInput;
    private TextView error;
    private String allowedHost;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        web = findViewById(R.id.web);
        connect = findViewById(R.id.connect);
        urlInput = findViewById(R.id.url);
        error = findViewById(R.id.error);

        floatLogo((ImageView) findViewById(R.id.logo));
        setupWebView();
        ((Button) findViewById(R.id.go)).setOnClickListener(v -> tryConnect(urlInput.getText().toString()));
        ((Button) findViewById(R.id.scan)).setOnClickListener(v -> scanQr());

        String saved = prefs().getString(KEY_URL, null);
        if (saved != null) {
            urlInput.setText(saved);
            tryConnect(saved);
        }
    }

    /** Logo redondeado que flota suavemente en la pantalla de conexion. */
    private void floatLogo(ImageView logo) {
        final float radius = 28 * getResources().getDisplayMetrics().density;
        logo.setOutlineProvider(new ViewOutlineProvider() {
            @Override
            public void getOutline(View v, Outline o) {
                o.setRoundRect(0, 0, v.getWidth(), v.getHeight(), radius);
            }
        });
        logo.setClipToOutline(true);
        float amp = 8 * getResources().getDisplayMetrics().density;
        ObjectAnimator a = ObjectAnimator.ofFloat(logo, View.TRANSLATION_Y, -amp, amp);
        a.setDuration(2200);
        a.setRepeatMode(ValueAnimator.REVERSE);
        a.setRepeatCount(ValueAnimator.INFINITE);
        a.setInterpolator(new AccelerateDecelerateInterpolator());
        a.start();
    }

    private SharedPreferences prefs() {
        return getSharedPreferences(PREFS, MODE_PRIVATE);
    }

    private void setupWebView() {
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                // Solo se navega a la PC emparejada; cualquier otro destino se bloquea.
                return allowedHost == null || !allowedHost.equals(req.getUrl().getHost());
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest req, WebResourceError err) {
                if (req.isForMainFrame()) {
                    showConnect("No se pudo conectar con la PC (" + err.getDescription() + "). "
                            + "Revisa que la app de PC tenga «Celular» activado y que ambos esten en la misma Wi-Fi.");
                }
            }

            @Override
            public void onReceivedHttpError(WebView view, WebResourceRequest req, WebResourceResponse res) {
                if (req.isForMainFrame()) {
                    showConnect("La PC respondio con error " + res.getStatusCode() + ". Vuelve a generar el enlace en la app de PC.");
                }
            }
        });
    }

    /** Devuelve la URL normalizada o null si no sirve. */
    static String normalize(String raw) {
        if (raw == null) return null;
        String u = raw.trim();
        if (u.isEmpty()) return null;
        if (!u.startsWith("http://") && !u.startsWith("https://")) u = "http://" + u;
        Uri uri = Uri.parse(u);
        if (uri.getHost() == null) return null;
        String t = uri.getQueryParameter("t");
        return (t == null || t.isEmpty()) ? null : u;
    }

    private void tryConnect(String raw) {
        String url = normalize(raw);
        if (url == null) {
            showConnect("Enlace no valido. Debe verse como http://192.168.x.x:8787/?t=clave (copialo de la app de PC o escanea el QR).");
            return;
        }
        prefs().edit().putString(KEY_URL, url).apply();
        allowedHost = Uri.parse(url).getHost();
        error.setVisibility(View.GONE);
        connect.setVisibility(View.GONE);
        web.setVisibility(View.VISIBLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        web.loadUrl(url);
    }

    private void showConnect(String message) {
        web.stopLoading();
        web.setVisibility(View.GONE);
        connect.setVisibility(View.VISIBLE);
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        if (message != null) {
            error.setText(message);
            error.setVisibility(View.VISIBLE);
        }
    }

    private void scanQr() {
        GmsBarcodeScannerOptions options = new GmsBarcodeScannerOptions.Builder()
                .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
                .build();
        GmsBarcodeScanner scanner = GmsBarcodeScanning.getClient(this, options);
        scanner.startScan()
                .addOnSuccessListener(barcode -> {
                    String value = barcode.getRawValue();
                    urlInput.setText(value);
                    tryConnect(value);
                })
                .addOnFailureListener(e -> showConnect("No se pudo abrir el escaner de QR (" + e.getMessage() + "). Pega el enlace a mano."));
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (connect.getVisibility() == View.VISIBLE) {
            super.onBackPressed();
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("AI World")
                .setItems(new String[]{"Cambiar de PC", "Salir"}, (d, which) -> {
                    if (which == 0) {
                        prefs().edit().remove(KEY_URL).apply();
                        showConnect(null);
                    } else {
                        finish();
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    @Override
    protected void onPause() {
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }
}
