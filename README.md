# hyprarch

ISO live de Arch Linux con **Hyprland + Waybar**, estética neón (verde ciber / rojo carmesí sobre fondo casi negro), pensada para equipos con gráficos **Intel**. Arranca directo al escritorio, sin instalar nada.

> Hyprland 0.55+ usa **Lua** (`hyprland.lua`); el formato viejo `hyprland.conf` está obsoleto. Esta ISO ya usa el nuevo.

## Atajos (SUPER = tecla Windows)
| Atajo | Acción |
|---|---|
| `SUPER+Enter` | Terminal |
| `Super` (sola) | Menú de inicio |
| `SUPER+Q` / `ALT+F4` | **Cerrar ventana** |
| `SUPER+T` | **Cambiar colores** (menú interactivo) |
| `SUPER+F1` | Lista de todos los atajos |
| `SUPER+N` | Wi-Fi |
| `SUPER+Esc` | Apagar / reiniciar / salir |

La barra también tiene botones para el mouse: lanzador, cerrar ventana, cambiar colores, ayuda y energía.

## Cambiar colores
`SUPER+T` abre un menú (fzf) con:
- **Modo Verde Dominante** · **Modo Rojo Dominante**
- **Acento personalizado (HEX)**: escribís tus propios códigos de acento y alerta
- Alternar verde/rojo · ver colores actuales

También por terminal: `hyprarch-theme verde|rojo|toggle|custom`.

El script genera solo estos archivos (el resto de la configuración los importa):
`~/.config/hypr/colors.lua`, `waybar/colors.css`, `kitty/colors.conf`, `fuzzel/fuzzel.ini`, `mako/config`, `gtk-3.0|4.0/gtk.css`.
Las paletas base están en `airootfs/usr/share/hyprarch/themes/*.env`.

**Regla de colores de la barra:** verde = todo bien, rojo = problema (batería baja, sin red, CPU/RAM/temperatura altas, volumen en mute).

## Animaciones
En `hyprland.lua`, sección "Animaciones": curvas `snap`, `softback`, `bounce` y un resorte (`pop`) para abrir ventanas con rebote ligero; barra y lanzador entran con rebote; espacios de trabajo deslizan con un pequeño pasarse. El borde con degradado giratorio se apaga con `ROTATING_BORDER = false` al inicio del archivo (ahorra batería).

## Compilar con GitHub Actions
1. Subir esta carpeta a un repositorio **público**.
2. Pestaña **Actions** → **Build ISO** (corre sola con cada push).
3. Descargar el artefacto `hyprarch-iso`.

## Compilar en un Arch local
```bash
sudo ./build.sh
```
La ISO queda en `out/`.

## Grabar en la USB
[Rufus](https://rufus.ie) o Ventoy. Se borra todo el contenido de la USB.

## Personalizar
- Paquetes: `packages.extra`
- Idioma, zona horaria, teclado de consola, hostname: variables al inicio de `build.sh`
- Escritorio: `airootfs/etc/skel/.config/`
