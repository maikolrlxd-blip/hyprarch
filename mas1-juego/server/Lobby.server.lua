-- Lobby de «+1 de lanzamiento por segundo» (PROVISIONAL, hecho con piezas hasta importar la Pradera de Codex): plaza de salida, el
-- CAÑON con su plataforma de lanzamiento (MAS1_Canon, que lee Partida.server.lua), zonas de entrenamiento (MAS1_AFK y MAS1_Entreno),
-- el punto de aparicion y carteles. Todo en Workspace.MAS1_Lobby. El vuelo sale hacia -Z; el lobby ocupa Z de +24 a -172, sobre
-- la misma altura del carril (techo en Y = 0). SIN PROBAR EN STUDIO.
local Lighting = game:GetService("Lighting")
local viejo = workspace:FindFirstChild("MAS1_Lobby")
if viejo then viejo:Destroy() end
local lobby = Instance.new("Folder")
lobby.Name = "MAS1_Lobby"

local function rgb(r, g, b) return Color3.fromRGB(r, g, b) end
local CRE, TIN, SOL, CIE, MEN, ROS, VIO = rgb(255, 247, 224), rgb(28, 21, 48), rgb(255, 210, 63), rgb(78, 200, 255), rgb(61, 220, 151), rgb(255, 93, 143), rgb(124, 92, 255)

local function parte(nombre, tam, cf, color, material, opciones)
	local p = Instance.new("Part")
	p.Name, p.Size, p.CFrame, p.Color = nombre, tam, cf, color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Anchored, p.TopSurface, p.BottomSurface = true, Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	for k, v in pairs(opciones or {}) do p[k] = v end
	p.Parent = lobby
	return p
end

local function cartel(texto, pos, ancho, color) -- tablero con letras, mirando a +Z (hacia quien aparece en la plaza); no se montan de lado
	local alto = math.max(ancho * 0.22, 3)
	local p = parte("Cartel", Vector3.new(ancho, alto, 0.6), CFrame.new(pos), TIN, nil, { CanCollide = false, CanQuery = false })
	local g = Instance.new("SurfaceGui")
	g.Face, g.SizingMode, g.PixelsPerStud = Enum.NormalId.Back, Enum.SurfaceGuiSizingMode.PixelsPerStud, 50
	g.Parent = p
	local t = Instance.new("TextLabel")
	t.Size, t.BackgroundTransparency, t.Text = UDim2.fromScale(1, 1), 1, texto
	t.Font, t.TextScaled, t.TextColor3 = Enum.Font.FredokaOne, true, color or SOL
	t.TextStrokeColor3, t.TextStrokeTransparency = TIN, 0.5
	t.Parent = g
end

-- suelo de toda la plaza (justo por debajo del techo del carril para no pelear con el mapa donde ya haya suelo)
parte("Suelo", Vector3.new(70, 2, 196), CFrame.new(0, -1.05, -74), rgb(120, 205, 110), Enum.Material.Grass)
for _, x in ipairs({ -33, 33 }) do
	parte("Borde", Vector3.new(2, 1.2, 196), CFrame.new(x, 0.1, -74), CRE, nil, { CanCollide = true })
end
-- franjas guia hacia el cañon y el carril
for z = 0, -170, -20 do
	parte("Franja", Vector3.new(3, 0.1, 8), CFrame.new(0, 0.02, z), CRE, nil, { CanCollide = false, CanQuery = false })
end

-- CAÑON: base, tubo inclinado hacia -Z y boca dorada, con la plataforma MAS1_Canon delante (de donde sale el jugador)
local cz = -22
parte("CanonBase", Vector3.new(14, 3, 14), CFrame.new(0, 1.5, cz), rgb(150, 70, 60))
parte("CanonRueda", Vector3.new(3, 8, 8), CFrame.new(-7.5, 4, cz) * CFrame.Angles(0, 0, 0), TIN, nil, { Shape = Enum.PartType.Cylinder })
parte("CanonRueda", Vector3.new(3, 8, 8), CFrame.new(7.5, 4, cz), TIN, nil, { Shape = Enum.PartType.Cylinder })
local tubo = parte("CanonTubo", Vector3.new(7, 7, 18), CFrame.new(0, 7, cz) * CFrame.Angles(math.rad(28), 0, 0), ROS)
parte("CanonAro", Vector3.new(8.5, 8.5, 2.2), tubo.CFrame * CFrame.new(0, 0, -9), SOL)
parte("CanonAro", Vector3.new(8.5, 8.5, 2.2), tubo.CFrame * CFrame.new(0, 0, 5), SOL)
parte("CanonBoca", Vector3.new(5, 5, 0.6), tubo.CFrame * CFrame.new(0, 0, -9.6), TIN)
local plat = parte("MAS1_Canon", Vector3.new(10, 1, 10), CFrame.new(0, 0.5, cz - 16), CIE, Enum.Material.Neon)
cartel("¡CAÑÓN!", Vector3.new(0, 16, cz + 4), 14, SOL)

-- el aviso del cañon: se acerca el jugador y pulsa E / toca (el cliente manda "lanzar")
local pp = Instance.new("ProximityPrompt")
pp.ActionText, pp.ObjectText, pp.HoldDuration, pp.MaxActivationDistance, pp.RequiresLineOfSight = "LANZARSE", "Cañón", 0, 14, false
pp.Parent = plat

-- arco de entrada y cartel del juego
for _, x in ipairs({ -14, 14 }) do parte("ArcoPilar", Vector3.new(3, 22, 3), CFrame.new(x, 11, -4), VIO) end
parte("ArcoDintel", Vector3.new(34, 4, 3), CFrame.new(0, 22, -4), VIO)
cartel("+1 DE LANZAMIENTO", Vector3.new(0, 26.5, -3.5), 30, SOL)

-- zonas de entrenamiento (las lee Partida.server.lua por el nombre)
local afk = parte("MAS1_AFK", Vector3.new(16, 0.4, 16), CFrame.new(-20, 0.2, -62), CIE, Enum.Material.Neon, { CanCollide = false })
local entreno = parte("MAS1_Entreno", Vector3.new(16, 0.4, 16), CFrame.new(20, 0.2, -62), rgb(255, 157, 0), Enum.Material.Neon, { CanCollide = false })
cartel("ZONA AFK  x1,5", Vector3.new(-20, 7, -70), 14, CIE)
cartel("ENTRENA CORRIENDO  x2", Vector3.new(20, 7, -70), 16, rgb(255, 157, 0))

-- puestos: huevos (B) y rebirth, solo decorativos; el menu lo abre el boton o la tecla
for _, d in ipairs({ { "HUEVOS Y MASCOTAS (B)", -20, MEN }, { "REBIRTH", 20, ROS } }) do
	parte("Puesto", Vector3.new(10, 5, 6), CFrame.new(d[2], 2.5, -100), d[3])
	parte("PuestoTecho", Vector3.new(12, 1, 8), CFrame.new(d[2], 7, -100), TIN)
	cartel(d[1], Vector3.new(d[2], 11, -96.5), 18, d[3])
end

-- punto de aparicion en la plaza, mirando al cañon; se apaga el de la place de prueba (estaba en el Mar de Nubes)
for _, s in ipairs(workspace:GetDescendants()) do
	if s:IsA("SpawnLocation") and s.Parent ~= lobby then s.Enabled = false end
end
local sp = Instance.new("SpawnLocation")
sp.Size, sp.CFrame, sp.Anchored, sp.Duration, sp.Neutral = Vector3.new(10, 1, 10), CFrame.new(0, 0.5, 14), true, 0, true
sp.Transparency, sp.Color, sp.Material = 0.4, MEN, Enum.Material.Neon
sp.Parent = lobby

lobby.Parent = workspace
Lighting.Brightness = math.max(Lighting.Brightness, 2)
