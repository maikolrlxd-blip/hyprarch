# Estado del encargo "apocalipsis" (arte en Blender) — juego Luto

Actualizado el 2026-10-23 a las 05:30 por la sesión del PC (Claude). El encargo completo está en `ENCARGO.md` y el estilo en `taller-ia/ESTILO.md` (Poli Pintado).

## Qué falla o falta (primero)
- **Armas:**
  - la v4 está subida;
  - la v5 se está construyendo: mangas del viewmodel más finas, recarga de la pistola sin tapar la pantalla, escopeta más cerca, inspecciones más visibles;
  - fallos que siguen: los de cada `armas/<arma>/ESTADO.md`;
  - **sin importar a Studio:** los clips (Animation Editor) y el Tool.
- **Mujer zombi:**
  - la v4 está hecha; la v5 en cola (sin zarpazos en el antebrazo y trazos de la cara más suaves);
  - **sin importar todavía a Studio**: el script `zombi-mujer/integracion/ArmarZombi.lua` ya está listo.
- **Jefes:** La Lamentadora v0.2 y La Alta, en cola. Salen de la misma base que la zombi: más grandes, brazos más largos y ropa de luto.
  - La v0.1 de Codex está guardada en `bosses/la-lamentadora-v01/`, con su crítica.
- **Mapa:** terminado y probado en Studio. Sus pegas menores están en `mapa/ESTADO.md`:
  - los solares se repiten;
  - el borde termina en seco;
  - el follaje es de bloques.
- **PENDIENTE DE MAIKOL:**
  - OK para subir los commits locales (mapa y La Lamentadora v0.1);
  - las animaciones de los zombis y las armas en Roblox se publican con su cuenta desde el Animation Editor.

## Entregas
| Pieza | Carpeta | Triángulos | Estado |
|---|---|---|---|
| Pistola 9mm | `armas/pistola-9mm/` | 634 | v4 subida, v5 en construcción |
| Escopeta | `armas/escopeta/` | 530 | v4 subida, v5 en construcción |
| Subfusil | `armas/subfusil/` | 780 | v4 subida, v5 en construcción |
| Mujer zombi | `zombi-mujer/` | 1966 | v4 hecha, v5 en cola |
| La Lamentadora | `bosses/la-lamentadora-v02/` | (≈1966, a 1,75×) | en cola |
| La Alta | `bosses/jefe-alta-v01/` | (≈1966, a 2×) | en cola |
| Mapa 300×300 | `mapa/` | 30 850 (121 piezas) | **terminado y probado en Studio** |

## Integración con Luto (`apocalipsis-juego/INTEGRACION.md`)
- **Place de prueba:** `C:\Users\maiko\Documents\Luto\Luto-prueba-2-mapa.rbxl`, con copia en `C:\Users\maiko\Backups\luto\`. Ya tiene:
  - `ServerStorage.LUTO_Plantillas.Mapa`, importado con el 3D Importer y la sesión de Maikol, más colisiones, marcadores y ambiente;
  - el servidor de Luto (desde Rojo) usa el mapa y la partida arranca en el cruce.
- **Zombi y jefes:**
  1. importar `<Nombre>_Estatico.fbx`;
  2. ejecutar su `integracion/ArmarZombi.lua` con el modelo seleccionado, que lo deja como rig R15 con HumanoidRootPart, Motor6D y Humanoid;
  3. moverlo a `LUTO_Plantillas` como `Zombi_Mujer`, `Jefe_lamentadora` o `Jefe_alta`.
- **Prueba de Luto en Studio:** el informe y el arreglo de una línea (`viva()` con un humanoide muerto) se le mandaron al director. No los commiteé yo.

## Cómo se construye
- Cada pieza tiene su script en `tools/`. Se ejecuta con:
  ```
  "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P apocalipsis-arte\tools\build_<pieza>.py
  ```
- Jefes: `ZOMBI_VARIANTE=lamentadora` o `alta`, con `build_zombi.py`.
- **Arreglo importante de esta noche:** `ap_lib.MB.finish` calcula la normal de las caras antes de triangular. Sin eso, los polígonos cóncavos salían con triángulos fuera del contorno, invertidos y negros (la «pared negra» de la Glock, las caras negras del mapa).

## Decisiones ya tomadas
- **Unidades y exportación:** 1 unidad = 1 stud, delante +Y y arriba +Z. FBX con `global_scale=0.01` y ejes −Z/Y. Comprobado en Studio con el mapa: 300 × 49,5 × 300 studs.
- **Zombi y jefes:** realistas, de proporciones tipo Rthro, con piezas y huesos R15. Sin gore.
- **Armas:** el origen está en la empuñadura y los casquillos se esconden dentro del arma en reposo. Los eventos y puntos están en `eventos.json` y `<Arma>_Eventos.lua`.
