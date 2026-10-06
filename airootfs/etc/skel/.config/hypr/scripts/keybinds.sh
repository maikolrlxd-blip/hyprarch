#!/usr/bin/env bash
# Hoja de atajos (SUPER + F1): rueda curva animada con buscador. Motor: hyprarch-pick.  SUPER = tecla Windows.
# Formato: id <TAB> descripción <TAB> ícono <TAB> combinación (se ve a la derecha y también se puede buscar).
cat <<'EOF' | hyprarch-pick --layout wheel --title "Atajos" --placeholder "¿Qué querés hacer? (ej. captura, cerrar)" >/dev/null
a	Terminal		SUPER + Enter
b	Menú de inicio (apps y búsqueda)		SUPER (sola)
c	Firefox		SUPER + B
d	Archivos		SUPER + E
e	Preguntar algo rápido a la IA (no se guarda)		SUPER + A
f	Chat flotante con la IA (o clic en Claudito)		SUPER + SHIFT + A
g	Redes Wi-Fi		SUPER + N
h	Colores del sistema		SUPER + T
i	CERRAR ventana		SUPER + Q  /  ALT + F4
j	Pantalla completa		SUPER + F
k	Ventana flotante / en mosaico		SUPER + SHIFT + F
l	Cambiar división		SUPER + J
m	Mover foco		SUPER + flechas
n	Mover ventana		SUPER + SHIFT + flechas
o	Redimensionar		SUPER + CTRL + flechas
p	Ir al espacio de trabajo		SUPER + 1..9
q	Enviar ventana al espacio		SUPER + SHIFT + 1..9
r	Espacio anterior		SUPER + Tab
s	Siguiente ventana		ALT + Tab
t	Historial del portapapeles		SUPER + V
ta	Recorte de pantalla		SUPER + SHIFT + S  (o Impr Pant)
u	Captura de área		Impr
v	Captura de pantalla		SHIFT + Impr
w	Cambiar distribución de teclado		ALT + SHIFT
x	Bloquear pantalla		SUPER + L
y	Menú de energía		SUPER + ESC
z	Modo gamer / cine / estudio / trabajo		SUPER + SHIFT + G / C / U / W
za	Volver al modo normal		SUPER + SHIFT + N
zb	Efecto de pantalla (CRT)		SUPER + S
zc	Recargar configuración		SUPER + SHIFT + R
EOF
