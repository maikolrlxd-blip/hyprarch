# Punto de retoma del Coordinador (05/11/2026)

Lo escribe el Coordinador (Claude en el PC de Maikol) para seguir sin perder el hilo si se resume la conversación. El director es Linux 2.0 (sesión en la nube). Maikol dijo «tienes todo permitido» y «que continúe». Subir audio a su cuenta solo con su «sí» en el chat del Coordinador.

## Hecho y subido
- **c77fee5 — zonas largas** (pedido de Maikol):
  - mapa en bloques de 360 studs (`mas1-arte/tools/build_mapa.py`, `mapa_roblox.py`), 10.289 piezas, carril hasta Z = −8.812;
  - `Vuelo.CFG.zonas` y `dineroPorStud` 0,12, `Encuentros.CFG.zonas`, `Zonas.client` y `tests/test_zonas.py`;
  - vuelta al lobby 3 s después de aterrizar (`server/Partida.server.lua`);
  - `construir_place.py` quita el SpawnLocation del mapa.
  - Probado en Studio.
- **3eca622 — gorro UGC de una pieza:** validador con 0 errores y 2 avisos de textura que no se pueden quitar.
- **92664cf — atributo `MascotasEq`** en el servidor; `mas1-arte/tools/exportar_rig_roblox.py`.
- **Regla de ejes FBX** (`mas1-arte/pruebas-studio/2026-10-30-ejes/LEEME.md`): con huesos, `bake_space_transform=True` + `axis_forward` `'Z'` (frente +Y) o `'-Z'` (frente −Y, Codex); sin huesos, girar la malla 180°.

## Hecho después (01/11)
- **d3bd1bf — MAS1_Modelos**: `assets/MAS1_Modelos.rbxmx` (11 mascotas y 3 alas, pivotes arreglados), metido en la place por `default.project.json` y `construir_place.py`, más `client/AnimaSeguidores.client.lua` (aleteo con Bone.Transform). Probado en Studio junto con las misiones del director.
- Comprobación del mapa largo: 14 caras solapadas, todas en los anillos de los planetas del Espacio (lejos del carril).
- **943e73f — alas con los clips reales, soporte en la espalda y cañón de Codex** (pedidos de Maikol y del director):
  - **Alas.** `mas1-arte/tools/clips_a_lua.py` → `src/ClipsHuesos.lua`.
    - Los huesos importados NO tienen los ejes de Blender: en los rigs con bake salen con giro identidad respecto a su padre, y en los de Codex con otros ejes. Por eso copiar `matrix_basis` cerraba las alas sobre el jugador.
    - Ahora se pasa por el espacio del modelo: semejanza ajustada con los huesos (error 0, escala 1 en las 14 piezas), C·D·C⁻¹ por fotograma y `Transform = (pose_padre · Bone.CFrame)⁻¹ · pose`.
    - Comprobado en Studio: `TransformedCFrame == CFrame * Transform`, y las avanzadas abren y aletean en V como el Flap.
  - **Soporte de las alas** (Maikol: «más pegado al cuerpo, la mitad dentro»).
    - `SOPORTE_ALAS` en `client/Seguidores.client.lua`: centro del soporte respecto al pivote, hacia atrás (iniciales −0,01, robóticas 0, avanzadas 0,27).
    - Se pone en la superficie de la espalda (`torso.Size.Z / 2`). Medido en Play: pivote de las avanzadas a 0,229 del centro del torso.
  - **Cañón pajarero de Codex** (Maikol: «usa el cañón que hizo ChatGPT»).
    - Está en `assets/MAS1_Equipo.rbxmx` → `ReplicatedStorage.MAS1_Equipo.Canon`, y `server/Lobby.server.lua` lo pone ×3 en Z = −22, con la boca hacia −Z.
    - Ver `mas1-arte/equipo-v01/canon/LEEME.md`. Un rig de piezas rígidas sale con Motor6D y al revés, como un estático: se gira el pivote.
  - **Herramientas.**
    - `tools/extraer_rbxmx.py`: de la place guardada a `.rbxmx`, sin el menú contextual, que no se ve en las capturas.
    - `construir_place.py` ya no repite SharedStrings: Studio no abría la place si se repetían.

## Noche del 05/11 (Maikol dormía; cola del director: trabajar solos, commits pequeños, push permitido)
Studio se actualizó solo a `version-fee454b8e2094ba9`. El permiso de pantalla para él se pidió y salió **denegado** (`user_denied`). Por eso esta noche nada está probado en Studio: todo va marcado así.
- **e61dc13 — reproductor de clips compartido y enemigos listos para sus mallas.**
  - `src/Clips.lua`: bucle o una vez, por encima de otro clip y con escala; lo prueba `tests/test_clips.py`.
  - `AnimaSeguidores` ya lo usa.
  - `Entidades`: si existe `ReplicatedStorage.MAS1_Enemigos`, malla ×2,2 girada hacia +Z, con Idle, Blink y Defeat; si no, las piezas.
  - `clips_a_lua.py` genera `src/ClipsEnemigos.lua` en cuanto exista `assets/MAS1_Enemigos.rbxmx`. Además, cada clip empieza con los huesos en reposo.
- **6a8bc2e — números medidos** (`NUMEROS.md`, `tools/medir_numeros.py`, con los módulos en lupa) **y dos ajustes:**
  - **Alas avanzadas:** antes 10 cofres o 25.000, que se tenían en 3-7 minutos y llegaban al final del mapa con potencia 100-300. Ahora 60 cofres o 75.000.
  - **Golpes:** el golpe que acierta devuelve la energía del ataque; antes atacar siempre hacía perder dinero.
- **c8908e7 — retroceso del cañón.**
  - `clips_a_lua.py`, modo «motor» → `src/ClipsEquipo.lua`.
  - `client/Canon.client.lua` mueve las 12 piezas del barril y la palanca con el efecto `"lanzamiento"`: apaga sus Motor6D en ese cliente y los vuelve a encender al acabar.
- **a9d7181 — icono v02** (`mas1-arte/icono-v02/`, `tools/icono_v02.py`).
- **1fa378b — vida en el lobby:** 20 farolas, 5 tiras de banderines y 14 árboles de bloques (`server/Lobby.server.lua`).

## En marcha / bloqueado por Studio (hace falta que Maikol acepte el aviso de pantalla para `version-fee454b8e2094ba9`)
1. **Importar los 6 enemigos voxel.** Los FBX con la regla de ejes están en el scratchpad de la sesión (`C:\Users\maiko\AppData\Local\Temp\claude\C--Users-maiko--local-bin\03b310d9-fea9-45c3-b932-e706bacfa36e\scratchpad\enemigos-fbx\<tipo>.fbx`). Se rehacen con `exportar_rig_roblox.py`: `BLEND=mas1-arte/enemigos-v02/<carpeta>/<Nombre>.blend`, `SALIDA=<tipo>.fbx`.
   - Importarlos uno a uno y pasarles `mas1-juego/tools/studio/preparar_enemigos.lua` en la barra de comandos: frente hacia −Z, pivote, anclados y carpeta `ReplicatedStorage.MAS1_Enemigos`.
   - Ctrl+S → `python tools/extraer_rbxmx.py build/Mas1-prueba.rbxlx ReplicatedStorage/MAS1_Enemigos assets/MAS1_Enemigos.rbxmx`.
   - Añadir `"MAS1_Enemigos": { "$path": "assets/MAS1_Enemigos.rbxmx" }` a `default.project.json`.
   - Volver a pasar `clips_a_lua.py` (genera `ClipsEnemigos.lua`) y `construir_place.py`, y probar en vuelo.
2. **Ver en vuelo** las alas iniciales y robóticas, el retroceso del cañón, las farolas, los banderines y los árboles.
3. **2 clientes** (Prueba → Servidor local) y FPS.
4. **Cofre con malla:** el «Cofre mensajero» de Codex (`equipo-inicial-v01/Cofre-mensajero-v01.blend`, clips `Courier_flight` y `Reward_open`). Tiene piezas rígidas, como el cañón: Motor6D y modo «motor».

## Lista pendiente, en orden (del director)
1. ~~**MAS1_Modelos**~~ HECHO (d3bd1bf). Detalles para rehacerlo: Models en `ReplicatedStorage.MAS1_Modelos.Mascotas.<id>` y `.Alas.<id>`, con el frente hacia −Z y `PrimaryPart`. Los lee `client/Seguidores.client.lua`.
   - **Rigs:** `exportar_rig_roblox.py` con `BLEND=<.blend>` `SALIDA=<carpeta>/<id>.fbx`.
   - **ids y su `.blend`:**
     - Codex (solo lectura, `C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\mas-1-lanzamiento\art`):
       - gorrion → `mascotas-comunes-v06/GorrionMiga_v06/GorrionMiga_v06.blend`;
       - golondrina → `mascotas-comunes-v06/GolondrinaBrisa_v06/GolondrinaBrisa_v06.blend`;
       - iniciales → `alas-iniciales-v02/Alas-ave-iniciales-v02.blend`;
       - roboticas → `alas-roboticas-v02/Alas-Roboticas-v02.blend`.
     - Míos (`mas1-arte`):
       - nube, globo, nubarron, ovni, meteorito, cometa → `mascotas-enemigos-v01/<id>/Mascota<Nombre>.blend`;
       - aguila → `mascotas-altas-v02/aguila-legendaria/AguilaLegendaria.blend`;
       - grifo → `mascotas-altas-v02/grifo-mitico/GrifoMitico.blend`;
       - fenix → `mascotas-altas-v02/fenix/FenixDeFuego.blend`;
       - avanzadas → `alas-avanzadas-v02/AlasAvanzadas_v02.blend`.
   - **Importar en Studio** (Inicio → Importar, uno a uno: el diálogo no deja elegir varios). El modelo se llama como el archivo. En la primera vez fallaron nubarrón y grifo: repetirlos.
   - **Pivote de las mascotas:** en las mías, el CFrame del MeshPart sale girado 180° respecto al de la escena. Arreglo:
     - medir `(Lid_R − Body)·LookVector` del pivote;
     - si sale < 0, `m:PivotTo(m:GetPivot() * CFrame.Angles(0, math.pi, 0))`;
     - luego `PrimaryPart.PivotOffset = PrimaryPart.CFrame:ToObjectSpace(CFrame.new(PrimaryPart.Position))`.
   - **Alas:** el pivote es el origen del FBX (el anclaje de la espalda): `PivotOffset = mayor.CFrame:ToObjectSpace(pivoteOriginal)`. Las avanzadas medían bien: Tip_R a la derecha 2,24, 1,06 detrás y 1,80 arriba.
   - **Alas de Codex:** dan Tip_R a la IZQUIERDA. Mirarlas desde detrás y compararlas con sus `previews` antes de darlas por buenas.
   - **Guardar la carpeta** como `.rbxmx`: clic derecho → Guardar / Exportar → Guardar en un archivo → `mas1-juego/assets/MAS1_Modelos.rbxmx`.
   - **Meterla en la place:** en `construir_place.py`, con referentes únicos y las `SharedStrings`; en `default.project.json`, `"$path"`.
   - **Probar `Seguidores`:** en Play, en el servidor, `plr:SetAttribute("MascotasEq", "aguila,nube,gorrion")` y `Alas = "avanzadas"`.
   - **Animación:** sin ids de Animation. Los clips de Blender se convierten a `Bone.Transform` con `clips_a_lua.py` (HECHO, 943e73f). Si se reimporta un modelo, hay que volver a pasar `clips_a_lua.py`, porque lee los huesos de `MAS1_Modelos.rbxmx`.
2. **Enemigos con mallas** en vez de piezas (`client/Entidades.client.lua`, carpetas `enemigos-v02`).
3. **Medir números** (duración de vuelos con potencia 0, 100 y 1000; dinero frente a precios) y **probar con 2 clientes** (Prueba → Servidor local) y los FPS.
4. **Sonidos:** 14 WAV en `mas1-sonidos/wav`. Se suben con el Gestor de recursos de Studio SOLO con el «sí» de Maikol, y los ids van en `src/Sonidos.lua`.
5. **Icono v02** (crítica del director): avatar de espaldas o de 3/4 con alas abiertas enormes, «+1» de ~40 %, aro dorado detrás y cielo en degradado.

## Trucos de Studio (exe `version-7062aec9dbe74b14`)
- **Abrir:** `Start-Process ...RobloxStudioBeta.exe -ArgumentList '"<ruta .rbxlx>"'`; después ShowWindow(3) + SetForegroundWindow.
- **Al abrir:** aviso de iluminación (Continuar en (837, 482)) y aviso de Rojo (Dismiss en (1268, 567)).
- **Barra de comandos:** clic en (600, 742), Ctrl+A, escribir y **Ctrl+Enter**. CurrentCamera o Destroy sacan «comando peligroso» → Continuar en (693, 467).
- **Importar:** (588, 80) → nombre de archivo en (372, 374) → Enter → nombre del modelo en (933, 197) (no pulsar Tab) → Importar en (967, 645). Cola de importación: X en (1445, 607).
- **Validación de UGC:** Avatar → (628, 80); volver a seleccionar el objeto con `Selection:Set`; menú → Hat.
- **Cerrar la place** sin guardar: CloseMainWindow → «No guardar» en (760, 418).
- **Play:** F5 / Shift+F5.
- **Cámara:** la de la vista Servidor durante Play a veces no hace caso; mejor medir por código.
- **Cámara del cliente para mirar algo:** en la vista Cliente, barra de comandos: `workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable` y `CFrame.lookAt(...)`.
- **F para lanzarse:** si la barra de comandos tiene el foco, la F se escribe ahí. Mejor el botón «¡LANZAR!» de la pantalla, en (660, 550).
- **Guardar algo importado:** Ctrl+S y después `python tools/extraer_rbxmx.py build/Mas1-prueba.rbxlx <Servicio/Carpeta> assets/<archivo>.rbxmx`.
- **Antes de tomar la pantalla**, mirar si Maikol está jugando (ventana en primer plano `RobloxPlayerBeta`). Si lo está, no tocarla.
