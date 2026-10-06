#!/usr/bin/env bash
# Compila hyprarch-wbar (C + Wayland + cairo). Uso: tools/wbar/build.sh [carpeta-de-salida]
# Necesita en la máquina que compila (NO en el sistema final): gcc, pkgconf, wayland, wayland-protocols, wlr-protocols, cairo.
# Sale un binario pequeño que solo depende de libwayland-client y libcairo (ya presentes en hyprarch por GTK).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=${1:-$here/out}
mkdir -p "$out"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

lls=/usr/share/wlr-protocols/unstable/wlr-layer-shell-unstable-v1.xml
xdg=/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml
for f in "$lls" "$xdg"; do [[ -r $f ]] || { echo "falta $f" >&2; exit 1; }; done

wayland-scanner client-header  "$lls" "$tmp/wlr-layer-shell-unstable-v1-client-protocol.h"
wayland-scanner private-code   "$lls" "$tmp/lls.c"
wayland-scanner client-header  "$xdg" "$tmp/xdg-shell-client-protocol.h"
wayland-scanner private-code   "$xdg" "$tmp/xdg.c"

gcc -O2 -s -Wall -Wextra -I"$tmp" -o "$out/hyprarch-wbar" "$here/wbar.c" "$tmp/lls.c" "$tmp/xdg.c" \
    $(pkg-config --cflags --libs wayland-client cairo)
echo "compilado: $out/hyprarch-wbar ($(stat -c %s "$out/hyprarch-wbar") bytes)"
