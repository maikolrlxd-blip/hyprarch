# Punto de retoma del Coordinador (01/11/2026, de madrugada)

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

## En marcha
- Comprobación de caras solapadas del mapa largo (`MAPA_RBX_FASE=check blender ... mapa_roblox.py`). Si da caras solapadas, arreglarlas (hay parpadeo en Roblox).

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
   - **Animación:** no hay ids de Animation. Propuesta: aletear con `Bone.Transform` desde el cliente (eje = la dirección de frente en el espacio del hueso).
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
