# La Alta v0.1 — estado

Del 2026-10-23. Es el segundo tipo de jefe de Luto, hecho sobre la base de la mujer zombi (piezas R15, rig y clips). Se construye con `ZOMBI_VARIANTE=alta` y `tools/build_zombi.py`.

## Qué falla
- **Sin identidad propia:** parece la mujer zombi en grande (2×), con vestido gris. Le falta algo que la distinga de lejos, como una silueta muy delgada y estirada, otra ropa o un peinado distinto.
- **Clips:** son los de la zombi escalados.
- **Importada en Studio** (2026-10-23) como `ServerStorage.LUTO_Plantillas.Jefe_alta`, con su rig R15.
- **Vista en una ronda de jefe** (2026-10-23, en el place de prueba con `JEFE_CADA = 1`):
  - camina y ataca con sus clips, y el cartel «LA ALTA» sale bajo el panel de ronda (`renders/Studio_Luto_HUD_1080_banner_jefe_la_alta.jpg`);
  - **se sube encima del jugador:** el servidor la lleva con `MoveTo` hasta la posición del jugador, y con su HipHeight de 4,9 acaba de pie sobre su cabeza (`renders/Studio_Luto_jefe_encima_del_jugador.jpg`);
  - **se quedó parada:** en z = 131, cerca del borde del mapa, unos 25 s sin moverse (`MoveDirection` 0) antes de echar a andar;
  - a contraluz del sol bajo del ambiente se ve lavada, casi blanca;
  - al morir se desmonta en piezas, porque se rompen las articulaciones, y no se ve el clip Caer;
  - Reposo se mezcla con Caminar porque todos los clips llevan prioridad Action (ver `zombi-mujer/ESTADO.md`).
- **Animaciones publicadas** (cuenta de Maikol), en `apocalipsis-juego/src/Animaciones.lua`:

  | Clip | Id |
  |---|---|
  | Reposo | 73495974087699 |
  | Caminar | 110159877146850 |
  | Atacar | 139329540979905 |
  | Caer | 124895291095508 |

## Qué funciona
- **Aspecto:** mide unos 11,5 studs, más del doble que un R15. Tiene los brazos largos (×1,25), la cara de angustia de la zombi y un vestido gris apagado y roto.
- **Montaje en Studio:**
  1. Importar `JefeAlta_Estatico.fbx`.
  2. Seleccionar el modelo.
  3. Ejecutar `integracion/ArmarZombi.lua`, que lo nombra `Jefe_alta` y crea el rig R15 con HipHeight ≈ 4,9.
  4. Moverlo a `LUTO_Plantillas`.

## Triángulos
1966, con 4 texturas de 1024.
