# Un Roblox de mentira, lo justo para ejecutar con lupa los scripts que solo construyen cosas al arrancar (server/Lobby.server.lua):
# Vector3, CFrame (con rotacion de verdad: *, Inverse, lookAt, Angles), Color3, UDim2, Enum, Instance con padre e hijos
# (Parent, Name, GetChildren, GetDescendants, FindFirstChild, IsA, Clone, Destroy, PivotTo, ScaleTo) y los servicios (game:GetService,
# workspace). Sirve para que un error de ejecucion (un nil, una operacion rara) salte aqui y no al darle a Play, y para medir donde
# queda cada pieza (tamaño y CFrame reales). NO valida nombres de propiedades ni hace fisica. Lo usan tests/test_lobby.py y los que
# se le sumen.
import lupa

PRELUDIO = r'''
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
function CF.Inverse(a)
	local m = a.r
	local t = { m[1], m[4], m[7], m[2], m[5], m[8], m[3], m[6], m[9] }
	return ncf(-rot(t, a.p), t)
end
function CF.ToObjectSpace(a, b) return a:Inverse() * b end
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

local Inst = {}
local PARTES = { Part = true, WedgePart = true, SpawnLocation = true, MeshPart = true }
local function nueva(clase)
	local d = { ClassName = clase, Name = clase, _hijos = {} }
	if PARTES[clase] then
		d.Size, d.CFrame, d.CanCollide, d.Anchored, d.Transparency = nv3(4, 1, 2), ncf(nv3(0, 0, 0), I3), true, false, 0
	end
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
		if v then v._d._hijos[#v._d._hijos + 1] = t end
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
Instance = { new = nueva }

local servicios = {}
local function servicio(n)
	if not servicios[n] then servicios[n] = nueva(n) end
	return servicios[n]
end
workspace = servicio("Workspace")
servicio("Lighting")._d.Brightness = 1
game = { GetService = function(_, n) return servicio(n) end, IsLoaded = function() return true end }
'''


def nuevo():
    """Un LuaRuntime con el Roblox de mentira instalado."""
    l = lupa.LuaRuntime()
    l.execute(PRELUDIO)
    return l


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
