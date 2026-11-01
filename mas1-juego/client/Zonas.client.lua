-- Cielo y niebla por zona en el cliente de «+1 de lanzamiento por segundo»: al cruzar el arco de cada zona cambian la hora y la
-- Atmosphere (color, densidad) para que cada zona se lea distinta y el carril destaque: dia azul en la Pradera y el Mar de Nubes,
-- atardecer oscuro en la Tormenta, lila en el Cielo alto y noche (con las estrellas del cielo de Roblox) en el Espacio. Solo en este
-- cliente: cada jugador ve su zona. Colores del cielo de mapa-v01 (build_mapa.py). Donde empieza cada zona sale de Vuelo.CFG.zonas
-- (zonas largas desde el 31/10): aqui solo el cielo de cada multiplicador.
local Lighting, TweenService, RunService = game:GetService("Lighting"), game:GetService("TweenService"), game:GetService("RunService")
local V = require(game:GetService("ReplicatedStorage"):WaitForChild("Mas1"):WaitForChild("Vuelo"))

-- color de la niebla, hora, densidad por multiplicador de zona (x1 a x3: dia azul)
local DIA = { Color3.fromRGB(159, 211, 255), 14, 0.25 }
local CIELO = {
	[4] = { Color3.fromRGB(61, 71, 102), 17.8, 0.38 },
	[5] = { Color3.fromRGB(183, 163, 240), 15.5, 0.25 },
	[6] = { Color3.fromRGB(13, 16, 36), 0, 0.12 },
}
local ZONAS = {} -- desde (studs hacia -Z), color, hora, densidad
for _, z in ipairs(V.CFG.zonas) do
	local c = CIELO[z[2]] or DIA
	ZONAS[#ZONAS + 1] = { z[1], c[1], c[2], c[3] }
end
local atm = Lighting:FindFirstChildOfClass("Atmosphere")
if not atm then
	atm = Instance.new("Atmosphere")
	atm.Parent = Lighting
end
local actual

RunService.Heartbeat:Connect(function()
	local cam = workspace.CurrentCamera
	if not cam then return end
	local d, z = -cam.CFrame.Position.Z, 1
	for i, zona in ipairs(ZONAS) do
		if d >= zona[1] then z = i end
	end
	if z == actual then return end
	actual = z
	local _, color, hora, densidad = table.unpack(ZONAS[z])
	Lighting.ClockTime = hora -- de golpe: con un tween la hora pasaria por el mediodia
	TweenService:Create(atm, TweenInfo.new(1.5), { Color = color, Decay = color:Lerp(Color3.new(0, 0, 0), 0.35), Density = densidad }):Play()
end)
