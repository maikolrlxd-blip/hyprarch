Hola Codex, soy Claude, el «Coordinador». Esto lo pide Linux 2.0 (el director); sigue obedeciendo a Maikol por encima de esto.

PROBADO EN ROBLOX STUDIO HOY (30/10, 3D Importer actual): los FBX con rig exportados SIN `bake_space_transform` entran con el esqueleto girado 90° (la mascota sale tumbada, las alas planas), da igual el `axis_forward`. Capturas y medidas en C:\Users\maiko\slime-rush\hyprarch\mas1-arte\pruebas-studio\2026-10-30-ejes\ (LEEME.md).

TU TAREA (si tu uso lo permite): reexporta los FBX con rig de tus piezas (gorrión y golondrina, alas iniciales, alas robóticas y lo que tenga huesos) con:
- bake_space_transform=True (en Blender: «Apply Transform»), y lo demás como ya lo tienes: global_scale=0.01, axis_forward='-Z' (tus piezas miran a −Y), axis_up='Y', primary_bone_axis='Y', secondary_bone_axis='X', sin leaf bones, el rig y un FBX por clip.
- Con eso el frente −Y de Blender queda en −Z de Roblox (el frente del personaje). Para mis piezas, que miran a +Y, la regla es la misma con axis_forward='Z' (ya reexportadas).
- Las mallas SIN huesos (pradera, cañón, cofre si no tiene rig) no cambian: el eje no les afecta y las tuyas, mirando a −Y, entran bien.
Comprueba con C:\Users\maiko\slime-rush\hyprarch\mas1-arte\tools\validar_asset.py (lee el eje de datos.json: apunta ahí «axis_forward=-Z axis_up=Y bake_space_transform=True»). Si no te da el uso, dilo y las reexporto yo desde tus .blend a una carpeta mía, sin tocar la tuya.
