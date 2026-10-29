# +1 de lanzamiento por segundo — arte que hace Claude (nube, Blender/bpy 5.0.1)
Proyecto de Codex; aquí solo lo que hace Claude para ayudar, sin tocar nada de la carpeta de Codex (`...\outputs\mas-1-lanzamiento`). Estilo pedido: cercano a *Steal a Brainrot* (vivo, grueso, colorido).

## Entregas
| Pieza | Carpeta | Triángulos | Estado |
|---|---|---|---|
| Aro de bronce / plata / oro | `aros/` | 192 cada uno | v0.1 (borrador): diámetro 11,3 studs, grosor 1,3; FBX (escala Roblox: global_scale 0.01) y GLB; textura pintada con franjas y rayas oscuras |
| Alas AVANZADAS (oscuras con turquesa y pinchos) | `alas-avanzadas/` | 316 | v0.1 (borrador): una malla, un material (atlas 512), 5 huesos (Raiz, AlaI_1/2, AlaD_1/2), clips Deploy 1,0 s / Flap 0,75 s / Glide 2,0 s; FBX del rig, FBX por clip y GLB con los 3 clips; 16 plumas-prisma, espolón y placas, envergadura ≈ 12,2 studs |
| **Alas AVANZADAS v0.2** (rehechas desde cero por el Coordinador, estilo Codex) | `alas-avanzadas-v02/` | 2.868 | v0.2: brazo óseo con espinas y cuerno, 4 filas de plumas lanceoladas, turquesa apagado, 7 huesos, clips Deploy/Flap/Glide; **Flap rehecho el 29/10 (recoger → extender → impulsar → recoger, razón plegada/extendida 0,25)**, textura con sangrado de bordes; fallos y límites en su `ESTADO.md`. Sustituye a v0.1 |
| **Mascotas altas v02** (águila legendaria, grifo mítico, fénix Robux; rehechas desde cero tras «se ve feo y buguiado» sobre la v01) | `mascotas-altas-v02/` | 4.044 / 4.518 / 4.458 | v02: cuerpo rechoncho, escamas en relieve, alas en arco de plumas en abanico, cola unida, sin contorno negro; **patas que cuelgan al volar y parpadeo** (12 huesos, 14 el grifo) y clips Fly/Glide/Celebrate con el aleteo nuevo (razón 0,564 / 0,549 / 0,526) + Blink; validación correcta, 0 piezas sueltas, 0 caras coplanares; fallos y límites en su `ESTADO.md`. Sin probar en Roblox |
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
