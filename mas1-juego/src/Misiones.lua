-- Misiones de sesion de «+1 de lanzamiento por segundo» (Lua puro, sin API de Roblox). Cada jugador tiene 3 misiones a la vez; al
-- cumplir una se paga una recompensa y sale otra nueva. Se cuentan con el resultado de cada vuelo. Por ahora NO se guardan (son de
-- la sesion). Metas y premios PROVISIONALES.
local M = {}

M.LISTA = {
	{ id = "aros", texto = "Cruza aros", stat = "aros", metas = { 10, 25, 50 }, premio = { 300, 900, 2500 } },
	{ id = "distancia", texto = "Vuela metros", stat = "distancia", metas = { 2000, 6000, 15000 }, premio = { 400, 1200, 3000 } },
	{ id = "golpes", texto = "Golpea enemigos", stat = "golpes", metas = { 8, 20, 40 }, premio = { 300, 900, 2500 } },
	{ id = "cofres", texto = "Atrapa cofres", stat = "cofres", metas = { 2, 5, 10 }, premio = { 500, 1500, 4000 } },
	{ id = "orbes", texto = "Recoge orbes +1", stat = "orbes", metas = { 30, 80, 160 }, premio = { 300, 900, 2500 } },
	{ id = "vuelos", texto = "Haz vuelos", stat = "vuelos", metas = { 3, 8, 15 }, premio = { 200, 700, 2000 } },
}

local function ordenar(estado, id)
	-- cada mision pasa por 3 niveles; el nivel sube cada vez que se completa
	local n = estado.niveles[id] or 1
	return math.min(n, 3)
end

-- estado: { activas = { {id, base} , ... }, niveles = {id=nivel}, contador = n }. rng() devuelve [0,1).
function M.nuevo(rng)
	local e = { activas = {}, niveles = {}, acumulado = {} }
	for i = 1, 3 do M.rellenar(e, rng) end
	return e
end

function M.rellenar(e, rng)
	local usadas = {}
	for _, a in ipairs(e.activas) do usadas[a.id] = true end
	local libres = {}
	for _, m in ipairs(M.LISTA) do if not usadas[m.id] then libres[#libres + 1] = m end end
	local m = libres[math.min(#libres, math.floor(rng() * #libres) + 1)]
	-- empieza a contar desde lo acumulado ahora (solo cuenta lo que pase desde que sale la mision)
	e.activas[#e.activas + 1] = { id = m.id, base = e.acumulado[m.stat] or 0 }
end

local function porId(id)
	for _, m in ipairs(M.LISTA) do if m.id == id then return m end end
end

-- Descripcion de las activas: { texto, progreso, meta, premio }. El progreso va ENTERO: la distancia se acumula con decimales y el
-- cliente (client/Misiones.client.lua) lee el atributo con un patron de enteros (%d+): una fila con «1234.5678» no encaja y la mision
-- desaparecia del panel en cuanto se volaba con «Vuela metros» activa.
function M.ver(e)
	local out = {}
	for _, a in ipairs(e.activas) do
		local m = porId(a.id)
		local n = ordenar(e, a.id)
		out[#out + 1] = { id = a.id, texto = m.texto, progreso = math.floor(math.min((e.acumulado[m.stat] or 0) - a.base, m.metas[n])), meta = m.metas[n], premio = m.premio[n] }
	end
	return out
end

-- Registra el resultado de un vuelo: { distancia, aros, golpes, cofres, orbes }. Devuelve premio total y lista de ids completadas.
function M.registrar(e, vuelo, rng)
	local ac = e.acumulado
	ac.distancia = (ac.distancia or 0) + (vuelo.distancia or 0)
	ac.aros = (ac.aros or 0) + (vuelo.aros or 0)
	ac.golpes = (ac.golpes or 0) + (vuelo.golpes or 0)
	ac.cofres = (ac.cofres or 0) + (vuelo.cofres or 0)
	ac.orbes = (ac.orbes or 0) + (vuelo.orbes or 0)
	ac.vuelos = (ac.vuelos or 0) + 1
	local premio, hechas = 0, {}
	local i = 1
	while i <= #e.activas do
		local a = e.activas[i]
		local m = porId(a.id)
		local n = ordenar(e, a.id)
		if (ac[m.stat] or 0) - a.base >= m.metas[n] then
			premio = premio + m.premio[n]
			hechas[#hechas + 1] = a.id
			e.niveles[a.id] = (e.niveles[a.id] or 1) + 1
			table.remove(e.activas, i)
			M.rellenar(e, rng)
		else
			i = i + 1
		end
	end
	return premio, hechas
end

-- Texto compacto para mandar al cliente en un atributo: "texto|progreso|meta;texto|progreso|meta;..."
function M.codificar(e)
	local t = {}
	for _, v in ipairs(M.ver(e)) do t[#t + 1] = v.texto .. "|" .. v.progreso .. "|" .. v.meta .. "|" .. v.premio end
	return table.concat(t, ";")
end

return M
