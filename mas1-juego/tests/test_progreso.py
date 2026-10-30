# Pruebas del entrenamiento, el rebirth y las alas (src/Vuelo.lua y src/Alas.lua) con lupa. Ejecutar desde mas1-juego:
# python tests/test_progreso.py
import lupa

l = lupa.LuaRuntime()
V = l.execute(open('src/Vuelo.lua', encoding='utf-8').read())
A = l.execute(open('src/Alas.lua', encoding='utf-8').read())
M = l.execute(open('src/Mascotas.lua', encoding='utf-8').read())
T = l.table_from
C = V.CFG

# entrenamiento: +1/s en tierra, x1,5 en AFK, x2 en el circuito solo corriendo, +50% por rebirth
assert V.ritmoEntreno(0, None, False) == 1
assert V.ritmoEntreno(0, 'afk', False) == 1.5
assert V.ritmoEntreno(0, 'entreno', False) == 1 and V.ritmoEntreno(0, 'entreno', True) == 2
assert V.ritmoEntreno(2, 'entreno', True) == 4
assert V.entrenar(0, 10, 2) == 20

# rebirth: 500, 1000, 2000...; solo reinicia la potencia
assert [V.costeRebirth(r) for r in range(4)] == [500, 1000, 2000, 4000]
j = T({'potencia': 600, 'rebirths': 0, 'puntos': 999, 'alas': 'iniciales', 'mascotas': 'm', 'desbloqueos': 'd'})
n = V.rebirth(j)
assert n.potencia == 0 and n.rebirths == 1 and n.puntos == 999 and n.alas == 'iniciales'

# alas: mas que las mascotas, escalan con los rebirths, y se multiplican con las mascotas
for a in A.LISTA.values():
    assert a.id and a.nombre and a.requisito and a.precio is not None
b0, b2 = A.bonus('roboticas', 0), A.bonus('roboticas', 2)
assert abs(b0.resistencia - 2.0) < 1e-9 and abs(b2.resistencia - 2.5) < 1e-9 and b2.impulso > b0.impulso
assert A.bonus('nada', 3).impulso == 1
mas_fuerte_mascota = max(max(p.bonus.values()) for p in M.LISTA.values() if p.rareza != 'robux')
assert A.get('iniciales').resistencia >= 50 > 0 and A.get('avanzadas').resistencia > mas_fuerte_mascota
assert A.desbloqueada('iniciales', T({'lanzamientos': 3})) and not A.desbloqueada('iniciales', T({'lanzamientos': 2}))
assert A.desbloqueada('avanzadas', T({'cofres': 10})) and not A.desbloqueada('roboticas', T({}))
tot = A.combinar(M.multiplicadores(T(['nube'])), A.bonus('iniciales', 0))
assert abs(tot.resistencia - 1.2 * 1.5) < 1e-9 and abs(tot.impulso - 1.2) < 1e-9 and tot.dinero == 1

# las alas se notan en el vuelo: mas energia (resistencia)
assert V.nuevo(0, tot).energiaMax > V.nuevo(0, None).energiaMax * 1.7
print('ok')
