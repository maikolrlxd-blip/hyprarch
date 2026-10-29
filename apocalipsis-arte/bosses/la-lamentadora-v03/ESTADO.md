# La Lamentadora v03 — revisión visual de Codex

## Qué falta
- Revisión visual de Maikol: quiere una mezcla de mujer reconocible y deformación profunda, aterradora, conservando **Poli Pintado** (`taller-ia/ESTILO.md`). Esta entrega es una propuesta para comparar, no arte aceptado.
- No probada ni importada en Roblox. La plantilla que Claude importó corresponde a v02, no a esta revisión.
- El cabello sigue unido a Head. Todavía no tiene movimiento independiente ni clip de lamento propio.
- Contacto geométrico de Caer corregido en Blender; la calidad completa del movimiento y las colisiones del juego necesitan revisión separada.
- Cuerpo/ropa conservan mucha estructura de la zombi original. La identidad final de la jefa aún debe cerrarse con las imágenes.

## Cambios
- Parte de la v02 de Claude, protegida y sin modificar. Nueva cabeza de 1368 triángulos con cuencas y boca interiores, mandíbula desviada y nariz modelada.
- Cabello con mechones afinados, curvados y distintos entre sí; tinte oscuro frío.
- Manos con palma, pulgar y cuatro dedos separados, uñas cortas apagadas.
- Cuello ligeramente alargado y adelantado, postura encorvada y cabeza inclinada.
- Acabado mate, paleta de luto, texturas pintadas a partir de la canalización original del proyecto. No usa PBR fotográfico ni imagen generada.
- Conserva 15 piezas y 16 huesos del esquema R15. Total **2824 triángulos**, dentro del presupuesto de 3000.
- Corrige guardado neutral: v02 conservaba en memoria la pose Caer aunque su acción estaba desasignada. Ahora se limpian las transformaciones antes de medir, guardar y exportar el estático.

## Imágenes vigentes
Las vistas `LaLamentadora_v03b_*.png` son renders Blender de la revisión con texturas. `Lamentadora-v03b-01-rostro-forma-Blender.png` solo muestra geometría con materiales provisionales.

Las imágenes sin `v03b` son diagnósticos anteriores. La primera pasada contenía un error al restaurar materiales tras el render de forma: `materials.clear()` puso a cero los índices de las caras. Se corrigió sustituyendo los slots en su lugar. No presentar esa pasada como actual. Copia anterior en `work/backups/Lamentadora-v03a-before-material-fix.zip` del workspace Codex.

## Archivos y alcance
- `LaLamentadora.blend`: escena editable con texturas empaquetadas.
- `LaLamentadora.fbx`, `_Estatico.fbx`, `_Estatico.glb` y `clips/`: exportaciones locales.
- `fuentes/build_lamentadora.py`: generador de esta copia; `prepare_revision.py` reproduce las modificaciones sobre la fuente v02 congelada. `boss_head.py` y `clip_contacts.py` contienen las revisiones específicas.
- `qa/CONTACTO-CAIDA.json`: muestreo cada cuarto de fotograma de la geometría evaluada. Alcance solo Blender.
- `qa/VALIDACION-BLENDER.json`: validación independiente PASADA: 15 mallas / 16 huesos / 2824 triángulos, UV finitas dentro de 0–1, sin vértices sueltos ni triángulos degenerados, pesos completos, cuatro texturas empaquetadas y cuatro acciones conservadas. Reimportación de FBX estático, rig y Caer pasada. Esto no equivale a Play.
- FBX mantiene la conversión `.01`, ejes -Z/Y. GLB conserva su convención distinta; escala e integración deben comprobarse en Studio.

No se publicaron assets, animaciones ni juego. No se abrieron ni tocaron ventanas de Studio. Los modelos v01/v02, las plantillas del juego y el código de Slime Rush se conservaron.

## Seguimiento visual acordado con Maikol
Mostrar imágenes reales de Blender en cada cambio importante para que indique qué funciona y qué hay que corregir. No pasar a armas o mapa antes de cerrar la dirección visual de esta jefa. El 23/10 pidió explícitamente combinar una apariencia humana con deformación profunda, manteniendo el estilo documentado del proyecto.
