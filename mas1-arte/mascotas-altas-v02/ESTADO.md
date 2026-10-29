# Mascotas altas v02 — águila legendaria, grifo mítico y fénix (Robux)
Hechas por el Coordinador (Claude en el PC de Maikol) el 29/10/2026. **Sustituyen a la v01**, que Maikol rechazó con «se ve feo y buguiado». Blender 5.2.2; `tools/build_mascota_aguila.py`, `build_mascota_grifo.py` y `build_mascota_fenix.py`, sobre `mas1_lib.py`, `mas1_pet.py` y `mas1_ave.py`.

## Fallos y límites (primero)
1. **Nada probado en Roblox**: importación del FBX, huesos como `Bone`/`Motor6D`, clips, escala y ejes. Lo único comprobado es Blender (renders) y la reimportación de los FBX/GLB en Blender (`VALIDACION.json` de cada carpeta: correcta). Maikol denegó el acceso de control a Studio.
2. **Eje del FBX sin confirmar con rig**: mis modelos miran a +Y en Blender y salen con `axis_forward='Z'` (variable `FBX_FORWARD`); los de Codex miran a −Y y salen con `'-Z'`. Deberían entrar igual; si entran girados 180°, cambiar a `'-Z'` y regenerar.
3. **Qué estaba mal en la v01 y por qué se rehízo** (lo vio Maikol, lo comprobé en mis propios renders): alas de persiana (tablas planas apiladas), cola del águila como una tabla suelta que sobresalía, penacho del grifo flotando fuera del cuerpo, cresta del fénix con cubos sueltos, hombros dorados como barras sueltas y, en la variante con contorno negro, líneas negras sueltas dentro del pecho. En esta versión todo eso está rehecho (ver «Qué cambió») y hay dos comprobaciones automáticas: piezas sueltas y caras que se pisan.
4. **Sin contorno negro**: al volver a mirar los iconos de Roba un huevo, el contorno grueso lo llevan las mascotas comunes y medias; las raras (cordero alado, pavo real, arcángel, pegaso…) no. Estas tres son de rareza alta, así que no lo llevan. `tools/contorno_negro.py` sigue ahí para las comunes si Maikol las quiere con contorno.
5. **Más pesadas que las comunes de Codex**: 3.974 / 4.446 / 4.382 triángulos (las suyas, 1.664–1.908), por las escamas en relieve y las plumas sueltas (183–192 piezas sueltas). Son las raras; si pesan en móvil, las escamas se quitan quitando las llamadas a `escamas(...)` (≈ 90 plaquitas, ≈ 900 triángulos).
6. **Piel rígida por hueso** (una malla, cada vértice sigue un solo hueso): sin huecos en los clips, pero la mano entera gira como un bloque: el abanico no se cierra como abanico, la mano se pliega entera hacia atrás.
7. **Ojos pequeños con brillo** (referencia Roba un huevo) frente a los **ojos grandes y blancos del gorrión v04 de Codex**: la familia no está unificada; hay que decidir cuál vale para todas.
8. **Alturas**: 4,31 / 4,43 / 5,25 studs frente a los 5,2 del R15: son «altas» como pidió el encargo, pero no se probó la distancia a la que flotan junto al jugador.
9. **Fénix**: el fuego va aparte (partículas); `datos.json` de `fenix/` trae `puntos_fuego` (cresta, puntas de ala y de cola, pecho) y el hueso al que atar cada emisor.
10. **Textura**: atlas 1024, un material, bordes de las islas UV sangrados 5 texeles para que el filtrado de Roblox no dibuje líneas oscuras entre caras; sombras frías (lavanda) en águila y grifo, cálidas en el fénix.
11. Sin las mascotas comunes poco comunes / raras (2 + 2): las hace Codex; si no llega, las hago yo (orden del encargo).
12. **Pendiente (comentario de Maikol, 29/10, tras ver la v02): los pies están muy tiesos; al volar deben guindar.** Hoy las patas son parte del hueso `Body` (rígidas, de pie). Plan: huesos `Leg_R/Leg_L` (rig de 10 huesos), patas colgando en la pose neutra y péndulo suave con el aleteo en `Fly`, más rectas en `Glide`, patadita en `Celebrate`; regenerar y revalidar las tres.

## Qué cambió respecto a la v01
- **Proporciones**: cuerpo rechoncho y cabeza grande (celda de 0,2 studs, volúmenes escalonados como los de Codex), patas cortas, ojos diminutos con brillo, ceja fiera, pico ancho en gancho.
- **Escamas de plumas en relieve** pegadas a las caras de los voxeles (pecho en tresbolillo, flancos y espalda al azar), como las de cisne, búho y terrorbird de Roba un huevo. Nada flota: `piezas_sueltas()` da 0 en las tres.
- **Alas en arco** (dihedro y barrido en el hueso del ala y otro en la mano): brazo, seis secundarias, dos filas de cubiertas y siete u ocho primarias en abanico; cada pluma es una pieza plana con grosor, **a su propia altura** (nunca coplanares: `caras_coplanares()` da 0 en las tres), con bandas de color que acaban en la punta dorada. Rombos dorados en el brazo y en el pecho.
- **Cola unida al cuerpo**: abanico levantado de cinco plumas (águila), cola de león con borla violeta y plumas en llama (grifo), siete plumas largas de dos tramos que se curvan (fénix).
- **Aleteo corregido por Maikol (recoger → extender → impulsar → recoger)**: `ALETEO` en `mas1_pet.py`. Arriba extendidas; el empuje baja el ala con la punta retrasada (más arriba que el hombro); abajo empieza a recoger: la muñeca y la mano flexionan hacia atrás mientras suben; arriba se extienden otra vez. El cuerpo sube con el empuje y la cola cabecea. `Celebrate` es el mismo ciclo, más amplio y con cabeza y cola.

## Qué hay (cada carpeta: `aguila-legendaria/`, `grifo-mitico/`, `fenix/`)
- `<Nombre>_Rig.fbx` (malla + 8 huesos, pose neutra con las alas en arco), `clips/<Nombre>_{Fly,Glide,Celebrate}.fbx` (mismo rig, animación bakeada a 30 fps), `<Nombre>.glb` con los tres clips y `<Nombre>.blend`. Huesos `Root, Body, Head, Tail, Wing_R/L, Tip_R/L` como las comunes de Codex.
- Clips en bucle (la última clave repite la primera; diferencia 0,0 al reimportar): `Fly` 1,0 s, `Glide` 2,0 s, `Celebrate` 2,0 s.
- `previews/`: frente con regla de 6 studs, 3/4, lateral, espalda, desde arriba, cara, aleteo arriba/abajo/recogiendo, planeo, celebrar, hoja de contacto, **secuencia del aleteo en 6 poses** y GIF del `Fly`. Todos con el maniquí R15 de 5,2 studs. `../Mascotas-altas-v02-hoja.jpg` junta las tres.
- `datos.json` (triángulos, límites, paleta, huesos, piezas sueltas y caras coplanares, escamas), `VALIDACION.json` (reimportación de FBX y GLB) y `COMPROBACION_MALLA.json`.

## Medidas y validación (reimportando los FBX/GLB en Blender)
| Pieza | Triángulos | Envergadura × alto × largo (studs, reposo) | Razón plegada/extendida `Fly` | `Glide` | `Celebrate` | Piezas sueltas | Caras coplanares |
|---|---:|---|---:|---:|---:|---:|---:|
| Águila legendaria | 3.974 | 8,1 × 4,31 × 4,91 | 0,564 | 0,945 | 0,548 | 0 | 0 |
| Grifo mítico | 4.446 | 8,48 × 4,43 × 6,0 | 0,549 | 0,943 | 0,533 | 0 | 0 |
| Fénix | 4.382 | 8,79 × 5,25 × 6,04 | 0,526 | 0,936 | 0,508 | 0 | 0 |
La razón es el ancho en X de la malla deformada en cada fotograma, mínimo entre máximo (la mide `tools/validar_asset.py`). Las mascotas comunes de Codex miden ≈ 0,56. Las seis poses del aleteo (`*-aleteo-secuencia.jpg`) enseñan el ciclo.

## Regenerar y validar
```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P mas1-arte\tools\build_mascota_aguila.py   (~10 min con renders; MASCOTA_FASE=geo: geometría rápida; MASCOTA_FASE=assets: sin renders, ~3 min; MASCOTA_FASE=check: solo comprobaciones)
set ASSET_DIR=mascotas-altas-v02/aguila-legendaria & set ASSET_NAME=AguilaLegendaria & set ASSET_CLIPS=Fly,Glide,Celebrate & set ASSET_LOOPS=Fly,Glide,Celebrate
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P mas1-arte\tools\validar_asset.py
set MALLA_BLEND=mascotas-altas-v02\aguila-legendaria\AguilaLegendaria.blend
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P mas1-arte\tools\comprobar_malla.py
```
Lo mismo con `build_mascota_grifo.py` (`GrifoMitico`) y `build_mascota_fenix.py` (`FenixDeFuego`). `tools\hoja_mascotas_altas.py` rehace la hoja de las tres; `tools\animar_preview.py` los GIF.

## Para probarlo en Studio (pendiente de permiso de Maikol)
1. Importador 3D con `<Nombre>_Rig.fbx`: debe entrar 1 MeshPart con 8 huesos, textura 1024 y la mascota mirando hacia delante (frente = el lado del pico).
2. Animaciones: importar los FBX de `clips/` con el mismo rig y reproducir `Fly`/`Glide`/`Celebrate` en bucle.
3. Fénix: colocar `ParticleEmitter` en los `puntos_fuego` de su `datos.json`.
