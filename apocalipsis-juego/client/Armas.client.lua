-- PROVISIONAL y SIN PROBAR EN STUDIO. Cliente de armas de Luto: clic = disparar (mantener = automatica), R recargar, F inspeccionar, 1/2/3 cambiar de arma.
-- Los impactos y agujeros de bala se dibujan con ImpactoFX (mismo folder).
local UIS, RS, Players = game:GetService("UserInputService"), game:GetService("ReplicatedStorage"), game:GetService("Players")
local plr = Players.LocalPlayer
local FX = require(script.Parent:WaitForChild("ImpactoFX"))
local Luto = RS:WaitForChild("Luto"); local Weapons = require(Luto.Weapons)
local E = RS:WaitForChild("LUTO_Equipar"); local D = RS:WaitForChild("LUTO_Disparar"); local Rec = RS:WaitForChild("LUTO_Recargar")
local Ins = RS:WaitForChild("LUTO_Inspeccionar"); local Est = RS:WaitForChild("LUTO_Estado"); local Imp = RS:WaitForChild("LUTO_Impacto")

local arma, modo = "pistola", "semi"
Est.OnClientEvent:Connect(function(st) if st.arma then arma, modo = st.arma, st.modo end end)

-- Punto al que apunta el jugador: rayo desde la CAMARA (lo que ve) hasta lo primero que toca; si no toca nada, un punto lejano en esa direccion.
-- El servidor dispara desde la cabeza hacia ese punto (asi funciona en tercera persona y de cerca).
local function apuntar()
	local cam = workspace.CurrentCamera; local p = UIS:GetMouseLocation()
	local rayo = cam:ViewportPointToRay(p.X, p.Y)
	local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
	local excluir = { cam }; if plr.Character then excluir[#excluir + 1] = plr.Character end
	params.FilterDescendantsInstances = excluir
	local res = workspace:Raycast(rayo.Origin, rayo.Direction.Unit * 600, params)
	return res and res.Position or (rayo.Origin + rayo.Direction.Unit * 600)
end

local disparando = false
UIS.InputBegan:Connect(function(i, gp)
	if gp then return end
	if i.UserInputType == Enum.UserInputType.MouseButton1 then
		disparando = true; D:FireServer(apuntar())
		if modo == "auto" then
			task.spawn(function() while disparando do task.wait(0.04); D:FireServer(apuntar()) end end)
		end
	elseif i.KeyCode == Enum.KeyCode.R then Rec:FireServer()
	elseif i.KeyCode == Enum.KeyCode.F then Ins:FireServer()
	elseif i.KeyCode == Enum.KeyCode.One then E:FireServer("pistola")
	elseif i.KeyCode == Enum.KeyCode.Two then E:FireServer("escopeta")
	elseif i.KeyCode == Enum.KeyCode.Three then E:FireServer("subfusil") end
end)
UIS.InputEnded:Connect(function(i) if i.UserInputType == Enum.UserInputType.MouseButton1 then disparando = false end end)

Imp.OnClientEvent:Connect(function(d)
	if typeof(d) ~= "table" or typeof(d.pos) ~= "Vector3" then return end
	if d.enemigo and d.spec then FX.mostrar(d.pos, d.spec, d.normal) end
	FX.agujero(d.pos, d.normal, d.pieza, d.arma, d.enemigo)
end)
