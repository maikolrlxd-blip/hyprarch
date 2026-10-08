# hyprarch — guía para IAs (Claude, Codex, Gemini, Ollama… cualquiera)

Estás dentro de **hyprarch**: un Arch Linux con Hyprland pensado como casa para IAs que hacen cosas por la persona,
pero también cómodo para jugar y para el día a día. Habla en el idioma de la persona (por defecto español).

## Cómo controlar el sistema (usa esto primero)
`hyprarch-api` da acciones **acotadas y seguras** con respuesta en JSON. Empieza con `hyprarch-api help`.

| Quiero… | Comando |
|---|---|
| ver ventanas / espacios / la activa | `hyprarch-api windows` · `workspaces` · `active` |
| enfocar o cerrar una ventana | `hyprarch-api focus <clase>` · `close <clase>` (o la dirección `0x…`) |
| abrir una aplicación instalada | `hyprarch-api apps` y luego `hyprarch-api open "Firefox"` |
| cambiar de modo (gamer, cine, estudio, trabajo, normal) | `hyprarch-api mode set gamer` |
| cambiar de tema de colores | `hyprarch-api theme set fresco` |
| volumen / brillo | `hyprarch-api volume set 40` · `brightness set 60` |
| red Wi‑Fi | `hyprarch-api wifi list` · `wifi connect "SSID" "clave"` |
| estado del equipo | `hyprarch-api system` |
| ver la pantalla | `hyprarch-api screenshot /tmp/pantalla.png` y luego leer la imagen |
| avisar a la persona | `hyprarch-api notify "Título" "Texto"` · `hyprarch-api osd "Listo"` |

Por SSH funciona igual (el comando entra solo a la sesión gráfica). Si necesitas algo más, hay `hyprarch-ctl <comando>`
(ejecuta un comando dentro de la sesión de Hyprland).

## Dónde vive cada cosa
- Modos y sus apps: `~/.config/hyprarch/modes/<modo>.conf` (una app por línea: `espacio|comando`; `0` = donde esté).
  Cámbialos con `hyprarch-mode add <modo> <comando> [espacio]` / `remove`. Los comandos no admiten `; & | $ \` < > ( ) { }`.
- Preferencias: `~/.config/hyprarch/` (`style`, `mascot`, `buddy.conf`, `intro`, `lang`, `perf`…). Tema: `hyprarch-theme`.
- Configuración de Hyprland: `~/.config/hypr/hyprland.lua` (Lua, Hyprland 0.56). Barra: `~/.config/waybar/`.
- Navegador: `hyprarch-browser pick|open [URL]|apply|status` (se elige en el primer inicio; guardado en `~/.config/hyprarch/browser`; Super+B lo abre). Firefox viene incluido; Chromium, Brave, Chrome, Edge, Opera, Opera GX, Vivaldi, LibreWolf, Zen y Falkon se instalan al elegirlos.
- Instalar programas por packs: `hyprarch-apps juegos|oficina|multimedia|tienda|comunicacion` (necesita internet).
- Menús del sistema: `hyprarch-pick` (selector animado; **no uses fuzzel, fzf ni menús de terminal básicos**).

## Reglas (para cuidar a la persona y su equipo)
1. **Pregunta antes de lo irreversible:** borrar archivos, formatear, cambiar contraseñas, tocar `/boot` o discos, enviar algo fuera del equipo.
2. **No abras el equipo hacia internet** (túneles, servidores públicos, compartir pantalla) sin que la persona lo pida y lo apruebe.
3. **No guardes ni muestres contraseñas, claves o tokens** en notas, registros o mensajes.
4. Prefiere `hyprarch-api` a comandos sueltos; si usas la terminal, que sea con permisos mínimos y explicando qué haces.
5. Si algo falla, dilo con claridad y propón el siguiente paso; no inventes que funcionó.
6. Anota lo que aprendas en la base de conocimiento de la persona si te lo ha pedido (notas en Markdown).

## Sobre la persona y el sistema
- El asistente visual es **Hyro** (robot en el escritorio); puedes cambiarle el nombre en `~/.config/hyprarch/buddy.conf`.
- Está pensado para equipos modestos: `hyprarch-perf status` dice si usa el perfil ligero.
- Atajos útiles: tecla Super (sola) menú de inicio · SUPER+I instalar apps · SUPER+N Wi‑Fi · SUPER+T colores · SUPER+A hablar con la IA · SUPER+F1 todos los atajos.
