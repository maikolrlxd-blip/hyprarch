-- Apariencia BASE de todos los jugadores de Luto (decision de Maikol): NO se usa la skin/avatar de Roblox. Manos y mangas iguales a las de los
-- viewmodels de las armas (mangas verde oliva, manos color piel apagado). La creacion de personaje (colores, ojos, altura...) queda para despues:
-- bastara con sustituir BASE por lo que el jugador elija. Modulo con API de Roblox (se usa solo en el servidor). SIN PROBAR EN STUDIO.
local Apariencia = {}

Apariencia.BASE = {
	piel = { 107, 90, 68 }, manga = { 75, 81, 54 }, torso = { 66, 72, 48 }, pantalon = { 52, 50, 46 }, zapato = { 32, 30, 28 }, -- iguales a los viewmodels de Blender
}

local function c(t) return Color3.fromRGB(t[1], t[2], t[3]) end

local PARTES = {
	Head = "piel", LeftHand = "piel", RightHand = "piel",
	UpperTorso = "torso", LowerTorso = "torso",
	LeftUpperArm = "manga", LeftLowerArm = "manga", RightUpperArm = "manga", RightLowerArm = "manga",
	LeftUpperLeg = "pantalon", LeftLowerLeg = "pantalon", RightUpperLeg = "pantalon", RightLowerLeg = "pantalon",
	LeftFoot = "zapato", RightFoot = "zapato",
}

-- Quita ropa, accesorios y colores del avatar y pinta el cuerpo base. Llamar con el personaje ya cargado.
function Apariencia.aplicar(char, base)
	base = base or Apariencia.BASE
	local hum = char:FindFirstChildOfClass("Humanoid"); if not hum then return end
	pcall(function() hum:ApplyDescription(Instance.new("HumanoidDescription")) end) -- descripcion vacia: sin ropa ni accesorios del avatar
	for _, d in ipairs(char:GetChildren()) do
		if d:IsA("Accessory") or d:IsA("Shirt") or d:IsA("Pants") or d:IsA("ShirtGraphic") or d:IsA("BodyColors") then d:Destroy() end
	end
	for nombre, clave in pairs(PARTES) do
		local p = char:FindFirstChild(nombre)
		if p and p:IsA("BasePart") then p.Color = c(base[clave]); p.Material = Enum.Material.SmoothPlastic end
	end
end

return Apariencia
