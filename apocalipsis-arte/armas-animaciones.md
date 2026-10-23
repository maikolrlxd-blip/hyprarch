# Animaciones de las armas — juego "apocalipsis"

Todas las animaciones van a 60 fps y usan exactamente los nombres de clip de las tablas. Cada arma se entrega en dos versiones con los mismos clips:

- **Modelo de mundo** (tercera persona): el rig `Arma` mueve solo las piezas del arma. En `Inspeccionar` también gira el arma en la mano.
- **Viewmodel** (primera persona): la jerarquía es `Camara` → `Arma` → piezas, más los brazos R15 (`RightUpperArm`/`LowerArm`/`Hand` y `LeftUpperArm`/`LowerArm`/`Hand`).

Las piezas del arma se mueven **en los mismos instantes en las dos versiones**. El viewmodel añade el movimiento del arma entera (retroceso, inclinación) y el de las manos.

## Duraciones exactas y eventos (para el código)
Cada arma trae `eventos.json` y `<Arma>_Eventos.lua` en su carpeta. El `.lua` es un ModuleScript listo para usar y contiene:
- **Por clip:** duración en segundos y en frames, si va en bucle y sus eventos en segundos.
- **Eventos:** `disparo`, `casquillo_sale`, `corredera_atras` y `corredera_adelante`, `cargador_suelta`, `cargador_fuera`, `cargador_nuevo` y `cargador_dentro`, `bomba_atras` y `bomba_adelante`, `cartucho_dentro`, `palanca_atras` y `palanca_suelta`.
- **Puntos del arma**, en studs y ejes de Roblox (X derecha, Y arriba, −Z delante = LookVector):
  - `Boca`: fogonazo y origen del disparo;
  - `Expulsion`: de aquí salen los casquillos con partículas;
  - `MiraTrasera` y `MiraDelantera`: para apuntar;
  - en la escopeta, además, `PuertoCarga`.
- Cada punto se da medido de dos formas:
  - desde el origen del FBX, que es el punto de agarre;
  - desde el centro de la caja del `Handle`, que es donde Roblox coloca el MeshPart importado.

Los FBX no llevan marcadores de evento: el Animation Editor no los importa desde FBX. O se lanzan los sonidos por tiempo con estas tablas, o se añaden marcadores a mano en el editor en esos tiempos.

## Cómo usarlo en Roblox
- **Clips:**
  - Hay un FBX por clip en `armas/<arma>/clips/<Arma>_<Mundo|VM>_<Clip>.fbx`, para importarlo con el Animation Editor sobre el rig importado.
  - También hay un FBX con todos los clips: `<Arma>_Mundo.fbx` y `<Arma>_VM.fbx`.
- **FBX estático** (`<Arma>_Mundo_Estatico.fbx`): el arma con sus piezas separadas y su pivote. La pieza principal se llama `Handle`. Sirve para montarla con Weld o Motor6D y animar las piezas por script con TweenService, si se prefiere.
- **Escala y ejes:** se exporta con `global_scale=0.01` y ejes −Z delante / +Y arriba, así que 1 unidad de Blender = 1 stud. Lo comprobé comparando con la roca que Codex validó en Studio.
  - El arma apunta a la LookVector del `Handle`.
  - El `Tool.Grip` hay que ajustarlo en Studio.
- **Casquillos y cartuchos:** Roblox no anima la escala.
  - En reposo, el casquillo está escondido dentro del arma (en la recámara o el cajón). Durante el clip sale volando y al final vuelve de golpe a su escondite.
  - El cartucho de la escopeta funciona igual: aparece en la mano, entra por el puerto de carga y vuelve a su sitio oculto.
- **Viewmodel:**
  - Cuelga el hueso `Camara` de la CFrame de la cámara.
  - El campo de visión vertical es de 70°, el de Roblox por defecto.
  - El arma queda abajo a la derecha. Las posiciones de la v4 están más cerca de la cámara que en la v3.

## Pistola 9mm (`armas/pistola-9mm/`)

| Clip | Duración | Bucle | Partes del arma | Extra en el viewmodel |
|---|---|---|---|---|
| Equipar | 0,80 s | no | Corredera: tirón atrás y suelta (0,48–0,53 s) | Sube el arma desde abajo girando. La mano izquierda monta la corredera por el lado. |
| Disparo | 0,25 s | no | Gatillo atrás (0,016 s). Corredera atrás 0,30 studs (0,033 s) y vuelta (0,11 s). Casquillo sale a la derecha y arriba girando (0,05 s). | Retroceso: el arma sube 7,5°, retrocede 0,10 y vuelve suave. |
| Recargar | 1,70 s | no | El cargador cae (0,22–0,32 s), el nuevo aparece bajo la culata (0,56 s) y entra (1,04 s). Corredera atrás y suelta (1,18–1,24 s). | El arma sube e inclina para enseñar la boca del cargador. La mano izquierda trae el cargador y lo empuja. Después el arma baja y gira a la derecha para montar la corredera por el lado. |
| Reposo | 2,00 s | sí | — | Respiración: ±0,6° y ±0,006 studs. |
| Inspeccionar | 3,30 s | no | Solo gira el arma en la mano | Según la descripción de Maikol: (1) la voltea en diagonal hacia la derecha (0,3–1,1 s); (2) lo mismo hacia la izquierda (1,1–1,9 s); (3) estira el brazo con la pistola de lado, estilo gánster, con pausa (2,4–2,8 s); (4) vuelve al reposo (3,3 s). La mano izquierda suelta el arma y baja fuera de cuadro. |

## Escopeta de corredera (`armas/escopeta/`)

| Clip | Duración | Bucle | Partes del arma | Extra en el viewmodel |
|---|---|---|---|---|
| Equipar | 0,90 s | no | Bomba y Cerrojo atrás y adelante (0,58 y 0,77 s) | Sube el arma. La mano izquierda llega a la bomba y la acciona. |
| Disparo | 0,45 s | no | Gatillo. La bomba vibra un poco (0,03 s). | Retroceso fuerte: 11,5° arriba y 0,27 studs atrás. |
| Bombear | 0,60 s | no | Bomba atrás 90 mm (0,16 s) y adelante (0,40 s). Cerrojo atrás 75 mm. El casquillo rojo gastado sale por la ventana derecha (0,18 s). | La mano izquierda acompaña a la bomba con una leve sacudida. |
| Recargar_Inicio | 0,45 s | no | — | El arma gira 22° para enseñar el puerto de carga y la mano izquierda baja a por cartuchos. |
| Recargar_Cartucho | 0,50 s | sí, uno por cartucho | El cartucho aparece en la mano, sube al puerto y entra (`cartucho_dentro` a 0,34 s). | La mano lleva el cartucho, lo empuja y vuelve abajo. |
| Recargar_Fin | 0,55 s | no | Un bombeo final de bomba y cerrojo (0,28 y 0,46 s). | El arma vuelve recta y la mano izquierda va a la bomba. |
| Recargar | 2,50 s | no | Inicio + 3 cartuchos + fin, como clip completo | igual |
| Reposo | 2,00 s | sí | — | Respiración |
| Inspeccionar | 3,00 s | no | Medio bombeo para mirar la recámara: bomba 45 mm y cerrojo 38 mm atrás (0,92 s) y adelante (1,25 s) | Inventada, porque Maikol la dejó libre: gira el arma para mirar la ventana de expulsión, abre la recámara con medio bombeo, cierra, la gira al otro lado y vuelve. La mano izquierda no suelta la bomba. |

En el juego, la recarga es `Recargar_Inicio` → `Recargar_Cartucho` × N → `Recargar_Fin`. `Disparo` no expulsa el casquillo: lo expulsa `Bombear`, igual que en una escopeta de corredera de verdad.

## Subfusil (`armas/subfusil/`)

| Clip | Duración | Bucle | Partes del arma | Extra en el viewmodel |
|---|---|---|---|---|
| Equipar | 0,80 s | no | Palanca de carga atrás (0,52 s) y suelta (0,59 s), con el cerrojo | Sube el arma. La mano izquierda tira de la palanca. |
| Disparo | 0,16 s | no | Gatillo. Cerrojo atrás y adelante (0,02–0,07 s). El casquillo sale por la derecha (0,02 s). | Retroceso corto: 3,4° y 0,11 studs. |
| Recargar | 1,95 s | no | El cargador curvo sale (0,30–0,36 s), viene uno nuevo de la bolsa (0,84 s) y entra (1,16 s). Palanca atrás (1,44 s) y suelta (1,51 s). | La mano izquierda saca el cargador, coge otro de la bolsa, lo mete y tira de la palanca. |
| Amartillar | 0,40 s | no | Palanca y cerrojo (0,10 y 0,17 s) | La mano izquierda tira de la palanca. |
| Reposo | 2,00 s | sí | — | Respiración |
| Inspeccionar | 3,00 s | no | El cargador sale a medias (`cargador_fuera` a 0,72 s) y vuelve a entrar (`cargador_dentro` a 1,20 s) | Inventada, porque Maikol la dejó libre: inclina el arma, la mano izquierda saca el cargador a medias, lo mira y lo vuelve a meter. Después gira el arma al otro lado y vuelve. |

Para fuego automático, `Disparo` se encadena cada 0,075–0,10 s. El casquillo se corta al reiniciar el clip, así que conviene añadir casquillos con partículas desde el script, en el punto `Expulsion`.

## Estado
- **Comprobado en Blender:** cada clip tiene vista externa y en primera persona en las hojas de contacto de `armas/<arma>/previews/`.
- **En tercera persona:** el brazo estirado de la inspección de la pistola es animación del personaje R15, no del arma. El clip del arma solo la gira en la mano.
- **No probado en Roblox Studio:** la importación de los FBX animados con el Animation Editor.
