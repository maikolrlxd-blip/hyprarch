import lupa
l=lupa.LuaRuntime()
V=l.execute(open('src/Vuelo.lua').read())
M=l.execute(open('src/Mascotas.lua').read())
# energia crece con potencia
assert V.energiaMax(100)>V.energiaMax(0)
# vuelo normal consume y termina planeando
v=V.nuevo(0)
t=0
while not v.planeando and t<1000:
    V.paso(v,0.1,None); t+=0.1
assert v.planeando and abs(t-12)<0.3, t
# boost gasta mas y va mas rapido
a=V.nuevo(100); b=V.nuevo(100)
va=V.paso(a,1,None); vb=V.paso(b,1,l.table_from({'boost':True}))
assert vb>va and b.energia<a.energia
# planeando: boost y ataque no funcionan
v=V.nuevo(0); v.energia=0; V.paso(v,0.1,l.table_from({'boost':True}))
assert v.planeando and not V.atacar(v)
# ataque consume
v=V.nuevo(100); e=v.energia; assert V.atacar(v) and v.energia==e-3
# multiplicador de zona
assert V.multiplicadorZona(0)==1 and V.multiplicadorZona(600)==4 and V.multiplicadorZona(5000)==6
# aterrizaje con bonus de mascota
m=M.multiplicadores(l.table_from(['grifo']))
v=V.nuevo(50,m)
for _ in range(50): V.paso(v,0.1,None)
V.cruzarAro(v); V.golpearEnemigo(v)
r=V.aterrizar(v); assert r.dinero>0 and r.aros==1
assert V.paso(v,1,None)==0
# entrenar y rebirth
assert V.entrenar(0,10,0)==10 and V.entrenar(0,10,2)==20
j=l.table_from({'potencia':500,'rebirths':0,'puntos':1234,'alas':'robotica','mascotas':'x','desbloqueos':'y'})
n=V.rebirth(j); assert n.potencia==0 and n.rebirths==1 and n.puntos==1234 and n.alas=='robotica'
print('ok')
