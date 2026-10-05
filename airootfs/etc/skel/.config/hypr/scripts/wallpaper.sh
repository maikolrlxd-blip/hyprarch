#!/usr/bin/env bash
# Pone el fondo de pantalla elegido por hyprarch-theme.
# Reintenta unos segundos: al arrancar la sesión, Wayland puede no estar listo todavía.
img=$(cat "$HOME/.config/hyprarch/wallpaper" 2>/dev/null)
[[ -f $img ]] || img=/usr/share/backgrounds/hyprarch-verde.jpg

pkill -x swaybg 2>/dev/null

for _ in $(seq 1 15); do
  swaybg -i "$img" -m fill &
  pid=$!
  sleep 1.5
  if kill -0 "$pid" 2>/dev/null; then
    wait "$pid"
    exit 0
  fi
done
