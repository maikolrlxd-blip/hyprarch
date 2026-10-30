# Mascotas de los enemigos v01 — estado (30/10/2026, Coordinador)
Maikol, 30/10: los enemigos también se consiguen como mascotas, y las mascotas solo salen de los huevos alados. Son las seis piezas voxel de `enemigos-v02/` en versión amable, cada una con la rareza de la tabla del director (`mas1-juego/src/Mascotas.lua`): nube y globo, poco comunes; nubarrón y ovni, raros; meteorito y cometa, épicos. Todo son renders de Blender: **nada está probado en Roblox**.

## Fallos y límites (primero)
- **Sin probar en Roblox**: ni la importación, ni los huesos, ni los clips, ni el tamaño junto al jugador en vuelo. La validación es una reimportación en Blender.
- **Los nombres no pegan con la cara**: `Mascotas.lua` las llama «Nube gruñona», «Cometa enfadada» o «Meteorito furioso», pero la mascota sonríe. Si el juego quiere, se pueden renombrar como mascotas (por ejemplo, «Nubecita» o «Cometa feliz»). Eso lo decide el juego.
- **Hueso `Brow` vacío**: el rig es el del enemigo y conserva `Brow`, pero la cara amable no tiene cejas: 0 vértices en las seis. En Roblox no hace nada; se puede quitar si estorba.
- **Nada brilla**: el rayo del nubarrón, las luces del ovni y la lava y el fuego del meteorito son solo color. Para brillo hacen falta piezas Neon o partículas en el juego.
- **La cometa es plana**: 0,36 studs de fondo. De lado casi desaparece, igual que el enemigo.
- **Seguir al jugador lo hace el juego**: el origen está en el suelo, bajo la pieza, y la mascota flota a su altura (por ejemplo, la nube empieza a 0,81 studs). Dónde va y a qué distancia del jugador, lo decide el código.

## Qué hay
| Mascota | Carpeta | Rareza | Escala respecto al enemigo | Triángulos | Ancho × alto × fondo (studs) | Huesos que se mueven |
|---|---|---|---|---|---|---|
| Nube | `nube/` | poco común | 0,62 | 1.250 | 2,60 × 1,36 × 1,45 | `Body, Puff_R/L, Lid_R/L` |
| Globo | `globo/` | poco común | 0,75 | 664 | 1,35 × 2,72 × 1,45 | `Body, String, Lid_R/L` |
| Nubarrón | `nubarron/` | raro | 0,70 | 1.274 | 2,94 × 2,35 × 1,63 | los de la nube + `Bolt` |
| Ovni | `ovni/` | raro | 0,70 | 1.488 | 2,97 × 1,68 × 3,12 | `Body, Rim, Alien, Antenna, Lid_R/L` |
| Meteorito | `meteorito/` | épico | 0,95 | 938 | 2,09 × 2,81 × 3,07 | `Body, Tail, Lid_R/L` |
| Cometa | `cometa/` | épico | 0,80 | 428 | 1,76 × 3,52 × 0,36 | `Body, Tail_1/2/3, Lid_R/L` |

- **Cara amable** en las seis: sin cejas, con sonrisa, mejillas rosas y los mismos ojos pequeños con brillo que las mascotas de Codex y Antigravity. Los párpados son una región propia sin oclusión, como en los enemigos.
- **Comprobaciones**: `comprobar_malla.py` da 0 piezas sueltas y 0 caras coplanares solapadas en las seis (las caras que quedaban cerca de un plano de voxel se apartaron para que no parpadeen al escalar). `validar_asset.py` da correcto en las seis (reimporta el FBX del rig, el de cada clip y el GLB).

## Clips
- `Fly`: 1,0 s, en bucle. Sube y baja inclinada hacia delante, con sus piezas en marcha: aletean las nubecitas, se balancea el rayo, ondean el cordel y la cola, gira el borde del ovni y tiembla el fuego.
- `Glide`: 2,0 s, en bucle. El mismo movimiento, más suave.
- `Celebrate`: 2,0 s, en bucle. Saltan con una vuelta entera y entornan los ojos.
- `Blink`: 8 fotogramas, solo los párpados. Su FBX solo lleva los canales de `Lid_R/L`.
- FBX con `global_scale=0.01` y `axis_forward='Z'`, como el resto de mis piezas.

## Archivos para mirar
- `Mascotas-enemigos-v01-hoja.jpg`: las seis juntas.
- `<id>/previews/Mascota-<id>-hoja.jpg`: frente con la regla de 6 studs, 3/4, cara, lateral, vuelo, planeo, celebración y parpadeo.
- Los GIF `-Fly` y `-Celebrate`.

## Cómo regenerar
1. `blender -b --factory-startup --python-exit-code 1 -P tools/build_mascotas_enemigos.py`. Variables: `MASCOTA_FASE=geo|check|full` y `MASCOTA_SOLO=<id>`. Reutiliza `construir()` de los scripts de enemigos, cambiándoles la cara.
2. `tools/hoja_mascotas_enemigos.py` para la hoja conjunta.
3. Validación: `tools/validar_asset.py` (CLIPS Fly,Glide,Celebrate,Blink; LOOPS Fly,Glide,Celebrate) y `tools/comprobar_malla.py`.
