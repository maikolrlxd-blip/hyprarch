-- Logica pura del vuelo de «+1 de lanzamiento por segundo» (sin API de Roblox, probada con lupa).
-- Todas las cifras son PROVISIONALES (Maikol no ha fijado numeros): se ajustan jugando.
-- Reglas acordadas: la potencia (+1/s) fija la reserva de energia de cada vuelo; volar siempre consume; acelerar (W) y atacar
-- consumen mas; sin energia se planea (solo A/D, sin boost ni ataque). Aros y enemigos golpeados suben los puntos del vuelo;
-- al aterrizar, la distancia por el multiplicador de zona da los puntos. Rebirth reinicia SOLO la potencia.
local V = {}

V.CFG = {
	energiaBase = 12, -- segundos de vuelo con potencia 0: el primer vuelo ya llega al Mar de Nubes
	energiaPorRaiz = 1.6, -- + por la raiz de la potencia: con +1 potencia/s una curva lineal agotaba el mapa en minutos
	consumoVuelo = 1.0, -- energia/s siempre
	consumoBoost = 1.5, -- extra/s con W (era 2,5: con potencia 0 el boost vaciaba la energia en 3 s y pillar un cofre no compensaba)
	costeAtaque = 3, -- por golpe
	velocidadBase = 40, -- studs/s
	velocidadBoost = 70,
	velocidadPlaneo = 30,
	puntosAro = 25, -- sumados al "bote" del vuelo (que se multiplica por la zona al aterrizar): que merezca la pena buscarlos
	puntosEnemigo = 30,
	puntosCofre = 250, -- mas que la distancia que se pierde por el boost para pillarlo
	potenciaPorSegundo = 1,
	-- Manejo (src/Manejo.lua en el cliente) y limites que valida el servidor (src/Partida.lua). Faciles a proposito: avanzar es
	-- automatico, no se puede salir del carril ni tocar el suelo mientras quede energia, y al planear se aterriza solo.
	velocidadLateral = 22, -- A/D
	velocidadSubir = 16, -- Espacio / salto
	velocidadBajar = 20, -- S / joystick abajo
	alturaMin = 6, -- altura minima de la raiz del personaje mientras queda energia
	alturaMax = 48,
	caidaPlaneo = 4.5, -- studs/s de bajada al planear
	anchoLibre = 30, -- |x| maximo: el carril del mapa mide 66
	suelo = 0, -- techo del carril del mapa (y de la Pradera)
	lanzamiento = { duracion = 1.2, velocidad = 85, subida = 30 }, -- disparo del cañon: rapido y hacia arriba
	-- multiplicador segun la posicion hacia -Z (studs desde el origen de la Pradera), como las marcas del suelo de mapa-v01:
	-- Pradera x1, prado de la Pradera x2 (desde y=37), Mar de Nubes x3 (172), Tormenta x4 (532), Cielo alto x5 (892), Espacio x6 (1252)
	zonas = { { 0, 1 }, { 37, 2 }, { 172, 3 }, { 532, 4 }, { 892, 5 }, { 1252, 6 } },
}

function V.energiaMax(potencia, cfg)
	cfg = cfg or V.CFG
	return cfg.energiaBase + cfg.energiaPorRaiz * math.sqrt(math.max(0, potencia))
end

function V.multiplicadorZona(distancia, cfg)
	cfg = cfg or V.CFG
	local m = cfg.zonas[1][2]
	for _, z in ipairs(cfg.zonas) do
		if distancia >= z[1] then m = z[2] end
	end
	return m
end

-- Estado de un vuelo. potencia viene del jugador; bonus = multiplicadores de Mascotas.multiplicadores (impulso/resistencia/dinero/exp).
function V.nuevo(potencia, bonus, cfg)
	cfg = cfg or V.CFG
	bonus = bonus or { impulso = 1, resistencia = 1, dinero = 1, exp = 1 }
	local emax = V.energiaMax(potencia, cfg) * (bonus.resistencia or 1)
	return {
		cfg = cfg, bonus = bonus, potencia = potencia,
		energia = emax, energiaMax = emax,
		distancia = 0, bote = 0, aros = 0, golpes = 0,
		planeando = false, terminado = false, tiempo = 0,
	}
end

-- Avanza dt segundos. entrada = { boost = bool }. Devuelve la velocidad usada.
function V.paso(v, dt, entrada)
	if v.terminado then return 0 end
	local c = v.cfg
	local boost = entrada and entrada.boost and v.energia > 0
	local gasto = c.consumoVuelo + (boost and c.consumoBoost or 0)
	v.energia = math.max(0, v.energia - gasto * dt)
	v.planeando = v.energia <= 0
	local vel
	if v.planeando then vel = c.velocidadPlaneo
	elseif boost then vel = c.velocidadBoost * (v.bonus.impulso or 1)
	else vel = c.velocidadBase * (v.bonus.impulso or 1) end
	v.distancia = v.distancia + vel * dt
	v.tiempo = v.tiempo + dt
	return vel
end

-- Ataca (puño/patada): consume energia y no se puede planeando. Devuelve true si el golpe cuenta.
function V.atacar(v)
	if v.terminado or v.planeando or v.energia < v.cfg.costeAtaque then return false end
	v.energia = v.energia - v.cfg.costeAtaque
	v.golpes = v.golpes + 1
	return true
end

function V.golpearEnemigo(v)
	if v.terminado then return end
	v.bote = v.bote + v.cfg.puntosEnemigo
end

function V.cruzarAro(v)
	if v.terminado then return end
	v.aros = v.aros + 1
	v.bote = v.bote + v.cfg.puntosAro
end

function V.atraparCofre(v)
	if v.terminado then return end
	v.cofres = (v.cofres or 0) + 1
	v.bote = v.bote + v.cfg.puntosCofre
end

-- Aterrizaje: puntos = (distancia + bote) * multiplicador de zona * bonus dinero. Devuelve resultado.
-- posZona: posicion hacia -Z donde aterriza (el servidor la pasa); sin ella, la zona sale de la distancia recorrida.
function V.aterrizar(v, posZona)
	v.terminado = true
	local mult = V.multiplicadorZona(posZona or v.distancia, v.cfg)
	local base = v.distancia + v.bote
	local dinero = math.floor(base * mult * (v.bonus.dinero or 1))
	local exp = math.floor((v.distancia / 10 + v.aros * 2 + v.golpes) * (v.bonus.exp or 1))
	return { distancia = v.distancia, aros = v.aros, golpes = v.golpes, cofres = v.cofres or 0, multiplicador = mult, dinero = dinero, exp = exp,
		tiempo = v.tiempo }
end

-- Entrenamiento en tierra (+1 potencia por segundo); rebirths aumentan principalmente la velocidad de entrenamiento.
function V.entrenar(potencia, segundos, rebirths, cfg)
	cfg = cfg or V.CFG
	local vel = cfg.potenciaPorSegundo * (1 + 0.5 * (rebirths or 0))
	return potencia + vel * segundos
end

-- Rebirth: reinicia SOLO la potencia; conserva todo lo demas. Devuelve jugador nuevo.
function V.rebirth(jugador)
	return {
		potencia = 0, rebirths = (jugador.rebirths or 0) + 1,
		puntos = jugador.puntos, alas = jugador.alas, mascotas = jugador.mascotas, desbloqueos = jugador.desbloqueos,
	}
end

return V
