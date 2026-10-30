# Prueba de ejes FBX en Roblox Studio (30/10/2026)

Encargo de Linux 2.0: probar 1 mascota y 1 ala con rig montadas en un R15 antes de reexportar en lote. Probado con el 3D Importer de Studio `version-7062aec9dbe74b14`, en un avatar R15 creado con `CreateHumanoidModelFromDescription`.

## Lo que pasaba: todo lo exportado con rig salía mal

- **El esqueleto entraba girado 90° de cabeceo**, y como la malla sigue a los huesos, la mascota salía tumbada.
  - El águila quedaba con el pico mirando al cielo (`01-antes-aguila-tumbada-de-perfil.jpg`).
  - Las alas v02 quedaban planas, en horizontal a la altura de la cintura (`02-antes-…jpg`).
  - La caja de la malla sí entraba bien, porque lo girado son los huesos y no la malla en reposo.
- **Daba igual exportar con `axis_forward` `Z` o `-Z`:** el águila vieja (`Z`) y la de prueba (`-Z`) dan exactamente las mismas medidas de huesos.
- **En las mallas estáticas** (gorro UGC) el eje tampoco cambia nada. En las 4 combinaciones (`Z` / `-Z`, con y sin `bake_space_transform`), el +Y de Blender acaba en +Z de Roblox, que es la nuca del personaje.

## Regla probada

| Pieza | Exportar con | Resultado en Studio |
|---|---|---|
| **Con huesos** (mascotas, huevos, alas), frente en +Y de Blender | `bake_space_transform=True`, `axis_forward='Z'`, `axis_up='Y'` (el resto igual: escala 0.01, `primary_bone_axis='Y'`, `secondary_bone_axis='X'`, sin leaf bones) | **Derecha y mirando al frente** (`03-despues-…jpg`). Las medidas de huesos coinciden **exactamente** con Blender: cabeza 1,13 por delante y 1,58 por encima de la cola; párpado 1,19 por delante; punta del ala derecha 2,24 a la derecha, 1,06 detrás y 1,80 arriba. El clip `Fly` importado en el Editor de animación aletea bien (`04-despues-…jpg`). |
| Con huesos, frente en **−Y** (como las de Codex) | `bake_space_transform=True`, `axis_forward='-Z'` | Por deducción de lo anterior: con bake y `-Z`, el +Y de Blender sale mirando atrás, así que −Y sale al frente. **Sin probar.** |
| **Sin huesos**, frente en +Y | Girar la malla 180° (en Z de Blender) antes de exportar. El eje da igual. | Mirando al frente (gorro UGC). |
| Sin huesos, frente en −Y | Tal cual | Al frente (por la misma regla). |

## Hecho

- `tools/mas1_lib.py`: `fbx()` pone `bake_space_transform=True` cuando exporta una armadura. `FBX_FORWARD` sigue en `'Z'`.
- `tools/build_alas_avanzadas_v02.py`: lo mismo.
- `tools/reexportar_fbx.py`: reexporta rig y clips desde el `.blend` sin volver a renderizar.
- **Reexportados 73 FBX de 16 piezas:**
  - alas avanzadas v02;
  - águila, fénix y grifo (mascotas altas v02);
  - las 6 mascotas-enemigo v01;
  - los 6 huevos alados v03.
- `datos.json` de cada pieza apunta la regla.
- `validar_asset.py` da 0 fallos en águila, alas, nube y huevo épico.

## Sin cubrir

- Los GLB no se han tocado ni probado en Studio.
- Los enemigos `enemigos-v01/v02` no se han reexportado, porque el juego hace los enemigos con piezas.
- El kit FBX del mapa (`mapa-v01`, estático y con +Y en el sentido del vuelo) entraría girado 180°. El juego usa la versión en piezas de Roblox, así que hoy no afecta.
- Solo se ha probado un clip (`Fly` del águila). El `Blink`, que solo lleva los canales de `Lid_R/L`, no se ha probado.
- Las piezas de Codex (gorrión, golondrina, alas iniciales y robóticas…) siguen exportadas sin bake: el encargo está en `PARA-CODEX-2026-10-30-ejes.md`.
