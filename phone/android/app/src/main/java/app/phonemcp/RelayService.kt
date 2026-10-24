package app.phonemcp

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.IBinder
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

/** Mantiene el WebSocket con el relay y despacha cada comando al servicio de accesibilidad. */
class RelayService : Service() {

    companion object {
        const val ACTION_STOP = "app.phonemcp.STOP"
        @Volatile var status = "Desconectado"
        @Volatile var onStatus: ((String) -> Unit)? = null
        fun updateStatus(s: String) { status = s; onStatus?.invoke(s) }
    }

    private val http = OkHttpClient.Builder().pingInterval(20, TimeUnit.SECONDS).readTimeout(0, TimeUnit.MILLISECONDS).build()
    private val worker = Executors.newSingleThreadExecutor() // un comando a la vez, en orden
    private var socket: WebSocket? = null
    private var stopped = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) { stopSelf(); return START_NOT_STICKY }
        startForeground(1, notification(), ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        stopped = false
        connect()
        return START_STICKY
    }

    override fun onDestroy() {
        stopped = true
        socket?.close(1000, "stop")
        worker.shutdownNow()
        updateStatus("Desconectado")
    }

    private fun connect() {
        val prefs = getSharedPreferences("cfg", MODE_PRIVATE)
        val url = prefs.getString("relay", "")!!.trimEnd('/').replaceFirst("http", "ws") + "/ws/phone"
        val token = prefs.getString("token", "")!!
        updateStatus("Conectando…")
        socket = http.newWebSocket(Request.Builder().url(url).header("Authorization", "Bearer $token").build(), object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, r: Response) = updateStatus("Conectado: el asistente puede controlar este celular")
            override fun onMessage(ws: WebSocket, text: String) {
                worker.execute {
                    val req = JSONObject(text)
                    val svc = PhoneAccessibilityService.instance
                    val res = svc?.execute(req.getString("action"), req.optJSONObject("args") ?: JSONObject())
                        ?: JSONObject().put("ok", false).put("error", "El servicio de accesibilidad no esta activado en el celular")
                    ws.send(res.put("id", req.getString("id")).toString())
                }
            }
            override fun onFailure(ws: WebSocket, t: Throwable, r: Response?) = retry("Error: ${t.message}")
            override fun onClosed(ws: WebSocket, code: Int, reason: String) = retry("Desconectado")
        })
    }

    private fun retry(msg: String) {
        if (stopped) return
        updateStatus("$msg. Reintentando…")
        Thread { Thread.sleep(5000); if (!stopped) connect() }.start()
    }

    private fun notification(): Notification {
        val nm = getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel("ctl", "Control remoto", NotificationManager.IMPORTANCE_LOW))
        val stop = PendingIntent.getService(this, 0, Intent(this, RelayService::class.java).setAction(ACTION_STOP), PendingIntent.FLAG_IMMUTABLE)
        return Notification.Builder(this, "ctl")
            .setSmallIcon(android.R.drawable.ic_lock_idle_lock)
            .setContentTitle("Control remoto ACTIVO")
            .setContentText("Un asistente de IA puede controlar este celular. Toca DETENER para cortarlo.")
            .setOngoing(true)
            .addAction(Notification.Action.Builder(null, "DETENER", stop).build())
            .build()
    }
}
