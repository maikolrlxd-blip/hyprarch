-- Rebirth y avisos de «+1 de lanzamiento por segundo»: boton REBIRTH (solo en tierra) con un panel de confirmacion que muestra
-- potencia, coste y rebirths; y los avisos de texto del servidor (MAS1_Aviso). El servidor decide: aqui solo se manda "rebirth".
-- Reinicia SOLO la potencia; conserva alas, mascotas, puntos y desbloqueos. Lee atributos Potencia, CosteRebirth, Rebirths, Entreno.
-- SIN PROBAR EN STUDIO.
local Players, RS, TweenService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("TweenService")
local plr = Players.LocalPlayer
local Mas1 = RS:WaitForChild("Mas1")
local Red = require(Mas1:WaitForChild("Red"))
local T = require(script.Parent:WaitForChild("Tema"))
local C, n = T.col, T.n
local accion, aviso = Red.evento("MAS1_Accion"), Red.evento("MAS1_Aviso")

local gui = n("ScreenGui", { Name = "Mas1Rebirth", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 15 }, plr:WaitForChild("PlayerGui"))
T.escala(gui)

local function fmt(x)
	local s = tostring(math.floor((x or 0) + 0.5))
	local out = s:reverse():gsub("(%d%d%d)", "%1."):reverse()
	return (out:gsub("^%.", ""))
end

-- avisos de texto (arriba, bajo la energia)
local toastActual
aviso.OnClientEvent:Connect(function(texto)
	if toastActual then toastActual:Destroy() end
	local p = T.panel(gui, { Size = UDim2.fromOffset(520, 64), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, -90) }, C.rosa)
	toastActual = p
	T.texto(p, { Text = tostring(texto), TextSize = 26, TextWrapped = true, Size = UDim2.new(1, -24, 1, 0), Position = UDim2.fromOffset(12, 0) })
	TweenService:Create(p, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = UDim2.new(0.5, 0, 0, 120) }):Play()
	task.delay(3, function()
		if toastActual == p then
			TweenService:Create(p, TweenInfo.new(0.25), { Position = UDim2.new(0.5, 0, 0, -90) }):Play()
			task.delay(0.3, function() if p.Parent then p:Destroy() end if toastActual == p then toastActual = nil end end)
		end
	end)
end)

-- panel de rebirth
local panel
local function cerrar() if panel then panel:Destroy(); panel = nil end end

local function abrir()
	if plr:GetAttribute("EnVuelo") == true then return end
	if panel then cerrar() return end
	local pot, coste, rb = plr:GetAttribute("Potencia") or 0, plr:GetAttribute("CosteRebirth") or 500, plr:GetAttribute("Rebirths") or 0
	local alcanza = pot >= coste
	panel = T.panel(gui, { Size = UDim2.fromOffset(560, 420), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5) }, C.violeta)
	T.texto(panel, { Text = "REBIRTH", TextSize = 52, TextColor3 = C.sol, Size = UDim2.new(1, 0, 0, 64), Position = UDim2.fromOffset(0, 12) })
	T.texto(panel, { Text = string.format("Rebirths: %d", rb), TextSize = 26, Size = UDim2.new(1, 0, 0, 30), Position = UDim2.fromOffset(0, 78) })
	local barra = T.barra(panel, { Size = UDim2.new(1, -60, 0, 44), Position = UDim2.fromOffset(30, 124) })
	barra.set(math.min(pot / coste, 1), alcanza and C.menta or C.sol)
	T.texto(panel, { Text = string.format("Potencia %s / %s", fmt(pot), fmt(coste)), TextSize = 28, Size = UDim2.new(1, 0, 0, 34), Position = UDim2.fromOffset(0, 176) })
	T.texto(panel, { Text = "Reinicia SOLO tu potencia. Conservas alas, mascotas y puntos. Entrenas más rápido y tus alas crecen.",
		TextSize = 20, TextWrapped = true, Size = UDim2.new(1, -60, 0, 80), Position = UDim2.fromOffset(30, 220) })
	local ok = T.boton(panel, { Size = UDim2.fromOffset(250, 66), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.3, 0, 1, -24), Text = alcanza and "¡REBIRTH!" or "FALTA POTENCIA" },
		alcanza and C.menta or Color3.fromRGB(110, 100, 130), function()
			if alcanza then accion:FireServer("rebirth"); cerrar() end
		end)
	T.boton(panel, { Size = UDim2.fromOffset(200, 66), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.76, 0, 1, -24), Text = "CERRAR" }, C.rosa, cerrar)
end

local btn = T.boton(gui, { Size = UDim2.fromOffset(170, 64), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 210, 1, -20), Text = "REBIRTH" }, C.rosa, abrir)
local function ver()
	local vuela = plr:GetAttribute("EnVuelo") == true
	btn.Visible = not vuela
	if vuela then cerrar() end
end
plr:GetAttributeChangedSignal("EnVuelo"):Connect(ver)
ver()
-- si el rebirth se hace, el panel se cierra solo; al subir el contador se anima el boton
plr:GetAttributeChangedSignal("Rebirths"):Connect(function()
	cerrar()
	btn.Size = UDim2.fromOffset(210, 80)
	TweenService:Create(btn, TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Size = UDim2.fromOffset(170, 64) }):Play()
end)
