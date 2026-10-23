-- PROVISIONAL y SIN PROBAR EN STUDIO. Servidor autoridad de las armas de Luto: equipar, disparar (raycast con dispersion), recargar,
-- inspeccionar, dano por zona y aviso a los clientes para dibujar impactos y agujeros de bala. Usa src/Weapons, Impactos y Disparo.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Collection = game:GetService("CollectionService")
local ServerStorage = game:GetService("ServerStorage")
local Luto = RS:WaitForChild("Luto")
local Weapons, Impactos, Disparo = require(Luto.Weapons), require(Luto.Impactos), require(Luto.Disparo)

local function remote(n) local r = Instance.new("RemoteEvent"); r.Name = n; r.Parent = RS; return r end
local R = { Equipar = remote("LUTO_Equipar"), Disparar = remote("LUTO_Disparar"), Recargar = remote("LUTO_Recargar"),
	Inspeccionar = remote("LUTO_Inspeccionar"), Estado = remote("LUTO_Estado"), Impacto = remote("LUTO_Impacto"), Anim = remote("LUTO_Anim") }
local ARMAS = { "pistola", "escopeta", "subfusil" }
local estado = {} -- [Player] = { armas = { id = Weapons }, actual = id }
local function now() return workspace:GetServerTimeNow() end

-- Arma en la mano (tercera persona): Tool clonado de ReplicatedStorage.LUTO_Armas[id] (Handle = malla de Blender, Grip ajustado). Sin plantilla no pasa nada.
local function equiparTool(plr, id)
	local char = plr.Character; local hum = char and char:FindFirstChildOfClass("Humanoid"); if not hum then return end
	for _, contenedor in ipairs({ char, plr:FindFirstChild("Backpack") }) do
		if contenedor then for _, t in ipairs(contenedor:GetChildren()) do if t:IsA("Tool") and t:GetAttribute("LutoArma") then t:Destroy() end end end
	end
	local plantillas = RS:FindFirstChild("LUTO_Armas"); local tpl = plantillas and plantillas:FindFirstChild(id)
	if not tpl then return end
	local tool = tpl:Clone(); tool:SetAttribute("LutoArma", id); tool.CanBeDropped = false; tool.Parent = plr:FindFirstChild("Backpack") or char
	pcall(function() hum:EquipTool(tool) end)
end
local function clip(plr, nombre) R.Anim:FireClient(plr, { clip = nombre }) end

local function enviarEstado(plr)
	local s = estado[plr]; if not s then return end
	local w = s.armas[s.actual]
	R.Estado:FireClient(plr, { arma = s.actual, nombre = w.def.name, municion = w.ammo, reserva = w.reserve, recargando = w.reloading ~= nil, modo = w.def.mode })
end

Players.PlayerAdded:Connect(function(plr)
	local s = { armas = {}, actual = "pistola" }
	for i, id in ipairs(ARMAS) do s.armas[id] = Weapons.new(id, plr.UserId * 10 + i) end
	estado[plr] = s; s.armas.pistola:equip(now()); enviarEstado(plr)
	plr.CharacterAdded:Connect(function(ch) ch:WaitForChild("Humanoid"); task.wait(0.3); if estado[plr] then equiparTool(plr, estado[plr].actual); clip(plr, "Equipar") end end)
end)
Players.PlayerRemoving:Connect(function(plr) estado[plr] = nil end)
for _, plr in ipairs(Players:GetPlayers()) do
	local s = { armas = {}, actual = "pistola" }
	for i, id in ipairs(ARMAS) do s.armas[id] = Weapons.new(id, plr.UserId * 10 + i) end
	estado[plr] = s; s.armas.pistola:equip(now()); enviarEstado(plr)
end

R.Equipar.OnServerEvent:Connect(function(plr, id)
	local s = estado[plr]; if not s or type(id) ~= "string" or not s.armas[id] then return end
	s.actual = id; s.armas[id]:equip(now()); enviarEstado(plr); equiparTool(plr, id); clip(plr, "Equipar")
end)

R.Recargar.OnServerEvent:Connect(function(plr)
	local s = estado[plr]; if not s then return end
	local w = s.armas[s.actual]
	local ok, info = w:reload(now()); if not ok then return end
	enviarEstado(plr); clip(plr, info.clip)
	task.spawn(function() -- avanza la recarga y avisa al terminar (la escopeta va cartucho por cartucho)
		local previa = w.ammo
		while w.reloading and estado[plr] do
			task.wait(0.1); w:update(now())
			if w.def.reload_shell and w.ammo > previa then clip(plr, "Recargar_Cartucho"); previa = w.ammo end
			enviarEstado(plr)
		end
		if w.def.reload_shell and estado[plr] then clip(plr, "Recargar_Fin") end
	end)
end)

R.Inspeccionar.OnServerEvent:Connect(function(plr)
	local s = estado[plr]; if not s then return end
	local ok, r = s.armas[s.actual]:inspect(now()); if ok then R.Estado:FireClient(plr, { inspeccionar = r.clip, duracion = r.duration }); clip(plr, "Inspeccionar") end
end)

local function cabeza(char)
	local h = char:FindFirstChild("Head") or char:FindFirstChild("HumanoidRootPart"); return h and h.Position
end

R.Disparar.OnServerEvent:Connect(function(plr, aim)
	local s = estado[plr]; local char = plr.Character
	if not s or not char or typeof(aim) ~= "Vector3" then return end
	local origen = cabeza(char); if not origen then return end
	if (aim - origen).Magnitude < 0.5 or (aim - origen).Magnitude > 2000 then return end -- 'aim' es el PUNTO apuntado por la camara del jugador
	local root = char:FindFirstChild("HumanoidRootPart")
	local moving = root and root.AssemblyLinearVelocity.Magnitude > 2 or false
	local w = s.armas[s.actual]
	local ok, r = w:fire(now(), moving)
	if not ok then enviarEstado(plr); return end
	clip(plr, "Disparo")
	if r.pump_clip then task.delay(0.35, function() if estado[plr] and estado[plr].actual == s.actual then clip(plr, "Bombear") end end) end
	local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { char }
	local a = (aim - origen).Unit
	for _, p in ipairs(r.pellets) do
		local d = Disparo.direccion({ x = a.X, y = a.Y, z = a.Z }, p.yaw, p.pitch)
		local res = workspace:Raycast(origen, Vector3.new(d.x, d.y, d.z) * w.def.range, params)
		if res then
			local modelo = res.Instance:FindFirstAncestorOfClass("Model")
			local hum = modelo and Collection:HasTag(modelo, "Zombi") and modelo:FindFirstChildOfClass("Humanoid") or nil
			local n = { x = res.Normal.X, y = res.Normal.Y, z = res.Normal.Z }
			if hum and hum.Health > 0 then
				local zona = Disparo.zona(res.Instance.Name)
				local spec = Impactos.resolve(s.actual, zona, res.Distance, n)
				if spec then
					modelo:SetAttribute("UltimoAtacante", plr.UserId) -- para pagar la recompensa al que lo mate
					hum:TakeDamage(spec.dano)
					local rootE = modelo:FindFirstChild("HumanoidRootPart")
					if rootE and not rootE.Anchored then rootE:ApplyImpulse(Vector3.new(d.x, 0, d.z) * spec.reaccion.empuje * rootE.AssemblyMass) end
					R.Impacto:FireAllClients({ pos = res.Position, normal = res.Normal, pieza = res.Instance, enemigo = true, arma = s.actual, spec = spec, tirador = plr.UserId, cabeza = zona == "cabeza" })
				end
			else
				R.Impacto:FireAllClients({ pos = res.Position, normal = res.Normal, pieza = res.Instance, enemigo = false, arma = s.actual })
			end
		end
	end
	enviarEstado(plr)
end)

-- Enlaces con Partida.server.lua (tienda y reinicio)
local bf = Instance.new("BindableFunction"); bf.Name = "LUTO_AnadirMunicion"; bf.Parent = ServerStorage
bf.OnInvoke = function(plr, cargadores)
	local s = estado[plr]; if not s then return 0 end
	local w = s.armas[s.actual]; local n = w:addReserve(w.def.mag * cargadores); enviarEstado(plr); return n
end
local be = Instance.new("BindableEvent"); be.Name = "LUTO_ReiniciarArmas"; be.Parent = ServerStorage
be.Event:Connect(function()
	for plr, s in pairs(estado) do
		for i, id in ipairs(ARMAS) do s.armas[id] = Weapons.new(id, plr.UserId * 10 + i + math.floor(now())) end
		s.actual = "pistola"; s.armas.pistola:equip(now()); enviarEstado(plr)
	end
end)
