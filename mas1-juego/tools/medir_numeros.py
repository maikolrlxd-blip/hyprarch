# Mide los números de «+1 de lanzamiento por segundo» con los módulos del juego (src/Vuelo.lua, Alas.lua, Mascotas.lua) en lupa:
# cuánto dura y cuánto da un vuelo según la potencia, cuánto cuesta en tiempo cada huevo y cada rebirth. Simula el vuelo como el
# servidor (lanzamiento del cañón, vuelo con energía, planeo hasta el suelo) con un jugador «normal»: cruza la mitad de los aros, coge
# un tercio de los orbes, no ataca y no persigue cofres. Escribe NUMEROS.md.
#   python tools/medir_numeros.py
import math, os, lupa

JUEGO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
l = lupa.LuaRuntime()
cargar = lambda n: l.execute(open(os.path.join(JUEGO, 'src', n), encoding='utf-8').read())
V, A, M = cargar('Vuelo.lua'), cargar('Alas.lua'), cargar('Mascotas.lua')
C = V.CFG

ALTURA_PLANEO = 24     # studs sobre el carril al quedarse sin energía (el cañón sube unos 36; se vuela entre 6 y 48)
EN_TIERRA = 11         # s por vuelo fuera del aire: 3 de vuelta al lobby + ir al cañón y lanzarse
AROS_CADA, ENEMIGO_CADA, ORBES_CADA = 120, 150, 180 / 7   # studs entre aros (3 por bloque de 360), enemigos y orbes
PARTE_AROS, PARTE_ORBES = 0.5, 1 / 3


def vuelo(potencia, bonus=None, golpes=0):
    """Un vuelo entero: distancia, tiempo, zona, dinero, exp y orbes."""
    b = l.table_from(bonus or {'impulso': 1, 'resistencia': 1, 'dinero': 1, 'exp': 1})
    v = V.nuevo(potencia, b)
    imp = v.bonus.impulso or 1
    for _ in range(golpes):   # golpes que aciertan (el servidor llama a golpearEnemigo tras atacar)
        if V.atacar(v):
            V.golpearEnemigo(v)
    dt, t = 0.05, 0.0
    while t < C.lanzamiento.duracion:            # disparo del cañón
        V.paso(v, dt, None)
        v.distancia += (C.lanzamiento.velocidad - C.velocidadBase) * imp * dt
        t += dt
    while not v.planeando and v.distancia < C.finMapa:
        V.paso(v, dt, None)
    if v.distancia >= C.finMapa:   # final del mapa: el servidor deja de avanzar y aterriza en el último tramo
        v.distancia = C.finMapa
    else:
        planeo = ALTURA_PLANEO / C.caidaPlaneo
        for _ in range(int(planeo / dt)):
            V.paso(v, dt, None)
        v.distancia = min(v.distancia, C.finMapa)
    d = v.distancia
    for _ in range(int(d / AROS_CADA * PARTE_AROS)):
        V.cruzarAro(v)
    r = V.aterrizar(v, min(d, C.finMapa))
    return {'dist': d, 't': v.tiempo, 'zona': r.multiplicador, 'dinero': r.dinero, 'exp': r.exp, 'orbes': int(d / ORBES_CADA * PARTE_ORBES)}


def fmt(x):
    return '{:,.0f}'.format(x).replace(',', '.')


def tiempo(s):
    return '%d s' % s if s < 90 else ('%.0f min' % (s / 60) if s < 5400 else '%.1f h' % (s / 3600))


out = ['# Números de «+1 de lanzamiento por segundo» (medidos con `tools/medir_numeros.py`)', '',
       'Medido con los módulos del juego en lupa, no jugando en Studio. Jugador «normal»: cruza la mitad de los aros, coge un tercio de los',
       'orbes, no ataca y no persigue cofres. Planeo desde %d studs; %d s en tierra por vuelo (vuelta al lobby y volver a lanzarse).' % (ALTURA_PLANEO, EN_TIERRA), '',
       'Ajustes hechos con estas medidas (05/11, Coordinador):',
       '- **Alas avanzadas**: pedían 10 cofres (salen 2 por vuelo) o 25.000, y se tenían en 3-7 minutos. Con ellas, potencia 100-300 ya',
       '  llega al final del mapa (x6). Ahora piden 60 cofres o 75.000: de media hora a una hora de juego.',
       '- **Golpes**: cada ataque gastaba 3 de energía (120 studs de vuelo) por 30 de bote, y atacar siempre hacía perder dinero y exp.',
       '  Ahora el golpe que acierta devuelve la energía; solo cuestan los golpes al aire.',
       '- **Sin tocar**: el ritmo del principio (primer huevo común en 3 vuelos), las zonas y los rebirths.',
       '- **Ojo, para decidir con Maikol**: el mapa acaba en %s studs. Con alas y mascotas buenas se llega al final con poca potencia, y' % fmt(C.finMapa),
       '  desde ahí más potencia ya no da más dinero por vuelo.', '']
for titulo, bonus in (('Sin mascotas ni alas', None),
                      ('Con las alas iniciales (3.er lanzamiento)', dict(A.bonus('iniciales', 0), dinero=1, exp=1)),
                      ('Con las alas avanzadas', dict(A.bonus('avanzadas', 0), dinero=1, exp=1))):
    out += ['## ' + titulo, '', '| Potencia | Vuelo | Distancia | Zona | Dinero | Exp | Orbes (+potencia) | Dinero por minuto |', '|---|---|---|---|---|---|---|---|']
    for p in (0, 10, 50, 100, 300, 1000, 3000, 10000):
        r = vuelo(p, bonus)
        out.append('| %s | %s | %s studs | x%d | %s | %s | %d | %s |' % (fmt(p), tiempo(r['t']), fmt(r['dist']), r['zona'], fmt(r['dinero']),
                                                                       fmt(r['exp']), r['orbes'], fmt(r['dinero'] / (r['t'] + EN_TIERRA) * 60)))
    out.append('')

out += ['## Huevos: vuelos para pagar cada uno', '', '| Huevo | Precio | Potencia 10 | Potencia 100 | Potencia 1.000 | Potencia 10.000 |', '|---|---|---|---|---|---|']
precios = sorted(((k, v) for k, v in M.PRECIO_HUEVO.items()), key=lambda kv: kv[1])
for k, precio in precios:
    fila = []
    for p in (10, 100, 1000, 10000):
        r = vuelo(p)
        n = math.ceil(precio / r['dinero'])
        fila.append('%d (%s)' % (n, tiempo(n * (r['t'] + EN_TIERRA))))
    out.append('| %s | %s | %s |' % (k, fmt(precio), ' | '.join(fila)))
out.append('')

out += ['## Potencia: tiempo en tierra para llegar', '',
        '| Potencia | Normal (+1/s) | Zona AFK (x%.1f) | Circuito corriendo (x%d) | Con 2 rebirths, AFK |' % (C.multAFK, C.multEntreno), '|---|---|---|---|---|']
for p in (70, 500, 630, 1000, 2300, 6600):
    fila = [tiempo(p / V.ritmoEntreno(r, z, True)) for r, z in ((0, None), (0, 'afk'), (0, 'entreno'), (2, 'afk'))]
    out.append('| %s | %s |' % (fmt(p), ' | '.join(fila)))
out += ['', 'Zonas: x3 pide unos 70 de potencia, x4 ~630, x5 ~2.300 y x6 ~6.600 (sin bonus).', '',
        '## Rebirths', '', '| Rebirth | Potencia que pide | Tiempo en la zona AFK con los rebirths anteriores | Total acumulado |', '|---|---|---|---|']
total = 0
for r in range(6):
    coste = V.costeRebirth(r)
    s = coste / V.ritmoEntreno(r, 'afk', False)
    total += s
    out.append('| %d.º | %s | %s | %s |' % (r + 1, fmt(coste), tiempo(s), tiempo(total)))
out.append('')

out += ['## Alas avanzadas: cuánto cuesta conseguirlas', '']
for p in (10, 100, 1000):
    r = vuelo(p)
    ciclo = r['t'] + EN_TIERRA
    out.append('- Potencia %s: %s de dinero = %d vuelos (%s); %d cofres atrapando 1 por vuelo = %s, o 2 por vuelo = %s.'
               % (fmt(p), fmt(A.get('avanzadas').precio), math.ceil(A.get('avanzadas').precio / r['dinero']),
                  tiempo(math.ceil(A.get('avanzadas').precio / r['dinero']) * ciclo), A.get('avanzadas').pide.cofres,
                  tiempo(A.get('avanzadas').pide.cofres * ciclo), tiempo(A.get('avanzadas').pide.cofres / 2 * ciclo)))
out.append('')

# golpes: lo que da un enemigo frente a la energía que gasta
sin, con = vuelo(100), vuelo(100, golpes=5)
out += ['## Atacar enemigos', '',
        'Con potencia 100, 5 golpes que aciertan cambian el vuelo de %s a %s de dinero y de %s a %s de exp. Atacar gasta %d de energía (%d studs'
        % (fmt(sin['dinero']), fmt(con['dinero']), fmt(sin['exp']), fmt(con['exp']), C.costeAtaque, C.costeAtaque * C.velocidadBase),
        'de vuelo); el golpe que acierta la devuelve y suma %d al bote.' % C.puntosEnemigo, '']
open(os.path.join(JUEGO, 'NUMEROS.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
