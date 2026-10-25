# LUTO / fuego cosmético v02 — 25/10/2026

Revisión separada del módulo de `lanzallamas-v01/integracion/QuemadoFX.lua`. La v01 y su paquete sellado se conservan. El fuego inicial se leía débil y quedaba dentro de las mallas en la copia de Studio; v02 coloca los emisores en la superficie, aumenta tamaño/opacidad y añade luz cálida suave sin sombras. No cambia mallas ni texturas Poli Pintado.

## API

- `FX.Muzzle(attachment)`: el Attachment debe mirar hacia delante. Devuelve `SetActive(true/false)` y `Destroy()`, llamadas con punto. Quien crea el controlador debe destruirlo al retirar el arma.
- `FX.Burn(model, seconds)`: presentación en UpperTorso, LowerTorso y LeftUpperArm. Repetir renueva el plazo sin acumular emisores. Duración acotada a 0,1–8 segundos; valor inválido usa 2,8.
- `FX.StopBurn(model)`: retira los attachments y su conexión.
- `FX.Destroy()`: retira los quemados activos; NO destruye controladores Muzzle, que tienen su propia limpieza.

No decide impactos, daño, munición ni muerte. El servidor de combate debe resolver esos estados; este módulo solo presenta el evento confirmado. Sin remotos nuevos. Sin audio ni carbonización. No se conectó al código de juego del coordinador.

Usa la textura incorporada `rbxasset://textures/particles/fire_main.dds`, comprobada en esta instalación y visible en Play. No requiere inventar IDs ni se publicó ningún recurso. Tres emisores a 18 partículas/s por NPC; chorro a 60/s. Son valores de revisión visual, no un presupuesto validado para hordas.

## Validación real

La copia aislada `apocalipsis-arte/qa/quemado-studio-v01` ejecutó seis comprobaciones en Roblox el 25/10: clips, renovación/expiración, limpieza explícita, retiro de modelo, toggle/destrucción del chorro y descenso de raíz. Se pulsaron los tres botones y el chorro desde la interfaz. Tres zombis: 43,23 FPS sin fuego y 41,98 con fuego, ventanas de 5 s, viewport 1096×635, un cliente sin combate. Ver `VALIDACION-MOTOR.json` y capturas MOTOR de esa carpeta.

Falta integración con arma/IA/servidor, cancelaciones reales, replicación, móvil y prueba con más NPC. Los siete casos con mocks de v01 son históricos; no se atribuyen a v02 como una nueva ejecución.
