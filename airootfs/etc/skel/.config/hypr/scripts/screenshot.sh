#!/usr/bin/env bash
# Captura de pantalla: guarda en ~/Pictures/Capturas y copia al portapapeles.
# Uso: screenshot.sh area | full
dir="$HOME/Pictures/Capturas"
mkdir -p "$dir"
file="$dir/$(date +%F_%H-%M-%S).png"

if [[ $1 == area ]]; then
  geom=$(slurp) || exit 0
  grim -g "$geom" "$file"
else
  grim "$file"
fi

wl-copy < "$file"
notify-send -i "$file" "Captura guardada" "$file"
