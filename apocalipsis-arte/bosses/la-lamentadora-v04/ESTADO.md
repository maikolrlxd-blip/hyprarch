# La Lamentadora v04 — revisión del rostro

Pedido de Maikol: más vida y detalles, principalmente en la cara. Esta revisión parte de v03b y conserva el estilo de `taller-ia/ESTILO.md` (Poli Pintado): silueta de pocos polígonos, mate, paleta apagada y pinceladas dirigidas.

## Cambios

- Mirada asimétrica con iris, pupila y punto de luz discreto dentro de las cuencas. Un ojo queda más cerrado que el otro.
- Cejas tensas y desiguales, pliegues pequeños en frente y lagrimales, ojeras y desgaste bajo los ojos.
- Variación de piel siguiendo pómulos y mejillas, una cicatriz curada fina y labios secos con estrías.
- Siete dientes pequeños de profundidad real, desiguales y dentro de la cavidad; fosas nasales más discretas.
- La pintura nueva solo se aplica al atlas de la cabeza. Cuerpo, vestido, manos, escala y cuatro clips proceden de v03b.

## Estado de revisión

Construcción y exportación terminadas el 23/10/2026. **2926 triángulos** (cabeza 1470, cuerpo 1456), 15 mallas, 16 huesos y cuatro clips. Cuatro atlas de color de 1024 px empaquetados en el .blend.

`qa/VALIDACION-BLENDER.json`: PASADA en proceso independiente. UV finitas dentro de 0–1, sin vértices sueltos ni triángulos degenerados, pesos completos, pose neutral guardada, clips y texturas presentes. Reimportación del FBX estático, rig y Caer con geometría y dimensiones coincidentes. El contacto de Caer es una comprobación geométrica muestreada; no es física del motor.

Se inspeccionaron las vistas completas, tres cuartos del rostro y primer plano frontal. La mirada y las cejas se leen mejor; los dientes superiores quedan poco visibles desde la pose con cabeza inclinada. El cabello sigue rígido. Maikol vio el acercamiento nuevo y respondió «ok»; esto no se registra como aprobación de integración ni como prueba de Roblox.

## Límites

La dirección sigue abierta a las correcciones de Maikol. El cabello sigue unido a Head, sin movimiento independiente. Esta pasada no añade un ataque Lamento, IA ni comportamiento jugable. La v02 integrada por el coordinador en Studio no se sustituye automáticamente. No se publicaron assets ni se usó Studio en este bloque.

## Archivos

- `fuentes/build_lamentadora.py`: construcción, pintura, rig, renders y exportación.
- `fuentes/boss_head.py`: geometría facial y pelo.
- `fuentes/face_paint.py`: pintura facial dirigida.
- `qa/validate_blender.py`: comprobación independiente del .blend y reimportación FBX; no prueba Roblox.
- `previews/LaLamentadora_v04_*.png`: renders nuevos de Blender. El archivo `Lamentadora-v04-01-rostro-forma-Blender.png` es una vista de materiales provisionales, no el acabado pintado.

La carpeta v03 permanece protegida como revisión anterior. Su .blend conserva SHA256 `2053783b1fc0f781f66285c8b4bb603b15fbc8ebf86e68e3e1aa00aff3e6a4a8`.

Paquete local: `C:/Users/maiko/Documents/Codex/2026-10-21/c/outputs/La Lamentadora v04 - rostro.zip`. `MANIFEST.json` registra los hashes internos; el hash del paquete va en el archivo `.zip.sha256` contiguo. Incluye las vistas pintadas; la vista de forma queda solo como diagnóstico local.
