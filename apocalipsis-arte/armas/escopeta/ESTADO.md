# Escopeta de corredera — estado

Versión v2c, del 2026-10-23. El diseño está congelado por Maikol: solo se han hecho correcciones de errores, animaciones y la exportación para el código.

## Qué falla
- **Primera persona:** aunque está más cerca que en la v2, sigue viéndose fina y lejana por lo larga que es (4 studs). El antebrazo izquierdo ocupa la esquina inferior izquierda.
- **Madera y cajón:** la madera es lisa, sin estrías en la bomba, y el cajón también es liso por el lado izquierdo.
- **No probado en Roblox Studio:** ni los clips con el Animation Editor ni el Tool.

## Qué funciona
- **Silueta:** la de una escopeta de corredera clara.
- **Correcciones:**
  - madera con menos saturación;
  - guardamonte y gatillo más finos;
  - sin caras negras.
- **Bombear:** el casquillo rojo sale por la ventana derecha.
- **Recarga:** mete los cartuchos de uno en uno (`Recargar_Inicio`, después `Recargar_Cartucho` × N y al final `Recargar_Fin`).
- **Inspeccionar (3,00 s):** gira el arma para mirar la ventana, medio bombeo para revisar la recámara, la gira al otro lado y vuelve.
- **Eventos y puntos** para el código: `eventos.json` y `Escopeta_Eventos.lua`.

## Triángulos
**530 en total**:
- Cuerpo 342
- Bomba 68
- Cerrojo 12
- Gatillo 20
- Cartucho 44
- Casquillo 44

## Clips
| Clip | Duración |
|---|---|
| Equipar | 0,90 s |
| Disparo | 0,45 s |
| Bombear | 0,60 s |
| Recargar_Inicio | 0,45 s |
| Recargar_Cartucho | 0,50 s (bucle) |
| Recargar_Fin | 0,55 s |
| Recargar | 2,50 s |
| Reposo | 2,00 s (bucle) |
| Inspeccionar | 3,00 s |

## Vueltas
1. **v1:** cajón negro y 1264 triángulos.
2. **v2:** cajón por piezas, culata recta y 530 triángulos.
3. **v2b:** sin caras negras, madera desaturada, guardamonte fino, inspección y eventos.
4. **v2c:** viewmodel más cerca, inspección más marcada y mangas finas.
