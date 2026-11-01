# Las zonas largas (31/10) estan en tres sitios que tienen que coincidir: src/Vuelo.lua (multiplicador, final del mapa),
# src/Encuentros.lua (enemigos y orbes por zona) y el mapa en piezas (mas1-arte/mapa-v01/roblox/datos.json, de build_mapa.py).
# Ademas, la progresion: el primer vuelo se queda en la Pradera y cada zona pide mas potencia. Ejecutar desde mas1-juego.
import json
import math
import lupa

l = lupa.LuaRuntime()
V = l.execute(open('src/Vuelo.lua', encoding='utf-8').read())
E = l.execute(open('src/Encuentros.lua', encoding='utf-8').read())
VC, EC = V.CFG, E.CFG
mapa = json.load(open('../mas1-arte/mapa-v01/roblox/datos.json', encoding='utf-8'))['zonas_z_roblox']
orden = ['pradera', 'mar-de-nubes', 'tormenta', 'cielo-alto', 'espacio']
limites = [(-mapa[k][0], -mapa[k][1]) for k in orden]                 # (desde, hasta) en studs hacia -Z
zonas = [(z[1], z[2]) for z in VC.zonas.values()]                     # (desde, multiplicador)
# el multiplicador x3..x6 empieza donde empieza la zona del mapa; x2 desde el prado del lobby
assert [d for d, m in zonas if m >= 3] == [d for d, _ in limites[1:]], (zonas, limites)
assert limites[0][0] == 172 and limites[-1][1] == 8812 and VC.finMapa < limites[-1][1]
# los enemigos y orbes de Encuentros, zona a zona igual que el mapa (la Pradera empieza en el prado: 40)
ez = [(z.desde, z.hasta) for z in EC.zonas.values()]
assert ez[1:] == limites[1:] and ez[0][1] == limites[0][1], (ez, limites)
# progresion: distancia aproximada del vuelo = lanzamiento + energia a velocidad base + planeo
def distancia(potencia):
    return 102 + VC.velocidadBase * V.energiaMax(potencia) + 100
def zona(potencia):
    return V.multiplicadorZona(38 + distancia(potencia))      # el cañon esta a 38 studs del origen
assert zona(0) == 2                                                   # el primer vuelo se queda en la Pradera
for potencia, minimo in ((100, 3), (700, 4), (2400, 5), (7000, 6)):
    assert zona(potencia) >= minimo, (potencia, zona(potencia))
for potencia, maximo in ((50, 2), (500, 3), (2000, 4), (6000, 5)):
    assert zona(potencia) <= maximo, (potencia, zona(potencia))
print('zonas: %s; potencia 0 -> x%d (%.0f studs)' % (limites, zona(0), distancia(0)))
print('ok')
