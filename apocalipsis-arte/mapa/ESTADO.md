# Mapa apocalíptico (300 × 300 studs) — estado

Versión v3, del 2026-10-23. Es solo apariencia, en estilo Poli Pintado: formas facetadas, pintura a mano mate, paleta sucia y apagada, y ambiente de polvo.

## Qué falla (primero)
- **Los solares se repiten:** el mismo `Suelo_Solar_60`, girado, cubre los 16 solares, y desde arriba se nota la repetición de manchas de hierba y piedras.
- **El mapa termina en seco:** el borde de los solares es un corte recto. En el juego lo tapan la bruma (`ambiente-roblox.lua`) y los muros invisibles del borde, pero desde arriba se ve.
- **El follaje es de bloques:** el arbusto, la copa del árbol y las hojas de la enredadera son poliedros. Se leen bien de lejos y de cerca se notan.
- **La enredadera, suelta, flota:** está pensada para pegarse a un muro. Así está colocada en el ensamblado, en dos fachadas.
- **Vistas previas:** el maniquí de escala queda pegado a algunas piezas (contenedor, barriles).
- **Nada probado todavía en Roblox Studio:** ni la importación del FBX, ni las texturas, ni las colisiones, ni los marcadores. Es el siguiente paso.

## Qué hay
- **Calles** (`calles/`), losetas de 60 × 60:
  - recta, cruce con pasos de cebra y calle rota con cráter;
  - solar de tierra con hierba;
  - la calzada está a z = 0 y aceras y solares a 0,55.
- **Edificios** (`edificios/`):
  - tienda con letrero «TIENDA» y toldos rotos;
  - bloque de 5 plantas con la esquina derrumbada;
  - almacén de chapa con el tejado hundido.
- **Vehículos** (`vehiculos/`): sedán oxidado, sedán quemado (óxido, hollín y sin cristales), sedán volcado, pickup y furgoneta. Los cristales llevan grietas en telaraña desde un impacto.
- **Props** (`props/`): sacos, barricada de madera, barrera de hormigón, valla de chapa, contenedor, farola doblada, hidrante, barriles, señal de ALTO, semáforo, cajas y neumáticos.
- **Natura** (`natura/`): escombros (tres tamaños), arbusto, hierba alta, maleza, árbol muerto, árbol invasor y enredadera.
- **Ensamblado** (`ensamble/`):
  - `Mapa_Completo.fbx` con las 121 instancias y nombres fijos, que serán los nombres de los MeshPart, por ejemplo `Calle_Cruce_60_01`;
  - `mapa-layout.json` con posiciones, colisiones y marcadores;
  - vistas con el ambiente.

Triángulos: **30 850 en total** y ninguna pieza pasa de 1500. La mayor es `Edificio_Bloque`, con 1384. El detalle por pieza está en el `datos.json` de cada carpeta.

## Para el juego (Luto)
- **`ambiente-roblox.lua`:** ModuleScript con la iluminación del mapa (Lighting, Atmosphere, ColorCorrection, Bloom y SunRays): tarde baja con polvo, colores apagados. Se usa con `require(...).aplicar()` desde un Script del servidor.
- **`integracion/MapaColisionesMarcadores.lua`:** se ejecuta una vez en la barra de comandos de Studio, con el FBX ya importado en `ServerStorage.LUTO_Plantillas.Mapa`. Hace esto:
  - deja las mallas ancladas y sin colisión;
  - crea 97 cajas invisibles `*_Colision` (suelos con su altura, edificios, coches, props, troncos y postes, más 4 muros de borde);
  - crea los marcadores `SpawnJugadores` (cruce), `SpawnZombis` (12, en finales de calle, esquinas y bordes), `Tienda_municion` y `Tienda_curar` (esquinas del cruce);
  - se alinea con el MeshPart `Calle_Cruce_60_01`, por si el importador movió el modelo.
- **Sin colisión a propósito:** hierba, maleza, arbusto y enredadera.

## Vueltas
1. **v1:** no llegó a ensamblarse. `Calles.blend` quedó roto por un corte de sesión.
2. **v2:** caras negras en los perfiles cóncavos (el mismo fallo que la pistola) y grietas que parecían curvas de nivel. Cristales y barrera con manchas como de mapa topográfico. En las vistas previas, el asfalto salía negro porque el suelo de referencia coincidía en altura con la calzada, y los edificios salían cortados.
3. **v3:**
   - normal calculada antes de triangular;
   - grietas de Voronoi en zonas y telaraña en los cristales;
   - barrera sin manchas de color;
   - coche quemado de verdad;
   - cajas con tablones y bolsas de basura;
   - follaje sin puntos negros;
   - panel interior de los muros acortado (dejaba una raya negra en las esquinas);
   - vistas previas bien encuadradas;
   - ambiente de polvo;
   - colisiones y marcadores para Luto.
