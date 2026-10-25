# LUTO / quemado — copia local de Studio

Estado 25/10/2026: seis comprobaciones pasadas en motor, botones Inicio/Bucle/Caída y chorro pulsados en Play, dos capturas reales nuevas. Prueba de presentación aislada; no es el lanzallamas jugable.

## Archivos y reproducción

Lugar observado: `C:/Users/maiko/Documents/Codex/2026-10-21/c/work/luto-fire-engine-qa/LUTO-Quemado-QA-03.rbxl`. También se entrega como `copia-QA/LUTO-Quemado-QA-03.rbxl` en el ZIP de esta revisión. Abrir esa copia y pulsar Play: prepara los clips, ejecuta seis comprobaciones y luego habilita botones. No guardar sobre `Documents/Luto/Luto-jugable.rbxl`.

`Preparar.server.lua` clona el mapa y la plantilla de zombi que ya existían en el lugar; CharacterAutoLoads=false. `Prueba.client.lua` crea tres zombis locales con raíz anclada, sin colisión, carga los clips y mide rendimiento. Los seis scripts originales están deshabilitados solamente en esta copia. Se conservan los 15 MeshParts originales de la zombi, sus MeshId, TextureID y Size. El arma no aparece: el botón dice «CHORRO VFX (sin arma)».

`exportar_clips.py` lee el .blend existente de `zombi-mujer/animaciones-quemado-v01` en un Blender background nuevo (máximo tres hilos). Reinicia pose por acción y convierte ejes Blender X/Y/Z a Roblox X/Z/-Y. Genera `datos/clips.json` y `Quemado-local.rbxmx`: Inicio 27 claves/0,85 s; Bucle 37/1,2 s; Caer 55/1,8 s. El movimiento del HRP se incorpora a LowerTorso para conservar la caída en el rig Motor6D. Solo Bucle se exporta con Loop=true. No modifica el Blender original.

`construir.lua` y `validar_copia.lua` son herramientas rbxmk de esta máquina, con rutas explícitas. Se ejecutan desde `C:/Users/maiko/Documents/Codex/2026-10-21/c`, con acceso a ese work y al repo. La construcción necesita `Luto-audit-uncompressed.rbxl`, copia descomprimida del binario nativo Zstandard para rbxmk antiguo. No reconstruir encima de QA03 sin protegerla y revisar cambios nativos. El ZIP incluye una QA03 lista para abrir, así no depende de reconstrucción.

Los clips usan `KeyframeSequenceProvider:RegisterKeyframeSequence` en Studio: IDs temporales, no publicación. Referencia: https://create.roblox.com/docs/reference/engine/classes/KeyframeSequenceProvider

## Evidencia y límites

- `runtime-03-2026-10-25.log`: todo el Output LUTO_FIRE_QA de esta ejecución. `runtime-01/02` son historial del 24/10, no el estado final.
- `VALIDACION-MOTOR.json`: resultados, SHA de la copia, FPS y límites. Se midieron 7/9/11 articulaciones con movimiento; descenso de LowerTorso -2,28644 studs, evaluado tras dos RenderStepped.
- `previews/*MOTOR.png`: fotos de Roblox Play, no Blender. Izquierda de pantalla: caída; centro: bucle; derecha: inicio. Los botones identifican el clip, no la posición espacial.
- `UI_HOLD.rootY` se registra inmediatamente tras buscar el final del clip y puede ser del fotograma anterior; no usarlo como medición de la pose final. La comprobación `fall_root_translation` sí espera al Animator. Los botones de inicio/caída hacen un bucle temporal y congelan la última pose SOLO para esta demostración; no es lógica de muerte.
- Primera revisión: emisores poco legibles; segunda: corrección visual del fuego y descenso; tercera: reproducir/congelar poses sin depender de que el track siga activo al final con FPS bajos. Repetición manual de Caída y permanencia visual comprobadas.
- No se verificó contacto físico exacto contra suelo, IA, daño, interrupciones en combate, viewmodel, animaciones del arma en motor, audio, carbonización, multijugador ni móvil.

Rendimiento observado: 43,23 FPS base / 41,98 con fuego en las mismas tres zombis animadas. P95 38,72 / 37,96 ms. Cada muestra dura unos 5 s; viewport 1096×635, un cliente, no combate. No extrapolar a hordas ni FPS del juego terminado.

Aviso ajeno a las comprobaciones: `ContentId: rbxassetid://203785492 failed due to: Asset type does not match requested type`. También apareció antes de Play, sin avatar cargado. Ese ID no está en el XML auditado ni en las fuentes nuevas; origen exacto no demostrado. El registro previo que lo atribuía a Studio no prueba qué componente lo solicita. Rojo también intentó conectarse a su servidor local ausente; no se alteró su configuración.

Al acabar: Play detenido, un Studio conservado editando la copia QA03, sin guardar sobre el lugar entregado. No publicar esta copia: contiene helpers de prueba y el juego está deshabilitado.
