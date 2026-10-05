#!/usr/bin/env bash
choice=$(printf 'Apagar\nReiniciar\nSuspender\nCerrar sesión' | fuzzel --dmenu --prompt "Energía > " --lines 4)
case "$choice" in
  "Apagar")        systemctl poweroff ;;
  "Reiniciar")     systemctl reboot ;;
  "Suspender")     systemctl suspend ;;
  "Cerrar sesión") hyprctl dispatch exit ;;
esac
