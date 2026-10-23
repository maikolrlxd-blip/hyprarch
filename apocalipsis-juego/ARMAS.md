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
