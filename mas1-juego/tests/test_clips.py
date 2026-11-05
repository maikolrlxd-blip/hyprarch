import lupa
l = lupa.LuaRuntime()
# CFrame de mentira para probar src/Clips.lua fuera de Roblox: posicion + cuaternion; Lerp lineal (basta para comprobar fotogramas)
l.execute('''
local mt = {}
mt.__index = mt
local function nuevo(x, y, z, qx, qy, qz, qw)
    return setmetatable({ Position = { X = x, Y = y, Z = z }, q = { qx or 0, qy or 0, qz or 0, qw or 1 } }, mt)
end
function mt:Lerp(o, a)
    local p, r = self.Position, o.Position
    local q = {}
    for i = 1, 4 do q[i] = self.q[i] + (o.q[i] - self.q[i]) * a end
    return nuevo(p.X + (r.X - p.X) * a, p.Y + (r.Y - p.Y) * a, p.Z + (r.Z - p.Z) * a, q[1], q[2], q[3], q[4])
end
local vmt = {}
vmt.__mul = function(v, s) return setmetatable({ X = v.X * s, Y = v.Y * s, Z = v.Z * s }, vmt) end
mt.__sub = function(c, v) return nuevo(c.Position.X - v.X, c.Position.Y - v.Y, c.Position.Z - v.Z, c.q[1], c.q[2], c.q[3], c.q[4]) end
mt.__add = function(c, v) return nuevo(c.Position.X + v.X, c.Position.Y + v.Y, c.Position.Z + v.Z, c.q[1], c.q[2], c.q[3], c.q[4]) end
local viejo = nuevo
nuevo = function(...)
    local c = viejo(...)
    setmetatable(c.Position, vmt)
    return c
end
CFrame = { new = nuevo, identity = nuevo(0, 0, 0) }
math.clamp = function(x, a, b) return math.max(a, math.min(b, x)) end
''')
C = l.execute(open('src/Clips.lua', encoding='utf-8').read())
# un clip de 3 fotogramas (dur 1 s): el hueso A sube en Y de 0 a 2; el hueso B solo en el clip Otro
datos = l.eval('''{
    Sube = { n = 3, dur = 1, huesos = { A = { 0,0,0, 0,0,0,1,  0,1,0, 0,0,0,1,  0,2,0, 0,0,0,1 } } },
    Otro = { n = 2, dur = 0.5, huesos = { B = { 1,0,0, 0,0,0,1,  3,0,0, 0,0,0,1 } } },
}''')
p = C.preparar(datos)
assert p.Sube.n == 3 and p.Sube.dur == 1
assert l.eval('rawequal')(C.preparar(datos), p)  # se prepara una sola vez por tabla de datos
assert C.preparar(None) is None
huesos = l.eval('{ A = { Transform = CFrame.identity }, B = { Transform = CFrame.identity } }')
y = lambda h: huesos[h].Transform.Position.Y
x = lambda h: huesos[h].Transform.Position.X
# bucle: a mitad de clip, el fotograma del medio; pasado el final vuelve a empezar
C.aplicar(huesos, p.Sube, 0.5, 1, True)
assert abs(y('A') - 1) < 1e-9, y('A')
C.aplicar(huesos, p.Sube, 1.25, 1, True)
assert abs(y('A') - 0.5) < 1e-9, y('A')
# sin bucle: se queda en el ultimo fotograma
C.aplicar(huesos, p.Sube, 3, 1, False)
assert abs(y('A') - 2) < 1e-9
# escala: los desplazamientos crecen con la escala del modelo
C.aplicar(huesos, p.Sube, 3, 2.2, False)
assert abs(y('A') - 4.4) < 1e-9, y('A')
# sin «encima», los huesos que el clip no trae vuelven a reposo; con «encima» se quedan como estaban
C.aplicar(huesos, p.Otro, 0, 1, False)
assert abs(x('B') - 1) < 1e-9 and y('A') == 0
C.aplicar(huesos, p.Sube, 3, 1, False)
C.aplicar(huesos, p.Otro, 0.5, 1, False, True)
assert abs(x('B') - 3) < 1e-9 and abs(y('A') - 2) < 1e-9
C.aplicar(huesos, None, 0, 1, True)  # sin clip no hace nada
print('ok')
