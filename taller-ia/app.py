#!/usr/bin/env python3
"""Taller IA como aplicacion: abre una ventana propia (sin barra de navegador ni consola).
Doble clic en TallerIA.exe. Al cerrar la ventana, se apaga el servidor.

Usa el Edge que ya trae Windows 11 (o Chrome/Chromium) en modo "app".
"""
import contextlib
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import taller


def find_browser():
    env = os.environ
    roots = [env.get(k) for k in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA") if env.get(k)]
    rel = [r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe",
           r"BraveSoftware\Brave-Browser\Application\brave.exe"]
    for r in roots:
        for x in rel:
            p = Path(r) / x
            if p.is_file():
                return str(p)
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser", "chrome", "brave-browser"):
        w = shutil.which(name)
        if w:
            return w
    for p in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if Path(p).is_file():
            return p
    return None


def port_free(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def main():
    port = next((p for p in range(8770, 8790) if port_free(p)), None)
    if port is None:
        sys.exit("No hay puerto libre (8770-8789)")
    srv, url = taller.make_server(port)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    exe = find_browser()
    if not exe:  # sin navegador Chromium: pestana normal; se queda corriendo hasta cerrar el proceso
        webbrowser.open(url)
        while True:
            time.sleep(3600)
    profile = taller.DIR / "ventana"
    profile.mkdir(parents=True, exist_ok=True)
    args = [exe, f"--app={url}", f"--user-data-dir={profile}", "--window-size=1500,900",
            "--no-first-run", "--no-default-browser-check", "--disable-features=Translate"]
    if os.environ.get("TALLER_APP_NOSANDBOX"):  # solo para pruebas en contenedores
        args += ["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
    proc = subprocess.Popen(args)
    proc.wait()  # perfil propio => el proceso vive mientras la ventana este abierta
    srv.shutdown()


if __name__ == "__main__":
    main()
