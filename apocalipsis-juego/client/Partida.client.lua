-- PROVISIONAL y SIN PROBAR EN STUDIO. HUD de la partida de Luto: ronda, zombis, monedas, vivos, mensajes y pantalla de fin.
local RS, Players = game:GetService("ReplicatedStorage"), game:GetService("Players")
local plr = Players.LocalPlayer
local R = RS:WaitForChild("LUTO_Partida")
local gui = Instance.new("ScreenGui"); gui.Name = "LutoPartida"; gui.ResetOnSpawn = false; gui.Parent = plr:WaitForChild("PlayerGui")

local function etiqueta(y, w, h, size)
	local l = Instance.new("TextLabel"); l.Size = UDim2.new(0, w, 0, h); l.AnchorPoint = Vector2.new(0.5, 0); l.Position = UDim2.new(0.5, 0, 0, y)
	l.BackgroundTransparency = 0.35; l.BackgroundColor3 = Color3.fromRGB(16, 16, 20); l.TextColor3 = Color3.new(1, 1, 1)
	l.Font = Enum.Font.GothamBold; l.TextSize = size; l.Parent = gui; return l
end
local barra = etiqueta(10, 560, 36, 20); barra.Text = "LUTO"
local aviso = etiqueta(60, 520, 44, 24); aviso.Visible = false; aviso.TextColor3 = Color3.fromRGB(255, 215, 120)
local fin = Instance.new("Frame"); fin.Size = UDim2.new(0, 520, 0, 220); fin.AnchorPoint = Vector2.new(0.5, 0.5); fin.Position = UDim2.new(0.5, 0, 0.5, 0)
fin.BackgroundColor3 = Color3.fromRGB(10, 10, 14); fin.BackgroundTransparency = 0.1; fin.Visible = false; fin.Parent = gui
local finTxt = Instance.new("TextLabel"); finTxt.Size = UDim2.new(1, -24, 1, -24); finTxt.Position = UDim2.new(0, 12, 0, 12); finTxt.BackgroundTransparency = 1
finTxt.TextColor3 = Color3.new(1, 1, 1); finTxt.Font = Enum.Font.GothamBold; finTxt.TextSize = 26; finTxt.TextWrapped = true; finTxt.Parent = fin

local nombres = { esperando = "ESPERANDO", intermision = "PREPARACIÓN", ronda = "RONDA", fin = "FIN" }
local token = 0
R.OnClientEvent:Connect(function(d)
	if d.fin then
		fin.Visible = true
		finTxt.Text = string.format("LUTO\nLlegaste a la ronda %d\nMonedas del lobby: +%d\nNueva partida en unos segundos…", d.rondaMax, d.monedasLobby)
		return
	end
	if d.msg then
		aviso.Text = d.msg; aviso.Visible = true; token = token + 1; local mi = token
		task.delay(3.5, function() if token == mi then aviso.Visible = false end end)
	end
	if d.estado then
		fin.Visible = false
		local txt = string.format("%s %d  ·  Zombis %d  ·  Monedas %d  ·  Vivos %d/%d", nombres[d.estado] or d.estado, d.ronda, d.restantes, d.monedas, d.vivos, d.total)
		if d.siguiente then txt = txt .. "  ·  Siguiente en " .. d.siguiente end
		barra.Text = (d.jefe and "★ JEFE ★  " or "") .. txt
	end
end)
