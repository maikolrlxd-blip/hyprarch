#!/usr/bin/env bash
# Menú de energía (SUPER + ESC): estilo menú principal de videojuego (motor: hyprarch-pick).
# Formato: id <TAB> opción <TAB> ícono <TAB> descripción corta (se ve bajo la opción elegida).
choice=$(printf '%s\n' \
  $'continue\tContinuar\t\tvolver al escritorio' \
  $'lock\tBloquear\t\tla sesión queda protegida' \
  $'suspend\tSuspender\t\tpausa rápida, ahorra energía' \
  $'reboot\tReiniciar\t\tapagar y volver a encender' \
  $'poweroff\tApagar\t\thasta la próxima' \
  $'exit\tCerrar sesión\t\tvolver a la pantalla de inicio' |
  hyprarch-pick --layout orbit --title "¿Qué querés hacer?") || exit 0

case "$choice" in
  continue) ;;
  lock)     hyprlock ;;
  suspend)  systemctl suspend ;;
  reboot)   systemctl reboot ;;
  poweroff) systemctl poweroff ;;
  exit)     hyprctl dispatch 'hl.dsp.exit()' ;;
esac
