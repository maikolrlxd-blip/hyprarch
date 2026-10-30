-- Alas de «+1 de lanzamiento por segundo» (Lua puro, probado con lupa): datos, requisitos y bonus. Maikol (30/10): las alas dan un
-- multiplicador de resistencia y de impulso «mucho mas notorio que las mascotas», y escalan con los rebirths; se multiplican con los
-- bonus de las mascotas. Requisitos de Maikol: iniciales en el 3.er lanzamiento, roboticas con 3 dias seguidos, avanzadas con
-- puntos, misiones o cofres (aqui: 10 cofres, o comprarlas). La interfaz (client/Inventario.client.lua) lee LISTA con
-- {id, nombre, requisito, precio}. CIFRAS PROVISIONALES. Modelos: Codex (iniciales, roboticas), Coordinador (avanzadas v0.2).
local A = {}

A.LISTA = {
	{ id = "iniciales", nombre = "Alas iniciales", requisito = "Tu 3.er lanzamiento", precio = 0, impulso = 20, resistencia = 50,
		pide = { lanzamientos = 3 } },
	{ id = "roboticas", nombre = "Alas robóticas", requisito = "Juega 3 días seguidos", precio = 0, impulso = 40, resistencia = 100,
		pide = { diasSeguidos = 3 } },
	{ id = "avanzadas", nombre = "Alas avanzadas", requisito = "Atrapa 10 cofres o cómpralas", precio = 25000, impulso = 80,
		resistencia = 200, pide = { cofres = 10 } },
}
A.PORREBIRTH = 0.25 -- cada rebirth sube un 25% lo que dan las alas

local porId = {}
for _, a in ipairs(A.LISTA) do porId[a.id] = a end

function A.get(id)
	return porId[id]
end

-- Multiplicadores de unas alas con cierto numero de rebirths: { impulso, resistencia } (1 = sin alas).
function A.bonus(id, rebirths)
	local a = porId[id]
	if not a then return { impulso = 1, resistencia = 1 } end
	local f = 1 + A.PORREBIRTH * (rebirths or 0)
	return { impulso = 1 + a.impulso / 100 * f, resistencia = 1 + a.resistencia / 100 * f }
end

-- ¿Cumple los requisitos? progreso = { lanzamientos, diasSeguidos, cofres }.
function A.desbloqueada(id, progreso)
	local a = porId[id]
	if not a then return false end
	for k, n in pairs(a.pide) do
		if (progreso[k] or 0) < n then return false end
	end
	return true
end

-- Bonus de un vuelo: los de las mascotas (Mascotas.multiplicadores) por los de las alas (A.bonus).
function A.combinar(mascotas, alas)
	local t = {}
	for k, v in pairs(mascotas) do t[k] = v end
	t.impulso = (t.impulso or 1) * (alas.impulso or 1)
	t.resistencia = (t.resistencia or 1) * (alas.resistencia or 1)
	return t
end

return A
