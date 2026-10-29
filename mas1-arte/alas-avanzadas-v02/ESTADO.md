# Alas avanzadas v0.2 — oscuras con turquesa y pinchos (estilo Codex)
Hechas por el Coordinador (Claude en el PC de Maikol) el 29/10/2026, tras el «usa el estilo de Codex, esas alas están feas, q las haga el coordinador». Modelo propio, no el abanico de prismas de v0.1. Blender 5.2.2, `tools/build_alas_avanzadas_v02.py`.

## Fallos y límites (primero)
1. **Nada probado en Roblox**: importación del FBX, rig como huesos, clips, orientación y acople a `BodyBackAttachment`. Lo único comprobado es Blender (renders) y la reimportación de los FBX/GLB en Blender (`VALIDACION.json`: correcta). Maikol denegó el acceso de control a Studio, así que no he podido probarlo.
2. **Eje del FBX sin confirmar con rig**: el frente es +Y en Blender y exporto con `axis_forward='Z'` (variable `FBX_FORWARD`). Con mallas sueltas de Luto, `-Z` entraba girado 180°. Si las alas entran giradas, cambiar a `'-Z'` y regenerar.
3. **La imagen de referencia de Maikol no está como archivo.** Me guié por las «alas oscuras» de ForgeGUI (arco óseo con espinas, plumas largas en capas) y por la paleta oscuro/turquesa del encargo. Si la imagen real difiere, hay que ajustar.
4. **Más pesadas que las de Codex**: 2.868 triángulos y 1.848 vértices (las suyas, 1.168 y 1.796 triángulos). 7 huesos (`Mid` es nuevo; Codex usa 2 por ala).
5. **Plegadas no es un abanico cerrado**: la pose de `Deploy` T=0 salió de `tools/buscar_pliegue_alas.py` (cinemática directa en numpy + búsqueda sobre los 9 giros) y mide ±1,48 studs de ancho, 2,6 por detrás del montaje y de z −3,69 a +2,66 (el suelo del maniquí está en −3,8), sin entrar en el torso. Pero con piezas rígidas las cuatro filas siguen siendo cuatro filas: desde atrás se ve una hoja oscura con los cuernos arriba, no un abanico cerrado. Mi primer pliegue (barrido a mano) salía 4,5 studs hacia atrás y atravesaba el torso; las poses con las dos alas cruzadas en X se descartaron.
6. **Piel rígida por pieza** (cada pluma sigue un solo hueso): en los clips no se ven huecos, pero con giros de `Mid`/`Tip` mayores de ±35° aparecerían cortes entre grupos.
7. **Aleteo hacia abajo limitado a +14°** (arriba hasta −30°): más abajo las plumas interiores de las dos alas se cruzan en el centro de la espalda.
8. **Perfil lateral de lámina fina** (como casi todas las alas de accesorio); la profundidad total es 1,8 studs.
9. **Turquesa**: ya no es neón como en v0.1, pero las puntas de las primarias siguen siendo lo más vivo; se baja en una línea de `PAL` (`punta`).
10. No probado con el torso R6 ni con ropa por capas. El origen es el punto de montaje: la placa dorsal toca la espalda (y = −0,04) y las alas quedan detrás.

## Qué hay
- `AlasAvanzadas_v02_Rig.fbx` (malla + 7 huesos, pose neutra) y `clips/AlasAvanzadas_v02_{Deploy,Flap,Glide}.fbx` (el mismo rig con cada animación bakeada a 30 fps). `AlasAvanzadas_v02.glb` con los tres clips (para verlas fuera de Blender) y `AlasAvanzadas_v02.blend` (227 KB).
- Una malla, un material, atlas 1024 (`texturas/AlasAvanzadas_paleta_1024.png`), un solo hueso por vértice.
- Medidas en reposo: envergadura 9,99 studs, alto de −3,39 a +3,15 (con el montaje a 3,8 studs del suelo del maniquí R15 de 5,2), fondo 1,84. Origen = punto de montaje en la espalda; +Y delante, +Z arriba.
- Huesos: `Root`, `Wing_R/L` (hombro), `Mid_R/L` (codo), `Tip_R/L` (muñeca; lleva la mano, las primarias, el cuerno y la garra).
- Clips (30 fps): `Deploy` 1,2 s (36 fotogramas; parte plegada, se cierra un poco más como anticipación, abre de golpe, rebota y se asienta en la pose de `Glide`), `Flap` 0,9 s en bucle (27; la mano va retrasada 0,14 s, el cuerpo sube con la bajada), `Glide` 2,4 s en bucle (72). Los dos bucles cierran (diferencia 0,0 entre el primer y el último fotograma, comprobado al reimportar).
- Medido sobre la malla deformada: abiertas en reposo ±5,0 de ancho; en el aleteo llegan a ±6,0 de ancho y de −4,2 a +4,2 de alto; en el rebote de `Deploy` ±6,2.
- `previews/`: espalda con regla de 6 studs, 3/4, lateral, de frente, detalle del brazo, plegadas, aleteo arriba/abajo, planeo, secuencia de Deploy en 6 fotogramas y hoja de contacto. Todos con el maniquí de 5,2 studs.

## Crítica contra lo que pidió el director sobre v0.1
- **Pinchos** (antes: un espolón por ala): ahora 7 espinas por ala sobre el arco, cuerno curvo en la muñeca, garra en la mano y corona de 3 espinas en la placa. ✔
- **Rígidas y simétricas**: el arco óseo es hexagonal, afinado y con codo, las plumas son lanceoladas con largos irregulares (±7 %) y cuatro filas en capas (cubiertas, secundarias, primarias y las largas de debajo). Sigue siendo simétrica de izquierda a derecha (es un accesorio). ✔ a medias
- **Turquesa menos neón**: oscuro azulado con puntas que se aclaran de dentro afuera (3 tonos) y anillos con gema. Ver fallo 9. ✔ a medias
- **Deploy que de verdad pliegue**: empieza recogida y no abierta. Ver fallo 5. ✔ a medias
- **Cuerpo visible**: las plumas interiores son cortas; desde atrás se ven la espalda y las piernas.

## Regenerar y validar
```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P mas1-arte\tools\build_alas_avanzadas_v02.py   (~9 min)
set ASSET_DIR=alas-avanzadas-v02 & set ASSET_NAME=AlasAvanzadas_v02 & set ASSET_CLIPS=Deploy,Flap,Glide & set ASSET_LOOPS=Flap,Glide
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P mas1-arte\tools\validar_asset.py
```
`ALAS_FASE=geo` solo hace la geometría con colores planos y renders rápidos. La pose plegada se busca con `tools\buscar_pliegue_alas.py` (lee el .blend y solo imprime candidatas).

## Para probarlo en Studio (pendiente de permiso de Maikol)
1. Importador 3D con `AlasAvanzadas_v02_Rig.fbx`: debe entrar 1 MeshPart con 7 huesos, textura 1024, envergadura ≈ 10 studs y las alas en +Z (detrás; el frente del personaje es −Z).
2. Acople: Accessory con ese MeshPart como `Handle` y un `Attachment` llamado `BodyBackAttachment` en su origen.
3. Animaciones: importar los FBX de `clips/` con el mismo rig.
