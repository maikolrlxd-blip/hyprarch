-- Orbes «+1» de «+1 de lanzamiento por segundo» vistos en el cliente: los mismos que genera el servidor (Encuentros.colocarOrbes,
-- con semilla fija), como bolas Neon doradas que giran y flotan. Al cogerlos (MAS1_Orbe, indices que manda el servidor) encogen
-- y desaparecen; en cada lanzamiento vuelven todos. Cada uno da +1 de potencia (lo suma el servidor). SIN PROBAR EN STUDIO.
local Players, RS, RunService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService")
local plr = Players.LocalPlayer
local Mas1 = RS:WaitForChild("Mas1")
local E = require(Mas1:WaitForChild("Encuentros"))
local Red = require(Mas1:WaitForChild("Red"))
local orbeEv = Red.evento("MAS1_Orbe")

local carpeta = Instance.new("Folder")
carpeta.Name = "MAS1_Orbes"
carpeta.Parent = workspace
local orbes = {}
for i, o in ipairs(E.colocarOrbes()) do
	local p = Instance.new("Part")
	p.Shape, p.Size, p.Material = Enum.PartType.Ball, Vector3.new(1.8, 1.8, 1.8), Enum.Material.Neon
	p.Color = Color3.fromRGB(255, 214, 64)
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Position = Vector3.new(o.pos.x, o.pos.y, o.pos.z)
	p.Parent = carpeta
	orbes[i] = { p = p, base = p.Position, fase = i * 0.7, vivo = true, escala = 1 }
end

orbeEv.OnClientEvent:Connect(function(indices)
	for _, i in ipairs(indices) do
		if orbes[i] then orbes[i].vivo = false end
	end
end)

plr:GetAttributeChangedSignal("EnVuelo"):Connect(function()
	if plr:GetAttribute("EnVuelo") == true then -- cada vuelo, todos otra vez
		for _, o in ipairs(orbes) do o.vivo = true end
	end
end)

RunService.RenderStepped:Connect(function(dt)
	local cam, t = workspace.CurrentCamera, os.clock()
	local cz = cam and cam.CFrame.Position.Z or 0
	for _, o in ipairs(orbes) do
		if math.abs(o.base.Z - cz) < 260 then -- solo los cercanos: el resto no se ve
			o.escala += ((o.vivo and 1 or 0) - o.escala) * (1 - math.exp(-14 * dt))
			o.p.Transparency = o.escala < 0.05 and 1 or 0
			o.p.Size = Vector3.one * 1.8 * math.max(0.05, o.escala) * (1 + 0.12 * math.sin(t * 6 + o.fase))
			o.p.Position = o.base + Vector3.new(0, math.sin(t * 2 + o.fase) * 0.4, 0)
		end
	end
end)
