# La Lamentadora v0.2 — estado

Del 2026-10-23. Está hecha sobre la base de la mujer zombi: piezas R15, rig y clips. Se construye con `ZOMBI_VARIANTE=lamentadora` y `tools/build_zombi.py`.

## Qué falla
- **Deformación:** la única deformación son los brazos largos (×1,35). El resto son proporciones humanas a 1,75×, sin joroba ni cuello largo.
- **Pelo:** es negro, pero sus reflejos pintados tiran a marrón y, de cerca, los mechones siguen pareciendo tablas.
- **Cara:** las arrugas y los surcos son los mismos trazos que en la zombi.
- **Clips:** son los de la zombi escalados; no tiene clip de lamento propio.
- **Importada en Studio** (2026-10-23) como `ServerStorage.LUTO_Plantillas.Jefe_lamentadora`, con su rig R15. Faltan las animaciones publicadas y verla en una ronda de jefe (cada 15 rondas).

## Qué funciona
- **Tamaño:** mide unos 10 studs, casi el doble que un R15.
- **Aspecto:** piel gris pálida, vestido negro de luto, liso, roto y manchado de tierra, y manos con dedos largos como garras.
- **Cara:** ojos hundidos y negros con un brillo apagado, párpado inferior enrojecido, cejas de angustia y boca muy abierta en un lamento. Sin gore.
- **Clips:** Reposo, Caminar, Atacar y Caer, con los desplazamientos escalados al tamaño.
- **Montaje en Studio:**
  1. importar `LaLamentadora_Estatico.fbx`;
  2. seleccionar el modelo y ejecutar `integracion/ArmarZombi.lua`, que lo nombra `Jefe_lamentadora`, crea el `HumanoidRootPart`, los Motor6D R15 y el Humanoid con HipHeight ≈ 4,2;
  3. moverlo a `LUTO_Plantillas`.

## Triángulos
Los mismos que la zombi: **1966**. Lleva 4 texturas de 1024.

## Relación con la v0.1 (Codex)
La v0.1 está en `../la-lamentadora-v01/`. Su silueta era más original (hombros enormes y cuerpo encorvado), pero la cara era de caricatura y no entraba en la canalización R15 de Luto. Se puede retomar su silueta más adelante.
