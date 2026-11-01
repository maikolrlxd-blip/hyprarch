-- Sonido de «+1 de lanzamiento por segundo» en el cliente: engancha los eventos del juego (efectos, orbes, huevos, avisos, atributos) y
-- reproduce los ids de src/Sonidos.lua (vacios hasta subir los WAV: sin id no suena nada). SIN PROBAR EN STUDIO.
local Players, RS, SoundService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("SoundService")
local plr = Players.LocalPlayer
local Mas1 = RS:WaitForChild("Mas1")
local S = require(Mas1:WaitForChild("Sonidos"))
local Red = require(Mas1:WaitForChild("Red"))

local function sonar(nombre, tono)
	local id = S[nombre]
	if type(id) ~= "string" or id == "" then return end
	local s = Instance.new("Sound")
	s.SoundId, s.Volume = id, (S.volumen and S.volumen[nombre]) or 0.7
	if tono then s.PlaybackSpeed = tono end
	s.Parent = SoundService
	s.Ended:Connect(function() s:Destroy() end)
	s:Play()
	task.delay(5, function() if s.Parent then s:Destroy() end end)
end

Red.evento("MAS1_Efecto").OnClientEvent:Connect(function(nombre)
	if nombre == "lanzamiento" or nombre == "aro" or nombre == "golpe" or nombre == "rebirth" then sonar(nombre) end
end)
Red.evento("MAS1_Orbe").OnClientEvent:Connect(function() sonar("orbe", 0.95 + math.random() * 0.2) end)
Red.evento("MAS1_Aviso").OnClientEvent:Connect(function() sonar("error") end)
Red.evento("MAS1_Resultado").OnClientEvent:Connect(function() sonar("aterrizaje") end)
Red.evento("MAS1_Huevo").OnClientEvent:Connect(function(d)
	sonar("huevo_agita")
	task.delay(0.7, function() sonar(d and (d.rareza == "mitico" or d.rareza == "legendario") and "mitico" or "huevo_abre") end)
end)
plr:GetAttributeChangedSignal("Boost"):Connect(function() if plr:GetAttribute("Boost") == true then sonar("boost") end end)
plr:GetAttributeChangedSignal("Cofres"):Connect(function() sonar("cofre") end)
local ultimoCombo = 0
plr:GetAttributeChangedSignal("Combo"):Connect(function()
	local c = plr:GetAttribute("Combo") or 0
	if c > ultimoCombo and c % 5 == 0 then sonar("combo", 1 + math.min(c, 30) / 60) end
	ultimoCombo = c
end)
