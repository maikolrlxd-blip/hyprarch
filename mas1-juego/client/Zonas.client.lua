-- Cielo y niebla por zona en el cliente de «+1 de lanzamiento por segundo»: al cruzar el arco de cada zona cambian la hora y la
-- Atmosphere (color, densidad) para que cada zona se lea distinta y el carril destaque: dia azul en la Pradera y el Mar de Nubes,
-- atardecer oscuro en la Tormenta, lila en el Cielo alto y noche (con las estrellas del cielo de Roblox) en el Espacio. Solo en este
-- cliente: cada jugador ve su zona. Colores del cielo de mapa-v01 (build_mapa.py). SIN PROBAR EN STUDIO.
local Lighting, TweenService, RunService = game:GetService("Lighting"), game:GetService("TweenService"), game:GetService("RunService")

-- desde (studs hacia -Z), color de la niebla, hora, densidad
local ZONAS = {
	{ 0, Color3.fromRGB(159, 211, 255), 14, 0.25 },
	{ 532, Color3.fromRGB(61, 71, 102), 17.8, 0.38 },
	{ 892, Color3.fromRGB(183, 163, 240), 15.5, 0.25 },
	{ 1252, Color3.fromRGB(13, 16, 36), 0, 0.12 },
}
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
