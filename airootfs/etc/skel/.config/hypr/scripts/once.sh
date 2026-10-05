#!/usr/bin/env bash
# Abre un programa de terminal UNA sola vez: si ya está abierto, solo le da el foco.
# Uso: once.sh <clase> <comando> [args...]
class=$1; shift

if hyprctl clients -j | jq -e --arg c "$class" 'any(.[]; .class == $c)' >/dev/null 2>&1; then
  hyprctl dispatch "hl.dsp.focus({ window = \"class:$class\" })" >/dev/null
else
  exec kitty --class "$class" -e "$@"
fi
