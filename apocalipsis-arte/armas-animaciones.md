# Animaciones de las armas — juego "apocalipsis"

Todas las animaciones están a 60 fps y usan los nombres exactos que aparecen abajo. Cada arma se entrega en dos versiones con los mismos clips:

- **Modelo de mundo** (tercera persona): el rig `Arma` mueve solo las piezas del arma.
- **Viewmodel** (primera persona): la jerarquía es `Camara` → `Arma` → piezas, más los brazos R15 `RightUpperArm/LowerArm/Hand` y `LeftUpperArm/LowerArm/Hand`.

Las piezas del arma tienen el **mismo tiempo en las dos versiones**. El viewmodel añade el movimiento del arma entera (retroceso, inclinación) y el de las manos.

## Cómo usarlo en Roblox
- **Un FBX por clip** en `armas/<arma>/clips/<Arma>_<Mundo|VM>_<Clip>.fbx`, para importarlo con el Animation Editor sobre el rig importado. También hay un FBX con todos los clips (`<Arma>_Mundo.fbx`, `<Arma>_VM.fbx`).
- **FBX estático** (`<Arma>_Mundo_Estatico.fbx`): el arma con las piezas separadas y su pivote, la principal llamada `Handle`. Sirve para montarla con Weld/Motor6D y animar las piezas por script (TweenService) si se prefiere.
- **Escala y ejes:** exportado con `global_scale=0.01` y ejes -Z delante / +Y arriba. Así 1 unidad de Blender = 1 stud, según la prueba de escala que Codex hizo en Studio con una roca. El arma apunta a la LookVector del `Handle`; el `Tool.Grip` hay que ajustarlo en Studio.
- **Casquillos y cartuchos:** Roblox no anima la escala. Por eso en reposo el casquillo está escondido dentro del arma (recámara o cajón): sale volando en el clip y al final vuelve a su escondite de un salto. El cartucho de la escopeta funciona igual: aparece en la mano, entra por el puerto de carga y vuelve a su sitio oculto.
- **Viewmodel:** colgar el hueso `Camara` de la CFrame de la cámara. El arma queda abajo a la derecha con un campo de visión vertical de 70°, el que trae Roblox por defecto.

## Pistola 9mm (`armas/pistola-9mm/`)

| Clip | Duración | Bucle | Partes del arma | Extra en el viewmodel |
|---|---|---|---|---|
| Equipar | 0.80 s | no | Corredera: tirón atrás y suelta (0.40–0.53 s) | Sube el arma desde abajo con giro; la mano izquierda monta la corredera |
| Disparo | 0.25 s | no | Gatillo atrás (0.016 s); Corredera atrás 0.30 studs (0.033 s) y vuelve (0.11 s); Casquillo sale a la derecha y arriba girando (0.033–0.23 s) | Retroceso: el arma sube 7.5°, va atrás 0.10 y vuelve con suavidad |
| Recargar | 1.70 s | no | Cargador cae (0.22–0.50 s) → aparece el nuevo bajo la culata (0.56 s) → entra (1.04 s); Corredera atrás y suelta (1.10–1.24 s) | El arma se inclina hacia la izquierda; la mano izquierda baja, trae el cargador, lo empuja y luego monta la corredera |
| Reposo | 2.00 s | sí | — | Respiración: ±0.6° y ±0.006 studs |

## Escopeta de corredera (`armas/escopeta/`)

| Clip | Duración | Bucle | Partes del arma | Extra en el viewmodel |
|---|---|---|---|---|
| Equipar | 0.90 s | no | Bomba y Cerrojo atrás y adelante (0.48–0.77 s) | Sube el arma; la mano izquierda llega a la bomba y la acciona |
| Disparo | 0.45 s | no | Gatillo; la Bomba vibra un poco (0.03 s) | Retroceso fuerte: 11.5° arriba y 0.27 studs atrás |
| Bombear | 0.60 s | no | Bomba atrás 90 mm y adelante; Cerrojo atrás 75 mm; el Casquillo (rojo, gastado) sale por la ventana derecha | La mano izquierda acompaña a la bomba; leve sacudida |
| Recargar_Inicio | 0.45 s | no | — | El arma gira 22° para enseñar el puerto de carga y la mano izquierda baja a por cartuchos |
| Recargar_Cartucho | 0.50 s | sí (uno por cartucho) | Cartucho: aparece en la mano, sube al puerto de carga y entra (0.26–0.38 s) | La mano lleva el cartucho, lo empuja y vuelve abajo |
| Recargar_Fin | 0.55 s | no | Bomba y Cerrojo: un bombeo final (0.18–0.46 s) | El arma vuelve recta y la mano izquierda va a la bomba |
| Recargar | 2.50 s | no | Inicio + 3 cartuchos + fin, para tener el clip completo | igual |
| Reposo | 2.00 s | sí | — | Respiración |

La recarga en el juego es: `Recargar_Inicio` → `Recargar_Cartucho` × N → `Recargar_Fin`. `Disparo` no expulsa el casquillo: lo expulsa `Bombear`, que es como funciona una escopeta de corredera de verdad.

## Subfusil (`armas/subfusil/`)

| Clip | Duración | Bucle | Partes del arma | Extra en el viewmodel |
|---|---|---|---|---|
| Equipar | 0.80 s | no | Palanca de carga atrás y suelta; Cerrojo (0.42–0.72 s) | Sube el arma; la mano izquierda tira de la palanca |
| Disparo | 0.16 s | no | Gatillo; Cerrojo atrás y adelante (0.02–0.07 s); Casquillo sale por la derecha | Retroceso corto: 3.4° y 0.11 studs |
| Recargar | 1.95 s | no | Cargador curvo fuera (0.30–0.50 s) → nuevo desde la bolsa (0.84 s) → entra (1.16 s); Palanca atrás y golpe (1.34–1.64 s) | La mano izquierda saca el cargador, coge otro de la bolsa, lo mete y tira de la palanca |
| Amartillar | 0.40 s | no | Palanca y Cerrojo | La mano izquierda tira de la palanca |
| Reposo | 2.00 s | sí | — | Respiración |

Para fuego automático, `Disparo` se encadena cada 0.075–0.10 s; el casquillo se corta al reiniciar, así que conviene sumar casquillos con partículas desde el script.

## Estado
- La verificación de los clips en Blender está hecha: la vista externa y la de primera persona de cada clip están en las hojas de contacto de `armas/<arma>/previews/`.
- **No probado en Roblox Studio:** la importación de los FBX animados con el Animation Editor.
