# Pruebas de src/Encuentros.lua y de los encuentros dentro de src/Partida.lua, con lupa: aros, golpes, reparto de enemigos y cofres
# que huyen (sin boost no se pillan, con boost si). Ejecutar desde mas1-juego: python tests/test_encuentros.py
import math
import random
import lupa

l = lupa.LuaRuntime()
V = l.execute(open('src/Vuelo.lua', encoding='utf-8').read())
E = l.execute(open('src/Encuentros.lua', encoding='utf-8').read())
P = l.execute(open('src/Partida.lua', encoding='utf-8').read())
Man = l.execute(open('src/Manejo.lua', encoding='utf-8').read())
T = l.table_from
EC, VC = E.CFG, V.CFG


def vec(x, y, z):
    return T({'x': x, 'y': y, 'z': z})


def aro(x, y, z, r=8.0):
    return T({'centro': vec(x, y, z), 'radio': r})


# aros: cruzar por el centro, por el borde con margen, por fuera, y sin llegar al plano
A = aro(0, 20, -300)
assert E.cruzaAro(vec(0, 20, -299), vec(0, 20, -301), A)
assert E.cruzaAro(vec(9.2, 20, -299), vec(9.2, 20, -301), A)         # radio 8 + margen 1,5
assert not E.cruzaAro(vec(10, 20, -299), vec(10, 20, -301), A)
assert not E.cruzaAro(vec(0, 20, -290), vec(0, 20, -299), A)
assert E.cruzaAro(vec(0, 14, -295), vec(0, 26, -305), A)             # en diagonal: cuenta el punto donde cruza el plano

# golpe: el vivo mas cercano al alcance, delante o como mucho 4 studs detras
en = T({1: T({'pos': vec(0, 20, -110), 'vivo': True}), 2: T({'pos': vec(3, 20, -106), 'vivo': True}),
        3: T({'pos': vec(0, 20, -95), 'vivo': True}), 4: T({'pos': vec(0, 20, -104), 'vivo': False})})
assert E.enemigoAlAlcance(vec(0, 20, -100), en) == 2   # el 4 esta mas cerca pero no vive; el 3 queda 5 detras
assert E.enemigoAlAlcance(vec(0, 20, -60), en) is None

# reparto de enemigos con los aros del mapa (3 por zona como en mapa-v01): separados, lejos de los aros y dentro del carril
rnd = random.Random(7)
aros = [aro(rnd.uniform(-12, 12), z, -(172 + i * 360 + dy)) for i in range(4) for dy, z in ((80, 14), (170, 20), (260, 26))]
lista = E.colocarEnemigos(T(dict(enumerate(aros, 1))), random.Random(3).random)
ps = [(e.pos.x, e.pos.y, e.pos.z) for e in lista.values()]
total = sum(z.cantidad for z in EC.zonas.values())
assert len(ps) >= 0.8 * total, (len(ps), total)
for i, p in enumerate(ps):
    assert abs(p[0]) <= 24 and 10 <= p[1] <= 28, p
    for q in ps[i + 1:]:
        assert math.dist(p, q) >= EC.separacion, (p, q)
    for a in aros:
        c = (a.centro.x, a.centro.y, a.centro.z)
        assert math.dist(p, c) >= EC.lejosDeAros + a.radio, (p, c)
tipos = {e.tipo for e in lista.values()}
assert tipos == {'globo', 'nube', 'nubarron', 'cometa', 'ovni', 'meteorito'}, tipos
print('enemigos: %d de %d huecos, tipos %s' % (len(ps), total, sorted(tipos)))


# cofre: a velocidad normal no se pilla; con boost, si
def perseguir(vel, segundos=30, dt=1 / 60):
    c = E.nuevoCofre(vec(0, 18, 0))
    z, t = 0.0, 0.0
    while t < segundos:
        z -= vel * dt
        t += dt
        if E.pasoCofre(c, dt, vec(math.sin(t * 0.8) * 12, 18 + math.sin(t * 1.3) * 3, z)):
            return t
    return None


assert perseguir(VC.velocidadBase) is None
t = perseguir(VC.velocidadBoost)
assert t is not None and t < 12, t
print('cofre: sin boost no se pilla; con boost, a los %.1f s' % t)


# dentro de Partida: un aro en el camino cuenta una vez, un golpe alcanza al enemigo de delante y el cofre se pilla con boost
def vuelo_con_mundo(boost):
    s = P.nueva(V, E)
    pos = [0.0, 4.0, -182.0]
    P.lanzar(s, vec(*pos), 400, None)  # con potencia 400 hay energia para el boost y el golpe
    mundo = T({'aros': T({1: aro(0, 22, -300)}), 'enemigos': T({1: T({'pos': vec(0, 22, -420), 'vivo': True})})})
    m, dt, aros_vistos, golpe, atrapados = Man.nuevo(), 1 / 60, 0, None, 0
    for _ in range(60 * 60):
        P.intencion(s, 'boost', boost and pos[2] < -430)  # como jugaria alguien: boost al ir a por el cofre
        Man.paso(m, dt, T({}), T({'planeando': s.v.planeando, 'boost': P.boostActivo(s), 'impulso': 1}), pos[0], pos[1], VC)
        pos = [pos[0] + m.vx * dt, max(3.0, pos[1] + m.vy * dt), pos[2] - m.vf * dt]
        if s.cofre and pos[2] < -430:  # pasados el aro y el enemigo, va a por el cofre (de lado y de alto)
            pos[0] += (s.cofre.pos.x - pos[0]) * 0.1
            pos[1] += (s.cofre.pos.y - pos[1]) * 0.1 if not s.v.planeando else 0
        if golpe is None and pos[2] < -412:
            golpe = P.intencion(s, 'ataque', None, mundo)[0]
        r = P.tick(s, dt, vec(*pos), mundo)
        if r.aros:
            aros_vistos += len(list(r.aros.values()))
        if r.cofreAtrapado:
            atrapados += 1
        if r.corregir:
            pos = [r.corregir.x, r.corregir.y, r.corregir.z]
        if r.aterrizaje:
            return s, r.aterrizaje, aros_vistos, golpe, atrapados, mundo
    raise AssertionError('no aterrizo')


s, res, aros_vistos, golpe, atrapados, mundo = vuelo_con_mundo(boost=True)
assert aros_vistos == 1 and res.aros == 1, (aros_vistos, res.aros)
assert golpe == 'golpe' and mundo.enemigos[1].vivo is False and res.golpes == 1
assert atrapados >= 1 and res.cofres == atrapados and s.violaciones == 0, (atrapados, s.violaciones)
esperado = res.distancia + VC.puntosAro + VC.puntosEnemigo + VC.puntosCofre * atrapados
assert res.dinero == math.floor(esperado * res.multiplicador), (res.dinero, esperado, res.multiplicador)
print('vuelo con encuentros: 1 aro, 1 golpe, %d cofres, %.0f studs, %d de dinero' % (atrapados, res.distancia, res.dinero))
s, res, _, _, atrapados, _ = vuelo_con_mundo(boost=False)
assert atrapados == 0 and res.cofres == 0
print('ok')
