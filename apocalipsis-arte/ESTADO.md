# Estado del encargo "apocalipsis" (arte en Blender)

Actualizado el 2026-10-23 de madrugada por la sesión del PC (Claude). El encargo completo está en `ENCARGO.md`.

## Qué falla o falta (primero)
- **Armas: congeladas por decisión de Maikol** ("Ya déjale las armas así"), cada una con sus fallos conocidos:
  - **Pistola:** tiene un triángulo negro grande en el armazón, entre el guardamonte y la empuñadura.
  - **Escopeta:** el gatillo es una cuña negra demasiado grande, la madera sale muy saturada y en primera persona el arma se ve pequeña.
  - **Subfusil:** en primera persona la culata tapa un tercio de la pantalla.
  - El detalle de cada una está en `armas/<arma>/ESTADO.md`.
- **Zombi mujer:** la versión v3 realista está construida, pero aún no he hecho su crítica. Va lo siguiente.
- **Mapa:**
  - Calles: construido.
  - Props, vehículos, edificios, vegetación y ensamblado: construyéndose ahora.
- **Nada probado en Roblox Studio** con estos FBX: ni la importación de clips animados ni el `Tool.Grip`.
  - La escala sí está comprobada: coincide con el FBX de la roca que Codex validó en Studio (1 unidad de Blender = 1 stud).
- **Falta:** `RESUMEN-NOCHE.md`.

## Entregas
| Pieza | Carpeta | Triángulos | Clips | Estado |
|---|---|---|---|---|
| Pistola 9mm | `armas/pistola-9mm/` | 634 | Equipar, Disparo, Recargar, Reposo | congelada (v3b) |
| Escopeta de corredera | `armas/escopeta/` | 530 | Equipar, Disparo, Bombear, Recargar_Inicio/_Cartucho/_Fin, Recargar, Reposo | congelada (v2) |
| Subfusil | `armas/subfusil/` | 780 | Equipar, Disparo, Recargar, Amartillar, Reposo | congelado (v2) |
| Mujer zombi | `zombi-mujer/` | (v3, por medir) | Reposo, Caminar, Atacar, Caer | en crítica |
| Mapa 300×300 | `mapa/` | (por pieza) | — | en construcción |

- Cada arma trae modelo de mundo, viewmodel con brazos R15 y los mismos clips en los dos.
- Los clips están documentados en `armas-animaciones.md`.
- Los renders finales y las hojas de contacto están en `renders/`.

## Cómo se construye
Cada pieza tiene su script en `tools/`, que se ejecuta así:

```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P apocalipsis-arte\tools\build_<pieza>.py
```

- El script deja en la carpeta de la pieza:
  - el .blend;
  - los FBX y GLB;
  - `clips/` (FBX por clip);
  - `texturas/` (color de 1024 px);
  - `previews/`;
  - `datos.json`, con los triángulos y las medidas.
- Librerías comunes:
  - `ap_lib.py`: geometría facetada, horneado, pintura a mano en numpy, rig, clips, exportación y render.
  - `ap_armas.py`: viewmodel, brazos R15, IK y hojas de contacto.
  - `ap_piezas.py` y `ap_estilos.py`: piezas del mapa.
- Para comprobar la escala de un FBX: `tools/check_fbx_scale.py`.

## Decisiones ya tomadas
- **Unidades:** 1 unidad de Blender = 1 stud; delante es +Y y arriba es +Z.
- **Exportación FBX:** `global_scale=0.01`, `apply_scale_options=FBX_SCALE_ALL`, `axis_forward=-Z`, `axis_up=Y`.
- **Armas:**
  - Tamaño exagerado para que se lean en la mano de un R15: pistola de 1,5 studs, subfusil de 2,9 y escopeta de 4,0.
  - El origen está en la empuñadura.
- **Casquillos y cartuchos:** Roblox no anima la escala, así que en reposo esperan escondidos dentro del arma.
- **Zombi:** por petición de Maikol es una **mujer** y **realista**, con proporciones tipo Rthro. Sus piezas y huesos llevan los nombres R15.
