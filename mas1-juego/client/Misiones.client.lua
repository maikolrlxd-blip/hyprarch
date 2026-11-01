-- Panel de misiones de «+1 de lanzamiento por segundo»: 3 misiones de la sesion con barra de progreso, a la izquierda, solo en tierra.
-- Lee el atributo Misiones ("texto|progreso|meta|premio;..."), que escribe el servidor al aterrizar. SIN PROBAR EN STUDIO.
local Players = game:GetService("Players")
local plr = Players.LocalPlayer
local T = require(script.Parent:WaitForChild("Tema"))
local C = T.col

local gui = T.n("ScreenGui", { Name = "Mas1Misiones", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 4 }, plr:WaitForChild("PlayerGui"))
T.escala(gui)
local panel = T.panel(gui, { Size = UDim2.fromOffset(300, 252), Position = UDim2.fromOffset(24, 236) }, C.morado)
T.texto(panel, { Text = "MISIONES", TextSize = 24, TextColor3 = C.sol, Size = UDim2.new(1, 0, 0, 34), Position = UDim2.fromOffset(0, 6) })
local filas = {}
for i = 1, 3 do
	local y = 46 + (i - 1) * 68
	local t = T.texto(panel, { Text = "", TextSize = 18, TextXAlignment = Enum.TextXAlignment.Left, Size = UDim2.new(1, -20, 0, 22), Position = UDim2.fromOffset(12, y) })
	local b = T.barra(panel, { Size = UDim2.new(1, -24, 0, 22), Position = UDim2.fromOffset(12, y + 26) })
	filas[i] = { t = t, b = b }
end

local function pintar()
	local s = plr:GetAttribute("Misiones") or ""
	local i = 0
	for texto, prog, meta, premio in string.gmatch(s, "([^|;]+)|(%d+)|(%d+)|(%d+)") do
		i = i + 1
		local f = filas[i]
		if not f then break end
		f.t.Text = string.format("%s  %s/%s  ·  +%s", texto, prog, meta, premio)
		f.b.set(tonumber(prog) / tonumber(meta), tonumber(prog) / tonumber(meta) >= 1 and C.menta or C.cielo)
	end
end
plr:GetAttributeChangedSignal("Misiones"):Connect(pintar)
pintar()
local function ver() panel.Visible = plr:GetAttribute("EnVuelo") ~= true end
plr:GetAttributeChangedSignal("EnVuelo"):Connect(ver)
ver()
