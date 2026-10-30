-- Partida de «+1 de lanzamiento por segundo» en el servidor: adaptador de Roblox de src/Partida.lua y src/Encuentros.lua (Lua puro,
-- probados con lupa). El cliente mueve su personaje y manda intenciones por MAS1_Accion. Aqui se lanza, se llevan la energia, el
-- boost, la distancia y los puntos, se valida cada paso (si va mas rapido de lo permitido o se sale de los limites, se le devuelve
-- atras), se cuentan los aros del mapa (Models «Aro» con su pieza «Centro»), los golpes a los enemigos y los cofres que huyen, y al
-- aterrizar se pagan el dinero y la exp y se manda MAS1_Resultado. Los enemigos y los cofres son anclas invisibles en
-- Workspace.MAS1_Entidades (atributos Tipo, Vivo y Dueno); los dibuja el cliente (client/Entidades.client.lua).
-- En tierra se entrena (+1 potencia/s, mas en las zonas MAS1_AFK y MAS1_Entreno del mapa) y se puede hacer rebirth; el bonus del
-- vuelo combina las mascotas equipadas y las alas (src/Alas.lua, que escalan con los rebirths). El inventario (src/Inventario.lua:
-- huevos, mascotas equipadas, alas) va a la interfaz por MAS1_Inventario y MAS1_Huevo, y los fallos por MAS1_Aviso.
-- Los datos se cargan y guardan con server/Guardado.lua (DataStore con bloqueo de sesion); hasta que cargan, el jugador no actua.
-- Las alas se desbloquean solas al cumplir su requisito (Alas.desbloqueada). Atributos y eventos en CONTRATO.md. SIN PROBAR EN STUDIO.
local Players, RS, RunService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService")
local Mas1 = RS:WaitForChild("Mas1")
local V = require(Mas1:WaitForChild("Vuelo"))
local P = require(Mas1:WaitForChild("Partida"))
local E = require(Mas1:WaitForChild("Encuentros"))
local M = require(Mas1:WaitForChild("Mascotas"))
local Alas = require(Mas1:WaitForChild("Alas"))
local I = require(Mas1:WaitForChild("Inventario"))
local D = require(Mas1:WaitForChild("Datos"))
local G = require(script.Parent:WaitForChild("Guardado"))
local Red = require(Mas1:WaitForChild("Red"))
local accion, efecto, resultado = Red.evento("MAS1_Accion"), Red.evento("MAS1_Efecto"), Red.evento("MAS1_Resultado")
local avisoEv, inventarioEv, huevoEv = Red.evento("MAS1_Aviso"), Red.evento("MAS1_Inventario"), Red.evento("MAS1_Huevo")
local PRODUCTO_FENIX = nil -- id del producto de Robux del fenix: SIN CONFIGURAR (no se ha creado ningun producto ni precio)

local INICIALES = { Potencia = 0, Dinero = 0, Exp = 0, Rebirths = 0, Cofres = 0, Lanzamientos = 0, Puntos = 0, Distancia = 0,
	ZonaMult = 1, Aros = 0, ArosTotal = 0, Energia = 1, EnergiaMax = 0, Impulso = 1, EnVuelo = false, Planeando = false, Boost = false,
	Mascota = "—", MascotaBonus = 1, Alas = "", Entreno = 1, CosteRebirth = V.costeRebirth(0) }
local MENSAJES_POR_SEGUNDO = 30
local jugadores = {} -- [plr] = { s = sesion de Partida, msgs, desde, hud, cofre = ancla del cofre, potencia, entreno }

local function aviso(plr, texto)
	avisoEv:FireClient(plr, texto)
end

-- inventario: a la interfaz con la forma acordada, y la mascota principal y su bonus de dinero al HUD
local function mandarInventario(plr, j)
	inventarioEv:FireClient(plr, I.copia(j.inv))
	local p = I.principal(M, j.inv)
	plr:SetAttribute("Mascota", p and p.nombre or "—")
	plr:SetAttribute("MascotaBonus", math.floor(M.multiplicadores(j.inv.equipadas).dinero * 100 + 0.5) / 100)
	plr:SetAttribute("Alas", j.inv.alaEquipada or "")
end

local function tabla(v)
	return { x = v.X, y = v.Y, z = v.Z }
end

local function v3(t)
	return Vector3.new(t.x, t.y, t.z)
end

local function raiz(plr)
	local c = plr.Character
	local h = c and c:FindFirstChildOfClass("Humanoid")
	if h and h.Health > 0 then return c:FindFirstChild("HumanoidRootPart"), h end
	return nil
end

-- ---------------------------------------------------------------- mundo: aros del mapa y enemigos repartidos por zona
local entidades = Instance.new("Folder")
entidades.Name = "MAS1_Entidades"
entidades.Parent = workspace
local mundo = { aros = {}, enemigos = {} }

for _, m in ipairs(workspace:GetDescendants()) do
	local c = m:IsA("Model") and m.Name == "Aro" and m:FindFirstChild("Centro")
	if c then
		local suma, n = 0, 0 -- radio: la distancia media de los bloques del aro a su centro
		for _, p in ipairs(m:GetChildren()) do
			if p:IsA("BasePart") and p ~= c then
				suma += (p.Position - c.Position).Magnitude
				n += 1
			end
		end
		mundo.aros[#mundo.aros + 1] = { centro = tabla(c.Position), radio = n > 0 and suma / n or 8 }
	end
end
table.sort(mundo.aros, function(a, b) return a.centro.z > b.centro.z end) -- en el orden del vuelo

local function ancla(nombre, pos, atributos)
	local p = Instance.new("Part")
	p.Name = nombre
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
	p.Transparency = 1
	p.Size = Vector3.new(1, 1, 1)
	p.Position = pos
	for k, v in pairs(atributos) do p:SetAttribute(k, v) end
	p.Parent = entidades
	return p
end

local azar = Random.new(30)
mundo.enemigos = E.colocarEnemigos(mundo.aros, function() return azar:NextNumber() end)
for _, en in ipairs(mundo.enemigos) do
	en.ancla = ancla("Enemigo", v3(en.pos), { Tipo = en.tipo, Vivo = true })
end

-- zonas de entrenamiento del mapa: partes llamadas MAS1_AFK (x1,5 aunque no te muevas) y MAS1_Entreno (x2 corriendo)
local zonasEntreno = {}
for _, p in ipairs(workspace:GetDescendants()) do
	if p:IsA("BasePart") and (p.Name == "MAS1_AFK" or p.Name == "MAS1_Entreno") then
		zonasEntreno[#zonasEntreno + 1] = { parte = p, tipo = p.Name == "MAS1_AFK" and "afk" or "entreno" }
	end
end

local function zonaDe(pos)
	for _, z in ipairs(zonasEntreno) do
		local rel, s = z.parte.CFrame:PointToObjectSpace(pos), z.parte.Size
		if math.abs(rel.X) <= s.X / 2 and math.abs(rel.Z) <= s.Z / 2 and rel.Y >= -2 and rel.Y <= s.Y / 2 + 8 then return z.tipo end
	end
	return nil
end

local function golpeado(i)
	local en = mundo.enemigos[i]
	en.ancla:SetAttribute("Vivo", false)
	efecto:FireAllClients("golpe", en.ancla.Position)
	task.delay(E.CFG.reaparicion, function()
		en.vivo = true
		en.ancla:SetAttribute("Vivo", true)
	end)
end

-- ---------------------------------------------------------------- jugadores: datos, alas que se desbloquean y guardado
local function revisarAlas(plr, j) -- hito 6: iniciales en el 3.er lanzamiento, roboticas con 3 dias seguidos, avanzadas con 10 cofres
	local progreso = { lanzamientos = plr:GetAttribute("Lanzamientos") or 0, diasSeguidos = j.dias.diasSeguidos,
		cofres = plr:GetAttribute("Cofres") or 0 }
	local nuevas = false
	for _, a in ipairs(Alas.LISTA) do
		if not I.tieneAla(j.inv, a.id) and Alas.desbloqueada(a.id, progreso) then
			I.darAla(j.inv, a.id)
			if not j.inv.alaEquipada then I.equiparAla(j.inv, a.id) end -- las primeras se ponen solas
			aviso(plr, "¡Nuevas alas: " .. a.nombre .. "!")
			nuevas = true
		end
	end
	if nuevas then mandarInventario(plr, j) end
end

local function aplicar(plr, j, d)
	j.potencia = d.potencia
	j.inv = d.inventario
	j.dias = { diasSeguidos = d.diasSeguidos, ultimoDia = d.ultimoDia }
	plr:SetAttribute("Potencia", math.floor(d.potencia))
	plr:SetAttribute("Dinero", d.dinero)
	plr:SetAttribute("Exp", d.exp)
	plr:SetAttribute("Rebirths", d.rebirths)
	plr:SetAttribute("CosteRebirth", V.costeRebirth(d.rebirths))
	plr:SetAttribute("Cofres", d.cofres)
	plr:SetAttribute("Lanzamientos", d.lanzamientos)
	plr:SetAttribute("DiasSeguidos", d.diasSeguidos)
	mandarInventario(plr, j)
	revisarAlas(plr, j)
end

local function datosDe(plr, j)
	return { version = D.VERSION, potencia = j.potencia, dinero = plr:GetAttribute("Dinero") or 0, exp = plr:GetAttribute("Exp") or 0,
		rebirths = plr:GetAttribute("Rebirths") or 0, cofres = plr:GetAttribute("Cofres") or 0,
		lanzamientos = plr:GetAttribute("Lanzamientos") or 0, diasSeguidos = j.dias.diasSeguidos, ultimoDia = j.dias.ultimoDia,
		inventario = I.copia(j.inv) }
end

local function alEntrar(plr)
	for k, v in pairs(INICIALES) do
		if plr:GetAttribute(k) == nil then plr:SetAttribute(k, v) end
	end
	plr:SetAttribute("ArosTotal", #mundo.aros)
	local j = { s = P.nueva(V, E), msgs = 0, desde = 0, hud = 0, potencia = 0, entreno = 0, inv = I.nuevo(), cargado = false,
		dias = { diasSeguidos = 0, ultimoDia = -1 } }
	jugadores[plr] = j
	plr:GetAttributeChangedSignal("Potencia"):Connect(function() -- cambiada a mano (en Studio, para probar): se adopta
		local v = plr:GetAttribute("Potencia")
		if j.cargado and type(v) == "number" and math.abs(v - math.floor(j.potencia)) >= 1 then j.potencia = v end
	end)
	plr.CharacterAdded:Connect(function() mandarInventario(plr, j) end) -- para cuando los scripts del cliente ya escuchan
	task.spawn(function()
		local d, motivo = G.cargar(plr)
		if not plr.Parent or jugadores[plr] ~= j then return end
		if not d then -- mejor no jugar que jugar con datos vacios y pisar los buenos al guardar
			plr:Kick(motivo == "bloqueado" and "Tus datos siguen abiertos en otro servidor. Vuelve a entrar en un momento."
				or "No se pudieron cargar tus datos. Vuelve a entrar en un momento.")
			return
		end
		D.registrarDia(d, math.floor(os.time() / 86400))
		aplicar(plr, j, d)
		j.cargado = true
	end)
end
Players.PlayerAdded:Connect(alEntrar)
for _, plr in ipairs(Players:GetPlayers()) do alEntrar(plr) end

local enCurso = 0 -- guardados en marcha: al cerrar el servidor se espera a todos, tambien a los de jugadores que ya salieron

local function guardar(plr, j, soltar)
	if not j.cargado then return end
	enCurso += 1
	local ok, escrito = G.guardar(plr, datosDe(plr, j), soltar)
	enCurso -= 1
	if ok and not escrito and not soltar then -- otra sesion se quedo sus datos: este servidor ya no puede seguir con el
		j.cargado = false
		plr:Kick("Tus datos se abrieron en otro servidor.")
	end
end

local function despedir(plr, j) -- guardar y soltar el bloqueo una sola vez (al salir o al cerrar el servidor)
	if j.saliendo then return end
	j.saliendo = true
	guardar(plr, j, true)
end

task.spawn(function() -- autoguardado
	while true do
		task.wait(G.AUTOGUARDADO)
		for plr, j in pairs(jugadores) do
			if not j.saliendo then task.spawn(guardar, plr, j, false) end
		end
	end
end)

game:BindToClose(function() -- al cerrar el servidor: guardar y soltar a todos (Roblox espera hasta 30 s)
	for plr, j in pairs(jugadores) do task.spawn(despedir, plr, j) end
	task.wait() -- que arranquen
	local t0 = os.clock()
	while enCurso > 0 and os.clock() - t0 < 25 do task.wait(0.2) end
end)

local function quitarCofre(j)
	if j.cofre then
		j.cofre:Destroy()
		j.cofre = nil
	end
end

Players.PlayerRemoving:Connect(function(plr)
	local j = jugadores[plr]
	if not j then return end
	quitarCofre(j)
	jugadores[plr] = nil
	despedir(plr, j) -- guarda y suelta el bloqueo
end)

local function bonusDe(plr, j) -- mascotas equipadas por las alas equipadas, que escalan con los rebirths
	return Alas.combinar(M.multiplicadores(j.inv.equipadas), Alas.bonus(j.inv.alaEquipada, plr:GetAttribute("Rebirths") or 0))
end

local azarHuevos = Random.new()

-- intenciones del inventario (en tierra): abrir huevos, equipar y desequipar mascotas y alas, comprar alas
local function inventario(plr, j, nombre, a, b)
	if P.enVuelo(j.s) then
		aviso(plr, "Eso se hace en tierra")
		return
	end
	local ok, x, p, nueva
	if nombre == "abrirHuevo" and type(a) == "string" then
		ok, x, p, nueva = I.abrirHuevo(M, j.inv, plr:GetAttribute("Dinero") or 0, a, function() return azarHuevos:NextNumber() end)
		if ok then
			plr:SetAttribute("Dinero", x)
			huevoEv:FireClient(plr, { rareza = a, mascotaId = p.id, nueva = nueva })
		end
	elseif nombre == "equipar" and a == "mascota" and type(b) == "string" then
		ok, x = I.equipar(M, j.inv, b)
	elseif nombre == "desequipar" and a == "mascota" and type(b) == "string" then
		ok, x = I.desequipar(j.inv, b)
	elseif nombre == "equipar" and a == "ala" and type(b) == "string" then
		ok, x = I.equiparAla(j.inv, b)
	elseif nombre == "desequipar" and a == "ala" then
		ok, x = I.desequiparAla(j.inv)
	elseif nombre == "comprarAla" and type(a) == "string" then
		ok, x = I.comprarAla(Alas, j.inv, plr:GetAttribute("Dinero") or 0, a)
		if ok then plr:SetAttribute("Dinero", x) end
	elseif nombre == "inventario" then
		ok = true
	else
		return
	end
	if ok then mandarInventario(plr, j) elseif type(x) == "string" then aviso(plr, x) end
end

if PRODUCTO_FENIX then -- fenix solo con Robux: al cobrar el producto se da la mascota (hito 5 lo guardara)
	game:GetService("MarketplaceService").ProcessReceipt = function(recibo)
		local plr = Players:GetPlayerByUserId(recibo.PlayerId)
		local j = plr and jugadores[plr]
		if not j or recibo.ProductId ~= PRODUCTO_FENIX then return Enum.ProductPurchaseDecision.NotProcessedYet end
		I.darFenix(j.inv)
		mandarInventario(plr, j)
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end
end

local function rebirth(plr, j)
	if P.enVuelo(j.s) then return end
	local r = plr:GetAttribute("Rebirths") or 0
	local coste = V.costeRebirth(r)
	if j.potencia < coste then
		aviso(plr, string.format("Te falta potencia para el rebirth: %d / %d", math.floor(j.potencia), coste))
		return
	end
	j.potencia = 0
	plr:SetAttribute("Potencia", 0)
	plr:SetAttribute("Rebirths", r + 1)
	plr:SetAttribute("CosteRebirth", V.costeRebirth(r + 1))
	local hrp = raiz(plr)
	if hrp then efecto:FireAllClients("rebirth", hrp.Position) end
end

local function cerrarVuelo(plr, j, hrp)
	quitarCofre(j)
	plr:SetAttribute("EnVuelo", false)
	plr:SetAttribute("Planeando", false)
	if plr:GetAttribute("Boost") then
		plr:SetAttribute("Boost", false)
		if hrp then efecto:FireAllClients("estela", nil, hrp, false) end
	end
end

local function lanzar(plr, j)
	local hrp, hum = raiz(plr)
	if not hrp or P.enVuelo(j.s) or hum.Sit or hum.FloorMaterial == Enum.Material.Air then return end -- solo desde el suelo
	local canon = workspace:FindFirstChild("MAS1_Canon", true) -- el cañon de la Pradera cuando este; si no, desde donde esta
	local base = (canon and canon:IsA("BasePart")) and canon.Position or hrp.Position
	local pos = base + Vector3.new(0, 4, 0)
	hrp.CFrame = CFrame.lookAt(pos, pos + Vector3.new(0, 0, -1))
	hrp.AssemblyLinearVelocity = Vector3.zero
	local b = bonusDe(plr, j)
	P.lanzar(j.s, tabla(pos), j.potencia, b)
	plr:SetAttribute("Lanzamientos", (plr:GetAttribute("Lanzamientos") or 0) + 1)
	plr:SetAttribute("Entreno", 0)
	revisarAlas(plr, j)
	quitarCofre(j)
	if j.s.cofre then j.cofre = ancla("Cofre", v3(j.s.cofre.pos), { Tipo = "cofre", Dueno = plr.UserId }) end
	plr:SetAttribute("Impulso", b.impulso)
	plr:SetAttribute("EnergiaMax", j.s.v.energiaMax)
	plr:SetAttribute("Energia", 1)
	plr:SetAttribute("Puntos", 0)
	plr:SetAttribute("Distancia", 0)
	plr:SetAttribute("Aros", 0)
	plr:SetAttribute("ArosTotal", #mundo.aros)
	plr:SetAttribute("Planeando", false)
	plr:SetAttribute("Boost", false)
	plr:SetAttribute("EnVuelo", true)
	efecto:FireAllClients("lanzamiento", pos)
end

accion.OnServerEvent:Connect(function(plr, nombre, valor, extra)
	local j = jugadores[plr]
	if not j or not j.cargado or type(nombre) ~= "string" then return end -- hasta que cargan sus datos, nada
	local ahora = os.clock()
	if ahora - j.desde > 1 then j.desde, j.msgs = ahora, 0 end
	j.msgs += 1
	if j.msgs > MENSAJES_POR_SEGUNDO then return end
	if nombre == "lanzar" then
		lanzar(plr, j)
		return
	elseif nombre == "rebirth" then
		rebirth(plr, j)
		return
	elseif nombre == "abrirHuevo" or nombre == "equipar" or nombre == "desequipar" or nombre == "comprarAla" or nombre == "inventario" then
		inventario(plr, j, nombre, valor, extra)
		return
	end
	local fx, i = P.intencion(j.s, nombre, valor, mundo)
	if i then
		golpeado(i)
	elseif fx == "golpe" then -- golpe al aire: solo el efecto
		local hrp = raiz(plr)
		if hrp then efecto:FireAllClients("golpe", hrp.Position + Vector3.new(0, 0, -5)) end
	end
end)

RunService.Heartbeat:Connect(function(dt)
	for plr, j in pairs(jugadores) do
		if not P.enVuelo(j.s) then -- en tierra: entrenar (+1/s, mas en las zonas AFK y de entrenamiento y con los rebirths)
			if not j.cargado then continue end
			j.entreno += dt
			if j.entreno >= 0.25 then
				local hrp, hum = raiz(plr)
				if hrp then
					local ritmo = V.ritmoEntreno(plr:GetAttribute("Rebirths") or 0, zonaDe(hrp.Position), hum.MoveDirection.Magnitude > 0.1)
					j.potencia += ritmo * j.entreno
					plr:SetAttribute("Potencia", math.floor(j.potencia))
					plr:SetAttribute("Entreno", ritmo)
				end
				j.entreno = 0
			end
			continue
		end
		local hrp = raiz(plr)
		if not hrp then -- murio o se quedo sin personaje: el vuelo no paga
			P.cancelar(j.s)
			cerrarVuelo(plr, j, nil)
			continue
		end
		local r = P.tick(j.s, dt, tabla(hrp.Position), mundo)
		if r.corregir then
			hrp.CFrame = CFrame.new(r.corregir.x, r.corregir.y, r.corregir.z) * hrp.CFrame.Rotation
		end
		if r.aros then
			for _, i in ipairs(r.aros) do efecto:FireClient(plr, "aro", v3(mundo.aros[i].centro)) end
			plr:SetAttribute("Aros", j.s.v.aros)
		end
		if r.cofreAtrapado then
			efecto:FireClient(plr, "aro", v3(r.cofreAtrapado))
			plr:SetAttribute("Cofres", (plr:GetAttribute("Cofres") or 0) + 1)
			quitarCofre(j)
			revisarAlas(plr, j)
		end
		if r.cofre then
			if not j.cofre then j.cofre = ancla("Cofre", v3(r.cofre), { Tipo = "cofre", Dueno = plr.UserId }) end
			j.cofre.Position = v3(r.cofre)
		end
		if plr:GetAttribute("Boost") ~= r.boost then
			plr:SetAttribute("Boost", r.boost)
			efecto:FireAllClients("estela", nil, hrp, r.boost)
		end
		plr:SetAttribute("Planeando", r.planeando)
		j.hud += dt
		if j.hud >= 0.1 or r.aterrizaje then -- el HUD no necesita 60 cambios por segundo
			j.hud = 0
			plr:SetAttribute("Energia", math.floor(r.energia * 1000) / 1000)
			plr:SetAttribute("Distancia", math.floor(r.distancia))
			plr:SetAttribute("ZonaMult", r.mult)
			plr:SetAttribute("Puntos", r.puntos)
		end
		if r.aterrizaje then
			local res = r.aterrizaje
			plr:SetAttribute("Dinero", (plr:GetAttribute("Dinero") or 0) + res.dinero)
			plr:SetAttribute("Exp", (plr:GetAttribute("Exp") or 0) + res.exp)
			cerrarVuelo(plr, j, hrp)
			resultado:FireClient(plr, { distancia = math.floor(res.distancia), aros = res.aros, golpes = res.golpes, cofres = res.cofres,
				multiplicador = res.multiplicador, dinero = res.dinero, exp = res.exp, tiempo = res.tiempo })
		end
	end
end)
