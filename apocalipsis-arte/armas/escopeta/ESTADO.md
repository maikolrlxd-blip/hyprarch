# Escopeta de corredera — estado

**Congelada por decisión de Maikol** (2026-10-23, "Ya déjale las armas así"). Esta es la versión v2 y no se hacen más vueltas de crítica.

## Qué falla
- **Gatillo demasiado grande:** dentro del guardamonte se ve una cuña negra y gruesa, no una lámina fina.
- **Madera muy saturada:** la culata y la bomba son de un naranja fuerte y a distancia se ven planas. La bomba es un bloque sin estrías.
- **Cajón de mecanismos liso:** es una caja que desde la izquierda no tiene ningún detalle.
- **Primera persona:**
  - el arma ocupa poca pantalla;
  - el antebrazo izquierdo, una manga verde, es un bloque grande que domina la esquina inferior izquierda.
- **No probado en Roblox Studio:** la importación de los FBX animados.

## Qué funciona
- La silueta se lee claramente como una escopeta de corredera.
- Al bombear, el casquillo rojo sale por la ventana derecha.
- La recarga mete los cartuchos uno a uno: `Recargar_Inicio`, después `Recargar_Cartucho` las veces que haga falta y al final `Recargar_Fin`.

## Triángulos
Cuerpo 342, Bomba 68, Cerrojo 12, Gatillo 20, Cartucho 44 y Casquillo 44: **530 en total** (presupuesto 300–800). Los brazos del viewmodel suman 256 aparte.

## Clips (modelo de mundo y viewmodel)
| Clip | Duración | Bucle |
|---|---|---|
| Equipar | 0,90 s | no |
| Disparo | 0,45 s | no |
| Bombear | 0,60 s | no |
| Recargar_Inicio | 0,45 s | no |
| Recargar_Cartucho | 0,50 s | sí, una vez por cartucho |
| Recargar_Fin | 0,55 s | no |
| Recargar (el clip completo con 3 cartuchos) | 2,50 s | no |
| Reposo | 2,00 s | sí |

## Vueltas
1. **v1:** tenía 1264 triángulos y la culata era rara. El cajón salía negro porque una caja exterior tapaba la ventana de expulsión.
2. **v2:** cajón rehecho como un prisma más las piezas de la pared derecha alrededor de la ventana, y culata recta clásica. Bajó a 530 triángulos.

## Archivos
Siguen el mismo esquema que la pistola:
- `Escopeta.blend`;
- `Escopeta_Mundo.fbx`, `Escopeta_VM.fbx` y `Escopeta_Mundo_Estatico.fbx` (con su pieza `Handle`);
- GLB;
- `clips/` (16 FBX);
- `texturas/`;
- `previews/`, con copia en `../../renders/`.
