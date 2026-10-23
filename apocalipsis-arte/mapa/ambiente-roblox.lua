-- Ambiente apocaliptico del mapa (solo apariencia). Generado por tools/build_mapa_ensamble.py.
-- Uso: ModuleScript en ReplicatedStorage; desde un Script del servidor: require(ruta).aplicar()
local Lighting = game:GetService("Lighting")
local Ambiente = {}

Ambiente.Lighting = {
	ClockTime = 17.4,                 -- tarde baja: sombras largas y luz calida
	GeographicLatitude = 38,
	Brightness = 2.3,
	Ambient = Color3.fromRGB(70, 62, 55),
	OutdoorAmbient = Color3.fromRGB(124, 113, 101),
	ColorShift_Top = Color3.fromRGB(255, 208, 160),
	ColorShift_Bottom = Color3.fromRGB(58, 49, 43),
	EnvironmentDiffuseScale = 0.45,
	EnvironmentSpecularScale = 0.15,
	ExposureCompensation = -0.1,
	GlobalShadows = true,
}
-- bruma de polvo: el horizonte se pierde en marron grisaceo
Ambiente.Atmosphere = {Density = 0.38, Offset = 0.15, Color = Color3.fromRGB(199, 180, 154), Decay = Color3.fromRGB(112, 84, 62), Glare = 0.12, Haze = 2.4}
-- colores apagados y algo de contraste (estilo Poli Pintado: paleta sucia y mate)
Ambiente.ColorCorrection = {Brightness = -0.02, Contrast = 0.10, Saturation = -0.28, TintColor = Color3.fromRGB(255, 244, 228)}
Ambiente.Bloom = {Intensity = 0.3, Size = 26, Threshold = 1.7}
Ambiente.SunRays = {Intensity = 0.05, Spread = 0.55}

local function efecto(clase, nombre, props)
	local e = Lighting:FindFirstChild(nombre) or Instance.new(clase)
	e.Name = nombre
	for k, v in pairs(props) do
		e[k] = v
	end
	e.Parent = Lighting
end

function Ambiente.aplicar()
	for k, v in pairs(Ambiente.Lighting) do
		Lighting[k] = v
	end
	efecto("Atmosphere", "AtmosferaApocalipsis", Ambiente.Atmosphere)
	efecto("ColorCorrectionEffect", "ColorApocalipsis", Ambiente.ColorCorrection)
	efecto("BloomEffect", "BrilloApocalipsis", Ambiente.Bloom)
	efecto("SunRaysEffect", "RayosApocalipsis", Ambiente.SunRays)
end

return Ambiente
