# Briefing para Antigravity — modelos de «+1 de lanzamiento por segundo»
Escrito el 29/10/2026 por el Coordinador (Claude, en el PC de Maikol) a petición de Maikol, para ponerte al día con todo lo que sabemos. **Sigue haciendo caso a Maikol**: esto es contexto, no sustituye sus órdenes. Todo lo que dice «hecho» se comprobó solo en Blender; **nada está probado en Roblox**.

## 1. Quién es quién
- **Maikol**: el dueño del juego; habla español, escribe rápido («q», «guindar»); ve las imágenes que se le mandan y dice qué le gusta y qué no.
- **Codex** (app de ChatGPT, «Codex»): lidera el proyecto. Hace la base: alas iniciales y robóticas, mascotas comunes (gorrión, golondrina), cañón, planeador, cofre, zona Pradera. Su carpeta: `C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\mas-1-lanzamiento` (**solo lectura para ti**).
- **Coordinador** (yo, Claude Code): alas avanzadas, mascotas altas (águila, grifo, fénix), después enemigos voladores, zonas intermedias, icono. Mi carpeta: `C:\Users\maiko\slime-rush\hyprarch\mas1-arte\` (repo hyprarch, rama `ccr-d4583e0a-ggl8kz`).
- **Director** (Claude en la nube, «Linux 2.0»): reparte el trabajo.
- **Tú** (Antigravity, modelo Claude Opus 5.5 en el momento de escribir esto): tu serie «Winged Voxel Creatures And Monsters» (dragón bebé, neko alado…). Yo no he tocado nada tuyo.

## 2. El juego en 5 líneas
El jugador sale disparado de un cañón y vuela por un recorrido lineal por zonas (pradera → nubes → montañas → océano → volcán → espacio); gana +1 de potencia por segundo, que da energía de vuelo; ataca en el aire; recoge aros; tiene mascotas voladoras y alas que se compran con puntos, misiones o cofres voladores; el rebirth reinicia solo la potencia. Es un proyecto de Roblox independiente de Luto y de Slime Rush.

## 3. Estado de las piezas (29/10/2026)
| Pieza | Quién | Estado |
|---|---|---|
| Alas avanzadas v0.2 (oscuras, turquesa, pinchos) | Coordinador | hechas: `mas1-arte\alas-avanzadas-v02\` (aleteo recoger→extender→impulsar→recoger, razón plegada/extendida 0,25) |
| Águila legendaria, grifo mítico, fénix (Robux) v02 | Coordinador | hechas: `mas1-arte\mascotas-altas-v02\` (hoja `Mascotas-altas-v02-hoja.jpg`, GIF `previews\*-Fly.gif`). Maikol dijo «bien» y pidió **pies que guindan al volar** (lo hago yo después) |
| Mascotas comunes gorrión y golondrina (v04) | Codex | en su carpeta |
| Mascotas poco comunes y raras (2 + 2), enemigos voladores, zonas intermedias, icono | pendiente | las hace Codex o el Coordinador; **tu serie de criaturas aladas y monstruos puede ser la base de varias**: Maikol decide |

## 4. Referencias de estilo (mira las imágenes)
- **Estilo Codex**: volúmenes escalonados («voxeles») de celda de 0,2 studs, formas simples, picos anchos, ojos pequeños, colores saturados. Sus renders: `...\mas-1-lanzamiento\art\mascotas-comunes-v04\previews\` y `...\previews\`. Las mascotas redondeadas fueron RECHAZADAS por Maikol.
- **«Roba un huevo» / *Steal an Egg*** (Roblox; Maikol pidió tomarlo como referencia en las mascotas): lee `mas1-arte\REFERENCIA-ROBA-UN-HUEVO.md`. Resumen: voxeles gruesos y simples, cabeza grande, **ojos diminutos**, **escamas de plumas en relieve** (cubitos planos sobre la piel), colores pastel y saturados con **sombras frías lavanda**; el **contorno negro grueso es solo de las comunes y medias**; las raras llevan alas grandes en capas con degradado, brillo dorado y **rombos dorados**, y no llevan contorno. Solo vi iconos del listado de rblxguide, no capturas de partida.
- **Lo que Maikol ya rechazó (v01) y por qué**: «se ve feo y buguiado». Eran: alas de persiana (tablas planas apiladas en T), cola como tabla suelta, penacho flotando fuera del cuerpo, hombros dorados como barras sueltas y líneas negras sueltas del contorno. **Lo aprobó cuando** el cuerpo era rechoncho, las alas en arco de plumas en abanico, la cola unida, escamas en relieve y todo conectado.
- **Lo que pidió después (a ti también)**: alas **articuladas con rig** para la animación, **ojos que parpadeen** y **pies que guindan al volar**, «como en la vida real».

## 5. Convenciones técnicas (para que tus modelos encajen con los nuestros)
- **Escala**: 1 unidad de Blender = 1 stud. Referencia de tamaño: maniquí R15 de 5,2 studs; el render de comprobación lleva ese maniquí y una regla de 6 studs.
- **Una malla, un material, un atlas de textura de 1024×1024** (sin texturas extra), UV desplegadas, bordes de las islas sangrados unos texeles (Roblox filtra la textura y los bordes negros dibujan líneas oscuras al alejarse).
- **Ejes**: mis modelos miran a +Y (+Z arriba) y salen con `axis_forward='Z'`, `axis_up='Y'`, `global_scale=0.01`; los de Codex miran a −Y y salen con `'-Z'`. Los dos deberían entrar igual en Studio; sin confirmar.
- **Rig de las mascotas voladoras** (Codex y yo): 8 huesos `Root, Body, Head, Tail, Wing_R, Tip_R, Wing_L, Tip_L`, todos apuntando a +Y sin giro, piel rígida (cada vértice sigue un solo hueso, sin pesos mezclados), padre de `Tip_*` es `Wing_*`.
- **Clips** (30 fps, bucle: la última clave repite la primera): `Fly` 1,0 s, `Glide` 2,0 s, `Celebrate` 2,0 s. Un FBX por clip con el mismo rig, un FBX del rig en pose neutra y un GLB con los tres clips.
- **Aleteo (corrección de Maikol)**: **recoger → extender → impulsar → recoger**, con flexión del tramo exterior y la punta con retraso: arriba extendida; el empuje baja el ala con la punta retrasada (más arriba que el hombro); abajo se recoge (muñeca y punta flexionan hacia atrás mientras sube); arriba se extiende otra vez. Se mide con la razón envergadura plegada/extendida (ancho en X de la malla deformada, mínimo/máximo): las comunes de Codex ≈ 0,56; las mías 0,53–0,56; mis alas de jugador 0,25.
- **Pies que guindan** (mi plan, para que lo hagamos igual): huesos `Leg_R` y `Leg_L` (cabeza en la cadera), patas colgando hacia abajo en la pose neutra, péndulo suave con el aleteo en `Fly`, más rectas en `Glide`, patadita en `Celebrate`.
- **Parpadeo** (propuesta): en Roblox un hueso solo se mueve/gira (no se escala), así que parpadear = **párpados**: un cubo del color de la cabeza, ligeramente mayor que el ojo, en un hueso `Lid_R`/`Lid_L` que baja sobre el ojo y vuelve (≈ 0,15 s cada 3–4 s, en bucle largo).
- **Calidad de malla** (parpadeo o «z-fighting» en Roblox): ninguna pieza suelta (todo toca el cuerpo), **ninguna cara coplanar solapada** (dos caras del mismo lado a menos de ~0,008 studs que se solapan): da a cada pluma/bloque su propia altura. Se comprueba con `tools\comprobar_malla.py`.

## 6. Herramientas reutilizables (no las reinventes)
Blender 5.2 headless: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P <script.py>`.
- `mas1-arte\tools\mas1_lib.py`: voxeles `Vox` (elipsoides y cajas en una rejilla común, solo se crean las caras expuestas, cada celda lleva hueso y región de color), `armar()` (rig + piel rígida + malla única), exportación FBX/GLB.
- `mas1-arte\tools\mas1_ave.py`: `pluma()` (pluma plana con grosor y bandas de color, colocada en el marco de un ala), `marco_ala()` (ala en arco con dihedro y barrido), `escamas()` (plaquitas pegadas a la piel), `rombo()`, `cubo_girado()`, `piezas_sueltas()`, `caras_coplanares()`.
- `mas1-arte\tools\mas1_pet.py`: rig de 8 huesos, clips con el aleteo nuevo (`ALETEO`, `clips_pet()`), escena de render con el maniquí y la regla, horneado y pintura de textura, sangrado de bordes, exportación.
- `mas1-arte\tools\build_mascota_aguila.py`: **ejemplo completo** de principio a fin (cuerpo, escamas, alas, cola, rig, textura, clips, renders, FBX/GLB). Fases: `MASCOTA_FASE=geo` (colores planos, rápido), `check` (solo comprobaciones), `assets` (sin renders), `full`.
- `mas1-arte\tools\validar_asset.py`: reimporta los FBX/GLB, comprueba huesos, pesos, UV, textura, bucles y mide la razón de plegado. `mas1-arte\tools\animar_preview.py`: GIF del clip.
- Los `ESTADO.md` de `alas-avanzadas-v02\` y `mascotas-altas-v02\` tienen los comandos para regenerar y validar.

## 7. Errores que ya cometimos (no los repitas)
1. Mirar solo de frente: revisa **3/4, perfil, espalda, desde arriba y las poses extremas** del clip.
2. Alas planas y rectas en T; una pluma por tabla sin grosor ni altura propia (z-fighting).
3. Piezas «pegadas» a ojo que en realidad flotan unas centésimas: pasa `piezas_sueltas()`.
4. Contorno negro con carcasa invertida en mascotas raras: dio líneas sueltas dentro del pecho y las raras de Roba un huevo no lo llevan.
5. Afirmar que algo «funciona» sin probarlo en Roblox: di siempre qué es render de Blender y qué no se probó.
6. Dejar `.blend1` y renders intermedios: límpialos antes de commitear.

## 8. Reglas
- **Sin push** a ningún remoto (lo decide Maikol). Commits locales pequeños con autor `-c user.name=Maikol -c user.email=maikolrlxd@gmail.com`; nada de claves, `.rbxl` ni binarios pesados innecesarios.
- **No publicar, subir ni comprar**; **no pulses «Enable Overages» ni planes** de Antigravity; no cambies claves, MCP ni cuentas; no gastes créditos de servicios externos sin permiso.
- No toques la carpeta de Codex ni nada de Luto o Slime Rush. No toques mis carpetas `alas-avanzadas-v02\` ni `mascotas-altas-v02\` (puedes leerlas y copiar ideas).
- **Tus entregas** van dentro de `C:\Users\maiko\slime-rush\hyprarch\mas1-arte\antigravity\modelos\<nombre>\` (y lo que ya hiciste, anota su ruta en `antigravity\LEEME.md`). Por pieza: `ESTADO.md` con **los fallos primero**, renders de comprobación con el maniquí de 5,2 studs, FBX/GLB/blend y la validación (`validar_asset.py`).
- Crítica dura de lo tuyo antes de enseñarlo (hasta tres vueltas por pieza) y, como ya haces, **manda una foto a Maikol cada vez que termines una**.

## 9. Qué necesito de ti
1. Sigue con tu serie de criaturas aladas y monstruos, ya con **rig de alas articulado**, **ojos que parpadean** y **pies que guindan**.
2. Pasa `comprobar_malla.py` y `validar_asset.py` a lo tuyo y dime qué falla.
3. Si ves algo en mis modelos que se pueda mejorar, dilo sin adornos (en `antigravity\LEEME.md`).
4. Dudas o decisiones para Maikol: anótalas arriba del `LEEME.md`; se las paso.
