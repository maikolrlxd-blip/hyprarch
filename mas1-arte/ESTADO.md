# +1 de lanzamiento por segundo — arte que hace Claude (nube, Blender/bpy 5.0.1)
Proyecto de Codex; aquí solo lo que hace Claude para ayudar, sin tocar nada de la carpeta de Codex (`...\outputs\mas-1-lanzamiento`). Estilo pedido: cercano a *Steal a Brainrot* (vivo, grueso, colorido).

## Entregas
| Pieza | Carpeta | Triángulos | Estado |
|---|---|---|---|
| Aro de bronce / plata / oro | `aros/` | 192 cada uno | v0.1 (borrador): diámetro 11,3 studs, grosor 1,3; FBX (escala Roblox: global_scale 0.01) y GLB; textura pintada con franjas y rayas oscuras |
| Boceto HUD de vuelo | `ui-mock/hud_vuelo.png` | — | boceto HTML (no es Roblox) |

## Crítica (v0.1)
- ✔ Se leen a distancia: franjas vivas, contraste, sin brillos.
- ✘ Son un toro facetado liso: falta carácter (sin adornos, sin brillo propio; el brillo irá con partículas en Roblox).
- ✘ Poco polígono (192): a cámara cercana se nota la facetación de 16 segmentos.
- ✘ Sin importar ni probar en Studio; la dirección de las franjas y la colisión (deben ser atravesables) están sin comprobar.
- ✘ La figura de escala del render es un bloque; sirve solo como referencia de 6 studs.
Regenerar: `python3 tools/build_aros.py` (necesita `bpy`, numpy y Pillow).
