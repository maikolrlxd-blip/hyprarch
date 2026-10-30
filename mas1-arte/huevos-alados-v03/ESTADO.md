# Huevos alados v03 — estado (30/10/2026, Coordinador)
La segunda crítica del director decía que las formas eran aún muy parecidas: todos eran un huevo ovalado con alas pequeñas, el común y el poco común casi medían lo mismo, y la diferencia principal era el color. Pedía que el mítico se leyera de lejos con silueta propia. La v03 separa mucho más los tamaños, hace crecer las alas de 0,6 a 1,6 y da a cada rareza un extra que cambia la silueta. Son los mismos seis huevos de la tabla `HUEVOS` de `mas1-juego/src/Mascotas.lua`. Todo son renders de Blender: **nada está probado en Roblox**.

## Fallos y límites (primero)
- **Sin probar en Roblox**: ni la importación del FBX, ni los huesos, ni los clips. La validación es una reimportación en Blender.
- **Siguen facetados, no en voxeles**, como en la v02.
- **Extras pequeños de lejos**: en la foto de grupo, los cuernos del épico y el halo del mítico se ven pequeños. De cerca se leen bien.
- **El halo no flota**: atraviesa las plumas de la corona para quedar unido al resto. Sube y baja con la tapa (hueso `Cap`), así que al eclosionar sale volando con ella.
- **El brillo y el aura por rareza no están en la malla**: los pone la capa de efectos de Linux 2.0 (`src/Efectos.lua`, `aura_*`).
- Lo demás sigue como en la v02: el interior brilla solo por color, y las manchas y estrellas son geometría pegada.

## Qué hay
| Rareza | Carpeta | Triángulos | Envergadura × alto (studs) | Silueta |
|---|---|---|---|---|
| Común | `comun/` | 1.040 | 2,81 × 1,80 | pequeño y redondo, alas cortitas (escala 0,60) |
| Poco común | `poco-comun/` | 1.000 | 3,87 × 2,56 | mediano, con un **copete** de tres plumas arriba (0,85) |
| Raro | `raro/` | 1.068 | 4,62 × 2,80 | **alto y puntiagudo**, 5 primarias (1,05) |
| Épico | `epico/` | 1.228 | 5,40 × 2,65 | **ancho**, con dos **cuernos** curvos a los lados de la tapa (1,15) |
| Legendario | `legendario/` | 1.308 | 5,92 × 3,29 | grande, con **cresta** de plumas largas doradas (1,35) |
| Mítico | `mitico/` | 2.020 | 6,91 × 3,90 | el más grande, con **alas enormes de doble abanico**, corona y **halo** dorado (1,60) |

- Comprobaciones:
  - `validar_asset.py` da correcto en los seis: reimporta el FBX del rig, el de cada clip y el GLB.
  - `comprobar_malla.py` da 0 piezas sueltas y 0 caras coplanares solapadas en los seis.
- Rig y clips iguales que en la v02:
  - 7 huesos: `Root`, `Body`, `Cap`, `Wing_R/L` y `Tip_R/L`;
  - `Fly`: 0,6 s, en bucle;
  - `Glide`: 2,0 s, en bucle;
  - `Hatch`: 1,5 s, sin bucle.
  - FBX con `global_scale=0.01` y `axis_forward='Z'`.

## Archivos para mirar
- `Huevos-alados-v03-hoja.jpg`: los seis juntos al lado del maniquí, cerrados, volando y abriéndose.
- `<rareza>/previews/Huevo-<rareza>-hoja.jpg`, y los GIF `-Fly` y `-Hatch`.

## Cómo regenerar
1. `blender -b --factory-startup --python-exit-code 1 -P tools/build_huevos_alados.py`. Variables: `HUEVO_FASE=geo|check|full` y `HUEVO_SOLO=<rareza>`.
2. `tools/hoja_huevos_alados.py` para la hoja conjunta.
3. Validación: `tools/validar_asset.py` y `tools/comprobar_malla.py`.

La v02 (siluetas parecidas) sigue en `huevos-alados-v02/`, y la v01 en `huevos-alados-v01/`.
