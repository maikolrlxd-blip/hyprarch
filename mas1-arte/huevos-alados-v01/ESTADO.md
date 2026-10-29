# Huevos alados v01 — estado (29/10/2026, Coordinador)
Idea de Maikol: los cofres voladores dan alas y los **huevos voladores con alas dan mascotas**; cuanto más raro el huevo, más rara la mascota. Cinco rarezas con el mismo modelo y rig: común, poco común, raro, legendario y mítico. Todo son renders de Blender: **nada está probado en Roblox**.

## Fallos y límites (primero)
- **Sin probar en Roblox**: ni la importación del FBX, ni los huesos, ni los clips. La validación es una reimportación en Blender.
- **Estilo distinto de las mascotas**: los huevos son facetados low-poly (como el cofre de Codex), no voxeles como mis mascotas. La v01 en voxeles de 0,2 se descartó antes de enseñarla porque a ese tamaño parecía una roca. Falta que Maikol diga si el huevo facetado encaja.
- **El interior "brilla" solo por color**: la grieta deja una rendija de 0,05 studs que enseña el interior claro, pero con un solo material no hay luz propia. En Roblox puede verse como una línea gris. Para que brille de verdad hace falta una pieza Neon aparte o partículas en el juego.
- **Manchas (común) y estrellas (mítico) son geometría**: rombos medio hundidos en la cáscara (sobresalen unos 0,04 studs). Suman triángulos y se reparten al azar con semilla fija; la distribución no está revisada desde todos los ángulos.
- **Hatch**: la tapa salta 0,5 studs y se inclina 24° hacia atrás. Por detrás pasa cerca del borde del cuerpo (holgura de unos 0,18 studs), comprobado solo en los renders.
- **Alas**: abanico vertical como el del cofre, con el aleteo de las mascotas (recoger → extender → impulsar → recoger). La razón envergadura plegada/extendida de `Fly` es 0,69–0,73 (mis mascotas: 0,53–0,56): el abanico es vertical y al recoger se nota menos.. Las coberteras de delante se ven algo cuadradas de cerca.
- **Sin cara ni clip de suelo**: el huevo no tiene ojos (como el cofre) ni clip Idle/Celebrate. La mascota que sale no está incluida: la pone el juego.

## Qué hay
| Rareza | Carpeta | Triángulos | Envergadura × alto (studs) | Patrón | Adorno | Escala de alas |
|---|---|---|---|---|---|---|
| Común | `comun/` | 1.344 | 4,24 × 2,64 | manchas marrones (rombos pegados) | — | 0,86 |
| Poco común | `poco-comun/` | 1.056 | 4,42 × 2,64 | zigzag de Pascua (ecuador y tapa) | — | 0,92 |
| Raro | `raro/` | 1.068 | 4,66 × 2,64 | rayas blancas | gema cian | 1,00 |
| Legendario | `legendario/` | 1.068 | 4,90 × 2,64 | rombos dorados (banda entera en el ecuador, filas sueltas abajo y en la tapa) y polos dorados | joya dorada | 1,08 |
| Mítico | `mitico/` | 1.332 | 5,14 × 3,30 (con la corona) | estrellas claras y doradas (rombos pegados) | rombo dorado y corona de tres plumas | 1,16 |

- Cáscara: torno de 16 lados y 12 bandas con los anillos girados medio lado (malla de triángulos facetada), unos 2,0 × 2,64 studs (la mitad del maniquí de 5,2). Grieta en zigzag de 8 dientes; tapa y cuerpo son piezas separadas con el interior hueco (borde y cuenco del color `interior`).
- Patrones pintados por caras: manchas (común), zigzag de Pascua (poco común), rayas (raro), rombos dorados con banda completa en el ecuador y polos dorados (legendario), estrellas claras y doradas (mítico).
- Adornos: gema cian (raro), joya dorada (legendario), rombo dorado y corona de tres plumas (mítico).
- Alas en abanico vertical de plumas en flecha (claras con la punta del color de la rareza, como el cofre): 2 coberteras, 3 secundarias y 5 primarias por lado; crecen con la rareza (de 0,86 a 1,16).
- Comprobaciones: `validar_asset.py` correcta en los cinco (reimporta el FBX del rig, el de cada clip y el GLB) y `comprobar_malla.py` con 0 piezas sueltas y 0 caras coplanares solapadas en los cinco.

## Rig y clips
- 7 huesos: `Root`, `Body` (centro del huevo), `Cap` (tapa, en el centro de la grieta), `Wing_R/L` (hombro), `Tip_R/L` (muñeca). Piel rígida (un hueso por vértice).
- `Fly` 0,6 s en bucle (aleteo rápido, sube y baja), `Glide` 2,0 s en bucle (alas abiertas, se mece), `Hatch` 1,5 s sin bucle (tiembla, salta la tapa, se queda abierto con las alas arriba).
- Exportación: `<Nombre>_Rig.fbx` (pose neutra), `clips/<Nombre>_<Clip>.fbx`, `<Nombre>.glb` (los tres clips), `.blend`, `texturas/<Nombre>_paleta_1024.png` (un material, una malla), `datos.json`, `VALIDACION.json`, `COMPROBACION_MALLA.json`. FBX con `global_scale=0.01`, `axis_forward='Z'` (frente +Y en Blender), como mis mascotas.

## Archivos para mirar
- `Huevos-alados-v01-hoja.jpg`: los cinco juntos, cerrados, volando y abiertos.
- `<rareza>/previews/Huevo-<rareza>-hoja.jpg`: frente con la regla de 6 studs, 3/4, lateral, espalda, aleteo arriba y abajo, eclosión.
- `<rareza>/previews/Huevo-<rareza>-Fly.gif` y `-Hatch.gif`.

## Cómo regenerar
`blender -b --factory-startup --python-exit-code 1 -P tools/build_huevos_alados.py` (`HUEVO_FASE=geo|check|full`, `HUEVO_SOLO=<rareza>`), después `tools/hoja_huevos_alados.py` para la hoja conjunta. Validación: `tools/validar_asset.py` (CLIPS Fly,Glide,Hatch; LOOPS Fly,Glide) y `tools/comprobar_malla.py`.
