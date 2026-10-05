package app.phonemcp

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.IBinder
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Agente en el propio celular (sin PC): Claude ve la pantalla, decide una accion, la ejecuta
 * el servicio de accesibilidad y el resultado vuelve a Claude, en bucle hasta terminar.
 */
class AgentService : Service() {

    companion object {
        const val ACTION_STOP = "app.phonemcp.AGENT_STOP"
        const val EXTRA_TASK = "task"
        const val MAX_STEPS = 40
        const val MODEL = "claude-sonnet-5-5"
        @Volatile var running = false
        @Volatile var onLog: ((String) -> Unit)? = null
        val history = StringBuilder()
        /** Conversacion en curso; permite responder a una pregunta del asistente. */
        val messages = JSONArray()
        fun reset() { synchronized(messages) { while (messages.length() > 0) messages.remove(0) }; history.setLength(0) }
        fun log(s: String) { history.append(s).append('\n'); onLog?.invoke(history.toString()) }

        private fun tool(name: String, desc: String, props: JSONObject = JSONObject(), req: List<String> = emptyList()) =
            JSONObject().put("name", name).put("description", desc).put("input_schema",
                JSONObject().put("type", "object").put("properties", props).put("required", JSONArray(req)))
        private fun n(d: String) = JSONObject().put("type", "number").put("description", d)
        private fun s(d: String) = JSONObject().put("type", "string").put("description", d)

        val TOOLS = JSONArray(listOf(
            tool("screenshot", "Captura la pantalla. Las coordenadas son en px reales."),
            tool("ui", "Lista los elementos en pantalla con texto y coordenadas del centro. Mas barato y preciso que screenshot."),
            tool("tap", "Toca en (x,y).", JSONObject().put("x", n("x")).put("y", n("y")), listOf("x", "y")),
            tool("tap_text", "Toca el primer elemento cuyo texto contenga el valor dado.", JSONObject().put("text", s("texto")), listOf("text")),
            tool("swipe", "Desliza de (x1,y1) a (x2,y2).", JSONObject().put("x1", n("x1")).put("y1", n("y1")).put("x2", n("x2")).put("y2", n("y2")), listOf("x1", "y1", "x2", "y2")),
            tool("scroll", "Desplaza la pantalla.", JSONObject().put("direction", s("down o up"))),
            tool("text", "Escribe texto en el campo enfocado (toca el campo antes).", JSONObject().put("text", s("texto")), listOf("text")),
            tool("key", "Tecla global: back, home, recents, notifications, quick_settings, lock.", JSONObject().put("key", s("tecla")), listOf("key")),
            tool("launch", "Abre una app por paquete (usa packages para buscarlo).", JSONObject().put("package", s("paquete")), listOf("package")),
            tool("packages", "Lista las apps instaladas con su paquete."),
            tool("open_url", "Abre una URL.", JSONObject().put("url", s("url")), listOf("url")),
        ))

        const val SYSTEM = "Eres un asistente que controla el celular de tu usuario, con su permiso, para cumplir su tarea. " +
            "Prefiere 'ui' o 'tap_text' antes que 'screenshot'. Haz una accion por paso y verifica el resultado. " +
            "ANTES de cualquier accion irreversible o con consecuencias (enviar mensajes o correos, pagar, comprar, borrar, publicar, cambiar contrasenas) " +
            "detente y pidele confirmacion al usuario en texto, sin ejecutarla. " +
            "Nunca escribas contrasenas ni datos de pago por tu cuenta. Si algo es ambiguo, pregunta. Responde en el idioma del usuario y se breve."
    }

    private val http = OkHttpClient.Builder().callTimeout(150, TimeUnit.SECONDS).readTimeout(150, TimeUnit.SECONDS).build()
    @Volatile private var cancelled = false
    private var worker: Thread? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) { cancelled = true; stopSelf(); return START_NOT_STICKY }
        val task = intent?.getStringExtra(EXTRA_TASK) ?: return START_NOT_STICKY
        if (running) return START_NOT_STICKY
        startForeground(2, notification("Trabajando en tu tarea…"), ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        cancelled = false; running = true
        worker = Thread { try { run(task) } catch (e: Exception) { log("⚠ ${e.message}") } finally { running = false; stopSelf() } }.also { it.start() }
        return START_NOT_STICKY
    }

    override fun onDestroy() { cancelled = true; running = false }

    private fun run(task: String) {
        val key = getSharedPreferences("cfg", MODE_PRIVATE).getString("apikey", "")!!
        if (key.isBlank()) { log("⚠ Falta la API key"); return }
        if (PhoneAccessibilityService.instance == null) { log("⚠ Activa primero el servicio de accesibilidad"); return }
        synchronized(messages) { messages.put(JSONObject().put("role", "user").put("content", task)) }
        log("▶ $task")
        var steps = 0
        while (!cancelled && steps++ < MAX_STEPS) {
            val resp = call(key)
            val content = resp.getJSONArray("content")
            synchronized(messages) { messages.put(JSONObject().put("role", "assistant").put("content", content)) }
            val results = JSONArray()
            for (i in 0 until content.length()) {
                val b = content.getJSONObject(i)
                if (b.getString("type") == "text" && b.getString("text").isNotBlank()) log("💬 ${b.getString("text")}")
                if (b.getString("type") != "tool_use") continue
                val name = b.getString("name"); val input = b.getJSONObject("input")
                log("• $name ${input.toString().take(80)}")
                updateNotification("Ejecutando: $name")
                val r = if (cancelled) JSONObject().put("ok", false).put("error", "cancelado") else PhoneAccessibilityService.instance!!.execute(name, input)
                val parts = JSONArray()
                if (r.has("image")) parts.put(JSONObject().put("type", "image").put("source",
                    JSONObject().put("type", "base64").put("media_type", r.optString("mime", "image/jpeg")).put("data", r.getString("image"))))
                parts.put(JSONObject().put("type", "text").put("text", if (r.optBoolean("ok")) r.optString("text", "ok") else "Error: ${r.optString("error")}"))
                results.put(JSONObject().put("type", "tool_result").put("tool_use_id", b.getString("id")).put("content", parts).put("is_error", !r.optBoolean("ok")))
            }
            if (results.length() == 0) { log("✔ Listo"); return }
            synchronized(messages) { messages.put(JSONObject().put("role", "user").put("content", results)) }
        }
        log(if (cancelled) "■ Detenido" else "■ Limite de $MAX_STEPS pasos alcanzado")
    }

    /** Mantiene solo las 2 imagenes mas recientes para no inflar el contexto. */
    private fun trimmed(): JSONArray {
        val copy = JSONArray(synchronized(messages) { messages.toString() })
        var seen = 0
        for (m in copy.length() - 1 downTo 0) {
            val c = copy.getJSONObject(m).opt("content") as? JSONArray ?: continue
            for (i in 0 until c.length()) {
                val parts = c.optJSONObject(i)?.optJSONArray("content") ?: continue
                var hasImg = false
                for (j in parts.length() - 1 downTo 0) if (parts.getJSONObject(j).optString("type") == "image") {
                    hasImg = true
                    if (seen >= 2) parts.put(j, JSONObject().put("type", "text").put("text", "[captura anterior omitida]"))
                }
                if (hasImg) seen++
            }
        }
        return copy
    }

    private fun call(key: String): JSONObject {
        val body = JSONObject().put("model", MODEL).put("max_tokens", 1024).put("system", SYSTEM)
            .put("tools", TOOLS).put("messages", trimmed())
        val req = Request.Builder().url("https://api.anthropic.com/v1/messages")
            .header("x-api-key", key).header("anthropic-version", "2023-06-01")
            .post(body.toString().toRequestBody("application/json".toMediaType())).build()
        http.newCall(req).execute().use {
            val txt = it.body?.string() ?: ""
            if (!it.isSuccessful) throw IllegalStateException("API ${it.code}: ${runCatching { JSONObject(txt).getJSONObject("error").getString("message") }.getOrDefault(txt.take(200))}")
            return JSONObject(txt)
        }
    }

    private fun notification(text: String): Notification {
        getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel("agent", "Asistente", NotificationManager.IMPORTANCE_LOW))
        val stop = PendingIntent.getService(this, 1, Intent(this, AgentService::class.java).setAction(ACTION_STOP), PendingIntent.FLAG_IMMUTABLE)
        return Notification.Builder(this, "agent").setSmallIcon(android.R.drawable.ic_lock_idle_lock)
            .setContentTitle("Asistente controlando el celular").setContentText(text).setOngoing(true)
            .addAction(Notification.Action.Builder(null, "DETENER", stop).build()).build()
    }

    private fun updateNotification(text: String) = getSystemService(NotificationManager::class.java).notify(2, notification(text))
}
