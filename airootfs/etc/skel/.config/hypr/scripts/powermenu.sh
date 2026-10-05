#!/usr/bin/env bash
# Menú de energía (SUPER + ESC): estilo menú principal de videojuego (motor: hyprarch-pick). Traducido (hyprarch-i18n).
# Formato: id <TAB> opción <TAB> ícono <TAB> qué hace (se muestra abajo a la derecha al apuntar la opción).
T() { hyprarch-i18n "$1" "${2:-$1}"; }
choice=$(printf '%s\n' \
  "continue"$'\t'"$(T power.continue)"$'\t\t'"$(T power.continue.d)" \
  "lock"$'\t'"$(T power.lock)"$'\t\t'"$(T power.lock.d)" \
  "suspend"$'\t'"$(T power.suspend)"$'\t\t'"$(T power.suspend.d)" \
  "reboot"$'\t'"$(T power.reboot)"$'\t\t'"$(T power.reboot.d)" \
  "poweroff"$'\t'"$(T power.poweroff)"$'\t\t'"$(T power.poweroff.d)" \
  "exit"$'\t'"$(T power.exit)"$'\t\t'"$(T power.exit.d)" |
  hyprarch-pick --layout orbit --title "$(T power.title)") || exit 0

case "$choice" in
  continue) ;;
  lock)     hyprlock ;;
  suspend)  systemctl suspend ;;
  reboot)   systemctl reboot ;;
  poweroff) systemctl poweroff ;;
  exit)     hyprctl dispatch 'hl.dsp.exit()' ;;
esac
