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
	-- nubarron en la Tormenta, cometa en el Cielo alto, ovni y meteorito en el Espacio
	zonas = {
		{ desde = 40, hasta = 172, tipos = { "globo" }, cantidad = 2 },
		{ desde = 172, hasta = 532, tipos = { "nube", "globo" }, cantidad = 5 },
		{ desde = 532, hasta = 892, tipos = { "nubarron", "nube" }, cantidad = 5 },
		{ desde = 892, hasta = 1252, tipos = { "cometa" }, cantidad = 5 },
		{ desde = 1252, hasta = 1612, tipos = { "ovni", "meteorito" }, cantidad = 5 },
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
