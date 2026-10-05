#!/usr/bin/env bash
# Captura de pantalla: guarda en ~/Pictures/Capturas y copia al portapapeles.
# Uso: screenshot.sh area | full
dir="$HOME/Pictures/Capturas"
mkdir -p "$dir" || exit 1

if [[ $1 == area ]]; then
  geom=$(slurp) || exit 0
fi

file=$(mktemp "$dir/$(date +%F_%H-%M-%S)_XXXXXX.png") || exit 1
if [[ $1 == area ]]; then
  grim -g "$geom" "$file" || { rm -f "$file"; exit 1; }
else
  grim "$file" || { rm -f "$file"; exit 1; }
fi

wl-copy < "$file"
notify-send -i "$file" "Captura guardada" "$file"
