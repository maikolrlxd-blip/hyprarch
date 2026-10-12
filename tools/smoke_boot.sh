#!/usr/bin/env bash
set -euo pipefail

# Uso: bash tools/smoke_boot.sh ISO [bios|uefi] [directorio-nuevo]
#
# Requisitos de la ISO:
# - Arranque automático y sesión gráfica automática.
# - Renderizado por software disponible dentro del invitado.
# - En las entradas BIOS y UEFI, agregar al kernel:
#     console=ttyS0,115200n8 console=tty0
#   -serial de QEMU NO configura la consola del kernel invitado.
#
# SMOKE_REQUIRE_HYPRARCH=1 exige "hyprarch" en serie.
# SMOKE_READY_MARKER permite exigir un marcador emitido por la sesión.
# SMOKE_GPU=virtio usa virtio-vga; SMOKE_GPU=std sirve como alternativa.

iso=$(realpath -e -- "${1:?Falta la ISO}")
firmware=${2:-bios}
output=${3:-smoke-${firmware}}
gpu=${SMOKE_GPU:-virtio}
[[ -f "$iso" ]] || { echo "No es un archivo ISO" >&2; exit 2; }
case "$gpu" in virtio|std) ;; *) echo "SMOKE_GPU: virtio o std" >&2; exit 2 ;; esac
case "$firmware" in bios|uefi) ;; *) echo "Firmware: bios o uefi" >&2; exit 2 ;; esac
for tool in qemu-system-x86_64 python3; do command -v "$tool" >/dev/null; done

# Directorio exclusivo: nunca aceptar evidencia de una prueba anterior.
mkdir -- "$output"
output=$(realpath -- "$output")
case "$iso$output" in *,*) echo "Usá rutas sin comas" >&2; exit 2 ;; esac

args=(-machine q35 -accel kvm -accel "tcg,thread=multi"
      -cpu max -smp 2 -m 4096 -vga "$gpu" -display none
      -monitor none -qmp "unix:qmp.sock,server=on,wait=off"
      -serial "file:$output/serial.log" -nic none
      -boot "order=d,menu=off" -cdrom "$iso" -no-reboot)

if [[ "$firmware" == uefi ]]; then
    code=/usr/share/OVMF/OVMF_CODE_4M.fd
    vars=/usr/share/OVMF/OVMF_VARS_4M.fd
    if [[ ! -r "$code" || ! -r "$vars" ]]; then
        code=/usr/share/OVMF/OVMF_CODE.fd
        vars=/usr/share/OVMF/OVMF_VARS.fd
    fi
    [[ -r "$code" && -r "$vars" ]] || { echo "Falta OVMF" >&2; exit 2; }
    cp -- "$vars" "$output/OVMF_VARS.fd"
    args+=(-drive "if=pflash,format=raw,readonly=on,file=$code"
           -drive "if=pflash,format=raw,file=$output/OVMF_VARS.fd")
fi

qemu-system-x86_64 --version >"$output/versions.log"
python3 --version >>"$output/versions.log"

# Biblioteca estándar: QMP/JSON, PPM binario y control del proceso.
exec python3 - "$output" "${args[@]}" <<'PY'
import collections
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time

out = Path(sys.argv[1])
black_max = float(os.environ.get("SMOKE_BLACK_MAX", "0.99"))
dominant_max = float(os.environ.get("SMOKE_DOMINANT_MAX", "0.995"))
require_brand = os.environ.get("SMOKE_REQUIRE_HYPRARCH", "0") == "1"
ready_marker = os.environ.get("SMOKE_READY_MARKER", "").encode()
if not (0 < black_max < 1 and 0 < dominant_max < 1):
    raise SystemExit("Los umbrales deben estar entre 0 y 1")


def interrupted(signum, _frame):
    raise SystemExit(128 + signum)


signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGINT, interrupted)


def capture(sockpath, filename, deadline):
    # Reconectar permite recuperarse de un timeout sin desincronizar QMP.
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        limit = min(deadline, time.monotonic() + 5)

        def remaining():
            seconds = limit - time.monotonic()
            if seconds <= 0:
                raise TimeoutError("QMP agotó su plazo")
            sock.settimeout(seconds)

        remaining()
        sock.connect(str(sockpath))
        with sock.makefile("rb") as stream:
            def receive():
                remaining()
                line = stream.readline()
                if not line:
                    raise EOFError("QMP cerrado")
                return json.loads(line)

            if "QMP" not in receive():
                raise ValueError("Saludo QMP inválido")

            def command(name, arguments=None):
                request = {"execute": name, "id": name}
                if arguments is not None:
                    request["arguments"] = arguments
                remaining()
                sock.sendall(json.dumps(request).encode() + b"\n")
                while True:
                    reply = receive()
                    if reply.get("id") != name:
                        continue  # Eventos asíncronos.
                    if "error" in reply:
                        raise ValueError(str(reply["error"]))
                    return reply["return"]

            command("qmp_capabilities")
            status = command("query-status")
            command("screendump", {"filename": str(filename)})
            return status["running"]


def pixels_ok(path):
    # QEMU genera PPM P6 de 8 bits; no saltar bytes del raster.
    raw = path.read_bytes()
    header = re.match(
        rb"P6\s+(?:#[^\n]*\n\s*)*(\d+)\s+(\d+)\s+255(?:\r\n|\n| |\t)",
        raw,
    )
    if header is None:
        raise ValueError("PPM no reconocido")
    width, height = map(int, header.groups())
    data = memoryview(raw)[header.end():]
    count = width * height
    if count == 0 or len(data) != count * 3:
        raise ValueError("PPM truncado")

    # Muestreo reproducible; agrupar colores evita aceptar ruido mínimo.
    step = max(1, count // 65536)
    colors = collections.Counter()
    dark = total = 0
    for index in range(0, count, step):
        red, green, blue = data[index * 3:index * 3 + 3]
        dark += max(red, green, blue) <= 16
        colors[(red // 16, green // 16, blue // 16)] += 1
        total += 1
    black = dark / total
    dominant = max(colors.values()) / total
    print(f"{path.name}: negro={black:.4f}, dominante={dominant:.4f}",
          flush=True)
    return black < black_max and dominant < dominant_max


def serial_log():
    path = out / "serial.log"
    data = path.read_bytes() if path.exists() else b""
    if re.search(rb"kernel\s+panic", data, re.IGNORECASE):
        raise RuntimeError("Kernel panic en la consola serie")
    return data


def run():
    # Socket corto: AF_UNIX limita la longitud de la ruta.
    with tempfile.TemporaryDirectory(prefix="hyprarch-", dir="/tmp") as work:
        with (out / "qemu.log").open("wb") as log:
            start = time.monotonic()
            deadline = start + 480
            process = subprocess.Popen(
                ["qemu-system-x86_64", *sys.argv[2:]],
                cwd=work, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            )
            try:
                consecutive = 0
                best = 0
                index = 0
                while time.monotonic() < deadline:
                    index += 1
                    shot = out / f"screen-{index:03d}.ppm"
                    tick = time.monotonic()
                    try:
                        running = capture(Path(work) / "qmp.sock", shot, deadline)
                        valid = pixels_ok(shot)
                        # No contar las primeras pantallas del firmware.
                        if running and valid and tick - start >= 120:
                            consecutive += 1
                            best = max(best, consecutive)
                        else:
                            consecutive = 0
                    except (OSError, EOFError, ValueError, KeyError) as error:
                        consecutive = 0
                        print(f"Captura pendiente/fallida: {error}", flush=True)

                    # Capturar antes de fallar para conservar evidencia.
                    serial_log()
                    if process.poll() is not None:
                        raise RuntimeError(f"QEMU terminó: {process.returncode}")
                    time.sleep(max(0, min(tick + 15, deadline) - time.monotonic()))

                data = serial_log()
                if process.poll() is not None:
                    raise RuntimeError("QEMU terminó antes de completar la prueba")
                if not data.strip():
                    raise RuntimeError(
                        "Serie vacía: habilita console=ttyS0,115200n8 en la ISO"
                    )
                if require_brand and b"hyprarch" not in data.lower():
                    raise RuntimeError("Falta 'hyprarch' en la consola serie")
                if ready_marker and ready_marker not in data:
                    raise RuntimeError("Falta el marcador de escritorio")
                # La pantalla puede apagarse por inactividad (DPMS) al final: basta con
                # tres capturas válidas seguidas en cualquier momento tras el arranque.
                if best < 3:
                    raise RuntimeError("No hubo tres capturas válidas seguidas")
                print("PASS: smoke visual y serie; observación de 480 s.", flush=True)
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


try:
    run()
except Exception as error:
    print(f"FAIL: {error}", file=sys.stderr, flush=True)
    sys.exit(1)
PY
