# Pistola 9mm — estado

Versión v5, del 2026-10-23. Maikol congeló el diseño («Ya déjale las armas así»): desde la v4 solo hay correcciones de errores, animaciones y la exportación para el código.

## Qué falla
- **Recarga en primera persona:** al montar la corredera, entre 1,13 y 1,25 s, la manga izquierda todavía cubre media pantalla. Con mangas más finas y el arma más baja mejoró, pero no del todo.
- **Cargador en la recarga:** se ve el gesto de la mano, pero el cargador nuevo queda en parte tapado por la mano.
- Por el puerto de expulsión se ve un bloque de latón liso. Es el casquillo, que va escondido en la recámara porque Roblox no anima la escala.
- Las manos del viewmodel son bloques estilo R15, sin dedos.
- **No probado en Roblox Studio:** la importación de los clips con el Animation Editor ni el Tool.

## Qué funciona
- **Sin pared negra.** Era un fallo de triangulación (la normal de la cara no se calculaba) y está arreglado en `ap_lib`.
- Viewmodel más cerca y centrado.
- La vista de escala tiene la pistola en la mano del R15, con el brazo hacia delante (pose de Tool).
- **Inspeccionar (3,30 s)**, según la descripción de Maikol:
  - diagonal a la derecha;
  - diagonal a la izquierda;
  - brazo estirado con la pistola de lado, estilo gánster, con pausa;
  - vuelta al reposo.
  La mano izquierda baja fuera de cuadro. En el modelo de mundo la pistola solo gira en la mano.
- **Eventos y puntos** para el código, en `eventos.json` y `Pistola9mm_Eventos.lua`.

## Triángulos
Armazón 176, Corredera 260, Cargador 72, Gatillo 60 y Casquillo 66: **634 en total**. Los brazos del viewmodel van aparte.

## Clips (mundo y viewmodel)
| Clip | Duración |
|---|---|
| Equipar | 0,80 s |
| Disparo | 0,25 s |
| Recargar | 1,70 s |
| Reposo | 2,00 s, en bucle |
| Inspeccionar | 3,30 s |

## Vueltas
1. **v1:** oscura y plana.
2. **v2:** corredera cromada y 890 triángulos.
3. **v3:** 634 triángulos y viewmodel que deformaba bien.
4. **v3b:** pasó a EAR_CLIP, pero el triángulo negro seguía.
5. **v4:** corregido el triángulo negro (normal antes de triangular). Viewmodel más cerca, inspección, eventos y pose de Tool.
6. **v5:** mangas más finas (0,30) y recarga más baja y adelantada.
