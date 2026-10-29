# Punto de retoma — Luto (arte e integración en Studio)

Escrito el 2026-10-29 por la sesión del PC (Claude), al pasar al proyecto «+1 de lanzamiento por segundo» (`mas1-arte/`). El detalle de cada pieza está en `ESTADO.md` y en el `ESTADO.md` de cada carpeta.

## Qué hay hecho
- Mapa 300 × 300, mujer zombi, La Lamentadora v0.2, La Alta v0.1 y las tres armas (pistola, escopeta, subfusil): construidos en Blender, importados y probados en Studio.
- 31 animaciones publicadas con la cuenta de Maikol: 12 de zombi y jefes y 19 de los viewmodels. Sus ids están en `apocalipsis-juego/src/Animaciones.lua` y se comprobaron contra las secuencias locales. No falta ningún id de primera persona.
- Partida completa probada el 23/10 en `Luto-jugable.rbxl`: rondas, 10 monedas por zombi, tienda de munición, 1/2/3, R, F, jefes, rutas con PathfindingService y 8 zombis a la vez a 60 FPS.

## Armas en mano: estado exacto
Se ve en Play (probado el 23/10):
- **Primera persona:** el viewmodel de cada arma abajo a la derecha, con manga oliva y mano color piel; 1/2/3 lo cambian; Reposo en bucle; R y F lo animan.
- **Tercera persona:** el Tool sale en la mano del personaje (plantillas `ReplicatedStorage.LUTO_Armas`), pero sin animar.
- **Arreglado tras la prueba de Maikol** (en el repo, no en el `.rbxl`):
  - la raíz del viewmodel va anclada, porque suelta caía por debajo del mapa y el arma «desaparecía»;
  - va más abajo y a la derecha (`OFFSET` en `client/Viewmodel.client.lua`, ajustable en Play con el atributo `LUTO_VMOffset` del jugador);
  - la sangre es pequeña y la marca del cuerpo se borra en 1,5 s (`src/Impactos.lua`, `src/Disparo.lua`, `client/ImpactoFX.lua`).

No verificado: que se vean los clips Disparo, Equipar, Bombear y Recargar_* (solo vi Reposo, Recargar e Inspeccionar), el agarre (Grip) de las tres armas en tercera persona y la escopeta y el subfusil con el offset nuevo.

Falta:
1. **Animar al personaje en tercera persona** (Maikol eligió «animar el personaje»): unos 19 clips R15 (apuntar, disparar, recargar, equipar e inspeccionar por arma), publicados con su cuenta. Sin empezar; aplazado por el encargo nuevo.
2. **Refrescar `Luto-jugable.rbxl`** (ver abajo).
3. Revisar que las tiendas de `LUTO_Mapa` no estén duplicadas: hay dos `Tienda_municion` y dos `Tienda_curar`, y el prompt va en una de cada par.

## Archivos y cómo rehacer el place
- `C:\Users\maiko\Documents\Luto\Luto-jugable.rbxl`, guardado el 23/10 a las 17:34. Tiene Mapa, Zombi_Mujer, los dos jefes, `LUTO_VM` y `LUTO_Armas` (con el giro de 180° ya corregido) y el ambiente v2. Sus scripts son anteriores a los arreglos de arriba. Los cambios del 23/10 a las 22:24 se perdieron al cerrarse Studio sin guardar.
- Para refrescarlo:
  1. Abrirlo en Studio con la sesión de Maikol.
  2. `rojo build apocalipsis-arte/tools/luto-scripts.project.json -o luto-scripts.rbxm`. Rojo 7.7.1 está en `C:\Users\maiko\Documents\Codex\2026-10-21\c\work\tools\rojo-7.7.1\`.
  3. Archivo > Importar modelo Roblox y elegir el `.rbxm`. Desde la barra de comandos, mover `Luto` a ReplicatedStorage, `LutoServidor` a ServerScriptService y `LutoCliente` a StarterPlayerScripts, borrando las versiones viejas.
  4. Guardar y copiar a `C:\Users\maiko\Backups\luto\`.
- Otros places: `Luto-prueba-2-mapa.rbxl` (el de pruebas, con `ServerStorage.LUTO_Pruebas`). Las copias están en `C:\Users\maiko\Backups\luto\`; `Luto-jugable_20261023-1655.rbxl` es la última del jugable.
- El importador 3D de Studio deja las mallas giradas 180°. `tools/girar180_roblox.lua` lo corrige y los scripts `ArmarVM_*` y `ArmarTool_*` ya lo hacen.
- `tools/exportar_viewmodel_roblox.py` genera, de cada `<Arma>.blend`, el FBX por piezas, `ArmarVM_*.lua`, `ArmarTool_*.lua` y `Animaciones_VM_*.rbxmx`.

## Git (rama ccr-d4583e0a-ggl8kz)
- Sin subir en mi copia: `b8fb176` (mío: arma, ancla y sangre) y los tres de Codex (`ebe6a52`, `a9b7bce`, `e9b8086`: 95 MB en total, ningún archivo de más de 20 MB).
- El remoto trae tres del director del proyecto «+1» (`mas1-arte/`) que no chocan con nada mío.
- Modificados por otros y sin commitear (no son míos, no los toco): `slime-rush-juego/client/Hud.client.lua` y `slime-rush-juego/server/GameServer.server.lua`.

## Pendiente de Maikol
- Probar con 2 clientes.
- Ver el arma con el offset nuevo y decir si le gusta.
- OK de push de lo anterior: la regla del director para esta tanda es push solo con su OK.
