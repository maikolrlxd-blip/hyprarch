# Slime Rush v2 — la isla del Gran Torneo

> **Estado:** diseño vigente con las respuestas del usuario (2026-10-22). **[Maikol]** = lo dijo él; **[Propuesta]** = propuesta del director, ajustable. Nada está probado en Roblox Studio todavía (la lógica sí: 34 pruebas en Lua puro).

## 0. Regla de arte (obligatoria)
**Todo hecho con modelos propios en Blender. Nada básico de Roblox Studio** (ni bloques/Parts, ni Terrain de fábrica con sus materiales por defecto, ni Toolbox). Cada aspecto del mundo —**hasta la playa, los botes y los cactus del desierto**— es un modelo con textura propia, mismo estilo cartoon mate. Ver §7.

## 1. Historia **[Maikol]**
Los concursantes **vienen del extranjero en botes** a una isla misteriosa para el **Gran Torneo**: quien consiga más botín gana **mucho dinero y se hace famoso**. Empieza con una **animación de llegada**: los botes navegan hasta las playas y cada jugador desembarca en su punto de la costa.

## 2. La idea **[Maikol]**
Isla **grande**, **distinta en cada partida** (como Minecraft: una semilla crea el mundo), para **20 jugadores o más** (diseñado para **24**). Se explora, se recolectan recursos, hay **cofres ocultos**, **slimes raros** (casi nunca aparecen) y **accesorios raros**. Pasado cierto tiempo **se abre el regreso a la meta** y todos deben volver antes de que se acabe; los primeros en llegar reciben **bonificación** (1º, 2º, 3º…), pero **la mayoría de los puntos salen de lo que encuentras en el mapa**.

## 3. Línea de tiempo **[Propuesta; la duración total "aún no se sabe", se decide más adelante]**
| Fase | Tiempo | Qué pasa |
|---|---|---|
| Generación y llegada | ~15 s | El servidor elige la semilla y construye la isla; animación de los botes; cuenta 3-2-1 |
| Exploración | 0:00 → 6:00 | Recolectar, abrir cofres, cazar raros, derrotar y saquear |
| **Regreso habilitado** | 6:00 → 10:00 | La meta se abre (aviso y marcador); se puede depositar y cobrar el bono de llegada |
| **Colapso** | 10:00 → 10:30 | **Desastres naturales**: terremotos que abren el suelo, tornados, tormenta con rayos, erupción, y la isla se hunde |
| Resultados | ~8 s | Puntos, bonos y raros destacados |
Todos los tiempos son constantes (`Rules.DEFAULT`).

## 4. Puntos **[Propuesta]** (en simulación con 24 bots, los bonos son ≈ 8 % del total)
| Fuente | Valor | Frecuencia |
|---|---|---|
| Recursos comunes (bayas 1 · cristales 3 · minerales 5) | 1–5 | Muchísimos |
| Cofres: común 20 · musgoso 40 · dorado 140 · **oculto 90** (enterrado, con pista) | presupuesto fijo | 80 en total: 32/16/16/16 |
| **Slime raro** (Dorado 250 · Cristal 180 · Sombra 300 · Arcoíris 400) | 180–400 | Muy raro: 0–5 por partida |
| **Accesorio raro** (sombrero, alitas, corona…) | 80–160 (y se conserva como cosmético) | Bono de suerte en cofres |
| Bono de llegada | 1º +150 · 2º +100 · 3º +60 · 4º +30 · resto +10 | Fijo |

## 5. Combate, robo y la meta
**[Maikol]** *"Que no se robe por golpe: al **derrotar** a alguien queda **inconsciente en el piso por un tiempo**, y ahí le puedes robar."* También: *"se campea en la meta para robar"*; lo robable es **lo que recolectaste en la partida**.
**[Propuesta de reglas]** (implementadas y probadas):
- Derrotar (el combate vive en el juego) → el rival queda **inconsciente 12 s**: no puede actuar y se corta su depósito.
- Un jugador inconsciente puede ser **saqueado**: 1–2 objetos al azar por saqueo, con 1,2 s de espera entre saqueos. Lo que no cabe en tu mochila cae al suelo.
- Al despertar tiene **8 s de inmunidad** (no se puede encadenar derrotas).
- Los objetos **ligados** (slimes y accesorios raros) piden **2 saqueos seguidos** en 3 s.
- Mochila de 12 objetos. **Una sola llegada**: al depositar (canal de 2 s) terminas tu partida a salvo.
- **Campear la meta** es una estrategia válida: quien llega a depositar puede ser derrotado y saqueado.

## 6. Volcán y desastres **[Maikol]**
- **Volcán:** *"puede llegar a generarse"* (en ~60 % de las islas, en roca/montaña alta, lejos de la meta). **Si alguien se tira al cráter, la erupción queda asegurada** y la **lava sube lentamente** desde el cráter, **sin cubrir todo el mapa**: crece 1,2 studs/s hasta un tope (≤ 220) que **nunca alcanza la meta** (probado). Complica sin hacer imposible. Quien se lanza pierde lo que llevaba.
- **Colapso final:** *"si se acaba el tiempo y no llegaste pierdes todo, porque empiezan los desastres naturales: terremotos que abren el suelo, tornados, tormentas, erupciones; la isla colapsa."* Se genera una lista **determinista** de desastres (4 terremotos, 3 tornados, tormenta, 18 rayos, erupción si hay volcán, y el hundimiento) para animarlos.

## 7. Mundo generado y arte **[Propuesta técnica]**
- **Isla** de 1536 × 1536 studs (cuadrado que la contiene), costa irregular, mar alrededor, **meta en una plaza plana al centro**, **24 apariciones en playas** repartidas alrededor y su **bote** mar adentro (para la animación). Misma semilla = mismo mundo.
- **Biomas de tierra:** pradera, bosque, desierto, roca/cueva, montaña, lago (+ mar). Cofres y recursos repartidos por sectores para que **ninguna zona sea mejor** (desviación ≤ 21 % en 30 semillas).
- **Arte 100 % Blender** (kit modular): terreno por teselas propias (llano, pendiente, acantilado, orilla, playa) con texturas propias; **playa** (arena, espuma, conchas, rocas, palmeras, muelle); **botes** (4–6 diseños con animación de llegar); **desierto** (cactus, dunas, rocas rojizas, cráneos, oasis); bosque (árboles, arbustos, flores, hongos, troncos); roca/cueva (rocas, cristales, boca de cueva); **volcán** (cono, lava, ceniza); **cofres** y **nodos de recurso**; **meta**; **desastres con modelos propios** (embudo de tornado, grietas, nube de tormenta, rayos, columna de erupción); slimes y accesorios raros.
- **Cómo ensamblar el terreno (decisión técnica pendiente de verificar en Studio):** el generador entrega una rejilla de 128 × 128 alturas y biomas (celdas de 12 studs). Opción A: teselas de Blender de 48 studs ensambladas según la rejilla. Opción B: mallas construidas en tiempo de ejecución con el terreno por trozos y texturas propias (depende de disponibilidad de `EditableMesh` en el juego publicado). **No se usará el Terrain de fábrica.**

## 8. Decisiones
| # | Tema | Estado |
|---|---|---|
| 1 | Duración total | **Por decidir más adelante** (hoy 10 min + 30 s de colapso, ajustable) |
| 2 | Robo | **Decidido [Maikol]:** derrotar → inconsciente → saquear (sin robo por golpe) |
| 3 | Lava | **Decidido [Maikol]:** volcán que puede aparecer; erupción asegurada si alguien salta al cráter; lava lenta y limitada |
| 4 | Tamaño y jugadores | **Decidido [Maikol]:** grande, **24 jugadores** (20 o más) |
| 5 | Tiempo agotado | **Decidido [Maikol]:** pierdes todo; desastres y colapso de la isla |
| 6 | Una sola llegada | **[Propuesta]** (por confirmar) |

## Habilidades de slime (ideas de Maikol, 2026-10-22)
Nombres tentativos (no los puso él): Resorte = **Bongo**, Montura = **Rayo**, Divide = **Miga**.
- **Bongo (resorte):** (1) se enrolla en el brazo y da un puñetazo que lanza al enemigo (contra suelo, pared o solo volando); (2) se pone en el suelo y te impulsa; (3) lo mandas a atacar: rebota por paredes/árboles/techo y se lanza al enemigo.
- **Rayo (montura rápida):** (1) te montas unos segundos; (2) lleva un objeto, dinero o **un jugador (también inconsciente: confirmado "sí")** hacia donde quiera el dueño (rescatar, lanzar, empujar o secuestrar para saquear); (3) acelera y se estrella contra el enemigo.
- **Miga (se divide):** (1) lanza 4 partes (antes anotadas como 3; confirmado 4) que se regeneran (mantener = apuntar; clic = al más cercano); (2) partes en manos y pies para escalar cualquier superficie o anclarse al suelo contra tornado/tormenta; (3) tapa heridas (cura) y reduce el daño en esas partes. Las partes son un recurso compartido: cuanto más usas 1-2-3, menos tienes.
- **Cuerpo de slime (decisión de Maikol):** todos los jugadores juegan con cuerpo de slime; sus cuerpos reales se quedan en el inicio (botes/muelle). Heridas = gel, no sangre, para escenas dramáticas sin clasificación +18. Propuesta pendiente de confirmar: al colapso, quien no llegó se derrite. Ojo: la clasificación de Roblox también depende de la intensidad de la violencia, no solo de la sangre.

## Apariencia de los jugadores (Maikol, 2026-10-22)
El jugador **no es un slime redondo**: tiene un **cuerpo humanoide hecho de slime, personalizable** (color, forma, accesorios). Es el "cuerpo de slime" de la isla; el cuerpo real queda en el inicio/botes. Los slimes con habilidades (Bongo, Rayo, Miga) son criaturas aparte que se unen al jugador. Pendiente de confirmar con Maikol: qué se personaliza (color/textura/ojos/accesorios raros), y cómo se ve el cuerpo al perder gel (heridas, derretirse). Implicación técnica: humanoide R15 con malla/materiales de slime (translúcido, mate), compatible con animaciones estándar.

## Aclaraciones de Maikol (2026-10-22, 2)
- **Compañeros:** Bongo, Rayo y Miga conservan su forma de slime normal; los jugadores son humanoides de slime.
- **Personalización:** color, ojos, altura, anchura y accesorios.
- **Partes del cuerpo:** al recibir daño se pierden partes (p. ej. un brazo). Se reemplazan **robándoselas a otro jugador mientras lo saqueas y sigue inconsciente**.
- **Miga:** con sus **4 pedazos** (antes se anotaron 3; confirmar cuántos) puede darte una extremidad nueva. Si quieres usar tus habilidades, tienes que deshacer la extremidad de slime (los pedazos vuelven a ser recurso).
- Pendiente de definir: qué hace cada parte perdida (brazo = sin habilidad de ese lado/menos mochila, pierna = más lento…), si un brazo robado es del color del otro jugador, cuánto dura, y el tope de partes. Ojo con la clasificación de Roblox: mostrar la pérdida de partes como "gel que se desprende" y sin gore.

## Reglas de extremidades (Maikol, 2026-10-22, 3) — CONFIRMADO
- **Miga = 4 pedazos.**
- **Color:** la extremidad robada conserva el color del dueño original.
- **Ojo:** pequeño, perderlo casi no tiene mecánica.
- **Pie/pierna:** saltas con una pierna y vas más lento.
- **Brazo:** menos capacidad de atacar (un solo brazo).
- Se puede perder **todo**. Sin ninguna extremidad quedas en el suelo, quieto, y **tu slime se une a ti y lo pierdes durante esa partida**; a cambio te da **dos extremidades a elección: brazo+pierna, dos piernas o dos brazos**.
- Pendiente de afinar: cuántas extremidades tiene el humanoide (2 brazos + 2 piernas), si "sin extremidades" cuenta como inconsciente para el saqueo, cuánto dura la penalización de un brazo (¿baja daño/alcance/velocidad de ataque?) y si un brazo robado se puede volver a perder.

## Extremidades: respuestas finales (Maikol, 2026-10-22, 4)
1. **Sin extremidades = en el suelo y se puede saquear/robar.** Dos opciones: (a) sacrificar al slime (fusión, 2 extremidades a elección) o (b) quedarte quieto: si alguien se acerca, **tu slime lo ataca por ti**; si lo derrota, el slime te trae tus partes de vuelta.
2. **Un brazo robado se puede volver a perder** (y volver a robar).
3. **Un solo brazo = la velocidad de ataque baja a la mitad** (de 2 golpes/s a 1; el daño por golpe no cambia). Con 0 brazos no se ataca con las manos.
Para Rules.lua/Codex: parámetros `attack_rate_base=2`, `attack_rate_per_arm=1` (2 brazos→2/s, 1→1/s, 0→0); pierna perdida: velocidad de movimiento reducida y salto a una pierna; sin extremidades: estado `limbless` (saqueable, el slime defiende).

## PRIORIDAD DE MECÁNICAS (Maikol: "son demasiadas") — vigente
Todo lo anterior se conserva como idea, pero se construye **por capas**. Una capa nueva solo entra cuando la anterior divierte.
- **Capa 1 (prueba jugable):** isla, explorar, recoger recursos y cofres, llegar a la meta, tiempo y colapso simple, puntos. Un solo slime con UNA habilidad (puñetazo). Quedar inconsciente y saquear.
- **Capa 2:** los otros dos slimes (Rayo, Miga) con una habilidad cada uno; botes y llegada.
- **Capa 3:** volcán y desastres; cofres raros y accesorios.
- **Capa 4:** cuerpo humanoide personalizable y extremidades (perder, robar, fusión del slime).
- **Capa 5:** habilidades 2 y 3 de cada slime; sensación de juego (efectos/sonido).

## GUION de una partida (Maikol, 2026-10-22) — guía narrativa vigente
1. **Desembarco:** acaba el tiempo de preparación y todos los jugadores desembarcan en el **muelle**. De cada cuerpo real sale una **réplica de slime** (el humanoide con el que se juega) y el cuerpo real cae al suelo. La **animación de salir del cuerpo depende de la que tenga equipada cada jugador** (cosmético/personalizable).
2. **Reunión en la meta:** todos van a la meta y, tras unos segundos de cuenta atrás, comienza el juego y todos salen corriendo.
3. **Isla entera, libertad total:** cada uno va por donde quiera (bosque, desierto, montaña, volcán…).
4. **Ejemplo de combate (contrajuego):** en el bosque, alguien ataca por la espalda con **Rayo** (embestida). La víctima usa **Bongo** para saltar y esquivar y luego activa el **golpe resorte** y le da al atacante. → el combate necesita esquivas con habilidades, no solo daño.
5. **Aviso final:** cuando queda poco tiempo suenan **altavoces del muelle** y aparece un **contador arriba**.
6. **Colapso:** quien no llegó **muere/se derrite** porque la isla es consumida por un desastre (volcán, tormenta, tornado…).

### Decisiones tomadas (Maikol)
- **Muelle = meta: CONFIRMADO.** Un solo muelle en la costa (ángulo por semilla); la plaza de la meta queda tierra adentro; todos aparecen en la plaza; los botes esperan mar adentro frente al muelle. Implementado en `World.lua` (`world.dock`, `world.goal`, `World.sectorOf`: sectores = abanico de 22,5° visto desde el muelle).
- **Cuerpos reales en el muelle:** no se pueden tocar ni saquear; quedan ahí "supervisados" por NPCs (escenografía).

### Preguntas abiertas que salen del guion
- **¿La meta y el muelle son el mismo lugar?** Hoy el generador pone la meta como plaza en el centro y los botes en las playas (24 apariciones). El guion habla de UN muelle de desembarco y de volver ahí. Propuesta: muelle = meta, en la costa, con todos saliendo desde el mismo punto (más justo y simple). Pendiente de confirmar; implica cambiar World.lua.
- **Los cuerpos reales caídos en el muelle:** ¿se pueden tocar/saquear? (propuesta: no, son solo escenografía y puntuación de "quién llegó").
- **Duración de la cuenta atrás en la meta** (propuesta: 10 s).
