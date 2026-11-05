import lupa, random
l=lupa.LuaRuntime()
M=l.execute(open('src/Misiones.lua').read())
rng=random.Random(3).random
e=M.nuevo(rng)
assert len(e.activas)==3
ids=[a.id for a in e.activas.values()]; assert len(set(ids))==3
# un vuelo enorme completa varias y repone con otras distintas
v=l.table_from({'distancia':20000,'aros':60,'golpes':50,'cofres':12,'orbes':200})
prem,hechas=M.registrar(e,v,rng)
assert prem>0 and len(e.activas)==3
ids=[a.id for a in e.activas.values()]; assert len(set(ids))==3
# lo acumulado antes de que salga una mision no cuenta
for a in e.activas.values(): assert a.base>=0
prem2,_=M.registrar(e,l.table_from({'distancia':10}),rng); assert prem2==0
s=M.codificar(e); assert s.count(';')==2, s

# el cliente lee el atributo con un patron de enteros: con la distancia acumulada con decimales, la fila de «Vuela metros» no encajaba
# y la mision desaparecia del panel. Se lee el patron del propio cliente para que no se desincronice.
import re
cliente = open('client/Misiones.client.lua', encoding='utf-8').read()
m = re.search(r'string\.gmatch\(s, "([^"]+)"\)', cliente)
assert m and m.group(1) == '([^|;]+)|(%d+)|(%d+)|(%d+)', 'el cliente cambio su patron: actualiza esta prueba'
patron = re.compile(r'([^|;]+)\|(\d+)\|(\d+)\|(\d+)')
e = M.nuevo(random.Random(5).random)
for i, id_ in enumerate(('distancia', 'aros', 'golpes'), start=1):
    e.activas[i].id = id_
    e.activas[i].base = 0
M.registrar(e, l.table_from({'distancia': 1234.5678, 'aros': 3, 'golpes': 1}), random.Random(5).random)
s = M.codificar(e)
filas = patron.findall(s)
assert len(filas) == 3, ('una fila no encaja con el patron del cliente', s)
assert filas[0] == ('Vuela metros', '1234', '2000', '400'), filas[0]
for v in M.ver(e).values():
    assert v.progreso == int(v.progreso) and 0 <= v.progreso <= v.meta
print('ok', s)
