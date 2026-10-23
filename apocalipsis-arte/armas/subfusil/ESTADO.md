# Subfusil — estado

**Congelado por decisión de Maikol** (2026-10-23, "Ya déjale las armas así"). Esta es la versión v2; no se hacen más vueltas de crítica.

## Qué falla
- **En primera persona la culata tapa la pantalla.** Queda pegada a la cámara y cubre casi un tercio de la imagen por la derecha con un bloque gris oscuro. Es el fallo más visible del arma.
  - Arreglo propuesto, no aplicado por la congelación: adelantar y bajar el arma en el viewmodel, o plegar la culata solo en el viewmodel.
- **Todo es del mismo gris oscuro,** así que las piezas se distinguen poco.
- **La base del cargador** sobresale en ángulo, como una pestaña.
- **Triángulos al límite:** 780, dentro del presupuesto pero cerca del máximo de 800.
- **Sin probar en Roblox Studio:** la importación de los FBX animados.

## Qué funciona
- La silueta se reconoce como un subfusil tipo MP5 genérico.
- El cargador curvo va delante del guardamonte.
- Tiene palanca de carga, anillo del punto de mira y alza.
- `Disparo` es corto (0,16 s), así que sirve para fuego automático.

## Triángulos
| Pieza | Triángulos |
|---|---|
| Cuerpo | 592 |
| Cargador | 72 |
| Palanca | 40 |
| Cerrojo | 12 |
| Gatillo | 20 |
| Casquillo | 44 |
| **Total** | **780** |

Los brazos del viewmodel suman 256 aparte.

## Clips (modelo de mundo y viewmodel)
| Clip | Duración |
|---|---|
| Equipar | 0,80 s |
| Disparo | 0,16 s |
| Recargar | 1,95 s |
| Amartillar | 0,40 s |
| Reposo | 2,00 s, en bucle |

## Vueltas
1. **v1:** culata como una losa, cañón fino y 1266 triángulos.
2. **v2:** culata más fina, tubo de la palanca, anillo del punto de mira y alza más pequeña. Se quitaron los biseles y quedó en 780.

## Archivos
Siguen el mismo esquema que la pistola:
- `Subfusil.blend`
- `Subfusil_Mundo.fbx`, `Subfusil_VM.fbx` y `Subfusil_Mundo_Estatico.fbx` (con `Handle`)
- GLB
- `clips/` (10 FBX)
- `texturas/`
- `previews/`, con copia en `../../renders/`
