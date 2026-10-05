#!/usr/bin/env bash
# Menú de energía (SUPER + ESC): estilo menú principal de videojuego (motor: hyprarch-pick).
# Formato: id <TAB> opción <TAB> ícono <TAB> qué hace (se muestra abajo a la derecha al apuntar la opción).
choice=$(printf '%s\n' \
  $'continue\tContinuar\t\tCierra este menú y sigues trabajando donde estabas.' \
  $'lock\tBloquear\t\tBloquea la pantalla. Tus programas siguen abiertos; para volver se pide la contraseña.' \
  $'suspend\tSuspender\t\tPone el equipo en reposo y ahorra energía. Al volver, todo está como lo dejaste.' \
  $'reboot\tReiniciar\t\tCierra todo y vuelve a encender el equipo. Guardá tu trabajo antes.' \
  $'poweroff\tApagar\t\tCierra todo y apaga el equipo por completo. Guardá tu trabajo antes.' \
  $'exit\tCerrar sesión\t\tCierra tu sesión y vuelve a la pantalla de inicio. Se cierran tus programas.' |
  hyprarch-pick --layout orbit --title "¿Qué querés hacer?") || exit 0

case "$choice" in
  continue) ;;
  lock)     hyprlock ;;
  suspend)  systemctl suspend ;;
  reboot)   systemctl reboot ;;
  poweroff) systemctl poweroff ;;
  exit)     hyprctl dispatch 'hl.dsp.exit()' ;;
esac
