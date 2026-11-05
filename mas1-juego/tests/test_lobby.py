# Ejecuta server/Lobby.server.lua entero con el Roblox de mentira (tests/roblox_falso.py) y mira lo que construye: que no falle al
# arrancar (ni con el cañon de Codex ni con el de piezas de repuesto), que esten las piezas que lee el resto del juego (MAS1_Canon,
# MAS1_AFK, MAS1_Entreno, el punto de aparicion, el aviso del cañon), que la decoracion (farolas, banderines, arboles) quede sobre
# el suelo de la plaza y no pise el cañon, la plataforma, las zonas de entreno, los puestos, el arco ni el camino central, y que el
# cañon de Codex, con su tamaño y posicion reales (leidos de assets/MAS1_Equipo.rbxmx), no choque con nada. No comprueba nombres de
# propiedades de Roblox ni fisica: eso es de Studio. Ejecutar desde mas1-juego: python tests/test_lobby.py
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roblox_falso as R

FUENTE = open(os.environ.get('LOBBY', 'server/Lobby.server.lua'), encoding='utf-8').read()
FUENTE = re.sub(r'([\w\.\[\]"]+)\s*([+\-*/])=\s*', r'\1 = \1 \2 ', FUENTE)   # Luau: x += y
FUENTE = re.sub(r'\bcontinue\b', 'do end', FUENTE)


def plantilla_canon(l):
    """ReplicatedStorage.MAS1_Equipo.Canon con las piezas reales del .rbxmx (tamaño y CFrame)."""
    def prop(it, n):
        return next((c for c in it.find('Properties') if c.get('name').lower() == n.lower()), None)
    nodo = l.eval('function(clase, nombre, padre) local o = Instance.new(clase) o.Name = nombre o.Parent = padre return o end')
    pieza = l.eval('''function(clase, nombre, padre, x, y, z, a, b, c, d, e, f, g, h, i, sx, sy, sz)
        local o = Instance.new(clase) o.Name = nombre
        o.CFrame = CFrame.new(x, y, z, a, b, c, d, e, f, g, h, i) o.Size = Vector3.new(sx, sy, sz)
        o.Parent = padre return o end''')
    rs = l.eval('game:GetService("ReplicatedStorage")')
    carpeta = nodo('Folder', 'MAS1_Equipo', rs)
    modelo = nodo('Model', 'Canon', carpeta)
    raiz = ET.parse('assets/MAS1_Equipo.rbxmx').getroot()
    canon = next(m for m in raiz.iter('Item') if m.get('class') == 'Model')
    n = 0
    for it in canon.iter('Item'):
        if it.get('class') in ('MeshPart', 'Part'):
            c, s = prop(it, 'CFrame'), prop(it, 'size')
            v = [float(c.find(k).text) for k in ('X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22')]
            t = [float(s.find(k).text) for k in 'XYZ']
            pieza(it.get('class'), prop(it, 'Name').text, modelo, *v, *t)
            n += 1
    assert n >= 25, n
    return n


def correr(con_canon):
    l = R.nuevo()
    if con_canon:
        plantilla_canon(l)
    try:
        l.execute(FUENTE)
    except Exception as e:   # un error de Lua con el mensaje y la linea
        raise AssertionError('Lobby.server.lua fallo al ejecutarse (%s): %s' % ('con cañon de Codex' if con_canon else 'con cañon de piezas', e))
    listar = l.eval('function(n) local r = {} for _, d in ipairs(n:GetDescendants()) do r[#r + 1] = d end return r end')
    lobby = l.eval('workspace:FindFirstChild("MAS1_Lobby")')
    assert lobby is not None, 'no se creo workspace.MAS1_Lobby'
    return l, lobby, [p for p in listar(lobby).values()]


def cajas(partes, nombres):
    return [(p.Name, R.caja(p)) for p in partes if p.Name in nombres and p.Size is not None]


DECOR = {'FarolaBase', 'FarolaPoste', 'Farol', 'FarolTecho', 'Cuerda', 'Banderin', 'Tronco', 'Copa'}
FIJAS = {'MAS1_Canon', 'MAS1_AFK', 'MAS1_Entreno', 'Puesto', 'PuestoTecho', 'ArcoPilar', 'ArcoDintel', 'SpawnLocation'}
CAMINO = ((-5.2, 0.0, -175.0), (5.2, 40.0, 22.0))   # la franja central por donde se camina hasta el cañon y se sale volando

for con_canon in (False, True):
    nombre = 'con el cañon de Codex' if con_canon else 'con el cañon de piezas'
    l, lobby, partes = correr(con_canon)
    por_nombre = {}
    for p in partes:
        por_nombre.setdefault(p.Name, []).append(p)
    # lo que lee el resto del juego
    for n in ('MAS1_Canon', 'MAS1_AFK', 'MAS1_Entreno', 'SpawnLocation'):
        assert n in por_nombre, (nombre, 'falta', n)
    assert any(h.ClassName == 'ProximityPrompt' for h in por_nombre['MAS1_Canon'][0].GetChildren(por_nombre['MAS1_Canon'][0]).values()), \
        'el aviso del cañon cuelga de MAS1_Canon'
    assert por_nombre['SpawnLocation'][0].IsA(por_nombre['SpawnLocation'][0], 'BasePart')
    if con_canon:
        assert 'CanonPajarero' in {m.Name for m in lobby.GetChildren(lobby).values()}, 'el cañon de Codex no se clono al lobby'
        assert all(p.Anchored for p in partes if p.Parent is not None and p.Parent.Name == 'CanonPajarero'), 'piezas del cañon sin anclar'
    else:
        assert 'CanonTubo' in por_nombre
    # la decoracion: cuantas y donde
    assert len(por_nombre['Farol']) == 20 and len(por_nombre['FarolaPoste']) == 20, nombre
    assert len(por_nombre['Banderin']) == 55 and len(por_nombre['Cuerda']) == 50 and len(por_nombre['Tronco']) == 14, nombre
    luces = [p for p in partes if p.ClassName == 'PointLight']
    assert len(luces) == 20, len(luces)
    assert len(partes) < 900, ('demasiadas piezas para un lobby', len(partes))
    # sobre el suelo de la plaza (70 x 196 centrada en z -74: de -172 a 24) y no bajo tierra
    for n, (mi, ma) in cajas(partes, DECOR):
        v = 2.0 if n == 'Copa' else 0.0   # el follaje de un arbol puede sobresalir un poco del borde del suelo; lo que se apoya, no
        assert -35 - v <= mi[0] and ma[0] <= 35 + v and -172 - v <= mi[2] and ma[2] <= 24 + v and mi[1] >= -0.05, (nombre, n, mi, ma)
    # lo que choca (poste, base, tronco) no pisa nada importante ni el camino central
    if con_canon:
        del_canon = [('cañon', R.caja(p)) for p in partes if p.Parent is not None and p.Parent.Name == 'CanonPajarero']
    else:
        del_canon = cajas(partes, {'CanonBase', 'CanonRueda', 'CanonTubo', 'CanonAro', 'CanonBoca'})
    assert len(del_canon) >= 5, (nombre, len(del_canon))
    protegidas = cajas(partes, FIJAS) + del_canon
    for p in partes:
        if p.Name in DECOR and p.CanCollide:
            c = R.caja(p)
            assert not R.solapan(c, CAMINO), (nombre, p.Name, 'en medio del camino central', c)
            for n, otra in protegidas:
                assert not R.solapan(c, otra, 0.5), (nombre, p.Name, 'pisa', n, c, otra)
    # los banderines cruzan el camino, pero altos: nadie a pie se da con ellos
    for n in ('Banderin', 'Cuerda'):
        for p in por_nombre[n]:
            mi, ma = R.caja(p)
            if R.solapan((mi, ma), CAMINO):
                assert mi[1] > 6.0 and not p.CanCollide, (nombre, n, 'baja o con choque sobre el camino', mi)
    # el cañon no choca con la plataforma de salida, el arco ni el punto de aparicion (margen de 1 stud)
    for n, c in del_canon:
        for otra_n, otra in cajas(partes, {'MAS1_Canon', 'ArcoPilar', 'ArcoDintel', 'SpawnLocation', 'Puesto'}):
            assert not R.solapan(c, otra, 1.0), (nombre, 'el cañon pisa', otra_n, c, otra)
    if con_canon:   # solo las mallas: RootPart es una pieza invisible (Transparency 1) de 2 x 2 x 1 que baja hasta -1 antes de escalar
        todo = [R.caja(p) for p in partes if p.Parent is not None and p.Parent.Name == 'CanonPajarero' and p.ClassName == 'MeshPart']
        assert len(todo) >= 25, len(todo)
        mi = [min(c[0][i] for c in todo) for i in range(3)]
        ma = [max(c[1][i] for c in todo) for i in range(3)]
        print('cañon de Codex en el lobby: x %.1f..%.1f, y %.1f..%.1f, z %.1f..%.1f' % (mi[0], ma[0], mi[1], ma[1], mi[2], ma[2]))
        # apoyado en el suelo (el techo del suelo esta en y = -0,05): ni hundido ni flotando, delante del arco y detras de la plataforma
        assert -9 < mi[0] and ma[0] < 9 and -0.1 <= mi[1] <= 1.0 and 12 < ma[1] < 25 and -34 < mi[2] and ma[2] < -8, (mi, ma)
    print('ok %s: %d piezas, 20 farolas, 55 banderines, 14 arboles' % (nombre, len(partes)))
print('ok')
