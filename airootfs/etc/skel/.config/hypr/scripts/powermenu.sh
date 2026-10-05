#!/usr/bin/env bash
# Menú de energía (SUPER + ESC): órbita animada alrededor del personajito. Motor: hyprarch-pick.
choice=$(printf '%s\n' \
  $'lock\tBloquear\t' \
  $'suspend\tSuspender\t' \
  $'reboot\tReiniciar\t' \
  $'poweroff\tApagar\t' \
  $'exit\tCerrar sesión\t' |
  hyprarch-pick --layout orbit --title "¿Qué querés hacer?") || exit 0

case "$choice" in
  lock)     hyprlock ;;
  suspend)  systemctl suspend ;;
  reboot)   systemctl reboot ;;
  poweroff) systemctl poweroff ;;
  exit)     hyprctl dispatch 'hl.dsp.exit()' ;;
esac
