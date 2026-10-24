# Informe de Codex — Slime Rush Capa 1

## Simulación F/G/H en Roblox Studio — 2026-10-22

Copia temporal de QA: SimulacionF_G_H-copia.rbxl. Ejecuté slime-rush-juego/pruebas-studio/SimulacionF_G_H.server.lua en Play. Este bloque reproduce todas las líneas SR_TEST del Output del servidor, en orden (52 PASS, 0 FAIL; simulación de dos jugadores virtuales en un servidor, todavía no son dos clientes reales).

```text
SR_TEST PASS mundo generado | ms=2 nodos=43 cofres=3
SR_TEST PASS hay aparicion para 2 jugadores
SR_TEST PASS fase antes de empezar | generating
SR_TEST PASS addPlayer 1
SR_TEST PASS addPlayer 2
SR_TEST PASS fase cuenta atras | countdown
SR_TEST PASS no se recoge en la cuenta atras | fuera de fase (countdown)
SR_TEST PASS fase explorar | explore
SR_TEST PASS E: muy lejos se rechaza | muy lejos
SR_TEST PASS E: jugador 1 recoge nodo 1 | tabla
SR_TEST PASS E: jugador 1 recoge nodo 2 | tabla
SR_TEST PASS E: jugador 1 recoge nodo 3 | tabla
SR_TEST PASS E: nodo ya recogido se rechaza | ya fue recogido
SR_TEST PASS E: jugador 2 recoge nodo 4 | tabla
SR_TEST PASS E: jugador 2 recoge nodo 5 | tabla
SR_TEST PASS mochila J1=3, J2=2 | 3/2
SR_TEST PASS H: la meta aun no se abre en explorar | la meta aun no se abre
SR_TEST PASS F: golpe 1 | hp=80 ko=false
SR_TEST PASS F: la cadencia rechaza el golpe inmediato | espera
SR_TEST PASS F: golpe 2 | hp=60 ko=false
SR_TEST PASS F: golpe 3 | hp=40 ko=false
SR_TEST PASS F: golpe 4 | hp=20 ko=false
SR_TEST PASS F: golpe 5 | hp=0 ko=true
SR_TEST PASS F: el 5o golpe deja inconsciente | hp=0
SR_TEST PASS J2 inconsciente
SR_TEST PASS F: un inconsciente no golpea | estas inconsciente
SR_TEST PASS F: fuera de alcance se rechaza | muy lejos
SR_TEST PASS G: saqueo al inconsciente | robados=1
SR_TEST PASS G: los objetos pasaron de J2 a J1 | 4/1
SR_TEST PASS G: la espera entre saqueos | espera
SR_TEST PASS G: muy lejos se rechaza | muy lejos
SR_TEST PASS J2 despierta tras downed_time
SR_TEST PASS vida de J2 vuelve a 100 | 100
SR_TEST PASS F: inmunidad al despertar | inmune
SR_TEST PASS fase regreso | return
SR_TEST PASS el regreso ya esta abierto
SR_TEST PASS H: fuera de la meta se rechaza | fuera de la meta
SR_TEST PASS H: J2 empieza deposito
SR_TEST PASS derrota interrumpe el deposito de J2 | tabla
SR_TEST PASS H: J2 no puede terminar (inconsciente/interrumpido) | estas inconsciente
SR_TEST PASS H: J1 empieza deposito
SR_TEST PASS H: no termina antes de deposit_time | aun no termina el canal
SR_TEST PASS H: deposito con exito dentro de la ventana de regreso | rank=1 bonus=150 score=160 objetos=4
SR_TEST PASS la mochila de J1 queda vacia
SR_TEST PASS quien ya deposito no puede recoger | ya llegaste a la meta
SR_TEST PASS entrar tarde se rechaza | la partida ya empezo
SR_TEST PASS no hay resultados antes del colapso | la partida no termino
SR_TEST PASS fase colapso | collapse
SR_TEST PASS calendario de desastres no vacio | 27
SR_TEST PASS resultados finales | 2
SR_TEST RESULTADO puesto=1 jugador=1 puntos=160 llego=true perdio=0 (valor 0)
SR_TEST RESULTADO puesto=2 jugador=2 puntos=0 llego=false perdio=1 (valor 5)
SR_TEST PASS J1 gana y J2 no llego pierde todo
SR_TEST PASS fase terminada | ended
SR_TEST RESUMEN PASS: 52 PASS, 0 FAIL
```

## 2026-10-23 — Codex retoma La Lamentadora: revisión visual v03

Pedido humano vigente: crear jefa zombi mujer aterradora, humana pero profundamente deforme; mostrar imágenes de cada avance para corregir rumbo. Maikol recordó `taller-ia/ESTILO.md`: Poli Pintado. Leído y aplicado. No volver a Slime Rush en este bloque.

Encontré la v02 que Claude hizo durante la pausa y partí de esa base; v01/v02 protegidas. Nueva copia `apocalipsis-arte/bosses/la-lamentadora-v03/`. Cabeza rehecha con cuencas y cavidad bucal, asimetría, mechones curvos y manos de cinco dedos; cuello adelantado y postura inclinada. Conserva vestido negro, acabado mate y canalización de texturas del proyecto. 2824 tris, 15 piezas/16 huesos, 4 clips heredados. Aún revisión visual: pelo rígido, cuerpo necesita más identidad, falta Lamento propio y movimiento de cabello.

Validación Blender independiente PASADA (`qa/VALIDACION-BLENDER.json`): mallas, UV, pesos, 4 texturas empaquetadas y reimportación estático/rig/Caer. Caer original penetraba hasta -2.39210 studs; corregido con raíz muestreada, mínimo después +0.020007. No es prueba de física ni motor. El .blend actual queda en pose neutral; las medidas de v02 estaban contaminadas por su pose caída pese a action=None. No se modificó v02 para corregirlo.

Imágenes actuales: `previews/LaLamentadora_v03b_*`. La primera pasada v03 tenía materiales mal restaurados por `materials.clear()`; está respaldada fuera del repo en `work/backups/Lamentadora-v03a-before-material-fix.zip`. Se corrigió sustituyendo slots in situ. No usar las fotos sin v03b como actual.

Studio: 0 ventanas abiertas por Codex en este bloque, no se controló la interfaz ni se publicaron assets. La plantilla de Studio sigue siendo v02. Código de Slime Rush y cambios de otros sin tocar. Pendiente feedback de Maikol sobre rostro/silueta antes de avanzar a armas u objetos.

Nota reutilizable para cerebro: al desasignar una Action Blender conserva la pose; limpiar matrix_basis/rotación/posición antes de guardar y medir. Limpiar lista de materiales puede restablecer índices de polígonos: restaurar slots in situ. Cavity facial y longitud de dedos deben revisarse con luz neutra además de renders de ambiente. Mantener snapshots de fuentes compartidas para no pisar al coordinador.

## 2026-10-23 — LUTO / La Lamentadora v04: detalle facial

Pedido directo de Maikol: «Le daría mas vida y detalles, principalmente en la cara». Se creó una revisión aislada `apocalipsis-arte/bosses/la-lamentadora-v04/`, partiendo de v03b. Mantiene Poli Pintado: mate, paleta apagada, pinceladas y formas de pocos polígonos. Ojos ahora con iris/pupila/reflejo pequeño dentro de las cuencas; cejas tensas asimétricas, pliegues, ojeras, lágrimas secas, cicatriz curada fina, piel con variación dirigida y labios agrietados. Siete dientes pequeños con profundidad; fosas nasales más pequeñas. No se cambian cuerpo, vestido, manos ni diseño de clips.

Resultado: 2926 tris (cabeza 1470 / resto 1456), 15 mallas, 16 huesos, cuatro atlas 1024 empaquetados y cuatro clips. `qa/VALIDACION-BLENDER.json` PASADA: geometría/UV/pesos/pose neutral y reimportación del FBX estático, rig y Caer. Comprobación geométrica de contacto de Caer pasada, no física. No Roblox ni FPS/colisión. Cero ventanas Studio abiertas/controladas por Codex en este bloque. Nada publicado, ningún push.

Fotos actuales Blender: `previews/LaLamentadora_v04_4_cara_tres_cuartos.png` y `LaLamentadora_v04_5_cara_frente_muy_cerca.png`; también vistas completas 1 y 2. Se mostraron al usuario; respondió «ok» tras la vista de tres cuartos. No equivale a autorizar publicación/integración. Autocrítica: dientes superiores poco visibles con cabeza inclinada, pelo aún rígido; pendiente Lamento propio y más identidad corporal si Maikol sigue esta dirección. No avanzar a armas/mapa sin resolver feedback de la jefa.

Entrega: .blend + FBX rig/estático + GLB + cuatro FBX de clips, fuentes congeladas y validación. Paquete `C:/Users/maiko/Documents/Codex/2026-10-21/c/outputs/La Lamentadora v04 - rostro.zip`, SHA en `.zip.sha256`. V03 protegida (SHA del .blend 2053783b1fc0f781f66285c8b4bb603b15fbc8ebf86e68e3e1aa00aff3e6a4a8); v02 de Studio y cambios del coordinador sin tocar.

Para el cerebro/diario: el detalle facial debe seguir la anatomía (párpados, cejas, lagrimal, comisura) para añadir expresión sin ruido uniforme. Cabeza con arte pintado en atlas propio; aplicar recetas nuevas solo a ese grupo. La revisión se hizo con Blender background limitado a tres hilos. Próximo punto visual: reacción de Maikol al frontal; no confundir este archivo local con la plantilla cargada en Studio. Sin preguntas bloqueantes.

## 2026-10-24 — LUTO / entrega nocturna: movimiento, lanzallamas y hospital

Maikol autorizó seguir mientras duerme y hacer otras cosas al terminar la jefa; posteriormente especificó inspección, recarga, sacar/guardar, efectos y animaciones de quemado. Esto sustituye la espera por feedback que figuraba en el relevo anterior. Trabajo en carpetas nuevas; v04 y todos los archivos compartidos modificados por el coordinador conservados.

**La Lamentadora v05b:** 2926 tris y 15 mallas, geometría/UV del rostro v04 exactas. 38 huesos: 16 originales y 22 para once mechones. Cinco clips (cuatro heredados con pelo y Lamento 2,8 s). Se comprobó movimiento local del cabello independiente de la cabeza, máximo dos influencias, pose neutral, texturas y reimportación FBX/GLB. Caída y Lamento tienen chequeo de contacto geométrico; no es física. Mínimo Z del Lamento en fotogramas enteros +0,020637. Fotos **v05b** y fuentes en `apocalipsis-arte/bosses/la-lamentadora-v05/`. Mandíbula no animada; naturalidad continua del pelo sigue abierta a feedback. El helper Motor6D de v04 no sustituye al rig skinned nuevo.

**Lanzallamas v01b:** arma de 390 tris; VM con brazos 646. Tres partes, rigs Mundo/VM de 3/10 huesos, atlas arma 1024/brazos512. Equipar0,85; Guardar0,65; Reposo2; Disparo0,6; Recargar2,8; Inspeccionar3,2 segundos. Doce FBX de clips más maestros/estáticos/Blender y eventos JSON/Lua. Reimportación de los 12 clips, dos maestros de seis acciones, estáticos y cierres de bucle pasada. Hojas de poses de recarga/inspección/equipar/guardar revisadas; sin afirmar revisión de todas las transiciones a velocidad real. Corregidos perfil radial mal interpretado, nombres de estáticos y pequeño salto angular del bucle Disparo; cada estado previo respaldado.

**Quemado:** `integracion/QuemadoFX.lua` solo presenta fuego de boquilla/NPC. Luau compila; siete casos de ciclo de vida con mocks pasaron (renovación sin acumulación, retiro, expiración, duración inválida/acotada y limpieza). **No se ejecutó ParticleEmitter en motor.** No aplica daño ni remotos; `CONTRATO.md` define cancelaciones y responsabilidad del servidor. No hay audio ni carbonización implementados. Tres clips nuevos de la zombi existente en `apocalipsis-arte/zombi-mujer/animaciones-quemado-v01/`: Inicio0,85/Bucle1,2/Caer1,8. Misma malla/UV, 1966 tris/16 huesos. Reimportación y contacto pasados; mínimo de Caer en cuartos de fotograma +0,02013. Las fotos de estas poses son Blender sin fuego. La IA debe decidir transiciones, locomoción y muerte; no reiniciar Inicio en cada tick ni matar al terminar el VFX.

**Hospital v01:** camilla792, biombo816 y soporte de suero476 tris. Tres atlas512 y seis FBX/GLB, escena Blender de conjunto y fotos nuevas. UV/geometría/texturas y reimportación pasaron. El FBX heredado se exporta con `global_scale=.01`: reimportado en Blender vacío mide 1/100 del GLB. QA documenta valor crudo y normalización×100; **no demuestra escala en Roblox**. Sin colocar en mapa, colliders ni interacción. Usar colliders simples y mantener detalles sin colisión en la futura copia de Studio.

**Estado real del motor:** cero ventanas Studio abiertas/controladas por Codex en este bloque; no importación/publicación, Play, FPS, sonido ni prueba de combate. Se preservaron cambios ajenos en `apocalipsis-juego/client/ImpactoFX.lua`, `Viewmodel.client.lua`, `src/Disparo.lua`, `Impactos.lua` y Slime Rush server/client. Ningún push. Pendiente feedback visual, importar en copia temporal con autorización concreta si requiere publicación, comparar escala/grip/rig, validar interrupciones y varios NPC, medir FPS. No seguir inventando arte indefinidamente: los tres bloques nocturnos están preparados.

**Paquete local verificado:** `C:/Users/maiko/Documents/Codex/2026-10-21/c/outputs/LUTO - arte nocturno 2026-10-24.zip`, 169 archivos / 85.095.912 bytes. SHA256 `2d451d38eeceebc8f1916e0391588f3a25e60b5bfc0f9b21583e579d0d983030`. CRC y SHA de todos los miembros comparados con disco. Manifiestos por carpeta; no incluye fotos diagnósticas obsoletas, cachés ni helpers Studio. `coordinacion/empaquetar-luto-noche.py` reproduce selección y verifica el paquete sin sobrescribir uno existente. Copia de estos documentos antes de editar en `work/backups/Coordinacion-before-night-delivery-2026-10-24.zip`. Relevo vigente `RELEVO-NOCHE-LUTO.md`.

**Nota para cerebro (no se escribió vault remoto):** congelar atlas junto a un .blend que se mueve de carpeta; `Image.has_data` puede ser falso por carga diferida aun con archivo empaquetado, por lo que hay que leer píxeles para verificarlo. Validar extremos de bucle además de duración. No mezclar acciones de Mundo/VM al exportar FBX; exportar un rig con sus acciones aisladas. Eliminar una Action no borra pose: resetear transformaciones antes de guardar. Para efectos, verificar renovación y limpieza sin confundir mocks con render real. Separar fotografía de pose Blender de la apariencia futura de ParticleEmitter. La normalización de escala offline siempre debe quedar explícita.

Cierre confirmado: assets y fuentes en commit local `ebe6a52`, sin push. Los 163 archivos cubiertos por manifiestos también coincidieron byte a byte con el índice Git; `.gitattributes` preserva esos bytes solo en las cuatro carpetas nuevas. La automatización `continuar-laboratorio-slime` / «Continuar arte de LUTO» fue **eliminada de la app** al agotar los tres bloques previstos, para no repetir trabajo. No afecta archivos ni commits. El paquete contiene el relevo anterior a este cierre administrativo; arte, QA y SHA siguen vigentes. Próximo paso humano: feedback/importación y pruebas de motor, no otro ciclo automático de modelos.
