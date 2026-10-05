#!/usr/bin/env bash
# Hoja de atajos (SUPER + F1)
cat <<'EOF' | fuzzel --dmenu --prompt "Atajos > " --lines 20 --width 56 >/dev/null
SUPER + Enter           Terminal
SUPER + D               Lanzador de aplicaciones
SUPER + B               Firefox
SUPER + E               Archivos
SUPER + N               Redes Wi-Fi (nmtui)
SUPER + Q               Cerrar ventana
SUPER + F               Pantalla completa
SUPER + V               Ventana flotante
SUPER + J               Cambiar división
SUPER + flechas         Mover foco
SUPER + SHIFT + flechas Mover ventana
SUPER + CTRL + flechas  Redimensionar
SUPER + 1..9            Ir al espacio de trabajo
SUPER + SHIFT + 1..9    Enviar ventana al espacio
SUPER + Tab             Espacio anterior
ALT + Tab               Siguiente ventana
SUPER + SHIFT + V       Historial del portapapeles
Impr / SHIFT + Impr     Captura (área / pantalla)
ALT + SHIFT             Cambiar distribución de teclado
SUPER + ESC             Menú de energía
SUPER + SHIFT + R       Recargar configuración
EOF
