# Coordinación del arte de «+1 de lanzamiento por segundo» (Coordinador ↔ Codex)
Escrito el 2026-10-29 por el Coordinador (Claude en el PC de Maikol). Aquí solo lo que hago yo, dentro de `mas1-arte\` del repo hyprarch. No toco nada de la carpeta de Codex (`...\outputs\mas-1-lanzamiento`); como no hay canal directo, esto se relee desde ahí o lo relaya el director.

## Quién hace qué
| Pieza | Hace | Estado (29/10) |
|---|---|---|
| Alas iniciales, cañón, planeador, cofre, mascotas comunes (gorrión, golondrina), zona Pradera, alas robóticas | Codex | hechas, sin probar en Roblox |
| **Alas avanzadas v0.2** (oscuras con turquesa y pinchos) | Coordinador | hechas en `alas-avanzadas-v02\` (modelo, textura, rig, clips, validación); falta la revisión de Maikol |
| **Águila legendaria, grifo mítico, fénix (Robux, con el fuego aparte)** | Coordinador | águila y grifo en construcción en `mascotas-altas-v01\`, el fénix después. Mismo rig de 8 huesos y clips que las comunes; Codex: si ya tienes alguna en marcha, dilo y me salto esa |
| Mascotas poco comunes y raras (2 + 2) | Codex; si no llega, el Coordinador | sin empezar por mi parte |
| Enemigos voladores por zona, zonas intermedias, icono y miniaturas | Coordinador, en ese orden, después de las mascotas | sin empezar |

## Convenciones que sigo para encajar con las de Codex
- **Alas:** una malla, un material, atlas 1024, origen en el punto de montaje de la espalda (`BodyBackAttachment`). Huesos `Root`, `Wing_R/L`, `Tip_R/L` como las suyas, más `Mid_R/L` (codo). Clips `Deploy`, `Flap`, `Glide`.
- **Mascotas altas voladoras:** huesos `Root, Body, Head, Tail, Wing_L/R, Tip_L/R` y clips `Fly`, `Glide`, `Celebrate` como el gorrión y la golondrina; estilo escalonado con ojos pequeños y picos anchos.
- **FBX y ejes (corrección del 29/10):** `global_scale=0.01` (1 unidad = 1 stud). Mis piezas miran a **+Y** en Blender y salen con `axis_forward='Z'` (variable `FBX_FORWARD` en mi script); las de Codex miran a **−Y** (el frente por defecto de Blender: cara en y<0, cola y alas en y>0) y salen con `'-Z'`. Los dos casos dejan el frente en el mismo lado del FBX, así que deberían entrar igual en Studio. Origen del aviso: los FBX de Luto (frente +Y) exportados con `'-Z'` entraron girados 180° (mapa, zombi, armas, comprobado en Studio con mallas sueltas), de ahí mi `'Z'`. Sin confirmar con rig ni accesorios. Un aviso anterior mío decía que los FBX de Codex entrarían girados: era un error mío, no lo es.
- **Pruebas:** todo lo mío son renders de Blender. Nada está probado en Roblox (importación, huesos como `Bone`/`Motor6D`, animaciones, ataduras de accesorios).
- **Git:** commits locales pequeños; sin push hasta el «sí» de Maikol; nada de `.rbxl`, `.blend` pesados ni claves.
