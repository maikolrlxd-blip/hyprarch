# Referencia de estilo para las mascotas: «Roba un huevo» (Steal an Egg)
Maikol pidió el 29/10: «toma referencia de roba un huevo en los diseños de las mascotas». Aquí queda lo que miré, lo que saqué y lo que apliqué. Solo se toma el **estilo**: no se copia ningún personaje ni asset.

## Qué es y qué miré
- **Robar un huevo** (en inglés *Steal an Egg*, [página de Roblox](https://www.roblox.com/games/107778070777162/Steal-An-Egg), creador «and Collect Rare Pets»): robas huevos de nidos custodiados, los incubas y las mascotas dan dinero cada segundo. 13 biomas y unas 265 mascotas según [rblxguide](https://rblxguide.com/es/games/steal-an-egg/pets); [Beebom](https://beebom.com/steal-an-egg-all-eggs/) lista animales reales, «brainrots» y míticos (hay fénix, cerbero, kitsune, unicornio, esfinge, dragones; no vi águila ni grifo).
- Miré los **iconos de mascotas del listado de rblxguide**: comunes (pollo, pájaro, cisne, tucán, búho, pingüino, pterodáctilo), medias y raras con aves o alas (grulla, paloma de luz, cordero alado, pavo real sagrado, pegaso, arcángel, murciélago, arrendajo encantado, terrorbird, fénix, gárgola). También la miniatura oficial.
- **No pude ver capturas de partida** (ni entrar al juego): lo de abajo sale de iconos, no de modelos en juego.

## Rasgos que se ven en los iconos
1. **Voxeles gruesos y simples** en las comunes: silueta legible de un vistazo, cabeza grande, patas cortas, pocas piezas.
2. **Contorno negro grueso** solo en las **comunes y medias** (pollo, cisne, tucán, pterodáctilo, búho, tigre, unicornio). **Las raras no lo llevan**: grulla, paloma de luz, cordero alado, pavo real, pegaso, arcángel, arrendajo, terrorbird, gárgola y murciélago salen sin contorno, con sombreado suave.
3. **Ojos diminutos**: un punto negro (pollo, cisne); más expresión en las raras (arrendajo con aro amarillo, gárgola con ojos rojos).
4. **Escamas de plumas en relieve**: cubitos planos que sobresalen de la piel en filas desiguales (cisne, búho, terrorbird, cordero): da el aspecto «chunky» sin cambiar la silueta.
5. **Color**: pastel y saturado a la vez, sombras frías (lavanda), variación de un voxel a otro.
6. **El detalle sube con la rareza**: las raras llevan **alas grandes de plumas en capas con degradado y brillo dorado/naranja en los bordes**, **adornos dorados en rombo** (frente, pecho, alas), colas grandes en abanico (pavo real) y partes que brillan.
7. **Fénix** (el común del juego): llamas de píxeles naranja y amarillo, alas abiertas en V, plumas con el borde en dientes de sierra.

## Qué apliqué (águila legendaria, grifo mítico, fénix) — versión 02 (29/10, tras «se ve feo y buguiado»)
- Cuerpo **rechoncho y cabeza grande**, ojos diminutos con brillo y ceja fiera; pico ancho en gancho.
- **Escamas de plumas en relieve** pegadas a las caras de los voxeles (pecho en tresbolillo, flancos y espalda al azar): nada flota.
- **Alas en arco de plumas en abanico** (siete u ocho primarias, seis secundarias y dos filas de cubiertas), con **bandas de color que acaban en la punta dorada** (degradado por tramos) y **rombos dorados**.
- Cola de abanico unida al cuerpo (águila), borla de león en llama (grifo) y siete plumas largas curvadas (fénix).
- **Sin contorno negro** en estas tres: las raras del juego no lo llevan y la carcasa invertida de la v01 daba líneas sueltas dentro del pecho. La herramienta `tools/contorno_negro.py` sigue ahí para las comunes si Maikol las quiere con contorno.
- Se mantienen la celda de 0,2 studs y el rig de ocho huesos de Codex con los clips Fly / Glide / Celebrate.

## Pendiente de decidir
- Si Maikol quiere el contorno negro en las comunes, el tamaño de voxel de la referencia (más fino o igual de grueso), o que las mascotas salgan de huevos propios (el diseño de Codex no los tiene). Las mascotas comunes de Codex siguen su camino propio: la decisión de adaptarlas es suya.
- Nada de esto está probado en Roblox.
