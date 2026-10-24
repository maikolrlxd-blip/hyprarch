# Kit de hospital v01 — LUTO / Poli Pintado

24/10/2026. Tercer bloque acotado del trabajo nocturno autorizado por Maikol. Tres objetos ambientales originales en Blender, separados del mapa existente:

| Objeto | Triángulos | Tamaño fuente aproximado (ancho/fondo/alto, studs) |
|---|---:|---|
| Camilla | 792 | 2,93 × 6,25 × 3,35 |
| Biombo | 816 | 5,61 × 1,66 × 5,75 |
| Soporte de suero | 476 | 1,85 × 1,92 × 5,69 |

Un atlas mate de 512 por objeto, dentro del presupuesto de 1500 triángulos por pieza. Camilla con ruedas, barandillas, correas y almohada; biombo de tres secciones, tela continua con pliegues geométricos y dobladillo desigual; soporte con bolsa estilizada y tubo recogido. Paleta verde grisácea, metal gastado, pinceladas y suciedad. Sin sangre ni detalle fotográfico. Ningún componente mecánico funcional.

`Hospital.blend` contiene la composición de revisión y los atlas empaquetados. Cada FBX/GLB de `fbx/` se exportó individualmente desde origen local; piso, cámaras y luces no están incluidos en las piezas. Las fotos de `previews/` son renders Blender, no capturas del juego.

## Comprobaciones y límites

`qa/VALIDACION.json` PASADA: seis reimportaciones (tres FBX y tres GLB), conteos, UV, ausencia de vértices sueltos/triángulos degenerados, texturas y límites. Revisión visual del conjunto realizada. **Sin Roblox, colisiones, escala de importador ni FPS verificados.**

El exportador heredado del proyecto usa `global_scale=0.01` en FBX. Al reimportar en Blender vacío, las medidas crudas FBX son 1/100 de las del GLB. La prueba informa medidas crudas y normalizadas por 100; no oculta esta diferencia ni afirma que el importador Roblox la resuelva automáticamente. Medir contra avatar/figura de seis studs antes de distribuir. No se modificó la convención del resto del proyecto.

Pendiente: una copia temporal de Studio, escala/orientación y colliders simples de camilla/biombo; tubo, bolsa y correas sin colisión. Mantener paso libre y usar una densidad moderada. No hay objetos instalados en el mapa, interacción, ruedas físicas ni animaciones. Se evitó tocar escenas y código compartidos.

Fuentes congeladas en `fuentes/`, datos en `datos.json`. La primera construcción se detuvo al solicitar un material ausente en una pieza: ahora pinta solo regiones existentes. El primer chequeo de escala detectó la convención FBX anterior; el informe final la hace explícita. No se regeneraron fotos para cambiar resultados de QA.
