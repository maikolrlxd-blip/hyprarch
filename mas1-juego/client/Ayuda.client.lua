-- Ayuda de mandos de «+1 de lanzamiento por segundo»: un jugador nuevo no sabe que A/D mueven ni que W da boost. Muestra una tira
-- de mandos arriba (teclado o movil) durante los primeros vuelos de la sesion y un consejo en tierra antes del primer lanzamiento.
-- Sin imagenes. SIN PROBAR EN STUDIO.
local Players, UIS = game:GetService("Players"), game:GetService("UserInputService")
local plr = Players.LocalPlayer
local T = require(script.Parent:WaitForChild("Tema"))
local C = T.col

local gui = T.n("ScreenGui", { Name = "Mas1Ayuda", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 5 }, plr:WaitForChild("PlayerGui"))
T.escala(gui)

local movil = UIS.TouchEnabled and not UIS.KeyboardEnabled
local MANDOS = movil
	and { { "JOYSTICK", "mover y boost" }, { "SALTO", "subir" }, { "PUÑO / PATADA", "golpear" } }
	or { { "A / D", "a los lados" }, { "W", "boost" }, { "ESPACIO / S", "subir / bajar" }, { "CLIC", "puño" }, { "E", "patada" } }

-- tira de mandos durante el vuelo
local ancho = #MANDOS * 170
local tira = T.panel(gui, { Size = UDim2.fromOffset(ancho, 78), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -110), Visible = false }, C.tinta)
for i, m in ipairs(MANDOS) do
	T.texto(tira, { Text = m[1], TextSize = 24, TextColor3 = C.sol, Size = UDim2.fromOffset(170, 30), Position = UDim2.fromOffset((i - 1) * 170, 8) })
	T.texto(tira, { Text = m[2], TextSize = 18, Size = UDim2.fromOffset(170, 26), Position = UDim2.fromOffset((i - 1) * 170, 40) })
end

-- consejo en tierra
local consejo = T.panel(gui, { Size = UDim2.fromOffset(560, 70), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -130), Visible = false }, C.cielo)
T.texto(consejo, { Text = movil and "Toca ¡LANZAR! para salir volando" or "Pulsa F o ¡LANZAR! para salir volando", TextSize = 26, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.fromScale(1, 1) })

local vuelos = 0
local function refrescar()
	local vuela = plr:GetAttribute("EnVuelo") == true
	tira.Visible = vuela and vuelos <= 3
	consejo.Visible = (not vuela) and vuelos == 0
end
plr:GetAttributeChangedSignal("EnVuelo"):Connect(function()
	if plr:GetAttribute("EnVuelo") == true then
		vuelos = vuelos + 1
		refrescar()
		local este = vuelos
		task.delay(12, function() if vuelos == este then tira.Visible = false end end) -- se esconde solo a los 12 s
	else
		refrescar()
	end
end)
refrescar()
