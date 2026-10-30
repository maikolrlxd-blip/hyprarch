-- Inventario de un jugador de «+1 de lanzamiento por segundo» (Lua puro, probado con lupa): mascotas por cantidad, hasta 3 equipadas
-- (se puede repetir una si tienes varias), huevos que se pagan con dinero, alas compradas o desbloqueadas y la equipada. Lo usa el
-- servidor (server/Partida.server.lua) y se manda a la interfaz con la forma acordada con Linux 2.0 (MAS1_Inventario). El fenix solo
-- se da con Robux (I.darFenix, sin producto configurado todavia). Cada funcion que cambia algo devuelve ok y, si no, el motivo
-- (texto para MAS1_Aviso).
local I = {}

function I.nuevo()
	return { mascotas = {}, equipadas = {}, alas = {}, alaEquipada = nil }
end

local function cuantas(lista, id)
	local n = 0
	for _, x in ipairs(lista) do
		if x == id then n = n + 1 end
	end
	return n
end

-- Abre un huevo pagando con dinero. Devuelve ok, dinero que queda, mascota (de Mascotas.LISTA), nueva (primera vez) o false, motivo.
function I.abrirHuevo(M, inv, dinero, rareza, rng)
	local precio = M.PRECIO_HUEVO[rareza]
	if not precio then return false, "Ese huevo no existe" end
	if dinero < precio then return false, string.format("Te falta dinero: el huevo cuesta %d", precio) end
	local p = M.abrirHuevo(rareza, rng)
	if not p then return false, "Ese huevo no existe" end
	local nueva = (inv.mascotas[p.id] or 0) == 0
	inv.mascotas[p.id] = (inv.mascotas[p.id] or 0) + 1
	return true, dinero - precio, p, nueva
end

function I.darFenix(inv) -- compra con Robux (MarketplaceService.ProcessReceipt): hito 4 sin producto configurado
	inv.mascotas.fenix = (inv.mascotas.fenix or 0) + 1
end

function I.equipar(M, inv, id)
	if not M.get(id) then return false, "Esa mascota no existe" end
	if #inv.equipadas >= M.MAX_EQUIPADAS then return false, string.format("Ya llevas %d mascotas", M.MAX_EQUIPADAS) end
	if cuantas(inv.equipadas, id) >= (inv.mascotas[id] or 0) then return false, "No tienes otra de esas" end
	inv.equipadas[#inv.equipadas + 1] = id
	return true
end

function I.desequipar(inv, id)
	for i, x in ipairs(inv.equipadas) do
		if x == id then
			table.remove(inv.equipadas, i)
			return true
		end
	end
	return false, "No llevas esa mascota"
end

-- La mascota que se ve en el HUD: la de mas rareza de las equipadas (nil si no hay).
function I.principal(M, inv)
	local orden = {}
	for i, r in ipairs(M.RAREZAS) do orden[r] = i end
	local mejor
	for _, id in ipairs(inv.equipadas) do
		local p = M.get(id)
		if p and (not mejor or orden[p.rareza] > orden[mejor.rareza]) then mejor = p end
	end
	return mejor
end

-- Alas: comprarlas con dinero, conseguirlas al cumplir el requisito (Alas.desbloqueada) y equiparlas.
function I.tieneAla(inv, id)
	for _, x in ipairs(inv.alas) do
		if x == id then return true end
	end
	return false
end

function I.darAla(inv, id)
	if I.tieneAla(inv, id) then return false end
	inv.alas[#inv.alas + 1] = id
	return true
end

function I.comprarAla(Alas, inv, dinero, id)
	local a = Alas.get(id)
	if not a then return false, "Esas alas no existen" end
	if I.tieneAla(inv, id) then return false, "Ya tienes esas alas" end
	if not a.precio or a.precio <= 0 then return false, "Esas alas no se compran: " .. a.requisito end
	if dinero < a.precio then return false, string.format("Te falta dinero: cuestan %d", a.precio) end
	I.darAla(inv, id)
	return true, dinero - a.precio
end

function I.equiparAla(inv, id)
	if not I.tieneAla(inv, id) then return false, "No tienes esas alas" end
	inv.alaEquipada = id
	return true
end

function I.desequiparAla(inv)
	inv.alaEquipada = nil
	return true
end

-- Copia para la interfaz (MAS1_Inventario) y para guardar: solo datos, sin referencias compartidas.
function I.copia(inv)
	local m, e, a = {}, {}, {}
	for k, v in pairs(inv.mascotas) do m[k] = v end
	for i, v in ipairs(inv.equipadas) do e[i] = v end
	for i, v in ipairs(inv.alas) do a[i] = v end
	return { mascotas = m, equipadas = e, alas = a, alaEquipada = inv.alaEquipada }
end

return I
