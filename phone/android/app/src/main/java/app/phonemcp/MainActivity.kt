package app.phonemcp

import android.Manifest
import android.app.Activity
import android.content.ClipboardManager
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {
    private lateinit var status: TextView
    private val prefs get() = getSharedPreferences("cfg", MODE_PRIVATE)

    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
        val pad = (20 * resources.displayMetrics.density).toInt()
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(pad, pad, pad, pad) }
        fun label(t: String, size: Float = 16f) = TextView(this).apply { text = t; textSize = size; setPadding(0, pad / 2, 0, pad / 4) }
        fun button(t: String, f: () -> Unit) = Button(this).apply { text = t; setOnClickListener { f() } }

        root.addView(label("Phone MCP", 26f))
        root.addView(label("Deja que un asistente de IA que TÚ autorices use este celular."))
        root.addView(label("1. Activa el permiso (una sola vez)"))
        root.addView(button("Abrir accesibilidad") { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) })
        root.addView(label("Android 13+: si sale bloqueado → Ajustes › Apps › Phone MCP › ⋮ › Permitir ajustes restringidos", 12f))
        root.addView(label("2. En tu PC ejecuta start.py y escanea el QR con la cámara del celular. Se conecta solo."))
        root.addView(button("Pegar enlace (si no puedes escanear)") { pasteLink() })
        status = label(RelayService.status)
        root.addView(status)
        root.addView(button("Detener control remoto") { startService(Intent(this, RelayService::class.java).setAction(RelayService.ACTION_STOP)) })
        setContentView(ScrollView(this).apply { addView(root) })
        handle(intent)
    }

    override fun onNewIntent(i: Intent) { super.onNewIntent(i); handle(i) }

    private fun handle(i: Intent?) {
        val u = i?.data ?: return
        if (u.scheme == "phonemcp") pair(u)
    }

    private fun pasteLink() {
        val t = (getSystemService(CLIPBOARD_SERVICE) as ClipboardManager).primaryClip?.getItemAt(0)?.text?.toString()?.trim()
        if (t != null && t.startsWith("phonemcp://")) pair(Uri.parse(t)) else Toast.makeText(this, "No hay un enlace phonemcp:// copiado", Toast.LENGTH_LONG).show()
    }

    private fun pair(u: Uri) {
        val url = u.getQueryParameter("u"); val token = u.getQueryParameter("t")
        if (url.isNullOrBlank() || token.isNullOrBlank()) { Toast.makeText(this, "Enlace inválido", Toast.LENGTH_LONG).show(); return }
        prefs.edit().putString("relay", url).putString("token", token).apply()
        startForegroundService(Intent(this, RelayService::class.java))
        Toast.makeText(this, "Conectando…", Toast.LENGTH_SHORT).show()
    }

    override fun onResume() { super.onResume(); RelayService.onStatus = { s -> runOnUiThread { status.text = s } }; status.text = RelayService.status }
    override fun onPause() { super.onPause(); RelayService.onStatus = null }
}
