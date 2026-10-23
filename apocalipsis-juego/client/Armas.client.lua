-- PROVISIONAL y SIN PROBAR EN STUDIO. Cliente de armas de Luto: clic = disparar (mantener = automatica), R recargar, F inspeccionar, 1/2/3 cambiar de arma.
-- Los impactos y agujeros de bala se dibujan con ImpactoFX (mismo folder).
local UIS, RS, Players = game:GetService("UserInputService"), game:GetService("ReplicatedStorage"), game:GetService("Players")
local plr = Players.LocalPlayer
local FX = require(script.Parent:WaitForChild("ImpactoFX"))
local Luto = RS:WaitForChild("Luto"); local Weapons = require(Luto.Weapons)
local E = RS:WaitForChild("LUTO_Equipar"); local D = RS:WaitForChild("LUTO_Disparar"); local Rec = RS:WaitForChild("LUTO_Recargar")
local Ins = RS:WaitForChild("LUTO_Inspeccionar"); local Est = RS:WaitForChild("LUTO_Estado"); local Imp = RS:WaitForChild("LUTO_Impacto")

local gui = Instance.new("ScreenGui"); gui.Name = "LutoArmas"; gui.ResetOnSpawn = false; gui.Parent = plr:WaitForChild("PlayerGui")
local lbl = Instance.new("TextLabel"); lbl.Size = UDim2.new(0, 360, 0, 34); lbl.Position = UDim2.new(1, -372, 1, -90)
lbl.BackgroundTransparency = 0.4; lbl.BackgroundColor3 = Color3.fromRGB(20, 20, 24); lbl.TextColor3 = Color3.new(1, 1, 1)
lbl.Font = Enum.Font.GothamBold; lbl.TextSize = 20; lbl.Parent = gui
local mira = Instance.new("Frame"); mira.Size = UDim2.new(0, 6, 0, 6); mira.AnchorPoint = Vector2.new(0.5, 0.5)
mira.Position = UDim2.new(0.5, 0, 0.5, 0); mira.BackgroundColor3 = Color3.new(1, 1, 1); mira.BorderSizePixel = 0; mira.Parent = gui

local arma, modo = "pistola", "semi"
Est.OnClientEvent:Connect(function(s)
	if s.arma then
		arma, modo = s.arma, s.modo
		lbl.Text = string.format("%s  %d / %d%s", s.nombre, s.municion, s.reserva, s.recargando and "  (recargando)" or "")
	end
	if s.inspeccionar then lbl.Text = lbl.Text .. "  [" .. s.inspeccionar .. " " .. s.duracion .. "s]" end
end)

local function apuntar()
	local cam = workspace.CurrentCamera; local p = UIS:GetMouseLocation()
	return cam:ViewportPointToRay(p.X, p.Y).Direction.Unit
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
