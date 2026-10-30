# Contrato servidor ↔ interfaz — SIN PROBAR EN STUDIO
Borrador de Claude nube (30/10), puesto al día por el Coordinador con el hito 1 (el vuelo). Si a la interfaz le falta algo, se cambia aquí con un commit y el servidor se adapta.

## Coordenadas y zonas
- **El vuelo va hacia −Z.** El origen es el de la Pradera de Codex (mapa-v01 empieza en Z = −172).
- La zona sale de la posición hacia −Z (`Vuelo.CFG.zonas`, igual que las marcas del suelo del mapa):

  | Desde (studs hacia −Z) | Zona | Multiplicador |
  |---|---|---|
  | 0 | Pradera | x1 |
  | 37 | prado de la Pradera | x2 |
  | 172 | Mar de Nubes | x3 |
  | 532 | Tormenta | x4 |
  | 892 | Cielo alto | x5 |
  | 1.252 | Espacio | x6 |

- **Lanzamiento**: sale de una parte llamada `MAS1_Canon` en el Workspace (la del cañón de la Pradera, cuando esté). Si no la hay, sale desde donde está el jugador, que tiene que estar en el suelo.

## Atributos del jugador
Los escribe el servidor; la interfaz solo los lee.

| Atributo | Tipo | Qué es | Estado |
|---|---|---|---|
| `EnVuelo` | bool | está volando | hito 1 |
| `Energia` | 0–1 | fracción de energía del vuelo (el HUD la pinta tal cual) | hito 1 |
| `EnergiaMax` | número | energía del vuelo actual (segundos sin boost) | hito 1 |
| `Planeando` | bool | sin energía: baja sola, sin boost ni ataque | hito 1 |
| `Boost` | bool | boost activo, confirmado por el servidor | hito 1 |
| `Impulso` | número | multiplicador de velocidad (mascotas y alas) | hito 1 (vale 1 hasta el hito 4) |
| `Distancia` | entero | studs avanzados hacia −Z desde el lanzamiento (el HUD los llama m) | hito 1 |
| `ZonaMult` | entero | multiplicador de la zona donde está | hito 1 |
| `Puntos` | entero | puntos del vuelo en curso: (distancia + bote) × zona × bonus de dinero | hito 1 |
| `Dinero` | entero | **nuevo**: total del jugador; se suma al aterrizar | hito 1 (sin guardar hasta el hito 5) |
| `Exp` | entero | **nuevo**: total del jugador | hito 1 (sin guardar hasta el hito 5) |
| `Potencia` | número | potencia del jugador | hito 3 (ahora 0; en Studio se puede cambiar a mano en la vista del servidor) |
| `Rebirths` | entero | — | hito 3 |
| `Aros`, `ArosTotal` | entero | aros cruzados en este vuelo / aros del mapa | hito 2 |
| `Cofres` | entero | **nuevo**: cofres voladores atrapados en total (para las alas avanzadas del hito 6) | hito 2 (sin guardar hasta el hito 5) |
| `Mascota`, `MascotaBonus` | texto, número | — | hito 4 (ahora «—» y 1) |
| `Alas` | texto | id de las alas equipadas | hito 6 |

## RemoteEvents
Están en ReplicatedStorage y los crea `src/Red.lua`.

- **`MAS1_Accion`** (cliente → servidor). Como mucho 30 mensajes por segundo; lo demás se ignora.
  - `"lanzar"`: solo en el suelo y fuera de un vuelo.
  - `"boost", bool`: mantener pulsado (W o joystick arriba). El servidor lo confirma en el atributo `Boost`.
  - `"turbo"`: un toque (botón TURBO del HUD) que da 1,2 s de boost.
  - `"ataque"`, `"puno"` o `"patada"`: gasta `Vuelo.CFG.costeAtaque` de energía y no se puede planeando. Golpea al enemigo vivo más cercano a 12 studs (`Encuentros.CFG.alcance`); vuelve a los 15 s.
  - Pendientes: `"equipar", tipo, id`; `"abrirHuevo", rareza`; `"rebirth"`; `"comprarAla", id`.
- **`MAS1_Efecto`** (servidor → clientes), con nombres de `src/Efectos.lua`:
  - `"lanzamiento", pos`;
  - `"golpe", pos`: un golpe, a un enemigo o al aire;
  - `"aro", pos`: solo al jugador, cuando cruza un aro o atrapa un cofre;
  - `"estela", nil, raíz, bool`: el rastro del boost, que se enciende y se apaga.
- **`MAS1_Resultado`** (servidor → cliente), al aterrizar: `{ distancia, aros, golpes, cofres, multiplicador, dinero, exp, tiempo }`.
- Pendientes: `MAS1_Huevo` (`{ rareza, mascotaId }`) y `MAS1_Inventario` (`{ mascotas = {id = cantidad}, equipadas = {ids}, alas = {ids} }`).

## Mundo (hito 2)
- **Aros**: son los Models `Aro` del mapa, cada uno con una pieza invisible `Centro`. El radio es la distancia media de sus bloques al centro. Cada aro cuenta una vez por vuelo, con 1,5 studs de margen por fuera.
- **Enemigos y cofres**: son anclas invisibles en `Workspace.MAS1_Entidades`. Las dibuja `client/Entidades.client.lua` con piezas (provisionales hasta importar las mallas de `mas1-arte/enemigos-v02`).
  - Enemigo: atributos `Tipo` (globo, nube, nubarron, cometa, ovni o meteorito) y `Vivo`.
  - Cofre: atributos `Tipo = "cofre"` y `Dueno = UserId`. Cada jugador solo ve el suyo.
  - Los enemigos se reparten por zona (`Encuentros.CFG.zonas`): separados 40 studs y lejos de los aros.
  - El cofre sale 140 studs por delante y huye a 52 studs/s. Hacen falta el boost (70) y unos 4 s para pillarlo, y salen 2 por vuelo como mucho.
- **Cielo por zona**: `client/Zonas.client.lua` cambia en cada cliente la hora y la `Atmosphere` según la zona.

## Quién mueve al personaje
El **cliente** (`client/VueloControl.client.lua`) mueve su personaje con `src/Manejo.lua`, para que responda al instante. El **servidor** (`src/Partida.lua`) lleva todo lo que cuenta y valida cada paso:
- tres presupuestos de distancia (hacia delante, de lado y vertical) que crecen con la velocidad permitida en cada momento;
- la media de los últimos 4 s hacia delante;
- los límites del carril y la altura;
- el planeo hasta el suelo.

Si algo no cuadra, devuelve al personaje a la última posición buena. La distancia que se paga es la validada.

## Datos
- `src/Mascotas.lua`: ids, rarezas y bonus.
- `src/Vuelo.lua`: reglas y cifras provisionales.
- `src/Manejo.lua`: cómo se vuela.
- `src/Partida.lua`: sesión y validación.
- `src/Encuentros.lua`: aros, golpes, reparto de enemigos y cofres.

La interfaz no calcula bonus: se los pide al servidor.
