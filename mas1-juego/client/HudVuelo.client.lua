-- HUD de vuelo de «+1 de lanzamiento por segundo». Lee atributos del jugador local (los pone el juego o DemoVisual.server.lua):
-- Energia (0-1), Potencia, Puntos, Distancia (m), ZonaMult, Aros, ArosTotal, Mascota (nombre), MascotaBonus (numero). SIN PROBAR EN STUDIO.
local Players, RS, UIS = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local plr = Players.LocalPlayer
local T = require(script.Parent:WaitForChild("Tema"))
local C, n = T.col, T.n
local accion = RS:WaitForChild("MAS1_Accion", 3) -- RemoteEvent opcional (puno / patada / turbo)

local gui = n("ScreenGui", { Name = "Mas1Hud", ResetOnSpawn = false, IgnoreGuiInset = true, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, plr:WaitForChild("PlayerGui"))
T.escala(gui)

local function fmt(x) -- 12480 -> "12.480"
	local s = tostring(math.floor(x + 0.5)); local out = s:reverse():gsub("(%d%d%d)", "%1."):reverse()
	return (out:gsub("^%.", ""))
end
local function pop(label) -- pequeno rebote al cambiar un numero
	label.TextSize = label:GetAttribute("base") * 1.25
	TweenService:Create(label, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { TextSize = label:GetAttribute("base") }):Play()
end
local function numero(padre, texto, color) -- etiqueta pequeña + número grande; devuelve el número
	T.texto(padre, { Text = string.upper(texto), TextSize = 17, Size = UDim2.new(1, -24, 0, 20), Position = UDim2.fromOffset(14, 6), TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = color or C.crema })
	local l = T.texto(padre, { Text = "0", TextSize = 42, Size = UDim2.new(1, -24, 0, 46), Position = UDim2.fromOffset(14, 26), TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = color or C.crema })
	l:SetAttribute("base", 42); return l
end

-- Energia (arriba al centro)
local pEn = T.panel(gui, { Size = UDim2.fromOffset(620, 84), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 18) }, C.crema)
T.texto(pEn, { Text = "ENERGÍA", TextSize = 20, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.fromOffset(200, 24), Position = UDim2.fromOffset(18, 6), TextXAlignment = Enum.TextXAlignment.Left })
local tEnPct = T.texto(pEn, { Text = "100%", TextSize = 28, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.fromOffset(120, 28), Position = UDim2.new(1, -138, 0, 4), TextXAlignment = Enum.TextXAlignment.Right })
local bEn = T.barra(pEn, { Size = UDim2.new(1, -36, 0, 30), Position = UDim2.fromOffset(18, 40) })

local pPun = T.panel(gui, { Size = UDim2.fromOffset(300, 84), Position = UDim2.fromOffset(24, 18) }, C.rosa)
local tPun = numero(pPun, "puntos del vuelo")
local pDis = T.panel(gui, { Size = UDim2.fromOffset(300, 84), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -24, 0, 18) }, C.cielo)
local tDis = numero(pDis, "distancia", C.tinta); tDis.TextXAlignment = Enum.TextXAlignment.Right
local pPot = T.panel(gui, { Size = UDim2.fromOffset(250, 84), Position = UDim2.fromOffset(24, 122) }, C.menta)
local tPot = numero(pPot, "potencia")
local pAro = T.panel(gui, { Size = UDim2.fromOffset(250, 84), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -24, 0, 122) }, C.crema)
local tAro = numero(pAro, "aros", C.tinta)

-- Multiplicador de zona (centro, inclinado)
local pMul = T.panel(gui, { Size = UDim2.fromOffset(200, 96), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 114), Rotation = -3 }, C.sol)
T.texto(pMul, { Text = "ZONA", TextSize = 17, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.new(1, 0, 0, 20), Position = UDim2.fromOffset(0, 6) })
local tMul = T.texto(pMul, { Text = "x1", TextSize = 58, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.new(1, 0, 0, 64), Position = UDim2.fromOffset(0, 24) }); tMul:SetAttribute("base", 58)

-- Mascota (abajo a la izquierda)
local pMas = T.panel(gui, { Size = UDim2.fromOffset(280, 92), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 24, 1, -34) }, C.crema)
T.texto(pMas, { Text = "MASCOTA", TextSize = 16, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.new(1, -24, 0, 18), Position = UDim2.fromOffset(14, 6), TextXAlignment = Enum.TextXAlignment.Left })
local tMas = T.texto(pMas, { Text = "—", TextSize = 28, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.new(1, -24, 0, 32), Position = UDim2.fromOffset(14, 22), TextXAlignment = Enum.TextXAlignment.Left })
local chip = T.panel(pMas, { Size = UDim2.fromOffset(150, 28), Position = UDim2.fromOffset(14, 56) }, C.menta); chip.UIStroke.Thickness = 3
local tChip = T.texto(chip, { Text = "x1 ganancias", TextSize = 18, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.fromScale(1, 1) })

-- Botones (movil y escritorio; en escritorio: clic = puño, E = patada, W = turbo; son PROPUESTAS)
local function lanzar(nombre) if accion then accion:FireServer(nombre) end end
local bPuno = T.boton(gui, { Size = UDim2.fromOffset(130, 130), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -150, 1, -60), Text = "PUÑO" }, C.rosa, function() lanzar("puno") end)
local bPat = T.boton(gui, { Size = UDim2.fromOffset(110, 110), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -34, 1, -130), Text = "PATADA" }, C.sol, function() lanzar("patada") end); bPat.TextColor3 = C.tinta
local bTur = T.boton(gui, { Size = UDim2.fromOffset(100, 100), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -300, 1, -34), Text = "TURBO" }, C.menta, function() lanzar("turbo") end); bTur.TextColor3 = C.tinta
if not UIS.TouchEnabled then
	for _, b in ipairs({ bPuno, bPat, bTur }) do b.Active = false end
	local focoDesde = 0 -- el clic que da el foco a la ventana no es un golpe
	UIS.WindowFocused:Connect(function() focoDesde = os.clock() end)
	UIS.InputBegan:Connect(function(i, gp)
		if gp or plr:GetAttribute("EnVuelo") ~= true then return end -- solo se golpea volando
		if i.UserInputType == Enum.UserInputType.MouseButton1 and os.clock() - focoDesde < 0.4 then return end
		if i.UserInputType == Enum.UserInputType.MouseButton1 then lanzar("puno") elseif i.KeyCode == Enum.KeyCode.E then lanzar("patada") elseif i.KeyCode == Enum.KeyCode.W then lanzar("turbo") end
	end)
end

-- Actualizacion desde atributos
local ultimo = {}
local function refrescar()
	local en = math.clamp(plr:GetAttribute("Energia") or 1, 0, 1)
	bEn.set(en, en > 0.5 and C.sol or (en > 0.2 and Color3.fromRGB(255, 150, 40) or C.rosa)); tEnPct.Text = math.floor(en * 100 + 0.5) .. "%"
	for _, d in ipairs({ { "Puntos", tPun }, { "Distancia", tDis }, { "Potencia", tPot } }) do
		local v = plr:GetAttribute(d[1]) or 0
		d[2].Text = (d[1] == "Distancia" and (fmt(v) .. " m")) or (d[1] == "Potencia" and ("+" .. fmt(v))) or fmt(v)
		if ultimo[d[1]] and ultimo[d[1]] ~= v then pop(d[2]) end; ultimo[d[1]] = v
	end
	local m = plr:GetAttribute("ZonaMult") or 1; tMul.Text = "x" .. m
	if ultimo.m and ultimo.m ~= m then pop(tMul) end; ultimo.m = m
	tAro.Text = (plr:GetAttribute("Aros") or 0) .. " / " .. (plr:GetAttribute("ArosTotal") or 0)
	tMas.Text = plr:GetAttribute("Mascota") or "—"; tChip.Text = "x" .. tostring(plr:GetAttribute("MascotaBonus") or 1) .. " ganancias"
end
for _, a in ipairs({ "Energia", "Potencia", "Puntos", "Distancia", "ZonaMult", "Aros", "ArosTotal", "Mascota", "MascotaBonus" }) do plr:GetAttributeChangedSignal(a):Connect(refrescar) end
refrescar()
