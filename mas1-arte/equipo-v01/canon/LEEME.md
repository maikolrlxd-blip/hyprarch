# Cañón pajarero (de Codex) para el lobby

Maikol (01/11): «usa el cañón que hizo ChatGPT».

- **Origen:** `Canon-pajarero-v01.blend` de Codex (`art/equipo-inicial-v01`, solo lectura).
  - En Blender apunta a +Y, y 1 unidad = 1 stud (3,8 × 4,8 × 5,7).
  - Rig de 3 huesos (Root, Barrel, Lever) con 28 mallas rígidas y el clip `Launch_recoil`.
- **`CanonPajarero.fbx`:** exportado con `tools/exportar_rig_roblox.py` y `FRENTE=+Y`.
- **Importado en Studio (Importar 3D):**
  - Las mallas y la textura (`rbxassetid://131423038722652`) se subieron a la cuenta de Maikol.
  - El importador montó las mallas rígidas con Motor6D. Con `bake` + `axis_forward='Z'` la boca salió hacia +Z, al revés que en los rigs con piel. Un rig de piezas rígidas se comporta como un modelo estático.
  - Arreglo: girar el pivote 180°, llamar al modelo `Canon` y meterlo en la carpeta `ReplicatedStorage.MAS1_Equipo`.
  - Se guardó con Ctrl+S y `mas1-juego/tools/extraer_rbxmx.py build/Mas1-prueba.rbxlx ReplicatedStorage/MAS1_Equipo assets/MAS1_Equipo.rbxmx`.
- **En el juego:** `server/Lobby.server.lua` lo pone a escala 3 en (0, 0, −22). Comprobado en Play: la boca queda en Z = −26,8 y la trasera en Z = −17,5, apuntando a la plataforma `MAS1_Canon` (Z = −38).
- **Pendiente:** el retroceso (`Launch_recoil`) al lanzarse.
