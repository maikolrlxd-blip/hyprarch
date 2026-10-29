# Coordinación del arte de «+1 de lanzamiento por segundo» (Coordinador ↔ Codex)
Escrito el 2026-10-29 por el Coordinador (Claude en el PC de Maikol). Aquí solo lo que hago yo, dentro de `mas1-arte\` del repo hyprarch. No toco nada de la carpeta de Codex (`...\outputs\mas-1-lanzamiento`); como no hay canal directo, esto se relee desde ahí o lo relaya el director.

## Quién hace qué
| Pieza | Hace | Estado (29/10) |
|---|---|---|
| Alas iniciales, cañón, planeador, cofre, mascotas comunes (gorrión, golondrina), zona Pradera, alas robóticas | Codex | hechas, sin probar en Roblox |
| **Alas avanzadas v0.2** (oscuras con turquesa y pinchos) | Coordinador | hechas en `alas-avanzadas-v02\` (modelo, textura, rig, clips, validación); `Flap` rehecho el 29/10 como pidió Maikol (recoger→extender→impulsar→recoger); falta la revisión de Maikol |
| **Águila legendaria, grifo mítico, fénix (Robux, con el fuego aparte)** | Coordinador | **v02** en `mascotas-altas-v02\` (la v01 la rechazó Maikol: «se ve feo y buguiado»; rehechas desde cero el 29/10). Mismo rig de 8 huesos y clips que las comunes; aleteo recoger→extender→impulsar→recoger. Codex: si ya tienes alguna en marcha, dilo y me salto esa |
| Mascotas poco comunes y raras (2 + 2) | Codex; si no llega, el Coordinador | sin empezar por mi parte |
| Enemigos voladores por zona, zonas intermedias, icono y miniaturas | Coordinador, en ese orden, después de las mascotas | sin empezar |

## Referencia nueva de Maikol (29/10) para las mascotas
Maikol pidió «tomar referencia de Roba un huevo (Steal an Egg) en los diseños de las mascotas». Lo que saqué de sus iconos está en `REFERENCIA-ROBA-UN-HUEVO.md` (voxeles chunky, ojos diminutos, escamas de plumas en relieve, sombras lavanda; **el contorno negro grueso es de las comunes y medias, las raras no lo llevan**; el detalle sube con la rareza: alas grandes en capas con degradado y adornos dorados en rombo). Lo apliqué a águila, grifo y fénix (v02, sin contorno). **Codex:** las comunes no llevan escamas ni contorno; decide si las adaptas (el contorno está hecho para cualquier malla de Blender en `tools\contorno_negro.py`, solo depende de `bpy`; las raras de Roba un huevo no lo llevan).

## Convenciones que sigo para encajar con las de Codex
- **Alas:** una malla, un material, atlas 1024, origen en el punto de montaje de la espalda (`BodyBackAttachment`). Huesos `Root`, `Wing_R/L`, `Tip_R/L` como las suyas, más `Mid_R/L` (codo). Clips `Deploy`, `Flap`, `Glide`.
- **Mascotas altas voladoras:** huesos `Root, Body, Head, Tail, Wing_L/R, Tip_L/R` y clips `Fly`, `Glide`, `Celebrate` como el gorrión y la golondrina; estilo escalonado con ojos pequeños y picos anchos.
- **Aleteo (corrección de Maikol, 29/10):** `Fly` y `Flap` van **recoger → extender → impulsar → recoger**: arriba extendidas, el empuje baja el ala con la punta retrasada, abajo se recogen (muñeca y punta flexionan hacia atrás mientras suben) y arriba se extienden otra vez. Se mide con la razón envergadura plegada/extendida de `tools\validar_asset.py` (las comunes de Codex miden ≈ 0,56; mis mascotas altas 0,53–0,56 y las alas del jugador, `Flap`, 0,25).
- **FBX y ejes (corrección del 29/10):** `global_scale=0.01` (1 unidad = 1 stud). Mis piezas miran a **+Y** en Blender y salen con `axis_forward='Z'` (variable `FBX_FORWARD` en mi script); las de Codex miran a **−Y** (el frente por defecto de Blender: cara en y<0, cola y alas en y>0) y salen con `'-Z'`. Los dos casos dejan el frente en el mismo lado del FBX, así que deberían entrar igual en Studio. Origen del aviso: los FBX de Luto (frente +Y) exportados con `'-Z'` entraron girados 180° (mapa, zombi, armas, comprobado en Studio con mallas sueltas), de ahí mi `'Z'`. Sin confirmar con rig ni accesorios. Un aviso anterior mío decía que los FBX de Codex entrarían girados: era un error mío, no lo es.
- **Pruebas:** todo lo mío son renders de Blender. Nada está probado en Roblox (importación, huesos como `Bone`/`Motor6D`, animaciones, ataduras de accesorios).
- **Git:** commits locales pequeños; sin push hasta el «sí» de Maikol; nada de `.rbxl`, `.blend` pesados ni claves.
