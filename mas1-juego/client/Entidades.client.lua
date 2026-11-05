-- Enemigos y cofres de «+1 de lanzamiento por segundo» vistos en el cliente. El servidor solo pone anclas invisibles en
-- Workspace.MAS1_Entidades (atributos Tipo, Vivo y, en los cofres, Dueno); aqui cada una se dibuja, se mueve suave y se anima: los
-- enemigos flotan con cara enfadada mirando a +Z (por donde llega el jugador) y encogen al ser golpeados; el cofre de cada jugador
-- (solo lo ve el) aletea mientras huye. Los enemigos usan las mallas voxel de mas1-arte/enemigos-v02 si estan en
-- ReplicatedStorage.MAS1_Enemigos (assets/MAS1_Enemigos.rbxmx), con sus clips de Blender (src/ClipsEnemigos.lua): Idle en bucle con
-- parpadeos (Blink) y Defeat al derribarlos, antes de encoger. Si no estan, y para el cofre, piezas provisionales con esos colores.
local Players, RS, RunService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService")
local plr = Players.LocalPlayer
if not game:IsLoaded() then game.Loaded:Wait() end -- con todo replicado, las mallas y sus clips ya estan si existen
local Mas1 = RS:WaitForChild("Mas1")
local Clips = require(Mas1:WaitForChild("Clips"))
local moduloClips = Mas1:FindFirstChild("ClipsEnemigos")
local CLIPS = moduloClips and require(moduloClips) or {}
local MALLAS = RS:FindFirstChild("MAS1_Enemigos")
local ESCALA_MALLA = 2.2 -- las mallas miden de 2 a 4,5 studs: asi quedan como las piezas de antes (unos 9)
local GIRO_MALLA = CFrame.Angles(0, math.pi, 0) -- el frente de la malla es su -Z; el enemigo mira a +Z, al jugador que llega
local RETRASO_ENCOGER = 0.6 -- s: con malla, al derribarlo se ve un momento su Defeat antes de encoger
local CERCA = 320 -- studs: mas lejos no se anima (no se aprecia y ahorra trabajo)
local anclas = workspace:WaitForChild("MAS1_Entidades")
local vista = Instance.new("Folder")
vista.Name = "MAS1_EntidadesVista"
vista.Parent = workspace

local function rgb(h)
	h = h:gsub("#", "")
	return Color3.fromRGB(tonumber(h:sub(1, 2), 16), tonumber(h:sub(3, 4), 16), tonumber(h:sub(5, 6), 16))
end

local function pieza(m, forma, tam, cf, color, neon, transp)
	local p = forma == "Wedge" and Instance.new("WedgePart") or Instance.new("Part")
	if forma ~= "Wedge" then p.Shape = Enum.PartType[forma] end
	p.Size, p.CFrame, p.Color = tam, cf, rgb(color)
	p.Material = neon and Enum.Material.Neon or Enum.Material.SmoothPlastic
	p.Transparency = transp or 0
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, not neon
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = m
	return p
end

local GIRO = CFrame.Angles(0, 0, math.rad(90)) -- un cilindro de Roblox va a lo largo de X: asi queda de pie

local function cara(m, y, z, s) -- ojos pequeños con brillo y cejas enfadadas, mirando a +Z
	for _, x in ipairs({ -0.6, 0.6 }) do
		pieza(m, "Block", Vector3.new(0.45, 0.65, 0.2) * s, CFrame.new(x * s, y, z), "#1d1626")
		pieza(m, "Block", Vector3.new(0.18, 0.18, 0.22) * s, CFrame.new((x + 0.1) * s, y + 0.15 * s, z + 0.02), "#ffffff")
		pieza(m, "Block", Vector3.new(0.75, 0.18, 0.2) * s, CFrame.new(x * s, y + 0.62 * s, z) * CFrame.Angles(0, 0, x > 0 and 0.45 or -0.45), "#1d1626")
	end
	pieza(m, "Block", Vector3.new(0.9, 0.18, 0.2) * s, CFrame.new(0, y - 0.6 * s, z), "#1d1626") -- morro gruñon
end

local MODELOS = {
	nube = function(m)
		pieza(m, "Ball", Vector3.one * 4.6, CFrame.new(), "#f4f6ff")
		pieza(m, "Ball", Vector3.one * 3.4, CFrame.new(-2.6, -0.5, 0), "#e8ebfb")
		pieza(m, "Ball", Vector3.one * 3.4, CFrame.new(2.6, -0.5, 0), "#e8ebfb")
		cara(m, 0.2, 2.25, 1.3)
	end,
	nubarron = function(m)
		pieza(m, "Ball", Vector3.one * 4.8, CFrame.new(), "#7a86a8")
		pieza(m, "Ball", Vector3.one * 3.6, CFrame.new(-2.7, -0.5, 0), "#56607f")
		pieza(m, "Ball", Vector3.one * 3.6, CFrame.new(2.7, -0.5, 0), "#56607f")
		pieza(m, "Block", Vector3.new(0.6, 2.4, 0.4), CFrame.new(-0.3, -3.2, 0) * CFrame.Angles(0, 0, 0.5), "#ffd23f", true)
		pieza(m, "Block", Vector3.new(0.6, 2.4, 0.4), CFrame.new(0.2, -4.9, 0) * CFrame.Angles(0, 0, -0.5), "#ffd23f", true)
		cara(m, 0.2, 2.35, 1.3)
	end,
	globo = function(m)
		pieza(m, "Ball", Vector3.one * 4.4, CFrame.new(), "#ff5d6c")
		pieza(m, "Ball", Vector3.one * 0.7, CFrame.new(0, -2.3, 0), "#e04a58")
		pieza(m, "Cylinder", Vector3.new(3, 0.12, 0.12), CFrame.new(0, -4, 0) * GIRO, "#ffffff")
		cara(m, 0.3, 2.1, 1.2)
	end,
	cometa = function(m)
		pieza(m, "Block", Vector3.new(4, 4, 0.4), CFrame.Angles(0, 0, math.rad(45)), "#ff6b5a")
		pieza(m, "Block", Vector3.new(2.2, 2.2, 0.44), CFrame.new(0, 0.9, 0) * CFrame.Angles(0, 0, math.rad(45)), "#ffd23f")
		for k, c in ipairs({ "#ff6b5a", "#ffd23f", "#ff6b5a" }) do
			pieza(m, "Block", Vector3.one * 0.7, CFrame.new((k % 2 == 0) and 0.4 or -0.3, -2.6 - k, 0) * CFrame.Angles(0, 0, 0.4 * k), c)
		end
		cara(m, -0.2, 0.3, 1.0)
	end,
	ovni = function(m)
		pieza(m, "Cylinder", Vector3.new(1.2, 7, 7), GIRO, "#7c5cff")
		pieza(m, "Ball", Vector3.one * 2.8, CFrame.new(0, 0.9, 0), "#bdeaff", false, 0.35)
		pieza(m, "Ball", Vector3.one * 1.7, CFrame.new(0, 1.0, 0), "#6cd36c")
		for k = 0, 5 do
			local a = k * math.pi / 3
			pieza(m, "Ball", Vector3.one * 0.6, CFrame.new(math.cos(a) * 3.2, -0.1, math.sin(a) * 3.2), "#ffe14d", true)
		end
		cara(m, 1.05, 0.85, 0.55)
	end,
	meteorito = function(m)
		pieza(m, "Block", Vector3.new(3.6, 3.2, 3.4), CFrame.Angles(0.4, 0.6, 0.2), "#4a4359")
		pieza(m, "Block", Vector3.new(2.6, 2.8, 2.6), CFrame.new(0.6, 0.4, -0.5) * CFrame.Angles(-0.3, 0.2, 0.5), "#605670")
		pieza(m, "Wedge", Vector3.new(1.2, 2.6, 3.4), CFrame.new(-0.5, 1.6, -2.4) * CFrame.Angles(0.6, 0, 0), "#ff9d00", true)
		pieza(m, "Wedge", Vector3.new(0.9, 2.0, 2.6), CFrame.new(0.7, 1.4, -2.2) * CFrame.Angles(0.8, 0, 0), "#ff3d00", true)
		cara(m, 0.1, 2.05, 1.1)
	end,
	cofre = function(m)
		pieza(m, "Block", Vector3.new(3.4, 2.2, 2.4), CFrame.new(), "#8a5a34")
		pieza(m, "Block", Vector3.new(3.5, 0.8, 2.5), CFrame.new(0, 1.45, 0), "#a8703f")
		pieza(m, "Block", Vector3.new(0.5, 3.1, 2.6), CFrame.new(0, 0.4, 0), "#ffc42e")
		pieza(m, "Block", Vector3.new(0.7, 0.8, 0.3), CFrame.new(0, 0.6, 1.3), "#ffd23f", true)
		for _, s in ipairs({ -1, 1 }) do -- alas que aletean (las mueve el bucle de abajo)
			local ala = pieza(m, "Wedge", Vector3.new(0.3, 1.8, 3.2), CFrame.new(s * 2.4, 0.6, 0) * CFrame.Angles(0, 0, s * 0.3), "#ffffff")
			ala.Name = s < 0 and "AlaIzq" or "AlaDer"
		end
	end,
}

-- [ancla] = { m, pos (suavizada), fase, alas, escala (1 = vivo), tam, giro, partes, huesos y clips (con malla), golpe, parpadeo }
local vistos = {}

local function crear(a)
	local tipo = a:GetAttribute("Tipo") or ""
	local malla = tipo ~= "cofre" and MALLAS and MALLAS:FindFirstChild(tipo)
	if (not malla and not MODELOS[tipo]) or vistos[a] then return end
	if tipo == "cofre" and a:GetAttribute("Dueno") ~= plr.UserId then return end -- cada uno ve solo su cofre
	local m
	if malla then
		m = malla:Clone()
	else
		m = Instance.new("Model")
		MODELOS[tipo](m)
		m.WorldPivot = CFrame.new() -- las piezas se hacen alrededor del origen: PivotTo y ScaleTo trabajan desde ahi
	end
	m.Name = tipo
	local partes = {}
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then
			p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
			partes[#partes + 1] = p
		end
	end
	m.Parent = vista
	local alas = {}
	for _, n in ipairs({ "AlaIzq", "AlaDer" }) do
		local p = m:FindFirstChild(n)
		if p then alas[#alas + 1] = { p = p, base = p.CFrame, s = n == "AlaIzq" and -1 or 1 } end
	end
	vistos[a] = {
		m = m, pos = a.Position, fase = math.random() * 6.28, alas = alas, escala = 1, partes = partes,
		tam = malla and ESCALA_MALLA or 1, giro = malla and GIRO_MALLA or CFrame.identity,
		huesos = malla and Clips.huesos(m), clips = malla and Clips.preparar(CLIPS[tipo]),
		parpadeo = os.clock() + 1 + math.random() * 3,
	}
end

local function quitar(a)
	local v = vistos[a]
	if v then
		v.m:Destroy()
		vistos[a] = nil
	end
end

for _, a in ipairs(anclas:GetChildren()) do crear(a) end
anclas.ChildAdded:Connect(crear)
anclas.ChildRemoved:Connect(quitar)

local camara = workspace.CurrentCamera

RunService.RenderStepped:Connect(function(dt)
	local t = os.clock()
	local ojo = camara.CFrame.Position
	for a, v in pairs(vistos) do
		v.pos = v.pos:Lerp(a.Position, 1 - math.exp(-12 * dt)) -- los cofres se mueven: suave aunque el servidor mande a saltos
		local vivo = a:GetAttribute("Vivo") ~= false
		if vivo then v.golpe = nil elseif not v.golpe then v.golpe = t end -- golpe = cuando lo derribaron
		-- golpeado: encoge hasta desaparecer y vuelve al reaparecer
		local objetivo = (vivo or (v.huesos and t - v.golpe < RETRASO_ENCOGER)) and 1 or 0.05
		v.escala += (objetivo - v.escala) * (1 - math.exp(-10 * dt))
		local cf = CFrame.new(v.pos + Vector3.new(0, math.sin(t * 2 + v.fase) * 0.6, 0)) * CFrame.Angles(0, math.sin(t + v.fase) * 0.15, 0)
		local escala = math.max(0.05, v.escala) * v.tam
		if math.abs(v.m:GetScale() - escala) > 0.01 then v.m:ScaleTo(escala) end
		v.m:PivotTo(cf * v.giro)
		for _, ala in ipairs(v.alas) do
			ala.p.CFrame = cf * ala.base * CFrame.Angles(0, 0, ala.s * math.sin(t * 14) * 0.6)
		end
		if v.clips and (v.pos - ojo).Magnitude < CERCA then
			local e = v.m:GetScale()
			if v.golpe then
				Clips.aplicar(v.huesos, v.clips.Defeat, t - v.golpe, e, false)
			else
				Clips.aplicar(v.huesos, v.clips.Idle, t + v.fase, e, true)
				local parpado = v.clips.Blink
				if parpado and t >= v.parpadeo then
					Clips.aplicar(v.huesos, parpado, t - v.parpadeo, e, false, true)
					if t - v.parpadeo > parpado.dur then v.parpadeo = t + 2 + math.random() * 3 end
				end
			end
		end
		for _, p in ipairs(v.partes) do
			p.LocalTransparencyModifier = v.escala < 0.08 and 1 or 0
		end
	end
end)
