# Estado del encargo "apocalipsis" (arte en Blender) — juego Luto

Actualizado el 2026-10-29 por la sesión del PC (Claude). **El traspaso con el estado exacto de las armas en mano, los archivos y el git está en `PUNTO-DE-RETOMA.md`.** El encargo completo está en `ENCARGO.md` y el estilo en `taller-ia/ESTILO.md` (Poli Pintado). El resumen de la noche está en `RESUMEN-NOCHE.md`. Lo que va después del 23/10 (armas en mano) está en este mismo archivo, más abajo.

## Qué falla o falta (primero)
- **Armas y manos** (2026-10-23, probado en Studio): las plantillas `LUTO_VM` y `LUTO_Armas` están montadas y los 19 clips de primera persona, publicados (ids en `apocalipsis-juego/src/Animaciones.lua`).
  - En primera persona se ve el arma abajo a la derecha con manga oliva y mano piel; 1/2/3, R y F la cambian y la animan.
  - Tras la prueba de Maikol se arregló que el arma desapareciera (la raíz suelta caía por debajo del mapa), que estorbara y que la sangre fuera enorme. Esos arreglos están en el repo (`b8fb176`), pero **no en el `.rbxl`**.
  - **Falta animar al personaje en tercera persona** (Maikol eligió animarlo): unos 19 clips R15 más. Sin empezar.
- **Partida de prueba completa en `Luto-jugable.rbxl`** (2026-10-23, configuración real). Funciona:
  - ronda 1 superada y ronda 2 empezada;
  - 6 zombis muertas que dan 10 monedas cada una;
  - en la tienda se compró munición (−52) y sale el aviso de monedas insuficientes;
  - las teclas 1/2/3, R, F y E responden.

  Fallos del código del director (avisados):
  - los disparos salen de la cabeza con la dirección de la cámara, así que en tercera persona falla lo que no está en la mira;
  - las zombis se paran a alcance + 2 studs y solo atacan por debajo del alcance, así que nunca pegan;
  - el jefe solo avanza 4 studs por cada recálculo de ruta, porque compara la distancia al punto de ruta en 3D;
  - con muchas zombis, los nombres «Zombi» y sus barras se amontonan.
- **Cuerpo base de los jugadores** (`src/Apariencia.lua`, del director):
  - los colores salen exactos y no queda ropa ni accesorios del avatar;
  - pero la cabeza conserva la cara sonriente por defecto de Roblox (capturas `renders/Studio_Luto_cuerpo_base_*.jpg`).
- **Mapa:** en `LUTO_Mapa` hay dos piezas `Tienda_municion` y dos `Tienda_curar`, y solo una de cada par lleva el prompt. Hay que revisar `MapaColisionesMarcadores.lua`.
- **Animaciones de la zombi y los jefes:** publicadas (12 clips; ids en `zombi-mujer/ESTADO.md`). Los tres fallos de servidor que vio la primera prueba ya los arregló el director:
  - prioridades;
  - `BreakJointsOnDeath`;
  - que el jefe se subiera al jugador.

  Ahora la zombi muerta queda tendida entera.
- **Ambiente v2** (`mapa/ambiente-roblox.lua`, aplicado en los dos places): cumplido.
  - Bruma de polvo gris-marrón densa (Density 0,5, Haze 4, Glare 0) que tapa el cielo azul por defecto, sin subir texturas.
  - Sol a unos 35° y en diagonal a las calles (latitud 55, ClockTime 15,2).
  - Bloom bajo, y el `Bloom` de la plantilla de Roblox apagado: se sumaba al nuestro.
  - El cielo de arriba aún tira un poco a verde grisáceo (`renders/Studio_Luto_ambiente_v2_*.jpg`).
- **Rendimiento:** con 8 zombis a la vez, el servidor va a 60 Hz (0,2 ms por Heartbeat) y el cliente a 60 FPS.
- **Rutas:** los 12 spawns tienen ruta con PathfindingService tanto para la zombi (radio 2) como para el jefe (radio 3).
- **Armas (v5):** sus fallos están en `armas/<arma>/ESTADO.md`:
  - la manga tapa la pantalla al montar la corredera de la pistola;
  - la escopeta se ve fina en primera persona.
- **Mujer zombi (v5):** el pelo, de cerca, se ve rígido y se nota la costura de las rodillas.
- **Jefes:** La Alta todavía no tiene identidad propia, y en los dos la única deformación son los brazos largos.
- **Mapa (v3):** los solares se repiten, el borde termina en seco y el follaje es de bloques.
- **PENDIENTE DE MAIKOL:** una prueba con 2 clientes. El push ya no necesita su OK, porque lo dijo él el 2026-10-23.
- **Place jugable para Maikol:** `C:\Users\maiko\Documents\Luto\Luto-jugable.rbxl`. Al lado está `LEEME-JUGAR.txt` con los pasos y los controles, y hay copia en `C:\Users\maiko\Backups\luto\`.

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
- **Animaciones:**
  - `tools/exportar_animaciones_roblox.py` saca de cada `.blend` un `integracion/Animaciones_*.rbxmx` con las KeyframeSequence.
  - Se inserta en `ServerStorage` y cada secuencia se publica con clic derecho > Guardar / Exportar > Guardar en Roblox.
  - Los ids están en `zombi-mujer/ESTADO.md` y en el de cada jefe.
- **Segunda prueba en Studio (2026-10-23):**
  - Copia del place antes y después en `C:\Users\maiko\Backups\luto\`.
  - Las capturas del HUD a 1920 × 1080 (emulador de dispositivos de Studio; la pantalla del PC es de 1024 × 768) están en `renders/Studio_Luto_HUD_1080_*.jpg`.
  - El script de prueba con `JEFE_CADA = 1` quedó en `ServerStorage.LUTO_Pruebas` del place y no se ejecuta.

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
