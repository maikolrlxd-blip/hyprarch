#!/usr/bin/env bash
# Cambia volumen/brillo y muestra el aviso animado de hyprarch (hyprarch-osd); si no está, una notificación con barra.
# Uso: osd.sh vol-up | vol-down | mute | bright-up | bright-down

show() { # show <vol|bright> <porcentaje|mute> <texto>
  if command -v hyprarch-osd >/dev/null 2>&1; then
    hyprarch-osd "$1" "$2" &
  else
    notify-send -t 1500 -h string:x-canonical-private-synchronous:osd -h "int:value:${2/mute/0}" "$1" "$3"
  fi
}

case "$1" in
  vol-up|vol-down|mute)
    case "$1" in
      vol-up)   wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+ || exit 1 ;;
      vol-down) wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%- || exit 1 ;;
      mute)     wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle || exit 1 ;;
    esac
    out=$(wpctl get-volume @DEFAULT_AUDIO_SINK@) || exit 1
    pct=$(LC_ALL=C awk '{printf "%d", $2 * 100}' <<<"$out")
    if grep -q MUTED <<<"$out"; then
      show vol mute "Silenciado"
    else
      show vol "$pct" "$pct%"
    fi
    ;;
  bright-up|bright-down)
    if [[ $1 == bright-up ]]; then brightnessctl -q set 5%+ || exit 1; else brightnessctl -q set 5%- || exit 1; fi
    out=$(brightnessctl -m) || exit 1
    pct=$(cut -d, -f4 <<<"$out" | tr -d %)
    show bright "$pct" "$pct%"
    ;;
esac
