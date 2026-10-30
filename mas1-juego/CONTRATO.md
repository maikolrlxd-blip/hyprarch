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
| `Potencia` | entero | potencia del jugador: +1/s en tierra (más en las zonas, con los rebirths); en Studio se puede cambiar a mano en la vista del servidor | hito 3 |
| `Entreno` | número | **nuevo**: potencia por segundo ahora mismo (0 volando). La interfaz puede pintar «AFK x1,5» o «ENTRENANDO x2» | hito 3 |
| `Rebirths` | entero | rebirths hechos | hito 3 |
| `CosteRebirth` | entero | **nuevo**: potencia que pide el siguiente rebirth (500, 1.000, 2.000…) | hito 3 |
| `Lanzamientos` | entero | **nuevo**: lanzamientos en total (las alas iniciales salen en el 3.º) | hito 3 |
| `DiasSeguidos` | entero | **nuevo**: racha de días seguidos jugando (las alas robóticas salen con 3) | hito 5 |
| `Aros`, `ArosTotal` | entero | aros cruzados en este vuelo / aros del mapa | hito 2 |
| `Cofres` | entero | **nuevo**: cofres voladores atrapados en total (para las alas avanzadas del hito 6) | hito 2 (sin guardar hasta el hito 5) |
| `Mascota`, `MascotaBonus` | texto, número | la mascota equipada de más rareza y el multiplicador de dinero de las equipadas | hito 4 |
| `Alas` | texto | id de las alas equipadas (`""` = ninguna). El servidor ya aplica su bonus (`Alas.bonus`, que sube con los rebirths); equiparlas y desbloquearlas llega en el hito 6 | hito 3 / 6 |

## RemoteEvents
Están en ReplicatedStorage y los crea `src/Red.lua`.

- **`MAS1_Accion`** (cliente → servidor). Como mucho 30 mensajes por segundo; lo demás se ignora.
  - `"lanzar"`: solo en el suelo y fuera de un vuelo.
  - `"boost", bool`: mantener pulsado (W o joystick arriba). El servidor lo confirma en el atributo `Boost`.
  - `"turbo"`: un toque (botón TURBO del HUD) que da 1,2 s de boost.
  - `"ataque"`, `"puno"` o `"patada"`: gasta `Vuelo.CFG.costeAtaque` de energía y no se puede planeando. Golpea al enemigo vivo más cercano a 12 studs (`Encuentros.CFG.alcance`); vuelve a los 15 s.
  - `"rebirth"`: solo en tierra y con `Potencia ≥ CosteRebirth`. Reinicia solo la potencia, suma un rebirth y lanza el efecto `"rebirth"`. Si falta potencia, llega un `MAS1_Aviso`.
  - Inventario (hito 4; solo en tierra, y si algo falla llega un `MAS1_Aviso` con el motivo):
    - `"abrirHuevo", rareza`: cobra `Mascotas.PRECIO_HUEVO[rareza]` del `Dinero`;
    - `"equipar", "mascota", id` y `"desequipar", "mascota", id`: hasta `Mascotas.MAX_EQUIPADAS` (3); se puede repetir una si tienes varias;
    - `"equipar", "ala", id` y `"desequipar", "ala"`;
    - `"comprarAla", id`: solo las que tienen precio; las de requisito se desbloquean solas;
    - `"inventario"`: vuelve a pedir `MAS1_Inventario`. El servidor también lo manda al entrar y cada vez que aparece el personaje.
- **`MAS1_Efecto`** (servidor → clientes), con nombres de `src/Efectos.lua`:
  - `"lanzamiento", pos`;
  - `"golpe", pos`: un golpe, a un enemigo o al aire;
  - `"aro", pos`: solo al jugador, cuando cruza un aro o atrapa un cofre;
  - `"estela", nil, raíz, bool`: el rastro del boost, que se enciende y se apaga.
- **`MAS1_Resultado`** (servidor → cliente), al aterrizar: `{ distancia, aros, golpes, cofres, multiplicador, dinero, exp, tiempo }`.
- **`MAS1_Aviso`** (servidor → cliente): `texto` para mostrar, como «Te falta potencia para el rebirth: 320 / 500».
- **`MAS1_Huevo`** (servidor → cliente, hito 4): `{ rareza, mascotaId, nueva }`.
  - `rareza` es la del huevo y `nueva` indica si es la primera vez que la consigue.
  - El nombre y la rareza de la mascota salen de `Mascotas.get(mascotaId)`.
- **`MAS1_Inventario`** (servidor → cliente, hito 4): `{ mascotas = {id = cantidad}, equipadas = {ids}, alas = {ids}, alaEquipada = id | nil }`. Llega al entrar, al aparecer el personaje y en cada cambio. Con él se ponen al día los atributos:
  - `Mascota`: la de más rareza de las equipadas;
  - `MascotaBonus`: el multiplicador de dinero;
  - `Alas`.
- El fénix solo se consigue con Robux: `Inventario.darFenix` desde `ProcessReceipt`. El id del producto (`PRODUCTO_FENIX` en el servidor) **no está configurado**: no se ha creado ningún producto ni precio.

## Guardado y alas (hitos 5 y 6)
- **Qué se guarda**: `Potencia`, `Dinero`, `Exp`, `Rebirths`, `Cofres`, `Lanzamientos`, la racha de días y el inventario (mascotas, equipadas, alas y la equipada).
  - Va en el DataStore `MAS1_Datos_v1`, con la clave `j_<UserId>` (`server/Guardado.lua` + `src/Datos.lua`).
  - Se guarda cada 60 s, al salir y al cerrar el servidor.
  - Un servidor toma los datos con un bloqueo de sesión y otro no los pisa hasta que se sueltan o caducan (3 min).
  - Si no se pueden cargar, se expulsa al jugador con un mensaje, mejor que jugar con datos vacíos y pisar los buenos.
- **Mientras carga**, el servidor ignora las intenciones y no entrena.
- **Solo en Studio sin publicar** (o sin acceso a las API) se juega sin guardar; lo avisa el Output. En un servidor de verdad nunca: si no hay DataStore o fallan los reintentos, el jugador sale con un mensaje.
- **Alas**: se desbloquean solas al cumplir el requisito. Las primeras se equipan solas, y llega un `MAS1_Aviso` «¡Nuevas alas: …!».
  - iniciales: en el 3.er lanzamiento;
  - robóticas: con 3 días seguidos;
  - avanzadas: con 10 cofres, o comprándolas por 25.000.

## Entrenamiento y rebirth (hito 3)
- Zonas del mapa (irán en la Pradera; en la place de prueba son dos placas junto al spawn):
  - partes llamadas `MAS1_AFK` (×1,5 aunque no te muevas);
  - partes llamadas `MAS1_Entreno` (×2 si corres).
  - Cuentan la huella de la parte y hasta 8 studs por encima.
- Ritmo: `Vuelo.ritmoEntreno(rebirths, zona, corriendo)` = 1/s × (1 + 0,5 × rebirths) × zona.
- Coste del rebirth: `Vuelo.costeRebirth(r)` = 500 × 2^r.
- Alas (`src/Alas.lua`): la `LISTA` lleva `{ id, nombre, requisito, precio, impulso, resistencia, pide }`.
  - `Alas.bonus(id, rebirths)` sube un 25 % por rebirth.
  - `Alas.combinar(mascotas, alas)` multiplica las alas con las mascotas.

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
- `src/Alas.lua`: alas, requisitos y bonus.
- `src/Inventario.lua`: huevos, mascotas equipadas y alas de un jugador.

La interfaz no calcula bonus: se los pide al servidor.
