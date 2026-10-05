#!/usr/bin/env bash
# Historial del portapapeles (SUPER + SHIFT + V): rueda curva animada con buscador. Motor: hyprarch-pick.
# cliphist devuelve "id<TAB>texto": justo el formato que entiende hyprarch-pick (id, etiqueta).
command -v cliphist >/dev/null 2>&1 || exit 0
sel=$(cliphist list | hyprarch-pick --layout wheel --title "Portapapeles" --placeholder "Buscar en lo que copiaste…") || exit 0
[[ -n $sel ]] || exit 0
printf '%s\n' "$sel" | cliphist decode | wl-copy
