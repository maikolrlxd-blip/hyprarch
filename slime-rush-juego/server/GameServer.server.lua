-- PROVISIONAL (prueba jugable, Capa 1). NO probado en Roblox Studio todavia: lo escribio Claude sin Studio a mano.
-- Servidor autoridad: crea la isla (World), las reglas (Rules) y el combate (Combat); formas simples de colores, sin arte final.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local SR = RS:WaitForChild("SlimeRush")
local World, Rules, Combat = require(SR.World), require(SR.Rules), require(SR.Combat)

local SEED = tonumber(workspace:GetAttribute("Seed")) or 1234
local TEST = { size = 512, node_count = 120, players = 8 }  -- isla pequeña para la prueba
local world = World.generate(SEED, TEST)
local rules = Rules.new(world, { countdown = 3, explore = 120, return_window = 60, collapse = 20 }, SEED)
local combat = Combat.new(rules)

local function remote(name) local r = Instance.new("RemoteEvent"); r.Name = name; r.Parent = RS; return r end
local E = { State = remote("SR_State"), Collect = remote("SR_Collect"), Punch = remote("SR_Punch"),
	Loot = remote("SR_Loot"), Deposit = remote("SR_Deposit"), Info = remote("SR_Info") }

-- Mundo provisional: suelo plano + marcadores (el terreno real sin Terrain de fabrica lo hace Codex)
local folder = Instance.new("Folder"); folder.Name = "SR_World"; folder.Parent = workspace
local function part(name, size, pos, color, shape)
	local p = Instance.new("Part"); p.Name = name; p.Size = size; p.Position = pos; p.Anchored = true
	p.Color = color; p.Material = Enum.Material.SmoothPlastic; if shape then p.Shape = shape end; p.Parent = folder; return p
end
part("Suelo", Vector3.new(world.size, 2, world.size), Vector3.new(world.size / 2, -1, world.size / 2), Color3.fromRGB(110, 170, 90))
local goal = world.goal
part("Meta", Vector3.new(goal.radius * 2, 0.5, goal.radius * 2), Vector3.new(goal.x, 0.3, goal.z), Color3.fromRGB(240, 200, 60))
local nodeParts = {}
for id, nd in ipairs(world.nodes) do
	nodeParts[id] = part("Nodo" .. id, Vector3.new(2, 2, 2), Vector3.new(nd.x, 2, nd.z), Color3.fromRGB(80, 200, 220), Enum.PartType.Ball)
end
local chestParts = {}
for id, ch in ipairs(world.chests) do chestParts[id] = part("Cofre" .. id, Vector3.new(4, 3, 3), Vector3.new(ch.x, 2, ch.z), Color3.fromRGB(200, 140, 60)) end

local ids, byUser = {}, {}
local function now() return workspace:GetServerTimeNow() end
local function pos(plr)
	local c = plr.Character; local h = c and c:FindFirstChild("HumanoidRootPart")
	return h and { x = h.Position.X, z = h.Position.Z } or nil, h
end

local started = false
Players.PlayerAdded:Connect(function(plr)
	if #rules.order >= TEST.players then return end
	local id = #rules.order + 1
	ids[plr] = id; byUser[id] = plr
	rules:addPlayer(id, started and now() or 0); combat:addPlayer(id)
	plr.CharacterAdded:Connect(function(char)
		local sp = world.spawns[id] or { x = goal.x + 20, z = goal.z }
		task.defer(function() char:PivotTo(CFrame.new(sp.x, 5, sp.z)) end)
	end)
end)

E.Collect.OnServerEvent:Connect(function(plr, kind, objId)
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
	local id, p, h = ids[plr], pos(plr); if not id or not p then return end
	local target = Players:GetPlayerByUserId(targetUserId); local tid = target and ids[target]
	local tp, th = pos(target or plr); if not tid or not tp then return end
	local ok, res = combat:punch(id, tid, p, tp, now())
	if ok then
		if th then th.AssemblyLinearVelocity = Vector3.new(res.push.x * 4, 25, res.push.z * 4) end
		E.Info:FireClient(target, res.knocked_out and "¡Estás inconsciente!" or ("Recibiste un golpe, vida " .. res.hp))
		E.Info:FireClient(plr, res.knocked_out and "¡Lo derrotaste! Puedes saquearlo" or "Golpe")
	end
end)

E.Loot.OnServerEvent:Connect(function(plr, targetUserId)
	local id, p = ids[plr], pos(plr); local target = Players:GetPlayerByUserId(targetUserId)
	local tid, tp = target and ids[target], target and pos(target); if not id or not p or not tid or not tp then return end
	local ok, res = rules:lootDowned(id, tid, p, tp, now())
	E.Info:FireClient(plr, ok and ("Saqueaste " .. #res.stolen .. " objeto(s)") or res)
end)

E.Deposit.OnServerEvent:Connect(function(plr, step)
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
	task.wait(5); rules:start(now()); started = true
	while true do
		local t, ph = now(), rules:phase(now())
		for plr, id in pairs(ids) do
			local p = rules.players[id]
			E.State:FireClient(plr, { phase = ph, t = t - rules.t0, items = #p.items, hp = combat.hp[id], downed = rules:isDowned(id, t),
				deposited = p.deposited, score = p.score })
		end
		if ph == "ended" then
			local _, res = rules:finalScores(t)
			for plr in pairs(ids) do E.State:FireClient(plr, { phase = "ended", results = res }) end
			break
		end
		task.wait(1)
	end
end)
