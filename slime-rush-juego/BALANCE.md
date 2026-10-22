# Balance (simulaciones) — Slime Rush v2
Herramienta: `python3 slime-rush-juego/tools/sim_mochila.py` (24 bots avaros compitiendo, 16 studs/s, 5 semillas, 360 s de exploración).

| Mochila | Bots que la llenan | Tiempo medio en llenarla | Valor peor / mediana / mejor | Valor que sobra en el mapa |
|---|---|---|---|---|
| 12 | 24/24 | 52 s | 115 / 194 / 267 | 1866 |
| 20 | 24/24 | 85 s | 169 / 224 / 308 | 1014 |
| **30** | 24/24 | **134 s** | 200 / 260 / 334 | 318 |
| 40 | 21/24 | 177 s | 211 / 275 / 346 | 31 |

**Conclusión:** con 12 huecos la exploración de 6 minutos queda vacía (todos llenos en menos de 1 min, más de la mitad del mapa sin tocar). Con **30** (el HUD de Codex ya mostraba 0/30) se llena hacia los 2 min, queda tiempo para robar y volver, hay menos diferencia entre el peor y el mejor y el mapa casi se agota (tensión). `Rules.DEFAULT.backpack = 30`.
Límites del modelo: los bots no pelean, no cargan raros/accesorios ni sufren el volcán; es una guía, no una verdad. Falta medir con jugadores reales.
Otras cifras: bonos de llegada ≈ 7 % de los puntos (24 bots).
