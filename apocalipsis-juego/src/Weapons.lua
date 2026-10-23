-- Armas del roguelike zombi: estadisticas, cadencia, cargador, recarga, dispersion y dano. Modulo PURO (sin API de Roblox).
-- El servidor es la autoridad: llama aqui con el tiempo actual y aplica el resultado. Valores PROVISIONALES para ajustar jugando.
local Rng = script and require(script.Parent.Rng) or require("Rng")

local Weapons = {}
Weapons.__index = Weapons

-- Tiempos de animacion (segundos) = los de los clips de Blender (Equipar, Disparo, Recargar...). Inspeccionar: duraciones reales de los clips (pistola 3,3 s; escopeta y subfusil 3,0 s).
Weapons.DEFS = {
	pistola = {
		name = "Pistola 9mm", mode = "semi", pellets = 1, damage = 25, headshot = 2.0, rate = 4.5,   -- tiros/s (limite de cadencia)
		mag = 15, reserve = 90, reload = 1.7, equip = 0.8, inspect = 3.3,
		range = 140, falloff_start = 60, falloff_min = 0.6, spread = 0.8, spread_move = 1.5, recoil = 1.2,
		sound = { fire = "pistola_disparo", reload = "pistola_recarga", empty = "clic_vacio", equip = "pistola_equipar" },
	},
	escopeta = {
		name = "Escopeta", mode = "semi", pellets = 8, damage = 12, headshot = 1.5, rate = 1.1,
		mag = 6, reserve = 36, reload_shell = 0.55, reload_start = 0.5, reload_end = 0.4, pump = 0.45, equip = 1.0, inspect = 3.0,
		range = 60, falloff_start = 12, falloff_min = 0.15, spread = 5.5, spread_move = 7.0, recoil = 4.0,
		sound = { fire = "escopeta_disparo", pump = "escopeta_bombeo", shell = "escopeta_cartucho", empty = "clic_vacio", equip = "escopeta_equipar" },
	},
	subfusil = {
		name = "Subfusil", mode = "auto", pellets = 1, damage = 14, headshot = 1.8, rate = 12,
		mag = 30, reserve = 150, reload = 1.95, equip = 0.9, inspect = 3.0,
		range = 110, falloff_start = 45, falloff_min = 0.5, spread = 1.6, spread_move = 3.0, spread_burst = 0.12, recoil = 0.9,
		sound = { fire = "subfusil_disparo", reload = "subfusil_recarga", empty = "clic_vacio", equip = "subfusil_equipar" },
	},
}

function Weapons.new(id, seed, overrides)
	local def = {}
	for k, v in pairs(Weapons.DEFS[id]) do def[k] = v end
	if overrides then for k, v in pairs(overrides) do def[k] = v end end
	return setmetatable({ id = id, def = def, ammo = def.mag, reserve = def.reserve, ready = 0, reloading = nil, burst = 0, last_shot = -1e9,
		rng = Rng.new(seed or 1) }, Weapons)
end

-- Multiplicador de dano por distancia: pleno hasta falloff_start y baja linealmente hasta falloff_min en range; mas alla: 0.
function Weapons.falloff(def, dist)
	if dist > def.range then return 0 end
	if dist <= def.falloff_start then return 1 end
	local t = (dist - def.falloff_start) / (def.range - def.falloff_start)
	return 1 - t * (1 - def.falloff_min)
end

function Weapons:equip(now) self.ready = now + self.def.equip; self.reloading = nil; return self.def.equip end

-- Estado de recarga por pasos (escopeta: inicio -> un cartucho a la vez -> fin; el resto: un solo paso)
function Weapons:isReloading(now) return self.reloading ~= nil end

function Weapons:reload(now)
	local d = self.def
	if self.reloading then return false, "ya recargando" end
	if self.ammo >= d.mag then return false, "cargador lleno" end
	if self.reserve <= 0 then return false, "sin municion de reserva" end
	if now < self.ready then return false, "ocupada" end
	if d.reload_shell then
		self.reloading = { kind = "shell", next = now + d.reload_start }
		self.ready = now + d.reload_start
		return true, { clip = "Recargar_Inicio", duration = d.reload_start }
	end
	self.reloading = { kind = "mag", done = now + d.reload }
	self.ready = now + d.reload
	return true, { clip = "Recargar", duration = d.reload }
end

-- Avanza la recarga hasta 'now'. Devuelve true si termino.
function Weapons:update(now)
	local r, d = self.reloading, self.def
	if not r then return false end
	if r.kind == "mag" then
		if now >= r.done then
			local take = math.min(d.mag - self.ammo, self.reserve)
			self.ammo = self.ammo + take; self.reserve = self.reserve - take; self.reloading = nil
			return true
		end
		return false
	end
	-- escopeta: cartucho por cartucho
	while r.next and now >= r.next do
		if self.ammo >= d.mag or self.reserve <= 0 then
			self.reloading = nil; self.ready = math.max(self.ready, r.next + d.reload_end); return true
		end
		self.ammo = self.ammo + 1; self.reserve = self.reserve - 1
		r.next = r.next + d.reload_shell; self.ready = r.next
	end
	return false
end

-- Disparar: valida cadencia, municion y recarga (la escopeta puede interrumpir la recarga disparando).
-- Devuelve (true, {pellets = {{dir_yaw, dir_pitch, mult}...}, clip, sound, recoil}) o (false, motivo).
-- moving: el jugador se mueve (mas dispersion); dist se usa en 'damage' al impactar, no aqui.
function Weapons:fire(now, moving)
	local d = self.def
	self:update(now)
	if self.reloading then
		if self.reloading.kind == "shell" and self.ammo > 0 then self.reloading = nil; self.ready = now -- interrumpir recarga por cartuchos
		else return false, "recargando" end
	end
	if now < self.ready then return false, "no lista" end
	if self.ammo <= 0 then self.ready = now + 0.25; return false, "sin municion", d.sound.empty end
	self.ammo = self.ammo - 1
	local cooldown = 1 / d.rate
	if d.pump then cooldown = math.max(cooldown, d.pump + 0.1) end
	self.ready = now + cooldown
	-- la dispersion del subfusil crece en rafagas largas
	if now - self.last_shot > 0.4 then self.burst = 0 end
	self.burst = self.burst + 1; self.last_shot = now
	local spread = (moving and d.spread_move or d.spread) + (d.spread_burst or 0) * math.min(self.burst, 20)
	local pellets = {}
	for i = 1, d.pellets do
		local a, r = self.rng:range(0, 6.283185307), self.rng:next() ^ 0.5 * spread -- uniforme en un disco (grados)
		pellets[i] = { yaw = math.cos(a) * r, pitch = math.sin(a) * r }
	end
	return true, { pellets = pellets, clip = "Disparo", sound = d.sound.fire, recoil = d.recoil, ammo = self.ammo,
		pump_clip = d.pump and "Bombear" or nil }
end

-- Dano de UN perdigon/bala: base * distancia * (cabeza ? mult : 1)
function Weapons:damage(dist, headshot)
	local d = self.def
	local m = Weapons.falloff(d, dist)
	if headshot then m = m * d.headshot end
	return d.damage * m
end

function Weapons:inspect(now)
	if self.reloading or now < self.ready then return false, "ocupada" end
	self.ready = now + 0.1
	return true, { clip = "Inspeccionar", duration = self.def.inspect }
end

-- Tiempo para matar a un zombi de 'hp' disparando a cuerpo a cuerpo (sin fallar, sin recargar) a distancia 'dist'.
function Weapons.ttk(id, hp, dist, headshot)
	local d = Weapons.DEFS[id]
	local per_shot = d.damage * d.pellets * Weapons.falloff(d, dist) * (headshot and d.headshot or 1)
	local shots = math.ceil(hp / per_shot)
	local cd = 1 / d.rate; if d.pump then cd = math.max(cd, d.pump + 0.1) end
	return (shots - 1) * cd, shots
end

return Weapons
