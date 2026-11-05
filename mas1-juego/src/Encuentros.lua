-- Encuentros del vuelo de «+1 de lanzamiento por segundo» (Lua puro, probado con lupa): aros que se cruzan, enemigos que se golpean y
-- cofres voladores que huyen. Faciles a proposito: el aro cuenta con un margen por fuera del borde, el golpe alcanza al enemigo vivo
-- mas cercano a 12 studs y el cofre huye algo mas rapido que el vuelo normal (hay que usar el boost para pillarlo, pero con boost se
-- pilla en un par de segundos). Los enemigos van repartidos por zona, alternando lados, separados entre si y lejos de los aros: sin
-- saturar. Coordenadas de Roblox; el vuelo va hacia -Z. Vectores como tablas {x, y, z}.
local E = {}

E.CFG = {
	margenAro = 1.5, -- studs por fuera del radio que aun cuentan
	alcance = 12, -- golpe: distancia maxima al enemigo (delante, o como mucho 4 studs detras)
	reaparicion = 15, -- segundos hasta que vuelve un enemigo golpeado
	cofreDistancia = 140, -- aparece por delante del jugador
	cofreAltura = 18,
	cofreVista = 55, -- a esta distancia empieza a huir
	cofreHuida = 52, -- studs/s huyendo: mas que Vuelo.CFG.velocidadBase (40), menos que velocidadBoost (70)
	cofreCalma = 22, -- studs/s sin nadie cerca
	cofreEspera = 170, -- si se adelanta tanto, espera
	cofreAtrapar = 7,
	cofresPorVuelo = 2,
	separacion = 40, -- entre enemigos
	lejosDeAros = 18, -- de un aro (sumado a su radio)
	-- enemigos por zona (studs hacia -Z), con los tipos de enemigos-v02: globo en la Pradera, nube en el Mar de Nubes,
	-- nubarron en la Tormenta, cometa en el Cielo alto, ovni y meteorito en el Espacio. Zonas largas (31/10): los mismos limites
	-- que Vuelo.CFG.zonas y el mapa (lo comprueba un test), un enemigo cada ~150 studs
	zonas = {
		{ desde = 40, hasta = 1252, tipos = { "globo" }, cantidad = 8 },
		{ desde = 1252, hasta = 2332, tipos = { "nube", "globo" }, cantidad = 7 },
		{ desde = 2332, hasta = 3772, tipos = { "nubarron", "nube" }, cantidad = 10 },
		{ desde = 3772, hasta = 5932, tipos = { "cometa" }, cantidad = 14 },
		{ desde = 5932, hasta = 8812, tipos = { "ovni", "meteorito" }, cantidad = 19 },
	},
}

local function d2(a, b)
	return (a.x - b.x) ^ 2 + (a.y - b.y) ^ 2 + (a.z - b.z) ^ 2
end

-- ¿El tramo a -> b atraviesa el aro (de cara a -Z)? Cruza su plano z y en ese punto queda dentro del radio + margen.
function E.cruzaAro(a, b, aro, cfg)
	cfg = cfg or E.CFG
	local c = aro.centro
	if a.z == b.z or (a.z - c.z) * (b.z - c.z) > 0 then return false end
	local t = (c.z - a.z) / (b.z - a.z)
	local x, y = a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t
	return (x - c.x) ^ 2 + (y - c.y) ^ 2 <= (aro.radio + cfg.margenAro) ^ 2
end

-- El enemigo vivo mas cercano al alcance del golpe desde pos. Devuelve su indice o nil.
function E.enemigoAlAlcance(pos, enemigos, cfg)
	cfg = cfg or E.CFG
	local mejor, dmin = nil, cfg.alcance ^ 2
	for i, en in ipairs(enemigos) do
		if en.vivo and en.pos.z - pos.z < 4 then
			local d = d2(en.pos, pos)
			if d <= dmin then mejor, dmin = i, d end
		end
	end
	return mejor
end

-- Coloca los enemigos de todas las zonas. aros: lista de {centro, radio}; aleatorio(): numero en [0, 1).
-- Devuelve lista de {tipo, pos, vivo}. Si un hueco no cabe tras 12 intentos, se queda sin enemigo (mejor de menos que saturar).
function E.colocarEnemigos(aros, aleatorio, cfg)
	cfg = cfg or E.CFG
	local lista = {}
	local function libre(p)
		for _, a in ipairs(aros) do
			if d2(p, a.centro) < (cfg.lejosDeAros + a.radio) ^ 2 then return false end
		end
		for _, en in ipairs(lista) do
			if d2(p, en.pos) < cfg.separacion ^ 2 then return false end
		end
		return true
	end
	for _, z in ipairs(cfg.zonas) do
		local tramo = (z.hasta - z.desde) / z.cantidad
		for k = 1, z.cantidad do
			local lado = (k % 2 == 0) and 1 or -1
			for _ = 1, 12 do
				local p = { x = lado * (6 + aleatorio() * 18), y = 10 + aleatorio() * 18,
					z = -(z.desde + (k - 0.5) * tramo + (aleatorio() - 0.5) * tramo * 0.5) }
				if libre(p) then
					lista[#lista + 1] = { tipo = z.tipos[(k - 1) % #z.tipos + 1], pos = p, vivo = true }
					break
				end
			end
		end
	end
	return lista
end

-- Orbes «+1» (Maikol, 30/10: el vuelo «aburre»): trazos de 7 orbes por el carril, en eslalon, en subida o en diagonal, para que
-- haya que moverse todo el rato. Cada uno da +1 de potencia. Cliente y servidor los generan iguales con la misma semilla (E.azar).
-- Medido el 05/11 con un piloto simulado que va al orbe mas cercano (tools/medir_numeros.py, tests/test_encuentros.py): con 9 studs
-- entre orbes y radio 3,5 cogia el 95 % a velocidad base pero solo el 30 % con boost (85 studs/s: 0,1 s entre orbes, y el eslalon
-- pide cruzar medio carril); con 14 y 4,5 coge el 100 % a base y el 74 % con boost. El orbe se ve de 1,8 studs de diametro.
E.CFG.orbe = { radio = 4.5, cadaStuds = 180, porTrazo = 7, paso = 14, semilla = 3017 } -- un trazo cada 180 studs de zona

function E.azar(semilla) -- generador congruencial propio: mismo resultado en el cliente, en el servidor y en las pruebas
	local x = semilla % 2147483647
	return function()
		x = (x * 48271) % 2147483647
		return x / 2147483647
	end
end

function E.colocarOrbes(cfg)
	cfg = cfg or E.CFG
	local o, azar, lista = cfg.orbe, E.azar(cfg.orbe.semilla), {}
	for _, z in ipairs(cfg.zonas) do
		local trazos = math.max(1, math.floor((z.hasta - z.desde) / o.cadaStuds + 0.5))
		local tramo = (z.hasta - z.desde) / trazos
		for g = 1, trazos do
			local z0, forma, x0 = z.desde + (g - 0.5) * tramo - o.paso * 3, g % 3, (azar() - 0.5) * 28
			for k = 0, o.porTrazo - 1 do
				local t = k / (o.porTrazo - 1)
				local x, y
				if forma == 0 then x, y = x0 + math.sin(t * math.pi * 2) * 10, 18 -- eslalon
				elseif forma == 1 then x, y = x0, 10 + t * 16 -- subida
				else x, y = x0 - 12 + t * 24, 24 - t * 10 end -- diagonal
				lista[#lista + 1] = { pos = { x = math.max(-26, math.min(26, x)), y = y, z = -(z0 + k * o.paso) } }
			end
		end
	end
	return lista
end

-- ¿El tramo a -> b pasa a menos de radio del orbe?
function E.tocaOrbe(a, b, orbe, radio)
	local p = orbe.pos
	local abx, aby, abz = b.x - a.x, b.y - a.y, b.z - a.z
	local l2 = abx * abx + aby * aby + abz * abz
	local t = l2 > 0 and math.max(0, math.min(1, ((p.x - a.x) * abx + (p.y - a.y) * aby + (p.z - a.z) * abz) / l2)) or 0
	return d2(p, { x = a.x + abx * t, y = a.y + aby * t, z = a.z + abz * t }) <= radio * radio
end

-- Cofre volador por delante de pos.
function E.nuevoCofre(pos, cfg)
	cfg = cfg or E.CFG
	return { pos = { x = 0, y = cfg.cofreAltura, z = pos.z - cfg.cofreDistancia }, vel = cfg.cofreCalma, t = 0, atrapado = false }
end

-- Mueve el cofre dt segundos segun donde esta el jugador (pj). Devuelve true si el jugador lo atrapa en este paso.
function E.pasoCofre(c, dt, pj, cfg)
	cfg = cfg or E.CFG
	if c.atrapado then return false end
	if math.sqrt(d2(c.pos, pj)) <= cfg.cofreAtrapar then
		c.atrapado = true
		return true
	end
	c.t = c.t + dt
	local delante = pj.z - c.pos.z -- > 0: el cofre va por delante
	local objetivo = math.sqrt(d2(c.pos, pj)) < cfg.cofreVista and cfg.cofreHuida or cfg.cofreCalma
	if delante > cfg.cofreEspera or delante < -10 then objetivo = 0 end -- muy adelantado, o ya lo pasaron: espera
	c.vel = c.vel + (objetivo - c.vel) * (1 - math.exp(-2.5 * dt))
	c.pos.z = c.pos.z - c.vel * dt
	c.pos.x = math.sin(c.t * 0.8) * 12 -- zigzag suave dentro del carril
	c.pos.y = cfg.cofreAltura + math.sin(c.t * 1.3) * 3
	return false
end

return E
