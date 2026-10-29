#!/usr/bin/env python3
"""phone-mcp: servidor MCP (stdio) para controlar un celular Android por ADB.

Sin dependencias obligatorias (solo biblioteca estandar + `adb`).
Si Pillow esta instalado, las capturas se reducen para ahorrar tokens.
Dos modos:
  - ADB (por defecto): ADB (ruta de adb), ANDROID_SERIAL (dispositivo por defecto).
  - Relay (app Android): PHONE_RELAY_URL (ej. https://relay.ejemplo.com) y PHONE_TOKEN.
"""
import urllib.error
import urllib.request
import base64
import io
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ADB = os.environ.get("ADB", "adb")
MAX_DIM = int(os.environ.get("PHONE_MAX_DIM", "1280"))


def adb(*args, serial=None, binary=False, timeout=30):
    cmd = [ADB]
    serial = serial or os.environ.get("ANDROID_SERIAL")
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        raise RuntimeError("No se encontro 'adb'. Instala android-tools (pacman -S android-tools).")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).decode("utf-8", "replace").strip() or "adb fallo")
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def screen_size(serial=None):
    m = re.search(r"(\d+)x(\d+)", adb("shell", "wm", "size", serial=serial).split("Override size:")[-1])
    return int(m.group(1)), int(m.group(2))


# ---------- herramientas ----------

def t_devices(a):
    return adb("devices", "-l").strip()


def t_screenshot(a):
    png = adb("exec-out", "screencap", "-p", serial=a.get("serial"), binary=True)
    w, h = screen_size(a.get("serial"))
    note = f"Pantalla real: {w}x{h}px. Las coordenadas de tap/swipe son en px reales."
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(png))
        if max(im.size) > MAX_DIM:
            k = MAX_DIM / max(im.size)
            im = im.resize((int(im.width * k), int(im.height * k)))
            note += f" Imagen reducida a {im.width}x{im.height}; multiplica por {1 / k:.3f} para obtener px reales."
        buf = io.BytesIO()
        im.save(buf, "PNG")
        png = buf.getvalue()
    except ImportError:
        pass
    return [{"type": "image", "data": base64.b64encode(png).decode(), "mimeType": "image/png"},
            {"type": "text", "text": note}]


def t_ui(a):
    """Lista compacta de elementos visibles con su centro (mas barata y precisa que una captura)."""
    xml = adb("exec-out", "uiautomator", "dump", "/dev/tty", serial=a.get("serial"), timeout=40)
    xml = xml[xml.find("<?xml"):xml.rfind("</hierarchy>") + len("</hierarchy>")]
    rows = []
    for n in ET.fromstring(xml).iter("node"):
        text, desc, rid = n.get("text"), n.get("content-desc"), n.get("resource-id", "")
        click = n.get("clickable") == "true" or n.get("long-clickable") == "true"
        if not (text or desc or click):
            continue
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", n.get("bounds", ""))
        if not m:
            continue
        x1, y1, x2, y2 = map(int, m.groups())
        label = text or desc or rid.split("/")[-1] or n.get("class", "").split(".")[-1]
        rows.append(f"{'*' if click else ' '} ({(x1 + x2) // 2},{(y1 + y2) // 2}) {label!r}"
                    + (f" id={rid.split('/')[-1]}" if rid else ""))
    return "* = clickeable. Coordenadas = centro del elemento.\n" + "\n".join(rows)


def t_tap(a):
    adb("shell", "input", "tap", str(int(a["x"])), str(int(a["y"])), serial=a.get("serial"))
    return f"tap {a['x']},{a['y']}"


def t_tap_text(a):
    want = a["text"].lower()
    for line in t_ui(a).splitlines()[1:]:
        m = re.match(r".\s\((\d+),(\d+)\)\s(.*)", line)
        if m and want in m.group(3).lower():
            return t_tap({"x": m.group(1), "y": m.group(2), "serial": a.get("serial")}) + f" -> {m.group(3)}"
    raise RuntimeError(f"No hay ningun elemento con '{a['text']}' en pantalla")


def t_swipe(a):
    adb("shell", "input", "swipe", *(str(int(a[k])) for k in ("x1", "y1", "x2", "y2")),
        str(int(a.get("ms", 300))), serial=a.get("serial"))
    return "swipe ok"


def t_scroll(a):
    w, h = screen_size(a.get("serial"))
    cx, top, bot = w // 2, int(h * 0.3), int(h * 0.7)
    y1, y2 = (bot, top) if a.get("direction", "down") == "down" else (top, bot)
    return t_swipe({"x1": cx, "y1": y1, "x2": cx, "y2": y2, "ms": 400, "serial": a.get("serial")})


def t_text(a):
    # `input text` solo acepta ASCII; los espacios van como %s
    s = a["text"]
    if not s.isascii():
        raise RuntimeError("adb input text solo soporta ASCII (sin tildes/emojis).")
    esc = re.sub(r"([\\'\"&|;<>()$`!*?~#{}\[\]])", r"\\\1", s.replace("%", "%25")).replace(" ", "%s")
    adb("shell", "input", "text", esc, serial=a.get("serial"))
    return "texto enviado"


KEYS = {"back": 4, "home": 3, "recents": 187, "enter": 66, "power": 26, "delete": 67,
        "volume_up": 24, "volume_down": 25, "menu": 82, "tab": 61, "wake": 224}


def t_key(a):
    k = a["key"].lower()
    adb("shell", "input", "keyevent", str(KEYS.get(k, k)), serial=a.get("serial"))
    return f"key {k}"


def t_launch(a):
    pkg = a["package"]
    adb("shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1", serial=a.get("serial"))
    return f"abierto {pkg}"


def t_packages(a):
    out = adb("shell", "pm", "list", "packages", "-3", serial=a.get("serial"))
    return out.replace("package:", "").strip()


def t_open_url(a):
    adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", a["url"], serial=a.get("serial"))
    return f"abierto {a['url']}"


S = {"serial": {"type": "string", "description": "Serial ADB (opcional si hay un solo dispositivo)"}}


def schema(**props):
    return {"type": "object", "properties": {**props, **S}, "required": [k for k, v in props.items() if not v.pop("optional", False)]}


def num(d, **kw): return {"type": "number", "description": d, **kw}
def string(d, **kw): return {"type": "string", "description": d, **kw}


TOOLS = {
    "phone_devices": (t_devices, "Lista los dispositivos Android conectados por ADB.", schema()),
    "phone_screenshot": (t_screenshot, "Captura la pantalla del celular.", schema()),
    "phone_ui": (t_ui, "Lista los elementos de la pantalla (texto + coordenadas del centro). Preferir sobre captura para decidir donde tocar.", schema()),
    "phone_tap": (t_tap, "Toca en (x,y) en px reales.", schema(x=num("x"), y=num("y"))),
    "phone_tap_text": (t_tap_text, "Toca el primer elemento cuyo texto/descripcion contenga el texto dado.", schema(text=string("texto a buscar"))),
    "phone_swipe": (t_swipe, "Desliza de (x1,y1) a (x2,y2).", schema(x1=num("x1"), y1=num("y1"), x2=num("x2"), y2=num("y2"), ms=num("duracion ms", optional=True))),
    "phone_scroll": (t_scroll, "Desplaza la pantalla hacia 'down' o 'up'.", schema(direction=string("down|up", enum=["down", "up"], optional=True))),
    "phone_text": (t_text, "Escribe texto (ASCII) en el campo enfocado.", schema(text=string("texto"))),
    "phone_key": (t_key, "Pulsa una tecla: back, home, recents, enter, power, delete, volume_up, volume_down, menu, tab, wake, o un keycode numerico.", schema(key=string("tecla"))),
    "phone_launch": (t_launch, "Abre una app por nombre de paquete (ej. com.whatsapp).", schema(package=string("paquete"))),
    "phone_packages": (t_packages, "Lista las apps de terceros instaladas.", schema()),
    "phone_open_url": (t_open_url, "Abre una URL o deep link en el celular.", schema(url=string("url"))),
}


# ---------- modo relay: la app Android ejecuta la accion ----------

RELAY_URL = os.environ.get("PHONE_RELAY_URL", "").rstrip("/")
RELAY_TOKEN = os.environ.get("PHONE_TOKEN", "")


def relay_call(tool, args):
    req = urllib.request.Request(
        RELAY_URL + "/api/cmd",
        data=json.dumps({"action": tool[len("phone_"):], "args": args}).encode(),
        headers={"Authorization": "Bearer " + RELAY_TOKEN, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            res = json.loads(e.read())
        except ValueError:
            res = {"ok": False, "error": "Token invalido o relay rechazo la peticion" if e.code == 401 else f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        raise RuntimeError(f"No se pudo contactar el relay: {e.reason}")
    if not res.get("ok"):
        raise RuntimeError(res.get("error", "fallo desconocido"))
    content = []
    if res.get("image"):
        content.append({"type": "image", "data": res["image"], "mimeType": res.get("mime", "image/jpeg")})
    content.append({"type": "text", "text": res.get("text", "ok")})
    return content


# ---------- protocolo MCP (JSON-RPC por stdio, un mensaje por linea) ----------

def handle(req):
    m, p = req.get("method"), req.get("params") or {}
    if m == "initialize":
        return {"protocolVersion": p.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "phone-mcp", "version": "0.1.0"}}
    if m == "ping":
        return {}
    if m == "tools/list":
        return {"tools": [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in TOOLS.items()]}
    if m == "tools/call":
        name = p.get("name")
        if name not in TOOLS:
            raise KeyError(name)
        try:
            args = p.get("arguments") or {}
            out = relay_call(name, args) if RELAY_URL else TOOLS[name][0](args)
            content = out if isinstance(out, list) else [{"type": "text", "text": out}]
            return {"content": content}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
    raise NotImplementedError(m)


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        if "id" not in req:  # notificacion
            continue
        try:
            resp = {"jsonrpc": "2.0", "id": req["id"], "result": handle(req)}
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": str(e)}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
