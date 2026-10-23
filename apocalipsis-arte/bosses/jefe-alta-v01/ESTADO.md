# La Alta v0.1 — estado

Del 2026-10-23. Es el segundo tipo de jefe de Luto, hecho sobre la base de la mujer zombi (piezas R15, rig y clips). Se construye con `ZOMBI_VARIANTE=alta` y `tools/build_zombi.py`.

## Qué falla
- **Sin identidad propia:** parece la mujer zombi en grande (2×), con vestido gris. Le falta algo que la distinga de lejos, como una silueta muy delgada y estirada, otra ropa o un peinado distinto.
- **Clips:** son los de la zombi escalados.
- **Importada en Studio** (2026-10-23) como `ServerStorage.LUTO_Plantillas.Jefe_alta`, con su rig R15. Faltan las animaciones publicadas y verla en una ronda de jefe.

## Qué funciona
- **Aspecto:** mide unos 11,5 studs, más del doble que un R15. Tiene los brazos largos (×1,25), la cara de angustia de la zombi y un vestido gris apagado y roto.
- **Montaje en Studio:**
  1. Importar `JefeAlta_Estatico.fbx`.
  2. Seleccionar el modelo.
  3. Ejecutar `integracion/ArmarZombi.lua`, que lo nombra `Jefe_alta` y crea el rig R15 con HipHeight ≈ 4,9.
  4. Moverlo a `LUTO_Plantillas`.

## Triángulos
1966, con 4 texturas de 1024.
