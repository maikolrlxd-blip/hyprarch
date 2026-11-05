# Ejecuta los scripts del cliente que se escribieron sin poder verlos en Studio (client/Seguidores, AnimaSeguidores, Entidades, Orbes y
# Canon) en un cliente de mentira (tests/roblox_falso.py) con el codigo real de src/ y los modelos reales de assets/*.rbxmx (huesos y
# uniones Motor6D incluidos). Pilla errores de ejecucion y comprueba lo que se puede medir sin motor grafico: las mascotas y las alas
# se crean, las alas van medio metidas en la espalda y abiertas en tierra, el aleteo recoge y extiende (la V), los enemigos aparecen,
# desaparecen y vuelven, los orbes se esconden al cogerlos y el cañon retrocede hacia atras y vuelve a su sitio. NO prueba lo que
# depende del motor (como se ve, la interfaz). Ejecutar desde mas1-juego: python tests/test_cliente.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roblox_falso as R


def hijos(cl, nodo):
    return [h.Name for h in cl.lista(nodo)]


# ------------------------------------------------------------------ 1) mascotas y alas: Seguidores + AnimaSeguidores
cl = R.Cliente()
plr, ws = cl.jugador, cl.g.workspace
cl.ejecutar('client/Seguidores.client.lua')
cl.ejecutar('client/AnimaSeguidores.client.lua')
cl.H.poner(plr, 'MascotasEq', 'aguila,nube,gorrion')
cl.H.poner(plr, 'Alas', 'avanzadas')
cl.cuadros(1.0)
nombres = hijos(cl, ws)
assert nombres.count('Mas1Alas') == 1 and sorted(n for n in nombres if n.startswith('Mas1Mascota_')) == \
    ['Mas1Mascota_aguila', 'Mas1Mascota_gorrion', 'Mas1Mascota_nube'], nombres
alas, torso = cl.hijo(ws, 'Mas1Alas'), cl.hijo(plr.Character, 'UpperTorso')
pv = alas.GetPivot(alas).Position
rel = (pv.X - torso.Position.X, pv.Y - torso.Position.Y, pv.Z - torso.Position.Z)
assert abs(rel[0]) < 0.01 and 0.3 < rel[1] < 0.5 and 0.0 < rel[2] < 0.5, ('el soporte de las alas va medio metido en la espalda (media profundidad del torso = 0,5)', rel)
for n in ('aguila', 'nube', 'gorrion'):   # ninguna mascota pasa de 5 studs y andan cerca del jugador, sobre el suelo
    m = cl.hijo(ws, 'Mas1Mascota_' + n)
    plantilla = cl.hijo(cl.hijo(cl.rs, 'MAS1_Modelos'), n)
    e = plantilla.GetExtentsSize(plantilla)   # el tamaño real: la caja de una mascota girada es mayor que ella
    assert max(e.X, e.Y, e.Z) * m.GetScale(m) <= 5.01, (n, max(e.X, e.Y, e.Z), m.GetScale(m))
    q = m.GetPivot(m).Position
    assert ((q.X - 0) ** 2 + (q.Z - 14) ** 2) ** 0.5 < 14 and q.Y > 0, (n, q.X, q.Y, q.Z)

punta = cl.l.eval('function(m, n) local b = m:FindFirstChild(n, true) return (m:GetPivot():Inverse() * H.hueso_mundo(b)).Position end')


def muestrea(segundos):
    """Posicion de las puntas de las alas (en el espacio de las alas) en cada fotograma: ([Tip_R], [Tip_L])."""
    r, l, t = [], [], 0.0
    while t < segundos:
        cl.cuadros(1 / 60)
        r.append(punta(alas, 'Tip_R'))
        l.append(punta(alas, 'Tip_L'))
        t += 1 / 60
    return r, l


r, l = muestrea(3.0)                       # en tierra: Glide despacio, alas abiertas y no pegadas al cuerpo
assert all(abs(p.X) > 1.5 for p in r + l), ('en tierra las alas estan abiertas', min(abs(p.X) for p in r + l))
assert all(a.X > 0 for a in r) and all(a.X < 0 for a in l), 'cada punta en su lado'
cl.H.poner(plr, 'EnVuelo', True)           # en vuelo: Flap, recoger -> extender -> impulsar
r, l = muestrea(1.8)
xs, ys = [abs(p.X) for p in r], [p.Y for p in r]
assert max(xs) > 2.0 and min(xs) < 1.0, ('el aleteo se recoge y se extiende hacia los lados', min(xs), max(xs))
assert max(ys) - min(ys) > 0.6, ('el aleteo sube y baja', min(ys), max(ys))
assert all(a.X > -0.2 for a in r) and all(a.X < 0.2 for a in l), 'las puntas no se cruzan al otro lado del cuerpo'
assert all(abs(a.X + b.X) < 0.05 for a, b in zip(r, l)), 'el aleteo es simetrico'
cl.H.poner(plr, 'Planeando', True)         # planeando: Glide, abiertas
r, l = muestrea(2.0)
assert all(abs(p.X) > 1.5 for p in r + l), 'al planear las alas estan abiertas'
# las mascotas aletean (Fly): un hueso de la aguila se mueve
cuerpo = cl.hijo(cl.hijo(ws, 'Mas1Mascota_aguila'), 'Body')
a = cl.l.eval('function(b) return b.Transform.Position end')(cuerpo)
cl.cuadros(0.4)
b = cl.l.eval('function(b) return b.Transform.Position end')(cuerpo)
assert abs(a.Y - b.Y) > 1e-4 or abs(a.Z - b.Z) > 1e-4, 'el cuerpo de la mascota se mueve con su clip Fly'
cl.H.poner(plr, 'Alas', '')                # sin alas: se retiran
cl.cuadros(0.1)
assert 'Mas1Alas' not in hijos(cl, ws), 'quitar las alas las retira'
cl.H.poner(plr, 'MascotasEq', '')
cl.cuadros(0.1)
assert not [n for n in hijos(cl, ws) if n.startswith('Mas1Mascota_')], 'quitar las mascotas las retira'
print('seguidores: 3 mascotas y alas avanzadas; en tierra |x| de las puntas %.2f..%.2f; aleteo de %.2f a %.2f studs de lado' % (1.5, 2.2, min(xs), max(xs)))

# ------------------------------------------------------------------ 2) enemigos y cofre: Entidades (piezas de repuesto, sin MAS1_Enemigos)
cl = R.Cliente()
plr, ws = cl.jugador, cl.g.workspace
for i, tipo in enumerate(('globo', 'nube', 'nubarron', 'cometa', 'ovni', 'meteorito', 'cofre', 'cofre')):
    a = cl.H.nodo('Part', 'Enemigo' if tipo != 'cofre' else 'Cofre', cl.entidades)
    a.Position = cl.l.eval('Vector3.new')(i * 12 - 40, 20.0, -150.0)
    cl.H.poner(a, 'Tipo', tipo)
    cl.H.poner(a, 'Vivo', True)
    if tipo == 'cofre':
        cl.H.poner(a, 'Dueno', 7 if i == 6 else 99)    # solo se dibuja el cofre de este jugador (id 7)
    if i == 1:
        nube = a
cl.ejecutar('client/Entidades.client.lua')
cl.cuadros(0.5)
vista = cl.hijo(ws, 'MAS1_EntidadesVista')
modelos = cl.lista(vista)
assert sorted(m.Name for m in modelos) == sorted(['globo', 'nube', 'nubarron', 'cometa', 'ovni', 'meteorito', 'cofre']), \
    ('6 enemigos y solo el cofre propio', [m.Name for m in modelos])
modelo_nube = next(m for m in modelos if m.Name == 'nube')
assert abs(modelo_nube.GetScale(modelo_nube) - 1.0) < 0.05
cl.H.poner(nube, 'Vivo', False)            # golpeado: encoge hasta desaparecer
cl.cuadros(1.0)
assert modelo_nube.GetScale(modelo_nube) < 0.2, ('un enemigo golpeado encoge', modelo_nube.GetScale(modelo_nube))
cl.H.poner(nube, 'Vivo', True)             # reaparece
cl.cuadros(1.0)
assert modelo_nube.GetScale(modelo_nube) > 0.9, 'el enemigo reaparece'
nube.Parent = None                         # el ancla se retira: su modelo tambien
cl.cuadros(0.1)
assert 'nube' not in [m.Name for m in cl.lista(vista)]
print('entidades: 6 enemigos y 1 cofre (el ajeno no), golpeado encoge y reaparece, ancla retirada quita su modelo')

# ------------------------------------------------------------------ 3) orbes: se crean todos y se esconden al cogerlos
cl = R.Cliente()
plr, ws = cl.jugador, cl.g.workspace
cl.ejecutar('client/Orbes.client.lua')
carpeta = cl.hijo(ws, 'MAS1_Orbes')
orbes = cl.lista(carpeta)
assert len(orbes) == 343, len(orbes)
cl.cuadros(0.3)
tamanos0 = [o.Size.X for o in orbes[:7]]
assert all(1.2 < t < 2.4 for t in tamanos0), tamanos0
cl.l.eval('function(rs, l) rs:FindFirstChild("MAS1_Orbe")._d.OnClientEvent:Fire(l) end')(cl.rs, cl.l.table_from([1, 2, 3]))
cl.cuadros(1.0)
assert all(o.Size.X < 0.3 and o.Transparency == 1 for o in orbes[:3]), 'los orbes cogidos se esconden'
assert all(o.Size.X > 1.2 and o.Transparency == 0 for o in orbes[3:7]), 'los demas siguen'
cl.H.poner(plr, 'EnVuelo', True)           # cada lanzamiento vuelven todos
cl.cuadros(1.0)
assert all(o.Size.X > 1.2 for o in orbes[:3]), 'al lanzarse vuelven los orbes'
print('orbes: 343 creados, 3 cogidos se esconden y vuelven en el siguiente lanzamiento')

# ------------------------------------------------------------------ 4) el cañon de Codex retrocede hacia atras y vuelve a su sitio
cl = R.Cliente()
plr, ws = cl.jugador, cl.g.workspace
cl.ejecutar('server/Lobby.server.lua')     # construye el lobby con el cañon (clon del modelo real, a escala x3)
canon = cl.hijo(ws, 'CanonPajarero')
assert canon is not None, 'el lobby pone el cañon de Codex'
boca = cl.hijo(canon, 'Wide_sky_muzzle')
palanca = cl.hijo(canon, 'Lever_grip')
base = cl.hijo(canon, 'Front_crossbeam')
reposo = {n: (p.Position.X, p.Position.Y, p.Position.Z) for n, p in (('boca', boca), ('palanca', palanca), ('base', base))}
cl.ejecutar('client/Canon.client.lua')
cl.cuadros(0.2)
assert abs(boca.Position.Z - reposo['boca'][2]) < 1e-6, 'sin disparo el cañon no se mueve'
cl.l.eval('function(rs, v) rs:FindFirstChild("MAS1_Efecto")._d.OnClientEvent:Fire("lanzamiento", v) end')(cl.rs, cl.l.eval('Vector3.new')(0.0, 4.0, -38.0))
zs, ys = [], []
for _ in range(90):                        # 1,5 s: el clip dura 1,2
    cl.cuadros(1 / 60)
    zs.append(boca.Position.Z - reposo['boca'][2])
    ys.append(boca.Position.Y - reposo['boca'][1])
    assert abs(base.Position.X - reposo['base'][0]) < 1e-6 and abs(base.Position.Z - reposo['base'][2]) < 1e-6, 'la base no se mueve'
assert max(zs) > 0.3 and min(zs) > -0.6, ('la boca retrocede hacia atras (+Z: el cañon apunta a -Z)', min(zs), max(zs))
assert max(abs(y) for y in ys) < 1.5, ('el retroceso no manda el cañon por los aires', min(ys), max(ys))
assert abs(boca.Position.Z - reposo['boca'][2]) < 1e-5 and abs(boca.Position.Y - reposo['boca'][1]) < 1e-5, 'al acabar el cañon vuelve a su sitio'
motores = [d for d in cl.l.eval('function(n) return n:GetDescendants() end')(canon).values() if d.ClassName == 'Motor6D']
assert len(motores) == 28 and all(m.Enabled for m in motores), 'las uniones se vuelven a encender'
assert abs(palanca.Position.X - reposo['palanca'][0]) < 1e-5, 'la palanca tambien vuelve'
print('cañon: la boca retrocede %.2f studs hacia atras (y %.2f..%.2f) y vuelve exacta; 28 uniones encendidas' % (max(zs), min(ys), max(ys)))
print('ok')
