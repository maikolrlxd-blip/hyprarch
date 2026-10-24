# Zombi mujer — reacciones al fuego v01

24/10/2026. Reutiliza exactamente la geometría y UV de la zombi del proyecto: 1966 triángulos, 15 mallas y 16 huesos. Base protegida en `fuentes/Base-zombi.blend`, SHA en `datos.json`. Cuatro atlas usados de 1024, empaquetados y copiados localmente para no depender de rutas de la base.

Tres clips nuevos: **QuemadoInicio 0,85 s**, **QuemadoBucle 1,2 s**, **QuemadoCaer 1,8 s**. Se entregan Blender, FBX completo, tres FBX individuales y GLB con tres acciones. El bucle agita brazos/cabeza con los pies fijos; todavía requiere decidir cómo mezclarlo con locomoción de la IA. Caer baja a las rodillas y termina en el suelo. No reemplaza los clips originales.

`qa/VALIDACION.json` PASADA en Blender: comparación exacta de geometría/UV con la base, pesos, texturas, neutral, duraciones y reimportación de tres FBX más GLB. Extremos del bucle coinciden (error de matriz ~2,6e-17). Mínimo Z por fotogramas enteros: Inicio/Bucle +0,02808; Caer +0,021. Corrección de contacto de Caer verificada cada cuarto de fotograma: mínimo +0,02013. Esto comprueba malla evaluada sobre un plano; no es física ni colisión del motor.

Hoja de seis poses `previews/Zombi-quemado-v01-secuencia-Blender.png` inspeccionada. **Sin VFX en esas fotos**: el módulo ParticleEmitter del lanzallamas es otra entrega. Sin prueba Roblox, sin audio ni conexión a IA/daño. No afirmar quemado jugable. Inicio solo al comenzar el estado; Bucle mientras siga vivo; Caer únicamente tras muerte confirmada por servidor. La expiración del efecto no debe matar al NPC.

Durante la construcción se detectó un guard que solo aceptaba la acción Caer y rutas externas de texturas tras copiar la base. Se corrigieron en los fuentes locales, permitiendo explícitamente QuemadoCaer y cargando atlas congelados. El primer chequeo de imágenes confundía carga diferida de píxeles con ausencia: se verificaron los datos empaquetados leyendo sus píxeles. No hubo cambio de malla para resolverlo. Logs finales: build-v01c y validate-v01b.
