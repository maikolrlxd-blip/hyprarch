-- Manejo del vuelo de «+1 de lanzamiento por segundo» (Lua puro, probado con lupa): a que velocidad volar en cada fotograma segun los
-- mandos. Lo usa el cliente (client/VueloControl.client.lua) para mover su personaje; el servidor valida con los mismos limites de
-- Vuelo.CFG (src/Partida.lua). Pensado para que sea facil y se sienta bien:
--   avanzar hacia -Z es automatico (W solo acelera); A/D mueven de lado con un muro suave en el borde del carril; Espacio sube,
--   S baja y sin mandos se mantiene la altura; mientras queda energia no se baja de alturaMin; al planear se baja solo hasta el suelo;
--   todos los cambios de velocidad son suaves (nada de tirones) y el personaje se inclina en los giros.
-- Coordenadas de Roblox: x a la derecha, y arriba, el vuelo va hacia -Z (vf es la velocidad hacia delante, positiva).
local M = {}

function M.nuevo()
	return { vx = 0, vy = 0, vf = 0, t = 0, alabeo = 0, cabeceo = 0 }
end

local function hacia(actual, objetivo, rapidez, dt) -- acercamiento exponencial: igual de suave con cualquier dt
	return actual + (objetivo - actual) * (1 - math.exp(-rapidez * dt))
end

-- s: estado de M.nuevo; entrada = { lateral = -1..1, subir, bajar }; info = { planeando, boost (el que confirma el servidor), impulso };
-- x, y, z: posicion actual de la raiz del personaje (z opcional). Devuelve s con vx, vy, vf (studs/s), alabeo y cabeceo (radianes).
function M.paso(s, dt, entrada, info, x, y, cfg, z)
	entrada, info = entrada or {}, info or {}
	local imp = info.impulso or 1
	local L = cfg.lanzamiento
	s.t = s.t + dt
	local vfObj, vyObj
	if s.t < L.duracion then -- disparo del cañon: rapido y subiendo cada vez menos
		vfObj = L.velocidad * imp
		vyObj = L.subida * (1 - s.t / L.duracion)
	elseif info.planeando then
		vfObj = cfg.velocidadPlaneo
		vyObj = -cfg.caidaPlaneo * (entrada.bajar and 2 or 1)
	else
		vfObj = (info.boost and cfg.velocidadBoost or cfg.velocidadBase) * imp
		vyObj = (entrada.subir and cfg.velocidadSubir or 0) - (entrada.bajar and cfg.velocidadBajar or 0)
	end
	if z and cfg.finMapa and -z >= cfg.finMapa then -- final del mapa: deja de avanzar y baja al ultimo tramo del carril
		vfObj, vyObj = 0, -cfg.caidaPlaneo * 3
	end
	local vxObj = math.max(-1, math.min(1, entrada.lateral or 0)) * cfg.velocidadLateral
	local borde = cfg.anchoLibre - 6 -- muro suave: empuja hacia dentro cuanto mas se pasa (con A/D a tope se queda a ~2 del limite)
	if math.abs(x) > borde then
		local signo = x > 0 and 1 or -1
		vxObj = vxObj - signo * (math.abs(x) - borde) * 6
		if signo * vxObj > 0 and math.abs(x) >= cfg.anchoLibre then vxObj = 0 end
	end
	s.vx = hacia(s.vx, vxObj, 9, dt) -- giros rapidos: el lado responde al momento
	s.vy = hacia(s.vy, vyObj, 5, dt)
	-- suelo y techo blandos sobre la velocidad (no sobre el objetivo, para no pasarse): frenan antes del limite y empujan si se pasa
	if s.t >= L.duracion and not info.planeando then s.vy = math.max(s.vy, (cfg.alturaMin - y) * 4) end
	s.vy = math.min(s.vy, (cfg.alturaMax - y) * 4)
	s.vf = hacia(s.vf, vfObj, s.t < L.duracion and 12 or 3, dt) -- el disparo arranca de golpe; el boost entra y sale suave
	s.alabeo = hacia(s.alabeo, -s.vx / cfg.velocidadLateral * 0.6, 8, dt) -- unos 35 grados en el giro maximo
	s.cabeceo = hacia(s.cabeceo, math.max(-0.35, math.min(0.35, s.vy / 30)), 6, dt)
	return s
end

return M
