# Slime Rush v2 — mundo generado, exploración, robo y carrera a la meta

> **Estado:** propuesta del director, pendiente de aprobación del usuario. Lo que dijo Maikol está marcado **[Maikol]**; lo que propongo yo, **[Propuesta]**. Nada de esto está probado en Roblox Studio.
> Reemplaza el enfoque anterior de "mapa fijo + lava" (arena/valle). Los archivos de ese enfoque se perdieron con el reinicio del PC.

## 1. La idea en una frase
**[Maikol]** Un mapa grande que cambia en cada partida (como Minecraft: una semilla crea el mundo). Los jugadores exploran, consiguen recursos, se roban entre ellos y acampan en la meta para robar. Hay tiempo límite; pasado cierto punto se puede volver a la meta y todos deben llegar antes de que se acabe; los primeros en llegar ganan bonificación. **La mayoría de los puntos salen de lo que encuentras en el mapa.**

## 2. Línea de tiempo de una partida **[Propuesta: tiempos ajustables]**
| Fase | Tiempo | Qué pasa |
|---|---|---|
| Generación y entrada | ~10 s | El servidor elige la semilla y construye el mundo; entrada animada de todos, cuenta 3-2-1 |
| Exploración | 0:00 → 6:00 | Se recolecta, se abren cofres, se caza lo raro, se roba |
| **Regreso habilitado** | 6:00 → 10:00 | Se abre la meta (aviso + marcador visible); se puede volver a depositar y cobrar bono de llegada |
| Fin | 10:00 | Quien no depositó **pierde lo que lleva** (se queda en el suelo/devuelve al mundo) |
| Resultados | ~8 s | Puntos, bonos y raros destacados |

## 3. De dónde salen los puntos **[Propuesta]** (meta: ≥ 80 % del total viene del mapa)
| Fuente | Ejemplo de valor | Frecuencia |
|---|---|---|
| Recursos comunes repartidos (cristales, bayas, minerales) | 1–5 | Muchos |
| Cofres comunes / musgosos | 20 / 40 | Bastantes, a la vista o con pista |
| **Cofres ocultos** (enterrados, tras ruinas, en cuevas) | 60–150 | Pocos, buscados con indicios |
| **Slime raro** (apareces rara vez) | 100–300 | Muy raro |
| **Accesorio raro** (sombrero, alitas…) | 60–200 (+ se conserva como cosmético) | Raro |
| Bono de llegada a la meta | 1º +150 · 2º +100 · 3º +60 · 4º +30 · resto +10 | Fijo, **máx. ~20 %** del total |

Los valores son semilla de ajuste: se equilibran con partidas de prueba, no a ojo.

## 4. Robo y la meta **[Maikol: "campean en la meta para robar"; "te pueden robar lo que recolectaste en la partida"]**
**[Propuesta de reglas]**
- Lo que llevas en la **mochila** es robable. Lo **depositado** en la meta está a salvo.
- Robar = golpe/embestida: quita **1–2 objetos** (aleatorios, no todo) de la mochila del rival y pasan a la tuya. Los robados también son robables.
- **Contrajuego** para que acampar no sea imbatible: el depósito en la meta es un **canal de ~2 s** (se interrumpe si te golpean); después de que te roben tienes **6 s de inmunidad** y empujón de escape; la mochila tiene capacidad limitada (más botín = más lento).
- Lo raro puede ser **ligado** (un slime raro te sigue y cuesta 2 golpes quitarlo).
- Si te caes del mapa/mueres **sueltas** parte de lo que llevas.

## 5. Generación del mundo **[Propuesta técnica]**
- El servidor elige una **semilla** por partida (`Random.new(seed)` + `math.noise` desplazado por la semilla). Misma semilla = mismo mundo: permite repetir, comparar y depurar.
- **Tamaño:** ~1024 × 1024 studs (grande pero no inmenso). Terreno por voxels (`Terrain`) con materiales de colores cartoon, en trozos para no congelar el servidor; Streaming activado.
- **Biomas** (bosque, pradera/colinas, lago/costa, cueva/roca, desierto, montaña): dos ruidos de baja frecuencia (humedad, temperatura) + elevación; transiciones suaves.
- **Meta:** en una plaza plana y legible (centro o borde, según semilla); **aparición** de los jugadores repartida y equidistante.
- **Colocación:** muestreo de Poisson por bioma para recursos, árboles y rocas; cofres con separación mínima y reglas (los ocultos: cuevas, tras ruinas, enterrados con indicio sutil); raros con probabilidad pequeña por bioma.
- **Justicia:** el valor total de botín por cuadrante se normaliza (±10 %) para que ninguna zona de aparición sea mejor.
- **Arte:** kit modular hecho en **Blender** (rocas, arbustos, cofres, nodos de recurso, ruinas, meta). El generador instancia piezas, no hace un mapa único a mano.

## 6. Qué se hace y quién **[Propuesta de reparto]**
Ver tablero del Taller IA (`taller-ia/planes/slime-rush.json`). Resumen: Opus → kit de arte, biomas, árboles, slimes/accesorios raros (Blender); Claude (director) → este diseño, generador de mundo y reglas de partida en Luau con pruebas; Codex → integración en Studio, robo/depósito, cofres, rendimiento y pruebas con 2+ clientes; Antigravity → crítica visual, diseño de interfaz y de los accesorios raros.

## 7. Decisiones abiertas (necesito tu respuesta)
1. **Duración** de la partida y cuándo se abre el regreso (propongo 10 min y regreso a los 6).
2. **Cuánto se roba** por golpe (1–2 objetos vs. un % de la mochila vs. todo).
3. **¿Mantener la lava** del diseño anterior como presión de tiempo o sustituirla por el cierre a los 10:00?
4. **Tamaño** del mapa y jugadores por partida (propongo 1024 × 1024 y hasta 8–12).
5. **Qué pasa con lo que no depositaste** al acabar el tiempo (se pierde vs. se conserva a mitad).
