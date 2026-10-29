-- Dibuja los efectos de src/Efectos.lua con ParticleEmitter. El servidor (o el juego) dispara RemoteEvent MAS1_Efecto:
--   FireClient(plr, "aro", Vector3)           -> rafaga en un punto
--   FireClient(plr, "estela", nil, parteOModelo, true/false) -> activa/desactiva un efecto continuo pegado a una parte
-- SIN PROBAR EN STUDIO.
local RS, Debris = game:GetService("ReplicatedStorage"), game:GetService("Debris")
local E = require(RS:WaitForChild("Mas1"):WaitForChild("Efectos"))
local R = RS:WaitForChild("MAS1_Efecto")

local function rgb(h) h = h:gsub("#", ""); return Color3.fromRGB(tonumber(h:sub(1, 2), 16), tonumber(h:sub(3, 4), 16), tonumber(h:sub(5, 6), 16)) end
local function emisor(spec, padre)
	local pe = Instance.new("ParticleEmitter"); pe.Rate = spec.rate or 0
	pe.Lifetime = NumberRange.new(spec.life[1], spec.life[2]); pe.Speed = NumberRange.new(spec.speed[1], spec.speed[2])
	pe.SpreadAngle = Vector2.new(spec.spread, spec.spread); pe.Acceleration = Vector3.new(spec.accel[1], spec.accel[2], spec.accel[3]); pe.Drag = 2
	pe.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, spec.size[1]), NumberSequenceKeypoint.new(1, spec.size[2]) })
	local ks = {}
	for i, c in ipairs(spec.colors) do ks[#ks + 1] = ColorSequenceKeypoint.new((i - 1) / math.max(1, #spec.colors - 1), rgb(c)) end
	pe.Color = ColorSequence.new(ks); pe.LightEmission = spec.light or 0.3
	pe.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.7, 0.2), NumberSequenceKeypoint.new(1, 1) })
	pe.Parent = padre; return pe
end

local continuos = {} -- [parte] = {tipo = emisor}
R.OnClientEvent:Connect(function(tipo, pos, parte, activo)
	local spec = E.TIPOS[tipo]; if not spec then return end
	if parte then -- efecto continuo pegado a una parte
		local p = parte:IsA("Model") and (parte.PrimaryPart or parte:FindFirstChildWhichIsA("BasePart")) or parte
		if not p then return end
		continuos[p] = continuos[p] or {}
		if activo == false then if continuos[p][tipo] then continuos[p][tipo]:Destroy(); continuos[p][tipo] = nil end
		elseif not continuos[p][tipo] then continuos[p][tipo] = emisor(spec, p) end
		return
	end
	local ancla = Instance.new("Part"); ancla.Anchored = true; ancla.CanCollide = false; ancla.CanQuery = false; ancla.Transparency = 1
	ancla.Size = Vector3.new(0.2, 0.2, 0.2); ancla.Position = pos; ancla.Parent = workspace
	local pe = emisor(spec, ancla); pe:Emit(spec.count or 20); Debris:AddItem(ancla, spec.life[2] + 0.5)
end)
