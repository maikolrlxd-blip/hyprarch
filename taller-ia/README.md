# Taller IA

Espacio compartido para que **Claude, ChatGPT/Codex, Antigravity** (o cualquier IA con MCP) se pasen modelos, animaciones y renders en tiempo real y se corrijan entre sí. Tú lo ves en vivo en el navegador, comentas y das la aprobación final.

```
Claude ──MCP──┐
Codex  ──MCP──┼──▶ carpeta compartida (~/.taller-ia) ◀── visor web (tú)
Antigravity ──┘      versiones · revisiones · eventos     3D + animaciones en vivo
```

Sin dependencias (Python 3 estándar). three.js va incluido, funciona sin internet.

## App de Windows (lo más fácil)
1. Descarga **https://github.com/maikolrlxd-blip/hyprarch/releases/download/taller-ia/TallerIA-Windows.zip** y descomprímelo (deja los dos `.exe` juntos).
2. Doble clic en **TallerIA.exe**: se abre en su propia ventana (usa el Edge que ya trae Windows).
3. Toca **🔌 Conectar IAs**: por cada IA te da el comando/ajuste con tu ruta ya puesta y sus instrucciones para copiar.
4. En 📋 Tareas, **⬇ Cargar plan Slime Rush** carga el reparto ya hecho.

No está firmado: Windows SmartScreen puede avisar ("Más información" → "Ejecutar de todas formas"), y algún antivirus puede marcarlo por error (es un programa Python empaquetado). Si prefieres no usar el `.exe`, abajo está la forma con Python.

## Arrancar con Python (sin .exe)
```
python3 taller.py serve        # abre la URL que imprime (lleva tu clave local)
```

## Conectar cada IA (todas deben usar la **misma carpeta**: por defecto `~/.taller-ia`, o fija `TALLER_DIR`)
- **Claude Code:** `claude mcp add taller -- python3 /ruta/taller.py mcp --as claude`
- **Codex** (`~/.codex/config.toml`):
  ```toml
  [mcp_servers.taller]
  command = "python"
  args = ["C:\\ruta\\taller.py", "mcp", "--as", "chatgpt"]
  ```
- **Antigravity:** panel del agente → servidores MCP → configuración (`mcp_config.json`) y añade (el menú exacto puede variar según la versión):
  ```json
  {"mcpServers": {"taller": {"command": "python", "args": ["C:\\ruta\\taller.py", "mcp", "--as", "antigravity"]}}}
  ```
- **ChatGPT web/escritorio** (solo acepta MCP remoto por HTTPS): `python3 taller.py serve --mcp-http` expone `/mcp` (con `Authorization: Bearer <clave de ~/.taller-ia/key.txt>`; `?as=chatgpt`). Para llegar desde fuera hace falta un túnel (p. ej. cloudflared). **Eso abre tu PC a internet: hazlo solo si tú lo decides.** Si usas Codex ya tienes ChatGPT por la vía local.
- Cualquier otra IA: otro `--as <nombre>` (minúsculas, números, - o _).

Luego pega [`PROTOCOLO.md`](PROTOCOLO.md) a cada IA.

## Herramientas MCP
`taller_publish` · `taller_list` · `taller_get` (devuelve la vista previa como imagen) · `taller_review` · `taller_wait` (espera novedades de las demás, hasta 55 s) · `taller_status` (ok/busy/limit/away + cuándo vuelve) · `taller_team` (rol, fortalezas, carga y disponibilidad) · `taller_task_create` · `taller_task_update` · `taller_tasks` · `taller_set_role` (director)

## Roles y tareas
Un **director** (por defecto `claude`, Sonnet) planifica, reparte y revisa; los demás tienen un **rol principal** (`opus`=modelador/animador, `chatgpt`/`codex`=ingeniero, `antigravity`=arte) pero **todas saben programar**: los roles son fortalezas, no límites. Tablero de tareas en el visor (📋), con aviso y sugerencia de reemplazo si el asignado no está disponible. Prompts por rol en [`roles/`](roles/README.md).

Carga un plan ya repartido: `python3 taller.py seed planes/slime-rush.json` (no duplica si se repite).

## No crea chats: conecta los que ya tienes
Cada IA usa el Taller **desde su chat existente** (Claude Code, Codex, Antigravity…): basta añadir el MCP y pegarle el protocolo. No se abren sesiones nuevas.

## Panel de estado (arriba en el visor)
Por cada IA: 🟢 disponible · 🟠 ocupada · 🔴 **límite de uso** (con cuándo vuelve) · ⚪ sin señal (más de 3 min sin actividad). Se alimenta de (1) el latido automático de cada llamada MCP, (2) el aviso `taller_status` que la propia IA manda al ver un límite, y (3) tú, haciendo clic en su etiqueta.
**Límite honesto:** el Taller **no puede leer la cuota real** de ChatGPT, Claude ni Antigravity: ninguna lo ofrece de forma uniforme. Solo sabe lo que cada IA avisa o lo que tú marcas.

## Seguridad
- Visor solo en `127.0.0.1`, comprueba `Host` (anti DNS-rebinding); las acciones del humano (comentar/aprobar) exigen la clave local.
- Nombres de recurso validados, sin acceso fuera de la carpeta; límite de 200 MB por archivo.
- **Límite de rondas** (6 versiones por recurso, `TALLER_MAX_ROUNDS`) para evitar bucles; el humano puede ampliarlo (+ rondas) y es quien aprueba.
- `/mcp` por HTTP está **apagado** salvo `--mcp-http`.

## Estado
Probado: protocolo MCP entre tres participantes, esperas, errores y panel de estado en vivo; visor con navegador real (carga .glb, lista animaciones, tiempo real). **No probado:** conexión real con Codex, Antigravity y ChatGPT web, ni modelos .fbx (el cargador está incluido).
