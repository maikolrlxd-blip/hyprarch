-- PROVISIONAL: HUD minimo (fase, tiempo, mochila, vida, mensajes) y controles: E recoger, F golpear, G saquear, H depositar.
local Players, RS, UIS = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("UserInputService")
local plr = Players.LocalPlayer
local State, Collect, Punch, Loot, Deposit, Info = RS:WaitForChild("SR_State"), RS:WaitForChild("SR_Collect"), RS:WaitForChild("SR_Punch"),
	RS:WaitForChild("SR_Loot"), RS:WaitForChild("SR_Deposit"), RS:WaitForChild("SR_Info")

local gui = Instance.new("ScreenGui"); gui.Name = "SR_Hud"; gui.ResetOnSpawn = false; gui.Parent = plr:WaitForChild("PlayerGui")
local function label(y, size)
	local l = Instance.new("TextLabel"); l.Size = UDim2.new(0, 420, 0, size or 28); l.Position = UDim2.new(0, 12, 0, y)
	l.BackgroundTransparency = 0.4; l.BackgroundColor3 = Color3.fromRGB(20, 20, 30); l.TextColor3 = Color3.new(1, 1, 1)
	l.TextXAlignment = Enum.TextXAlignment.Left; l.Font = Enum.Font.GothamBold; l.TextSize = 18; l.Parent = gui; return l
end
local main, msg = label(12), label(46)
msg.TextSize = 16; msg.Text = "E recoger · F golpear · G saquear · H depositar"
msg.TextWrapped = true
local phaseNames = { countdown = "PREPARADOS", explore = "EXPLORAR", ["return"] = "REGRESAR",
	collapse = "TORMENTA", ended = "FIN", spectator = "ESPECTADOR" }
State.OnClientEvent:Connect(function(s)
	if s.results then
		local out = "FIN\n"; for _, r in ipairs(s.results) do out = out .. r.place .. ". Jugador " .. r.id .. ": " .. r.score .. (r.arrived and "" or " (no llegó)") .. "\n" end
		msg.Size = UDim2.new(0, 420, 0, 28 * (#s.results + 1)); msg.Text = out; return
	end
	main.Text = string.format("%s · %ds · Mochila %d/%d · Vida %s%s", phaseNames[s.phase] or s.phase,
		s.remaining or math.floor(s.t), s.items, s.capacity or 30,
		tostring(s.hp), s.downed and " · INCONSCIENTE" or "")
end)
Info.OnClientEvent:Connect(function(t) msg.Text = tostring(t) end)

local function nearestPlayer()
	local me = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart"); if not me then return end
	local best, bd
	for _, o in ipairs(Players:GetPlayers()) do
		local h = o ~= plr and o.Character and o.Character:FindFirstChild("HumanoidRootPart")
		if h then local d = (h.Position - me.Position).Magnitude; if not bd or d < bd then best, bd = o, d end end
	end
	return best
end
local function nearestWorldPart(prefix)
	local me = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart"); local f = workspace:FindFirstChild("SR_World")
	if not me or not f then return end
	local best, bd
	for _, p in ipairs(f:GetChildren()) do
		if p.Name:sub(1, #prefix) == prefix then local d = (p.Position - me.Position).Magnitude; if not bd or d < bd then best, bd = p, d end end
	end
	return best
end
UIS.InputBegan:Connect(function(i, gp)
	if gp then return end
	if i.KeyCode == Enum.KeyCode.E then
		local n = nearestWorldPart("Nodo"); local c = nearestWorldPart("Cofre")
		local me = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
		if c and me and (c.Position - me.Position).Magnitude < 14 then Collect:FireServer("chest", tonumber(c.Name:sub(6)))
		elseif n then Collect:FireServer("node", tonumber(n.Name:sub(5))) end
	elseif i.KeyCode == Enum.KeyCode.F then local t = nearestPlayer(); if t then Punch:FireServer(t.UserId) end
	elseif i.KeyCode == Enum.KeyCode.G then local t = nearestPlayer(); if t then Loot:FireServer(t.UserId) end
	elseif i.KeyCode == Enum.KeyCode.H then Deposit:FireServer("start"); task.delay(2.2, function() Deposit:FireServer("finish") end) end
end)
