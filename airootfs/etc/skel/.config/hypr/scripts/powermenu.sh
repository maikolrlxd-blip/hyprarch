#!/usr/bin/env bash
choice=$(printf 'Bloquear\nApagar\nReiniciar\nSuspender\nCerrar sesión' | fuzzel --dmenu --prompt "Energía > " --lines 5)
case "$choice" in
  "Bloquear")      hyprlock ;;
  "Apagar")        systemctl poweroff ;;
  "Reiniciar")     systemctl reboot ;;
  "Suspender")     systemctl suspend ;;
  "Cerrar sesión") hyprctl dispatch 'hl.dsp.exit()' ;;
esac
