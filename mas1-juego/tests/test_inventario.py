# Pruebas de src/Inventario.lua con lupa: huevos que se pagan, equipar hasta 3 (repetidas solo si tienes varias), mascota principal,
# alas compradas y equipadas, y que el fenix solo llega con Robux. Ejecutar desde mas1-juego: python tests/test_inventario.py
import random
import lupa

l = lupa.LuaRuntime()
M = l.execute(open('src/Mascotas.lua', encoding='utf-8').read())
A = l.execute(open('src/Alas.lua', encoding='utf-8').read())
I = l.execute(open('src/Inventario.lua', encoding='utf-8').read())

# precios: cada huevo de la tabla HUEVOS tiene precio y suben con la rareza
precios = [M.PRECIO_HUEVO[r] for r in ('comun', 'poco_comun', 'raro', 'epico', 'legendario', 'mitico')]
assert all(precios) and precios == sorted(precios) and set(M.HUEVOS.keys()) == set(M.PRECIO_HUEVO.keys())

inv = I.nuevo()
rng = random.Random(5).random
r = I.abrirHuevo(M, inv, 100, 'comun', rng)
assert r[0] is False and 'cuesta' in r[1]                       # sin dinero no se abre
ok, queda, p, nueva = I.abrirHuevo(M, inv, 10000, 'comun', rng)
assert ok and queda == 10000 - M.PRECIO_HUEVO.comun and nueva and inv.mascotas[p.id] == 1
ok, queda, p2, nueva2 = I.abrirHuevo(M, inv, queda, 'comun', rng)
assert ok and (nueva2 == (p2.id != p.id))
assert I.abrirHuevo(M, inv, 10 ** 9, 'robux', rng)[0] is False    # no hay huevo del fenix
vistos = set()
for _ in range(3000):
    vistos.add(I.abrirHuevo(M, I.nuevo(), 10 ** 9, 'mitico', rng)[2].id)
assert 'fenix' not in vistos

# equipar: hasta 3, repetidas solo si tienes varias, desequipar
inv = I.nuevo()
inv.mascotas.gorrion, inv.mascotas.grifo, inv.mascotas.nube = 2, 1, 1
assert I.equipar(M, inv, 'grifo') and I.equipar(M, inv, 'gorrion') and I.equipar(M, inv, 'gorrion')
r = I.equipar(M, inv, 'nube')
assert r[0] is False and 'Ya llevas 3' in r[1]
assert I.desequipar(inv, 'gorrion') and I.equipar(M, inv, 'nube')
r = I.equipar(M, I.nuevo(), 'grifo')
assert r[0] is False                                               # no la tienes
inv2 = I.nuevo(); inv2.mascotas.grifo = 1
assert I.equipar(M, inv2, 'grifo') and I.equipar(M, inv2, 'grifo')[0] is False   # solo tienes una
assert I.principal(M, inv).id == 'grifo' and I.principal(M, I.nuevo()) is None
b = M.multiplicadores(inv.equipadas)
assert abs(b.impulso - (1 + 0.7)) < 1e-9 and abs(b.dinero - (1 + 0.7 + 0.1)) < 1e-9

# fenix solo con Robux
I.darFenix(inv)
assert inv.mascotas.fenix == 1

# alas: las de requisito no se compran, las avanzadas si; equipar solo las tuyas
r = I.comprarAla(A, inv, 10 ** 6, 'iniciales')
assert r[0] is False and 'no se compran' in r[1]
r = I.comprarAla(A, inv, 100, 'avanzadas')
assert r[0] is False and 'cuestan' in r[1]
ok, queda = I.comprarAla(A, inv, 30000, 'avanzadas')
assert ok and queda == 5000 and I.tieneAla(inv, 'avanzadas') and I.comprarAla(A, inv, 10 ** 6, 'avanzadas')[0] is False
assert I.equiparAla(inv, 'roboticas')[0] is False and I.equiparAla(inv, 'avanzadas') and inv.alaEquipada == 'avanzadas'
assert I.darAla(inv, 'iniciales') and not I.darAla(inv, 'iniciales')

# copia para la interfaz: misma forma acordada y sin compartir tablas
c = I.copia(inv)
assert c.alaEquipada == 'avanzadas' and c.mascotas.grifo == 1 and len(list(c.equipadas.values())) == 3
c.mascotas.grifo = 99
assert inv.mascotas.grifo == 1
print('ok')
