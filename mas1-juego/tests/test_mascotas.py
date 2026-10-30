import lupa, random
l=lupa.LuaRuntime()
M=l.execute(open('src/Mascotas.lua').read())
ids=[p.id for p in M.LISTA.values()]
assert len(ids)==11 and len(set(ids))==11
cnt={}
for p in M.LISTA.values():
    n=M.cantidadBonus(p); cnt.setdefault(p.rareza,set()).add(n)
print(cnt)
# fenix no sale de huevos y las suma de porcentajes tienen mascotas candidatas
for r,t in M.HUEVOS.items():
    for rz in t.keys():
        assert any(p.rareza==rz for p in M.LISTA.values()),(r,rz)
rng=random.Random(1).random
vistos={}
for _ in range(20000):
    for hr in ['comun','poco_comun','raro','epico','legendario','mitico']:
        p=M.abrirHuevo(hr,rng); assert p.id!='fenix'; vistos[p.id]=1
assert len(vistos)==10
m=M.multiplicadores(l.table_from(['grifo','gorrion']))
assert abs(m.dinero-1.8)<1e-9 and abs(m.impulso-1.7)<1e-9
print('ok')
