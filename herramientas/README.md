# Herramientas

## `instalar-skills.ps1` / `instalar-skills.sh`
Reinstalan las 30 skills de Claude de Maikol (Agent Skills ×4, Emil Kowalski ×5, taste-skill, impeccable, Remotion ×12, HyperFrames ×7) con commits fijados y revisados el 2026-10-22.
- Windows: `powershell -ExecutionPolicy Bypass -File instalar-skills.ps1`
- Linux/Mac: `./instalar-skills.sh`

No ejecutan nada de lo descargado. `impeccable` se instala sin su carpeta `scripts/` (descarga y ejecuta un binario). `media-use` (HyperFrames) envía estadísticas de uso a PostHog: apágalo con `DO_NOT_TRACK=1`.
Probado: la versión `.sh` (30 skills instaladas). La versión `.ps1` **no se ha probado en Windows**.

Nota: HyperFrames cambió de estructura desde octubre: hoy el repo oficial trae 7 skills (no las 21 que se instalaron antes).
