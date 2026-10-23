# Subfusil — estado

Versión v2c, del 2026-10-23. Maikol congeló el diseño, así que en esta versión solo hay correcciones de errores, animaciones y la exportación para el código.

## Qué falla
- **Base del cargador:** sobresale en ángulo, como una pestaña.
- **Triángulos:** 780, al límite del presupuesto (800).
- **Sin probar en Roblox Studio:** los clips con el Animation Editor y el Tool.

## Qué funciona
- **La culata ya no tapa la pantalla:** es más fina y más baja, y el viewmodel está más bajo. Solo asoma una cuña pequeña abajo a la derecha.
- **Más contraste:** el polímero es oscuro y el metal del cajón, el cañón y el cargador, más claro.
- **Inspeccionar (3,00 s):** levanta el arma y la gira hacia la mano izquierda, que saca el cargador a medias, lo mira y lo mete. Después gira el arma al otro lado y vuelve.
- **Eventos y puntos para el código:** `eventos.json` y `Subfusil_Eventos.lua`.

## Triángulos
**780 en total**:
- Cuerpo: 592
- Cargador: 72
- Palanca: 40
- Cerrojo: 12
- Gatillo: 20
- Casquillo: 44

## Clips
- Equipar: 0,80 s
- Disparo: 0,16 s (fuego automático)
- Recargar: 1,95 s
- Amartillar: 0,40 s
- Reposo: 2,00 s
- Inspeccionar: 3,00 s

## Vueltas
1. **v1:** losa y 1266 triángulos.
2. **v2:** 780 triángulos.
3. **v2b:** culata fina, contraste, viewmodel más bajo, inspección y eventos.
4. **v2c:** inspección con el cargador a la vista y mangas finas.
