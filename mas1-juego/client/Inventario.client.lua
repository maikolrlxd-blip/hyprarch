-- Inventario de «+1 de lanzamiento por segundo»: pestañas MASCOTAS (equipar hasta 3), HUEVOS (abrir con dinero) y ALAS (comprar y
-- equipar). Revelado del huevo con rebote y color de rareza. Formas de eventos en CONTRATO.md (MAS1_Inventario, MAS1_Huevo,
-- MAS1_Accion). La UI NO calcula nada: manda intenciones y pinta lo que diga el servidor. SIN PROBAR EN STUDIO.
local Players, RS, UIS, TweenService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("UserInputService"), game:GetService("TweenService")
local plr = Players.LocalPlayer
local Mas1 = RS:WaitForChild("Mas1")
local M = require(Mas1:WaitForChild("Mascotas"))
local okA, Alas = pcall(function() return require(Mas1:WaitForChild("Alas", 3)) end) -- hito 6: lista de alas con precio y requisitos
if not okA then Alas = nil end
local Red = require(Mas1:WaitForChild("Red"))
local T = require(script.Parent:WaitForChild("Tema"))
local C, n = T.col, T.n
local accion, evInv, evHuevo = Red.evento("MAS1_Accion"), Red.evento("MAS1_Inventario"), Red.evento("MAS1_Huevo")

local COLOR = { comun = Color3.fromRGB(190, 190, 200), poco_comun = Color3.fromRGB(110, 210, 120), raro = Color3.fromRGB(80, 160, 255),
	epico = Color3.fromRGB(170, 100, 255), legendario = Color3.fromRGB(255, 190, 40), mitico = Color3.fromRGB(255, 80, 140), robux = Color3.fromRGB(255, 120, 40) }
local NOMBRE = { comun = "Común", poco_comun = "Poco común", raro = "Raro", epico = "Épico", legendario = "Legendario", mitico = "Mítico", robux = "Robux" }
local STAT = { impulso = "Impulso", resistencia = "Resistencia", dinero = "Dinero", exp = "Exp" }

local inv = { mascotas = {}, equipadas = {}, alas = {}, alaEquipada = nil }

local gui = n("ScreenGui", { Name = "Mas1Inventario", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 10 }, plr:WaitForChild("PlayerGui"))
T.escala(gui)

local panel, pestana = nil, "mascotas"
local pintar

local function bonusTexto(p)
	local t = {}
	for _, s in ipairs(M.STATS) do if p.bonus[s] then t[#t + 1] = STAT[s] .. " +" .. p.bonus[s] .. "%" end end
	return table.concat(t, "  ·  ")
end

local function tarjeta(padre, p, cant, x, y, equipada)
	local c = T.panel(padre, { Size = UDim2.fromOffset(250, 150), Position = UDim2.fromOffset(x, y) }, equipada and C.sol or C.morado)
	n("Frame", { Size = UDim2.new(1, 0, 0, 8), BackgroundColor3 = COLOR[p.rareza], BorderSizePixel = 0 }, c)
	T.texto(c, { Text = p.nombre, TextSize = 24, TextColor3 = equipada and C.tinta or C.crema, TextStrokeTransparency = equipada and 1 or 0.55, Size = UDim2.new(1, -16, 0, 30), Position = UDim2.fromOffset(8, 14) })
	T.texto(c, { Text = NOMBRE[p.rareza] .. (cant > 1 and ("  x" .. cant) or ""), TextSize = 18, TextColor3 = COLOR[p.rareza], Size = UDim2.new(1, -16, 0, 22), Position = UDim2.fromOffset(8, 44) })
	T.texto(c, { Text = bonusTexto(p), TextSize = 16, TextWrapped = true, TextColor3 = equipada and C.tinta or C.crema, TextStrokeTransparency = equipada and 1 or 0.55, Size = UDim2.new(1, -16, 0, 44), Position = UDim2.fromOffset(8, 68) })
	local b = T.boton(c, { Size = UDim2.fromOffset(130, 34), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -6), Text = equipada and "QUITAR" or "EQUIPAR" }, equipada and C.rosa or C.menta, function()
		accion:FireServer(equipada and "desequipar" or "equipar", "mascota", p.id)
	end)
	b.TextSize = 18
	return c
end

local function paginaMascotas(cont)
	local y = 10
	T.texto(cont, { Text = string.format("EQUIPADAS %d / 3", #inv.equipadas), TextSize = 24, TextXAlignment = Enum.TextXAlignment.Left, Size = UDim2.new(1, -20, 0, 30), Position = UDim2.fromOffset(10, y) })
	y = y + 36
	local x = 10
	for _, id in ipairs(inv.equipadas) do
		local p = M.get(id)
		if p then tarjeta(cont, p, 1, x, y, true); x = x + 262 end
	end
	if #inv.equipadas == 0 then T.texto(cont, { Text = "Ninguna: equipa mascotas para ganar bonus.", TextSize = 20, Size = UDim2.new(1, -20, 0, 30), Position = UDim2.fromOffset(10, y + 8) }) end
	y = y + 168
	T.texto(cont, { Text = "TUS MASCOTAS", TextSize = 24, TextXAlignment = Enum.TextXAlignment.Left, Size = UDim2.new(1, -20, 0, 30), Position = UDim2.fromOffset(10, y) })
	y = y + 36
	local col, hay = 0, false
	for _, p in ipairs(M.LISTA) do
		local cant = inv.mascotas[p.id] or 0
		if cant > 0 then
			hay = true
			tarjeta(cont, p, cant, 10 + col * 262, y, false)
			col = col + 1
			if col == 3 then col, y = 0, y + 162 end
		end
	end
	if not hay then T.texto(cont, { Text = "Aún no tienes mascotas. ¡Abre un huevo!", TextSize = 22, Size = UDim2.new(1, -20, 0, 30), Position = UDim2.fromOffset(10, y) }) end
	cont.CanvasSize = UDim2.fromOffset(0, y + (col > 0 and 170 or 10) + 20)
end

local function paginaHuevos(cont)
	local dinero = plr:GetAttribute("Dinero") or 0
	local y = 10
	T.texto(cont, { Text = "Los huevos cuestan dinero. Más rareza, mejores mascotas.", TextSize = 20, TextXAlignment = Enum.TextXAlignment.Left, Size = UDim2.new(1, -20, 0, 26), Position = UDim2.fromOffset(10, y) })
	y = y + 36
	for _, r in ipairs({ "comun", "poco_comun", "raro", "epico", "legendario", "mitico" }) do
		local precio = M.PRECIO_HUEVO and M.PRECIO_HUEVO[r] -- lo pone el servidor en el hito 4
		local f = T.panel(cont, { Size = UDim2.new(1, -30, 0, 70), Position = UDim2.fromOffset(10, y) }, C.morado)
		n("Frame", { Size = UDim2.fromOffset(12, 70), BackgroundColor3 = COLOR[r], BorderSizePixel = 0 }, f)
		T.texto(f, { Text = "Huevo " .. string.lower(NOMBRE[r]), TextSize = 28, TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = COLOR[r], Size = UDim2.new(0.5, 0, 1, 0), Position = UDim2.fromOffset(28, 0) })
		local alcanza = precio and dinero >= precio
		local b = T.boton(f, { Size = UDim2.fromOffset(190, 46), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -12, 0.5, 0), Text = precio and ("ABRIR · " .. precio) or "ABRIR" },
			alcanza and C.sol or Color3.fromRGB(110, 100, 130), function() accion:FireServer("abrirHuevo", r) end)
		b.TextSize = 22
		y = y + 82
	end
	cont.CanvasSize = UDim2.fromOffset(0, y + 10)
end

local function paginaAlas(cont)
	local y = 10
	local lista = Alas and Alas.LISTA or {}
	if #lista == 0 then
		T.texto(cont, { Text = "Las alas llegan pronto.", TextSize = 24, Size = UDim2.new(1, -20, 0, 36), Position = UDim2.fromOffset(10, y) })
		return
	end
	for _, a in ipairs(lista) do
		local tiene = table.find(inv.alas, a.id) ~= nil
		local puesta = inv.alaEquipada == a.id
		local f = T.panel(cont, { Size = UDim2.new(1, -30, 0, 84), Position = UDim2.fromOffset(10, y) }, puesta and C.sol or C.morado)
		T.texto(f, { Text = a.nombre, TextSize = 28, TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = puesta and C.tinta or C.crema, TextStrokeTransparency = puesta and 1 or 0.55, Size = UDim2.new(0.55, 0, 0, 36), Position = UDim2.fromOffset(16, 6) })
		T.texto(f, { Text = a.requisito or "", TextSize = 17, TextXAlignment = Enum.TextXAlignment.Left, TextWrapped = true, TextColor3 = puesta and C.tinta or C.crema, TextStrokeTransparency = puesta and 1 or 0.55, Size = UDim2.new(0.55, 0, 0, 36), Position = UDim2.fromOffset(16, 42) })
		local texto = puesta and "QUITAR" or (tiene and "EQUIPAR" or (a.precio and ("COMPRAR · " .. a.precio) or "BLOQUEADA"))
		local b = T.boton(f, { Size = UDim2.fromOffset(200, 48), AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -12, 0.5, 0), Text = texto },
			puesta and C.rosa or (tiene and C.menta or C.sol), function()
				if puesta then accion:FireServer("desequipar", "ala", a.id)
				elseif tiene then accion:FireServer("equipar", "ala", a.id)
				else accion:FireServer("comprarAla", a.id) end
			end)
		b.TextSize = 20
		y = y + 96
	end
	cont.CanvasSize = UDim2.fromOffset(0, y + 10)
end

pintar = function()
	if not panel then return end
	local cont = panel:FindFirstChild("Contenido")
	if cont then cont:Destroy() end
	cont = n("ScrollingFrame", { Name = "Contenido", Size = UDim2.new(1, -30, 1, -140), Position = UDim2.fromOffset(15, 120), BackgroundTransparency = 1, BorderSizePixel = 0,
		ScrollBarThickness = 8, CanvasSize = UDim2.fromOffset(0, 600), AutomaticCanvasSize = Enum.AutomaticSize.None }, panel)
	if pestana == "mascotas" then paginaMascotas(cont) elseif pestana == "huevos" then paginaHuevos(cont) else paginaAlas(cont) end
end

local function cerrar() if panel then panel:Destroy(); panel = nil end end

local function abrir()
	if plr:GetAttribute("EnVuelo") == true then return end
	if panel then cerrar() return end
	panel = T.panel(gui, { Size = UDim2.fromOffset(820, 640), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5) }, C.violeta)
	T.texto(panel, { Text = "MASCOTAS Y ALAS", TextSize = 38, TextColor3 = C.sol, Size = UDim2.new(1, -80, 0, 48), Position = UDim2.fromOffset(20, 10), TextXAlignment = Enum.TextXAlignment.Left })
	local x = n("TextButton", { Text = "X", Font = T.fuente, TextSize = 26, TextColor3 = C.crema, BackgroundColor3 = C.rosa, Size = UDim2.fromOffset(46, 46), Position = UDim2.new(1, -58, 0, 10), BorderSizePixel = 0 }, panel)
	n("UICorner", { CornerRadius = UDim.new(1, 0) }, x); n("UIStroke", { Color = C.tinta, Thickness = 4 }, x)
	x.MouseButton1Click:Connect(cerrar)
	for i, par in ipairs({ { "mascotas", "MASCOTAS" }, { "huevos", "HUEVOS" }, { "alas", "ALAS" } }) do
		local activa = pestana == par[1]
		local b = n("TextButton", { Text = par[2], Font = T.fuente, TextSize = 24, TextColor3 = activa and C.tinta or C.crema, BackgroundColor3 = activa and C.sol or C.morado,
			Size = UDim2.fromOffset(150, 44), Position = UDim2.fromOffset(20 + (i - 1) * 160, 66), BorderSizePixel = 0 }, panel)
		n("UICorner", { CornerRadius = UDim.new(0, 12) }, b); n("UIStroke", { Color = C.tinta, Thickness = 4 }, b)
		b.MouseButton1Click:Connect(function() pestana = par[1]; cerrar(); abrir() end)
	end
	pintar()
end

-- boton de la esquina para abrir el inventario (y tecla B)
local btn = T.boton(gui, { Size = UDim2.fromOffset(170, 64), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 20, 1, -20), Text = "MASCOTAS" }, C.violeta, abrir)
local function verBtn() btn.Visible = plr:GetAttribute("EnVuelo") ~= true end
plr:GetAttributeChangedSignal("EnVuelo"):Connect(function() verBtn(); if plr:GetAttribute("EnVuelo") == true then cerrar() end end)
verBtn()
UIS.InputBegan:Connect(function(i, gp) if not gp and i.KeyCode == Enum.KeyCode.B then abrir() end end)

evInv.OnClientEvent:Connect(function(d)
	inv = { mascotas = d.mascotas or {}, equipadas = d.equipadas or {}, alas = d.alas or {}, alaEquipada = d.alaEquipada }
	pintar()
end)
plr:GetAttributeChangedSignal("Dinero"):Connect(function() if panel and pestana == "huevos" then pintar() end end)

-- revelado del huevo: sacude, estalla y muestra la mascota con el color de su rareza
evHuevo.OnClientEvent:Connect(function(d)
	local p = M.get(d.mascotaId)
	if not p then return end
	local fondo = n("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = C.tinta, BackgroundTransparency = 0.35, BorderSizePixel = 0, ZIndex = 50 }, gui)
	local huevo = T.texto(fondo, { Text = "🥚", TextSize = 140, Size = UDim2.fromOffset(200, 200), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.45), ZIndex = 51 })
	task.spawn(function()
		for i = 1, 10 do huevo.Rotation = (i % 2 == 0 and 14 or -14); task.wait(0.07) end
		huevo:Destroy()
		local tarj = T.panel(fondo, { Size = UDim2.fromOffset(420, 300), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.45), ZIndex = 52 }, COLOR[p.rareza])
		T.texto(tarj, { Text = d.nueva and "¡NUEVA!" or "¡OTRA VEZ!", TextSize = 28, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.new(1, 0, 0, 36), Position = UDim2.fromOffset(0, 12), ZIndex = 53 })
		T.texto(tarj, { Text = p.nombre, TextSize = 44, Size = UDim2.new(1, -20, 0, 56), Position = UDim2.fromOffset(10, 60), ZIndex = 53 })
		T.texto(tarj, { Text = string.upper(NOMBRE[p.rareza]), TextSize = 28, TextColor3 = C.tinta, TextStrokeTransparency = 1, Size = UDim2.new(1, 0, 0, 34), Position = UDim2.fromOffset(0, 124), ZIndex = 53 })
		T.texto(tarj, { Text = bonusTexto(p), TextSize = 20, TextWrapped = true, Size = UDim2.new(1, -30, 0, 70), Position = UDim2.fromOffset(15, 172), ZIndex = 53 })
		tarj.Size = UDim2.fromOffset(120, 90)
		TweenService:Create(tarj, TweenInfo.new(0.4, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Size = UDim2.fromOffset(420, 300) }):Play()
		task.wait(3)
		fondo:Destroy()
	end)
end)
