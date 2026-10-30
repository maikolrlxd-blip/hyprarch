-- Pantalla de resultados del vuelo de «+1 de lanzamiento por segundo»: aparece al aterrizar (MAS1_Resultado), cuenta hacia arriba
-- la distancia, el multiplicador de zona, el dinero y la exp, y ofrece ¡OTRA VEZ! (lanzar de nuevo). Sustituye al cartel provisional
-- de VueloControl. Datos de CONTRATO.md. SIN PROBAR EN STUDIO.
local Players, RS, TweenService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("TweenService")
local plr = Players.LocalPlayer
local Mas1 = RS:WaitForChild("Mas1")
local Red = require(Mas1:WaitForChild("Red"))
local T = require(script.Parent:WaitForChild("Tema"))
local accion, resultado = Red.evento("MAS1_Accion"), Red.evento("MAS1_Resultado")

local gui = T.n("ScreenGui", { Name = "Mas1Resultados", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 20 }, plr:WaitForChild("PlayerGui"))
T.escala(gui)
local actual -- panel abierto

local function cerrar()
	if actual then actual:Destroy(); actual = nil end
end

local function fila(padre, y, nombre, color)
	local f = T.panel(padre, { Size = UDim2.new(1, -40, 0, 54), Position = UDim2.new(0, 20, 0, y) }, color)
	T.texto(f, { Text = nombre, TextSize = 26, TextXAlignment = Enum.TextXAlignment.Left, Size = UDim2.new(0.5, -14, 1, 0), Position = UDim2.fromOffset(16, 0) })
	local v = T.texto(f, { Text = "0", TextSize = 32, TextXAlignment = Enum.TextXAlignment.Right, Size = UDim2.new(0.5, -16, 1, 0), Position = UDim2.new(0.5, 0, 0, 0) })
	return v
end

-- cuenta de 0 al valor en 'dur' segundos, con formato opcional
local function contar(etiqueta, valor, dur, formato)
	task.spawn(function()
		local t0 = os.clock()
		while etiqueta.Parent do
			local a = math.min((os.clock() - t0) / dur, 1)
			local x = 1 - (1 - a) * (1 - a) -- frena al final
			etiqueta.Text = formato(math.floor(valor * x + 0.5))
			if a >= 1 then break end
			task.wait()
		end
	end)
end

resultado.OnClientEvent:Connect(function(r)
	cerrar()
	local raiz = T.n("Frame", { Size = UDim2.fromOffset(560, 470), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 1.6), BackgroundTransparency = 1 }, gui)
	actual = raiz
	local p = T.panel(raiz, { Size = UDim2.fromScale(1, 1), Position = UDim2.fromScale(0, 0) }, T.col.violeta)
	T.texto(p, { Text = "¡ATERRIZAJE!", TextSize = 50, TextColor3 = T.col.sol, Size = UDim2.new(1, 0, 0, 64), Position = UDim2.fromOffset(0, 12) })
	local d = fila(p, 90, "Distancia", T.col.morado)
	local m = fila(p, 154, "Zona", T.col.cielo)
	local di = fila(p, 218, "Dinero", T.col.menta)
	local ex = fila(p, 282, "Exp", T.col.rosa)
	contar(d, r.distancia or 0, 0.9, function(n) return n .. " m" end)
	m.Text = "x" .. (r.multiplicador or 1)
	contar(di, r.dinero or 0, 1.2, function(n) return "+" .. n end)
	contar(ex, r.exp or 0, 1.2, function(n) return "+" .. n end)
	T.texto(p, { Text = string.format("%d aros  ·  %d golpes", r.aros or 0, r.golpes or 0), TextSize = 22, TextColor3 = T.col.crema, Size = UDim2.new(1, 0, 0, 30), Position = UDim2.fromOffset(0, 346) })
	T.boton(raiz, { Size = UDim2.fromOffset(280, 70), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 1, -62), Text = "¡OTRA VEZ!" }, T.col.sol, function()
		cerrar()
		accion:FireServer("lanzar")
	end)
	TweenService:Create(raiz, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = UDim2.fromScale(0.5, 0.45) }):Play()
	task.delay(12, function() if actual == raiz then cerrar() end end)
end)

-- al volver a volar se esconde
plr:GetAttributeChangedSignal("EnVuelo"):Connect(function()
	if plr:GetAttribute("EnVuelo") == true then cerrar() end
end)
