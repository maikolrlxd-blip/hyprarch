# Números de «+1 de lanzamiento por segundo» (medidos con `tools/medir_numeros.py`)

Medido con los módulos del juego en lupa, no jugando en Studio. Jugador «normal»: cruza la mitad de los aros, coge un tercio de los
orbes, no ataca y no persigue cofres. Planeo desde 24 studs; 11 s en tierra por vuelo (vuelta al lobby y volver a lanzarse).

Ajustes hechos con estas medidas (05/11, Coordinador):
- **Alas avanzadas**: pedían 10 cofres (salen 2 por vuelo) o 25.000, y se tenían en 3-7 minutos. Con ellas, potencia 100-300 ya
  llega al final del mapa (x6). Ahora piden 60 cofres o 75.000: de media hora a una hora de juego.
- **Golpes**: cada ataque gastaba 3 de energía (120 studs de vuelo) por 30 de bote, y atacar siempre hacía perder dinero y exp.
  Ahora el golpe que acierta devuelve la energía; solo cuestan los golpes al aire.
- **Sin tocar**: el ritmo del principio (primer huevo común en 3 vuelos), las zonas y los rebirths.
- **Ojo, para decidir con Maikol**: el mapa acaba en 8.760 studs. Con alas y mascotas buenas se llega al final con poca potencia, y
  desde ahí más potencia ya no da más dinero por vuelo.

## Sin mascotas ni alas

| Potencia | Vuelo | Distancia | Zona | Dinero | Exp | Orbes (+potencia) | Dinero por minuto |
|---|---|---|---|---|---|---|---|
| 0 | 17 s | 692 studs | x2 | 178 | 73 | 8 | 377 |
| 10 | 22 s | 896 studs | x2 | 233 | 95 | 11 | 419 |
| 50 | 28 s | 1.146 studs | x2 | 299 | 122 | 14 | 452 |
| 100 | 33 s | 1.332 studs | x3 | 524 | 143 | 17 | 710 |
| 300 | 45 s | 1.802 studs | x3 | 711 | 194 | 23 | 761 |
| 1.000 | 67 s | 2.716 studs | x4 | 1.435 | 293 | 35 | 1.091 |
| 3.000 | 2 min | 4.198 studs | x5 | 2.774 | 453 | 54 | 1.435 |
| 10.000 | 3 min | 7.092 studs | x6 | 5.628 | 767 | 91 | 1.793 |

## Con las alas iniciales (3.er lanzamiento)

| Potencia | Vuelo | Distancia | Zona | Dinero | Exp | Orbes (+potencia) | Dinero por minuto |
|---|---|---|---|---|---|---|---|
| 0 | 23 s | 1.087 studs | x2 | 284 | 116 | 14 | 497 |
| 10 | 30 s | 1.452 studs | x3 | 576 | 157 | 18 | 825 |
| 50 | 40 s | 1.903 studs | x3 | 748 | 204 | 24 | 875 |
| 100 | 47 s | 2.241 studs | x3 | 887 | 242 | 29 | 912 |
| 300 | 64 s | 3.084 studs | x4 | 1.624 | 332 | 39 | 1.284 |
| 1.000 | 2 min | 4.730 studs | x5 | 3.123 | 511 | 61 | 1.700 |
| 3.000 | 3 min | 7.399 studs | x6 | 5.867 | 799 | 95 | 2.123 |
| 10.000 | 3 min | 8.760 studs | x6 | 6.955 | 948 | 113 | 2.171 |

## Con las alas avanzadas

| Potencia | Vuelo | Distancia | Zona | Dinero | Exp | Orbes (+potencia) | Dinero por minuto |
|---|---|---|---|---|---|---|---|
| 0 | 41 s | 2.846 studs | x4 | 1.498 | 306 | 36 | 1.719 |
| 10 | 56 s | 3.940 studs | x5 | 2.604 | 426 | 51 | 2.315 |
| 50 | 75 s | 5.291 studs | x5 | 3.504 | 573 | 68 | 2.438 |
| 100 | 89 s | 6.306 studs | x6 | 5.008 | 682 | 81 | 2.994 |
| 300 | 2 min | 8.760 studs | x6 | 6.955 | 948 | 113 | 3.081 |
| 1.000 | 2 min | 8.760 studs | x6 | 6.955 | 948 | 113 | 3.177 |
| 3.000 | 2 min | 8.760 studs | x6 | 6.955 | 948 | 113 | 3.177 |
| 10.000 | 2 min | 8.760 studs | x6 | 6.955 | 948 | 113 | 3.177 |

## Huevos: vuelos para pagar cada uno

| Huevo | Precio | Potencia 10 | Potencia 100 | Potencia 1.000 | Potencia 10.000 |
|---|---|---|---|---|---|
| comun | 500 | 3 (2 min) | 1 (44 s) | 1 (78 s) | 1 (3 min) |
| poco_comun | 2.000 | 9 (5 min) | 4 (3 min) | 2 (3 min) | 1 (3 min) |
| raro | 8.000 | 35 (19 min) | 16 (12 min) | 6 (8 min) | 2 (6 min) |
| epico | 25.000 | 108 (60 min) | 48 (35 min) | 18 (24 min) | 5 (16 min) |
| legendario | 80.000 | 344 (3.2 h) | 153 (1.9 h) | 56 (74 min) | 15 (47 min) |
| mitico | 250.000 | 1073 (10.0 h) | 478 (5.9 h) | 175 (3.8 h) | 45 (2.4 h) |

## Potencia: tiempo en tierra para llegar

| Potencia | Normal (+1/s) | Zona AFK (x1.5) | Circuito corriendo (x2) | Con 2 rebirths, AFK |
|---|---|---|---|---|
| 70 | 70 s | 46 s | 35 s | 23 s |
| 500 | 8 min | 6 min | 4 min | 3 min |
| 630 | 10 min | 7 min | 5 min | 4 min |
| 1.000 | 17 min | 11 min | 8 min | 6 min |
| 2.300 | 38 min | 26 min | 19 min | 13 min |
| 6.600 | 1.8 h | 73 min | 55 min | 37 min |

Zonas: x3 pide unos 70 de potencia, x4 ~630, x5 ~2.300 y x6 ~6.600 (sin bonus).

## Rebirths

| Rebirth | Potencia que pide | Tiempo en la zona AFK con los rebirths anteriores | Total acumulado |
|---|---|---|---|
| 1.º | 500 | 6 min | 6 min |
| 2.º | 1.000 | 7 min | 13 min |
| 3.º | 2.000 | 11 min | 24 min |
| 4.º | 4.000 | 18 min | 42 min |
| 5.º | 8.000 | 30 min | 71 min |
| 6.º | 16.000 | 51 min | 2.0 h |

## Alas avanzadas: cuánto cuesta conseguirlas

- Potencia 10: 75.000 de dinero = 322 vuelos (3.0 h); 60 cofres atrapando 1 por vuelo = 33 min, o 2 por vuelo = 17 min.
- Potencia 100: 75.000 de dinero = 144 vuelos (1.8 h); 60 cofres atrapando 1 por vuelo = 44 min, o 2 por vuelo = 22 min.
- Potencia 1.000: 75.000 de dinero = 53 vuelos (70 min); 60 cofres atrapando 1 por vuelo = 79 min, o 2 por vuelo = 39 min.

## Atacar enemigos

Con potencia 100, 5 golpes que aciertan cambian el vuelo de 524 a 578 de dinero y de 143 a 148 de exp. Atacar gasta 3 de energía (120 studs
de vuelo); el golpe que acierta la devuelve y suma 30 al bote.

