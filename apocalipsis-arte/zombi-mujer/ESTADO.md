# Mujer zombi — estado

v5, del 2026-10-23. Es realista, con proporciones tipo Rthro, tal como pidió Maikol («que sea mujer», «vete por lo realista»). Sin gore.

## Qué falla
- **El pelo se ve rígido:**
  - el casco de pelo ya tiene 16 lados y se nota menos, pero sigue viéndose rígido;
  - los mechones de delante, de cerca, todavía parecen tablas.
- **Rodillas:** se ve una costura en la junta de cada rodilla, porque cada pieza R15 es rígida.
- **Arrugas:** las de la frente y los surcos de la boca siguen siendo trazos pintados, aunque ya suaves.
- **Sin dedos:** las manos tienen palma y dedos en bloque.
- **Animaciones en el juego (publicadas el 2026-10-23):** se reproducen, pero con dos fallos que se arreglan en el servidor (`apocalipsis-juego/server/Partida.server.lua`, que no es mío):
  - los cuatro clips se publicaron con prioridad Action, y como el servidor deja Reposo sonando mientras camina o ataca, Reposo se mezcla al 50 % con Caminar y Atacar. Hay que asignar la prioridad de cada pista al cargarla: Reposo Idle, Caminar Movement, Atacar Action, Caer Action2;
  - al morir se rompen las articulaciones (`BreakJointsOnDeath`), así que el cuerpo se desmonta y el clip Caer no llega a verse.

## Probado en Roblox Studio (2026-10-23)
- **Importación:** `ZombiMujer_Estatico.fbx` entró con el 3D Importer y la sesión de Maikol, con 15 MeshPart de nombres R15 exactos y texturas.
- **Rig:** `integracion/ArmarZombi.lua` lo dejó como rig R15 con `HumanoidRootPart`, 15 Motor6D y un Humanoid R15. Mide 2 × 5,71 × 1,17 studs y está en `ServerStorage.LUTO_Plantillas.Zombi_Mujer`.
- **Play:** el servidor de Luto clona la plantilla. Las mujeres zombi salen de los bordes del mapa con su textura y su barra de vida y van a por el jugador (captura en `renders/Studio_Luto_zombis_mujer_en_partida.jpg`).
- **Animaciones publicadas** (cuenta de Maikol, fuera de venta) y escritas en `apocalipsis-juego/src/Animaciones.lua`:

  | Clip | Id |
  |---|---|
  | Reposo | 117323418394221 |
  | Caminar | 128425423837041 |
  | Atacar | 81918422160520 |
  | Caer | 131892149953171 |

  - Salen de `integracion/Animaciones_Zombi.rbxmx`, que genera `tools/exportar_animaciones_roblox.py` desde `ZombiMujer.blend` (KeyframeSequence a 30 fps).
  - Antes de publicar se comprobaron sobre el rig: caminar, atacar y caer.
  - Después, cada id se descargó en Studio y coincide con su secuencia local en claves y poses.
  - En Play, las zombis reproducen Reposo, Caminar y Atacar.

## Qué funciona
- **Cuerpo y ropa:** piel pálida verdosa con moretones y suciedad, y vestido floral desvaído, roto y manchado de tierra (no de sangre). Un pie va descalzo y el otro con zapato.
- **Cara de angustia** (encaja con «Luto»):
  - cejas con el extremo interior subido;
  - arrugas de preocupación;
  - ojos nublados con el párpado inferior enrojecido;
  - boca abierta en un gemido, con los dientes de arriba.
- **Proporciones:** brazos un 15 % más llenos que en la v3. Mide unos 5,7 studs, algo más que un R15 de 5,2.
- **Clips:**
  - Reposo: 2,0 s en bucle, encorvada y balanceándose;
  - Caminar: 1,1 s en bucle, paso arrastrado con los brazos por delante;
  - Atacar: 0,9 s, zarpazo;
  - Caer: 1,4 s, se queda tumbada boca arriba con los brazos abiertos.
- **Encuadres de comprobación completos:** frente con referencia, tres cuartos, espalda, perfil y la cara de cerca.

## Triángulos
**1966 en total** (presupuesto ≤ 3000):

| Pieza | Triángulos |
|---|---|
| Head | 774 |
| LowerTorso | 212 |
| UpperTorso | 208 |
| Cada mano | 90 |
| Cada muslo | 76 |

Hay 4 texturas de 1024 px: Cabeza, Torso, Brazos y Piernas.

## Para Luto
- **FBX:** `ZombiMujer_Estatico.fbx` lleva las piezas con nombres R15 exactos. `ZombiMujer.fbx` lleva el rig y los clips, y `clips/` un FBX por clip.
- **Montaje en Studio:**
  1. Importa el estático.
  2. Selecciona el modelo.
  3. Ejecuta `integracion/ArmarZombi.lua`. Crea el `HumanoidRootPart`, los Motor6D con nombres R15 (Root, Waist, Neck, LeftShoulder…) y un Humanoid R15 con HipHeight 1,95.
  4. Muévelo a `ServerStorage.LUTO_Plantillas.Zombi_Mujer`.

## Vueltas
1. **v1:** de bloques. Pelo en losa, nariz de cubo y venas como curvas de nivel.
2. **v2:** realista, a petición de Maikol, pero la cara parecía maquillaje y los arañazos chevrones.
3. **v3:** pelo con volumen, hombros caídos y juntas solapadas.
4. **v4:**
   - cara de angustia;
   - brazos más llenos;
   - pelo de 16 lados;
   - encuadres sin cortes;
   - exportación estática con nombres R15 exactos (antes salían como `Head.001`);
   - script de Studio.
5. **v5:** sin zarpazos en el antebrazo (en el cilindro parecían chevrones) y trazos de la cara más suaves.
