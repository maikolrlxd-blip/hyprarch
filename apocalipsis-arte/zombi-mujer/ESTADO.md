# Mujer zombi — estado

v5, del 2026-10-23. Es realista, con proporciones tipo Rthro, tal como pidió Maikol («que sea mujer», «vete por lo realista»). Sin gore.

## Qué falla
- **El pelo se ve rígido:**
  - el casco de pelo ya tiene 16 lados y se nota menos, pero sigue viéndose rígido;
  - los mechones de delante, de cerca, todavía parecen tablas.
- **Rodillas:** se ve una costura en la junta de cada rodilla, porque cada pieza R15 es rígida.
- **Arrugas:** las de la frente y los surcos de la boca siguen siendo trazos pintados, aunque ya suaves.
- **Sin dedos:** las manos tienen palma y dedos en bloque.
- **Sin probar en Studio:** los clips con el Animation Editor. El rig R15 con Motor6D se monta con `integracion/ArmarZombi.lua`.

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
