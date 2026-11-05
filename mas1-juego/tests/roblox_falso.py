# Un Roblox de mentira, lo justo para ejecutar con lupa los scripts del juego que no se pueden probar sin Studio:
#   - nuevo(): Vector3, CFrame (con rotacion de verdad: *, +, Inverse, lookAt, Angles, Rotation), Color3, UDim2, Enum, Instance con
#     padre e hijos (Parent, Name, GetChildren, GetDescendants, FindFirstChild, IsA, Clone, Destroy, PivotTo, ScaleTo, atributos),
#     servicios y workspace. Para scripts que solo construyen cosas al arrancar (server/Lobby.server.lua).
#   - Servidor: ademas senales (Connect/Fire), RemoteEvent (OnServerEvent y un registro de todo lo que se manda con FireClient),
#     jugadores con personaje, un reloj virtual con task.spawn/delay/wait, un DataStore en memoria (con latencia y fallos a pedido),
#     require de ModuleScripts y Random. Para ejecutar de verdad server/Partida.server.lua y server/Guardado.lua: entrar, entrenar,
#     lanzarse, volar, aterrizar, comprar, salir.
#   - a_lua(): traduce el Luau de los scripts (continue, +=) a Lua con el mismo significado.
# NO valida nombres de propiedades de Roblox ni hace fisica: un error de ejecucion (un nil, una operacion rara) salta aqui y no al darle
# a Play, pero lo que depende del motor de Roblox sigue siendo cosa de Studio. Lo usan tests/test_lobby.py y tests/test_servidor.py.
import glob
import os
import re
import lupa

PRELUDIO = r'''
local function nuevaSenal()
	local s = { _c = {} }
	function s:Connect(f)
		local c = { f = f, on = true }
		self._c[#self._c + 1] = c
		return { Disconnect = function() c.on = false end }
	end
	function s:Fire(...)
		for _, c in ipairs(self._c) do
			if c.on then c.f(...) end
		end
	end
	return s
end
__senal = nuevaSenal

local V3 = {}
local function nv3(x, y, z) return setmetatable({ X = x, Y = y, Z = z }, V3) end
V3.__index = function(t, k)
	if k == "Magnitude" then return math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z) end
	if k == "Unit" then
		local m = math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z)
		return nv3(t.X / m, t.Y / m, t.Z / m)
	end
	return nil
end
V3.__add = function(a, b) return nv3(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
V3.__sub = function(a, b) return nv3(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
V3.__unm = function(a) return nv3(-a.X, -a.Y, -a.Z) end
V3.__mul = function(a, b)
	if type(a) == "number" then return nv3(a * b.X, a * b.Y, a * b.Z) end
	if type(b) == "number" then return nv3(a.X * b, a.Y * b, a.Z * b) end
	return nv3(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
V3.__div = function(a, b)
	if type(b) == "number" then return nv3(a.X / b, a.Y / b, a.Z / b) end
	return nv3(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
end
Vector3 = { new = function(x, y, z) return nv3(x or 0, y or 0, z or 0) end }
Vector3.zero, Vector3.one = nv3(0, 0, 0), nv3(1, 1, 1)

local function cross(a, b) return nv3(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X) end
local CF = {}
local I3 = { 1, 0, 0, 0, 1, 0, 0, 0, 1 }
local function ncf(p, r) return setmetatable({ p = p, r = r }, CF) end
CF.__index = function(t, k)
	if k == "Position" then return t.p end
	if k == "LookVector" then return nv3(-t.r[3], -t.r[6], -t.r[9]) end
	if k == "RightVector" then return nv3(t.r[1], t.r[4], t.r[7]) end
	if k == "UpVector" then return nv3(t.r[2], t.r[5], t.r[8]) end
	if k == "Rotation" then return ncf(nv3(0, 0, 0), t.r) end
	return rawget(CF, k)
end
local function mulm(a, b)
	local r = {}
	for i = 0, 2 do
		for j = 0, 2 do
			r[i * 3 + j + 1] = a[i * 3 + 1] * b[j + 1] + a[i * 3 + 2] * b[j + 4] + a[i * 3 + 3] * b[j + 7]
		end
	end
	return r
end
local function rot(m, v) return nv3(m[1] * v.X + m[2] * v.Y + m[3] * v.Z, m[4] * v.X + m[5] * v.Y + m[6] * v.Z, m[7] * v.X + m[8] * v.Y + m[9] * v.Z) end
CF.__mul = function(a, b)
	if getmetatable(b) == V3 then return rot(a.r, b) + a.p end
	return ncf(rot(a.r, b.p) + a.p, mulm(a.r, b.r))
end
CF.__add = function(a, v) return ncf(a.p + v, a.r) end
CF.__sub = function(a, v) return ncf(a.p - v, a.r) end
function CF.Inverse(a)
	local m = a.r
	local t = { m[1], m[4], m[7], m[2], m[5], m[8], m[3], m[6], m[9] }
	return ncf(-rot(t, a.p), t)
end
function CF.ToObjectSpace(a, b) return a:Inverse() * b end
function CF.PointToObjectSpace(a, p) return a:Inverse() * p end
CFrame = {}
function CFrame.new(x, y, z, ...)
	if x == nil then return ncf(nv3(0, 0, 0), I3) end
	if getmetatable(x) == V3 then return ncf(x, I3) end
	local r = { ... }
	if #r == 9 then return ncf(nv3(x, y, z), r) end   -- CFrame.new(x, y, z, R00 ... R22)
	return ncf(nv3(x, y, z), I3)
end
function CFrame.Angles(rx, ry, rz)
	local cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
	local Rx, Ry, Rz = { 1, 0, 0, 0, cx, -sx, 0, sx, cx }, { cy, 0, sy, 0, 1, 0, -sy, 0, cy }, { cz, -sz, 0, sz, cz, 0, 0, 0, 1 }
	return ncf(nv3(0, 0, 0), mulm(Rz, mulm(Ry, Rx)))
end
function CFrame.lookAt(from, to, up)
	local look = (to - from).Unit
	local right = cross(look, up or nv3(0, 1, 0)).Unit
	local upv = cross(right, look)
	return ncf(from, { right.X, upv.X, -look.X, right.Y, upv.Y, -look.Y, right.Z, upv.Z, -look.Z })
end
CFrame.identity = ncf(nv3(0, 0, 0), I3)

Color3 = { fromRGB = function(r, g, b) return { R = r / 255, G = g / 255, B = b / 255 } end }
UDim2 = { new = function(...) return { ... } end, fromScale = function(a, b) return { a, b } end, fromOffset = function(a, b) return { a, b } end }
Enum = setmetatable({}, { __index = function(t, k)
	local v = setmetatable({}, { __index = function(_, kk) return k .. "." .. kk end })
	rawset(t, k, v)
	return v
end })
NumberRange, NumberSequence, ColorSequence = { new = function(...) return { ... } end }, { new = function(...) return { ... } end }, { new = function(...) return { ... } end }

REGISTRO, KICKS = {}, {}
local Inst = {}
local PARTES = { Part = true, WedgePart = true, SpawnLocation = true, MeshPart = true }
local function nueva(clase)
	local d = { ClassName = clase, Name = clase, _hijos = {} }
	if PARTES[clase] then
		d.Size, d.CFrame, d.CanCollide, d.Anchored, d.Transparency = nv3(4, 1, 2), ncf(nv3(0, 0, 0), I3), true, false, 0
	end
	if clase == "RemoteEvent" then d.OnServerEvent, d.OnClientEvent = nuevaSenal(), nuevaSenal() end
	if clase == "Player" then d.CharacterAdded = nuevaSenal() end
	if clase == "Humanoid" then d.Health, d.Sit, d.FloorMaterial, d.MoveDirection = 100, false, "Material.Grass", nv3(0, 0, 0) end
	return setmetatable({ _d = d }, Inst)
end
Inst.__index = function(t, k)
	local m = rawget(Inst, k)
	if m ~= nil then return m end
	local d = rawget(t, "_d")
	if k == "Position" and d.CFrame then return d.CFrame.p end
	return d[k]
end
Inst.__newindex = function(t, k, v)
	local d = rawget(t, "_d")
	if k == "Parent" then
		if d.Parent then
			local h = d.Parent._d._hijos
			for i, x in ipairs(h) do
				if x == t then table.remove(h, i) break end
			end
		end
		d.Parent = v
		if v then
			v._d._hijos[#v._d._hijos + 1] = t
			local anc = v
			while anc do
				local senal = anc._d.DescendantAdded
				if senal then senal:Fire(t) end
				anc = anc._d.Parent
			end
		end
	elseif k == "Position" and d.CFrame then d.CFrame = ncf(v, d.CFrame.r)
	else d[k] = v end
end
function Inst.IsA(t, c)
	local clase = t._d.ClassName
	return clase == c or c == "Instance" or (c == "BasePart" and PARTES[clase] == true)
end
function Inst.GetChildren(t)
	local r = {}
	for i, h in ipairs(t._d._hijos) do r[i] = h end
	return r
end
function Inst.GetDescendants(t)
	local r = {}
	local function rec(n)
		for _, h in ipairs(n._d._hijos) do r[#r + 1] = h rec(h) end
	end
	rec(t)
	return r
end
function Inst.FindFirstChild(t, nombre, recursivo)
	for _, h in ipairs(t._d._hijos) do
		if h._d.Name == nombre then return h end
	end
	if recursivo then
		for _, h in ipairs(t._d._hijos) do
			local x = h:FindFirstChild(nombre, true)
			if x then return x end
		end
	end
	return nil
end
function Inst.WaitForChild(t, nombre)
	local x = t:FindFirstChild(nombre)
	if not x then error("WaitForChild: no existe " .. nombre .. " en " .. t._d.Name, 2) end
	return x
end
function Inst.FindFirstChildOfClass(t, clase)
	for _, h in ipairs(t._d._hijos) do
		if h._d.ClassName == clase then return h end
	end
	return nil
end
function Inst.FindFirstChildWhichIsA(t, clase, recursivo)
	for _, h in ipairs(t._d._hijos) do
		if h:IsA(clase) then return h end
	end
	if recursivo then
		for _, h in ipairs(t._d._hijos) do
			local x = h:FindFirstChildWhichIsA(clase, true)
			if x then return x end
		end
	end
	return nil
end
function Inst.Destroy(t) t.Parent = nil end
function Inst.Clone(t)
	local c = nueva(t._d.ClassName)
	for k, v in pairs(t._d) do
		if k ~= "Parent" and k ~= "_hijos" then c._d[k] = v end
	end
	for _, h in ipairs(t._d._hijos) do h:Clone().Parent = c end
	return c
end
function Inst.GetPivot(t) return t._d.pivote or CFrame.identity end
function Inst.PivotTo(t, cf)
	local viejo = t:GetPivot()
	for _, d in ipairs(t:GetDescendants()) do
		if d:IsA("BasePart") then d.CFrame = cf * (viejo:Inverse() * d.CFrame) end
	end
	t._d.pivote = cf
end
function Inst.GetScale(t) return t._d.escala or 1 end
function Inst.ScaleTo(t, s)
	local f, piv = s / t:GetScale(), t:GetPivot()
	for _, d in ipairs(t:GetDescendants()) do
		if d:IsA("BasePart") then
			local rel = piv:Inverse() * d.CFrame
			d.Size = d.Size * f
			d.CFrame = piv * ncf(rel.p * f, rel.r)
		end
	end
	t._d.escala = s
end
function Inst.SetAttribute(t, n, v)
	local d = t._d
	d._attr = d._attr or {}
	local viejo = d._attr[n]
	d._attr[n] = v
	if viejo ~= v and d._senales and d._senales[n] then d._senales[n]:Fire() end
end
function Inst.GetAttribute(t, n)
	local a = t._d._attr
	return a and a[n]
end
function Inst.GetAttributeChangedSignal(t, n)
	local d = t._d
	d._senales = d._senales or {}
	d._senales[n] = d._senales[n] or nuevaSenal()
	return d._senales[n]
end
function Inst.FireClient(t, plr, ...) REGISTRO[#REGISTRO + 1] = { ev = t._d.Name, plr = plr, args = table.pack(...) } end
function Inst.FireAllClients(t, ...) REGISTRO[#REGISTRO + 1] = { ev = t._d.Name, todos = true, args = table.pack(...) } end
function Inst.Kick(t, mensaje) KICKS[#KICKS + 1] = { plr = t, mensaje = mensaje } end
Instance = { new = nueva }

local servicios = {}
local function servicio(n)
	if not servicios[n] then servicios[n] = nueva(n) end
	return servicios[n]
end
workspace = servicio("Workspace")
workspace._d.DescendantAdded = nuevaSenal()
servicio("Lighting")._d.Brightness = 1
game = { GetService = function(_, n) return servicio(n) end, IsLoaded = function() return true end }
'''

PRELUDIO_SERVIDOR = r'''
RELOJ = 0
local cola, seq = {}, 0
local function programar(t, tarea)
	seq = seq + 1
	tarea.t, tarea.seq = t, seq
	cola[#cola + 1] = tarea
end
local function ejecutar(tarea)
	if tarea.co then
		local ok, err = coroutine.resume(tarea.co)
		if not ok then error(debug.traceback(tarea.co, tostring(err)), 0) end
	else
		tarea.f(table.unpack(tarea.args, 1, tarea.args.n))
	end
end
function AVANZAR(dt)   -- el reloj virtual avanza dt segundos y se ejecuta lo que toque, en orden
	local objetivo = RELOJ + dt
	while true do
		local mejor, mi
		for i, tarea in ipairs(cola) do
			if tarea.t <= objetivo and (not mejor or tarea.t < mejor.t or (tarea.t == mejor.t and tarea.seq < mejor.seq)) then mejor, mi = tarea, i end
		end
		if not mejor then break end
		table.remove(cola, mi)
		if mejor.t > RELOJ then RELOJ = mejor.t end
		ejecutar(mejor)
	end
	RELOJ = objetivo
end
task = {}
function task.spawn(f, ...)
	local co = coroutine.create(f)
	local ok, err = coroutine.resume(co, ...)
	if not ok then error(debug.traceback(co, tostring(err)), 0) end
	return co
end
function task.delay(t, f, ...) programar(RELOJ + t, { f = f, args = table.pack(...) }) end
function task.wait(t)
	t = t or 0.03
	if coroutine.isyieldable() then
		programar(RELOJ + t, { co = coroutine.running() })
		coroutine.yield()
	else
		AVANZAR(t)
	end
	return t
end
AVISOS = {}   -- lo que el servidor escribe con warn(): se guarda para comprobarlo en vez de ensuciar la salida
warn = function(...)
	local t = {}
	for i = 1, select("#", ...) do t[#t + 1] = tostring((select(i, ...))) end
	AVISOS[#AVISOS + 1] = table.concat(t, " ")
end
os.clock = function() return RELOJ end
os.time = function() return 1700000000 + math.floor(RELOJ) end
Random = { new = function(semilla)
	local x = (semilla or 12345) % 2147483647
	if x == 0 then x = 1 end
	return { NextNumber = function(self) x = (x * 48271) % 2147483647 return x / 2147483647 end }
end }

local Pl = game:GetService("Players")
Pl._d.PlayerAdded, Pl._d.PlayerRemoving = __senal(), __senal()
Pl._d.GetPlayers = function(self)
	local r = {}
	for _, h in ipairs(self._d._hijos) do
		if h._d.ClassName == "Player" then r[#r + 1] = h end
	end
	return r
end
Pl._d.GetPlayerByUserId = function(self, id)
	for _, h in ipairs(self._d._hijos) do
		if h._d.ClassName == "Player" and h._d.UserId == id then return h end
	end
	return nil
end
local Run = game:GetService("RunService")
Run._d.Heartbeat = __senal()
Run._d.IsStudio = function() return true end
Run._d.IsServer = function() return true end
local nguid = 0
game:GetService("HttpService")._d.GenerateGUID = function() nguid = nguid + 1 return "guid-" .. nguid end
game.JobId = ""
CERRAR = nil
game.BindToClose = function(_, f) CERRAR = f end

ALMACEN, LATENCIA, FALLOS = {}, 0, 0   -- el DataStore en memoria; LATENCIA: segundos de espera por llamada; FALLOS: llamadas que fallan
local function copia(v)
	if type(v) ~= "table" then return v end
	local c = {}
	for k, x in pairs(v) do c[k] = copia(x) end
	return c
end
local tienda = {}
tienda.GetAsync = function(self, k)
	if LATENCIA > 0 then task.wait(LATENCIA) end
	return copia(ALMACEN[k])
end
tienda.UpdateAsync = function(self, k, f)
	if LATENCIA > 0 then task.wait(LATENCIA) end
	if FALLOS > 0 then
		FALLOS = FALLOS - 1
		error("DataStore caido (simulado)")
	end
	local nuevo = f(copia(ALMACEN[k]))
	if nuevo ~= nil then ALMACEN[k] = copia(nuevo) end
	return copia(ALMACEN[k])
end
game:GetService("DataStoreService")._d.GetDataStore = function(self, nombre) return tienda end

function require(m)
	local d = m._d
	if d.cargado == nil then
		d.cargado = false
		local f, e = load(d.fuente, "=" .. d.Name, "t", setmetatable({ script = m }, { __index = _G }))
		if not f then error(e, 0) end
		d.valor = f()
		d.cargado = true
	end
	return d.valor
end

H = {}
function H.carpeta(padre, nombre)
	local f = Instance.new("Folder")
	f.Name = nombre
	f.Parent = padre
	return f
end
function H.codigo(clase, padre, nombre, fuente)
	local m = Instance.new(clase)
	m.Name = nombre
	m._d.fuente = fuente
	m.Parent = padre
	return m
end
function H.correr(s)
	local f, e = load(s._d.fuente, "=" .. s._d.Name, "t", setmetatable({ script = s }, { __index = _G }))
	if not f then error(e, 0) end
	return f()
end
function H.jugador(nombre, id)
	local p = Instance.new("Player")
	p.Name, p.UserId = nombre, id
	p.Parent = game:GetService("Players")
	game:GetService("Players")._d.PlayerAdded:Fire(p)
	return p
end
function H.personaje(p, x, y, z)
	local c = Instance.new("Model")
	c.Name = p.Name
	local h = Instance.new("Humanoid")
	h.Name = "Humanoid"
	h.Parent = c
	local r = Instance.new("Part")
	r.Name, r.CFrame = "HumanoidRootPart", CFrame.new(x, y, z)
	r.Parent = c
	p.Character = c
	p._d.CharacterAdded:Fire(c)
	return c
end
function H.raiz(p) return p.Character:FindFirstChild("HumanoidRootPart") end
function H.mover(p, x, y, z) H.raiz(p).CFrame = CFrame.new(x, y, z) end
function H.direccion(p, x, y, z) p.Character:FindFirstChildOfClass("Humanoid")._d.MoveDirection = Vector3.new(x, y, z) end
function H.salud(p, v) p.Character:FindFirstChildOfClass("Humanoid")._d.Health = v end
function H.sacar(p)
	game:GetService("Players")._d.PlayerRemoving:Fire(p)
	p.Parent = nil
end
function H.latido(dt)
	game:GetService("RunService")._d.Heartbeat:Fire(dt)
	AVANZAR(dt)
end
function H.accion(p, ...)
	game:GetService("ReplicatedStorage"):FindFirstChild("MAS1_Accion")._d.OnServerEvent:Fire(p, ...)
end
function H.attr(p, n) return p:GetAttribute(n) end
function H.poner(p, n, v) p:SetAttribute(n, v) end
function H.eventos(nombre, plr)   -- los argumentos de cada FireClient / FireAllClients de ese evento (de ese jugador o a todos)
	local r = {}
	for _, e in ipairs(REGISTRO) do
		if e.ev == nombre and (plr == nil or e.todos or e.plr == plr) then r[#r + 1] = e.args end
	end
	return r
end
'''


def _tokens(src):
    """(tipo, texto, inicio, fin) de palabras, cadenas, comentarios y otros caracteres sueltos de un fuente de Lua."""
    i, n, out = 0, len(src), []
    while i < n:
        c = src[i]
        m = re.match(r'(--)?\[(=*)\[', src[i:i + 40]) if (c == '[' or src.startswith('--[', i)) else None
        if m:   # comentario o cadena larga
            cierre = ']' + m.group(2) + ']'
            j = src.find(cierre, i + len(m.group(0)))
            j = n if j < 0 else j + len(cierre)
            out.append(('comentario' if m.group(1) else 'cadena', src[i:j], i, j))
            i = j
        elif src.startswith('--', i):
            j = src.find('\n', i)
            j = n if j < 0 else j
            out.append(('comentario', src[i:j], i, j))
            i = j
        elif c in '"\'':
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == '\\' else 1
            j += 1
            out.append(('cadena', src[i:j], i, j))
            i = j
        elif c.isalpha() or c == '_':
            m = re.match(r'[A-Za-z_]\w*', src[i:])
            out.append(('palabra', m.group(0), i, i + len(m.group(0))))
            i += len(m.group(0))
        else:
            out.append(('otro', c, i, i + 1))
            i += 1
    return out


COMPUESTA = re.compile(r'(?P<lhs>[A-Za-z_][\w\.\[\]]*)\s*(?P<op>\+|-|\*|/|%|\^|\.\.)=\s*(?P<rhs>.+?)'
                       r'(?=\s+end\b|\s+else\b|\s*--|\s*;|\s+[A-Za-z_][\w\.\[\]]*\s*(?:\+|-|\*|/|%|\^|\.\.)=|\s*$)', re.M)


def a_lua(src):
    """Luau -> Lua con el mismo significado: `x += y` (y -=, *=, /=, %=, ^=, ..=) y `continue` (un goto a una etiqueta al final del bucle)."""
    protegidos = [(a, b) for tipo, _, a, b in _tokens(src) if tipo in ('cadena', 'comentario')]

    def dentro(pos):
        return any(a <= pos < b for a, b in protegidos)
    cambios = []
    for m in COMPUESTA.finditer(src):
        if not dentro(m.start()):
            lhs, op, rhs = m.group('lhs'), m.group('op'), m.group('rhs')
            cambios.append((m.start(), m.end(), '%s = %s %s (%s)' % (lhs, lhs, op, rhs)))
    for a, b, texto in sorted(cambios, reverse=True):
        src = src[:a] + texto + src[b:]
    pila, nid, cambios, previo = [], 0, [], None
    for tipo, txt, a, b in _tokens(src):
        if tipo == 'comentario':
            continue
        campo = previo is not None and previo[0] == 'otro' and previo[1] in '.:'
        if tipo == 'palabra' and not campo:
            if txt in ('for', 'while'):
                nid += 1
                pila.append({'k': 'lazo', 'id': nid, 'do': True, 'usado': False})
            elif txt == 'do':
                if pila and pila[-1]['k'] == 'lazo' and pila[-1]['do']:
                    pila[-1]['do'] = False
                else:
                    pila.append({'k': 'do'})
            elif txt in ('if', 'function', 'repeat'):
                pila.append({'k': txt})
            elif txt == 'until':
                pila.pop()
            elif txt == 'end':
                e = pila.pop()
                if e['k'] == 'lazo' and e['usado']:
                    cambios.append((a, a, '::continue_%d:: ' % e['id']))
            elif txt == 'continue':
                lazo = next(e for e in reversed(pila) if e['k'] == 'lazo')
                lazo['usado'] = True
                cambios.append((a, b, 'goto continue_%d' % lazo['id']))
        previo = (tipo, txt)
    for a, b, texto in sorted(cambios, reverse=True):
        src = src[:a] + texto + src[b:]
    return src


def nuevo():
    """Un LuaRuntime con el Roblox de mentira instalado."""
    l = lupa.LuaRuntime()
    l.execute(PRELUDIO)
    return l


class Servidor:
    """Un servidor de juego de mentira con el codigo real de src/, server/Guardado.lua y server/Partida.server.lua cargado."""

    def __init__(self, aros=(-300, -700, -1100), enemigos_fijos=False):
        self.l = nuevo()
        self.l.execute(PRELUDIO_SERVIDOR)
        self.H = self.l.globals().H
        self.g = self.l.globals()
        self._mundo(aros)
        rs = self.l.eval('game:GetService("ReplicatedStorage")')
        mas1 = self.H.carpeta(rs, 'Mas1')
        for ruta in sorted(glob.glob('src/*.lua')):
            self.H.codigo('ModuleScript', mas1, os.path.basename(ruta)[:-4], a_lua(open(ruta, encoding='utf-8').read()))
        sss = self.l.eval('game:GetService("ServerScriptService")')
        carpeta = self.H.carpeta(sss, 'Mas1Servidor')
        self.H.codigo('ModuleScript', carpeta, 'Guardado', a_lua(open('server/Guardado.lua', encoding='utf-8').read()))
        self.script = self.H.codigo('Script', carpeta, 'Partida', a_lua(open(os.environ.get('PARTIDA_SERVER', 'server/Partida.server.lua'), encoding='utf-8').read()))
        self.H.correr(self.script)

    def _mundo(self, aros):
        self.l.execute('''
        local function carpeta(n) local f = Instance.new("Folder") f.Name = n f.Parent = workspace return f end
        local function parte(padre, n, x, y, z, sx, sy, sz, clase)
            local p = Instance.new(clase or "Part") p.Name = n p.CFrame = CFrame.new(x, y, z) p.Size = Vector3.new(sx, sy, sz) p.Parent = padre return p
        end
        local lobby = carpeta("MAS1_Lobby")
        parte(lobby, "SpawnLocation", 0, 0.5, 14, 10, 1, 10, "SpawnLocation")
        parte(workspace, "MAS1_Canon", 0, 0.5, -38, 10, 1, 10)
        parte(workspace, "MAS1_AFK", -20, 0.2, -62, 16, 0.4, 16)
        parte(workspace, "MAS1_Entreno", 20, 0.2, -62, 16, 0.4, 16)
        function CREAR_ARO(z)
            local m = Instance.new("Model") m.Name = "Aro" m.Parent = workspace
            parte(m, "Centro", 0, 20, z, 1, 1, 1)
            for k = 0, 11 do
                local a = k * math.pi / 6
                parte(m, "Bloque", math.cos(a) * 8, 20 + math.sin(a) * 8, z, 2, 2, 2)
            end
        end
        ''')
        for z in aros:
            self.l.eval('CREAR_ARO')(z)

    # ---- manejo de jugadores y del tiempo
    def jugador(self, nombre='Ana', uid=1001, x=0.0, y=3.0, z=14.0, cargar=True):
        p = self.H.jugador(nombre, uid)
        self.H.personaje(p, x, y, z)
        if cargar:
            self.avanzar(0.1)
        return p

    def avanzar(self, segundos, paso=1 / 60):
        t = 0.0
        while t < segundos - 1e-9:
            self.H.latido(min(paso, segundos - t))
            t += paso

    def attr(self, p, nombre):
        return self.H.attr(p, nombre)

    def poner(self, p, nombre, valor):
        self.H.poner(p, nombre, valor)

    def accion(self, p, *args):
        self.H.accion(p, *args)

    def eventos(self, nombre, p=None):
        return [[a[i] for i in range(1, a.n + 1)] for a in self.H.eventos(nombre, p).values()]

    def almacen(self, clave):
        return self.g.ALMACEN[clave]

    def avisos(self):
        """Lo que el servidor ha escrito con warn()."""
        return [a for _, a in self.g.AVISOS.items()]


def caja(parte):
    """(min, max) de la caja alineada con los ejes de una pieza (con su rotacion), como tuplas (x, y, z)."""
    s, c = parte.Size, parte.CFrame
    r = [c.r[i] for i in range(1, 10)]
    ext = (s.X, s.Y, s.Z)
    centro = (c.p.X, c.p.Y, c.p.Z)
    half = [sum(abs(r[i * 3 + j]) * ext[j] for j in range(3)) / 2 for i in range(3)]
    return tuple(centro[i] - half[i] for i in range(3)), tuple(centro[i] + half[i] for i in range(3))


def solapan(a, b, margen=0.0):
    """¿Se pisan dos cajas (min, max)? margen > 0: tambien si quedan a menos de ese margen."""
    return all(a[0][i] < b[1][i] + margen and b[0][i] < a[1][i] + margen for i in range(3))
