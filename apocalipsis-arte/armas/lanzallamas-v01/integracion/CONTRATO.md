# Lanzallamas LUTO — contrato de integración pendiente

Pedido de Maikol: inspección, recarga, sacar, guardar, efectos y reacciones de quemado para zombis. Asset de videojuego ficticio; no contiene un diseño mecánico funcional.

## Estados y eventos

`Equipar` 0,85 s → `Reposo` 2 s en bucle. `Disparo` 0,60 s es un bucle de sostener el arma, sin retroceso de bala. Activar Muzzle al entrar a disparo y apagar al soltar, cambiar estado, quedar sin recurso, morir o retirar Tool. No volver a crear emisores por cada vuelta del clip.

`Guardar` 0,65 s apaga fuego en t=0 y permite ocultar el modelo en t=0,60. `Inspeccionar` 3,2 s apaga fuego en t=0, gira el arma a ambos lados y regresa. Debe poder cancelarse por equipar otra arma, disparar o daño según reglas del juego.

`Recargar` 2,8 s: apertura 0,34, cartucho fuera 0,88, sustitución fuera de cámara 1,36, insertar 2,12 y confirmar recarga 2,42. La autoridad del servidor debe validar posesión, inventario, estado y cancelación antes de consumir/reponer. El evento del cliente solo sincroniza presentación; no otorga combustible. Valores de capacidad, daño, alcance y coste siguen sin fijar en este bloque de arte.

Los clips están en `clips/`, tanto Mundo como VM. `eventos.json` y `Lanzallamas_Eventos.lua` contienen las marcas temporales y el punto Boca convertido a ejes Roblox. Rig y clips no tienen IDs publicados. La anatomía del agarre y las transiciones se deben revisar en primera y tercera persona dentro del motor.

## Quemado visual y animaciones de zombi

`QuemadoFX.lua` crea un controlador `Muzzle(Attachment)` con `SetActive(boolean)` y `Destroy()`. El Attachment debe orientarse hacia el LookVector de la boquilla. `Burn(model, seconds)` crea tres emisores locales, renueva duración si se repite y limpia al terminar o retirar el modelo. `StopBurn(model)` y `Destroy()` permiten limpieza explícita. No envía remotos ni aplica daño.

Llamar al `Destroy()` de cada controlador Muzzle cuando se retire el arma. `FX.Destroy()` limpia los quemados de NPC; no administra los controladores de boquilla. Llamar funciones de controlador con punto (`controller.SetActive(true)`), no con dos puntos. El módulo usa una textura incorporada de Roblox; aún falta comprobar su apariencia/carga en motor. No hay máscara de carbonización ni audio implementados en esta revisión.

Animaciones específicas en `apocalipsis-arte/zombi-mujer/animaciones-quemado-v01/`: `QuemadoInicio` al primer impacto, `QuemadoBucle` mientras el estado de quemado siga activo y `QuemadoCaer` solo cuando el servidor confirme muerte. No reiniciar Inicio con cada tick; no reproducir Caer por la expiración de VFX. Todavía no están conectadas a la IA ni al daño del juego.

El fuego visual y las poses son entregas distintas: renders Blender de pose no verifican ParticleEmitter de Roblox. Falta Play con blanco vivo/muerto, interrupción de recarga, guardar durante fuego, reequipo, desaparición de NPC, varios zombis y FPS. No marcar estos casos pasados por compilar o por reimportar FBX. No tocar los archivos de combate que el coordinador tiene modificados.
