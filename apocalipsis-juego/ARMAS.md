# Armas del roguelike zombi — estadísticas provisionales (a ajustar jugando)
Código: `src/Weapons.lua` (puro, sin Roblox) + `tests/` (9 pruebas ok: `python3 apocalipsis-juego/tests/run_tests.py`). Sonidos: `../apocalipsis-sonidos/`.

| | Pistola 9mm | Escopeta | Subfusil |
|---|---|---|---|
| Modo | semiautomática | semiautomática (bombeo) | automática |
| Daño por bala / perdigón | 25 | 8 × 12 | 14 |
| Cabeza | ×2,0 | ×1,5 | ×1,8 |
| Cadencia (tiros/s) | 4,5 | 1,1 (bombeo 0,45 s) | 12 |
| Cargador / reserva | 15 / 90 | 6 / 36 | 30 / 150 |
| Recarga | 1,7 s | 0,5 inicio + 0,55 s por cartucho + 0,4 fin (interrumpible disparando) | 1,95 s |
| Equipar | 0,8 s | 1,0 s | 0,9 s |
| Alcance / daño pleno hasta | 140 / 60 studs (cae a 60 %) | 60 / 12 studs (cae a 15 %) | 110 / 45 studs (cae a 50 %) |
| Dispersión (quieto / moviéndose) | 0,8° / 1,5° | 5,5° / 7,0° | 1,6° / 3,0° (+0,12° por bala en ráfaga) |
| **Inspeccionar** | Maikol: la gira en diagonal a la derecha, luego a la izquierda, estira la mano y la pone de lado en posición de disparo (estilo gángster) y vuelve al reposo **3,30 s** | gira, medio bombeo para mirar la recámara, gira al otro lado y vuelve: **3,00 s** | gira, saca el cargador a medias y lo mete, gira y vuelve: **3,00 s** |

Tiempo para matar a un zombi de 100 de vida (todos los disparos aciertan): pistola 4 disparos / 0,67 s; escopeta cerca 2 / 0,91 s; subfusil 8 / 0,58 s. A la cabeza: pistola 2 / 0,22 s, escopeta 1, subfusil 4 / 0,25 s. (No cuenta fallos, recargas ni dispersión: es el mejor caso.)

Las duraciones de equipar/recargar/disparo deben coincidir con los clips exportados de Blender (el Coordinador entrega los tiempos reales; si cambian, se ajustan aquí). Nombres de clip usados: Equipar, Disparo, Bombear, Recargar, Recargar_Inicio, Recargar_Cartucho, Recargar_Fin, Reposo, Inspeccionar.
Pendiente de decidir con Maikol: moneda/precio de cada arma, munición comprable en la tienda del mapa, mejoras, y cómo funciona la inspección de cada una.

## Impactos en enemigos (Luto)
`src/Impactos.lua` (puro, 5 pruebas ok): zona (cabeza/torso/brazo/pierna) → daño, reacción ("Golpeado", probabilidad de tambalearse, empuje), efecto de partículas, sonido (`impacto_zombi`, `marcador_impacto`) y mancha que se desvanece (tope de 60). Sangre ESTILIZADA con opción de apagarla (chispas neutras). `client/ImpactoFX.lua` dibuja los efectos en Roblox: **SIN PROBAR EN STUDIO**. Faltan: el zombi con su animación "Golpeado", subir los audios a Roblox, el disparo real con raycast y la zona de impacto (cabeza/torso...), todo ello por conectar.

## Disparo real y agujeros de bala (Luto) — SIN PROBAR EN STUDIO
Proyecto Rojo propio: `apocalipsis-juego/default.project.json` (ReplicatedStorage.Luto = src, ServerScriptService.LutoServidor = server, StarterPlayerScripts.LutoCliente = client).
- `src/Disparo.lua` (puro, 5 pruebas ok): dirección de cada bala con dispersión, zona del cuerpo por nombre de pieza (R15 y R6) y especificación de los **agujeros de bala** (hueco oscuro con borde astillado; en el enemigo, marca roja que dura menos).
- `server/Armas.server.lua`: el servidor es la autoridad: equipar, disparar (rayo desde la cabeza con la dirección del cliente + dispersión), recargar, inspeccionar, daño por zona y aviso a los clientes.
- `client/Armas.client.lua`: clic = disparar (mantener = automática), R recargar, F inspeccionar, 1/2/3 cambiar de arma; HUD de munición y mira.
- `client/ImpactoFX.lua`: partículas, mancha de sangre estilizada y **agujero de bala** que se pega a la pieza golpeada y desaparece (mapa: 40 s, tope 150; enemigo: 8 s, tope 40).
- `server/Maniquies.server.lua`: 4 maniquíes de bloques (piezas con nombres R15, 100 de vida, etiqueta "Zombi") para probar sin el zombi.
Falta: sonidos (subirlos a Roblox), animaciones "Golpeado" y de las armas en el personaje, el zombi real y la prueba en Studio.

## Partida jugable mínima de Luto (provisional, SIN PROBAR EN STUDIO)
Para probar todo junto: abrir `apocalipsis-juego/default.project.json` con Rojo en un place vacío y pulsar Play (1 a 4 clientes).
- **Qué pasa:** 8 s de espera → ronda 1; los zombis (rigs R15 verdes, sin animación de caminar) salen del borde de una arena de 420×420 y te persiguen; matar da monedas; entre rondas hay 10 s; la tienda (2 bloques junto al centro: munición y curación, ProximityPrompt) gasta monedas; si mueres reapareces al empezar la siguiente ronda solo si queda un compañero vivo; si mueren todos sale la pantalla FIN con la ronda y la moneda del lobby y a los 12 s empieza otra partida. Jefe (más grande, 2 tipos al azar) cada 15 rondas.
- **Código puro probado (26 pruebas):** `src/Oleadas.lua`, `src/Partida.lua`, `src/Tienda.lua` (+ Weapons, Impactos, Disparo).
- **Roblox (no probado):** `server/Partida.server.lua`, `client/Partida.client.lua`, `server/Armas.server.lua`, `client/Armas.client.lua`, `client/ImpactoFX.lua`. `server/Maniquies.server.lua` solo se activa con `workspace:SetAttribute("LUTO_Maniquies", true)`.
- **Falta:** el mapa real y el zombi de Blender (ahora son bloques/rigs por defecto), animaciones de caminar y de las armas, sonidos subidos a Roblox, lobby y tienda de clases/armas con la moneda del lobby, balance real.

## Interfaces rediseñadas (Maikol: "las interfaces están horribles")
Estilo: paneles oscuros con esquinas ámbar, tipografía condensada (Oswald), colores apagados; todo por código, sin imágenes. Bocetos de diseño en `ui-mock/` (`hud.png`, `fin.png`, hechos en HTML; **no son capturas de Roblox**).
- `client/ui/Tema.lua`: paneles, etiquetas, barras con color por nivel (verde / ámbar / rojo), escala según la pantalla (móvil y escritorio).
- `client/Hud.client.lua` (reemplaza a las etiquetas provisionales): ronda y zombis arriba al centro, equipo con vida de cada compañero, vida y monedas abajo a la izquierda, arma y munición (número grande; ámbar al 30 %, rojo en 0; "RECARGANDO…") y ranuras 1-2-3 abajo a la derecha, mira con marcador de impacto (rojo; ámbar a la cabeza), viñeta roja al recibir daño y pulso con vida baja, anuncio central de ronda (rojo en jefe), banner con barra de vida del jefe, ganancias "+10 ZOMBI" a la derecha, pantalla de fin con ronda, bajas y moneda del lobby con cuenta atrás, y prompts de la tienda con el mismo estilo.
- Todo **sin probar en Studio** (solo sintaxis comprobada). Falta: lobby y menú de clases/armas.
