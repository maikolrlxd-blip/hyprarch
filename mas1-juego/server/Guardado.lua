-- Guardado de «+1 de lanzamiento por segundo» con DataStore: adaptador de Roblox de src/Datos.lua (Lua puro, probado con lupa).
-- Carga tomando el bloqueo de sesion (si otro servidor tiene los datos del jugador, espera a que los suelte o a que su bloqueo
-- caduque), guarda con reintentos y espera creciente, y nunca pisa datos de otra sesion. Solo EN STUDIO, si no hay acceso al
-- DataStore (place sin publicar o sin «Enable Studio Access to API Services»), se juega sin guardar y se avisa en el Output; en un
-- servidor de verdad nunca se juega sin guardar: si no se pueden cargar los datos, el jugador sale con un mensaje (revision de
-- Linux 2.0: una prueba de acceso fallida al arrancar dejaba todo el servidor sin guardar en silencio).
-- Lo usa server/Partida.server.lua (autoguardado cada G.AUTOGUARDADO s, al salir y al cerrar el servidor). SIN PROBAR EN STUDIO.
local DataStoreService, HttpService, RS = game:GetService("DataStoreService"), game:GetService("HttpService"), game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Mas1 = RS:WaitForChild("Mas1")
local D = require(Mas1:WaitForChild("Datos"))
local M = require(Mas1:WaitForChild("Mascotas"))
local Alas = require(Mas1:WaitForChild("Alas"))

local G = {}
G.CADUCA = 180 -- s sin refrescar para dar por abandonado un bloqueo (el otro servidor se cayo)
G.AUTOGUARDADO = 60
local SESION = game.JobId ~= "" and game.JobId or ("studio-" .. HttpService:GenerateGUID(false))

local tienda
do
	local ok, t = pcall(function() return DataStoreService:GetDataStore("MAS1_Datos_v1") end)
	if ok then tienda = t end
	-- la prueba de acceso solo en Studio: en un servidor de verdad un fallo pasajero no puede dejar a nadie sin guardar
	if tienda and RunService:IsStudio() and not pcall(function() tienda:GetAsync("prueba_de_acceso") end) then tienda = nil end
	if not tienda then
		if RunService:IsStudio() then
			warn("[MAS1 guardado] Studio sin acceso al DataStore: se juega SIN GUARDAR (place sin publicar o sin acceso a las API)")
		else
			warn("[MAS1 guardado] Servidor sin DataStore: no se dejara jugar a nadie (sus datos no se podrian guardar)")
		end
	end
end
G.sinGuardar = tienda == nil and RunService:IsStudio() -- solo Studio juega sin guardar
G.activo = tienda ~= nil

local function reintentar(f)
	local espera = 1
	for intento = 1, 5 do
		local ok, r = pcall(f)
		if ok then return true, r end
		warn(string.format("[MAS1 guardado] intento %d fallido: %s", intento, tostring(r)))
		if intento < 5 then
			task.wait(espera)
			espera *= 2
		end
	end
	return false
end

-- Carga los datos de plr, limpios, tomando el bloqueo. Devuelve los datos, o nil y el motivo ("bloqueado", "error" o "se fue").
function G.cargar(plr)
	if not tienda then
		if G.sinGuardar then return D.limpiar(nil, M, Alas) end
		return nil, "error"
	end
	local clave = "j_" .. plr.UserId
	for _ = 1, 8 do -- si acaba de cambiar de servidor, el otro aun puede tener el bloqueo: se espera a que lo suelte
		local bloqueado = false
		local ok, guardado = reintentar(function()
			return tienda:UpdateAsync(clave, function(viejo)
				local tomado, nuevo = D.tomar(viejo, SESION, os.time(), G.CADUCA)
				bloqueado = not tomado
				return nuevo -- nil: no se escribe nada
			end)
		end)
		if not ok then return nil, "error" end
		if not bloqueado then return D.limpiar(guardado and guardado.dato, M, Alas) end
		if not plr.Parent then return nil, "se fue" end
		task.wait(6)
	end
	return nil, "bloqueado"
end

-- Guarda dato (soltar = al salir). Devuelve dos cosas: si el DataStore respondio y si se escribio (false = otra sesion tiene el
-- bloqueo: este servidor ya no debe seguir con el jugador).
function G.guardar(plr, dato, soltar)
	if not tienda then return G.sinGuardar, G.sinGuardar end
	local escrito = false
	local ok = reintentar(function()
		return tienda:UpdateAsync("j_" .. plr.UserId, function(viejo)
			local puede, nuevo = D.escribir(viejo, SESION, dato, os.time(), soltar)
			escrito = puede
			return nuevo
		end)
	end)
	return ok, escrito
end

return G
