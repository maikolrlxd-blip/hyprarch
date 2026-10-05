#!/usr/bin/env bash
# Pone el fondo de pantalla elegido por hyprarch-theme.
img=$(cat "$HOME/.config/hyprarch/wallpaper" 2>/dev/null)
[[ -f $img ]] || img=/usr/share/backgrounds/hyprarch-verde.png
pkill -x swaybg 2>/dev/null
exec swaybg -i "$img" -m fill
