# Enemigos voladores v01 — estado (29/10/2026, Coordinador)
Enemigos que el jugador golpea en pleno vuelo para sumar puntos («aros y enemigos atacados aumentan puntos», DISENO.md de Codex). Hechos: dos de la zona de nubes y dos del espacio. Todo son renders de Blender: **nada está probado en Roblox**.

## Fallos y límites (primero)
- **Sin probar en Roblox**: ni la importación, ni los huesos, ni los clips, ni cómo se ven a la distancia del vuelo. La validación es una reimportación en Blender.
- **Las zonas no están decididas**: Codex solo ha diseñado la Pradera del Despegue y el diseño dice «el espacio como última zona inicial». Las zonas y el reparto de enemigos de abajo son una **propuesta mía sin aprobar**.
- **Antigravity** hace «criaturas aladas y monstruos» y aún no ha dicho si son mascotas o enemigos. Por eso hice enemigos que no son criaturas (nubes, ovni, meteorito). Si sus monstruos son enemigos, se reparte de nuevo.
- **Sin escala ni desvanecido**: en Roblox un hueso no se escala. El golpe (`Hit`) mueve piezas; encoger, desvanecer o soltar partículas al derrotarla lo tiene que hacer el juego (por ejemplo con `Model:ScaleTo` y transparencias).
- **Nada brilla**: el rayo del nubarrón, las luces del ovni y la lava y el fuego del meteorito son color con un solo material. Para brillo de verdad hacen falta piezas Neon, luces o partículas en el juego.
- **Golpe y colisión**: no hay caja de colisión ni zona de golpe. El juego tiene que definirlas (medidas en la tabla).
- **Ovni, vuelta de las luces**: en `Idle` el hueso `Rim` da una vuelta entera (de 0° a 360°). El validador lo marcaba como bucle que no cierra; era un falso fallo por el signo del cuaternión (q y −q son la misma orientación) y lo arreglé en `validar_asset.py`. Falta ver cómo lo interpreta Roblox al importar el clip.
- **Lava del meteorito**: triángulos naranjas sueltos al azar; de cerca parecen confeti.
- **La misma cara en los cuatro** (ojos, cejas y morro iguales): funciona como familia, pero la expresión cambia poco de un enemigo a otro.

## Qué hay
| Enemigo | Carpeta | Triángulos | Ancho × alto × fondo (studs) | Huesos |
|---|---|---|---|---|
| Nube gruñona | `nube-grunona/` | 1.250 | 4,20 × 2,20 × 2,36 | `Root, Body, Puff_R/L, Brow, Lid_R/L` |
| Nubarrón de tormenta | `nubarron/` | 1.274 | 4,20 × 3,36 × 2,36 (con el rayo) | los mismos + `Bolt` |
| Ovni | `ovni/` | 1.046 | 4,07 × 2,39 × 4,28 | `Root, Body, Rim, Alien, Antenna, Brow, Lid_R/L` |
| Meteorito | `meteorito/` | 628 | 2,26 × 2,95 × 3,25 (con la cola) | `Root, Body, Tail, Brow, Lid_R/L` |

- Nubes y alienígena en voxeles de 0,2 como mis mascotas (estilo Roba un huevo: bultos gordos, sombras lavanda); el platillo del ovni y la roca del meteorito son facetados como los huevos. Todos llevan ojos diminutos con brillo, párpados (región propia sin oclusión, para que al cerrarse tengan el color de la cara), cejas enfadadas en su hueso y morro gruñón.
- Nube gruñona: blanca. Nubarrón de tormenta: gris azulado, ojos amarillos y un rayo colgando en su hueso `Bolt`.
- Ovni: platillo facetado (torno de 20 lados) con borde violeta, diez luces amarillas en el hueso `Rim` (dan una vuelta entera en `Idle`), emisor cian debajo y un alienígena verde de voxeles asomado (hueso `Alien`) con antena (`Antenna`).
- Meteorito: roca facetada con grietas de lava y una cola de fuego de lenguas en flecha que sube por detrás (hueso `Tail`).
- Comprobaciones: `validar_asset.py` correcta en los cuatro (reimporta el FBX del rig, el de cada clip y el GLB) y `comprobar_malla.py` con 0 piezas sueltas y 0 caras coplanares solapadas en los cuatro.

## Rig y clips
- Huesos de las nubes: `Root`, `Body`, `Puff_R/L` (nubecitas laterales que se mueven como brazos), `Brow` (cejas), `Lid_R/L` (párpados), y `Bolt` en el nubarrón. Ovni: `Root`, `Body`, `Rim`, `Alien`, `Antenna`, `Brow`, `Lid_R/L`. Meteorito: `Root`, `Body`, `Tail`, `Brow`, `Lid_R/L`. Piel rígida.
- `Idle` 2,0 s en bucle (flota, respira, mueve las nubecitas y el rayo), `Hit` 0,5 s (sale hacia atrás, se encoge, cierra los ojos y sube las cejas), `Defeat` 1,0 s (golpe, vuelta entera y caída) y `Blink` (8 fotogramas, solo párpados; su FBX solo lleva los canales de `Lid_R/L`, como en las mascotas).
- Exportación como mis mascotas: `<Nombre>_Rig.fbx`, `clips/<Nombre>_<Clip>.fbx`, `<Nombre>.glb`, `.blend`, `texturas/<Nombre>_paleta_1024.png`, `datos.json`, `VALIDACION.json`, `COMPROBACION_MALLA.json`. FBX con `global_scale=0.01` y `axis_forward='Z'`.

## Propuesta de zonas y enemigos (sin aprobar)
| Zona (propuesta) | Enemigos |
|---|---|
| Pradera del Despegue (Codex) | idea: globo gruñón (lo siguiente que haría) o una criatura de Antigravity |
| Mar de Nubes | **Nube gruñona** (hecha) |
| Tormenta | **Nubarrón de tormenta** (hecho) |
| Cielo alto / aurora | idea: cometa de papel enfadada |
| Espacio | **Ovni** y **Meteorito** (hechos) |

Solo objetos y elementos con cara (nubes, globo, cometa, ovni, meteorito): las criaturas enemigas quedan para Antigravity si sus monstruos son enemigos.

## Archivos para mirar
- `Enemigos-v01-hoja.jpg`: los cuatro juntos, en reposo y golpeados.
- `<enemigo>/previews/<Enemigo>-hoja.jpg`: frente con la regla de 6 studs, 3/4, cara, lateral, espalda, golpe, derrota y parpadeo.
- `<enemigo>/previews/<Enemigo>-Idle.gif`, `-Hit.gif` y `-Defeat.gif`.

## Cómo regenerar
`blender -b --factory-startup --python-exit-code 1 -P tools/build_enemigo_nube.py` (`NUBE_FASE=geo|check|full`, `NUBE_SOLO=nube-grunona|nubarron`) y `tools/build_enemigo_espacio.py` (`ESPACIO_FASE`, `ESPACIO_SOLO=ovni|meteorito`); después `tools/hoja_enemigos.py` para la hoja conjunta. Validación: `tools/validar_asset.py` (CLIPS Idle,Hit,Defeat,Blink; LOOPS Idle) y `tools/comprobar_malla.py`.
