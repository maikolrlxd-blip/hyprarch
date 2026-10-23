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
