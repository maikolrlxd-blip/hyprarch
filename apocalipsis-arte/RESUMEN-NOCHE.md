# Resumen de la noche — arte del juego apocalipsis (Luto)

Noche del 22 al 23 de octubre de 2026. Lo hizo la sesión del PC (Claude), coordinada por el director (sesión en la nube). Para cada pieza: qué se ve y qué falla, sin adornos. El estilo es Poli Pintado (`taller-ia/ESTILO.md`): formas facetadas, pintura a mano mate y paleta sucia.

## Lo más importante
- **El mapa y la mujer zombi ya están dentro de Luto, en Studio.**
  - Están importados con tu sesión y se usan como plantillas (`ServerStorage.LUTO_Plantillas`).
  - Al dar a Play apareces en el cruce del mapa y las mujeres zombi llegan por las calles.
  - Place: `C:\Users\maiko\Documents\Luto\Luto-prueba-2-mapa.rbxl`, con copia en `C:\Users\maiko\Backups\luto\`.
  - Capturas: `renders/Studio_Luto_*.jpg`.
- **La «pared negra» de la Glock venía de un fallo de la librería.** La normal de las caras no se calculaba antes de triangular, y eso afectaba a todo lo que tenía perfiles cóncavos, mapa incluido. Está arreglado y todo está reconstruido.
- **Lo que falta para que se vea bien jugando:** importar y publicar las animaciones (clips FBX) con el Animation Editor y tu cuenta. Ahora las zombis se deslizan sin andar.

## Armas (diseño congelado por ti; versión v5)
Cada arma lleva modelo de mundo y viewmodel con brazos R15, con los mismos clips en los dos. También trae `eventos.json` y `<Arma>_Eventos.lua` con duraciones, eventos y puntos (boca, expulsión y miras) para el código.

| Arma | Tris | Qué se ve | Qué falla |
|---|---|---|---|
| Pistola 9mm | 634 | Glock genérica con «9MM», estrías y miras. Inspección como la describiste (3,30 s). | Al montar la corredera en la recarga, la manga izquierda tapa media pantalla durante 0,12 s. Las manos son bloques. |
| Escopeta | 530 | Corredera clásica. Bombea y expulsa el casquillo rojo; recarga cartucho a cartucho. Inspección con medio bombeo (3,00 s). | En primera persona se ve fina y lejana. Madera lisa. |
| Subfusil | 780 | Tipo MP5 con cargador curvo, más contraste y culata fina. Inspección sacando el cargador (3,00 s). | La base del cargador sobresale como una pestaña. Está al límite de triángulos. |

**No probado en Studio:** los clips de las armas ni el Tool.

## Mujer zombi (v5, realista, R15)
- **Qué se ve** (1966 tris):
  - mujer de proporciones reales, piel pálida verdosa con moretones y vestido floral roto;
  - cara de angustia: cejas levantadas, ojos nublados y boca abierta en un gemido;
  - clips Reposo, Caminar, Atacar y Caer;
  - sin gore.
- **Qué falla:**
  - el pelo, de cerca, todavía se ve rígido y los mechones de delante parecen tablas;
  - se nota la costura de las rodillas;
  - en el juego todavía no se anima.

## Jefes
- **La Lamentadora v0.1, de Codex:** guardada con su crítica, porque tenía la cara de caricatura y el pelo en tablas. El .blend está en Backups.
- **La Lamentadora v0.2 y La Alta:** se construyen sobre la base de la mujer zombi. Su estado está en `bosses/*/ESTADO.md`.

## Mapa (300 × 300 studs, v3)
- **Qué se ve:**
  - dos calles en cruz con cráter, asfalto agrietado y aceras;
  - 4 edificios (tienda, bloque derrumbado, almacén), 6 vehículos, barricadas, props y vegetación;
  - ambiente de polvo;
  - 121 piezas y 30 850 tris.
- **En Studio:**
  - 97 colisiones invisibles;
  - spawns del jugador y de 12 zombis;
  - las dos tiendas;
  - `ambiente-roblox.lua`.
- **Qué falla:**
  - los solares se repiten;
  - el borde del mapa termina en seco;
  - el follaje es de bloques.

## Prueba de la partida (informe al director, con un arreglo de una línea sin commitear)
- **Funciona:** HUD, rondas, zombis, disparo con ráfaga, agujeros de bala, cambio de arma, inspección y FIN.
- **Bug:** el jugador muerto vuelve a contar como vivo porque la vida del cadáver se regenera.
- **Ronda 1 demasiado dura:** los 6 zombis llegan juntos.

## Pendiente de ti
- OK para subir los commits locales de esta madrugada.
- Publicar las animaciones con tu cuenta, o decirme que lo haga yo en Studio.
- Probar con 2 clientes.
