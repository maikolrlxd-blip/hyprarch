# Pruebas de src/Partida.lua (servidor) y src/Manejo.lua (cliente) con lupa: un cliente simulado vuela con Manejo y el servidor valida
# con Partida, con paquetes que llegan juntos como en una red de verdad. Tambien trampas: ir rapido sin boost, teletransportarse y
# quedarse en el aire al planear. Ejecutar desde mas1-juego: python tests/test_partida.py
import math
import lupa

l = lupa.LuaRuntime()
V = l.execute(open('src/Vuelo.lua', encoding='utf-8').read())
P = l.execute(open('src/Partida.lua', encoding='utf-8').read())
Man = l.execute(open('src/Manejo.lua', encoding='utf-8').read())
C = V.CFG
T = l.table_from


def vec(x, y, z):
    return T({'x': x, 'y': y, 'z': z})


def volar(potencia=0, mandos=None, trampa=None, dt=1 / 60, lag_cada=5, z0=-182.0, con_z=False):
    """Vuela de principio a fin. mandos(t) -> dict de entrada; trampa(t, pos) -> pos nueva o None. Devuelve (sesion, resultado, info)."""
    s = P.nueva(V)
    pos = [0.0, 4.0, z0]
    assert P.lanzar(s, vec(*pos), potencia, None)
    m = Man.nuevo()
    t, resultado, enviada, min_y, max_x, correcciones = 0.0, None, list(pos), 99.0, 0.0, 0
    while t < 400:
        ent = mandos(t) if mandos else {}
        if 'boost' in ent:
            P.intencion(s, 'boost', ent['boost'])
        info = T({'planeando': s.v.planeando, 'boost': P.boostActivo(s), 'impulso': 1})
        Man.paso(m, dt, T(ent), info, pos[0], pos[1], C, pos[2] if con_z else None)
        pos[0] += m.vx * dt
        pos[1] = max(3.0, pos[1] + m.vy * dt)  # de pie en el carril la raiz queda a 3 studs
        pos[2] -= m.vf * dt
        if trampa:
            q = trampa(t, pos)
            if q:
                pos = q
        if s.t > 1.5 and not s.v.planeando:
            min_y = min(min_y, pos[1])
        max_x = max(max_x, abs(pos[0]))
        t += dt
        if lag_cada and int(t / dt) % lag_cada == 0:  # este paquete no llega: el siguiente trae el doble de movimiento
            r = P.tick(s, dt, vec(*enviada))
        else:
            enviada = list(pos)
            r = P.tick(s, dt, vec(*pos))
        if r.corregir:
            correcciones += 1
            pos = [r.corregir.x, r.corregir.y, r.corregir.z]
        if r.aterrizaje:
            resultado = r.aterrizaje
            break
    return s, resultado, dict(min_y=min_y, max_x=max_x, t=t, correcciones=correcciones, pos=pos)


# energia: 12 s con potencia 0 y crece con la raiz de la potencia
assert abs(V.energiaMax(0) - 12) < 1e-9 and abs(V.energiaMax(100) - 28) < 1e-9 and V.energiaMax(400) > V.energiaMax(100)

# zonas segun la posicion hacia -Z (como las marcas de mapa-v01)
for d, m in ((10, 1), (50, 2), (200, 3), (600, 4), (900, 5), (1300, 6), (5000, 6)):
    assert V.multiplicadorZona(d) == m, (d, m)

# 1) vuelo normal sin mandos, con lag: ninguna correccion, aterriza solo y cobra en la zona donde cae
s, r, i = volar()
assert r is not None and s.violaciones == 0 and i['correcciones'] == 0, (s.violaciones, i)
assert r.multiplicador == V.multiplicadorZona(-i['pos'][2]) and r.dinero > 0
assert 500 < r.distancia < 800, r.distancia  # disparo + 10,8 s a 40 + planeo
print('vuelo normal: %.0f studs, x%d, %d de dinero, %.1f s' % (r.distancia, r.multiplicador, r.dinero, i['t']))

# 2) zigzag y boost a ratos, subiendo y bajando: tampoco hay correcciones, no se sale del carril ni baja del minimo con energia
def zigzag(t):
    return {'lateral': 1 if (t % 4) < 2 else -1, 'boost': (t % 6) < 3, 'subir': (t % 5) < 1, 'bajar': 2 < (t % 5) < 3.5}
s, r, i = volar(potencia=150, mandos=zigzag)
assert r is not None and s.violaciones == 0, (s.violaciones, i)
assert i['max_x'] <= C.anchoLibre + 1, i['max_x']
assert i['min_y'] >= C.alturaMin - 0.6, i['min_y']
print('zigzag con boost: %.0f studs, x%d, max |x| %.1f, altura minima %.1f' % (r.distancia, r.multiplicador, i['max_x'], i['min_y']))

# 3) trampa: el cliente vuela a velocidad de boost sin pedir boost (mientras le quede energia)
def rapido(t, pos):
    return [pos[0], pos[1], pos[2] - (C.velocidadBoost - C.velocidadBase) / 60] if 2 < t < 8 else None
s, r, i = volar(trampa=rapido)
assert s.violaciones > 0, 'no se detecto ir a velocidad de boost sin boost'
print('trampa de velocidad: %d correcciones' % s.violaciones)

# 4) trampa: teletransporte de 300 studs hacia delante; no cuenta para la distancia
def salto(t, pos):
    return [pos[0], pos[1], pos[2] - 300] if abs(t - 3) < 0.009 else None
s, r, i = volar(trampa=salto)
assert s.violaciones >= 1 and r.distancia < 800, (s.violaciones, r.distancia)
print('trampa de teletransporte: %d correcciones, %.0f studs' % (s.violaciones, r.distancia))

# 5) trampa: no bajar al planear (se queda arriba): aterriza a la fuerza al acabarse el margen
def flotar(t, pos):
    return [pos[0], max(pos[1], 20.0), pos[2]] if t > 14 else None
s, r, i = volar(trampa=flotar)
assert r is not None and i['pos'][1] > 10, i
print('trampa de quedarse en el aire: aterrizaje forzado a los %.1f s' % i['t'])

# 6) ataque: gasta energia y no se puede planeando; turbo da 1,2 s de boost
s = P.nueva(V); P.lanzar(s, vec(0, 4, 0), 0, None)
e = s.v.energia
assert P.intencion(s, 'puno', None)[0] == 'golpe' and abs(s.v.energia - (e - C.costeAtaque)) < 1e-9  # devuelve (efecto, enemigo)
P.intencion(s, 'turbo', None)
assert P.boostActivo(s)
for _ in range(80):
    P.tick(s, 1 / 60, vec(0, 4, 0))
assert not P.boostActivo(s)
s.v.energia = 0
P.tick(s, 1 / 60, vec(0, 4, 0))
assert s.v.planeando and P.intencion(s, 'ataque', None) is None

# 7) no se puede lanzar dos veces ni actuar en tierra
s = P.nueva(V)
assert P.intencion(s, 'boost', True) is None and P.tick(s, 0.1, vec(0, 3, 0)) is None
assert P.lanzar(s, vec(0, 4, 0), 0, None) and not P.lanzar(s, vec(0, 4, 0), 0, None)
# 8) final del mapa: lanzandose cerca del final con mucha potencia, aterriza en el ultimo tramo del carril (no cae al vacio)
s, r, i = volar(potencia=900, z0=-1400.0, con_z=True)
assert r is not None and -i['pos'][2] <= 1612 and i['pos'][1] <= 4.5, i
print('final del mapa: aterriza a %.0f studs (el carril acaba en 1612)' % -i['pos'][2])
print('ok')
