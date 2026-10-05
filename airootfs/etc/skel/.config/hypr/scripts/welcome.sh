#!/usr/bin/env bash
sleep 3
notify-send -t 15000 "Bienvenido a hyprarch" "SUPER (tecla Windows) + Q cierra la ventana · +D apps · +Enter terminal · +T colores · +F1 todos los atajos"

# El personajito saluda según la hora (idea tomada del proyecto "Ale")
h=$((10#$(date +%H)))
if   (( h >= 6  && h < 13 )); then saludo="¡Buen día!"
elif (( h >= 13 && h < 20 )); then saludo="¡Buenas tardes!"
else                               saludo="¡Buenas noches!"
fi
sleep 2
claude-presence set done "$saludo Clic en mí para hablar" >/dev/null 2>&1 || true
