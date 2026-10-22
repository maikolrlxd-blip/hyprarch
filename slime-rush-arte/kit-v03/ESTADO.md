# Kit v03 — playa/desierto (Blender en la nube, bpy 5.0.1)
Estado: **lote 1, versión 0.2**. Generado por código (`kit_v03.py`), facetado + texturas pintadas (`pintura.py`). Sin Parts ni Terrain de fábrica.

| Modelo | Tamaño | Clips |
|---|---|---|
| bote_remos / lancha / velero | 9 / 15 / 12 studs de largo (286/262/218 tris) | Flotar, Atracar |
| saguaro1/2 | 11–12 de alto (522 tris) | Mecer |
| cactus_barril / nopal | 222 / 192 tris | Mecer |
| palmera | 13 de alto (698 tris) | Mecer |
| piezas_playa | 340 tris | — |

## Crítica (v0.2)
Mejorado: cascos cerrados con volumen, escala creíble, saguaro y palmera ya se leen, sin cuadrícula en las texturas.
Sigue mal: la textura parece papel arrugado; la proa de los botes es una cuña plana; la lancha es una caja con techo; el brazo izquierdo del saguaro casi no se ve; el nopal y el barril son blobs; la palmera tiene la copa vacía (sin cocos visibles) y la arena de prueba se repite; las piezas de playa son diminutas frente a la escena.
Falta: volcán, desastres, cofres, meta, terreno por teselas, slimes raros; revisión de Maikol/Antigravity.
Regenerar: `python3 kit_v03.py`.
