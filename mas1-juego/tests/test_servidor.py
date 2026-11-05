# Ejecuta de verdad server/Partida.server.lua y server/Guardado.lua (con el codigo real de src/) en un servidor de mentira
# (tests/roblox_falso.py): un jugador entra, se cargan sus datos con bloqueo de sesion, entrena, se lanza, vuela con el Manejo real,
# aterriza y cobra, abre un huevo, equipa alas, hace rebirth y sale; ademas casos raros: irse mientras cargan los datos, otro servidor
# con el bloqueo, un bloqueo con la hora rota, el DataStore caido, trampas de teletransporte, morir en pleno vuelo y spam de mensajes.
# Pilla errores de ejecucion (un nil, una variable mal escrita) en el codigo que Studio solo ejecuta al darle a Play, y los acuerdos
# entre servidor y cliente (el formato del atributo Misiones). NO prueba lo que depende del motor de Roblox. Ejecutar desde mas1-juego:
# python tests/test_servidor.py
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roblox_falso as R

cliente = open('client/Misiones.client.lua', encoding='utf-8').read()
assert '([^|;]+)|(%d+)|(%d+)|(%d+)' in cliente, 'el cliente cambio el patron del atributo Misiones: actualiza esta prueba'
FILA = re.compile(r'([^|;]+)\|(\d+)\|(\d+)\|(\d+)')


def volar(s, p, mandos=None, tope=240.0, trampa=None):
    """El cliente simulado: mueve el personaje con Manejo.lua cada fotograma y el servidor valida. Devuelve los segundos que dura."""
    Man = s.l.execute(open('src/Manejo.lua', encoding='utf-8').read())
    V = s.l.execute(open('src/Vuelo.lua', encoding='utf-8').read())
    T = s.l.table_from
    r = s.H.raiz(p).Position
    pos, m, t, dt = [r.X, r.Y, r.Z], Man.nuevo(), 0.0, 1 / 60
    while s.attr(p, 'EnVuelo') and t < tope:
        info = T({'planeando': bool(s.attr(p, 'Planeando')), 'boost': bool(s.attr(p, 'Boost')), 'impulso': s.attr(p, 'Impulso') or 1})
        Man.paso(m, dt, T(mandos(t) if mandos else {}), info, pos[0], pos[1], V.CFG, pos[2])
        pos = [pos[0] + m.vx * dt, max(3.0, pos[1] + m.vy * dt), pos[2] - m.vf * dt]
        if trampa:
            pos = trampa(t, pos) or pos
        s.H.mover(p, *pos)
        s.H.latido(dt)
        q = s.H.raiz(p).Position
        pos = [q.X, q.Y, q.Z]
        t += dt
    return t


def misiones_bien(s, p):
    filas = FILA.findall(s.attr(p, 'Misiones'))
    assert len(filas) == 3, ('las 3 misiones tienen que encajar con el patron del cliente', s.attr(p, 'Misiones'))
    return filas


# ------------------------------------------------------------------ 1) entrar: los datos se cargan con bloqueo y salen las misiones
# las 3 misiones iniciales se eligen al azar: se busca una semilla en la que una de ellas sea «Vuela metros» (la distancia se acumula con
# decimales: es la que rompia el panel), para que la prueba no dependa de la suerte
for semilla in range(1, 200):
    s = R.Servidor()
    s.l.execute('math.randomseed(%d)' % semilla)
    p = s.jugador('Ana', 1001)
    if 'Vuela metros' in s.attr(p, 'Misiones'):
        break
else:
    raise AssertionError('ninguna semilla da la mision «Vuela metros»: ha cambiado Misiones.LISTA')
assert s.attr(p, 'Potencia') == 0 and s.attr(p, 'CosteRebirth') == 500 and s.attr(p, 'EnVuelo') is False
misiones_bien(s, p)
guardado = s.almacen('j_1001')
assert guardado.bloqueo is not None and guardado.dato is not None, 'al cargar se toma el bloqueo de sesion'
assert s.eventos('MAS1_Inventario', p), 'se manda el inventario al entrar'

# ------------------------------------------------------------------ 2) entrenar en tierra: x1 normal, x1,5 en la zona AFK, x2 corriendo en el circuito
def entrenar(s, p, x, z, segundos, mover=0.0, direccion=0.0):
    s.H.mover(p, x, 3.0, z)
    s.H.direccion(p, direccion, 0, 0)
    s.avanzar(0.3)                       # un tick para fijar la posicion de partida
    antes = s.attr(p, 'Potencia')
    t, dt, v = 0.0, 1 / 60, mover
    while t < segundos:
        if mover:
            r = s.H.raiz(p).Position
            if r.X > 26 or r.X < 14:      # rebota dentro de la zona
                v = -v
            s.H.mover(p, r.X + v * dt, 3.0, z)
        s.H.latido(dt)
        t += dt
    return s.attr(p, 'Potencia') - antes


quieto = entrenar(s, p, 0.0, 14.0, 10)
assert 9 <= quieto <= 11, quieto
afk = entrenar(s, p, -20.0, -62.0, 10)
assert 14 <= afk <= 16, afk
corriendo = entrenar(s, p, 16.0, -62.0, 10, mover=6.0, direccion=1.0)
assert 19 <= corriendo <= 21, corriendo
falso = entrenar(s, p, 16.0, -62.0, 10, mover=0.0, direccion=1.0)    # MoveDirection dice que corre pero no se mueve: no vale
assert 9 <= falso <= 11, ('empujar quieto no cuenta como correr', falso)
print('entreno: quieto +%d, AFK +%d, corriendo +%d, direccion falsa +%d en 10 s' % (quieto, afk, corriendo, falso))

# ------------------------------------------------------------------ 3) lanzarse, volar y aterrizar
s.H.mover(p, 0.0, 3.0, 14.0)
s.H.direccion(p, 0, 0, 0)
potencia0 = s.attr(p, 'Potencia')
s.accion(p, 'lanzar')
assert s.attr(p, 'EnVuelo') is True and s.attr(p, 'Lanzamientos') == 1
assert 'lanzamiento' in [e[0] for e in s.eventos('MAS1_Efecto')]
duracion = volar(s, p)
assert s.attr(p, 'EnVuelo') is False, 'el vuelo no acabo'
res = s.eventos('MAS1_Resultado', p)
assert len(res) == 1, 'un resultado por vuelo'
r = res[0][0]
assert r['dinero'] > 0 and r['distancia'] > 400 and r['multiplicador'] >= 1 and r['tiempo'] > 5, dict(r.items())
assert all(k in r for k in ('distancia', 'aros', 'golpes', 'cofres', 'orbes', 'multiplicador', 'dinero', 'exp', 'tiempo')), 'campos del resultado'
assert s.attr(p, 'Dinero') >= r['dinero'] and s.attr(p, 'Exp') >= r['exp']
efectos = {e[0] for e in s.eventos('MAS1_Efecto')}
assert {'lanzamiento', 'aterrizaje'} <= efectos, efectos
assert s.attr(p, 'Potencia') >= potencia0 + (r['orbes'] or 0), 'cada orbe da +1 de potencia'
misiones_bien(s, p)
for e in s.eventos('MAS1_Orbe', p):
    assert len(e[0]) >= 1
# a los 3 s vuelve al lobby: el punto de aparicion
s.avanzar(3.5)
r2 = s.H.raiz(p).Position
assert abs(r2.X) < 1 and abs(r2.Z - 14) < 1 and 3 < r2.Y < 6, ('no volvio al lobby', r2.X, r2.Y, r2.Z)
print('vuelo: %.1f s, %.0f studs, x%d, +%d de dinero, %d aros, %d orbes' % (duracion, r['distancia'], r['multiplicador'], r['dinero'], r['aros'], r['orbes']))

# ------------------------------------------------------------------ 4) salir guarda y suelta el bloqueo; volver a entrar lo recupera
dinero, potencia, lanzamientos = s.attr(p, 'Dinero'), s.attr(p, 'Potencia'), s.attr(p, 'Lanzamientos')
s.H.sacar(p)
g = s.almacen('j_1001')
assert g.bloqueo is None, 'al salir se suelta el bloqueo'
assert g.dato.dinero == dinero and g.dato.lanzamientos == lanzamientos and abs(g.dato.potencia - potencia) < 1.0, (g.dato.dinero, dinero)
p = s.jugador('Ana', 1001)
assert s.attr(p, 'Dinero') == dinero and s.attr(p, 'Lanzamientos') == lanzamientos and s.attr(p, 'Potencia') == int(g.dato.potencia)
print('guardado: dinero %d, %d lanzamiento(s), potencia %d recuperados al volver' % (dinero, lanzamientos, s.attr(p, 'Potencia')))

# ------------------------------------------------------------------ 5) huevos, alas y rebirth
s.poner(p, 'Dinero', 200000)
n_inv = len(s.eventos('MAS1_Inventario', p))
s.accion(p, 'abrirHuevo', 'comun')
huevo = s.eventos('MAS1_Huevo', p)
assert len(huevo) == 1 and huevo[0][0]['rareza'] == 'comun' and huevo[0][0]['mascotaId'], huevo
assert s.attr(p, 'Dinero') == 200000 - 500 and len(s.eventos('MAS1_Inventario', p)) == n_inv + 1
mascota = huevo[0][0]['mascotaId']
s.accion(p, 'equipar', 'mascota', mascota)
assert s.attr(p, 'MascotasEq') == mascota, s.attr(p, 'MascotasEq')
s.accion(p, 'abrirHuevo', 'no_existe')
assert any('no existe' in a[0] for a in s.eventos('MAS1_Aviso', p)), 'un huevo que no existe da un aviso'
s.accion(p, 'comprarAla', 'avanzadas')
assert s.attr(p, 'Dinero') == 200000 - 500 - 75000
s.accion(p, 'equipar', 'ala', 'avanzadas')
assert s.attr(p, 'Alas') == 'avanzadas'
s.accion(p, 'comprarAla', 'iniciales')   # las de requisito no se compran
assert any('no se compran' in a[0] for a in s.eventos('MAS1_Aviso', p))
s.H.mover(p, 0.0, 3.0, 14.0)
s.accion(p, 'lanzar')
assert s.attr(p, 'Impulso') > 1.8 - 1e-9 and s.attr(p, 'EnergiaMax') >= 36, ('las alas avanzadas dan x1,8 de impulso y x3 de energia', s.attr(p, 'Impulso'), s.attr(p, 'EnergiaMax'))
s.accion(p, 'abrirHuevo', 'comun')     # en pleno vuelo no se hace nada
assert s.attr(p, 'Dinero') == 200000 - 500 - 75000 and any('en tierra' in a[0] for a in s.eventos('MAS1_Aviso', p))
volar(s, p)
s.avanzar(3.5)
s.poner(p, 'Potencia', 100)
s.accion(p, 'rebirth')
assert s.attr(p, 'Rebirths') == 0 and any('Te falta potencia' in a[0] for a in s.eventos('MAS1_Aviso', p)), 'sin potencia no hay rebirth'
s.poner(p, 'Potencia', 600)
s.avanzar(0.1)
s.accion(p, 'rebirth')
assert s.attr(p, 'Rebirths') == 1 and s.attr(p, 'Potencia') == 0 and s.attr(p, 'CosteRebirth') == 1000
print('inventario: huevo %s, alas avanzadas puestas (impulso x%.1f), rebirth hecho' % (mascota, s.attr(p, 'Impulso')))

# ------------------------------------------------------------------ 6) trampas, morir en pleno vuelo y spam
s = R.Servidor()
p = s.jugador('Beto', 1002)
s.accion(p, 'lanzar')
volar(s, p, trampa=lambda t, pos: [pos[0], pos[1], pos[2] - 400] if abs(t - 3) < 0.009 else None)
assert (s.attr(p, 'Correcciones') or 0) >= 1, 'un teletransporte de 400 studs se corrige'
assert any('correccion' in a and 'Beto' in a for a in s.avisos()), 'cada correccion queda en el Output con el jugador'
res = s.eventos('MAS1_Resultado', p)[0][0]
assert res['distancia'] < 900, ('el teletransporte no cuenta para la distancia', res['distancia'])
s.avanzar(3.5)
s.H.mover(p, 0.0, 3.0, 14.0)
s.accion(p, 'lanzar')
n_res = len(s.eventos('MAS1_Resultado', p))
volar(s, p, tope=2.0)
s.H.salud(p, 0)                          # muere en pleno vuelo: el vuelo no paga
s.avanzar(0.5)
assert s.attr(p, 'EnVuelo') is False and len(s.eventos('MAS1_Resultado', p)) == n_res, 'morir en vuelo cancela sin resultado'
s.H.salud(p, 100)
s.avanzar(3.5)
antes = len(s.eventos('MAS1_Inventario', p))
for _ in range(100):                     # spam de mensajes en el mismo segundo
    s.accion(p, 'inventario')
despues = len(s.eventos('MAS1_Inventario', p))
assert despues - antes <= 30, ('mas de 30 mensajes por segundo no se atienden', despues - antes)
print('trampas y limites: teletransporte corregido, morir cancela, spam limitado a %d de 100' % (despues - antes))

# ------------------------------------------------------------------ 7) datos: irse cargando, otro servidor con el bloqueo, hora rota, DataStore caido
s = R.Servidor()
s.g.LATENCIA = 0.5                       # el DataStore tarda medio segundo en cada llamada
p = s.jugador('Cris', 1003, cargar=False)
s.H.sacar(p)                             # se va antes de que acaben de cargar sus datos
s.avanzar(3.0)
g = s.almacen('j_1003')
assert g is not None and g.bloqueo is None, 'si se va mientras cargan, el bloqueo se suelta (no queda 3 minutos cerrado)'
s.g.LATENCIA = 0

s.g.ALMACEN['j_1004'] = s.l.table_from({'dato': s.l.table_from({'dinero': 777}), 'bloqueo': s.l.table_from({'sesion': 'otro-servidor', 't': 1700000000})})
p = s.jugador('Dani', 1004, cargar=False)
s.avanzar(70.0)                          # espera a que lo suelte (8 intentos de 6 s) y, como sigue cerrado, lo echa
kicks = [k for k in s.g.KICKS.values()]
assert len(kicks) == 1 and 'otro servidor' in kicks[0].mensaje and s.attr(p, 'Dinero') != 777, 'con el bloqueo de otro servidor no se juega ni se pisa'
assert s.almacen('j_1004').dato.dinero == 777 and s.almacen('j_1004').bloqueo.sesion == 'otro-servidor', 'no se pisan sus datos'

s.g.ALMACEN['j_1005'] = s.l.table_from({'dato': s.l.table_from({'dinero': 555}), 'bloqueo': s.l.table_from({'sesion': 'otro-servidor', 't': 10 ** 12})})
p = s.jugador('Eva', 1005)               # bloqueo con la hora en el futuro (dato roto): no la deja fuera para siempre
s.avanzar(1.0)
assert s.attr(p, 'Dinero') == 555 and len(s.g.KICKS) == 1, 'un bloqueo con la hora rota no cierra la puerta'

s.g.FALLOS = 20                          # el DataStore falla mas de lo que se reintenta: no se juega con datos vacios
p = s.jugador('Fer', 1006, cargar=False)
s.avanzar(60.0)
assert len(s.g.KICKS) == 2 and 'No se pudieron cargar' in [k for k in s.g.KICKS.values()][1].mensaje, 'sin DataStore, fuera con un mensaje'
assert sum('intento' in a and 'fallido' in a for a in s.avisos()) >= 5, 'se reintenta 5 veces y cada fallo queda en el Output'
print('datos: irse cargando suelta el bloqueo, bloqueo ajeno respetado, hora rota ignorada, DataStore caido echa con mensaje')


# ------------------------------------------------------------------ 8) golpear a un enemigo y atrapar el cofre (el piloto va hacia ellos)
def anclas(s, nombre):
    """Las anclas de MAS1_Entidades con ese nombre: [(x, y, z, vivo, ancla)]."""
    lista = s.l.eval('''function(n)
        local r = {}
        for _, a in ipairs(workspace:FindFirstChild("MAS1_Entidades"):GetChildren()) do
            if a._d.Name == n then r[#r + 1] = a end
        end
        return r
    end''')(nombre)
    return [(a.Position.X, a.Position.Y, a.Position.Z, a.GetAttribute(a, 'Vivo'), a) for a in lista.values()]


def perseguir(s, p, objetivo, tope=40.0, boost=False, al_llegar=None, cerca=8.0):
    """Vuela hacia objetivo() = (x, y, z) o None, con el Manejo real; al_llegar() se llama una vez al pasar a menos de «cerca» studs."""
    Man = s.l.execute(open('src/Manejo.lua', encoding='utf-8').read())
    V = s.l.execute(open('src/Vuelo.lua', encoding='utf-8').read())
    T = s.l.table_from
    if boost:
        s.accion(p, 'boost', True)
    r = s.H.raiz(p).Position
    pos, m, t, dt, hecho = [r.X, r.Y, r.Z], Man.nuevo(), 0.0, 1 / 60, False
    while s.attr(p, 'EnVuelo') and t < tope:
        o = objetivo()
        ent = {}
        if o:
            ent = {'lateral': max(-1.0, min(1.0, (o[0] - pos[0]) / 4.0)), 'subir': o[1] - pos[1] > 1.5, 'bajar': o[1] - pos[1] < -1.5}
            d = ((o[0] - pos[0]) ** 2 + (o[1] - pos[1]) ** 2 + (o[2] - pos[2]) ** 2) ** 0.5
            if not hecho and d < cerca and al_llegar:
                al_llegar()
                hecho = True
        info = T({'planeando': bool(s.attr(p, 'Planeando')), 'boost': bool(s.attr(p, 'Boost')), 'impulso': s.attr(p, 'Impulso') or 1})
        Man.paso(m, dt, T(ent), info, pos[0], pos[1], V.CFG, pos[2])
        pos = [pos[0] + m.vx * dt, max(3.0, pos[1] + m.vy * dt), pos[2] - m.vf * dt]
        s.H.mover(p, *pos)
        s.H.latido(dt)
        q = s.H.raiz(p).Position
        pos = [q.X, q.Y, q.Z]
        t += dt
    return hecho


s = R.Servidor()
p = s.jugador('Gus', 1007)
s.accion(p, 'lanzar')
enemigo = min((a for a in anclas(s, 'Enemigo') if a[2] < -60), key=lambda a: -a[2])   # el primero por delante del cañon
objetivo = (enemigo[0], max(10.0, min(28.0, enemigo[1])), enemigo[2] + 3)
golpes0 = len(s.eventos('MAS1_Efecto'))
combo = []


def pegar():
    s.accion(p, 'puno')
    combo.append(s.attr(p, 'Combo'))     # el combo dura 1,5 s: se mira justo al golpear


llego = perseguir(s, p, lambda: objetivo, tope=12.0, al_llegar=pegar, cerca=7.0)
assert llego, ('no se llego al enemigo', objetivo)
assert any(e[0] == 'golpe' for e in s.eventos('MAS1_Efecto')[golpes0:]), 'el golpe a un enemigo manda su efecto'
assert enemigo[4].GetAttribute(enemigo[4], 'Vivo') is False, 'el enemigo golpeado desaparece'
assert combo == [1], ('los golpes suman al combo', combo)
assert s.attr(p, 'Combo') == 0, 'el combo se apaga solo a los 1,5 s'
volar(s, p)
res = s.eventos('MAS1_Resultado', p)[0][0]
assert res['golpes'] == 1, res['golpes']
s.avanzar(16.0)
assert enemigo[4].GetAttribute(enemigo[4], 'Vivo') is True, 'el enemigo vuelve a los 15 s'
print('enemigo: golpeado a %.0f studs, desaparece, suma al combo y vuelve a los 15 s' % -enemigo[2])

s.avanzar(3.5)
s.H.mover(p, 0.0, 3.0, 14.0)
s.accion(p, 'lanzar')
cofres0 = s.attr(p, 'Cofres') or 0
cofre = [a for a in anclas(s, 'Cofre') if a[4].GetAttribute(a[4], 'Dueno') == 1007]
assert len(cofre) == 1, 'al lanzarse sale el cofre del jugador'
def pos_cofre():
    c = [a for a in anclas(s, 'Cofre') if a[4].GetAttribute(a[4], 'Dueno') == 1007]
    return (c[0][0], c[0][1], c[0][2]) if c else None
perseguir(s, p, pos_cofre, tope=30.0, boost=True)
assert (s.attr(p, 'Cofres') or 0) == cofres0 + 1 or (s.attr(p, 'Cofres') or 0) == cofres0 + 2, ('no se atrapo el cofre con boost', s.attr(p, 'Cofres'))
volar(s, p)
assert not [a for a in anclas(s, 'Cofre') if a[4].GetAttribute(a[4], 'Dueno') == 1007], 'al aterrizar el cofre desaparece'
print('cofre: atrapado con boost (%d en total) y retirado al aterrizar' % s.attr(p, 'Cofres'))

# ------------------------------------------------------------------ 9) las alas se desbloquean solas (3.er lanzamiento, racha de 3 dias, 60 cofres) y no se puede lanzar dos veces
s = R.Servidor()
p = s.jugador('Hana', 1008)
for i in range(3):
    s.avanzar(3.5)
    s.H.mover(p, 0.0, 3.0, 14.0)
    s.accion(p, 'lanzar')
    if i == 0:
        s.accion(p, 'lanzar')                       # lanzar en pleno vuelo no hace nada
        assert s.attr(p, 'Lanzamientos') == 1, 'no se puede lanzar dos veces seguidas'
    assert s.attr(p, 'Alas') == ('' if i < 2 else 'iniciales'), ('las alas iniciales salen en el 3.er lanzamiento', i, s.attr(p, 'Alas'))
    volar(s, p)
assert any('Nuevas alas' in a[0] for a in s.eventos('MAS1_Aviso', p)), 'aviso de alas nuevas'
dia = 1700000000 // 86400
s.g.ALMACEN['j_1009'] = s.l.table_from({'dato': s.l.table_from({'diasSeguidos': 2, 'ultimoDia': dia - 1, 'cofres': 60})})
p = s.jugador('Ivan', 1009)
tiene = [a for a in s.eventos('MAS1_Inventario', p)[-1][0]['alas'].values()]
assert 'roboticas' in tiene and 'avanzadas' in tiene, ('racha de 3 dias y 60 cofres desbloquean robóticas y avanzadas', tiene)
assert s.almacen('j_1009') is not None and s.attr(p, 'DiasSeguidos') == 3
print('alas: iniciales en el 3.er lanzamiento, roboticas con 3 dias y avanzadas con 60 cofres')
print('ok')
