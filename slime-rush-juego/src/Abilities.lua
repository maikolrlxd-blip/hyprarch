-- Capa 2: habilidades de los slimes companeros (UNA por slime para la prueba). Modulo PURO.
--   Rayo (montura):  mount (monta unos segundos, mas rapido), ram (embestida: danio; se esquiva saltando), carry (lleva/lanza a un
--                    jugador INCONSCIENTE: rescate o secuestro).
--   Miga (se divide): 4 pedazos compartidos y regenerables: throwPiece (danio al mas cercano), heal (cura + reduce danio), anchor (aguante).
-- Bongo (puñetazo) vive en Combat. El servidor llama aqui con posiciones y el tiempo; todo se valida aqui.
local Abilities = {}
Abilities.__index = Abilities

Abilities.DEFAULT = {
	-- Rayo
	mount_time = 6, mount_cooldown = 20, mount_speed = 2.2,
	ram_damage = 35, ram_range = 8, ram_cooldown = 3,
	carry_range = 8, carry_distance = 45, carry_cooldown = 10,
	-- Miga
	pieces = 4, piece_regen = 12,                 -- segundos por pedazo
	throw_damage = 12, throw_range = 40, throw_cooldown = 0.8,
	heal_amount = 25, reduce_pct = 0.30, reduce_time = 10,
	anchor_time = 8,                              -- inmune a empujes de tornado/tormenta (el servidor lo respeta)
	anchor_cost = 2,
}

local function dist(a, b) return math.sqrt((a.x - b.x) ^ 2 + (a.z - b.z) ^ 2) end

function Abilities.new(rules, combat, cfg)
	local c = {}
	for k, v in pairs(Abilities.DEFAULT) do c[k] = v end
	if cfg then for k, v in pairs(cfg) do c[k] = v end end
	return setmetatable({ rules = rules, combat = combat, cfg = c, p = {} }, Abilities)
end

function Abilities:addPlayer(id, slime)
	self.p[id] = { slime = slime, mounted_until = -1, mount_ready = 0, ram_ready = 0, carry_ready = 0, throw_ready = 0,
		pieces = self.cfg.pieces, regen_from = nil, anchored_until = -1 }
end

local function st(self, id, kind)
	local s = self.p[id]
	if not s then return nil, "jugador desconocido" end
	if s.slime ~= kind then return nil, "tu slime no tiene esa habilidad" end
	return s
end

-- ===== Rayo =====
function Abilities:mount(id, now)
	local s, why = st(self, id, "rayo"); if not s then return false, why end
	if self.rules:isDowned(id, now) then return false, "estas inconsciente" end
	if now < s.mount_ready then return false, "espera" end
	s.mounted_until = now + self.cfg.mount_time; s.mount_ready = now + self.cfg.mount_cooldown
	return true, { until_t = s.mounted_until }
end

function Abilities:speedMultiplier(id, now)
	local s = self.p[id]
	return (s and now < s.mounted_until) and self.cfg.mount_speed or 1
end

-- victimAirborne: el cliente/servidor indica si la victima esta en el aire (salto de Bongo); saltar esquiva la embestida.
function Abilities:ram(id, victimId, aPos, vPos, now, victimAirborne)
	local s, why = st(self, id, "rayo"); if not s then return false, why end
	if now >= s.mounted_until then return false, "no estas montado" end
	if now < s.ram_ready then return false, "espera" end
	if dist(aPos, vPos) > self.cfg.ram_range then return false, "muy lejos" end
	s.ram_ready = now + self.cfg.ram_cooldown
	if victimAirborne then return true, { dodged = true, damage = 0 } end
	local ok, res = self.combat:damage(id, victimId, self.cfg.ram_damage, now)
	if not ok then return false, res end
	res.dodged = false
	return true, res
end

-- Lleva a un jugador INCONSCIENTE (rescatar o secuestrar) en la direccion (dx,dz) unitaria hasta carry_distance.
function Abilities:carry(id, targetId, aPos, tPos, dx, dz, now)
	local s, why = st(self, id, "rayo"); if not s then return false, why end
	if now >= s.mounted_until then return false, "no estas montado" end
	if id == targetId then return false, "no puedes llevarte a ti mismo" end
	if now < s.carry_ready then return false, "espera" end
	if dist(aPos, tPos) > self.cfg.carry_range then return false, "muy lejos" end
	if not self.rules:isDowned(targetId, now) then return false, "solo puedes llevar a quien esta inconsciente" end
	local d = math.sqrt(dx * dx + dz * dz); if d < 1e-6 then return false, "sin direccion" end
	s.carry_ready = now + self.cfg.carry_cooldown
	return true, { x = tPos.x + dx / d * self.cfg.carry_distance, z = tPos.z + dz / d * self.cfg.carry_distance }
end

-- ===== Miga =====
function Abilities:pieces(id, now)
	local s = self.p[id]; if not s then return 0 end
	if s.pieces < self.cfg.pieces then
		s.regen_from = s.regen_from or now
		local gained = math.floor((now - s.regen_from) / self.cfg.piece_regen)
		if gained > 0 then
			s.pieces = math.min(self.cfg.pieces, s.pieces + gained)
			s.regen_from = s.pieces < self.cfg.pieces and (s.regen_from + gained * self.cfg.piece_regen) or nil
		end
	else s.regen_from = nil end
	return s.pieces
end

local function spend(self, s, id, n, now)
	if self:pieces(id, now) < n then return false end
	if s.pieces == self.cfg.pieces then s.regen_from = now end
	s.pieces = s.pieces - n
	return true
end

function Abilities:throwPiece(id, victimId, aPos, vPos, now)
	local s, why = st(self, id, "miga"); if not s then return false, why end
	if self.rules:isDowned(id, now) then return false, "estas inconsciente" end
	if now < s.throw_ready then return false, "espera" end
	if dist(aPos, vPos) > self.cfg.throw_range then return false, "muy lejos" end
	if self:pieces(id, now) < 1 then return false, "sin pedazos" end
	local ok, res = self.combat:damage(id, victimId, self.cfg.throw_damage, now)
	if not ok then return false, res end
	spend(self, s, id, 1, now); s.throw_ready = now + self.cfg.throw_cooldown
	res.pieces = s.pieces
	return true, res
end

-- Cierra heridas: cura y reduce el danio recibido un tiempo. Cuesta 1 pedazo.
function Abilities:heal(id, now)
	local s, why = st(self, id, "miga"); if not s then return false, why end
	if self.rules:isDowned(id, now) then return false, "estas inconsciente" end
	if not spend(self, s, id, 1, now) then return false, "sin pedazos" end
	local hp = self.combat:heal(id, self.cfg.heal_amount, now)
	self.combat:setReduction(id, self.cfg.reduce_pct, now + self.cfg.reduce_time)
	return true, { hp = hp, pieces = s.pieces }
end

function Abilities:anchor(id, now)
	local s, why = st(self, id, "miga"); if not s then return false, why end
	if not spend(self, s, id, self.cfg.anchor_cost, now) then return false, "sin pedazos" end
	s.anchored_until = now + self.cfg.anchor_time
	return true, { until_t = s.anchored_until, pieces = s.pieces }
end
function Abilities:isAnchored(id, now) local s = self.p[id]; return s ~= nil and now < s.anchored_until end

return Abilities
