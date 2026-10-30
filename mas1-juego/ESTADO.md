# mas1-juego — estado (30/10/2026, Coordinador)
Programación de «+1 de lanzamiento por segundo» (Maikol, 30/10: «todo seguido»). Linux 2.0 revisa y hace la interfaz y los efectos.

## Fallos y límites (primero)
- **SIN PROBAR EN STUDIO.** Nada de esto se ha ejecutado en Roblox: Studio rechazó el acceso de control dos veces el 30/10. Solo la lógica pura está probada, con lupa:
  - `tests/test_vuelo.py`;
  - `tests/test_mascotas.py`;
  - `tests/test_partida.py`: un cliente simulado vuela con `Manejo` y el servidor valida con `Partida`, con lag y con trampas.
- **Lo que más puede fallar en Studio** es la física del cliente. El humanoide pasa a estado `Physics` con `LinearVelocity` y `AlignOrientation` en la raíz, así que hay que mirar:
  - la postura tumbada;
  - la cámara;
  - el aterrizaje sobre el carril;
  - que el servidor no corrija de más con lag de verdad.
- **Cifras provisionales.** Están en `src/Vuelo.lua` y se ajustan jugando:
  - con potencia 0, unos 12 s de energía, un vuelo de unos 670 studs y aterrizaje en la Tormenta (x4);
  - la energía crece con la raíz de la potencia.
- **Sin guardado** (hito 5): el dinero, la exp y los cofres se pierden al salir.
- **Sin mascotas equipadas** (hito 4) **y sin potencia que suba** (hito 3, lo siguiente): de momento todos los vuelos son con potencia 0.
- **Enemigos y cofres hechos con piezas, PROVISIONALES.** Las mallas voxel de `mas1-arte/enemigos-v02` hay que importarlas en Studio. Los enemigos no hacen daño: solo se golpean.
- **Cielo por zona**: solo cambian la hora y la `Atmosphere`. El Espacio de noche usa las estrellas por defecto de Roblox.
- **El botón LANZAR y el cartel de resultado son provisionales**: la interfaz buena la hace Linux 2.0.
- **`server/DemoVisual.server.lua`** sigue en el proyecto: no hay que activar `MAS1_Demo` con el juego de verdad, porque pisa los atributos.

## Hitos
1. **Vuelo — hecho, sin probar en Studio.**
   - El lanzamiento sale del cañón (`MAS1_Canon`) o de donde estés.
   - W da boost, A/D mueven de lado, Espacio sube y S baja.
   - El ataque gasta energía. Sin energía se planea y se aterriza solo sobre el carril.
   - Al aterrizar se cobra según la zona donde caes.
   - Pensado para ser **fácil y que se sienta bien**:
     - avanzar es automático;
     - un muro suave te mantiene en el carril;
     - mientras queda energía no puedes bajar del mínimo;
     - los cambios de velocidad son suaves;
     - el personaje se inclina en los giros;
     - la cámara se aleja con la velocidad;
     - el campo de visión se abre con el boost.
2. **Aros, enemigos y cofres — hecho, sin probar en Studio.**
   - **Aros**: los del mapa cuentan una vez por vuelo, con margen por fuera del borde, y valen 25 puntos.
   - **Enemigos**: 22 repartidos por zona con los tipos de `enemigos-v02`, separados y lejos de los aros. Se golpean con el ataque a 12 studs (30 puntos) y vuelven a los 15 s.
   - **Cofres voladores**: salen por delante y huyen más rápido que el vuelo normal. Con boost se pillan en unos 4 s (250 puntos) y salen 2 por vuelo.
   - **Cielo y niebla por zona**.
   - **Mapa**: aros más grandes, bordes del carril en Neon y flechas y xN más grandes (crítica del director).
   - **Ajustes**: el boost gasta +1,5/s (antes +2,5/s), para que perseguir un cofre compense.
3. Entrenamiento (+1 potencia/s), zonas AFK, rebirth y alas que escalan con el rebirth.
4. Mascotas: abrir huevos, inventario, equipar 3 y bonus aplicados al vuelo; el fénix solo con Robux, sin productos configurados.
5. Guardado con DataStore y antitrampas básicas.
6. Alas: iniciales, robóticas y avanzadas.

## Cómo probarlo
1. Abre `build/Mas1-prueba.rbxlx` en Studio con `File → Open from File`. Es local: no sube nada. Lleva el mapa v01 en piezas y todos los scripts, colocados como los pondría Rojo.
2. Dale a Play. Sales al principio del Mar de Nubes.
3. Pulsa F o el botón ¡LANZAR!. Para vuelos más largos, sube el atributo `Potencia` del jugador en la vista del servidor.
4. Regenerar la place: `python tools/construir_place.py`.
5. Pruebas, desde `mas1-juego`: `python tests/test_partida.py`, `test_encuentros.py`, `test_vuelo.py` y `test_mascotas.py`.
