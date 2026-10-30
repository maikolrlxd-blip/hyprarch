# +1 de lanzamiento por segundo — arte que hace Claude (nube, Blender/bpy 5.0.1)
Proyecto de Codex; aquí solo lo que hace Claude para ayudar, sin tocar nada de la carpeta de Codex (`...\outputs\mas-1-lanzamiento`). Estilo pedido: cercano a *Steal a Brainrot* (vivo, grueso, colorido).

## Entregas
| Pieza | Carpeta | Triángulos | Estado |
|---|---|---|---|
| Aro de bronce / plata / oro | `aros/` | 192 cada uno | v0.1 (borrador): diámetro 11,3 studs, grosor 1,3; FBX (escala Roblox: global_scale 0.01) y GLB; textura pintada con franjas y rayas oscuras |
| Alas AVANZADAS (oscuras con turquesa y pinchos) | `alas-avanzadas/` | 316 | v0.1 (borrador): una malla, un material (atlas 512), 5 huesos (Raiz, AlaI_1/2, AlaD_1/2), clips Deploy 1,0 s / Flap 0,75 s / Glide 2,0 s; FBX del rig, FBX por clip y GLB con los 3 clips; 16 plumas-prisma, espolón y placas, envergadura ≈ 12,2 studs |
| **Alas AVANZADAS v0.2** (rehechas desde cero por el Coordinador, estilo Codex) | `alas-avanzadas-v02/` | 2.868 | v0.2: brazo óseo con espinas y cuerno, 4 filas de plumas lanceoladas, turquesa apagado, 7 huesos, clips Deploy/Flap/Glide; **Flap rehecho el 29/10 (recoger → extender → impulsar → recoger, razón plegada/extendida 0,25)**, textura con sangrado de bordes; fallos y límites en su `ESTADO.md`. Sustituye a v0.1 |
| **Mascotas altas v02** (águila legendaria, grifo mítico, fénix Robux; rehechas desde cero tras «se ve feo y buguiado» sobre la v01) | `mascotas-altas-v02/` | 4.044 / 4.518 / 4.458 | v02: cuerpo rechoncho, escamas en relieve, alas en arco de plumas en abanico, cola unida, sin contorno negro; **patas que cuelgan al volar y parpadeo** (12 huesos, 14 el grifo) y clips Fly/Glide/Celebrate con el aleteo nuevo (razón 0,564 / 0,549 / 0,526) + Blink; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sin probar en Roblox |
| **Huevos alados v01** (idea de Maikol: los huevos voladores con alas dan mascotas; común, poco común, raro, legendario y mítico) | `huevos-alados-v01/` | 1.056–1.344 | v01: huevo facetado como el cofre de Codex, patrón por rareza, grieta en zigzag con el interior claro, alas de plumas en flecha que crecen con la rareza; 7 huesos y clips Fly/Glide/Hatch; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sin probar en Roblox |
| **Enemigos voladores v01** (nube gruñona, nubarrón de tormenta, ovni, meteorito) | `enemigos-v01/` | 628–1.274 | v01: objetos con cara (ojos diminutos con párpados, cejas enfadadas), clips Idle/Hit/Defeat/Blink; validación correcta, 0 piezas sueltas, 0 caras coplanares; zonas propuestas sin aprobar; fallos y límites en su `ESTADO.md`. Sin probar en Roblox |
| **Enemigos voladores v02 (voxel)** (globo, nube gruñona, nubarrón, cometa, ovni, meteorito) | `enemigos-v02/` | 428–1.488 | v02: los seis en voxel de 0,2 como una familia (Maikol, 30/10); clips Idle/Hit/Defeat/Blink; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sustituye a la v01. Sin probar en Roblox |
| **Huevos alados v02** (seis rarezas: se suma el épico de `Mascotas.lua`) | `huevos-alados-v02/` | 928–1.636 | v02: cada huevo cambia de tamaño (cáscara de 2,0 a 3,0 studs), forma y alas (de 3 a 6 primarias, cresta en el legendario, doble abanico en el mítico), no solo de color; mismo rig y clips Fly/Glide/Hatch; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sustituye a la v01. Sin probar en Roblox |
| **Mascotas de los enemigos v01** (versión amable: nube, globo, nubarrón, ovni, meteorito, cometa) | `mascotas-enemigos-v01/` | 428–1.488 | v01: las piezas voxel de los enemigos v02 con cara amable y más pequeñas según su rareza de `Mascotas.lua`; clips Fly/Glide/Celebrate en bucle y Blink; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sin probar en Roblox |
| **Huevos alados v03** (silueta propia por rareza: copete, cuernos, cresta, halo; alas de 0,6 a 1,6) | `huevos-alados-v03/` | 1.000–2.020 | v03 (segunda crítica del director): tamaños mucho más separados (de 2,8 a 6,9 de envergadura) y un extra por rareza; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sustituye a la v02. Sin probar en Roblox |
| **Mapa v01** (Mar de Nubes x3 → Tormenta x4 → Cielo alto x5 → Espacio x6, después de la Pradera de Codex) | `mapa-v01/` | unos 85.000 en 24 piezas (ninguna pasa de 10.000) | v01, solo lo visual: kit en Blender (FBX/GLB por pieza, una textura de paleta) y la misma distribución en 3.112 piezas nativas de Roblox (`mapa-v01/roblox/`: modelo `.rbxmx` y place `.rbxlx` de prueba, sin mallas ni subidas). Largo y multiplicadores provisionales; sin cielo por zona ni colisiones de juego (código para después); fallos y límites en su `ESTADO.md`. Sin probar en Studio |
| Boceto HUD de vuelo | `ui-mock/hud_vuelo.png` | — | boceto HTML (no es Roblox) |

## Crítica (v0.1)
- ✔ Se leen a distancia: franjas vivas, contraste, sin brillos.
- ✘ Son un toro facetado liso: falta carácter (sin adornos, sin brillo propio; el brillo irá con partículas en Roblox).
- ✘ Poco polígono (192): a cámara cercana se nota la facetación de 16 segmentos.
- ✘ Sin importar ni probar en Studio; la dirección de las franjas y la colisión (deben ser atravesables) están sin comprobar.
- ✘ La figura de escala del render es un bloque; sirve solo como referencia de 6 studs.
Regenerar: `python3 tools/build_aros.py` (necesita `bpy`, numpy y Pillow).

## Crítica alas avanzadas v0.1
- ✔ Se lee de lejos como unas alas oscuras con raya turquesa; el abanico de plumas y la forma escalonada funcionan; sin brillos.
- ✘ Los pinchos son pocos: solo un espolón por ala y las puntas; para "alas con pinchos" falta más agresividad (pinchos en el borde, puntas más largas).
- ✘ Demasiado simétricas y rígidas: parecen un abanico plano, sin la silueta orgánica de un ala; falta una curva en el hueso externo.
- ✘ El turquesa es muy neón comparado con una referencia "oscura/turquesa" que no he visto (pendiente de la imagen que dio Maikol).
- ✘ El clip Deploy no pliega del todo (en el fotograma 1 las alas aún quedan casi abiertas): revisar ángulos de pliegue.
- ✘ Sin importar ni probar en Roblox: los 5 huesos están como huesos de Blender, no como Motor6D; hay que armarlo en Studio.

## Capa visual en Luau (mas1-juego/) — SIN PROBAR EN STUDIO
- Tema.lua, HudVuelo.client.lua, Efectos.client.lua, Efectos.lua, DemoVisual.server.lua (demo con `workspace:SetAttribute("MAS1_Demo", true)`).
- Solo comprobada la sintaxis con lupa. Falta: Rojo + capturas 1920x1080 y móvil.

## 29/10 — Aviso del Coordinador
- Alas avanzadas v0.2 rehechas por él en estilo Codex (2.788 tris, ~10 studs, rig Root+Wing/Mid/Tip, clips Deploy/Flap/Glide); en textura y exportación. Mis alas v0.1 quedan reemplazadas.
- Studio: Maikol denegó el control del equipo a la versión nueva. Bloqueado: refrescar Luto-jugable.rbxl, probar mas1-juego, tarea de Antigravity.
- CORRECCIÓN del Coordinador: el giro de 180° de Luto fue porque esas mallas miraban a +Y y salieron con '-Z'. Modelos que miran a -Y salen con '-Z' (Codex); los que miran a +Y, con 'Z'. Mis aros son simétricos; las alas v0.1 quedan reemplazadas. Sin comprobar con rig en Studio.
- Sin push de lo del Coordinador/Codex hasta OK de Maikol.

## 29/10 — Relevo de Codex
- Mascotas: nueva referencia «Roba un huevo / Steal an Egg» (aún no aplicada por Codex). Alas iniciales-v02, robóticas-v02 y comunes-v03 con extender/recoger (Blender, sin Roblox).
- mas1-juego existe en el repo; Codex no lo auditó ni lo probó.

## 30/10 — Decisión de Maikol: los enemigos también se consiguen como mascotas
- Falta definir cómo se obtienen, rareza y bonus. Como mascota necesitan clips Fly/Glide/Celebrate (+Blink) y expresión amable.
- Propuesta: cubrir con ellos las 2 poco comunes + 2 raras que faltan (hoy 5/9 mascotas).

## 31/10 — Eje FBX comprobado en Studio (aviso del Coordinador)
- Los FBX de mascotas y alas (frente +Y en Blender, axis_forward='Z') entran mirando hacia ATRÁS en Roblox: el importador pone el frente en +Z, que es la nuca del personaje (los personajes miran a -Z). Al montarlos, girarlos 180° o reexportarlos girados.
- Ojo: los de Codex salen con '-Z' y frente -Y; hay que comprobarlos uno a uno con rig/accesorio. Regla: probar CADA tipo de asset en Studio antes de dar el eje por bueno.
- **CORREGIDO por el Coordinador tras probarlo con rig (30/10 tarde; detalle en `pruebas-studio/2026-10-30-ejes/LEEME.md`):** lo de arriba solo vale para mallas SIN huesos (el gorro UGC). Con huesos el fallo era otro: sin `bake_space_transform` el esqueleto entraba girado 90° y la mascota/ala salía tumbada (con 'Z' o con '-Z'). Regla: con huesos, `bake_space_transform=True` + `axis_forward='Z'` (frente +Y; Codex, frente -Y: '-Z'); sin huesos, girar la malla 180° si mira a +Y. Alas v02, mascotas altas v02, mascotas-enemigo v01 y huevos v03 ya reexportados así (NO girarlos al montarlos).
