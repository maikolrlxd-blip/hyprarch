# Enemigos voladores v02 (voxel) — estado (30/10/2026, Coordinador)
Los seis enemigos en voxeles de 0,2 como una sola familia, como pidió Maikol tras la crítica del director («estilos mezclados: nubes voxel, ovni liso, meteorito facetado»). Son blancos que el jugador golpea en vuelo para sumar puntos y también salen como mascotas (versión amable en `mascotas-enemigos-v01/`). Todo son renders de Blender: **nada está probado en Roblox**.

## Fallos y límites (primero)
- **Sin probar en Roblox**: ni la importación, ni los huesos, ni los clips, ni cómo se ven a la distancia del vuelo. La validación es una reimportación en Blender.
- **Nada brilla**: el rayo del nubarrón, las luces del ovni y la lava y el fuego del meteorito son color con un solo material. Para brillo de verdad hacen falta piezas Neon, luces o partículas en el juego.
- **Sin escala ni desvanecido**: en Roblox un hueso no se escala. El golpe (`Hit`) mueve piezas; encoger, desvanecer o soltar partículas al derrotarlos lo tiene que hacer el juego.
- **Sin caja de colisión ni zona de golpe**: las define el juego (medidas en la tabla).
- **Mezcla dentro de la familia**: la cola de fuego del meteorito y el cordel del globo y de la cometa no son voxel (lenguas en flecha como las plumas de llama del fénix y cordeles finos); el resto sí.
- **Arreglos de esta versión**: la cola de la cometa salía como letras «H» (ahora tres cuadritos de papel); las luces del ovni y los ojos del ovni y del meteorito quedaban a 0,01 de un plano de voxel (riesgo de parpadeo en Roblox) y se movieron.
- **Las zonas siguen sin decidir del todo**: Maikol no rechazó la propuesta (Pradera → Mar de Nubes → Tormenta → Cielo alto → Espacio), pero no está cerrada.

## Qué hay
| Enemigo | Carpeta | Triángulos | Ancho × alto × fondo (studs) | Huesos |
|---|---|---|---|---|
| Globo gruñón (Pradera) | `globo/` | 664 | 1,80 × 3,63 × 1,93 (con el cordel) | `Root, Body, String, Brow, Lid_R/L` |
| Nube gruñona (Mar de Nubes) | `nube-grunona/` | 1.250 | 4,20 × 2,20 × 2,36 | `Root, Body, Puff_R/L, Brow, Lid_R/L` |
| Nubarrón de tormenta (Tormenta) | `nubarron/` | 1.274 | 4,20 × 3,36 × 2,36 (con el rayo) | los de la nube + `Bolt` |
| Cometa enfadada (Cielo alto) | `cometa/` | 428 | 2,20 × 4,40 × 0,46 (con la cola) | `Root, Body, Tail_1/2/3, Brow, Lid_R/L` |
| Ovni (Espacio) | `ovni/` | 1.488 | 4,24 × 2,40 × 4,46 | `Root, Body, Rim, Alien, Antenna, Brow, Lid_R/L` |
| Meteorito (Espacio) | `meteorito/` | 938 | 2,20 × 2,96 × 3,23 (con la cola) | `Root, Body, Tail, Brow, Lid_R/L` |

- Todos en voxeles de 0,2 (estilo Roba un huevo): ojos diminutos con brillo, párpados (región propia sin oclusión), cejas enfadadas en su hueso y morro gruñón sobre una cara plana.
- Comprobaciones: `validar_asset.py` correcta en los seis (reimporta el FBX del rig, el de cada clip y el GLB) y `comprobar_malla.py` con 0 piezas sueltas y 0 caras coplanares solapadas en los seis.

## Clips
- `Idle` 2,0 s en bucle, `Hit` 0,5 s, `Defeat` 1,0 s y `Blink` (8 fotogramas, solo párpados; su FBX solo lleva los canales de `Lid_R/L`). FBX con `global_scale=0.01` y `axis_forward='Z'`, como mis mascotas.

## Archivos para mirar
- `Enemigos-v02-hoja.jpg`: los seis juntos, en reposo y golpeados.
- `<enemigo>/previews/<Enemigo>-hoja.jpg` y los GIF `-Idle`, `-Hit` y `-Defeat`.

## Cómo regenerar
`tools/build_enemigo_nube.py` (`NUBE_FASE=geo|check|full`, `NUBE_SOLO`), `tools/build_enemigo_espacio.py` (`ESPACIO_*`) y `tools/build_enemigo_cielo.py` (`CIELO_*`), con lo común en `tools/mas1_enemigo.py`; después `tools/hoja_enemigos.py`. Validación: `tools/validar_asset.py` (CLIPS Idle,Hit,Defeat,Blink; LOOPS Idle) y `tools/comprobar_malla.py`. La v01 (estilos mezclados) sigue en `enemigos-v01/`.
