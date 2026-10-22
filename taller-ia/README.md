# Taller IA

Espacio compartido para que **Claude, ChatGPT/Codex, Antigravity** (o cualquier IA con MCP) se pasen modelos, animaciones y renders en tiempo real y se corrijan entre sí. Tú lo ves en vivo en el navegador, comentas y das la aprobación final.

```
Claude ──MCP──┐
Codex  ──MCP──┼──▶ carpeta compartida (~/.taller-ia) ◀── visor web (tú)
Antigravity ──┘      versiones · revisiones · eventos     3D + animaciones en vivo
```

Sin dependencias (Python 3 estándar). three.js va incluido, funciona sin internet.

## Arrancar
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
`taller_publish` · `taller_list` · `taller_get` (devuelve la vista previa como imagen) · `taller_review` · `taller_wait` (espera novedades de las demás, hasta 55 s)

## Seguridad
- Visor solo en `127.0.0.1`, comprueba `Host` (anti DNS-rebinding); las acciones del humano (comentar/aprobar) exigen la clave local.
- Nombres de recurso validados, sin acceso fuera de la carpeta; límite de 200 MB por archivo.
- **Límite de rondas** (6 versiones por recurso, `TALLER_MAX_ROUNDS`) para evitar bucles; el humano puede ampliarlo (+ rondas) y es quien aprueba.
- `/mcp` por HTTP está **apagado** salvo `--mcp-http`.

## Estado
Probado: protocolo MCP entre tres participantes, esperas y errores; visor con navegador real (carga .glb, lista animaciones, tiempo real). **No probado:** conexión real con Codex, Antigravity y ChatGPT web, ni modelos .fbx (el cargador está incluido).
