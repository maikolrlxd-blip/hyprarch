# +1 de lanzamiento por segundo — arte que hace Claude (nube, Blender/bpy 5.0.1)
Proyecto de Codex; aquí solo lo que hace Claude para ayudar, sin tocar nada de la carpeta de Codex (`...\outputs\mas-1-lanzamiento`). Estilo pedido: cercano a *Steal a Brainrot* (vivo, grueso, colorido).

## Entregas
| Pieza | Carpeta | Triángulos | Estado |
|---|---|---|---|
| Aro de bronce / plata / oro | `aros/` | 192 cada uno | v0.1 (borrador): diámetro 11,3 studs, grosor 1,3; FBX (escala Roblox: global_scale 0.01) y GLB; textura pintada con franjas y rayas oscuras |
| Alas AVANZADAS (oscuras con turquesa y pinchos) | `alas-avanzadas/` | 316 | v0.1 (borrador): una malla, un material (atlas 512), 5 huesos (Raiz, AlaI_1/2, AlaD_1/2), clips Deploy 1,0 s / Flap 0,75 s / Glide 2,0 s; FBX del rig, FBX por clip y GLB con los 3 clips; 16 plumas-prisma, espolón y placas, envergadura ≈ 12,2 studs |
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
- FBX con axis_forward='-Z' entran girados 180° en el importador de Studio (Luto). Mis aros/alas v0.1 usan '-Z': reexportar con 'Z' si se usan. Sin confirmar con rig.
- Sin push de lo del Coordinador/Codex hasta OK de Maikol.
