-- Combate de la Capa 1: UN puñetazo (Bongo). Modulo PURO; el servidor es la autoridad.
-- Valida alcance, cadencia y vida; al llegar a 0 llama a Rules:knockOut (derrota -> inconsciente -> saqueo).
local Combat = {}
Combat.__index = Combat

Combat.DEFAULT = {
	max_hp = 100, punch_damage = 20, punch_range = 7, -- studs
	attack_rate = 2,                                  -- golpes por segundo con 2 brazos (con 1 brazo: la mitad; Capa 4)
	knockback = 14,                                   -- empuje en studs (lo aplica el servidor)
}

local function dist(a, b) return math.sqrt((a.x - b.x) ^ 2 + (a.z - b.z) ^ 2) end

function Combat.new(rules, cfg)
	local c = {}
	for k, v in pairs(Combat.DEFAULT) do c[k] = v end
	if cfg then for k, v in pairs(cfg) do c[k] = v end end
	return setmetatable({ rules = rules, cfg = c, hp = {}, ready = {} }, Combat)
end

function Combat:addPlayer(id) self.hp[id] = self.cfg.max_hp; self.ready[id] = 0 end

function Combat:getHp(id, now)
	local r = self.rules
	if self.hp[id] and r:isDowned(id, now or 0) == false and self.hp[id] <= 0 then self.hp[id] = self.cfg.max_hp end -- al despertar vuelve la vida
	return self.hp[id]
end

-- Dano generico (puñetazo, embestida, pedazos de Miga...). Aplica reduccion de dano (Miga), llama a knockOut al llegar a 0.
-- Devuelve (true, {damage, hp, knocked_out}) o (false, motivo). No valida alcance ni cadencia: lo hace cada habilidad.
function Combat:damage(attackerId, victimId, amount, now)
	local r = self.rules
	if not self.hp[attackerId] or not self.hp[victimId] then return false, "jugador desconocido" end
	if r:isDowned(victimId, now) then return false, "ya esta inconsciente" end
	local vp = r.players[victimId]
	if vp and now < vp.immune_until then return false, "inmune" end
	local red = self.reduction and self.reduction[victimId]
	if red and now < red.until_t then amount = math.floor(amount * (1 - red.pct) + 0.5) end
	self:getHp(victimId, now)
	self.hp[victimId] = math.max(0, self.hp[victimId] - amount)
	local ko = false
	if self.hp[victimId] <= 0 then
		ko = r:knockOut(attackerId, victimId, now)
		if not ko then self.hp[victimId] = 1 end -- no se pudo derrotar (fase/inmunidad): no queda a 0
	end
	return true, { damage = amount, hp = self.hp[victimId], knocked_out = ko }
end

function Combat:setReduction(id, pct, until_t) self.reduction = self.reduction or {}; self.reduction[id] = { pct = pct, until_t = until_t } end
function Combat:heal(id, amount, now)
	if not self.hp[id] then return false end
	self:getHp(id, now); self.hp[id] = math.min(self.cfg.max_hp, self.hp[id] + amount); return self.hp[id]
end

-- Puñetazo de Bongo: valida cadencia y alcance y aplica dano; devuelve tambien el empuje.
function Combat:punch(attackerId, victimId, attackerPos, victimPos, now)
	local r = self.rules
	if attackerId == victimId then return false, "no puedes golpearte" end
	if not self.hp[attackerId] or not self.hp[victimId] then return false, "jugador desconocido" end
	if r:isDowned(attackerId, now) then return false, "estas inconsciente" end
	if now < self.ready[attackerId] then return false, "espera" end
	if dist(attackerPos, victimPos) > self.cfg.punch_range then return false, "muy lejos" end
	local ok, res = self:damage(attackerId, victimId, self.cfg.punch_damage, now)
	if not ok then return false, res end
	self.ready[attackerId] = now + 1 / self.cfg.attack_rate
	local dx, dz = victimPos.x - attackerPos.x, victimPos.z - attackerPos.z
	local d = math.sqrt(dx * dx + dz * dz); if d < 1e-6 then dx, dz, d = 1, 0, 1 end
	res.push = { x = dx / d * self.cfg.knockback, z = dz / d * self.cfg.knockback }
	return true, res
end

return Combat
