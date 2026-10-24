# Lanzallamas v01b — LUTO / Poli Pintado

24/10/2026. Modelo original de videojuego en Blender, siguiendo la petición de Maikol de incluir todas las animaciones. Arma de 390 triángulos, tres piezas (Handle, Cartucho, Cierre), atlas 1024. Primera persona: 646 triángulos incluyendo los brazos R15, atlas de brazos 512. Acabado mate oliva, metal azulado, marcas de desgaste, cartucho rojo apagado y franjas de seguridad.

## Entrega

- Blender con ambos rigs en pose neutral; Mundo: tres huesos, VM: diez.
- FBX Mundo y VM, FBX/GLB estáticos con nombres exactos y 12 FBX individuales: seis clips para cada rig.
- Equipar 0,85 s; Guardar 0,65 s; Reposo 2 s; Disparo sostenido 0,60 s; Recargar 2,8 s; Inspeccionar 3,2 s.
- Recarga con cartucho retirado y recolocado, mano de apoyo y cierre. Inspección gira ambos lados. Eventos temporales y punto Boca en JSON/Lua; no hay IDs publicados.
- `integracion/QuemadoFX.lua`: efecto cosmético local de boquilla y quemado de NPC, apagado y limpieza. Animaciones de zombi en `../../zombi-mujer/animaciones-quemado-v01/`.

## Comprobado

`qa/VALIDACION.json` PASADA: geometría, UV, pesos, rig neutral, texturas empaquetadas, reimportación FBX/GLB estáticos y los 12 clips FBX con duraciones correctas. Las seis imágenes principales y hojas de equipar/guardar/recarga/inspección fueron revisadas en Blender. Son fotogramas seleccionados, no prueba de todas las transiciones a velocidad real.

`qa/VALIDACION-FX-MOCK.json`: siete casos de ciclo de vida del módulo real con objetos simulados: encender/apagar, limpieza idempotente, objetivos inválidos, renovación sin acumulación, retirada del NPC, duración acotada y limpieza explícita. También compilaron `QuemadoFX.lua` y `Lanzallamas_Eventos.lua` con Luau. **No es Play ni render de ParticleEmitter.**

El control adicional de los bucles detectó una diferencia de giro de 0,0084 grados en el cierre de Disparo; se hizo periódico y se reexportaron únicamente ese clip, los maestros y el editable. La revisión final también verifica ambos maestros con seis acciones y coincidencia de extremos en Reposo/Disparo. Los renders siguen vigentes porque no muestran Disparo. Respaldo `Lanzallamas-before-loop-seam-fix.zip`.

FBX conserva la convención del exportador del proyecto (`global_scale=0.01`); GLB conserva unidades fuente. Confirmar escala contra referencia en el importador de Roblox, sin asumir equivalencia por el aspecto de las fotos.

La primera exportación interpretaba al revés el perfil radial de la boquilla/cartucho: quedó respaldada en `work/backups/Lanzallamas-v01-before-profile-fix.zip`. Usar exclusivamente fotos **v01b**. Otra copia protege los estáticos anteriores a corregir sus nombres. Los fuentes actuales reproducen ambas correcciones.

## Pendiente real

Sin integración Roblox, sonido, daño, combustible, compras ni guardado. Falta importar rigs/clips y probar agarre, cancelación de inspección/recarga, apagar al guardar/morir, fuego con varios NPC, muerte por autoridad del servidor y FPS. No se modificó el código compartido de combate/Viewmodel. `CONTRATO.md` explica eventos, cancelaciones y límites. No se publicó ni se hizo push.
