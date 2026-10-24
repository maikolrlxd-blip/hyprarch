-- PROVISIONAL y SIN PROBAR EN STUDIO. Servidor de la partida de Luto: arena simple, jugadores, oleadas de zombis (rigs R15 verdes, IA de perseguir),
-- tienda con ProximityPrompt, reaparicion y fin de partida. La logica vive en src/Partida, Oleadas y Tienda (probadas en Lua puro).
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local SS = game:GetService("ServerStorage")
local Collection = game:GetService("CollectionService")
local Debris = game:GetService("Debris")
local PFS = game:GetService("PathfindingService")
local Lighting = game:GetService("Lighting")
local Luto = RS:WaitForChild("Luto")
local Partida, Tienda, Animaciones = require(Luto.Partida), require(Luto.Tienda), require(Luto.Animaciones)
local Apariencia = require(Luto.Apariencia)

Players.CharacterAutoLoads = false
local SEED = tonumber(workspace:GetAttribute("LUTO_Seed")) or 1234
local partida = Partida.new(SEED)
local R = Instance.new("RemoteEvent"); R.Name = "LUTO_Partida"; R.Parent = RS
local function now() return workspace:GetServerTimeNow() end

-- ===== Plantillas hechas en Blender (se importan a Studio; ver apocalipsis-juego/INTEGRACION.md) =====
-- ServerStorage.LUTO_Plantillas puede contener: Mapa, Zombi_Mujer, Jefe_lamentadora, Jefe_alta. Si falta alguna se usa un sustituto provisional.
local plantillas = SS:FindFirstChild("LUTO_Plantillas")
local function plantilla(nombre) return plantillas and plantillas:FindFirstChild(nombre) end

local arena = Instance.new("Folder"); arena.Name = "LUTO_Arena"; arena.Parent = workspace
local function bloque(nombre, tam, pos, color)
	local p = Instance.new("Part"); p.Name = nombre; p.Size = tam; p.Position = pos; p.Anchored = true; p.Color = color
	p.Material = Enum.Material.Concrete; p.Parent = arena; return p
end

local mapa = nil           -- Model clonado de la plantilla (si existe)
local puntosZombi = {}     -- posiciones de aparicion de los zombis
local puntoJugadores = Vector3.new(0, 4, 0)
if plantilla("Mapa") then
	mapa = plantilla("Mapa"):Clone(); mapa.Name = "LUTO_Mapa"; mapa.Parent = workspace
	local sj = mapa:FindFirstChild("SpawnJugadores", true); if sj then puntoJugadores = sj.Position + Vector3.new(0, 4, 0) end
	local sz = mapa:FindFirstChild("SpawnZombis", true)
	if sz then for _, c in ipairs(sz:GetChildren()) do if c:IsA("BasePart") then puntosZombi[#puntosZombi + 1] = c.Position + Vector3.new(0, 4, 0) end end end
else
	bloque("Suelo", Vector3.new(420, 2, 420), Vector3.new(0, -1, 0), Color3.fromRGB(70, 72, 68))
	for _, w in ipairs({ { Vector3.new(420, 16, 2), Vector3.new(0, 8, 210) }, { Vector3.new(420, 16, 2), Vector3.new(0, 8, -210) },
		{ Vector3.new(2, 16, 420), Vector3.new(210, 8, 0) }, { Vector3.new(2, 16, 420), Vector3.new(-210, 8, 0) } }) do
		bloque("Muro", w[1], w[2], Color3.fromRGB(50, 50, 52))
	end
	Lighting.ClockTime = 17; Lighting.Brightness = 2; Lighting.OutdoorAmbient = Color3.fromRGB(120, 115, 105) -- tarde polvorienta (provisional)
end

-- ===== Tienda (ProximityPrompt) =====
local TIENDAS = { { item = "municion", pos = Vector3.new(-8, 1.5, -14), color = Color3.fromRGB(190, 160, 70) },
	{ item = "curar", pos = Vector3.new(8, 1.5, -14), color = Color3.fromRGB(80, 170, 100) } }
local prompts = {}
for _, t in ipairs(TIENDAS) do
	local b = mapa and mapa:FindFirstChild("Tienda_" .. t.item, true) or nil -- marcador del mapa de Blender (Part)
	if b and not b:IsA("BasePart") then b = b:FindFirstChildWhichIsA("BasePart", true) end
	b = b or bloque("Tienda_" .. t.item, Vector3.new(4, 3, 4), t.pos, t.color)
	local pp = Instance.new("ProximityPrompt"); pp.Style = Enum.ProximityPromptStyle.Custom; pp.HoldDuration = 0.3; pp.MaxActivationDistance = 10; pp.RequiresLineOfSight = false
	pp.ObjectText = (t.item == "municion") and "Munición" or "Curación"; pp.ActionText = "Comprar · " .. Tienda.precio(t.item, 1); pp.Parent = b
	prompts[t.item] = pp
end

-- ===== Jugadores =====
local porId = {}
local finPartida -- se define mas abajo
local function viva(plr)
	local c = plr.Character; local h = c and c:FindFirstChildOfClass("Humanoid"); return h and h.Health > 0 and h:GetState() ~= Enum.HumanoidStateType.Dead and c:FindFirstChild("HumanoidRootPart") or nil
end
local function mensaje(plr, texto) R:FireClient(plr, { msg = texto }) end
local function avisarTodos(texto) R:FireAllClients({ msg = texto }) end

local function cargar(plr, indice)
	task.spawn(function()
		plr:LoadCharacter()
		local ch = plr.Character or plr.CharacterAdded:Wait()
		local root = ch:WaitForChild("HumanoidRootPart", 5)
		if root then ch:PivotTo(CFrame.new(puntoJugadores + Vector3.new(((indice or 1) - 2.5) * 5, 0, 0))) end
		pcall(Apariencia.aplicar, ch) -- cuerpo base de Luto (sin la skin de Roblox del jugador)
		local hum = ch:FindFirstChildOfClass("Humanoid")
		if hum then
			hum.Died:Connect(function()
				local r = partida:jugadorMuerto(plr.UserId, now())
				avisarTodos(plr.Name .. " ha caido")
				if r.fin then finPartida(r) end
			end)
		end
	end)
end

local function agregarJugador(plr)
	if partida:addPlayer(plr.UserId) then
		porId[plr.UserId] = plr
		if partida.estado == "ronda" or partida.estado == "intermision" then cargar(plr, #partida.order) end
	else plr:SetAttribute("LUTO_Espectador", true) end
end
Players.PlayerAdded:Connect(agregarJugador)
for _, plr in ipairs(Players:GetPlayers()) do agregarJugador(plr) end

-- ===== Zombis =====
local vivosZ = 0
local function colorear(modelo, jefe)
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("BasePart") then d.Color = jefe and Color3.fromRGB(110, 90, 120) or Color3.fromRGB(122, 140, 112); d.Material = Enum.Material.SmoothPlastic end
	end
end

-- Carga las pistas de animacion (si ya hay ids publicados en src/Animaciones.lua)
-- Prioridades para que Reposo no se mezcle con Caminar/Atacar (prueba en Studio)
local PRIORIDAD = { Reposo = Enum.AnimationPriority.Idle, Caminar = Enum.AnimationPriority.Movement, Atacar = Enum.AnimationPriority.Action, Caer = Enum.AnimationPriority.Action2 }
local function cargarAnimaciones(hum, clave)
	local conj = Animaciones[clave] or Animaciones.zombi
	local animator = hum:FindFirstChildOfClass("Animator") or Instance.new("Animator", hum)
	local pistas = {}
	for nombre, id in pairs(conj) do
		if id ~= "" then
			local a = Instance.new("Animation"); a.AnimationId = id
			local ok, pista = pcall(function() return animator:LoadAnimation(a) end)
			if ok then pista.Priority = PRIORIDAD[nombre] or pista.Priority; pistas[nombre] = pista end
		end
	end
	if pistas.Caminar then pistas.Caminar.Looped = true end
	if pistas.Reposo then pistas.Reposo.Looped = true end
	return pistas
end

local function crearZombi(cfg, esJefe)
	local j0 = cfg.jefe
	local molde = esJefe and (plantilla("Jefe_" .. j0.tipo) or plantilla("Zombi_Mujer")) or plantilla("Zombi_Mujer")
	local ok, modelo
	if molde then ok, modelo = true, molde:Clone()
	else
		ok, modelo = pcall(function()
			return Players:CreateHumanoidModelFromDescription(Instance.new("HumanoidDescription"), Enum.HumanoidRigType.R15)
		end)
	end
	if not ok or not modelo then
		warn("LUTO: no se pudo crear el zombi: " .. tostring(modelo)); partida:zombiMuerto(nil, esJefe, now()); return
	end
	local hum = modelo:FindFirstChildOfClass("Humanoid")
	if not hum then hum = Instance.new("Humanoid"); hum.RigType = Enum.HumanoidRigType.R15; hum.Parent = modelo end
	if not modelo.PrimaryPart then modelo.PrimaryPart = modelo:FindFirstChild("HumanoidRootPart") end
	local j = cfg.jefe
	modelo.Name = esJefe and "Jefe" or "Zombi"; if not molde then colorear(modelo, esJefe) end -- con plantilla de Blender se respeta su textura pintada
	hum.MaxHealth = esJefe and j.hp or cfg.hp; hum.Health = hum.MaxHealth; hum.WalkSpeed = esJefe and j.velocidad or cfg.velocidad
	hum.NameDisplayDistance = esJefe and 80 or 0; hum.HealthDisplayDistance = esJefe and 80 or 20 -- sin carteles amontonados con muchas zombis
	hum.BreakJointsOnDeath = false -- para que se vea la animacion Caer en vez de desarmarse
	hum.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOn; hum.DisplayName = esJefe and "LA " .. string.upper(j.tipo) or "Zombi"
	Collection:AddTag(modelo, "Zombi"); modelo:SetAttribute("Jefe", esJefe)
	if esJefe and not plantilla("Jefe_" .. j.tipo) then modelo:ScaleTo(j.escala) end
	if #puntosZombi > 0 then
		-- elegir un punto de aparicion LEJOS de los jugadores (>= 100 studs; si no hay, el mas lejano)
		local mejorP, mejorD = nil, -1
		local candidatos = {}
		for _, pt in ipairs(puntosZombi) do
			local dmin = math.huge
			for _, plr in ipairs(Players:GetPlayers()) do local rp = viva(plr); if rp then dmin = math.min(dmin, (rp.Position - pt).Magnitude) end end
			if dmin >= 100 then candidatos[#candidatos + 1] = pt end
			if dmin > mejorD then mejorP, mejorD = pt, dmin end
		end
		modelo:PivotTo(CFrame.new(#candidatos > 0 and candidatos[math.random(1, #candidatos)] or mejorP))
	else local ang = math.random() * 2 * math.pi; local r = 150 + math.random() * 40; modelo:PivotTo(CFrame.new(math.cos(ang) * r, 4, math.sin(ang) * r)) end
	modelo.Parent = workspace
	local root = modelo:FindFirstChild("HumanoidRootPart"); if root then pcall(function() root:SetNetworkOwner(nil) end) end
	vivosZ = vivosZ + 1
	local dano = esJefe and j.dano or cfg.dano
	local pistas = cargarAnimaciones(hum, esJefe and ("jefe_" .. j.tipo) or "zombi")
	if pistas.Reposo then pistas.Reposo:Play() end
	local muerto = false
	hum.Died:Connect(function()
		if muerto then return end; muerto = true; vivosZ = vivosZ - 1
		for _, pista in pairs(pistas) do pista:Stop() end
		if pistas.Caer then pistas.Caer:Play() end
		local killer = modelo:GetAttribute("UltimoAtacante")
		local pago = partida:zombiMuerto(killer, esJefe, now())
		local kp = killer and porId[killer]
		if kp and pago > 0 then R:FireClient(kp, { ganancia = pago, tipo = esJefe and "JEFE" or "ZOMBI" }) end
		Debris:AddItem(modelo, 2)
	end)
	task.spawn(function() -- IA: perseguir al jugador vivo mas cercano y golpearlo cuerpo a cuerpo
		local ultimo = 0
		local camino, indice, ultimoCalc = nil, 2, 0 -- ruta por PathfindingService (evita quedarse pegado a coches y barreras)
		while modelo.Parent and hum.Health > 0 do
			local mejor, dist
			for _, plr in ipairs(Players:GetPlayers()) do
				local rp = viva(plr)
				if rp and root then local d = (rp.Position - root.Position).Magnitude; if not dist or d < dist then mejor, dist = plr, d end end
			end
			local moviendo = mejor ~= nil and dist >= (esJefe and 9 or 5)
			if pistas.Caminar then
				if moviendo and not pistas.Caminar.IsPlaying then pistas.Caminar:Play() elseif not moviendo and pistas.Caminar.IsPlaying then pistas.Caminar:Stop() end
			end
			if mejor then
				local alcance = esJefe and 9 or 5
				local destino = viva(mejor).Position
				if dist < alcance + 2 then destino = root.Position -- ya esta al alcance: no subirse encima del jugador
				elseif dist > 14 then
					local t = now()
					if not camino or t - ultimoCalc > 1.5 + math.random() * 0.5 then
						ultimoCalc = t
						local path = PFS:CreatePath({ AgentRadius = esJefe and 3 or 2, AgentHeight = esJefe and 10 or 5.5, AgentCanJump = false })
						local okp = pcall(function() path:ComputeAsync(root.Position, destino) end)
						if okp and path.Status == Enum.PathStatus.Success then camino = path:GetWaypoints(); indice = 2 else camino = nil end
					end
					if camino then
						local wp = camino[indice]
						if wp and ((root.Position - wp.Position) * Vector3.new(1, 0, 1)).Magnitude < 4 then indice = indice + 1; wp = camino[indice] end
						if wp then destino = wp.Position end
					end
				end
				hum:MoveTo(destino)
				if dist < (esJefe and 9 or 5) + 2 and now() - ultimo > 1.2 then
					ultimo = now(); if pistas.Atacar then pistas.Atacar:Play() end; local hp = mejor.Character:FindFirstChildOfClass("Humanoid"); if hp then hp:TakeDamage(dano) end
				end
			end
			task.wait(0.25)
		end
	end)
end

-- ===== Tienda: compras =====
for item, pp in pairs(prompts) do
	pp.Triggered:Connect(function(plr)
		local ok, r = Tienda.comprar(partida, plr.UserId, item, math.max(1, partida.ronda))
		if not ok then mensaje(plr, tostring(r)); return end
		if item == "municion" then SS.LUTO_AnadirMunicion:Invoke(plr, 2); mensaje(plr, "Municion comprada (-" .. r.precio .. ")")
		else local h = plr.Character and plr.Character:FindFirstChildOfClass("Humanoid"); if h then h.Health = h.MaxHealth end; mensaje(plr, "Curado (-" .. r.precio .. ")") end
	end)
end

-- ===== Fin y reinicio =====
finPartida = function(r)
	for id, plr in pairs(porId) do
		local p = partida.players[id]
		if plr.Parent then R:FireClient(plr, { fin = true, rondaMax = r.rondaMax, monedasLobby = r.monedasLobby, kills = p and p.kills or 0 }) end
	end
	for _, z in ipairs(Collection:GetTagged("Zombi")) do z:Destroy() end
	vivosZ = 0
	task.delay(12, function()
		local ids = {}
		for _, plr in ipairs(Players:GetPlayers()) do ids[#ids + 1] = plr end
		partida = Partida.new(SEED + os.time() % 1000)
		porId = {}
		for i, plr in ipairs(ids) do if partida:addPlayer(plr.UserId) then porId[plr.UserId] = plr; cargar(plr, i) end end
		SS.LUTO_ReiniciarArmas:Fire()
		partida:comenzar(now()); avisarTodos("Nueva partida")
	end)
end

-- ===== Bucle principal =====
local t0, proxSpawn, ultimoEstado = now(), 0, 0
task.spawn(function()
	while true do
		task.wait(0.2)
		local t = now()
		if partida.estado == "esperando" and #partida.order > 0 and t - t0 > 8 then
			partida:comenzar(t)
			for i, id in ipairs(partida.order) do local plr = porId[id]; if plr then cargar(plr, i) end end
			avisarTodos("Prepárense: la primera ronda empieza pronto")
		end
		for _, ev in ipairs(partida:actualizar(t)) do
			if ev.tipo == "revivir" then
				for _, id in ipairs(ev.ids) do local plr = porId[id]; if plr then cargar(plr, 1); mensaje(plr, "¡Has revivido!") end end
			elseif ev.tipo == "inicio_ronda" then
				R:FireAllClients({ anuncio = { ronda = ev.ronda, jefe = ev.config.esJefe } }); proxSpawn = t + 2
				for item, pp in pairs(prompts) do pp.ActionText = "Comprar · " .. Tienda.precio(item, ev.ronda) end
			end
		end
		if partida.estado == "ronda" and partida:porAparecer() > 0 and vivosZ < partida.config.simultaneos and t >= proxSpawn then
			local jefe = partida:esAparicionJefe(); partida:registrarAparicion()
			task.spawn(crearZombi, partida.config, jefe); proxSpawn = t + partida.config.intervalo
		end
		if t - ultimoEstado >= 0.5 and partida.estado ~= "fin" then
			ultimoEstado = t
			local equipo = {}
			for _, id in ipairs(partida.order) do
				local plr = porId[id]; local h = plr and plr.Character and plr.Character:FindFirstChildOfClass("Humanoid")
				equipo[#equipo + 1] = { nombre = plr and plr.DisplayName or "?", vivo = partida.players[id].vivo and h ~= nil and h.Health > 0,
					vida = h and h.Health / math.max(1, h.MaxHealth) or 0 }
			end
			local jefeVida, jefeNombre
			for _, z in ipairs(Collection:GetTagged("Zombi")) do
				local hz = z:FindFirstChildOfClass("Humanoid")
				if z:GetAttribute("Jefe") and hz and hz.Health > 0 then jefeVida = hz.Health / hz.MaxHealth; jefeNombre = hz.DisplayName end
			end
			for id, plr in pairs(porId) do
				local p = partida.players[id]
				if p and plr.Parent then
					R:FireClient(plr, { estado = partida.estado, ronda = partida.ronda, restantes = math.max(0, partida.restantes), monedas = p.monedas,
						vivos = partida:vivos(), total = #partida.order, siguiente = partida.estado == "intermision" and math.max(0, math.ceil(partida.t_next - t)) or nil,
						jefe = partida.config and partida.config.esJefe or false, equipo = equipo, jefeVida = jefeVida, jefeNombre = jefeNombre })
				end
			end
		end
	end
end)
