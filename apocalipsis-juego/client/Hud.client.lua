-- HUD de Luto (rediseno): ronda, equipo, vida y monedas, arma y municion, mira con marcador de impacto, anuncios, jefe, vineta de dano,
-- pantalla de fin y avisos de tienda. Reemplaza a las etiquetas de texto provisionales. SIN PROBAR EN STUDIO (solo sintaxis comprobada).
local Players, RS, UIS = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local PPS = game:GetService("ProximityPromptService")
local plr = Players.LocalPlayer
local Tema = require(script.Parent:WaitForChild("ui"):WaitForChild("Tema"))
local C, n, E = Tema.col, Tema.n, Tema.etiqueta
local RPartida, REstado, RImpacto = RS:WaitForChild("LUTO_Partida"), RS:WaitForChild("LUTO_Estado"), RS:WaitForChild("LUTO_Impacto")

pcall(function() game:GetService("StarterGui"):SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) end) -- evita que la lista de jugadores se monte con el equipo
local gui = n("ScreenGui", { Name = "LutoHud", ResetOnSpawn = false, IgnoreGuiInset = true, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, plr:WaitForChild("PlayerGui"))
Tema.escala(gui)

-- ===== Vineta de dano (4 bordes rojos con degradado) =====
local vineta = {}
for _, d in ipairs({ { "T", UDim2.new(1, 0, 0, 160), UDim2.new(0, 0, 0, 0), 90 }, { "B", UDim2.new(1, 0, 0, 160), UDim2.new(0, 0, 1, -160), 270 },
	{ "L", UDim2.new(0, 160, 1, 0), UDim2.new(0, 0, 0, 0), 0 }, { "R", UDim2.new(0, 160, 1, 0), UDim2.new(1, -160, 0, 0), 180 } }) do
	local f = n("Frame", { Size = d[2], Position = d[3], BackgroundColor3 = Color3.fromRGB(150, 20, 20), BackgroundTransparency = 1, BorderSizePixel = 0, Active = false }, gui)
	n("UIGradient", { Rotation = d[4], Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) }) }, f)
	vineta[#vineta + 1] = f
end
local function destello(fuerza)
	for _, f in ipairs(vineta) do
		f.BackgroundTransparency = 1 - fuerza
		TweenService:Create(f, TweenInfo.new(0.5), { BackgroundTransparency = 1 }):Play()
	end
end

-- ===== Panel de ronda (arriba al centro) =====
local pRonda = Tema.panel(gui, { Size = UDim2.fromOffset(340, 92), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 18) })
E(pRonda, { Text = "ronda", TextSize = 17, TextColor3 = C.mut, Size = UDim2.new(1, 0, 0, 18), Position = UDim2.fromOffset(0, 6) })
local tRonda = E(pRonda, { Text = "--", TextSize = 46, Font = Enum.Font.Oswald, Size = UDim2.new(1, 0, 0, 46), Position = UDim2.fromOffset(0, 18) })
local tZombis = E(pRonda, { Text = "", TextSize = 16, TextColor3 = C.mut, Size = UDim2.new(1, 0, 0, 20), Position = UDim2.new(0, 0, 1, -26) })
local tSiguiente = E(gui, { Text = "", TextSize = 18, TextColor3 = C.ambar, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 118), Size = UDim2.fromOffset(340, 24) })

-- ===== Jefe (banner bajo el panel de ronda) =====
local pJefe = Tema.panel(gui, { Size = UDim2.fromOffset(440, 54), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 146), Visible = false })
local tJefe = E(pJefe, { Text = "jefe", TextSize = 22, TextColor3 = Color3.fromRGB(225, 85, 85), Size = UDim2.new(1, 0, 0, 22), Position = UDim2.fromOffset(0, 4) })
local bJefe = Tema.barra(pJefe, { Size = UDim2.new(1, -28, 0, 12), Position = UDim2.new(0, 14, 1, -22) }); bJefe.relleno.BackgroundColor3 = C.rojo

-- ===== Equipo (arriba a la izquierda) =====
local pEquipo = Tema.panel(gui, { Size = UDim2.fromOffset(250, 40), Position = UDim2.fromOffset(28, 18), Visible = false })
E(pEquipo, { Text = "equipo", TextSize = 16, TextColor3 = C.mut, Size = UDim2.new(1, -16, 0, 16), Position = UDim2.fromOffset(10, 4), TextXAlignment = Enum.TextXAlignment.Left })
local filasEquipo = {}

-- ===== Vida y monedas (abajo a la izquierda) =====
local pVida = Tema.panel(gui, { Size = UDim2.fromOffset(380, 118), AnchorPoint = Vector2.new(0, 1), Position = UDim2.new(0, 28, 1, -28) })
E(pVida, { Text = "vida", TextSize = 17, TextColor3 = C.mut, Size = UDim2.fromOffset(80, 18), Position = UDim2.fromOffset(16, 10), TextXAlignment = Enum.TextXAlignment.Left })
local tVida = E(pVida, { Text = "100", TextSize = 34, Size = UDim2.fromOffset(120, 36), Position = UDim2.new(1, -136, 0, 4), TextXAlignment = Enum.TextXAlignment.Right })
local bVida = Tema.barra(pVida, { Size = UDim2.new(1, -32, 0, 16), Position = UDim2.fromOffset(16, 46) })
local rombo = n("Frame", { Size = UDim2.fromOffset(16, 16), Position = UDim2.fromOffset(22, 80), Rotation = 45, BackgroundColor3 = C.ambar, BorderSizePixel = 0 }, pVida)
n("UIStroke", { Color = Color3.fromRGB(138, 106, 28), Thickness = 2 }, rombo)
local tMonedas = E(pVida, { Text = "0", TextSize = 28, TextColor3 = C.ambar, Size = UDim2.fromOffset(120, 32), Position = UDim2.fromOffset(46, 72), TextXAlignment = Enum.TextXAlignment.Left })
E(pVida, { Text = "monedas", TextSize = 16, TextColor3 = C.mut, Size = UDim2.fromOffset(100, 18), Position = UDim2.fromOffset(150, 80), TextXAlignment = Enum.TextXAlignment.Left })

-- ===== Arma y municion (abajo a la derecha) =====
local pArma = Tema.panel(gui, { Size = UDim2.fromOffset(380, 150), AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -28, 1, -28) })
local tNombreArma = E(pArma, { Text = "pistola", TextSize = 20, TextColor3 = C.mut, Size = UDim2.new(1, -36, 0, 24), Position = UDim2.fromOffset(18, 8), TextXAlignment = Enum.TextXAlignment.Left })
local tMuni = E(pArma, { Text = "15", TextSize = 62, Size = UDim2.fromOffset(150, 66), Position = UDim2.fromOffset(16, 28), TextXAlignment = Enum.TextXAlignment.Left })
local tReserva = E(pArma, { Text = "/ 90", TextSize = 26, TextColor3 = C.mut, Size = UDim2.fromOffset(110, 30), Position = UDim2.fromOffset(150, 62), TextXAlignment = Enum.TextXAlignment.Left })
local tEstadoArma = E(pArma, { Text = "", TextSize = 18, TextColor3 = C.ambar, Size = UDim2.fromOffset(180, 24), Position = UDim2.new(1, -196, 0, 34), TextXAlignment = Enum.TextXAlignment.Right })
local ranuras = {}
for i, id in ipairs({ "pistola", "escopeta", "subfusil" }) do
	local r = n("Frame", { Size = UDim2.new(1 / 3, -8, 0, 34), Position = UDim2.new((i - 1) / 3, 18 - (i - 1) * 2, 1, -48), BackgroundColor3 = C.negro, BackgroundTransparency = 0.4, BorderSizePixel = 0 }, pArma)
	r.Size = UDim2.fromOffset(110, 34); r.Position = UDim2.fromOffset(16 + (i - 1) * 120, 106)
	local st = n("UIStroke", { Color = C.linea, Thickness = 1 }, r)
	E(r, { Text = i .. "  " .. id, TextSize = 15, TextColor3 = C.mut, Size = UDim2.fromScale(1, 1) })
	ranuras[id] = { marco = r, trazo = st, txt = r:FindFirstChildOfClass("TextLabel") }
end
local armaActual, municion, tamCargador = "pistola", 15, { pistola = 15, escopeta = 6, subfusil = 30 }
local function marcarArma(id)
	for k, r in pairs(ranuras) do
		local on = k == id
		r.trazo.Color = on and C.ambar or C.linea; r.txt.TextColor3 = on and C.txt or C.mut
		r.marco.BackgroundColor3 = on and Color3.fromRGB(60, 50, 24) or C.negro
	end
end

REstado.OnClientEvent:Connect(function(s)
	if s.arma then
		armaActual = s.arma; marcarArma(s.arma)
		tNombreArma.Text = string.upper(s.nombre or s.arma)
		tMuni.Text = tostring(s.municion); tReserva.Text = "/ " .. s.reserva
		local frac = s.municion / (tamCargador[s.arma] or 15)
		tMuni.TextColor3 = (s.municion == 0 and C.rojo) or (frac <= 0.3 and C.ambar) or C.txt
		tEstadoArma.Text = s.recargando and "RECARGANDO…" or (s.municion == 0 and s.reserva == 0 and "SIN MUNICIÓN") or (s.municion == 0 and "RECARGA (R)") or ""
	end
	if s.inspeccionar then tEstadoArma.Text = "INSPECCIONANDO" end
end)
marcarArma("pistola")

-- ===== Mira con marcador de impacto =====
local mira = n("Frame", { Size = UDim2.fromOffset(0, 0), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), BackgroundTransparency = 1 }, gui)
local brazos, hueco = {}, 8
local function brazo(dx, dy, w, h)
	local f = n("Frame", { Size = UDim2.fromOffset(w, h), AnchorPoint = Vector2.new(0.5, 0.5), BackgroundColor3 = Color3.new(1, 1, 1), BorderSizePixel = 0 }, mira)
	n("UIStroke", { Color = Color3.new(0, 0, 0), Transparency = 0.4, Thickness = 1 }, f)
	brazos[#brazos + 1] = { f = f, dx = dx, dy = dy }
end
brazo(0, -1, 2, 10); brazo(0, 1, 2, 10); brazo(-1, 0, 10, 2); brazo(1, 0, 10, 2)
local function ajustarMira(extra)
	for _, b in ipairs(brazos) do
		b.f.Position = UDim2.fromOffset(b.dx * (hueco + 5 + extra), b.dy * (hueco + 5 + extra))
	end
end
ajustarMira(0)
local marcador = n("Frame", { Size = UDim2.fromOffset(26, 26), AnchorPoint = Vector2.new(0.5, 0.5), Rotation = 45, BackgroundTransparency = 1, Visible = false }, mira)
local marcadorTrazo = n("UIStroke", { Color = C.rojo, Thickness = 3 }, marcador)
UIS.InputBegan:Connect(function(i, gp)
	if gp then return end
	if i.UserInputType == Enum.UserInputType.MouseButton1 then ajustarMira(7); task.delay(0.08, function() ajustarMira(0) end) end
end)
RImpacto.OnClientEvent:Connect(function(d)
	if typeof(d) == "table" and d.tirador == plr.UserId and d.enemigo then
		marcador.Visible = true; marcadorTrazo.Color = d.cabeza and C.ambar or C.rojo
		task.delay(0.12, function() marcador.Visible = false end)
	end
end)

-- ===== Anuncio central =====
local anuncio = n("Frame", { Size = UDim2.fromOffset(700, 130), AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 230), BackgroundTransparency = 1, Visible = false }, gui)
local aPeq = E(anuncio, { Text = "", TextSize = 26, TextColor3 = C.txt, TextStrokeTransparency = 0.4, TextStrokeColor3 = Color3.new(0, 0, 0), Size = UDim2.new(1, 0, 0, 26) })
local aGrande = E(anuncio, { Text = "", TextSize = 84, Size = UDim2.new(1, 0, 0, 90), Position = UDim2.fromOffset(0, 30), TextStrokeTransparency = 0.3, TextStrokeColor3 = Color3.new(0, 0, 0) })
local tokenAnuncio = 0
local function mostrarAnuncio(peq, grande, color, seg)
	tokenAnuncio = tokenAnuncio + 1; local mi = tokenAnuncio
	aPeq.Text = string.upper(peq); aGrande.Text = string.upper(grande); aGrande.TextColor3 = color or C.txt
	anuncio.Visible = true; aGrande.TextTransparency = 1; aPeq.TextTransparency = 1
	TweenService:Create(aGrande, TweenInfo.new(0.25), { TextTransparency = 0 }):Play(); TweenService:Create(aPeq, TweenInfo.new(0.25), { TextTransparency = 0 }):Play()
	task.delay(seg or 2.6, function()
		if tokenAnuncio ~= mi then return end
		TweenService:Create(aGrande, TweenInfo.new(0.5), { TextTransparency = 1 }):Play(); TweenService:Create(aPeq, TweenInfo.new(0.5), { TextTransparency = 1 }):Play()
		task.delay(0.55, function() if tokenAnuncio == mi then anuncio.Visible = false end end)
	end)
end

-- ===== Avisos y ganancias (columna a la derecha) =====
local feed = n("Frame", { Size = UDim2.fromOffset(280, 200), AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -28, 0, 90), BackgroundTransparency = 1 }, gui)
n("UIListLayout", { SortOrder = Enum.SortOrder.LayoutOrder, VerticalAlignment = Enum.VerticalAlignment.Top, Padding = UDim.new(0, 2) }, feed)
local orden = 0
local function entrada(texto, color)
	orden = orden + 1
	local l = E(feed, { Text = texto, TextSize = 20, TextColor3 = color or C.ambar, Size = UDim2.new(1, 0, 0, 26), TextXAlignment = Enum.TextXAlignment.Right, LayoutOrder = orden })
	task.delay(3, function()
		TweenService:Create(l, TweenInfo.new(0.5), { TextTransparency = 1 }):Play(); task.delay(0.55, function() l:Destroy() end)
	end)
end

-- ===== Fin de partida =====
local fin = Tema.panel(gui, { Size = UDim2.fromOffset(560, 300), AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Visible = false, BackgroundTransparency = 0.05, ZIndex = 5 })
E(fin, { Text = "luto", TextSize = 22, TextColor3 = C.rojo, Size = UDim2.new(1, 0, 0, 30), Position = UDim2.fromOffset(0, 16), ZIndex = 6 })
local fRonda = E(fin, { Text = "", TextSize = 64, Size = UDim2.new(1, 0, 0, 70), Position = UDim2.fromOffset(0, 46), ZIndex = 6 })
local fDetalle = E(fin, { Text = "", TextSize = 24, TextColor3 = C.mut, Size = UDim2.new(1, -40, 0, 90), Position = UDim2.fromOffset(20, 130), ZIndex = 6, TextWrapped = true })
local fNueva = E(fin, { Text = "", TextSize = 18, TextColor3 = C.ambar, Size = UDim2.new(1, 0, 0, 26), Position = UDim2.new(0, 0, 1, -42), ZIndex = 6 })
local tokenFin = 0

-- ===== Estado de la partida =====
local nombres = { esperando = "espera", intermision = "preparacion", ronda = "ronda", fin = "fin" }
RPartida.OnClientEvent:Connect(function(d)
	if d.fin then
		tokenFin = tokenFin + 1; local mi = tokenFin
		fin.Visible = true; fRonda.Text = "RONDA " .. d.rondaMax
		fDetalle.Text = string.format("BAJAS  %d\nMONEDAS DEL LOBBY  +%d", d.kills or 0, d.monedasLobby)
		task.spawn(function()
			for s = 12, 1, -1 do if tokenFin ~= mi then return end fNueva.Text = "NUEVA PARTIDA EN " .. s; task.wait(1) end
		end)
		return
	end
	if d.anuncio then
		mostrarAnuncio(d.anuncio.jefe and "cuidado" or "comienza la", d.anuncio.jefe and ("RONDA " .. d.anuncio.ronda .. " · JEFE") or ("RONDA " .. d.anuncio.ronda), d.anuncio.jefe and C.rojo or C.txt)
	end
	if d.ganancia then entrada("+" .. d.ganancia .. "  " .. (d.tipo or "ZOMBI")) end
	if d.msg then entrada(d.msg, C.txt) end
	if d.estado then
		tokenFin = tokenFin + 1; fin.Visible = false
		tRonda.Text = d.ronda > 0 and string.format("%02d", d.ronda) or "--"
		tZombis.Text = string.upper(string.format("zombis %d  ·  vivos %d/%d", d.restantes, d.vivos, d.total))
		tMonedas.Text = tostring(d.monedas)
		tSiguiente.Text = d.siguiente and string.upper("siguiente ronda en " .. d.siguiente) or (d.estado == "esperando" and "ESPERANDO JUGADORES…" or "")
		pJefe.Visible = d.jefeVida ~= nil
		if d.jefeVida then tJefe.Text = string.upper(d.jefeNombre or "jefe"); bJefe.set(d.jefeVida) end
		if d.equipo then
			pEquipo.Visible = #d.equipo > 1
			pEquipo.Size = UDim2.fromOffset(250, 28 + #d.equipo * 22)
			for i, m in ipairs(d.equipo) do
				local f = filasEquipo[i]
				if not f then
					f = { nombre = E(pEquipo, { Text = "", TextSize = 16, Size = UDim2.fromOffset(90, 20), Position = UDim2.fromOffset(10, 24 + (i - 1) * 22), TextXAlignment = Enum.TextXAlignment.Left }),
						barra = Tema.barra(pEquipo, { Size = UDim2.fromOffset(130, 10), Position = UDim2.fromOffset(106, 29 + (i - 1) * 22) }) }
					filasEquipo[i] = f
				end
				f.nombre.Text = string.sub(string.upper(m.nombre), 1, 9); f.nombre.TextColor3 = m.vivo and C.txt or C.mut
				f.barra.set(m.vida, m.vivo and Tema.colorVida(m.vida) or C.negro)
			end
		end
	end
end)

-- ===== Vida local, vineta y pulso de vida baja =====
local function enlazarPersonaje(ch)
	local hum = ch:WaitForChild("Humanoid"); local previa = hum.Health
	local function pintar()
		local p = hum.Health / math.max(1, hum.MaxHealth)
		tVida.Text = tostring(math.max(0, math.ceil(hum.Health))); bVida.set(p, Tema.colorVida(p))
	end
	pintar()
	hum.HealthChanged:Connect(function(h)
		if h < previa then destello(math.clamp((previa - h) / 25, 0.25, 0.8)) end
		previa = h; pintar()
	end)
end
plr.CharacterAdded:Connect(enlazarPersonaje); if plr.Character then task.spawn(enlazarPersonaje, plr.Character) end
task.spawn(function() -- pulso suave cuando la vida es baja
	while true do
		task.wait(0.6)
		local ch = plr.Character; local h = ch and ch:FindFirstChildOfClass("Humanoid")
		if h and h.Health > 0 and h.Health / h.MaxHealth < 0.3 then destello(0.35) end
	end
end)

-- ===== Prompts de la tienda con el mismo estilo (Style = Custom en el servidor) =====
local promptActual = nil
PPS.PromptShown:Connect(function(prompt)
	if prompt.Style ~= Enum.ProximityPromptStyle.Custom then return end
	promptActual = prompt
	local bb = n("BillboardGui", { Name = "LutoPrompt", Adornee = prompt.Parent, Size = UDim2.fromOffset(300, 72), StudsOffset = Vector3.new(0, 3.5, 0), AlwaysOnTop = true }, gui)
	local p = Tema.panel(bb, { Size = UDim2.fromScale(1, 1) })
	local tecla = n("Frame", { Size = UDim2.fromOffset(34, 34), Position = UDim2.fromOffset(14, 18), BackgroundColor3 = C.ambar, BorderSizePixel = 0 }, p)
	E(tecla, { Text = prompt.KeyboardKeyCode.Name, TextSize = 22, TextColor3 = C.negro, Size = UDim2.fromScale(1, 1) })
	E(p, { Text = prompt.ObjectText, TextSize = 18, TextTruncate = Enum.TextTruncate.AtEnd, Size = UDim2.new(1, -66, 0, 26), Position = UDim2.fromOffset(58, 8), TextXAlignment = Enum.TextXAlignment.Left })
	E(p, { Text = prompt.ActionText, TextSize = 20, TextTruncate = Enum.TextTruncate.AtEnd, TextColor3 = C.ambar, Size = UDim2.new(1, -66, 0, 28), Position = UDim2.fromOffset(58, 34), TextXAlignment = Enum.TextXAlignment.Left })
	local sin = nil
	sin = PPS.PromptHidden:Connect(function(pr) if pr == prompt then bb:Destroy(); if promptActual == prompt then promptActual = nil end; sin:Disconnect() end end)
end)
UIS.InputBegan:Connect(function(i, gp)
	if gp or not promptActual then return end
	if i.KeyCode == promptActual.KeyboardKeyCode then promptActual:InputHoldBegin() end
end)
UIS.InputEnded:Connect(function(i)
	if promptActual and i.KeyCode == promptActual.KeyboardKeyCode then promptActual:InputHoldEnd() end
end)
