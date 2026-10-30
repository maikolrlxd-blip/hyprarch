# Huevos alados v02 — estado (30/10/2026, Coordinador)
Maikol pidió «huevos más distintos» tras la crítica del director: en la v01 los cinco eran el mismo huevo cambiando el color. La v02 tiene **seis**, uno por cada huevo de la tabla `HUEVOS` de `mas1-juego/src/Mascotas.lua`: común, poco común, raro, **épico** (rareza nueva), legendario y mítico. El fénix no sale de huevos. Ahora cambian de tamaño, de forma y de alas, no solo de color. Todo son renders de Blender: **nada está probado en Roblox**.

## Fallos y límites (primero)
- **Sin probar en Roblox**: ni la importación del FBX, ni los huesos, ni los clips. La validación es una reimportación en Blender.
- **Siguen facetados, no en voxeles**: Maikol pidió los enemigos en voxel. Los huevos siguen en low-poly facetado, como el cofre de Codex, porque en voxeles de 0,2 el huevo parecía una roca (por eso se descartó la v01 en voxel). Si se quieren en voxel, haría falta otra versión.
- **El interior "brilla" solo por color**, como en la v01: para un brillo de verdad hace falta una pieza Neon o partículas en el juego.
- **Manchas, estrellas y rombos son geometría pegada**: rombos medio hundidos en la cáscara, repartidos al azar con semilla fija. No están revisados desde todos los ángulos.
- **Hatch**: la tapa salta en proporción al tamaño de cada huevo. Que no choque con el cuerpo solo se ha mirado en los renders.
- **Sin cara ni clip de suelo**. La mascota que sale no viene incluida: la pone el juego.
- **Fotos**: en la foto de frente de cada huevo, la regla de 6 studs queda fuera del encuadre. Para el tamaño, sirve el maniquí de 5,2 studs.

## Qué hay
| Rareza | Carpeta | Triángulos | Envergadura × alto (studs) | Forma | Alas | Patrón y adorno |
|---|---|---|---|---|---|---|
| Común | `comun/` | 1.040 | 3,34 × 2,04 | pequeño y redondo | 3 primarias (escala 0,72) | manchas marrones sobre crema |
| Poco común | `poco-comun/` | 928 | 3,82 × 2,28 | clásico | 4 primarias (0,82) | zigzag de Pascua verde |
| Raro | `raro/` | 1.068 | 4,36 × 2,72 | alto y puntiagudo | 5 primarias (0,95) | rayas blancas sobre azul, gema cian |
| Épico | `epico/` | 1.204 | 4,87 × 3,28 (con el pico) | ancho | 6 primarias (1,04) | espiral lila sobre morado, pico en la punta |
| Legendario | `legendario/` | 1.308 | 5,13 × 2,94 | grande | 6 primarias (1,10) y cresta de plumas largas | rombos dorados sobre crema, joya dorada |
| Mítico | `mitico/` | 1.636 | 5,43 × 3,66 (con la corona) | el más grande | 6 primarias (1,16) y doble abanico | estrellas doradas sobre carmesí, rombo dorado y corona |

- Cáscara: torno facetado con anillos girados medio lado, de 2,0 a 3,0 studs de alto. La grieta es un zigzag; la tapa y el cuerpo son piezas separadas con el interior hueco.
- Comprobaciones: `validar_asset.py` da correcto en los seis (reimporta el FBX del rig, el de cada clip y el GLB). `comprobar_malla.py` da 0 piezas sueltas y 0 caras coplanares solapadas en los seis.

## Rig y clips (igual que la v01)
- 7 huesos: `Root`, `Body`, `Cap`, `Wing_R/L` y `Tip_R/L`. Piel rígida: un hueso por vértice.
- Clips:
  - `Fly`: 0,6 s, en bucle.
  - `Glide`: 2,0 s, en bucle.
  - `Hatch`: 1,5 s, sin bucle. El huevo tiembla, la tapa salta y se queda abierto.
- Archivos por huevo: `<Nombre>_Rig.fbx`, `clips/<Nombre>_<Clip>.fbx`, `<Nombre>.glb`, `.blend` y `texturas/<Nombre>_paleta_1024.png`.
- Los FBX van con `global_scale=0.01` y `axis_forward='Z'`, como mis mascotas.

## Archivos para mirar
- `Huevos-alados-v02-hoja.jpg`: los seis juntos al lado del maniquí, cerrados, volando y abriéndose.
- `<rareza>/previews/Huevo-<rareza>-hoja.jpg` y los GIF `-Fly` y `-Hatch`.

## Cómo regenerar
1. `blender -b --factory-startup --python-exit-code 1 -P tools/build_huevos_alados.py`. Variables: `HUEVO_FASE=geo|check|full` y `HUEVO_SOLO=<rareza>`.
2. `tools/hoja_huevos_alados.py` para la hoja conjunta.
3. Validación: `tools/validar_asset.py` (CLIPS Fly,Glide,Hatch; LOOPS Fly,Glide) y `tools/comprobar_malla.py`.

La v01 (cinco huevos iguales cambiando el color) sigue en `huevos-alados-v01/`.
