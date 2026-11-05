# Icono v02 — estado (05/11/2026, Coordinador)

Rehecho con la crítica del director del 30/10:
- avatar de espaldas con las alas abiertas y enormes;
- «+1» de un 40 % del icono;
- aro dorado detrás;
- cielo en degradado.

Segunda vuelta con su revisión de las 05:40: avatar más grande en el centro del aro, alas en V y no como una franja plana, y que se lea a 128 px.

Archivos:
- `Icono-v02-512.png`: el que se sube a Roblox, 512 × 512.
- `Icono-v02-1024.png`: el mismo a 1024.

Se hace con `tools/icono_v02.py` (`ICONO_PRUEBA=1` para un render rápido). Es un render de Blender: **no se ha subido nada a Roblox**; el icono lo sube Maikol.

## Fallos (primero)
- **El torso no se ve:** lo tapa la placa oscura de las alas. El avatar se lee por la cabeza y los brazos amarillos y las dos piernas verdes.
- **El avatar es de bloques genérico, no el de Maikol.** Los colores son los clásicos.
- **El aro casi toca el borde de arriba**, y el «+1» tapa la parte de abajo del aro y de las nubes.
- **El «+1» mide un 38 % del alto.**
- **Sin ver en la página de Roblox.** Reducido a 128 px se leen el «+1», la V de las alas sobre el aro con luz y el aro dorado.

## Qué hay
- **Cielo:** degradado de la imagen, de `#c9f4ff` abajo a `#2f6bff` arriba.
- **Aro:** toro dorado (`#ffc83d`, un poco luminoso) con otro cian fino por dentro, como los aros del juego.
- **Luz dentro del aro:** un disco luminoso crema, para que la silueta oscura de las alas se recorte.
- **Avatar:** el de bloques de `tools/icono_miniaturas.py`, casi de pie (inclinado 18°) y de espaldas, en el centro del aro, con las alas avanzadas v0.2 a escala 2,1 en la pose «arriba extendida» del Flap.
- **Alrededor:** cuatro orbes «+1» y nubes abajo.
- **Título:** «+1» en Arial Black amarilla con contorno oscuro, abajo, sobre las nubes, para que la V de las alas quede libre arriba.

## Arreglos hechos de paso en `tools/icono_miniaturas.py` (el icono v01 y las miniaturas)
- `pieza_rig` se queda solo con el rig y sus mallas. Antes, si los nombres no coincidían, traía el `.blend` entero, con el maniquí, la plataforma y la regla de comprobación.
- **Contorno del título:** se separa más del relleno cuanto más grande es la letra.
- **Piernas del avatar:** con un hueco entre ellas.
- **Escena del v01:** va dentro de `if __name__ == '__main__'`.
