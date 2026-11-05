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

-- CAÑON apuntando a -Z, con la plataforma MAS1_Canon delante (de donde sale el jugador). Es el «Cañón pajarero» de Codex
-- (ReplicatedStorage.MAS1_Equipo.Canon: mide 3,8 x 5,7 x 4,8 studs, aquí x3) y, si no está, el provisional de piezas
local cz = -22
local ESCALA_CANON = 3
local equipo = game:GetService("ReplicatedStorage"):FindFirstChild("MAS1_Equipo")
local plantillaCanon = equipo and equipo:FindFirstChild("Canon")
if plantillaCanon then
	local canon = plantillaCanon:Clone()
	canon.Name = "CanonPajarero"
	canon:ScaleTo(ESCALA_CANON)
	canon:PivotTo(CFrame.new(0, 0, cz)) -- el pivote es el centro del suelo bajo el cañón, con la boca hacia -Z
	for _, d in ipairs(canon:GetDescendants()) do
		if d:IsA("BasePart") then d.Anchored = true end
	end
	canon.Parent = lobby
else
	parte("CanonBase", Vector3.new(14, 3, 14), CFrame.new(0, 1.5, cz), rgb(150, 70, 60))
	parte("CanonRueda", Vector3.new(3, 8, 8), CFrame.new(-7.5, 4, cz), TIN, nil, { Shape = Enum.PartType.Cylinder })
	parte("CanonRueda", Vector3.new(3, 8, 8), CFrame.new(7.5, 4, cz), TIN, nil, { Shape = Enum.PartType.Cylinder })
	local tubo = parte("CanonTubo", Vector3.new(7, 7, 18), CFrame.new(0, 7, cz) * CFrame.Angles(math.rad(28), 0, 0), ROS)
	parte("CanonAro", Vector3.new(8.5, 8.5, 2.2), tubo.CFrame * CFrame.new(0, 0, -9), SOL)
	parte("CanonAro", Vector3.new(8.5, 8.5, 2.2), tubo.CFrame * CFrame.new(0, 0, 5), SOL)
	parte("CanonBoca", Vector3.new(5, 5, 0.6), tubo.CFrame * CFrame.new(0, 0, -9.6), TIN)
end
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

-- vida en la plaza (cola del director, 05/11: «farolas, banderines, arboles de bloques»). Todo decorativo y fuera del camino central
-- (x = 0), del cañon (z -16 a -28), de la plataforma (z -33 a -43), de las zonas de entreno (|x| 12 a 28, z -54 a -70) y de los
-- puestos (|x| 14 a 26, z -96 a -104): farolas en x = ±9, banderines colgando entre ellas por encima del camino y arboles en x = ±30.
-- Solo chocan los postes y los troncos. SIN PROBAR EN STUDIO.
local MADERA, HOJA, HOJA2, FAROL = rgb(122, 84, 52), rgb(76, 175, 80), rgb(56, 142, 60), rgb(255, 226, 160)
local SIN_CHOQUE = { CanCollide = false, CanQuery = false }
for _, z in ipairs({ 6, -10, -46, -62, -78, -94, -110, -126, -142, -158 }) do
	for _, x in ipairs({ -9, 9 }) do
		parte("FarolaBase", Vector3.new(1.4, 0.6, 1.4), CFrame.new(x, 0.3, z), TIN)
		parte("FarolaPoste", Vector3.new(9, 0.5, 0.5), CFrame.new(x, 4.5, z) * CFrame.Angles(0, 0, math.rad(90)), TIN, nil,
			{ Shape = Enum.PartType.Cylinder })
		local farol = parte("Farol", Vector3.new(1.3, 1.6, 1.3), CFrame.new(x, 9.6, z), FAROL, Enum.Material.Neon, SIN_CHOQUE)
		parte("FarolTecho", Vector3.new(1.8, 0.4, 1.8), CFrame.new(x, 10.6, z), TIN, nil, SIN_CHOQUE)
		local luz = Instance.new("PointLight")
		luz.Range, luz.Brightness, luz.Color, luz.Shadows = 16, 1.2, FAROL, false
		luz.Parent = farol
	end
end
local COLORES_BANDERIN = { SOL, ROS, CIE, MEN, VIO }
for k, z in ipairs({ 6, -46, -78, -110, -142 }) do -- de farola a farola, con caida en el medio
	local n, previo = 11, nil
	for i = 0, n - 1 do
		local u = i / (n - 1)
		local punto = Vector3.new(-8.4 + 16.8 * u, 8.9 - 1.4 * (1 - (2 * u - 1) ^ 2), z)
		if previo then
			parte("Cuerda", Vector3.new(0.08, 0.08, (punto - previo).Magnitude), CFrame.lookAt((punto + previo) / 2, punto), CRE, nil, SIN_CHOQUE)
		end
		parte("Banderin", Vector3.new(0.9, 0.9, 0.08), CFrame.new(punto - Vector3.new(0, 0.6, 0)) * CFrame.Angles(0, 0, math.rad(45)),
			COLORES_BANDERIN[(i + k) % #COLORES_BANDERIN + 1], nil, SIN_CHOQUE)
		previo = punto
	end
end
local function arbol(x, z, s) -- tronco y dos cubos de copa, como los de la Pradera
	parte("Tronco", Vector3.new(1.4, 4.5, 1.4) * s, CFrame.new(x, 2.25 * s, z), MADERA)
	parte("Copa", Vector3.new(5, 3.6, 5) * s, CFrame.new(x, 6.1 * s, z), HOJA, nil, SIN_CHOQUE)
	parte("Copa", Vector3.new(3.4, 2.4, 3.4) * s, CFrame.new(x + 0.3 * s, 8.4 * s, z - 0.2 * s), HOJA2, nil, SIN_CHOQUE)
end
for _, z in ipairs({ 16, -14, -40, -86, -116, -136, -156 }) do
	arbol(-30, z, 1 + (z * 7 % 3) * 0.12)
	arbol(30, z + 6, 1 + (z * 5 % 3) * 0.12)
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
