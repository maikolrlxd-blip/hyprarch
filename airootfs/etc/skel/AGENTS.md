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
### MCP para Claude Code, Codex y Gemini

El servidor stdio `hyprarch-mcp` usa solo Python estándar, valida los argumentos,
invoca `hyprarch-api` sin shell y no registra argumentos ni resultados. No inicia
servidores de red. Regístralo desde una terminal como el usuario de la sesión:

```sh
claude mcp add --transport stdio --scope user hyprarch -- /usr/local/bin/hyprarch-mcp
codex mcp add hyprarch -- /usr/local/bin/hyprarch-mcp
gemini mcp add --scope user hyprarch /usr/local/bin/hyprarch-mcp
```

Comprueba con `claude mcp list`, `codex mcp list` o `gemini mcp list`. Para ofrecer
solo consultas, registra en su lugar `/usr/bin/env HYPRARCH_MCP_READONLY=1
/usr/local/bin/hyprarch-mcp` como comando y argumentos. El servidor completo
incluye acciones de escritorio: conserva la confirmación del cliente para ellas
(no uses `--trust` en Gemini). No proporciona un sistema de tarjetas por sí mismo.

La isla carga exclusivamente `/usr/share/hyprarch/island-mcp.json`, en modo de
solo lectura, y no hereda estos registros personales. Para acciones usa
`/usr/local/bin/hyprarch-api`; para comandos libres o archivos externos espera
la tarjeta. Una captura devuelve la ruta creada por la API: el MCP no acepta un
destino de escritura arbitrario. Usa esa ruta devuelta, no una ruta supuesta.

Referencias: [Claude MCP](https://code.claude.com/docs/en/mcp),
[Codex MCP](https://developers.openai.com/codex/mcp/) y
[Gemini CLI](https://geminicli.com/docs/cli/cli-reference/) (2026-10-12).

- Modos y sus apps: `~/.config/hyprarch/modes/<modo>.conf` (una app por línea: `espacio|comando`; `0` = donde esté).
  Cámbialos con `hyprarch-mode add <modo> <comando> [espacio]` / `remove`. Los comandos no admiten `; & | $ \` < > ( ) { }`.
- Preferencias: `~/.config/hyprarch/` (`style`, `mascot`, `buddy.conf`, `intro`, `lang`, `perf`…). Tema: `hyprarch-theme`.
- Configuración de Hyprland: `~/.config/hypr/hyprland.lua` (Lua, Hyprland 0.56). Barra: `~/.config/waybar/`.
- Navegador: `hyprarch-browser pick|open [URL]|apply|status` (se elige en el primer inicio; guardado en `~/.config/hyprarch/browser`; Super+B lo abre). Firefox viene incluido; Chromium, Brave, Chrome, Edge, Opera, Opera GX, Vivaldi, LibreWolf, Zen y Falkon se instalan al elegirlos.
- Instalar programas por packs: `hyprarch-apps juegos|oficina|multimedia|tienda|comunicacion` (necesita internet).
- Menús del sistema: `hyprarch-pick` (selector animado; **no uses fuzzel, fzf ni menús de terminal básicos**).

## Reglas (para cuidar a la persona y su equipo)
La isla inicia Claude en `~/.local/share/hyprarch/island-work`, con fuentes de
configuración vacías, `dontAsk`, herramientas restringidas y un hook propio.
No preautoriza la lectura de HOME. Trabaja con archivos que la persona haya
copiado deliberadamente a ese directorio. Para leer otra carpeta, solicita cada
archivo mediante `Read` con su ruta absoluta: la isla muestra una tarjeta con la
ruta y solo «Permitir» habilita esa llamada exacta en la siguiente consulta.
Nunca pidas claves privadas, `.env` ni tokens. Los enlaces fuera de island-work
también necesitan tarjeta. Un comando Bash autorizado puede acceder al sistema
con los permisos del usuario: esta política de herramientas no es un sandbox
de Linux. Explica siempre el alcance del comando en la tarjeta.

Flags y hook contrastados con la [CLI de Claude](https://code.claude.com/docs/en/cli-reference),
[permisos](https://code.claude.com/docs/en/permissions) y
[hooks](https://code.claude.com/docs/en/hooks), el 2026-10-12. Si la versión
instalada rechaza alguno, actualízala; no retires las restricciones para continuar.
Se exige Claude Code **2.1.295 o posterior** por `onFailure: block`: si el hook
falla o vence su plazo, la llamada se bloquea. Versiones anteriores no arrancan
desde la isla.
Se desactiva también la carga automática de CLAUDE.md, memoria y adjuntos `@`
con las [variables documentadas](https://code.claude.com/docs/en/env-vars).
Para aportar contexto solicita `Read` y espera la tarjeta cuando sea externo.

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
