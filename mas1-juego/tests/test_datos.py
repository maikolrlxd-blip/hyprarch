# Pruebas de src/Datos.lua con lupa: limpieza de datos cargados, bloqueo de sesion (sin pisar datos de otro servidor salvo que su
# bloqueo caduque) y racha de dias. Ejecutar desde mas1-juego: python tests/test_datos.py
import lupa

l = lupa.LuaRuntime()
D = l.execute(open('src/Datos.lua', encoding='utf-8').read())
M = l.execute(open('src/Mascotas.lua', encoding='utf-8').read())
A = l.execute(open('src/Alas.lua', encoding='utf-8').read())
T = l.table_from
nan = float('nan')

# limpiar: tipos raros, negativos, NaN, mascotas que no existen, equipadas de mas o que no tienes, alas que no existen
sucio = T({'potencia': -5, 'dinero': 'mucho', 'exp': nan, 'rebirths': 2.7, 'cofres': 4, 'lanzamientos': float('inf'),
           'ultimoDia': 19000, 'inventario': T({
               'mascotas': T({'grifo': 1, 'gorrion': 2, 'dragon': 5, 'nube': 0}),
               'equipadas': T(['grifo', 'grifo', 'gorrion', 'gorrion', 'gorrion', 'nube']),
               'alas': T(['avanzadas', 'avanzadas', 'turbo']), 'alaEquipada': 'turbo'})})
n = D.limpiar(sucio, M, A)
assert n.potencia == 0 and n.dinero == 0 and n.exp == 0 and n.rebirths == 2 and n.cofres == 4 and n.lanzamientos == 0
assert n.ultimoDia == 19000 and n.version == D.VERSION
inv = n.inventario
assert dict(inv.mascotas) == {'grifo': 1, 'gorrion': 2}
assert list(inv.equipadas.values()) == ['grifo', 'gorrion', 'gorrion']
assert list(inv.alas.values()) == ['avanzadas'] and inv.alaEquipada is None
assert D.limpiar(None, M, A).dinero == 0 and D.limpiar('x', M, A).potencia == 0
bueno = D.limpiar(T({'dinero': 1234, 'inventario': T({'alas': T(['iniciales']), 'alaEquipada': 'iniciales'})}), M, A)
assert bueno.dinero == 1234 and bueno.inventario.alaEquipada == 'iniciales'

# bloqueo de sesion
ok, g = D.tomar(None, 'A', 1000, 180)                     # jugador nuevo
assert ok and g.bloqueo.sesion == 'A' and g.dato.dinero == 0
g.dato.dinero = 50
assert D.tomar(g, 'B', 1100, 180) is False                # otro servidor no lo pisa mientras A lo tiene
ok, g2 = D.tomar(g, 'B', 1200, 180)                       # el de A caduco (A se cayo): B lo toma y conserva los datos
assert ok and g2.bloqueo.sesion == 'B' and g2.dato.dinero == 50
assert D.escribir(g2, 'A', T({'dinero': 1}), 1201, False) is False   # A ya no puede escribir
ok, g3 = D.escribir(g2, 'B', T({'dinero': 99}), 1202, True)          # B guarda y suelta al salir
assert ok and g3.dato.dinero == 99 and g3.bloqueo is None
ok, g4 = D.tomar(g3, 'C', 1203, 180)                       # suelto: otro servidor lo toma al momento
assert ok and g4.bloqueo.sesion == 'C'

# racha de dias seguidos
d = D.nuevo()
assert D.registrarDia(d, 100) and d.diasSeguidos == 1
assert not D.registrarDia(d, 100) and d.diasSeguidos == 1
assert D.registrarDia(d, 101) and D.registrarDia(d, 102) and d.diasSeguidos == 3
assert D.registrarDia(d, 105) and d.diasSeguidos == 1      # se rompe la racha
print('ok')
