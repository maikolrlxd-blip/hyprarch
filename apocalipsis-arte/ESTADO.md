# Estado del encargo "apocalipsis" (arte en Blender) — juego Luto

Actualizado el 2026-10-23 a las 06:20 por la sesión del PC (Claude). El encargo completo está en `ENCARGO.md` y el estilo en `taller-ia/ESTILO.md` (Poli Pintado). El resumen de la noche está en `RESUMEN-NOCHE.md`.

## Qué falla o falta (primero)
- **Animaciones en Roblox:** ningún clip está publicado todavía.
  - Las zombis y los jefes se deslizan sin andar en el juego.
  - Las armas no tienen sus clips en Studio.
  - Hay que importar los FBX de `clips/` con el Animation Editor, publicarlos con la cuenta de Maikol y que el servidor de Luto los cargue.
- **Armas (v5):** sus fallos están en `armas/<arma>/ESTADO.md`:
  - la manga tapa la pantalla al montar la corredera de la pistola;
  - la escopeta se ve fina en primera persona.
- **Mujer zombi (v5):** el pelo, de cerca, se ve rígido y se nota la costura de las rodillas.
- **Jefes:** La Alta todavía no tiene identidad propia, y en los dos la única deformación son los brazos largos.
- **Mapa (v3):** los solares se repiten, el borde termina en seco y el follaje es de bloques.
- **PENDIENTE DE MAIKOL:**
  - OK para subir los commits locales de esta madrugada;
  - publicar las animaciones, o decirme que lo haga yo en Studio;
  - una prueba con 2 clientes.

## Entregas
| Pieza | Carpeta | Triángulos | Estado |
|---|---|---|---|
| Pistola 9mm | `armas/pistola-9mm/` | 634 | v5 hecha |
| Escopeta | `armas/escopeta/` | 530 | v5 hecha |
| Subfusil | `armas/subfusil/` | 780 | v5 hecha |
| Mujer zombi | `zombi-mujer/` | 1966 | v5, **en Luto (Studio)** |
| La Lamentadora | `bosses/la-lamentadora-v02/` | 1966 (a 1,75×) | v0.2, importada en Studio |
| La Alta | `bosses/jefe-alta-v01/` | 1966 (a 2×) | v0.1, importada en Studio |
| Mapa 300×300 | `mapa/` | 30 850 (121 piezas) | v3, **en Luto (Studio)** |

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
