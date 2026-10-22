# Bitácora del equipo (léela ANTES de empezar una tarea)

> Para Codex y para cualquiera que se conecte: aquí está **quién hizo qué** para que nadie se confunda al ver trabajo "ya hecho" o repetido. Se actualiza al final de cada bloque. Última actualización: 2026-10-22 (Claude, director).

## Reglas para no pisarnos
1. Haz `git pull` de la rama `ccr-d4583e0a-ggl8kz` y mira esta bitácora y el tablero del Taller **antes** de tocar nada.
2. **Nadie le termina a otro su tarea en silencio.** Si adelanto algo que era tuyo, queda anotado aquí con ruta y estado. Que exista un archivo en el repo **no** significa que tu tarea esté cerrada: tú la revisas, la aceptas o la rehaces.
3. Una tarea = un responsable (`taller_tasks`). Si algo cambia de dueño, lo cambia el director o el humano.
4. Roblox Studio: solo los que de verdad necesites (ver `PARA-CODEX.md`).

## Qué pasó
- **Reinicio del PC del usuario (2026-10-22):** se perdieron los archivos originales del juego (.rbxl de arena y valle, .blend de personajes y árboles, Laboratorio Slime) y la memoria local. **Nada de lo que Codex tenía en su carpeta `...\Codex\...\slime-rush` existe ya**, salvo copias que el usuario recupere.
- **Giro de diseño (hoy):** el usuario cambió de idea. Slime Rush v2 = **mundo grande generado por semilla** (exploración, recursos, cofres ocultos, slimes y accesorios raros, robo, carrera a la meta). El mapa fijo y la lava del diseño anterior **quedan en pausa**. Detalle y decisiones abiertas: `slime-rush-juego/DISENO-v2.md`.
- **Todos los modelos se hacen con Blender** (regla del usuario).

## Quién hizo qué (desde el reinicio)
| Qué | Quién | Dónde | Estado |
|---|---|---|---|
| Taller IA (app de Windows, tablero, roles, estado de límites) | Claude (director) | `taller-ia/`, release `taller-ia` | Hecho; sin probar en el Windows del usuario |
| Instaladores de skills y programas | Claude | `herramientas/` | `.sh` probado; `.ps1` sin probar |
| Diseño v2 y reparto de tareas | Claude | `slime-rush-juego/DISENO-v2.md`, `taller-ia/planes/slime-rush-v2.json` | Propuesta, **pendiente de aprobación** |
| Árboles 0.5.0 | Opus (Blender) | `slime-rush-arte/arboles-v05/` | En curso |
| Kit modular + biomas + prototipo de generación | Opus (Blender) | `slime-rush-arte/mapa-v02/` | En curso |
| Generador de mundo y reglas de partida (módulos puros + pruebas) | Claude | `slime-rush-juego/` | Por empezar |

## Lo que NO he tocado (sigue siendo tuyo, Codex)
Integración en Roblox Studio, robo/depósito, cofres, terreno por voxels, correcciones de forma de Rayo y Miga, y pruebas con 2+ clientes. **No he hecho ninguna de esas tareas.** Si ves modelos de árboles o del kit en el repo, son **material de arte de Opus** que tú integras, no tu trabajo terminado por otro.

## Cómo avisarnos
Escribe en `coordinacion/DE-CODEX.md` (o por el Taller: `taller_task_update` con nota). El director lo lee al empezar cada turno.
