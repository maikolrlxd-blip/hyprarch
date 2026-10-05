#!/usr/bin/env bash
# Cambia volumen/brillo y muestra una notificación con barra de progreso.
# Uso: osd.sh vol-up | vol-down | mute | bright-up | bright-down

notify() { # notify <titulo> <porcentaje> <texto>
  notify-send -t 1500 -h string:x-canonical-private-synchronous:osd \
    -h "int:value:$2" "$1" "$3"
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
      notify "Volumen" 0 "Silenciado"
    else
      notify "Volumen" "$pct" "$pct%"
    fi
    ;;
  bright-up|bright-down)
    if [[ $1 == bright-up ]]; then brightnessctl -q set 5%+ || exit 1; else brightnessctl -q set 5%- || exit 1; fi
    out=$(brightnessctl -m) || exit 1
    pct=$(cut -d, -f4 <<<"$out" | tr -d %)
    notify "Brillo" "$pct" "$pct%"
    ;;
esac
