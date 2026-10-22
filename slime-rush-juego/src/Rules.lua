-- Reglas de partida de Slime Rush v2. Modulo PURO (sin API de Roblox): el servidor es la autoridad y llama
-- a estas funciones con posiciones y el tiempo actual; aqui se valida TODO. Las funciones devuelven
-- (true, datos) o (false, "motivo").
local Rng = script and require(script.Parent.Rng) or require("Rng")

local Rules = {}
Rules.__index = Rules

Rules.DEFAULT = {
	-- Tiempos (la duracion total esta por decidir; todo ajustable)
	countdown = 3, explore = 360, return_window = 240, collapse = 30, results = 8, -- el regreso se abre a los 6:00
	arrival_bonus = { 150, 100, 60, 30 }, arrival_default = 10,                      -- 1o, 2o, 3o, 4o, resto
	backpack = 12,                                                                   -- capacidad de la mochila
	-- Combate: al DERROTAR a alguien queda inconsciente en el suelo y se le puede saquear
	downed_time = 12,                                                                -- segundos inconsciente
	wake_immunity = 8,                                                               -- inmunidad al despertar
	loot_min = 1, loot_max = 2, loot_cooldown = 1.2,                                 -- objetos por saqueo y espera entre saqueos
	bound_hits = 2, bound_window = 3,                                                -- objetos ligados: 2 saqueos seguidos en 3 s
	deposit_time = 2,                                                                -- canal de deposito (se interrumpe si te derrotan)
	reach = 12,                                                                      -- alcance para recoger/saquear (studs)
	goal_radius = 48,
	max_players = 24,
	immunity = 8,                                                                    -- tras resucitar por el volcan
	-- Desastres del colapso final
	quakes = 4, tornados = 3, strikes = 18,
}

local function dist(a, b) return math.sqrt((a.x - b.x) ^ 2 + (a.z - b.z) ^ 2) end
local function value_of(items) local s = 0; for _, it in ipairs(items) do s = s + it.value end; return s end
local function merge(base, over)
	local out = {}
	for k, v in pairs(base) do out[k] = v end
	if over then for k, v in pairs(over) do out[k] = v end end
	return out
end

function Rules.new(world, cfg, seed)
	cfg = merge(Rules.DEFAULT, cfg)
	if world then cfg.goal_radius = world.goal.radius end
	return setmetatable({ world = world, cfg = cfg, rng = Rng.new(seed or (world and world.seed) or 1),
		players = {}, order = {}, taken_nodes = {}, taken_chests = {}, taken_rares = {}, arrivals = 0, t0 = nil, eruption = nil }, Rules)
end

function Rules:start(now) self.t0 = now end

-- generating | countdown | explore | return | collapse | ended
function Rules:phase(now)
	if not self.t0 then return "generating" end
	local t, c = now - self.t0, self.cfg
	if t < c.countdown then return "countdown" end
	if t < c.countdown + c.explore then return "explore" end
	if t < c.countdown + c.explore + c.return_window then return "return" end
	if t < c.countdown + c.explore + c.return_window + c.collapse then return "collapse" end
	return "ended"
end

function Rules:return_opens_in(now) -- segundos hasta que se abre el regreso (nil si ya se abrio)
	if not self.t0 then return nil end
	local left = self.t0 + self.cfg.countdown + self.cfg.explore - now
	return left > 0 and left or nil
end

function Rules:collapse_starts_at() return self.t0 + self.cfg.countdown + self.cfg.explore + self.cfg.return_window end

function Rules:addPlayer(id, now)
	local ph = self:phase(now or 0)
	if self.players[id] then return false, "ya esta" end
	if #self.order >= self.cfg.max_players then return false, "partida llena" end
	if ph ~= "generating" and ph ~= "countdown" then return false, "la partida ya empezo" end
	self.players[id] = { id = id, items = {}, deposited = false, score = 0, bonus = 0, rank = nil,
		immune_until = -1, downed_until = nil, loot_ready = 0, depositing = nil, hits = {} }
	self.order[#self.order + 1] = id
	return true
end

-- Despierta a quien ya cumplio su tiempo inconsciente (con inmunidad).
local function refresh(self, p, now)
	if p.downed_until and now >= p.downed_until then
		p.downed_until = nil
		p.immune_until = now + self.cfg.wake_immunity
	end
end

function Rules:isDowned(id, now)
	local p = self.players[id]
	if not p then return false end
	refresh(self, p, now)
	return p.downed_until ~= nil
end

local function active(self, id, now)
	local p = self.players[id]
	if not p then return nil, "jugador desconocido" end
	local ph = self:phase(now)
	if ph ~= "explore" and ph ~= "return" then return nil, "fuera de fase (" .. ph .. ")" end
	if p.deposited then return nil, "ya llegaste a la meta" end
	refresh(self, p, now)
	if p.downed_until then return nil, "estas inconsciente" end
	return p
end

local function room(self, p, n) return #p.items + n <= self.cfg.backpack end

function Rules:collectNode(id, nodeId, pos, now)
	local p, why = active(self, id, now); if not p then return false, why end
	local nd = self.world.nodes[nodeId]
	if not nd then return false, "nodo inexistente" end
	if self.taken_nodes[nodeId] then return false, "ya fue recogido" end
	if dist(pos, nd) > self.cfg.reach then return false, "muy lejos" end
	if not room(self, p, 1) then return false, "mochila llena" end
	self.taken_nodes[nodeId] = id
	local item = { id = "n" .. nodeId, kind = nd.kind, value = nd.value }
	p.items[#p.items + 1] = item
	return true, item
end

function Rules:claimChest(id, chestId, pos, now)
	local p, why = active(self, id, now); if not p then return false, why end
	local ch = self.world.chests[chestId]
	if not ch then return false, "cofre inexistente" end
	if self.taken_chests[chestId] then return false, "ya fue abierto" end -- el servidor decide UN solo ganador
	if dist(pos, ch) > self.cfg.reach then return false, "muy lejos" end
	if not room(self, p, #ch.loot) then return false, "mochila llena" end -- no se consume el cofre
	self.taken_chests[chestId] = id
	for i, it in ipairs(ch.loot) do
		p.items[#p.items + 1] = { id = "c" .. chestId .. "_" .. i, kind = it.kind, name = it.name, value = it.value, rare = it.rare, bound = it.bound }
	end
	return true, ch.loot
end

function Rules:claimRare(id, siteId, pos, now)
	local p, why = active(self, id, now); if not p then return false, why end
	local r = self.world.rares[siteId]
	if not r or not r.active then return false, "no hay slime raro ahi" end
	if self.taken_rares[siteId] then return false, "ya fue capturado" end
	if dist(pos, r) > self.cfg.reach then return false, "muy lejos" end
	if not room(self, p, 1) then return false, "mochila llena" end
	self.taken_rares[siteId] = id
	local item = { id = "r" .. siteId, kind = "slime_raro", name = r.slime, value = r.value, rare = true, bound = true }
	p.items[#p.items + 1] = item
	return true, item
end

local function interrupt(p) local was = p.depositing ~= nil; p.depositing = nil; return was end

-- DERROTA: el juego llama aqui cuando el atacante vence a la victima (el combate vive fuera de este modulo).
-- La victima queda inconsciente 'downed_time' segundos; no puede actuar y su deposito se interrumpe.
function Rules:knockOut(attackerId, victimId, now)
	local at, why = active(self, attackerId, now); if not at then return false, why end
	local vi = self.players[victimId]
	if not vi then return false, "victima desconocida" end
	if vi.deposited then return false, "la victima ya llego a la meta" end
	refresh(self, vi, now)
	if vi.downed_until then return false, "ya esta inconsciente" end
	if now < vi.immune_until then return false, "inmune" end
	interrupt(vi)
	vi.downed_until = now + self.cfg.downed_time
	vi.downed_by = attackerId
	return true, { wakes_at = vi.downed_until }
end

-- SAQUEO: solo a un jugador inconsciente; quita 1-2 objetos al azar (los ligados exigen 'bound_hits' saqueos seguidos).
function Rules:lootDowned(looterId, victimId, looterPos, victimPos, now)
	local lo, why = active(self, looterId, now); if not lo then return false, why end
	local vi = self.players[victimId]
	if not vi then return false, "victima desconocida" end
	if looterId == victimId then return false, "no puedes saquearte" end
	if vi.deposited then return false, "ya llego a la meta" end
	refresh(self, vi, now)
	if not vi.downed_until then return false, "no esta inconsciente" end
	if dist(looterPos, victimPos) > self.cfg.reach then return false, "muy lejos" end
	if now < lo.loot_ready then return false, "espera" end
	lo.loot_ready = now + self.cfg.loot_cooldown
	if #vi.items == 0 then return true, { stolen = {}, dropped = {} } end
	local want = self.rng:int(self.cfg.loot_min, self.cfg.loot_max)
	local stolen, dropped = {}, {}
	for _, it in ipairs(self.rng:shuffle(vi.items)) do
		if #stolen >= want then break end
		local ok = true
		if it.bound then
			local h = vi.hits[it.id]
			if h and now - h.t <= self.cfg.bound_window then h.n = h.n + 1 else h = { n = 1, t = now }; vi.hits[it.id] = h end
			ok = h.n >= self.cfg.bound_hits
		end
		if ok then stolen[#stolen + 1] = it end
	end
	for _, it in ipairs(stolen) do
		for i, x in ipairs(vi.items) do if x == it then table.remove(vi.items, i); break end end
		vi.hits[it.id] = nil
		if #lo.items < self.cfg.backpack then lo.items[#lo.items + 1] = it else dropped[#dropped + 1] = it end -- lo que no cabe cae al suelo
	end
	return true, { stolen = stolen, dropped = dropped }
end

-- Caida/ahogamiento: sueltas la mitad (redondeando hacia abajo) de lo que llevas.
function Rules:die(id, now)
	local p, why = active(self, id, now); if not p then return false, why end
	interrupt(p)
	local drop = {}
	for _ = 1, math.floor(#p.items / 2) do
		local i = self.rng:int(1, #p.items)
		drop[#drop + 1] = table.remove(p.items, i)
	end
	return true, drop
end

-- ===== Volcan =====
-- Si alguien SALTA al crater, la erupcion queda ASEGURADA: la lava crece despacio desde el crater hasta un
-- tope (que nunca alcanza la meta), asi complica el juego sin volverlo imposible. Quien salto pierde lo que llevaba.
function Rules:enterCrater(id, pos, now)
	local v = self.world.volcano
	if not v then return false, "no hay volcan" end
	local p, why = active(self, id, now); if not p then return false, why end
	if self.eruption then return false, "el volcan ya hizo erupcion" end
	if dist(pos, v) > v.crater_radius + 2 then return false, "no estas en el crater" end
	interrupt(p)
	local lost = #p.items
	p.items = {}
	p.immune_until = now + self.cfg.immunity
	self.eruption = { t0 = now, by = id }
	return true, { erupted_at = now, lost = lost }
end

function Rules:lavaRadius(now)
	local v, e = self.world.volcano, self.eruption
	if not v or not e then return 0 end
	return math.min(v.max_lava, v.crater_radius + v.speed * (now - e.t0))
end

function Rules:inLava(x, z, now)
	local v = self.world.volcano
	if not v or not self.eruption then return false end
	return dist({ x = x, z = z }, v) <= self:lavaRadius(now)
end

-- ===== Colapso final: desastres naturales =====
-- Lista determinista (misma partida = mismos desastres) de eventos con tiempo relativo al inicio del colapso:
-- terremotos que abren el suelo, tornados, tormenta con rayos, erupcion y, al final, el hundimiento de la isla.
function Rules:disasterSchedule()
	if self._schedule then return self._schedule end
	local rg, w, c = self.rng:fork("desastres"), self.world, self.cfg
	local size, ev = w.size, {}
	local function land()
		for _ = 1, 200 do
			local x, z = rg:range(40, size - 40), rg:range(40, size - 40)
			if w.walkable(x, z) then return x, z end
		end
		return w.goal.x, w.goal.z
	end
	ev[#ev + 1] = { t = 0, kind = "tormenta", x = w.goal.x, z = w.goal.z, radius = size, duration = c.collapse }
	for i = 1, c.quakes do
		local x, z = land()
		ev[#ev + 1] = { t = (i - 1) * (c.collapse * 0.7 / c.quakes) + 1, kind = "terremoto", x = x, z = z, radius = rg:range(120, 220), duration = 8 }
	end
	for i = 1, c.tornados do
		local x, z = land(); local x2, z2 = land()
		ev[#ev + 1] = { t = rg:range(2, c.collapse * 0.5), kind = "tornado", x = x, z = z, x2 = x2, z2 = z2, radius = 40, duration = 15 }
	end
	for _ = 1, c.strikes do
		local x, z = land()
		ev[#ev + 1] = { t = rg:range(1, c.collapse - 1), kind = "rayo", x = x, z = z, radius = 12, duration = 0.6 }
	end
	if w.volcano then
		ev[#ev + 1] = { t = 1, kind = "erupcion", x = w.volcano.x, z = w.volcano.z, radius = w.volcano.max_lava, duration = c.collapse - 1 }
	end
	ev[#ev + 1] = { t = c.collapse * 0.55, kind = "hundimiento", x = w.goal.x, z = w.goal.z, radius = size * 0.45, duration = c.collapse * 0.45 }
	table.sort(ev, function(a, b) if a.t ~= b.t then return a.t < b.t end; return a.kind < b.kind end)
	self._schedule = ev
	return ev
end

-- ===== Deposito en la meta =====
function Rules:startDeposit(id, pos, now)
	local p, why = active(self, id, now); if not p then return false, why end
	if self:phase(now) ~= "return" then return false, "la meta aun no se abre" end
	if dist(pos, self.world.goal) > self.cfg.goal_radius then return false, "fuera de la meta" end
	p.depositing = now
	return true
end

function Rules:cancelDeposit(id) local p = self.players[id]; return p ~= nil and interrupt(p) end

function Rules:finishDeposit(id, pos, now)
	local p, why = active(self, id, now); if not p then return false, why end
	if not p.depositing then return false, "no hay deposito en curso" end
	if now - p.depositing < self.cfg.deposit_time then return false, "aun no termina el canal" end
	if dist(pos, self.world.goal) > self.cfg.goal_radius then p.depositing = nil; return false, "saliste de la meta" end
	self.arrivals = self.arrivals + 1
	p.rank = self.arrivals
	p.bonus = self.cfg.arrival_bonus[p.rank] or self.cfg.arrival_default
	p.score = value_of(p.items) + p.bonus
	p.deposited, p.depositing, p.delivered = true, nil, #p.items
	p.items = {}
	return true, { rank = p.rank, bonus = p.bonus, score = p.score }
end

-- Resultados: quien no llego a la meta antes del colapso lo pierde TODO.
function Rules:finalScores(now)
	local ph = self:phase(now)
	if ph ~= "collapse" and ph ~= "ended" then return false, "la partida no termino" end
	local out = {}
	for _, id in ipairs(self.order) do
		local p = self.players[id]
		out[#out + 1] = { id = id, score = p.deposited and p.score or 0, bonus = p.bonus, rank = p.rank,
			arrived = p.deposited, lost = p.deposited and 0 or #p.items, lost_value = p.deposited and 0 or value_of(p.items) }
	end
	table.sort(out, function(a, b) if a.score ~= b.score then return a.score > b.score end; return tostring(a.id) < tostring(b.id) end)
	for i, r in ipairs(out) do r.place = i end
	return true, out
end

return Rules
