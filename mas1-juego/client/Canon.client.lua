-- Cañon del lobby: al activar el aviso del cañon (E, toque o mando) pide el lanzamiento al servidor. SIN PROBAR EN STUDIO.
local PPS, Players, RS = game:GetService("ProximityPromptService"), game:GetService("Players"), game:GetService("ReplicatedStorage")
local Red = require(RS:WaitForChild("Mas1"):WaitForChild("Red"))
local accion = Red.evento("MAS1_Accion")
local plr = Players.LocalPlayer
PPS.PromptTriggered:Connect(function(prompt, jugador)
	if jugador == plr and prompt.Parent and prompt.Parent.Name == "MAS1_Canon" and plr:GetAttribute("EnVuelo") ~= true then
		accion:FireServer("lanzar")
	end
end)
