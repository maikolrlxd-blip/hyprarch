# Pruebas de src/Efectos.lua con lupa: cada efecto del orden fijo tiene sus datos completos (o count, una rafaga, o rate, continuo) y
# todos los nombres de efecto que dispara el servidor (efecto:FireClient / FireAllClients) existen: client/Efectos.client.lua ignora en
# silencio un nombre que no conoce, asi que una errata no daria error, solo un efecto que no sale. Ejecutar desde mas1-juego:
# python tests/test_efectos.py
import glob
import re
import lupa

l = lupa.LuaRuntime()
E = l.execute(open('src/Efectos.lua', encoding='utf-8').read())
orden = list(E.ORDEN.values())
assert len(orden) == len(set(orden)), 'nombres repetidos en ORDEN'
for n in orden:
    t = E.TIPOS[n]
    assert t is not None, ('en ORDEN pero sin datos', n)
    assert (t.count is not None) != (t.rate is not None), (n, 'o count (rafaga) o rate (continuo), no los dos ni ninguno')
    for k in ('life', 'speed', 'size', 'accel', 'colors', 'spread', 'light'):
        assert t[k] is not None, (n, 'falta', k)
    assert t.life[1] <= t.life[2] and t.speed[1] <= t.speed[2], (n, 'rango al reves')
    assert all(re.fullmatch(r'#[0-9a-fA-F]{6}', c) for c in t.colors.values()), (n, 'color mal escrito')
    assert 0 <= t.light <= 1 and 0 <= t.spread <= 180, (n, t.light, t.spread)
assert set(E.TIPOS.keys()) == set(orden), ('hay efectos sin listar en ORDEN o al reves', set(E.TIPOS.keys()) ^ set(orden))

# los efectos que dispara el servidor
usados = {}
for ruta in glob.glob('server/*.lua'):
    texto = open(ruta, encoding='utf-8').read()
    for m in re.finditer(r'(?i)efecto:Fire(?:All)?Clients?\((?:\s*\w+\s*,)?\s*"(\w+)"', texto):
        usados.setdefault(m.group(1), set()).add(ruta)
assert usados, 'no se encontro ningun efecto disparado: ha cambiado la forma de llamarlos'
for nombre, rutas in usados.items():
    assert nombre in orden, ('el servidor dispara un efecto que no existe', nombre, sorted(rutas))
for nombre in ('lanzamiento', 'aro', 'golpe', 'rebirth', 'estela', 'orbe', 'aterrizaje'):
    assert nombre in usados, ('el juego ya no dispara', nombre)
print('ok (%d efectos; el servidor dispara %s)' % (len(orden), ', '.join(sorted(usados))))
