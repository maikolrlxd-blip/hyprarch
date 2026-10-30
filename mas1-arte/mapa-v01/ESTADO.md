# Mapa v01 — zonas después de la Pradera (30/10/2026, Coordinador)
Es solo la parte visual del recorrido recto que sigue a la Pradera del Despegue de Codex, como pidió Maikol («primero todo lo visual, el código después»): **Mar de Nubes → Tormenta → Cielo alto → Espacio**.

Hay dos versiones con la misma distribución:
- el **kit en Blender** (mallas FBX y GLB por pieza);
- una versión en **piezas nativas de Roblox** (`roblox/`): un modelo y una place de prueba que se abren en Studio sin subir nada.

**Nada se ha abierto ni probado en Roblox todavía.**

## Fallos y límites (primero)
- **Sin abrir en Studio**, ni el kit ni la versión en piezas. La versión en piezas sigue el formato XML de Roblox (versión 4), y para comprobarla la vuelvo a leer y la renderizo en Blender; aun así, Studio no la ha cargado nunca.
- **Ejes.** En la versión en piezas, el vuelo va hacia −Z de Roblox con el mismo origen que la Pradera, porque Codex la exportó con `axis_forward='-Z'` y la escala por defecto. Las mallas del kit salieron con `global_scale=0.01` y `axis_forward='Z'` (mi convención): si se monta el kit junto a la Pradera, puede que haya que girar 180° o reescalar una de las dos.
- **Largo provisional**: 360 studs por zona. El largo de verdad depende del vuelo (impulso y resistencia de las alas y las mascotas), que aún no está programado. Cada zona está hecha por tramos que se pueden repetir para alargarla.
- **Multiplicadores provisionales**: las marcas del suelo dicen x3, x4, x5 y x6, siguiendo el x2 de la Pradera. Los números los decide el juego.
- **Sin cielo, luz ni niebla por zona.** En los renders, el color del cielo es el fondo de Blender. La place de prueba lleva una sola Atmosphere azul para todo, así que el Espacio se verá con cielo de día hasta que haya código que cambie el cielo al entrar en cada zona.
- **Colisiones provisionales.** En la versión en piezas solo chocan las 180 baldosas del carril (para poder andar por él); el decorado no choca. Qué choca de verdad lo decide el juego. El kit no trae colisiones.
- **Brillo.** En el kit, nada brilla: solo es color. En la versión en piezas son Neon:
  - los rayos, las auroras (transparencia 0,3) y los aros;
  - las estrellas, los cristales (0,1) y las luces de los arcos;
  - las letras de la Tormenta;
  - las flechas y las marcas del suelo de la Tormenta, el Cielo alto y el Espacio.
- **La versión en piezas no es una copia exacta del kit.** Las piezas de Roblox no tienen bisel, así que:
  - las nubes del borde y del mar son bolas sobre dos discos planos;
  - las torres de nubes son solo bolas;
  - las rocas son dos bloques girados, y los planetas, una bola con una banda;
  - los aros son 16 bloques y los anillos de los planetas, 36;
  - los cristales y las auroras llevan colores más saturados, porque en Neon el pastel sale casi blanco.
- **Rendimiento sin medir**: 3.092 piezas, más de 1.000 de ellas bolas.
- **Mejorable en el kit**: las torres de nubes parecen pilas de bloques redondeados, y los asteroides y planetas son low-poly sencillos.
- **La Pradera no es mía.** Los renders la cargan del archivo de Codex (sin tocarlo) solo para ver el empalme. No va en los exportes ni en la place de prueba: se monta con su FBX.

## Qué hay
| Zona | Desde y hasta (Y en Blender = −Z en Roblox, studs) | Marca | Lo que tiene |
|---|---|---|---|
| Mar de Nubes | 172 → 532 | x3 | carril de baldosas de nube, nubes en el borde, mar de nubes bajo, torres de cúmulos, islitas flotantes con árbol |
| Tormenta | 532 → 892 | x4 | carril oscuro, nubarrones altos, rayos que caen al mar de nubes |
| Cielo alto | 892 → 1.252 | x5 | carril rosa, cristales clavados y flotando, tres auroras que ondulan a cada lado |
| Espacio | 1.252 → 1.612 | x6 | carril de roca con cráteres, rocas en el borde, asteroides, dos planetas con anillo, estrellas |

- En cada zona hay un arco de entrada con el nombre en letras de bloques (legible al llegar volando), la marca de multiplicador, flechas en el suelo y tres aros que suben (z = 14, 20 y 26).
- **Kit en Blender** (`exports/<zona>_<pieza>`): cada zona va en piezas separadas, en FBX y GLB:
  - las piezas son `Suelo`, `LadoIzq`, `LadoDer`, `Arco`, `Marcas` y `Aros`;
  - ninguna pasa de 10.000 triángulos (la mayor tiene 9.620); en total, unos 85.000;
  - una sola textura de paleta para todo: `texturas/Mapa_paleta_256.png`.
- **Versión en piezas de Roblox** (`roblox/`):
  - `Mapa-v01.rbxmx`: el modelo `Mapa_v01`, con un Model por zona (`MarDeNubes`, `Tormenta`, `CieloAlto`, `Espacio`) y dentro las carpetas de las piezas de arriba. Son 3.092 Part y WedgePart, todas ancladas.
  - `Mapa-v01-prueba.rbxlx`: la place de prueba, con el modelo, un SpawnLocation al principio del carril y una Atmosphere.
  - `Mapa-v01-roblox-hoja.jpg` y `previews/`: renders de Blender de las piezas leídas del `.rbxmx`, no de Roblox.
  - `datos.json`: piezas por zona y por tipo.
- **Comprobaciones de la versión en piezas**:
  - cada cuña coincide con su triángulo (error máximo de 0,00001 studs);
  - todos los giros son de verdad (sin escala ni espejo), y todas las piezas miden entre 0,02 y 2.048 studs;
  - el XML leído de vuelta da las mismas 3.092 piezas;
  - **0 pares de caras planas solapadas en el mismo plano**, es decir, sin parpadeo. Para llegar a 0 se cambió esto:
    - las bases de las nubes acababan todas a la misma altura;
    - los dos brazos de cada flecha y los bloques de los cráteres se solapaban;
    - las caras de los aros y de los anillos coincidían en las uniones;
    - los tramos seguidos de aurora quedaban en el mismo plano;
    - los dos discos de cada nube tenían la misma altura.
  - Las bolas y los lados de los cilindros no se comprueban: en Roblox son curvos.
- **Arreglo del 30/10 también en el kit**: los cráteres del Espacio pisaban la marca x6 y una flecha. Ahora van entre las flechas (y regenerado; lo demás no cambia).

## Cómo abrirlo en Studio
Son archivos locales: abrirlos o insertarlos no sube nada a Roblox.
- **Place de prueba**: en Studio, `File → Open from File…` y elegir `roblox/Mapa-v01-prueba.rbxlx`. Con Play, el personaje sale al principio del Mar de Nubes y puede andar por el carril.
- **En otra place** (la del juego): en el Explorer, clic derecho en `Workspace → Insert from File…` y elegir `roblox/Mapa-v01.rbxmx`.

## Siguiente
1. Abrir la place de prueba en Studio y comprobar la escala con un personaje, la luz, el Neon y el rendimiento. Para hacerlo yo, Maikol tiene que volver a darme permiso: Studio se actualizó el 29/10.
2. Montar la Pradera de Codex delante (con su FBX: importarlo sí sube la malla a Roblox, así que pedir OK) y ver el empalme.
3. Cuando haya vuelo programado, ajustar el largo de cada zona y la altura de los aros.
4. Código (después): cielo y niebla por zona, colisiones y aros que dan puntos.

## Cómo regenerar
- **Kit**: `blender -b --factory-startup --python-exit-code 1 -P tools/build_mapa.py`, con `MAPA_FASE=check|full`. Escribe `Mapa-v01.blend`, `exports/`, `texturas/`, `previews/`, `datos.json` y la hoja `Mapa-v01-hoja.jpg`.
- **Versión en piezas**: `blender -b --factory-startup --python-exit-code 1 -P tools/mapa_roblox.py`; con `MAPA_RBX_FASE=xml` solo escribe los archivos. Usa las mismas zonas y la misma semilla que `build_mapa.py`, comprueba las cuñas y los giros, y vuelve a leer el XML para los renders.
