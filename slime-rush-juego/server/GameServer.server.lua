-- PROVISIONAL (prueba jugable, Capa 1). NO probado en Roblox Studio todavia: lo escribio Claude sin Studio a mano.
-- Servidor autoridad: crea la isla (World), las reglas (Rules) y el combate (Combat); formas simples de colores, sin arte final.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")
local SR = RS:WaitForChild("SlimeRush")
local World, Rules, Combat = require(SR.World), require(SR.Rules), require(SR.Combat)

local SEED = tonumber(workspace:GetAttribute("Seed")) or 1234
local TEST = { size = 512, cell = 16, node_count = 40, players = 8,
	chests = { comun = 3, musgoso = 0, dorado = 0, oculto = 0 },
	rare_sites = 0, volcano_chance = 0 } -- Capa 1: tres cofres y sin contenido de otras capas
local generationStart = os.clock()
local world = World.generate(SEED, TEST)
local worldGenerationMs = math.floor((os.clock() - generationStart) * 1000 + 0.5)
local rules = Rules.new(world, { countdown = 10, explore = 120, return_window = 60, collapse = 20 }, SEED)
local combat = Combat.new(rules)

local function remote(name) local r = Instance.new("RemoteEvent"); r.Name = name; r.Parent = RS; return r end
local E = { State = remote("SR_State"), Collect = remote("SR_Collect"), Punch = remote("SR_Punch"),
	Loot = remote("SR_Loot"), Deposit = remote("SR_Deposit"), Info = remote("SR_Info") }

-- Geometria de prueba: bloques por celda de altura/bioma del mismo World.generate que usan las reglas.
-- Son marcadores descartables para medir jugabilidad; los modelos finales se harán en Blender.
local folder = Instance.new("Folder"); folder.Name = "SR_World"; folder.Parent = workspace
local function part(name, size, pos, color, shape)
	local p = Instance.new("Part"); p.Name = name; p.Size = size; p.Position = pos; p.Anchored = true
	p.Color = color; p.Material = Enum.Material.SmoothPlastic; if shape then p.Shape = shape end; p.Parent = folder; return p
end
local terrainFolder = Instance.new("Folder"); terrainFolder.Name = "TerrainTiles"; terrainFolder.Parent = folder
local palette = {
	mar = Color3.fromRGB(34, 85, 119), lago = Color3.fromRGB(47, 120, 147),
	pradera = Color3.fromRGB(105, 155, 77), bosque = Color3.fromRGB(55, 111, 67),
	desierto = Color3.fromRGB(201, 170, 103), roca = Color3.fromRGB(115, 119, 114),
	montana = Color3.fromRGB(154, 158, 148),
}
local heights, biomes, cells = World.grid(world)
local cell = world.cfg.cell
local bottom = -27
local function prototypeHeight(raw)
	-- La semilla y los biomas son reales. Comprimimos solo la altura VISUAL para que
	-- un avatar pueda recorrer esta version de bloques sin cientos de paredes infranqueables.
	return raw < 5 and raw or 5 + (raw - 5) * 0.1
end
for iz = 1, cells do
	for ix = 1, cells do
		local h, biome = prototypeHeight(heights[iz][ix]), biomes[iz][ix]
		heights[iz][ix] = h
		local tile = Instance.new("Part")
		tile.Name = "T" .. ix .. "_" .. iz
		tile.Size = Vector3.new(cell + 0.04, math.max(1, h - bottom), cell + 0.04)
		tile.Position = Vector3.new((ix - 0.5) * cell, (h + bottom) / 2, (iz - 0.5) * cell)
		tile.Anchored = true; tile.Material = Enum.Material.SmoothPlastic
		tile.Color = palette[biome] or palette.pradera
		tile.Parent = terrainFolder
	end
	if iz % 8 == 0 then task.wait() end -- Studio sigue respondiendo durante la construccion
end
local sea = part("Mar", Vector3.new(world.size, 0.2, world.size),
	Vector3.new(world.size / 2, -0.1, world.size / 2), Color3.fromRGB(59, 146, 192))
sea.Transparency = 0.38; sea.CanCollide = false
local function tileHeight(x, z)
	local ix = math.clamp(math.floor(x / cell) + 1, 1, cells)
	local iz = math.clamp(math.floor(z / cell) + 1, 1, cells)
	return heights[iz][ix]
end
local goal = world.goal
part("Meta", Vector3.new(goal.radius * 2, 0.5, goal.radius * 2),
	Vector3.new(goal.x, tileHeight(goal.x, goal.z) + 0.3, goal.z), Color3.fromRGB(240, 200, 60))
local nodeParts = {}
for id, nd in ipairs(world.nodes) do
	nodeParts[id] = part("Nodo" .. id, Vector3.new(2, 2, 2),
		Vector3.new(nd.x, tileHeight(nd.x, nd.z) + 2, nd.z), Color3.fromRGB(80, 200, 220), Enum.PartType.Ball)
end
local chestParts = {}
for id, ch in ipairs(world.chests) do
	chestParts[id] = part("Cofre" .. id, Vector3.new(4, 3, 3),
		Vector3.new(ch.x, tileHeight(ch.x, ch.z) + 1.5, ch.z), Color3.fromRGB(200, 140, 60))
end
local totalGenerationMs = math.floor((os.clock() - generationStart) * 1000 + 0.5)
workspace:SetAttribute("SR_WorldGenerationMs", worldGenerationMs)
workspace:SetAttribute("SR_TotalGenerationMs", totalGenerationMs)
print(string.format("SR_QA seed=%d world=%dms total=%dms tiles=%d nodes=%d chests=%d",
	SEED, worldGenerationMs, totalGenerationMs, cells * cells, #world.nodes, #world.chests))

local ids, byUser, downedMovement = {}, {}, {}
local function now() return workspace:GetServerTimeNow() end
local function pos(plr)
	local c = plr.Character; local h = c and c:FindFirstChild("HumanoidRootPart")
	return h and { x = h.Position.X, z = h.Position.Z } or nil, h
end

local started = false
local function addPlayer(plr)
	if #rules.order >= TEST.players then plr:SetAttribute("SR_Spectator", true); return end
	local id = #rules.order + 1
	local ok = rules:addPlayer(id, started and now() or 0)
	if not ok then plr:SetAttribute("SR_Spectator", true); return end
	ids[plr] = id; byUser[id] = plr
	combat:addPlayer(id)
	plr.CharacterAdded:Connect(function(char)
		local sp = world.spawns[id] or { x = goal.x + 20, z = goal.z }
		task.defer(function()
			if char:WaitForChild("HumanoidRootPart", 5) then
				char:PivotTo(CFrame.new(sp.x, tileHeight(sp.x, sp.z) + 5, sp.z))
			end
		end)
	end)
	if plr.Character then
		local sp = world.spawns[id]
		plr.Character:PivotTo(CFrame.new(sp.x, tileHeight(sp.x, sp.z) + 5, sp.z))
	end
end
Players.PlayerAdded:Connect(addPlayer)
for _, plr in ipairs(Players:GetPlayers()) do addPlayer(plr) end
Players.PlayerRemoving:Connect(function(plr)
	local id = ids[plr]
	if id then byUser[id] = nil; ids[plr] = nil end
	downedMovement[plr] = nil
end)

-- El estado de inconsciencia lo decide Rules, y esta funcion refleja ese estado en el Humanoid.
-- La sincronizacion por segundo tambien cubre el despertar y los cambios de Character.
local function syncDownedMovement(plr, downed)
	local char = plr.Character
	local humanoid = char and char:FindFirstChildOfClass("Humanoid")
	local saved = downedMovement[plr]
	if downed and humanoid then
		if not saved or saved.humanoid ~= humanoid then
			saved = { humanoid = humanoid, speed = humanoid.WalkSpeed,
				jumpPower = humanoid.JumpPower, jumpHeight = humanoid.JumpHeight,
				autoRotate = humanoid.AutoRotate }
			downedMovement[plr] = saved
		end
		humanoid.WalkSpeed = 0; humanoid.JumpPower = 0; humanoid.JumpHeight = 0
		humanoid.AutoRotate = false
	elseif saved then
		if saved.humanoid.Parent then
			saved.humanoid.WalkSpeed = saved.speed
			saved.humanoid.JumpPower = saved.jumpPower
			saved.humanoid.JumpHeight = saved.jumpHeight
			saved.humanoid.AutoRotate = saved.autoRotate
		end
		downedMovement[plr] = nil
	end
end

E.Collect.OnServerEvent:Connect(function(plr, kind, objId)
	if type(objId) ~= "number" or objId % 1 ~= 0 then return end -- nunca confiar en lo que manda el cliente
	local id, p = ids[plr], pos(plr); if not id or not p then return end
	if kind == "node" then
		local ok, res = rules:collectNode(id, objId, p, now())
		if ok and nodeParts[objId] then nodeParts[objId]:Destroy() end
		E.Info:FireClient(plr, ok and ("Recogiste " .. res.kind .. " (+" .. res.value .. ")") or res)
	elseif kind == "chest" then
		local ok, res = rules:claimChest(id, objId, p, now())
		if ok and chestParts[objId] then chestParts[objId]:Destroy() end
		E.Info:FireClient(plr, ok and "Abriste un cofre" or res)
	end
end)

E.Punch.OnServerEvent:Connect(function(plr, targetUserId)
	if type(targetUserId) ~= "number" then return end
	local id, p, h = ids[plr], pos(plr); if not id or not p then return end
	local target = Players:GetPlayerByUserId(targetUserId); local tid = target and ids[target]
	local tp, th = pos(target or plr); if not tid or not tp then return end
	local ok, res = combat:punch(id, tid, p, tp, now())
	if ok then
		if th then th.AssemblyLinearVelocity = Vector3.new(res.push.x * 4, 25, res.push.z * 4) end
		if res.knocked_out then syncDownedMovement(target, rules:isDowned(tid, now())) end
		E.Info:FireClient(target, res.knocked_out and "¡Estás inconsciente!" or ("Recibiste un golpe, vida " .. res.hp))
		E.Info:FireClient(plr, res.knocked_out and "¡Lo derrotaste! Puedes saquearlo" or "Golpe")
	else E.Info:FireClient(plr, res)
	end
end)

E.Loot.OnServerEvent:Connect(function(plr, targetUserId)
	if type(targetUserId) ~= "number" then return end
	local id, p = ids[plr], pos(plr); local target = Players:GetPlayerByUserId(targetUserId)
	local tid, tp = target and ids[target], target and pos(target); if not id or not p or not tid or not tp then return end
	local ok, res = rules:lootDowned(id, tid, p, tp, now())
	E.Info:FireClient(plr, ok and ("Saqueaste " .. #res.stolen .. " objeto(s)") or res)
end)

E.Deposit.OnServerEvent:Connect(function(plr, step)
	if step ~= "start" and step ~= "finish" then return end
	local id, p = ids[plr], pos(plr); if not id or not p then return end
	local ok, res
	if step == "start" then ok, res = rules:startDeposit(id, p, now()); E.Info:FireClient(plr, ok and "Depositando… quédate en la meta" or res)
	else
		ok, res = rules:finishDeposit(id, p, now())
		E.Info:FireClient(plr, ok and ("¡Llegaste! puesto " .. res.rank .. ", " .. res.score .. " puntos") or res)
	end
end)

-- Bucle de estado: fase, tiempo restante, mochila y vida de cada jugador, una vez por segundo
task.spawn(function()
	while #Players:GetPlayers() < 1 do task.wait(1) end
	task.wait(15) -- tiempo para que entren los demas jugadores de la prueba
	rules:start(now()); started = true
	local stormAnnounced = false
	while true do
		local t, ph = now(), rules:phase(now())
		local elapsed = t - rules.t0
		local phaseEnds = rules.cfg.countdown
		if ph == "explore" then phaseEnds = phaseEnds + rules.cfg.explore
		elseif ph == "return" then phaseEnds = phaseEnds + rules.cfg.explore + rules.cfg.return_window
		elseif ph == "collapse" then phaseEnds = phaseEnds + rules.cfg.explore + rules.cfg.return_window + rules.cfg.collapse end
		if ph == "collapse" then
			Lighting.ClockTime = 19; Lighting.Brightness = 1
			if not stormAnnounced then
				stormAnnounced = true
				for plr, id in pairs(ids) do
					if not rules.players[id].deposited then
						E.Info:FireClient(plr, "¡Tormenta! La meta está cerrada; perderás lo que no depositaste")
					end
				end
			end
		end
		for plr, id in pairs(ids) do
			local p = rules.players[id]
			local downed = rules:isDowned(id, t)
			syncDownedMovement(plr, downed)
			E.State:FireClient(plr, { phase = ph, t = elapsed, remaining = math.max(0, math.ceil(phaseEnds - elapsed)),
				items = #p.items, capacity = rules.cfg.backpack, hp = combat:getHp(id, t), downed = downed,
				deposited = p.deposited, score = p.score })
		end
		for _, plr in ipairs(Players:GetPlayers()) do
			if plr:GetAttribute("SR_Spectator") then E.State:FireClient(plr, { phase = "spectator", t = 0, items = 0,
				capacity = rules.cfg.backpack, hp = 0 }) end
		end
		if ph == "ended" then
			local _, res = rules:finalScores(t)
			for plr, id in pairs(ids) do
				plr:SetAttribute("SR_Eliminated", not rules.players[id].deposited)
				syncDownedMovement(plr, false)
			end
			for plr in pairs(ids) do E.State:FireClient(plr, { phase = "ended", results = res }) end
			break
		end
		task.wait(1)
	end
end)
