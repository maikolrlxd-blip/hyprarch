# Estado del encargo "apocalipsis" (arte en Blender)

Pausado el 2026-10-22 a las 15:18, porque Maikol apaga el PC para cambiar la placa madre. Lo hace la sesión del PC (Claude, Coordinador de Codex). El encargo está en `ENCARGO.md`, que está en la rama de origin y aún no en esta copia local.

## Qué falla o falta (primero)
- **No hay todavía ningún modelo entregado.** No existen renders, FBX ni .blend de ninguna arma, del zombi ni del mapa.
- **Pistola:** `tools/build_pistola.py` está escrito completo, pero **nunca terminó de ejecutarse**. Lo paré en el paso de horneado por el apagado, así que **no está probado**. Puede fallar en el rig, los clips, la exportación o los renders. Hay que ejecutarlo, corregir y criticar.
- **Sin empezar:** escopeta, subfusil, zombi, mapa, `armas-animaciones.md` y `RESUMEN-NOCHE.md`.
- **Sin comprobar en Studio:** la escala de exportación aplica la corrección de Codex (FBX `global_scale=0.01`, medida por él con una roca en una copia de Studio). Todavía no la he comprobado con un arma.
- El login de GitHub (`gh auth login --web`) caducó sin completarse y no se subió nada.

## Qué está hecho y verificado
- `tools/ap_lib.py` es la librería común. Incluye:
  - geometría facetada con bmesh: caja, prisma por perfil, loft, banda, cilindro, torno, roca;
  - UV para varias piezas en un solo atlas;
  - horneado en Cycles de los mapas de datos: región, posición, normal, oclusión y bordes;
  - pintura a mano en numpy: pinceladas, manchas, desgaste de bordes, suciedad, óxido, polvo y luz pintada;
  - material mate final, rig con huesos rígidos, clips con interpolaciones, export FBX/GLB y render.
- `tools/ap_armas.py` añade brazos de viewmodel estilo R15, IK de dos huesos, `ClipDef` (las mismas partes en el modelo de mundo y en el viewmodel), hojas de contacto con rótulos y utilidades de export y render.
- `tools/test_pipeline.py` pasa entero en Blender 5.2.2 sin interfaz. Recorre geometría, UV, horneado, pintura, rig, 2 clips, FBX con clips, GLB y renders Eevee y Cycles. Las salidas de prueba están en `_prueba/`, que no se sube.
- **Rendimiento en este PC** (i7-6700, Intel HD 530): Cycles por CPU tarda 2 s y Eevee 22 s en el mismo render de 640x360. Para las vistas previas uso Cycles.

## Cómo retomar
1. Ejecutar: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P apocalipsis-arte\tools\build_pistola.py`. Tarda unos minutos: hornea a 2048 y renderiza unas 40 imágenes.
2. Revisar `armas/pistola-9mm/previews/`:
   - 4 vistas;
   - primera persona;
   - escala con un maniquí R15 de 5,2 studs y una regla de 6 studs;
   - hojas de contacto de los clips del viewmodel (Equipar, Disparo, Recargar, Reposo) y del modelo de mundo.
3. Criticar sin adornos, rehacer hasta 3 vueltas y escribir `armas/pistola-9mm/ESTADO.md` con "qué falla" primero y los triángulos.
4. Copiar los renders finales a `renders/` con nombres claros y hacer un commit local pequeño.
5. Seguir el orden: escopeta, subfusil, zombi, mapa. Al final, `armas-animaciones.md` y `RESUMEN-NOCHE.md`.

## Decisiones ya tomadas (para no repensarlas)
- **Unidades y ejes:** 1 unidad de Blender = 1 stud. Delante es +Y y arriba es +Z. El FBX sale con `axis_forward=-Z`, `axis_up=Y`, `global_scale=0.01` y `apply_scale_options=FBX_SCALE_ALL`, como validó Codex.
- **Tamaño de las armas:** está exagerado respecto a la realidad para que se lea en la mano de un R15. Pistola de 1,5 studs, subfusil de unos 2,7 y escopeta de unos 3,9. Hay que confirmarlo con Maikol.
- **Pistola (dibujo en mm, ver el script):**
  - piezas: Armazón (`Handle` en el FBX estático), Corredera con miras y cañón, Cargador, Gatillo y Casquillo;
  - el origen está en el centro de la empuñadura, en el punto (y=19,6 mm, z=70 mm) del dibujo;
  - presupuesto estimado de unos 520 triángulos (por medir);
  - textura de 1024 px, horneada a 2048 y reducida.
- **Rig de mundo:** el hueso raíz `Arma` lleva las partes móviles (Corredera, Cargador, Gatillo, Casquillo), cada una con peso 1.
- **Viewmodel:**
  - jerarquía `Camara` → `Arma` → partes, y brazos R15 (`RightUpperArm`/`LowerArm`/`Hand` y los mismos `Left…`) colgados de `Arma`;
  - la cámara mira +Y con un campo de visión vertical de 70°;
  - origen del arma en la cámara: pistola (0.42, 1.40, -0.62).
- **Clips:** a 60 fps, con los nombres exactos `Equipar`, `Disparo`, `Recargar` y `Reposo` (en bucle). En la escopeta, además, `Bombear`, `Recargar_Inicio`, `Recargar_Cartucho` (en bucle por cartucho) y `Recargar_Fin`.
  - Se exporta por arma un FBX de mundo y otro de viewmodel con todos los clips, más un FBX por clip en `clips/`.
  - También un FBX estático con las piezas separadas y GLB estáticos.
  - Los casquillos esperan escondidos dentro del arma, porque Roblox no anima la escala.
- **Escopeta (diseño pendiente de escribir, en mm, total 990, X×1.25 para que sea gruesa):**
  - culata de madera y cantonera;
  - cajón de mecanismos de 330 a 560 con ventana de expulsión a la derecha y ventana de carga abajo, hecho por segmentos;
  - cañón r13 en z50 con alza de bola, tubo de cargador r12 en z22, abrazadera en y907 y bomba de madera de 610 a 800 que retrocede 90 mm;
  - cartucho rojo con base de latón y casquillo expulsado;
  - origen en la empuñadura (y290, z-20);
  - en el viewmodel, G≈(0.36, 0.45, -0.62), y el brazo izquierdo llega a la bomba (brazos de unos 2,7 de largo).
- **Subfusil (pendiente):**
  - estilo MP5 genérico con culata fija tipo A2;
  - cargador curvo separado y palanca de carga arriba a la izquierda (se tira y se suelta de golpe en `Recargar`);
  - `Disparo` de 0,1 s para el fuego automático.
