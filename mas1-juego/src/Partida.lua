-- Sesion de vuelo de un jugador en el servidor de «+1 de lanzamiento por segundo» (Lua puro, probado con lupa; el adaptador de
-- Roblox es server/Partida.server.lua). El cliente mueve su personaje (para que responda al instante) y solo manda intenciones
-- (lanzar, boost, turbo, ataque); aqui se lleva lo que cuenta (energia, boost, distancia, zona, puntos) y se valida cada paso:
-- cada tick gana un presupuesto de distancia segun la velocidad permitida en ese momento (con margen para el lag); si el personaje
-- se mueve mas de lo que tiene, o se sale de los limites, el servidor lo devuelve a la ultima posicion buena. La distancia es lo
-- avanzado hacia -Z desde el lanzamiento y la zona sale de la posicion en el mapa. Vectores como tablas {x, y, z}.
local P = {}

P.TOL = {
	factor = 1.3, -- margen sobre la velocidad permitida
	extra = 6, -- studs/s de margen fijo
	rafaga = 1.5, -- segundos de presupuesto acumulable (paquetes que llegan juntos)
	salto = 2, -- studs de margen por paso
	frenada = 45, -- studs/s2: lo rapido que baja la velocidad permitida al soltar el boost (el cliente frena suave)
	planeoExtra = 4, -- segundos de margen para llegar al suelo planeando
	vueloMax = 600, -- segundos: corte de seguridad
	gracia = 0.4, -- segundos sin medir tras un teletransporte (lanzar o corregir): aun llegan posiciones de antes
	ventana = 4, -- segundos: media hacia delante, mas estricta que el presupuesto (pilla ir algo mas rapido de forma seguida)
	factorMedia = 1.15,
	extraMedia = 10, -- studs
}

-- V = src/Vuelo.lua; E = src/Encuentros.lua (aros, enemigos y cofres; sin E el vuelo va sin encuentros).
function P.nueva(V, E)
	return { V = V, E = E, estado = "tierra", violaciones = 0 }
end

function P.enVuelo(s)
	return s.estado == "vuelo"
end

function P.lanzar(s, pos, potencia, bonus)
	if s.estado == "vuelo" then return false end
	s.estado = "vuelo"
	s.v = s.V.nuevo(potencia or 0, bonus)
	s.z0 = pos.z
	s.ultima = { x = pos.x, y = pos.y, z = pos.z }
	s.presZ, s.presX, s.presY = 0, 0, 0
	s.hist, s.pendiente = {}, 0
	s.boost, s.turboHasta, s.t, s.avance = false, -1, 0, 0
	s.vPermitida = nil
	s.planeoT, s.yPlaneo = nil, nil
	s.gracia = P.TOL.gracia
	s.arosHechos = {}
	s.cofre = s.E and s.E.nuevoCofre(pos) or nil
	s.cofresSalidos = s.cofre and 1 or 0
	return true
end

function P.cancelar(s) -- murio, se fue o se quedo sin personaje: sin resultado
	s.estado = "tierra"
end

function P.boostActivo(s)
	return s.estado == "vuelo" and not s.v.planeando and (s.boost or s.t < s.turboHasta)
end

-- Intenciones del cliente. Devuelve el nombre de un efecto si hay que mostrarlo ("golpe") y, si el golpe alcanza a un enemigo de
-- mundo.enemigos, su indice (queda con vivo = false: su reaparicion la lleva quien guarda el mundo).
function P.intencion(s, nombre, valor, mundo)
	if s.estado ~= "vuelo" then return nil end
	if nombre == "boost" then
		s.boost = valor == true
	elseif nombre == "turbo" then -- boton TURBO del HUD (un toque): 1,2 s de boost
		s.turboHasta = s.t + 1.2
	elseif nombre == "ataque" or nombre == "puno" or nombre == "patada" then
		if not s.V.atacar(s.v) then return nil end
		local i = s.E and mundo and mundo.enemigos and s.E.enemigoAlAlcance(s.ultima, mundo.enemigos)
		if i then
			mundo.enemigos[i].vivo = false
			s.V.golpearEnemigo(s.v)
		end
		return "golpe", i
	end
	return nil
end

-- Velocidades maximas permitidas ahora: hacia delante (z), de lado (x) y vertical (y), cada una con su presupuesto.
function P.limites(s, dt)
	local c, imp, T = s.v.cfg, s.v.bonus.impulso or 1, P.TOL
	local objetivo
	if s.t < c.lanzamiento.duracion then objetivo = c.lanzamiento.velocidad * imp
	elseif s.v.planeando then objetivo = c.velocidadPlaneo
	elseif P.boostActivo(s) then objetivo = c.velocidadBoost * imp
	else objetivo = c.velocidadBase * imp end
	-- sube al momento y baja poco a poco (el cliente tambien frena suave)
	s.vPermitida = math.max(objetivo, (s.vPermitida or objetivo) - T.frenada * dt)
	local z = s.vPermitida * T.factor + T.extra
	local x = (c.velocidadLateral + 12) * T.factor + T.extra -- + el empujon del muro suave
	local y = math.max(c.lanzamiento.subida, c.velocidadSubir, c.velocidadBajar, c.caidaPlaneo * 2) * T.factor + T.extra
	return z, x, y
end

-- Un tick del servidor con la posicion actual del personaje; mundo = { aros = {{centro, radio}}, enemigos = ... } (opcional). Devuelve:
-- { corregir = pos buena o nil, aterrizaje = resultado o nil, energia (0-1), planeando, distancia, mult, puntos, boost,
--   aros = indices de aros cruzados en este tick o nil, cofre = posicion del cofre o nil, cofreAtrapado = posicion o nil }
function P.tick(s, dt, pos, mundo)
	if s.estado ~= "vuelo" then return nil end
	local V, c, T = s.V, s.v.cfg, P.TOL
	s.t = s.t + dt
	local maxZ, maxX, maxY = P.limites(s, dt)
	s.presZ = math.min(s.presZ + maxZ * dt, maxZ * T.rafaga)
	s.presX = math.min(s.presX + maxX * dt, maxX * T.rafaga)
	s.presY = math.min(s.presY + maxY * dt, maxY * T.rafaga)
	local u = s.ultima
	local dZ, dX, dY = math.abs(pos.z - u.z), math.abs(pos.x - u.x), math.abs(pos.y - u.y)
	local fuera = math.abs(pos.x) > c.anchoLibre + 8 or pos.y > c.alturaMax + 15
	s.pendiente = s.pendiente + s.vPermitida * dt
	local media = false -- lo avanzado en la ventana frente a lo permitido en el mismo tiempo (el lag no le afecta)
	if s.gracia <= 0 then
		local hecho, permitido = u.z - pos.z, s.pendiente
		for _, h in ipairs(s.hist) do
			if h.t > s.t - T.ventana then hecho, permitido = hecho + h.dz, permitido + h.perm end
		end
		media = hecho > permitido * T.factorMedia + T.extraMedia
	end
	local r = {}
	if s.gracia > 0 then
		s.gracia = s.gracia - dt -- el presupuesto sigue creciendo: lo avanzado mientras tanto se mide despues
	elseif dZ > s.presZ + T.salto or dX > s.presX + T.salto or dY > s.presY + T.salto or fuera or media then
		s.violaciones = s.violaciones + 1
		r.motivo = fuera and 'fuera' or media and 'media' or dZ > s.presZ + T.salto and 'z' or dX > s.presX + T.salto and 'x' or 'y'
		s.gracia = T.gracia
		s.hist, s.pendiente = {}, 0
		r.corregir = { x = u.x, y = u.y, z = u.z }
	else
		s.presZ, s.presX, s.presY = s.presZ - dZ, s.presX - dX, s.presY - dY
		s.hist[#s.hist + 1] = { t = s.t, dz = u.z - pos.z, perm = s.pendiente }
		s.pendiente = 0
		while s.hist[1] and s.hist[1].t <= s.t - T.ventana do table.remove(s.hist, 1) end
		if s.E and mundo and mundo.aros then -- aros: con el tramo validado, cada uno una vez por vuelo
			for i, aro in ipairs(mundo.aros) do
				if not s.arosHechos[i] and s.E.cruzaAro(u, pos, aro) then
					s.arosHechos[i] = true
					s.V.cruzarAro(s.v)
					r.aros = r.aros or {}
					r.aros[#r.aros + 1] = i
				end
			end
		end
		s.ultima = { x = pos.x, y = pos.y, z = pos.z }
		s.avance = math.max(s.avance, s.z0 - pos.z)
	end
	if c.finMapa and -s.ultima.z >= c.finMapa then s.v.energia = 0 end -- final del mapa: se planea y se aterriza en el ultimo tramo
	V.paso(s.v, dt, { boost = P.boostActivo(s) })
	s.v.distancia = s.avance -- cuenta lo avanzado de verdad, no lo que dice la velocidad
	if s.cofre then -- cofre volador: huye del jugador; al atraparlo, puntos y (si quedan) otro por delante
		if s.E.pasoCofre(s.cofre, dt, s.ultima) then
			s.V.atraparCofre(s.v)
			r.cofreAtrapado = { x = s.cofre.pos.x, y = s.cofre.pos.y, z = s.cofre.pos.z }
			if s.cofresSalidos < s.E.CFG.cofresPorVuelo then
				s.cofre = s.E.nuevoCofre(s.ultima)
				s.cofresSalidos = s.cofresSalidos + 1
			else
				s.cofre = nil
			end
		end
		r.cofre = s.cofre and s.cofre.pos
	end
	local y = s.ultima.y
	if s.v.planeando then
		if not s.planeoT then s.planeoT, s.yPlaneo = 0, y end
		s.planeoT = s.planeoT + dt
	end
	local enSuelo = s.v.planeando and y <= c.suelo + 4.5 -- la raiz de un personaje de pie queda unos 3 studs sobre el suelo
	local caido = y < c.suelo - 30 -- se salio del mapa
	local tarde = s.planeoT and s.planeoT > (s.yPlaneo - c.suelo) / c.caidaPlaneo + T.planeoExtra -- no baja al planear
	local posZona = -s.ultima.z
	if enSuelo or caido or tarde or s.t > T.vueloMax then
		s.estado = "tierra"
		r.aterrizaje = V.aterrizar(s.v, posZona)
	end
	r.energia = s.v.energiaMax > 0 and s.v.energia / s.v.energiaMax or 0
	r.planeando = s.v.planeando
	r.distancia = s.avance
	r.mult = V.multiplicadorZona(posZona, c)
	r.puntos = math.floor((s.avance + s.v.bote) * r.mult * (s.v.bonus.dinero or 1))
	r.boost = P.boostActivo(s)
	return r
end

return P
