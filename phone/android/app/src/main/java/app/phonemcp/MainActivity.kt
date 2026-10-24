package app.phonemcp

import android.Manifest
import android.app.Activity
import android.content.ClipboardManager
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.text.InputType
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {
    private lateinit var log: TextView
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
        root.addView(label("Pídele algo a la IA y lo hace en este celular. No necesita PC."))

        root.addView(label("1. Permiso (una sola vez)"))
        root.addView(button("Activar accesibilidad") { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) })
        root.addView(label("Android 13+: si sale bloqueado → Ajustes › Apps › Phone MCP › ⋮ › Permitir ajustes restringidos", 12f))

        root.addView(label("2. Tu API key de Anthropic (se guarda solo en este celular)"))
        val key = EditText(this).apply {
            hint = "sk-ant-…"; setSingleLine(); setText(prefs.getString("apikey", ""))
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        }
        root.addView(key)

        root.addView(label("3. ¿Qué quieres que haga?"))
        val task = EditText(this).apply { hint = "Ej: abre WhatsApp y dime quién me escribió"; minLines = 2 }
        root.addView(task)
        root.addView(button("Ejecutar") {
            val t = task.text.toString().trim()
            prefs.edit().putString("apikey", key.text.toString().trim()).apply()
            when {
                t.isEmpty() -> toast("Escribe una tarea")
                key.text.isBlank() -> toast("Falta la API key")
                AgentService.running -> toast("Ya hay una tarea en curso")
                else -> { startForegroundService(Intent(this, AgentService::class.java).putExtra(AgentService.EXTRA_TASK, t)); task.setText("") }
            }
        })
        root.addView(button("Detener") { startService(Intent(this, AgentService::class.java).setAction(AgentService.ACTION_STOP)) })
        root.addView(button("Nueva conversación") { if (!AgentService.running) { AgentService.reset(); log.text = "" } })
        log = label(AgentService.history.toString(), 14f)
        root.addView(log)
        root.addView(label("Te pedirá confirmación antes de enviar, pagar o borrar. Puedes cortarlo con DETENER (aquí o en la notificación).", 12f))

        root.addView(label("Opcional: control desde una PC (modo relay)", 12f))
        status = label(RelayService.status, 12f)
        root.addView(button("Pegar enlace de start.py") { pasteLink() })
        root.addView(status)

        setContentView(ScrollView(this).apply { addView(root) })
        handle(intent)
    }

    override fun onNewIntent(i: Intent) { super.onNewIntent(i); handle(i) }
    private fun handle(i: Intent?) { val u = i?.data ?: return; if (u.scheme == "phonemcp") pair(u) }

    private fun pasteLink() {
        val t = (getSystemService(CLIPBOARD_SERVICE) as ClipboardManager).primaryClip?.getItemAt(0)?.text?.toString()?.trim()
        if (t != null && t.startsWith("phonemcp://")) pair(Uri.parse(t)) else toast("No hay un enlace phonemcp:// copiado")
    }

    private fun pair(u: Uri) {
        val url = u.getQueryParameter("u"); val token = u.getQueryParameter("t")
        if (url.isNullOrBlank() || token.isNullOrBlank()) { toast("Enlace inválido"); return }
        prefs.edit().putString("relay", url).putString("token", token).apply()
        startForegroundService(Intent(this, RelayService::class.java))
    }

    override fun onResume() {
        super.onResume()
        RelayService.onStatus = { s -> runOnUiThread { status.text = s } }
        AgentService.onLog = { t -> runOnUiThread { log.text = t } }
        status.text = RelayService.status; log.text = AgentService.history.toString()
    }
    override fun onPause() { super.onPause(); RelayService.onStatus = null; AgentService.onLog = null }
    private fun toast(m: String) = Toast.makeText(this, m, Toast.LENGTH_LONG).show()
}
