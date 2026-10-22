# Kit v03 — playa/desierto (Blender en la nube, bpy 5.0.1)
Estado: **lote 1, versión 0.1 (borrador honesto)**. Todo generado por código (`kit_v03.py`), facetado limpio + texturas pintadas (`pintura.py`), sin Parts ni Terrain de fábrica.

| Modelo | Triángulos | Clips GLB |
|---|---|---|
| bote_remos / lancha / velero | 120 / 120 / 100 | Flotar (48f, bucle), Atracar (90f) |
| saguaro1 / saguaro2 | 282 | Mecer (72f, bucle) |
| cactus_barril / nopal | 131 / 84 | Mecer |
| palmera | 426 | Mecer |
| piezas_playa (concha, estrella, tronco, muelle) | 325 | — |

Renders en `renders/` (figura de referencia de 6 studs a la izquierda). Clips verificados leyendo el JSON de cada GLB.

## Pendiente / defectos conocidos (no vender como terminado)
- Cascos de botes: proa/popa abiertas y rejilla de 5 vértices tosca; el bote de remos es demasiado plano.
- Palmera: frondas pequeñas, cámara la recorta; saguaro: brazos cortos.
- Piezas de playa fuera de cuadro en el render; falta escalar a studs reales en el juego.
- Falta: volcán, desastres, cofres, meta, terreno por teselas, slimes raros. Falta revisión visual de Maikol / Antigravity.
Regenerar: `python3 kit_v03.py` (requiere `bpy`, numpy, Pillow).
