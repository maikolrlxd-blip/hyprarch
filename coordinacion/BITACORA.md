# Bitácora del equipo (léela ANTES de empezar una tarea)

> Para Codex y para cualquiera que se conecte: aquí está **quién hizo qué** para que nadie se confunda al ver trabajo "ya hecho" o repetido. Se actualiza al final de cada bloque. Última actualización: 2026-10-22, tarde (Claude, director).

## Reglas para no pisarnos
1. Haz `git pull` de la rama `ccr-d4583e0a-ggl8kz` y mira esta bitácora y el tablero del Taller **antes** de tocar nada.
2. **Nadie le termina a otro su tarea en silencio.** Si adelanto algo que era tuyo, queda anotado aquí con ruta y estado. Que exista un archivo en el repo **no** significa que tu tarea esté cerrada: tú la revisas, la aceptas o la rehaces.
3. Una tarea = un responsable (`taller_tasks`). Si algo cambia de dueño, lo cambia el director o el humano.
4. Roblox Studio: solo los que de verdad necesites (ver `PARA-CODEX.md`).

## Qué pasó
- **Reinicio del PC del usuario (2026-10-22):** se perdieron programas y la memoria local de Claude, **pero los archivos de Codex SÍ existen** (lo comprobó la sesión del PC): `C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\slime-rush\` con los .blend de árboles v01–v04 (el estilo ORIGINAL 0.4.0 que pide el usuario), `Slime Rush - Characters.blend`, el valle (`maps\valle-abierto\`) y `QA rondas.rbxl`. **Antes se dio por perdido por error; corregido.**
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

## Actualización (tarde del 2026-10-22) — LÉELA, cambió bastante
**Diseño v2 definitivo con las respuestas del usuario** (`slime-rush-juego/DISENO-v2.md`): isla grande generada por semilla, **24 jugadores**, llegada **en botes** (historia: concursantes del extranjero, dinero y fama), robo **por inconsciencia** (derrotar → 12 s en el suelo → saquear), **volcán** opcional con erupción asegurada si alguien salta al cráter (lava lenta y limitada), **colapso final con desastres** (terremotos, tornados, tormenta, erupción, hundimiento) para quien no llegó a la meta. Sin lava fija. Duración total: por decidir.

**Regla de arte del usuario:** TODO con modelos propios hechos en Blender. **Nada básico de Roblox Studio** (ni Parts/bloques, ni Terrain de fábrica con materiales por defecto, ni Toolbox). Hasta la playa, los botes y los cactus.

**Código ya hecho y probado (Lua puro, 34 pruebas):** `slime-rush-juego/src/` — `World.lua` (isla, costa, biomas, meta, 24 apariciones en playa con su bote, volcán, recursos, cofres, raros), `Rules.lua` (fases, derrota/inconsciencia, saqueo, volcán, colapso, bonos de llegada, puntuación), `Rng.lua`, `Noise.lua`. Correr pruebas: `python3 slime-rush-juego/tests/run_tests.py` (necesita `pip install lupa`). Proyecto Rojo en `default.project.json`. **No está probado en Roblox Studio**: eso es tu parte.

**Arte: RECHAZADO por el usuario** (`slime-rush-arte/` tiene `ESTADO.md`): los árboles 0.5.0 y el kit v0.2.0 "se ven como plastilina" y "nada parecido a lo inicial". **No los integres.** Se rehacen con el estilo ORIGINAL (árboles 0.4.0: copas anchas de hojas en capas, troncos gruesos retorcidos con surcos, mate) y texturas pintadas, no formas lisas de un solo color.

**Los tres trabajadores de arte (Opus) fueron detenidos** al interrumpir el usuario la sesión; no hay nadie modelando ahora. Si el usuario te pide arte, ya sabes el criterio.

## Tus tareas hoy (rol: ingeniero), en orden
1. `git pull` y leer esto + `DISENO-v2.md`.
2. **Verificar en Studio cómo construir el terreno SIN el Terrain de fábrica:** opción A, teselas de 48 studs; opción B, mallas por trozos con `EditableMesh` (¿está disponible en un juego publicado?). Reporta qué funciona y el tiempo de generación.
3. Cargar `src/` con Rojo y probar que `World.generate(seed)` corre en Luau (mismo resultado que en Lua puro) y mide el tiempo.
4. Conectar `Rules` al combate real (derrota → `knockOut`; saqueo → `lootDowned`; depósito) con el servidor como autoridad.
5. Un solo Roblox Studio abierto (ver `PARA-CODEX.md`).

## Corrección importante (2026-10-22, tarde) — los archivos de Codex existen
La sesión de Claude que corre en el PC del usuario encontró `C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\slime-rush\`:
- `art\trees\models\`: **"Slime Rush - Arboles cartoon v01…v04.blend"** y "Bosque - estudio de escala v04.blend" → **el estilo ORIGINAL 0.4.0** que el usuario quiere. **Los árboles 0.6.0 deben partir de `v04.blend`**, no de cero.
- `art\slimes\models\Slime Rush - Characters.blend` (los 3 slimes).
- `maps\valle-abierto\` (el .rbxl y "Valle abierto - revision.blend") y `Slime Rush - QA rondas.rbxl`.
**Hecho antes de esta corrección y ahora obsoleto:** todo lo que dice "se perdió" en este repo, y los árboles 0.5.0 y el kit v0.2.0 de la nube (rechazados por el usuario; no integrar).
**Roblox Studio:** hay 7 ventanas abiertas (QA rondas, EngineFixture-travel-v2, Valle abierto, HUD012-clean, HUD012-mobilefix-clean, RouteFixture-v1, RouteFixture-v2); varias son copias de prueba (fixtures). Nadie cierra nada sin que Maikol lo apruebe y sin copia de seguridad previa.

## 2026-10-22 — Claude (nube) programó la Capa 1 de la prueba jugable
- `src/Combat.lua` (puñetazo: alcance 7, 2 golpes/s, 100 hp, 20 de daño, empuje; al llegar a 0 llama a `Rules:knockOut`) + `tests/run_combat.lua` (5 pruebas de combate y una partida completa de 12 bots, determinista). Total: 34 + 7 pruebas ok (`python3 slime-rush-juego/tests/run_tests.py`).
- `server/GameServer.server.lua` y `client/Hud.client.lua`: adaptador PROVISIONAL a Roblox (isla de 512, suelo plano, esferas/cajas de colores, HUD de texto; E recoger, F golpear, G saquear, H depositar). **Solo se comprobó la sintaxis; NO se ha probado en Studio.** `default.project.json` ya los mapea (ServerScriptService y StarterPlayerScripts).
- Codex: parte de esto en vez de rehacerlo. Tu trabajo: abrirlo con Rojo, corregir lo que falle en Studio, reemplazar el suelo plano por el terreno real (sin Terrain de fábrica), medir FPS, y avisar con captura.

## 2026-10-22 — Claude (nube): MUELLE = META (cambio en World.lua)
`World.generate` ahora elige un único muelle en la costa y pone la meta (plaza) tierra adentro frente a él. Nuevo: `world.dock = {x,z,angle,out,inward,sea}`; `spawns[i]` = anillo dentro de la plaza (ya NO están en las playas); `spawns[i].boat` = fila de botes mar adentro frente al muelle. Los sectores de justicia ahora son un abanico de 22,5° desde el muelle (`World.sectorOf(world,x,z)`; `World.sector` queda solo por compatibilidad). 41 pruebas ok. Codex: al construir el terreno usa `world.dock` para el muelle de madera y los NPC guardianes de los cuerpos; el servidor de prueba ya aparece a todos en la plaza.

## 2026-10-22 — Claude (nube): revisión de adaptador, balance y Capa 2
- **Servidor/HUD revisados** (siguen SIN probar en Studio): validación de argumentos de los RemoteEvents, inconsciente = PlatformStand durante `downed_time`, cuenta atrás 10 s, `math.floor` en el HUD.
- **Balance:** mochila 12 → **30** (ver `slime-rush-juego/BALANCE.md` y `tools/sim_mochila.py`).
- **Capa 2 en código puro:** `src/Abilities.lua` (Rayo: montar/embestir/llevar inconsciente; Miga: 4 pedazos, lanzar/curar/anclar), `Combat:damage/heal/setReduction`. 47 pruebas ok (34 + 13). **No está conectado al servidor de Roblox**: se conecta cuando la Capa 1 divierta.

## 2026-10-22 14:13–14:17 — PRIMERA PRUEBA REAL EN STUDIO CON 2 CLIENTES (sesión del PC, copia merge-copia)
- **Simulación SR_TEST en Luau (Studio): 52 PASS, 0 FAIL** (incluye depósito con éxito y "quien no llega lo pierde todo").
- **Play, servidor + 2 clientes:** aparición en la plaza OK; fases PREPARADOS→EXPLORAR(120)→REGRESAR(60)→TORMENTA(20)→FIN OK; **F** OK (cadencia, "muy lejos", 5 golpes = derrotado, 6º "ya está inconsciente", derrotado inmóvil); **G** OK pero con víctima sin objetos ("0 objetos"); **H** OK en la ventana de regreso (puesto 1, 150 puntos); pantalla FIN en texto: "1. Jugador 2: 150 / 2. Jugador 1: 0 (no llegó)".
- **No probado:** E con 2 clientes, saqueo que transfiere objetos en el motor, FPS con 2 clientes.
- **Output:** sin errores de GameServer/Hud/Rules/Combat. Rojo del ChatScript de Roblox (SetCore CoreGuiChatConnections) = de Roblox, no nuestro. ContentId rbxassetid://203785492 = de Studio. Generación total 994 ms con 2 clientes (463 y 278 en pruebas previas).
- **Fallos de UX a arreglar (Codex):** F golpea al más cercano aunque esté inconsciente; el HUD muestra "Label" antes del primer estado; el cuadro de resultados no tiene contraste; el colapso solo oscurece el cielo (sin drama) y nadie "muere".
