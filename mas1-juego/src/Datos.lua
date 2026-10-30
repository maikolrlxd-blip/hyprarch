-- Datos guardados de un jugador de «+1 de lanzamiento por segundo» (Lua puro, probado con lupa; el DataStore lo lleva
-- server/Guardado.lua). Tres cosas: los datos por defecto y la limpieza de lo que se carga (tipos, negativos, mascotas que no
-- existen, mas de 3 equipadas...), el bloqueo de sesion (un servidor «toma» los datos del jugador; otro no los pisa salvo que el
-- bloqueo caduque, porque el primero se cayo) y la racha de dias seguidos (alas roboticas). Lo guardado en el DataStore es
-- { dato = {...}, bloqueo = { sesion, t } }.
local D = {}

D.VERSION = 1

function D.nuevo()
	return { version = D.VERSION, potencia = 0, dinero = 0, exp = 0, rebirths = 0, cofres = 0, lanzamientos = 0,
		diasSeguidos = 0, ultimoDia = -1, inventario = { mascotas = {}, equipadas = {}, alas = {}, alaEquipada = nil } }
end

local function numero(x, minimo)
	if type(x) ~= "number" or x ~= x or x == math.huge or x == -math.huge then return minimo end -- nil, texto, NaN, infinito
	return math.max(minimo, x)
end

-- Limpia unos datos cargados: lo que falte o venga mal se queda por defecto. M = Mascotas, A = Alas.
function D.limpiar(d, M, A)
	local n = D.nuevo()
	if type(d) ~= "table" then return n end
	for _, k in ipairs({ "potencia", "dinero", "exp", "rebirths", "cofres", "lanzamientos", "diasSeguidos" }) do
		n[k] = numero(d[k], 0)
	end
	for _, k in ipairs({ "rebirths", "cofres", "lanzamientos", "diasSeguidos" }) do n[k] = math.floor(n[k]) end
	n.ultimoDia = math.floor(numero(d.ultimoDia, -1))
	local inv = type(d.inventario) == "table" and d.inventario or {}
	if type(inv.mascotas) == "table" then
		for id, c in pairs(inv.mascotas) do
			if type(id) == "string" and M.get(id) and type(c) == "number" and c >= 1 then n.inventario.mascotas[id] = math.floor(c) end
		end
	end
	local usadas = {}
	if type(inv.equipadas) == "table" then
		for _, id in ipairs(inv.equipadas) do
			if #n.inventario.equipadas < M.MAX_EQUIPADAS and (usadas[id] or 0) < (n.inventario.mascotas[id] or 0) then
				usadas[id] = (usadas[id] or 0) + 1
				n.inventario.equipadas[#n.inventario.equipadas + 1] = id
			end
		end
	end
	local tiene = {}
	if type(inv.alas) == "table" then
		for _, id in ipairs(inv.alas) do
			if type(id) == "string" and A.get(id) and not tiene[id] then
				tiene[id] = true
				n.inventario.alas[#n.inventario.alas + 1] = id
			end
		end
	end
	if tiene[inv.alaEquipada] then n.inventario.alaEquipada = inv.alaEquipada end
	return n
end

-- Bloqueo de sesion, dentro del UpdateAsync al cargar: devuelve true y lo que hay que guardar (con el bloqueo de esta sesion), o
-- false si otra sesion lo tiene y su bloqueo no ha caducado (no se escribe nada).
function D.tomar(guardado, sesion, ahora, caduca)
	if type(guardado) ~= "table" or type(guardado.dato) ~= "table" then
		return true, { dato = D.nuevo(), bloqueo = { sesion = sesion, t = ahora } } -- jugador nuevo
	end
	local b = guardado.bloqueo
	if type(b) == "table" and b.sesion ~= sesion and type(b.t) == "number" and ahora - b.t < caduca then return false end
	return true, { dato = guardado.dato, bloqueo = { sesion = sesion, t = ahora } }
end

-- Al guardar: solo si el bloqueo sigue siendo de esta sesion (o no hay); soltar = al salir el jugador. Devuelve false si otra sesion
-- se lo quedo (este servidor ya no debe escribir).
function D.escribir(guardado, sesion, dato, ahora, soltar)
	local b = type(guardado) == "table" and guardado.bloqueo
	if type(b) == "table" and b.sesion ~= sesion then return false end
	return true, { dato = dato, bloqueo = (not soltar) and { sesion = sesion, t = ahora } or nil }
end

-- Racha de dias: hoy = dias desde 1970 (os.time() // 86400). Devuelve true si es un dia nuevo.
function D.registrarDia(d, hoy)
	if d.ultimoDia == hoy then return false end
	d.diasSeguidos = (d.ultimoDia == hoy - 1) and d.diasSeguidos + 1 or 1
	d.ultimoDia = hoy
	return true
end

return D
