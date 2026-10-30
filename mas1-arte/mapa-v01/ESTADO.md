# Mapa v01 — zonas después de la Pradera (30/10/2026, Coordinador)
Lo visual del recorrido recto que sigue a la Pradera del Despegue de Codex, como pidió Maikol («primero todo lo visual, el código después»): **Mar de Nubes → Tormenta → Cielo alto → Espacio**. Todo son renders de Blender: **nada está montado ni probado en Roblox todavía**.

## Fallos y límites (primero)
- **Sin montar en Studio**: falta importar las piezas y comprobar la escala y la orientación junto a la Pradera. Ojo: la Pradera de Codex se exportó con `axis_forward='-Z'` y la escala por defecto, y mis piezas con `global_scale=0.01` y `axis_forward='Z'` (mi convención); puede que haya que girar 180° o reescalar una de las dos al juntarlas.
- **Largo provisional**: 360 studs por zona. El largo de verdad depende del vuelo (el impulso y la resistencia de las alas y las mascotas), que aún no está programado. Cada zona está hecha por tramos que se pueden repetir para alargarla.
- **Multiplicadores provisionales**: las marcas del suelo dicen x3, x4, x5 y x6 siguiendo el x2 de la Pradera; los números los decide el juego.
- **Sin cielo, luz ni niebla por zona**: el color del cielo de los renders es el fondo de Blender. En Roblox, cambiar el cielo al entrar en cada zona necesita código (para después).
- **Sin colisiones**: el carril de 66 studs (como el prado de la Pradera) es para aterrizar; las nubes del borde y los lados son decorado. Qué choca y qué no lo decide el juego.
- **Nada brilla**: auroras, rayos, cristales y estrellas son color con un solo material (para brillo, piezas Neon o partículas en el juego).
- **Mejorable**: las torres de nubes parecen pilas de bloques redondeados; los asteroides y planetas son low-poly sencillos.
- **La Pradera no es mía**: los renders la cargan del archivo de Codex (sin tocarlo) solo para ver el empalme; no va en los exportes.

## Qué hay
| Zona | Desde y hasta (Y, studs) | Marca | Lo que tiene |
|---|---|---|---|
| Mar de Nubes | 172 → 532 | x3 | carril de baldosas de nube, nubes redondeadas en el borde, mar de nubes bajo, torres de cúmulos, islitas flotantes con árbol |
| Tormenta | 532 → 892 | x4 | carril oscuro, nubarrones altos, rayos que caen al mar de nubes |
| Cielo alto | 892 → 1.252 | x5 | carril rosa, cristales clavados y flotando, tres auroras que ondulan a cada lado |
| Espacio | 1.252 → 1.612 | x6 | carril de roca con cráteres, rocas en el borde, asteroides, dos planetas con anillo, estrellas |

- En cada zona: arco de entrada con el nombre en letras de bloques (legible al llegar volando), marca de multiplicador y flechas en el suelo y tres aros que suben (z = 14, 20 y 26).
- Piezas por zona, cada una en su FBX y GLB (`exports/<zona>_<pieza>`): `Suelo`, `LadoIzq`, `LadoDer`, `Arco`, `Marcas` y `Aros`; ninguna pasa de 10.000 triángulos (la mayor, 9.620). Unos 85.000 en total.
- Una sola textura para todo: `texturas/Mapa_paleta_256.png` (un cuadro de color por región, como la paleta de la Pradera).

## Siguiente
1. Montarlo en Studio con la Pradera (permiso de Maikol del 30/10) y comprobar escala, orientación y que se ve igual con la luz de Roblox.
2. Cuando haya vuelo programado: ajustar el largo de cada zona y la altura de los aros.
3. Código (después): cielo y niebla por zona, colisiones, aros que dan puntos.

## Cómo regenerar
`blender -b --factory-startup --python-exit-code 1 -P tools/build_mapa.py` (`MAPA_FASE=check|full`). Escribe `Mapa-v01.blend`, `exports/`, `texturas/`, `previews/`, `datos.json` y la hoja `Mapa-v01-hoja.jpg`.
