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
print('ok', s)
