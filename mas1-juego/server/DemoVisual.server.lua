-- SOLO PARA VER LA CAPA VISUAL antes de que exista el juego: si workspace tiene el atributo MAS1_Demo = true, simula un vuelo (energia que baja,
-- puntos y distancia que suben, aros, multiplicadores) y dispara efectos de ejemplo. No es logica de juego. SIN PROBAR EN STUDIO.
local Players, RS = game:GetService("Players"), game:GetService("ReplicatedStorage")
local Red = require(RS:WaitForChild("Mas1"):WaitForChild("Red")) -- los mismos eventos que el juego (server/Partida.server.lua), sin duplicarlos
local Efecto, Accion = Red.evento("MAS1_Efecto"), Red.evento("MAS1_Accion")
while workspace:GetAttribute("MAS1_Demo") ~= true do workspace:GetAttributeChangedSignal("MAS1_Demo"):Wait() end -- sirve activarlo antes o durante el Play

local function raiz(plr) local c = plr.Character; return c and c:FindFirstChild("HumanoidRootPart") end
Accion.OnServerEvent:Connect(function(plr, nombre)
	local r = raiz(plr); if not r then return end
	if nombre == "puno" or nombre == "patada" then Efecto:FireClient(plr, "golpe", r.Position + r.CFrame.LookVector * 4)
	elseif nombre == "turbo" then Efecto:FireClient(plr, "aleteo", r.Position) end
end)

local ZONAS = { 1, 2, 3, 5 }
task.spawn(function()
	local t0 = os.clock()
	while true do
		task.wait(0.25)
		local t = os.clock() - t0; local ciclo = t % 20 -- un "vuelo" de 20 s que se repite
		for _, plr in ipairs(Players:GetPlayers()) do
			plr:SetAttribute("Energia", math.max(0, 1 - ciclo / 18)); plr:SetAttribute("Potencia", 1250 + math.floor(t))
			plr:SetAttribute("Puntos", math.floor(ciclo * 640)); plr:SetAttribute("Distancia", math.floor(ciclo * 47))
			plr:SetAttribute("ZonaMult", ZONAS[math.floor(ciclo / 5) % #ZONAS + 1]); plr:SetAttribute("ArosTotal", 12); plr:SetAttribute("Aros", math.min(12, math.floor(ciclo / 1.7)))
			plr:SetAttribute("Mascota", "Gorrión Miga"); plr:SetAttribute("MascotaBonus", 1.5)
			local r = raiz(plr)
			if r and math.floor(ciclo * 4) % 7 == 0 then Efecto:FireClient(plr, "aro", r.Position + Vector3.new(0, 4, -6)) end
			if r and ciclo < 0.3 then Efecto:FireClient(plr, "lanzamiento", r.Position) end
		end
	end
end)
