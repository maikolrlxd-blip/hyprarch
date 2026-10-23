-- Maquina de estados de una partida de Luto: espera -> intermision -> ronda -> ... -> fin. Modulo PURO (el servidor de Roblox llama aqui).
-- Reglas (Maikol): oleadas infinitas; si mueres reapareces al empezar la siguiente ronda SI queda un companero vivo; si mueren todos, fin
-- (y se paga la moneda del lobby segun la ronda alcanzada). Monedas por zombi muerto para la tienda del mapa.
local Oleadas = script and require(script.Parent.Oleadas) or require("Oleadas")

local Partida = {}
Partida.__index = Partida

Partida.DEFAULT = { max_players = 4, pausa_inicial = 8, intermision = 10 }

function Partida.new(seed, cfg)
	local c = {}
	for k, v in pairs(Partida.DEFAULT) do c[k] = v end
	if cfg then for k, v in pairs(cfg) do c[k] = v end end
	return setmetatable({ cfg = c, seed = seed or 1, estado = "esperando", ronda = 0, players = {}, order = {}, t_next = nil,
		config = nil, aparecidos = 0, restantes = 0, jefes = 0, rondaMax = 0 }, Partida)
end

function Partida:addPlayer(id)
	if self.players[id] then return false, "ya esta" end
	if #self.order >= self.cfg.max_players then return false, "partida llena" end
	self.players[id] = { id = id, vivo = true, monedas = 0, kills = 0 }
	self.order[#self.order + 1] = id
	return true
end

function Partida:vivos()
	local n = 0
	for _, id in ipairs(self.order) do if self.players[id].vivo then n = n + 1 end end
	return n
end

function Partida:comenzar(now)
	if self.estado ~= "esperando" then return false end
	self.estado = "intermision"; self.t_next = now + self.cfg.pausa_inicial; return true
end

-- Avanza el reloj. Devuelve una lista de eventos para que el servidor actue: {tipo="inicio_ronda", config=...}, {tipo="revivir", ids={...}}.
function Partida:actualizar(now)
	local ev = {}
	if self.estado == "intermision" and now >= self.t_next then
		self.ronda = self.ronda + 1; self.rondaMax = self.ronda
		local muertos = {}
		for _, id in ipairs(self.order) do local p = self.players[id]; if not p.vivo then p.vivo = true; muertos[#muertos + 1] = id end end
		if #muertos > 0 then ev[#ev + 1] = { tipo = "revivir", ids = muertos } end
		self.config = Oleadas.config(self.ronda, self.seed)
		self.aparecidos = 0
		self.restantes = self.config.cantidad + (self.config.jefe and 1 or 0)
		self.estado = "ronda"
		ev[#ev + 1] = { tipo = "inicio_ronda", ronda = self.ronda, config = self.config }
	end
	return ev
end

-- Zombis que aun faltan por aparecer (incluye el jefe como ultimo).
function Partida:porAparecer()
	if self.estado ~= "ronda" then return 0 end
	return (self.config.cantidad + (self.config.jefe and 1 or 0)) - self.aparecidos
end
function Partida:registrarAparicion() self.aparecidos = self.aparecidos + 1 end
function Partida:esAparicionJefe() return self.config ~= nil and self.config.jefe ~= nil and self.aparecidos == self.config.cantidad end

-- Un zombi (o el jefe) murio; killerId puede ser nil (murio solo). Devuelve la recompensa dada.
function Partida:zombiMuerto(killerId, esJefe, now)
	if self.estado ~= "ronda" then return 0 end
	self.restantes = self.restantes - 1
	local pago = esJefe and self.config.jefe.recompensa or self.config.recompensa
	local p = killerId and self.players[killerId]
	if p then p.monedas = p.monedas + pago; p.kills = p.kills + 1 end
	if esJefe then self.jefes = self.jefes + 1 end
	if self.restantes <= 0 and self:porAparecer() <= 0 then
		self.estado = "intermision"; self.t_next = now + self.cfg.intermision
	end
	return p and pago or 0
end

-- Un jugador murio. Si no queda nadie vivo, la partida termina. Devuelve {fin=true, rondaMax, monedasLobby} o {fin=false}.
function Partida:jugadorMuerto(id, now)
	local p = self.players[id]; if not p or not p.vivo then return { fin = false } end
	p.vivo = false
	if self:vivos() == 0 and self.estado ~= "fin" then
		self.estado = "fin"
		return { fin = true, rondaMax = self.rondaMax, monedasLobby = Oleadas.monedasLobby(self.rondaMax, self.jefes) }
	end
	return { fin = false }
end

function Partida:gastar(id, n)
	local p = self.players[id]; if not p or p.monedas < n then return false end
	p.monedas = p.monedas - n; return true
end

return Partida
