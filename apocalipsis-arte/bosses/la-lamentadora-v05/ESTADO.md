# La Lamentadora v05b — movimiento y Lamento

24/10/2026. Trabajo nocturno pedido por Maikol. Parte de una copia de v04, cuyo rostro y acabado Poli Pintado se preservan exactamente.

- 2926 triángulos y 15 mallas, sin aumentar geometría. 38 huesos: 16 originales y 22 para 11 mechones. Máximo dos influencias activas por vértice en esta revisión.
- Movimiento secundario del cabello horneado en los cuatro clips anteriores. No es simulación física en tiempo real.
- Nuevo **Lamento de 2,8 s**: anticipación 0–0,78, grito 1,10–1,65, recuperación hasta 2,8. Sin audio ni daño. Son momentos de animación; el servidor del juego debe decidir el combate.
- `.blend`, FBX skinned completo, cinco clips FBX, GLB skinned con cinco acciones y FBX estático. Cuatro atlas v04 conservados.

## Verificación
`qa/VALIDACION-BLENDER.json`: pasada, geometría/UV/pesos/pose neutral/texturas y reimportación de estático, skinned, Caer y Lamento. `qa/VALIDACION-MOVIMIENTO.json`: pasada, geometría y UV idénticas a v04, 325 vértices de mechones que se mueven independientemente, rostro sin deformación por el cabello (error numérico <0,000003 studs), cinco acciones y 38 huesos al reimportar GLB. Lamento muestreado en todos sus fotogramas enteros: mínimo Z +0,020637.

La primera pasada detectó -0,003363 studs de penetración de la suela neutral. Se respaldó en `work/backups/Lamentadora-v05-before-floor-fix.zip` y se corrigió con margen constante de raíz de 0,024 studs; no se cambió la malla. Usar imágenes **v05b**, no v05 sin b.

La secuencia v05b fue inspeccionada visualmente. Tiene anticipación y recuperación claras. El lamento no anima labios/mandíbula: conserva la boca abierta de v04. La amplitud y la naturalidad del pelo todavía necesitan feedback en movimiento continuo. Sin afirmar aprobación visual del usuario.

## Integración pendiente
**Sin probar en Roblox.** Los huesos de cabello requieren importar el rig skinned. El helper de Motor6D estático de v04 no reproduce estos pesos y no debe emplearse para afirmar que esta revisión está integrada. El estático es referencia/fallback sin pelo animado. Escala, Animator, transición entre clips y colisiones del motor pendientes. No se publicaron IDs ni se controló Studio.

Fuente reproducible: `fuentes/build_motion.py` sobre `fuentes/Base-v04.blend` protegido por SHA en `datos.json`. Renders reales: `previews/Lamentadora-v05b-Lamento-*-Blender.png`. Paquete y SHA externos en outputs; manifiesto interno.
