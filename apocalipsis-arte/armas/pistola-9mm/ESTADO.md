# Pistola 9mm — estado

**Congelada por decisión de Maikol** (2026-10-23, "Ya déjale las armas así"). Esta es la versión v3b y no se hacen más vueltas de crítica.

## Qué falla
- **Triángulo negro grande en el armazón.** Se ve en la vista izquierda, en la de tres cuartos y en la de escala. Una cara del armazón tapa el hueco entre el guardamonte y la empuñadura y se ve negra porque tiene la normal invertida.
  - Pasar la triangulación a EAR_CLIP no lo arregló, así que lo más probable es que el contorno del armazón se cruce en algún punto.
  - Arreglo propuesto, no hecho por la congelación: partir la tapa del armazón en piezas convexas (bloque superior + empuñadura).
- Por culpa de ese triángulo, el guardamonte no se ve desde la izquierda. Desde la derecha sí se ve.
- Por el puerto de expulsión se ve un bloque de latón liso. Es el casquillo, escondido en la recámara porque Roblox no anima la escala. Se lee como una bala en la recámara, pero es un bloque.
- Las manos del viewmodel son bloques estilo R15, sin dedos.
- **No probado en Roblox Studio:** la importación de los FBX animados.

## Triángulos
Armazón 176, Corredera 260, Cargador 72, Gatillo 60 y Casquillo 66: **634 en total** (presupuesto 300–800). Los brazos del viewmodel suman 256 aparte.

## Clips (modelo de mundo y viewmodel)
- Equipar: 0,80 s
- Disparo: 0,25 s, con el casquillo saliendo a la derecha
- Recargar: 1,70 s
- Reposo: 2,00 s, en bucle

El detalle de cada clip está en `../../armas-animaciones.md`.

## Vueltas
1. **v1:** salió oscura y plana, y el viewmodel era pobre.
2. **v2:** la corredera parecía cromada y tenía 890 triángulos.
3. **v3:** corredera más oscura, arañazos suaves y sin biseles, con 634 triángulos. También se arregló el viewmodel, que no se deformaba porque las copias compartían la malla y borraban los grupos de vértices.
4. **v3b:** la misma geometría con triangulación EAR_CLIP. No arregló el triángulo negro.

## Archivos
- `Pistola9mm.blend`: escena con los dos rigs y todos los clips, con prefijos `Mundo_` y `VM_`.
- `Pistola9mm_Mundo.fbx`: modelo de mundo con sus clips.
- `Pistola9mm_VM.fbx`: viewmodel con brazos R15 y sus clips.
- `Pistola9mm_Mundo_Estatico.fbx`: piezas separadas; la pieza principal se llama `Handle`.
- GLB de mundo y de viewmodel.
- `clips/`: un FBX por clip.
- `texturas/`: color de 1024 px.
- `previews/`: renders y hojas de contacto. Copia en `../../renders/`.
