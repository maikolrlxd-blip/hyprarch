#!/usr/bin/env python3
"""Un solo comando: relay + tunel HTTPS + registro en Claude Code + QR para el celular.

  python3 phone/start.py
"""
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = Path.home() / ".phone-mcp.json"
PORT = int(os.environ.get("PORT", "8765"))


def need(mod, pkg):
    try:
        __import__(mod)
    except ImportError:
        print(f"Instalando {pkg}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def tunnel():
    """HTTPS publico gratis con cloudflared (si esta instalado); si no, la IP de la red local."""
    if shutil.which("cloudflared"):
        p = subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{PORT}"],
                             stderr=subprocess.PIPE, text=True)
        for line in p.stderr:
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
            if m:
                return m.group(0), "internet (HTTPS)"
    return f"http://{lan_ip()}:{PORT}", "solo tu red Wi-Fi (el celular y la PC en la misma red)"


def register(token):
    if not shutil.which("claude"):
        print("\nNo encontre 'claude'. Registralo a mano:\n  claude mcp add phone "
              f"-e PHONE_RELAY_URL=http://127.0.0.1:{PORT} -e PHONE_TOKEN={token} -- python3 {HERE / 'phone_mcp.py'}")
        return
    subprocess.run(["claude", "mcp", "remove", "phone", "--scope", "user"], capture_output=True)
    r = subprocess.run(["claude", "mcp", "add", "--scope", "user", "phone",
                        "-e", f"PHONE_RELAY_URL=http://127.0.0.1:{PORT}", "-e", f"PHONE_TOKEN={token}",
                        "--", sys.executable, str(HERE / "phone_mcp.py")], capture_output=True, text=True)
    print("Claude Code: herramienta 'phone' registrada ✔" if r.returncode == 0 else f"No pude registrar en Claude: {r.stderr.strip()}")


def main():
    need("aiohttp", "aiohttp")
    cfg = json.loads(CFG.read_text()) if CFG.exists() else {}
    if "token" not in cfg:
        cfg["token"] = secrets.token_urlsafe(32)
        CFG.write_text(json.dumps(cfg))
        CFG.chmod(0o600)
    token = cfg["token"]

    url, where = tunnel()
    link = "phonemcp://pair?" + urllib.parse.urlencode({"u": url, "t": token})
    register(token)

    print(f"\nAlcance: {where}\n\nEn el celular: abre la camara, escanea este QR y toca el enlace.\n")
    try:
        need("qrcode", "qrcode")
        import qrcode
        q = qrcode.QRCode(border=1)
        q.add_data(link)
        q.print_ascii(invert=True)
    except Exception:
        print("(no pude dibujar el QR) Enlace:\n" + link)
    print("\nDejá esta ventana abierta. Ctrl+C para cortar el control del celular.\n")

    sys.path.insert(0, str(HERE / "server"))
    from aiohttp import web
    from relay import make_app
    web.run_app(make_app(), host="0.0.0.0", port=PORT, print=None)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
