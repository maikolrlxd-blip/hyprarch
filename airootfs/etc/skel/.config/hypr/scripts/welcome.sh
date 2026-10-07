#!/usr/bin/env bash
sleep 3
notify-send -t 15000 "Bienvenido a hyprarch" "Tecla SUPER (Windows) sola: menú de inicio · +Enter terminal · +Q cierra la ventana · +A habla con tu IA · +X centro de control · +F1 todos los atajos"

# El personajito saluda según la hora (idea tomada del proyecto "Ale")
h=$((10#$(date +%H)))
if   (( h >= 6  && h < 13 )); then saludo="¡Buen día!"
elif (( h >= 13 && h < 20 )); then saludo="¡Buenas tardes!"
else                               saludo="¡Buenas noches!"
fi
sleep 2
claude-presence set 'done' "$saludo Clic en mí: ¿qué hacemos?" >/dev/null 2>&1 || true
