package app.phonemcp

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Path
import android.graphics.Rect
import android.net.Uri
import android.os.Bundle
import android.util.Base64
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/** Ejecuta las acciones que llegan del relay. Cada accion devuelve un JSON {ok, text?, image?, error?}. */
class PhoneAccessibilityService : AccessibilityService() {

    companion object {
        @Volatile var instance: PhoneAccessibilityService? = null
        private const val MAX_DIM = 1280
        private val KEYS = mapOf(
            "back" to GLOBAL_ACTION_BACK, "home" to GLOBAL_ACTION_HOME,
            "recents" to GLOBAL_ACTION_RECENTS, "notifications" to GLOBAL_ACTION_NOTIFICATIONS,
            "quick_settings" to GLOBAL_ACTION_QUICK_SETTINGS, "lock" to GLOBAL_ACTION_LOCK_SCREEN,
        )
    }

    override fun onServiceConnected() { instance = this }
    override fun onUnbind(intent: Intent?): Boolean { instance = null; return super.onUnbind(intent) }
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() {}

    fun execute(action: String, args: JSONObject): JSONObject = try {
        when (action) {
            "screenshot" -> screenshot()
            "ui" -> ok(dumpUi())
            "tap" -> { gesture(args.getDouble("x").toFloat(), args.getDouble("y").toFloat(), null, null, 50); ok("tap") }
            "tap_text" -> tapText(args.getString("text"))
            "swipe" -> {
                gesture(args.getDouble("x1").toFloat(), args.getDouble("y1").toFloat(),
                    args.getDouble("x2").toFloat(), args.getDouble("y2").toFloat(), args.optLong("ms", 300))
                ok("swipe")
            }
            "scroll" -> scroll(args.optString("direction", "down"))
            "text" -> typeText(args.getString("text"))
            "key" -> key(args.getString("key"))
            "launch" -> launch(args.getString("package"))
            "packages" -> ok(packages())
            "open_url" -> {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(args.getString("url"))).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                ok("abierto")
            }
            else -> err("accion desconocida: $action")
        }
    } catch (e: Exception) { err(e.message ?: e.javaClass.simpleName) }

    private fun ok(text: String) = JSONObject().put("ok", true).put("text", text)
    private fun err(msg: String) = JSONObject().put("ok", false).put("error", msg)

    private fun gesture(x1: Float, y1: Float, x2: Float?, y2: Float?, ms: Long) {
        val path = Path().apply { moveTo(x1, y1); if (x2 != null && y2 != null) lineTo(x2, y2) }
        val g = GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(path, 0, ms.coerceAtLeast(1))).build()
        val done = CountDownLatch(1)
        var success = false
        dispatchGesture(g, object : GestureResultCallback() {
            override fun onCompleted(d: GestureDescription?) { success = true; done.countDown() }
            override fun onCancelled(d: GestureDescription?) { done.countDown() }
        }, null)
        done.await(5, TimeUnit.SECONDS)
        if (!success) throw IllegalStateException("el gesto fue cancelado (¿pantalla bloqueada o app protegida?)")
    }

    private fun scroll(dir: String): JSONObject {
        val m = resources.displayMetrics
        val cx = m.widthPixels / 2f
        val top = m.heightPixels * 0.3f
        val bot = m.heightPixels * 0.7f
        if (dir == "up") gesture(cx, top, cx, bot, 400) else gesture(cx, bot, cx, top, 400)
        return ok("scroll $dir")
    }

    private fun key(k: String): JSONObject {
        val a = KEYS[k.lowercase()] ?: return err("tecla no soportada: $k (usa ${KEYS.keys.joinToString()})")
        return if (performGlobalAction(a)) ok("key $k") else err("no se pudo ejecutar $k")
    }

    private fun typeText(text: String): JSONObject {
        val node = rootInActiveWindow?.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
            ?: return err("no hay un campo de texto enfocado; toca el campo primero")
        val current = if (node.isShowingHintText) "" else node.text?.toString() ?: ""
        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, current + text)
        }
        return if (node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)) ok("texto enviado") else err("el campo no acepta texto")
    }

    private fun launch(pkg: String): JSONObject {
        val i = packageManager.getLaunchIntentForPackage(pkg) ?: return err("app no encontrada: $pkg")
        startActivity(i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        return ok("abierto $pkg")
    }

    private fun packages(): String {
        val i = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        return packageManager.queryIntentActivities(i, PackageManager.MATCH_ALL)
            .joinToString("\n") { "${it.activityInfo.packageName}  ${it.loadLabel(packageManager)}" }
    }

    // ---- lectura de pantalla ----

    private data class Item(val clickable: Boolean, val cx: Int, val cy: Int, val label: String, val id: String)

    private fun items(): List<Item> {
        val out = ArrayList<Item>()
        fun walk(n: AccessibilityNodeInfo?) {
            if (n == null) return
            if (n.isVisibleToUser) {
                val text = n.text?.toString()?.takeIf { it.isNotBlank() } ?: n.contentDescription?.toString()
                val click = n.isClickable || n.isLongClickable
                if (!text.isNullOrBlank() || click) {
                    val r = Rect().also { n.getBoundsInScreen(it) }
                    val id = n.viewIdResourceName?.substringAfterLast('/') ?: ""
                    out += Item(click, r.centerX(), r.centerY(), text ?: id.ifEmpty { n.className?.toString()?.substringAfterLast('.') ?: "" }, id)
                }
            }
            for (i in 0 until n.childCount) walk(n.getChild(i))
        }
        walk(rootInActiveWindow)
        return out
    }

    private fun dumpUi(): String =
        "* = clickeable. Coordenadas = centro del elemento.\n" +
            items().joinToString("\n") { "${if (it.clickable) "*" else " "} (${it.cx},${it.cy}) '${it.label}'" + if (it.id.isNotEmpty()) " id=${it.id}" else "" }

    private fun tapText(q: String): JSONObject {
        val hit = items().firstOrNull { it.label.contains(q, ignoreCase = true) } ?: return err("no hay ningun elemento con '$q' en pantalla")
        gesture(hit.cx.toFloat(), hit.cy.toFloat(), null, null, 50)
        return ok("tap ${hit.cx},${hit.cy} -> ${hit.label}")
    }

    private fun screenshot(): JSONObject {
        val done = CountDownLatch(1)
        var result: JSONObject? = null
        takeScreenshot(0, mainExecutor, object : TakeScreenshotCallback {
            override fun onSuccess(s: ScreenshotResult) {
                try {
                    val hw = Bitmap.wrapHardwareBuffer(s.hardwareBuffer, s.colorSpace)!!
                    var bmp = hw.copy(Bitmap.Config.ARGB_8888, false)
                    s.hardwareBuffer.close()
                    val w = bmp.width; val h = bmp.height
                    var note = "Pantalla real: ${w}x${h}px. Las coordenadas de tap/swipe son en px reales."
                    val k = MAX_DIM.toFloat() / maxOf(w, h)
                    if (k < 1f) {
                        bmp = Bitmap.createScaledBitmap(bmp, (w * k).toInt(), (h * k).toInt(), true)
                        note += " Imagen reducida a ${bmp.width}x${bmp.height}; multiplica por ${"%.3f".format(1 / k)} para px reales."
                    }
                    val bos = ByteArrayOutputStream()
                    bmp.compress(Bitmap.CompressFormat.JPEG, 70, bos)
                    result = ok(note).put("image", Base64.encodeToString(bos.toByteArray(), Base64.NO_WRAP)).put("mime", "image/jpeg")
                } catch (e: Exception) { result = err("captura fallida: ${e.message}") }
                done.countDown()
            }
            override fun onFailure(code: Int) { result = err("captura fallida (codigo $code)"); done.countDown() }
        })
        done.await(10, TimeUnit.SECONDS)
        return result ?: err("tiempo agotado al capturar")
    }
}
