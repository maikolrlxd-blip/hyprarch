package app.phonemcp

import android.Manifest
import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.util.Base64
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import java.security.SecureRandom

class MainActivity : Activity() {
    private lateinit var status: TextView
    private lateinit var relay: EditText

    private val prefs get() = getSharedPreferences("cfg", MODE_PRIVATE)

    private fun token(): String = prefs.getString("token", null) ?: run {
        val b = ByteArray(32).also { SecureRandom().nextBytes(it) }
        Base64.encodeToString(b, Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP).also { prefs.edit().putString("token", it).apply() }
    }

    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
        val pad = (20 * resources.displayMetrics.density).toInt()
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(pad, pad, pad, pad) }

        fun label(t: String, size: Float = 15f) = TextView(this).apply { text = t; textSize = size; setPadding(0, pad / 2, 0, pad / 4) }
        fun button(t: String, f: () -> Unit) = Button(this).apply { text = t; setOnClickListener { f() } }

        root.addView(label("Phone MCP", 26f))
        root.addView(label("Deja que un asistente de IA que TÚ autorices use este celular. Puedes cortarlo cuando quieras con el botón Detener."))
        root.addView(label("1. Activa el servicio de accesibilidad"))
        root.addView(button("Abrir ajustes de accesibilidad") { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) })
        root.addView(label("(Android 13+: si aparece bloqueado, ve a Ajustes › Apps › Phone MCP › ⋮ › Permitir ajustes restringidos)", 12f))
        root.addView(label("2. Dirección de tu servidor relay"))
        relay = EditText(this).apply { hint = "https://relay.ejemplo.com"; setText(prefs.getString("relay", "")); setSingleLine() }
        root.addView(relay)
        root.addView(label("3. Conecta"))
        status = label(RelayService.status).apply { gravity = Gravity.START }
        root.addView(button("Conectar") {
            prefs.edit().putString("relay", relay.text.toString().trim()).apply()
            if (relay.text.isBlank()) { toast("Escribe la dirección del relay"); return@button }
            token()
            startForegroundService(Intent(this, RelayService::class.java))
        })
        root.addView(button("Detener") { startService(Intent(this, RelayService::class.java).setAction(RelayService.ACTION_STOP)) })
        root.addView(status)
        root.addView(label("4. Dale acceso a Claude"))
        root.addView(button("Copiar comando para Claude Code") {
            val cmd = "claude mcp add phone -e PHONE_RELAY_URL=${relay.text.toString().trim()} -e PHONE_TOKEN=${token()} -- python3 phone_mcp.py"
            (getSystemService(CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(ClipData.newPlainText("cmd", cmd))
            toast("Copiado. Contiene tu clave secreta: no la compartas.")
        })
        root.addView(button("Generar clave nueva (revoca la anterior)") {
            prefs.edit().remove("token").apply(); token(); toast("Clave nueva creada. Vuelve a conectar y copiar el comando.")
        })
        setContentView(android.widget.ScrollView(this).apply { addView(root) })
    }

    override fun onResume() { super.onResume(); RelayService.onStatus = { s -> runOnUiThread { status.text = s } }; status.text = RelayService.status }
    override fun onPause() { super.onPause(); RelayService.onStatus = null }
    private fun toast(m: String) = Toast.makeText(this, m, Toast.LENGTH_LONG).show()
}
