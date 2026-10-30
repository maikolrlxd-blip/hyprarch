-- Partida de «+1 de lanzamiento por segundo» en el servidor: adaptador de Roblox de src/Partida.lua (Lua puro, probado con lupa).
-- El cliente mueve su personaje y manda intenciones por MAS1_Accion. Aqui se lanza, se llevan la energia, el boost, la distancia y
-- los puntos, se valida cada paso (si va mas rapido de lo permitido o se sale de los limites, se le devuelve atras) y al aterrizar
-- se pagan el dinero y la exp y se manda MAS1_Resultado. Atributos y eventos en CONTRATO.md.
-- Todavia sin guardado (hito 5) ni mascotas equipadas (hito 4): los bonus valen 1. SIN PROBAR EN STUDIO.
local Players, RS, RunService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService")
local Mas1 = RS:WaitForChild("Mas1")
local V = require(Mas1:WaitForChild("Vuelo"))
local P = require(Mas1:WaitForChild("Partida"))
local M = require(Mas1:WaitForChild("Mascotas"))
local Red = require(Mas1:WaitForChild("Red"))
local accion, efecto, resultado = Red.evento("MAS1_Accion"), Red.evento("MAS1_Efecto"), Red.evento("MAS1_Resultado")

local INICIALES = { Potencia = 0, Dinero = 0, Exp = 0, Rebirths = 0, Puntos = 0, Distancia = 0, ZonaMult = 1, Aros = 0, ArosTotal = 0,
	Energia = 1, EnergiaMax = 0, Impulso = 1, EnVuelo = false, Planeando = false, Boost = false, Mascota = "—", MascotaBonus = 1 }
local MENSAJES_POR_SEGUNDO = 30
local jugadores = {} -- [plr] = { s = sesion de Partida, msgs, desde, hud }

local function tabla(v)
	return { x = v.X, y = v.Y, z = v.Z }
end

local function raiz(plr)
	local c = plr.Character
	local h = c and c:FindFirstChildOfClass("Humanoid")
	if h and h.Health > 0 then return c:FindFirstChild("HumanoidRootPart"), h end
	return nil
end

local function alEntrar(plr)
	for k, v in pairs(INICIALES) do
		if plr:GetAttribute(k) == nil then plr:SetAttribute(k, v) end
	end
	jugadores[plr] = { s = P.nueva(V), msgs = 0, desde = 0, hud = 0 }
end
Players.PlayerAdded:Connect(alEntrar)
for _, plr in ipairs(Players:GetPlayers()) do alEntrar(plr) end
Players.PlayerRemoving:Connect(function(plr) jugadores[plr] = nil end)

local function bonusDe(plr) -- hito 4: los bonus de las mascotas equipadas
	return M.multiplicadores({})
end

local function cerrarVuelo(plr, hrp)
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
	local b = bonusDe(plr)
	P.lanzar(j.s, tabla(pos), plr:GetAttribute("Potencia") or 0, b)
	plr:SetAttribute("Impulso", b.impulso)
	plr:SetAttribute("EnergiaMax", j.s.v.energiaMax)
	plr:SetAttribute("Energia", 1)
	plr:SetAttribute("Puntos", 0)
	plr:SetAttribute("Distancia", 0)
	plr:SetAttribute("Aros", 0)
	plr:SetAttribute("Planeando", false)
	plr:SetAttribute("Boost", false)
	plr:SetAttribute("EnVuelo", true)
	efecto:FireAllClients("lanzamiento", pos)
end

accion.OnServerEvent:Connect(function(plr, nombre, valor)
	local j = jugadores[plr]
	if not j or type(nombre) ~= "string" then return end
	local ahora = os.clock()
	if ahora - j.desde > 1 then j.desde, j.msgs = ahora, 0 end
	j.msgs += 1
	if j.msgs > MENSAJES_POR_SEGUNDO then return end
	if nombre == "lanzar" then
		lanzar(plr, j)
	elseif P.intencion(j.s, nombre, valor) == "golpe" then
		local hrp = raiz(plr)
		if hrp then efecto:FireAllClients("golpe", hrp.Position + Vector3.new(0, 0, -5)) end
	end
end)

RunService.Heartbeat:Connect(function(dt)
	for plr, j in pairs(jugadores) do
		if not P.enVuelo(j.s) then continue end
		local hrp = raiz(plr)
		if not hrp then -- murio o se quedo sin personaje: el vuelo no paga
			P.cancelar(j.s)
			cerrarVuelo(plr, nil)
			continue
		end
		local r = P.tick(j.s, dt, tabla(hrp.Position))
		if r.corregir then
			hrp.CFrame = CFrame.new(r.corregir.x, r.corregir.y, r.corregir.z) * hrp.CFrame.Rotation
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
			cerrarVuelo(plr, hrp)
			resultado:FireClient(plr, { distancia = math.floor(res.distancia), aros = res.aros, golpes = res.golpes,
				multiplicador = res.multiplicador, dinero = res.dinero, exp = res.exp, tiempo = res.tiempo })
		end
	end
end)
