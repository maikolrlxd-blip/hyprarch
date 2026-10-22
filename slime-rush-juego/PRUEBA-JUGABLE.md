# Prueba jugable (vertical slice) — Slime Rush v2
Objetivo: saber en pocas horas **si la partida divierte**, antes de invertir en arte. Todo provisional, hecho para tirarse.

## Alcance (solo esto)
- 1 isla pequeña (World.generate con size reducido, ej. 512, 4–8 jugadores/bots), semilla fija para comparar.
- 1 slime base con 1 habilidad por cada uno: **Bongo** (puñetazo), **Rayo** (montura corta), **Miga** (lanzar 3 partes). Las otras después.
- Fases de Rules.lua: cuenta atrás → explorar → regreso → colapso (versión corta: explorar 120 s, regreso 60 s, colapso 20 s).
- Recursos (nodos) y 3 cofres; inconsciencia + saqueo; meta con depósito; puntuación final.
- 1 desastre (tormenta/terremoto simple) y volcán opcional **no** en esta prueba.
- Animaciones, efectos, sonidos e impactos: DESPUÉS (ver SENSACION.md). Solo lo mínimo para entender qué pasó.
- Arte: formas simples de colores (provisional). Los modelos del kit v03 NO son requisito.

## Quién hace qué
| Quién | Tarea |
|---|---|
| Codex (ingeniero) | Terreno desde World.generate sin Terrain de fábrica o con bloques provisionales; conectar Rules.lua al combate; las 3 habilidades mínimas; Rojo + proyecto de Studio |
| Antigravity | Crítica visual de capturas, mockup del HUD (tiempo, mochila, puntos), guion de intro |
| Claude (nube) | Diseño/reglas, pruebas, balance con simulación, vault; **no** hace modelos |
| Claude del PC | Control de PC, tareas con permiso de Maikol, Roble v06 |
| Maikol | Jugar la prueba y decir "divierte / no divierte" por fase |

## Criterios para decir que funciona
1. Una partida completa de 4–8 jugadores sin errores en la consola.
2. 30+ FPS en la computadora de Maikol con 8 jugadores.
3. Al menos una decisión interesante por partida (volver pronto vs. arriesgarse; saquear vs. huir).
4. Maikol responde: ¿ganas ganas de otra partida? (sí/no y por qué).

## Qué medir
FPS, latencia al dar golpes, tamaño de la isla vs. tiempo de recorrido, puntos por fuente (mapa vs. bonos de llegada, meta ≤ ~10 %).

## Siguiente decisión según resultado
Si divierte: arte definitivo por bloques (botes, volcán, árboles) y subir a 24 jugadores/isla grande. Si no: ajustar reglas antes de hacer más arte.
