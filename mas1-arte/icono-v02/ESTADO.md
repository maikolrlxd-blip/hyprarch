# Icono v02 — estado (05/11/2026, Coordinador)

Rehecho con la crítica del director del 30/10:
- avatar de espaldas con las alas abiertas y enormes;
- «+1» de un 40 % del icono;
- aro dorado detrás;
- cielo en degradado.

Archivos:
- `Icono-v02-512.png`: el que se sube a Roblox, 512 × 512.
- `Icono-v02-1024.png`: el mismo a 1024.

Se hace con `tools/icono_v02.py`. Es un render de Blender: **no se ha subido nada a Roblox**; el icono lo sube Maikol.

## Fallos (primero)
- **El torso no se ve:** lo tapa la placa de las alas. El avatar se lee por la cabeza y los brazos amarillos y las dos piernas verdes.
- **El avatar es de bloques genérico, no el de Maikol.** Los colores son los clásicos: cabeza amarilla, torso azul y piernas verdes.
- **El «+1» pisa la parte de arriba del aro.** Mide un 37 % del alto, un poco menos del 40 % pedido; si se hace más grande, tapa más el aro.
- **Las nubes de abajo quedan fuera del encuadre:** con la cámara lejos (objetivo de 46 mm), el fondo es solo el degradado.
- **Sin probar a tamaño pequeño en la página de Roblox:** a unos 150 px debería leerse el «+1», el aro y las alas, pero no lo he visto ahí.

## Qué hay
- **Cielo:** degradado de la imagen, de `#c9f4ff` abajo a `#2f6bff` arriba (coordenadas de ventana en el fondo del mundo).
- **Aro:** toro dorado (`#ffc83d`, un poco luminoso) con otro cian fino por dentro, como los aros del juego. Cinco orbes «+1» amarillos van camino del aro.
- **Avatar:** el de bloques de `tools/icono_miniaturas.py`, inclinado 52°, con las alas avanzadas v0.2 a escala 1,75 en la pose «arriba extendida» del Flap (fotograma 0).
- **Título:** Arial Black amarilla con contorno oscuro, pegada a la cámara.

## Arreglos hechos de paso en `tools/icono_miniaturas.py` (el icono v01 y las miniaturas)
- `pieza_rig` se queda solo con el rig y sus mallas. Antes, si los nombres no coincidían, traía el `.blend` entero, con el maniquí, la plataforma y la regla de comprobación. En la v01 no se veían porque estaban lejos.
- **Contorno del título:** se separa más del relleno cuanto más grande es la letra; con letras grandes, el bisel tapaba el amarillo.
- **Piernas del avatar:** algo más estrechas, con un hueco entre ellas, para que no se lean como un solo bloque.
- **Escena del v01:** va dentro de `if __name__ == '__main__'`, así que `icono_v02.py` puede importar sus funciones.
