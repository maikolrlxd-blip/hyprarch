-- Ambiente apocaliptico del mapa (solo apariencia). Generado por tools/build_mapa_ensamble.py.
-- Uso: ModuleScript en ReplicatedStorage; desde un Script del servidor: require(ruta).aplicar()
-- (o pegado en la barra de comandos de Studio con Ambiente.aplicar() al final: los ajustes quedan guardados en el place).
local Lighting = game:GetService("Lighting")
local Ambiente = {}

Ambiente.Lighting = {
	-- media tarde: sol a unos 35 grados y en diagonal a las dos calles (acimut -50), asi no deslumbra al mirar por ellas
	ClockTime = 15.2,
	GeographicLatitude = 55,
	Brightness = 2.1,
	Ambient = Color3.fromRGB(70, 62, 55),
	OutdoorAmbient = Color3.fromRGB(120, 110, 100),
	ColorShift_Top = Color3.fromRGB(240, 205, 165),
	ColorShift_Bottom = Color3.fromRGB(58, 49, 43),
	EnvironmentDiffuseScale = 0.45,
	EnvironmentSpecularScale = 0.15,
	ExposureCompensation = -0.1,
	GlobalShadows = true,
}
-- cielo: sol pequeno y sin estrellas; el color lo pone la bruma (no hace falta subir texturas propias)
Ambiente.Sky = {SunAngularSize = 10, MoonAngularSize = 7, StarCount = 0, CelestialBodiesShown = true}
-- bruma de polvo gris-marron densa: tapa el azul del cielo por defecto y el horizonte se pierde (probado en Studio 2026-10-23)
Ambiente.Atmosphere = {Density = 0.5, Offset = 0.05, Color = Color3.fromRGB(188, 166, 134), Decay = Color3.fromRGB(118, 92, 66), Glare = 0, Haze = 4}
-- colores apagados y algo de contraste (estilo Poli Pintado: paleta sucia y mate); brillo bajo para que el sol no queme
Ambiente.ColorCorrection = {Brightness = -0.03, Contrast = 0.12, Saturation = -0.3, TintColor = Color3.fromRGB(255, 238, 216)}
Ambiente.Bloom = {Intensity = 0.12, Size = 18, Threshold = 2.2}
Ambiente.SunRays = {Intensity = 0.02, Spread = 0.4}

local function efecto(clase, nombre, props)
	local e = Lighting:FindFirstChild(nombre)
	if not e and (clase == "Sky" or clase == "Atmosphere") then
		e = Lighting:FindFirstChildOfClass(clase) -- solo puede haber uno: con dos, Roblox usa uno cualquiera
	end
	e = e or Instance.new(clase)
	e.Name = nombre
	for k, v in pairs(props) do
		e[k] = v
	end
	e.Parent = Lighting
	-- los efectos de la plantilla de Roblox (p. ej. un "Bloom" por defecto) se sumarian a estos: se apagan
	for _, o in ipairs(Lighting:GetChildren()) do
		if o ~= e and o.ClassName == clase and o:IsA("PostEffect") then
			o.Enabled = false
		end
	end
end

function Ambiente.aplicar()
	for k, v in pairs(Ambiente.Lighting) do
		Lighting[k] = v
	end
	efecto("Sky", "CieloPolvo", Ambiente.Sky)
	efecto("Atmosphere", "AtmosferaApocalipsis", Ambiente.Atmosphere)
	efecto("ColorCorrectionEffect", "ColorApocalipsis", Ambiente.ColorCorrection)
	efecto("BloomEffect", "BrilloApocalipsis", Ambiente.Bloom)
	efecto("SunRaysEffect", "RayosApocalipsis", Ambiente.SunRays)
end

return Ambiente
