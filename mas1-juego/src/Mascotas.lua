-- Mascotas de «+1 de lanzamiento por segundo»: datos y calculo de bonus (Lua puro, sin API de Roblox).
-- Cuatro cosas que suben: impulso (poder del canon), resistencia (energia de vuelo), dinero y exp (mascotas y alas).
-- Cada mascota da +% en 1 a 4 de ellas segun rareza. VALORES PROVISIONALES: se ajustan jugando.
local M = {}

M.STATS = { "impulso", "resistencia", "dinero", "exp" }
M.RAREZAS = { "comun", "poco_comun", "raro", "epico", "legendario", "mitico", "robux" }

-- id, modelo, rareza, bonus (en porcentaje). Los enemigos usan su version amable como mascota.
M.LISTA = {
	{ id = "gorrion", nombre = "Gorrion Miga", rareza = "comun", bonus = { dinero = 10 } },
	{ id = "golondrina", nombre = "Golondrina Brisa", rareza = "comun", bonus = { impulso = 10 } },
	{ id = "nube", nombre = "Nubecita", rareza = "poco_comun", bonus = { resistencia = 20 } },
	{ id = "globo", nombre = "Globito", rareza = "poco_comun", bonus = { exp = 20 } },
	{ id = "nubarron", nombre = "Truenito", rareza = "raro", bonus = { impulso = 30, resistencia = 30 } },
	{ id = "ovni", nombre = "Marcianito", rareza = "raro", bonus = { dinero = 30, exp = 30 } },
	{ id = "meteorito", nombre = "Meteorito Chispa", rareza = "epico", bonus = { impulso = 40, dinero = 40, exp = 40 } },
	{ id = "cometa", nombre = "Cometa Colita", rareza = "epico", bonus = { resistencia = 40, dinero = 40, exp = 40 } },
	{ id = "aguila", nombre = "Aguila legendaria", rareza = "legendario", bonus = { impulso = 55, resistencia = 55, dinero = 55 } },
	{ id = "grifo", nombre = "Grifo mitico", rareza = "mitico", bonus = { impulso = 70, resistencia = 70, dinero = 70, exp = 70 } },
	{ id = "fenix", nombre = "Fenix de fuego", rareza = "robux", bonus = { impulso = 90, resistencia = 90, dinero = 90, exp = 90 }, fuego = true },
}

-- Pesos de cada huevo (rareza del huevo -> rareza de la mascota). El fenix NO sale de huevos.
M.HUEVOS = {
	comun = { comun = 80, poco_comun = 20 },
	poco_comun = { comun = 30, poco_comun = 55, raro = 15 },
	raro = { poco_comun = 30, raro = 55, epico = 15 },
	epico = { raro = 40, epico = 50, legendario = 10 },
	legendario = { epico = 45, legendario = 50, mitico = 5 },
	mitico = { legendario = 60, mitico = 40 },
}

-- Precio de cada huevo en dinero (hito 4, PROVISIONAL): un primer vuelo da unos 2.600 y uno largo, 10.000 o mas.
M.PRECIO_HUEVO = { comun = 500, poco_comun = 2000, raro = 8000, epico = 25000, legendario = 80000, mitico = 250000 }
M.MAX_EQUIPADAS = 3

local porId = {}
for _, p in ipairs(M.LISTA) do porId[p.id] = p end
function M.get(id) return porId[id] end

function M.cantidadBonus(p)
	local n = 0
	for _ in pairs(p.bonus) do n = n + 1 end
	return n
end

-- Suma los bonus de las mascotas equipadas (ids). Devuelve multiplicadores: 1 + suma/100.
function M.multiplicadores(equipadas)
	local m = {}
	for _, s in ipairs(M.STATS) do m[s] = 1 end
	for _, id in ipairs(equipadas) do
		local p = porId[id]
		if p then
			for s, v in pairs(p.bonus) do m[s] = m[s] + v / 100 end
		end
	end
	return m
end

-- Elige una mascota al abrir un huevo. rng() devuelve [0,1). elegirEn(lista, rng) escoge dentro de la rareza.
function M.abrirHuevo(rarezaHuevo, rng)
	local tabla = M.HUEVOS[rarezaHuevo]
	if not tabla then return nil end
	local total = 0
	for _, r in ipairs(M.RAREZAS) do total = total + (tabla[r] or 0) end
	local x, acc, rareza = rng() * total, 0, nil
	for _, r in ipairs(M.RAREZAS) do
		if tabla[r] then
			acc = acc + tabla[r]
			if x < acc then rareza = r break end
		end
	end
	local cand = {}
	for _, p in ipairs(M.LISTA) do if p.rareza == rareza then cand[#cand + 1] = p end end
	return cand[math.min(#cand, math.floor(rng() * #cand) + 1)]
end

return M
