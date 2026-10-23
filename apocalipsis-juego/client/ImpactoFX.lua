-- PROVISIONAL y SIN PROBAR EN STUDIO. Dibuja en Roblox lo que decide src/Impactos.lua: particulas al acertar y mancha que se desvanece.
-- Uso: local FX = require(script.ImpactoFX); FX.mostrar(posicion, spec, normal) con spec = resultado de Impactos.resolve (spec.efecto, spec.mancha).
-- Los sonidos (wav de apocalipsis-sonidos/) hay que SUBIRLOS a Roblox como audios y poner sus ids en SONIDOS (Maikol: subida con tu cuenta).
local Debris = game:GetService("Debris")
local TweenService = game:GetService("TweenService")
local RS = game:GetService("ReplicatedStorage")
local SR = RS:WaitForChild("Luto", 5) or RS:WaitForChild("SlimeRush", 5)
local Impactos = SR and require(SR.Impactos) or nil
local Disparo = SR and require(SR.Disparo) or nil
local reservaHuecos, reservaMarcas = nil, nil

local FX = {}
local SONIDOS = {} -- nombre -> "rbxassetid://..." (pendiente de subir)
local reserva = nil

local function emisor(pos, e)
	local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.Transparency = 1
	p.Size = Vector3.new(0.2, 0.2, 0.2); p.Position = pos; p.Parent = workspace
	local pe = Instance.new("ParticleEmitter"); pe.Rate = 0; pe.Lifetime = NumberRange.new(e.life * 0.7, e.life)
	pe.Speed = NumberRange.new(e.speed * 0.5, e.speed); pe.SpreadAngle = Vector2.new(35, 35); pe.Drag = 6
	pe.Acceleration = Vector3.new(0, -40, 0)
	pe.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, e.size), NumberSequenceKeypoint.new(1, 0) })
	pe.Color = ColorSequence.new(Color3.fromRGB(e.color[1], e.color[2], e.color[3]))
	pe.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) })
	pe.LightEmission = 0; pe.Parent = p
	local d = e.direccion; p.CFrame = CFrame.lookAt(pos, pos + Vector3.new(d.x, d.y, d.z))
	pe:Emit(math.floor(e.count))
	Debris:AddItem(p, e.life + 0.5)
end

local function mancha(pos, normal, tam, vida)
	if not reserva and Impactos then reserva = Impactos.nuevaReserva() end
	local m = Instance.new("Part"); m.Anchored = true; m.CanCollide = false; m.CanQuery = false; m.Material = Enum.Material.SmoothPlastic
	m.Color = Color3.fromRGB(110, 12, 20); m.Shape = Enum.PartType.Cylinder; m.Size = Vector3.new(0.05, tam, tam)
	local n = Vector3.new(normal.x, normal.y, normal.z)
	m.CFrame = CFrame.lookAt(pos + n * 0.03, pos + n) * CFrame.Angles(0, math.rad(90), 0); m.Parent = workspace
	if reserva then
		local viejo = Impactos.agregarMancha(reserva, m, os.clock())
		if viejo and viejo.mancha and viejo.mancha.Parent then viejo.mancha:Destroy() end
	end
	task.delay(vida * 0.7, function()
		if m.Parent then TweenService:Create(m, TweenInfo.new(vida * 0.3), { Transparency = 1 }):Play() end
	end)
	Debris:AddItem(m, vida + 1)
end

-- AGUJERO DE BALA: marca visible DONDE impacta (hueco oscuro con borde astillado). Se pega a la pieza golpeada para que la siga si se mueve.
function FX.agujero(pos, normal, pieza, armaId, sobreEnemigo)
	if not Disparo or typeof(normal) ~= "Vector3" then return end
	local a = Disparo.agujero(armaId or "pistola", sobreEnemigo)
	local reserva = sobreEnemigo and reservaMarcas or reservaHuecos
	if not reserva then
		reserva = Impactos.nuevaReserva(sobreEnemigo and Disparo.AGUJERO.max_enemigo or Disparo.AGUJERO.max_mapa)
		if sobreEnemigo then reservaMarcas = reserva else reservaHuecos = reserva end
	end
	local function disco(tam, color, alto, desplazo)
		local d = Instance.new("Part"); d.Shape = Enum.PartType.Cylinder; d.Size = Vector3.new(alto, tam, tam)
		d.Color = Color3.fromRGB(color[1], color[2], color[3]); d.Material = Enum.Material.SmoothPlastic
		d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true; d.Anchored = false
		d.CFrame = CFrame.lookAt(pos + normal * desplazo, pos + normal) * CFrame.Angles(0, math.rad(90), 0)
		d.Parent = workspace
		if pieza and pieza.Parent then
			if pieza.Anchored then d.Anchored = true else local w = Instance.new("WeldConstraint"); w.Part0 = d; w.Part1 = pieza; w.Parent = d end
		else d.Anchored = true end
		Debris:AddItem(d, a.vida + 1); return d
	end
	local borde = disco(a.tam * a.borde, a.color_borde, 0.03, 0.02)
	local centro = disco(a.tam, a.color_centro, 0.05, 0.035)
	local viejo = Impactos.agregarMancha(reserva, { borde, centro }, os.clock())
	if viejo and viejo.mancha then for _, p in ipairs(viejo.mancha) do if p.Parent then p:Destroy() end end end
end

function FX.mostrar(pos, spec, normal)
	emisor(pos, spec.efecto)
	if spec.mancha and typeof(normal) == "Vector3" then mancha(pos, { x = normal.X, y = normal.Y, z = normal.Z }, spec.mancha.tam, Impactos and Impactos.MANCHAS.vida or 20) end
end

return FX
