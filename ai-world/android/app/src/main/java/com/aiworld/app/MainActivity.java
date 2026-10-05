package com.aiworld.app;

import android.app.Activity;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * AI World para Android. Dos modos:
 *  - Independiente: el mundo 3D y las IAs corren en el telefono (paginas locales en assets/web).
 *  - Conectado a la PC: se muestra el mundo que sirve la app de PC por la red local.
 *
 * Hay DOS WebView a proposito: el local (menu + modo independiente) tiene el puente nativo
 * {@code AiNative}; el remoto (contenido de la PC) NO lo tiene.
 */
public class MainActivity extends Activity {
    private static final String PREFS = "aiworld";
    private static final String KEY_PC_URL = "url";
    private static final String HOST = "appassets.androidplatform.net";
    private static final String MENU_URL = "https://" + HOST + "/web/menu.html";
    private static final int MAX_HTTP_RESPONSE = 4 * 1024 * 1024;

    private WebView local;
    private WebView remote;
    private String remoteHost;
    private String pendingError = "";
    private final ExecutorService io = Executors.newFixedThreadPool(4);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        local = findViewById(R.id.local);
        remote = findViewById(R.id.remote);
        setupLocal();
        setupRemote();
        local.loadUrl(MENU_URL);
    }

    // ------------------------------------------------------------------ WebViews

    private void baseSettings(WebView w) {
        WebSettings s = w.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
    }

    private void setupLocal() {
        baseSettings(local);
        local.setBackgroundColor(0xFF0A0418);
        local.setWebChromeClient(new WebChromeClient());
        local.addJavascriptInterface(new Bridge(), "AiNative");
        local.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (HOST.equals(u.getHost())) return serveAsset(u.getPath());
                return blocked(); // la pagina local nunca sale a internet por su cuenta
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                return !HOST.equals(req.getUrl().getHost());
            }
        });
    }

    private void setupRemote() {
        baseSettings(remote);
        remote.setBackgroundColor(0xFF0A0418);
        remote.setWebChromeClient(new WebChromeClient());
        remote.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                // Solo se navega a la PC emparejada.
                return remoteHost == null || !remoteHost.equals(req.getUrl().getHost());
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest req, WebResourceError err) {
                if (req.isForMainFrame()) {
                    backToMenu("No se pudo conectar con la PC (" + err.getDescription() + "). "
                            + "Revisa que la app de PC tenga «Celular» activado y que ambos esten en la misma Wi-Fi.");
                }
            }

            @Override
            public void onReceivedHttpError(WebView view, WebResourceRequest req, WebResourceResponse res) {
                if (req.isForMainFrame()) {
                    backToMenu("La PC respondio con error " + res.getStatusCode() + ". Vuelve a generar el enlace en la app de PC.");
                }
            }
        });
    }

    private WebResourceResponse serveAsset(String path) {
        try {
            String rel = path == null ? "" : path.replaceFirst("^/", "");
            if (rel.isEmpty() || rel.contains("..") || !rel.startsWith("web/")) return notFound();
            InputStream in = getAssets().open(rel);
            Map<String, String> headers = new HashMap<>();
            headers.put("Cache-Control", "no-cache");
            return new WebResourceResponse(mimeOf(rel), "utf-8", 200, "OK", headers, in);
        } catch (IOException e) {
            return notFound();
        }
    }

    private static WebResourceResponse notFound() {
        return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", new HashMap<>(), new java.io.ByteArrayInputStream(new byte[0]));
    }

    private static WebResourceResponse blocked() {
        return new WebResourceResponse("text/plain", "utf-8", 403, "Forbidden", new HashMap<>(), new java.io.ByteArrayInputStream(new byte[0]));
    }

    static String mimeOf(String path) {
        String p = path.toLowerCase(Locale.ROOT);
        if (p.endsWith(".html")) return "text/html";
        if (p.endsWith(".js") || p.endsWith(".mjs")) return "text/javascript"; // los modulos exigen un MIME de JS
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".svg")) return "image/svg+xml";
        if (p.endsWith(".json") || p.endsWith(".webmanifest")) return "application/json";
        if (p.endsWith(".png")) return "image/png";
        return "application/octet-stream";
    }

    // ------------------------------------------------------------------ navegacion

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

    private SharedPreferences prefs() {
        return getSharedPreferences(PREFS, MODE_PRIVATE);
    }

    private void connectRemote(String url) {
        prefs().edit().putString(KEY_PC_URL, url).apply();
        remoteHost = Uri.parse(url).getHost();
        local.setVisibility(View.GONE);
        remote.setVisibility(View.VISIBLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        remote.loadUrl(url);
    }

    private void backToMenu(String error) {
        pendingError = error == null ? "" : error;
        remote.stopLoading();
        remote.loadUrl("about:blank");
        remote.setVisibility(View.GONE);
        local.setVisibility(View.VISIBLE);
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        local.loadUrl(MENU_URL);
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (remote.getVisibility() == View.VISIBLE) {
            backToMenu(null);
            return;
        }
        String url = local.getUrl();
        if (url != null && !url.equals(MENU_URL)) { // en el modo independiente: volver al menu
            backToMenu(null);
            return;
        }
        super.onBackPressed();
    }

    @Override
    protected void onPause() {
        local.onPause();
        remote.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        local.onResume();
        remote.onResume();
    }

    @Override
    protected void onDestroy() {
        io.shutdownNow();
        super.onDestroy();
    }

    private void jsLocal(String script) {
        runOnUiThread(() -> local.evaluateJavascript(script, null));
    }

    // ------------------------------------------------------------------ puente nativo

    /** Lo ve solo la pagina local (menu y modo independiente). */
    private class Bridge {
        @JavascriptInterface
        public void scanQr() {
            runOnUiThread(() -> {
                GmsBarcodeScannerOptions options = new GmsBarcodeScannerOptions.Builder()
                        .setBarcodeFormats(Barcode.FORMAT_QR_CODE).build();
                GmsBarcodeScanning.getClient(MainActivity.this, options).startScan()
                        .addOnSuccessListener(b -> {
                            String v = b.getRawValue();
                            if (v != null) jsLocal("window.onQr&&window.onQr(" + JSONObject.quote(v) + ")");
                        })
                        .addOnFailureListener(e -> jsLocal("window.showError&&window.showError("
                                + JSONObject.quote("No se pudo abrir el escaner de QR (" + e.getMessage() + "). Pega el enlace a mano.") + ")"));
            });
        }

        /** Devuelve "" si todo bien, o el mensaje de error. */
        @JavascriptInterface
        public String connectPc(String raw) {
            String url = normalize(raw);
            if (url == null) {
                return "Enlace no valido. Debe verse como http://192.168.x.x:8787/?t=clave (copialo de la app de PC o escanea el QR).";
            }
            runOnUiThread(() -> connectRemote(url));
            return "";
        }

        @JavascriptInterface
        public String savedPc() {
            return prefs().getString(KEY_PC_URL, "");
        }

        @JavascriptInterface
        public String pendingError() {
            String e = pendingError;
            pendingError = "";
            return e;
        }

        /** Desde el modo independiente: volver al menu. */
        @JavascriptInterface
        public void exit() {
            runOnUiThread(() -> backToMenu(null));
        }

        /** POST JSON a un modelo de IA. Va por aqui (no por fetch) para evitar CORS. Responde via window.__aiHttp. */
        @JavascriptInterface
        public void http(final String id, final String url, final String headersJson, final String body) {
            io.execute(() -> {
                HttpURLConnection c = null;
                try {
                    if (!url.startsWith("https://") && !url.startsWith("http://")) throw new IOException("URL no permitida");
                    c = (HttpURLConnection) new URL(url).openConnection();
                    c.setRequestMethod("POST");
                    c.setConnectTimeout(15000);
                    c.setReadTimeout(90000);
                    c.setDoOutput(true);
                    c.setRequestProperty("Content-Type", "application/json");
                    JSONObject h = new JSONObject(headersJson == null ? "{}" : headersJson);
                    for (Iterator<String> it = h.keys(); it.hasNext(); ) {
                        String k = it.next();
                        c.setRequestProperty(k, h.getString(k));
                    }
                    try (OutputStream out = c.getOutputStream()) {
                        out.write(body.getBytes(StandardCharsets.UTF_8));
                    }
                    int status = c.getResponseCode();
                    InputStream in = status >= 400 ? c.getErrorStream() : c.getInputStream();
                    String text = in == null ? "" : readLimited(in);
                    jsLocal("window.__aiHttp(" + JSONObject.quote(id) + "," + status + "," + JSONObject.quote(text) + ")");
                } catch (Exception e) {
                    jsLocal("window.__aiHttpErr(" + JSONObject.quote(id) + "," + JSONObject.quote("Error de red: " + e.getMessage()) + ")");
                } finally {
                    if (c != null) c.disconnect();
                }
            });
        }
    }

    private static String readLimited(InputStream in) throws IOException {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        byte[] chunk = new byte[8192];
        int n;
        while ((n = in.read(chunk)) > 0) {
            buf.write(chunk, 0, n);
            if (buf.size() > MAX_HTTP_RESPONSE) throw new IOException("Respuesta demasiado grande");
        }
        return buf.toString("UTF-8");
    }
}
