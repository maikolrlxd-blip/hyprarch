# Roles del Taller IA
Pega el archivo del rol en el chat de cada IA, junto con `../PROTOCOLO.md`.

| Archivo | Rol | Recomendado | Nombre `--as` |
|---|---|---|---|
| `director.md` | Planifica, reparte y revisa | Claude Sonnet | `claude` |
| `modelador.md` | 3D difícil, rigs, animaciones | Claude Opus | `opus` |
| `ingeniero.md` | Código, Studio/Blender, pruebas | Codex / ChatGPT | `chatgpt` |
| `artista.md` | Crítica visual, estilo, referencias | Antigravity | `antigravity` |

**Los roles son fortalezas, no límites:** todas las IAs saben programar, revisar código, investigar y escribir. El director reparte por **afinidad y por carga** (`taller_team` muestra tareas abiertas), y si alguien llega a su límite de uso, lo cubre cualquiera disponible que sepa lo que pide la tarea (`needs`).

El rol por defecto sale del nombre; se cambia con `--role director|modelador|animador|ingeniero|artista` o con un clic en el panel del visor.
