# hyprarch

ISO live de Arch Linux con **Hyprland + Waybar**, tema Catppuccin Mocha minimalista, pensada para equipos con gráficos **Intel**. Arranca directo al escritorio, sin instalar nada.

## Qué incluye
- Barra con espacios de trabajo, ventana activa, reloj con calendario, distribución de teclado, CPU, RAM, temperatura, red, Bluetooth, volumen, brillo, batería y menú de energía.
- Lanzador (fuzzel), notificaciones con barra de volumen/brillo, historial del portapapeles, capturas de pantalla.
- Firefox, Thunar, kitty, mpv, imv, zathura, neovim y herramientas de terminal (starship, eza, bat, fzf, btop, fastfetch).
- Teclado `latam` / `es` / `us` (ALT+SHIFT para cambiar), idioma es_AR, zona horaria Buenos Aires.
- Usuario `live`, sin contraseña y con sudo sin contraseña (es un sistema live).

## Atajos principales
`SUPER+F1` muestra todos. Los básicos: `SUPER+Enter` terminal, `SUPER+D` apps, `SUPER+Q` cerrar, `SUPER+N` Wi-Fi.

## Compilar con GitHub Actions
1. Crear un repositorio **público** en GitHub (los artefactos grandes no caben en la cuota gratuita de repos privados) y subir esta carpeta.
2. Pestaña **Actions** → **Build ISO** → **Run workflow**.
3. Al terminar (~15-25 min), descargar el artefacto `hyprarch-iso` y descomprimirlo.

## Compilar en un Arch local
```bash
sudo ./build.sh
```
La ISO queda en `out/`.

## Grabar en la USB
Usar [Rufus](https://rufus.ie) (modo **DD** si lo pide) o Ventoy. Se borra todo el contenido de la USB.

## Personalizar
- Paquetes: `packages.extra`
- Idioma, zona horaria, teclado de consola, hostname: variables al inicio de `build.sh`
- Configuración del escritorio: `airootfs/etc/skel/.config/`
