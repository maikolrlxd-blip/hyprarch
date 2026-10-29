-- Generador de mundo de Slime Rush v2: SEMILLA -> ISLA (relieve, costa, biomas, meta, llegada en botes,
-- volcan opcional, recursos, cofres, slimes raros). Modulo PURO: no usa la API de Roblox.
-- Nada depende del orden de pairs(); solo listas ordenadas -> resultado identico en Lua y Luau.
local Rng = script and require(script.Parent.Rng) or require("Rng")
local Noise = script and require(script.Parent.Noise) or require("Noise")

local World = {}

World.DEFAULT = {
	size = 1536,          -- studs por lado del cuadrado que contiene la isla
	cell = 12,            -- resolucion de la rejilla exportable (128 x 128)
	players = 24,
	goal_radius = 48,     -- radio de la plaza de la meta
	plaza_height = 8,
	node_count = 720,     -- nodos de recurso
	chests = { comun = 32, musgoso = 16, dorado = 16, oculto = 16 }, -- multiplos de 8: un tipo por sector
	rare_sites = 20, rare_chance = 0.12, rare_max_active = 5,
	fair_band = 0.15,     -- tolerancia de valor por sector respecto al promedio
	volcano_chance = 0.6, volcano_max_lava = 220, volcano_speed = 1.2, crater_radius = 16,
	boat_offset = 200,    -- distancia mar adentro desde donde empieza a navegar cada bote
}

World.BIOMES = { "mar", "lago", "pradera", "bosque", "desierto", "roca", "montana" }
World.LAND_BIOMES = { "lago", "pradera", "bosque", "desierto", "roca", "montana" } -- "mar" es el exterior de la isla

World.NODE_TYPES = {
	{ kind = "baya", value = 1, min_dist = 9, w = { bosque = 2.0, pradera = 1.6, desierto = 0.2, roca = 0.3, montana = 0.1, lago = 0, mar = 0 } },
	{ kind = "cristal", value = 3, min_dist = 14, w = { bosque = 0.8, pradera = 1.0, desierto = 0.7, roca = 1.5, montana = 1.2, lago = 0, mar = 0 } },
	{ kind = "mineral", value = 5, min_dist = 20, w = { bosque = 0.1, pradera = 0.2, desierto = 1.2, roca = 2.0, montana = 2.0, lago = 0, mar = 0 } },
}
World.ACCESORIOS = { "Sombrero de hongo", "Alitas de nube", "Corona de musgo", "Gafas de sol", "Antenas de luz", "Capa dorada", "Cola de estrella", "Bufanda de nieve" }
World.RARE_SLIMES = {
	{ name = "Slime Dorado", value = 250, w = 0.40 }, { name = "Slime Cristal", value = 180, w = 0.35 },
	{ name = "Slime Sombra", value = 300, w = 0.20 }, { name = "Slime Arcoiris", value = 400, w = 0.05 },
}

local function clamp(v, a, b) if v < a then return a elseif v > b then return b end return v end
local function smooth(t) return t * t * (3 - 2 * t) end
local function merge(base, over)
	local out = {}
	for k, v in pairs(base) do out[k] = v end
	if over then for k, v in pairs(over) do out[k] = v end end
	return out
end
local function dist2(ax, az, bx, bz) return math.sqrt((ax - bx) ^ 2 + (az - bz) ^ 2) end

-- Octante (1..8) respecto al centro; sin trigonometria (todos de 45 grados).
function World.sector(dx, dz)
	local ax, az = math.abs(dx), math.abs(dz)
	if dx >= 0 and dz >= 0 then return ax >= az and 1 or 2
	elseif dx < 0 and dz >= 0 then return az >= ax and 3 or 4
	elseif dx < 0 and dz < 0 then return ax >= az and 5 or 6
	else return az >= ax and 7 or 8 end
end

-- Sector (1..8) de un punto visto desde el muelle: abanico de 22.5 grados que mira tierra adentro (sin trigonometria).
-- u = hacia adentro, v = lateral; lo que queda detras de la meta se asigna al sector extremo.
function World.sectorOf(world, x, z)
	local g, d = world.goal, world.dock
	local dx, dz = x - g.x, z - g.z
	local u, v = dx * d.inward.x + dz * d.inward.z, dx * -d.inward.z + dz * d.inward.x
	if u <= 0 then return v < 0 and 1 or 8 end
	local t = v / u
	if t < -2.4142 then return 1 elseif t < -1 then return 2 elseif t < -0.4142 then return 3 elseif t < 0 then return 4
	elseif t < 0.4142 then return 5 elseif t < 1 then return 6 elseif t < 2.4142 then return 7 else return 8 end
end

function World.generate(seed, over)
	local cfg = merge(World.DEFAULT, over)
	local base = Rng.new(seed)
	local sElev, sTemp, sHum, sCoast = base:int(1, 60000), base:int(1, 60000), base:int(1, 60000), base:int(1, 60000)
	local size, cx = cfg.size, cfg.size / 2
	local world = { seed = seed, cfg = cfg, size = size, goal = { x = cx, z = cx, y = cfg.plaza_height, radius = cfg.goal_radius } }

	-- Mascara de isla: 1 en el interior, 0 en el mar; la costa es irregular (ruido) pero casi circular.
	local function island(x, z)
		local nx, nz = x / size, z / size
		local dn = math.sqrt((nx - 0.5) ^ 2 + (nz - 0.5) ^ 2) * 2
		local coastR = 0.80 + (Noise.fbm(nx * 2.3, nz * 2.3, sCoast, 3, 2, 0.5) - 0.5) * 0.16
		return smooth(clamp((coastR - dn) / 0.20, 0, 1)), dn, coastR
	end
	-- MUELLE = META: un solo punto de desembarco en la costa (angulo por semilla). La meta es la plaza justo tierra adentro
	-- del muelle; el recorrido va desde la orilla (m ~ 0.52) hasta el mar (m ~ 0.30) y la plaza donde m >= 0.74.
	do
		local ad = base:fork("dock"):range(0, 6.283185307)
		local ux, uz = math.cos(ad), math.sin(ad)
		local rSea, rShore, rGoal
		for r = size * 0.5, size * 0.05, -2 do
			local m = island(cx + ux * r, cx + uz * r)
			if not rSea and m >= 0.12 then rSea = r end
			if not rShore and m >= 0.52 then rShore = r end
			if m >= 0.74 then rGoal = r; break end
		end
		rShore = rShore or size * 0.40; rSea = rSea or rShore + 60
		rGoal = math.max(size * 0.08, rShore - cfg.goal_radius * 1.8) -- la plaza queda tierra adentro, con margen de playa
		world.goal.x, world.goal.z = cx + ux * rGoal, cx + uz * rGoal
		world.dock = { x = cx + ux * rShore, z = cx + uz * rShore, angle = ad, out = { x = ux, z = uz }, inward = { x = -ux, z = -uz },
			sea = { x = cx + ux * rSea, z = cx + uz * rSea } }
	end
	local function height(x, z)
		local nx, nz = x / size, z / size
		local e = Noise.fbm(nx * 3.2, nz * 3.2, sElev, 5, 2, 0.5)
		local h = (e - 0.5) * 190 + 40
		local m = island(x, z)
		h = math.min(h, 7 + 100 * smooth(clamp((m - 0.30) / 0.70, 0, 1))) -- franja costera baja (sin montanas en la costa)
		h = -25 + (h + 25) * m -- hacia la costa baja hasta el fondo del mar
		-- playa: franja costera que NUNCA queda anegada, para que todos los botes tengan donde desembarcar
		local beach = 4.5 * smooth(clamp((m - 0.46) / 0.06, 0, 1)) * (1 - smooth(clamp((m - 0.80) / 0.15, 0, 1)))
		if beach > 0 then h = math.max(h, beach) end
		local dc = dist2(x, z, world.goal.x, world.goal.z)
		local r1, r2 = cfg.goal_radius, cfg.goal_radius * 2.6
		local w = 1 - smooth(clamp((dc - r1) / (r2 - r1), 0, 1)) -- plaza plana alrededor de la meta
		return h * (1 - w) + cfg.plaza_height * w
	end
	local function biome(x, z, h)
		h = h or height(x, z)
		if h < 1 then
			local m = island(x, z)
			return m < 0.45 and "mar" or "lago"
		end
		if h > 70 then return "montana" end
		if h > 44 then return "roca" end
		local nx, nz = x / size, z / size
		local t = Noise.fbm(nx * 2.1, nz * 2.1, sTemp, 3, 2, 0.5)
		local hu = Noise.fbm(nx * 2.6, nz * 2.6, sHum, 3, 2, 0.5)
		if t > 0.5 and hu < 0.5 then return "desierto" end
		if hu >= 0.5 then return "bosque" end
		return "pradera"
	end
	world.height, world.biome, world.island = height, biome, island
	local function walkable(x, z)
		if x < 16 or z < 16 or x > size - 16 or z > size - 16 then return false end
		local h = height(x, z)
		if h < 2.5 or h > 62 then return false end
		local b = biome(x, z, h)
		return b ~= "lago" and b ~= "mar"
	end
	local function farFromGoal(x, z, k) return dist2(x, z, world.goal.x, world.goal.z) > cfg.goal_radius * (k or 1.6) end
	world.walkable = walkable
	do -- el extremo del muelle: primer punto de agua mar adentro desde la orilla (ahora que hay walkable)
		local d = world.dock
		local r0 = dist2(d.x, d.z, cx, cx)
		for r = r0, size * 0.7, 4 do
			local x, z = cx + d.out.x * r, cx + d.out.z * r
			if not walkable(x, z) then d.sea = { x = cx + d.out.x * (r + 12), z = cx + d.out.z * (r + 12) }; break end
		end
	end

	-- Apariciones: TODOS desembarcan en el mismo muelle y se reunen en la meta (anillo dentro de la plaza). Los botes
	-- esperan mar adentro frente al muelle, en dos filas, para la escena de llegada.
	world.spawns = {}
	local d = world.dock
	local lat = { x = -d.out.z, z = d.out.x }
	for i = 1, cfg.players do
		local a = (i - 1) * 6.283185307 / cfg.players
		local sx, sz = world.goal.x + math.cos(a) * cfg.goal_radius * 0.55, world.goal.z + math.sin(a) * cfg.goal_radius * 0.55
		local row, col = (i - 1) // 12, (i - 1) % 12
		local off, lt = cfg.boat_offset + row * 24, (col - 5.5) * 18
		world.spawns[i] = { x = sx, z = sz, y = cfg.plaza_height,
			boat = { x = d.sea.x + d.out.x * off + lat.x * lt, z = d.sea.z + d.out.z * off + lat.z * lt } }
	end

	-- Volcan (opcional): en roca/montana alta, lejos de la meta y de la costa; el cráter se talla en el terreno.
	local rv = base:fork("volcano")
	world.volcano = nil
	if rv:chance(cfg.volcano_chance) then
		for _ = 1, 600 do
			local x, z = rv:range(0.12 * size, 0.88 * size), rv:range(0.12 * size, 0.88 * size)
			local h = height(x, z)
			local b = biome(x, z, h)
			local d = dist2(x, z, world.goal.x, world.goal.z)
			if (b == "roca" or b == "montana") and h >= 44 and h <= 90 and d >= size * 0.22 and island(x, z) > 0.8 then
				local cap = math.min(cfg.volcano_max_lava, d - cfg.goal_radius * 1.5 - cfg.crater_radius - 40) -- la lava NUNCA llega a la meta
				if cap > 60 then
					world.volcano = { x = x, z = z, y = h, crater_radius = cfg.crater_radius, max_lava = cap, speed = cfg.volcano_speed }
					break
				end
			end
		end
	end
	local function clearOfVolcano(x, z) return not world.volcano or dist2(x, z, world.volcano.x, world.volcano.z) > 50 end

	-- Recursos: lanzamiento de dardos con distancia minima por tipo.
	local rn = base:fork("nodes")
	world.nodes = {}
	local function try_node(rng, forced_kind)
		for _ = 1, 40 do
			local x, z = rng:range(24, size - 24), rng:range(24, size - 24)
			if walkable(x, z) and farFromGoal(x, z, 1.5) and clearOfVolcano(x, z) then
				local b = biome(x, z)
				local pick, total = nil, 0
				for _, t in ipairs(World.NODE_TYPES) do
					if not forced_kind or t.kind == forced_kind then total = total + t.w[b] end
				end
				if total > 0 then
					local roll = rng:next() * total
					for _, t in ipairs(World.NODE_TYPES) do
						if not forced_kind or t.kind == forced_kind then
							roll = roll - t.w[b]
							if roll <= 0 and t.w[b] > 0 then pick = t; break end
						end
					end
					if pick then
						local ok = true
						for _, n in ipairs(world.nodes) do
							if n.kind == pick.kind and dist2(x, z, n.x, n.z) < pick.min_dist then ok = false; break end
						end
						if ok then
							local nd = { id = #world.nodes + 1, kind = pick.kind, value = pick.value, x = x, z = z, y = height(x, z), biome = b }
							world.nodes[#world.nodes + 1] = nd
							return nd
						end
					end
				end
			end
		end
	end
	for _ = 1, cfg.node_count do try_node(rn) end

	-- Punto al azar dentro del abanico del sector s (polares alrededor de la meta): theta en [-90+22.5(s-1), +22.5] grados.
	local function inSector(rng, sct)
		local th, rr2 = math.rad(-90 + 22.5 * (sct - 1) + rng:next() * 22.5), rng:range(60, size * 0.9)
		local d, g = world.dock, world.goal
		return g.x + rr2 * (d.inward.x * math.cos(th) + -d.inward.z * math.sin(th)),
			g.z + rr2 * (d.inward.z * math.cos(th) + d.inward.x * math.sin(th))
	end

	-- Cofres: comun / musgoso / dorado visibles y oculto con pista (marcador a 14-24 studs), repartidos por sectores.
	local rc = base:fork("chests")
	world.chests = {}
	local specs = {
		{ kind = "comun", n = cfg.chests.comun, biomes = { pradera = 1, bosque = 1, desierto = 1, roca = 1, montana = 0 }, items = { 2, 4 }, budget = 20, acc = 0 },
		{ kind = "musgoso", n = cfg.chests.musgoso, biomes = { bosque = 1, pradera = 1 }, items = { 3, 5 }, budget = 40, acc = 0.05 },
		{ kind = "dorado", n = cfg.chests.dorado, biomes = { roca = 1, montana = 1, desierto = 1 }, items = { 4, 6 }, budget = 140, acc = 0.35 },
		{ kind = "oculto", n = cfg.chests.oculto, biomes = { pradera = 1, bosque = 1, desierto = 1, roca = 1, montana = 1 }, items = { 3, 5 }, budget = 90, acc = 0.15 },
	}
	for _, sp in ipairs(specs) do
		local order = rc:shuffle({ 1, 2, 3, 4, 5, 6, 7, 8 })
		for ci = 1, sp.n do
			local target = order[(ci - 1) % 8 + 1]
			for attempt = 1, 800 do
				local x, z
				if attempt < 600 then x, z = inSector(rc, target) else x, z = rc:range(24, size - 24), rc:range(24, size - 24) end
				local b = biome(x, z)
				local sep = attempt < 500 and 55 or 25
				local ok = walkable(x, z) and farFromGoal(x, z, 2.0) and clearOfVolcano(x, z) and (sp.biomes[b] or 0) > 0
				if ok and attempt < 600 then ok = World.sectorOf(world, x, z) == target end
				if ok then for _, c in ipairs(world.chests) do if dist2(x, z, c.x, c.z) < sep then ok = false; break end end end
				if ok then
					-- Presupuesto FIJO de gemas por tipo de cofre (justicia); el accesorio raro es un bono de suerte aparte.
					local n = rc:int(sp.items[1], sp.items[2])
					local ws, wsum = {}, 0
					for i = 1, n do ws[i] = 0.5 + rc:next(); wsum = wsum + ws[i] end
					local loot, total = {}, 0
					for i = 1, n do
						local v = math.max(1, math.floor(ws[i] / wsum * sp.budget + 0.5))
						loot[i] = { kind = "gema", value = v }; total = total + v
					end
					loot[1].value = loot[1].value + (sp.budget - total); total = sp.budget
					local bonus = 0
					if rc:chance(sp.acc) then
						bonus = rc:int(80, 160)
						loot[#loot + 1] = { kind = "accesorio", name = rc:pick(World.ACCESORIOS), value = bonus, rare = true, bound = true }
					end
					local ch = { id = #world.chests + 1, kind = sp.kind, x = x, z = z, y = height(x, z), biome = b, loot = loot, value = total, bonus = bonus }
					if sp.kind == "oculto" then
						local a, d = rc:range(0, 6.283185307), rc:range(14, 24)
						ch.hint = { x = x + math.cos(a) * d, z = z + math.sin(a) * d }
						ch.hint.y = height(ch.hint.x, ch.hint.z)
					end
					world.chests[#world.chests + 1] = ch
					break
				end
			end
		end
	end

	-- Slimes raros: sitios fijos por semilla; cada uno se activa con poca probabilidad (maximo N activos).
	local rr = base:fork("rares")
	world.rares = {}
	local prefs = { "bosque", "pradera", "desierto", "roca", "montana" }
	local active = 0
	for i = 1, cfg.rare_sites do
		local want = prefs[(i - 1) % #prefs + 1]
		for _ = 1, 400 do
			local x, z = rr:range(24, size - 24), rr:range(24, size - 24)
			if walkable(x, z) and farFromGoal(x, z, 2.5) and clearOfVolcano(x, z) and biome(x, z) == want then
				local roll, slime = rr:next(), World.RARE_SLIMES[1]
				for _, s in ipairs(World.RARE_SLIMES) do roll = roll - s.w; if roll <= 0 then slime = s; break end end
				local on = rr:chance(cfg.rare_chance) and active < cfg.rare_max_active
				if on then active = active + 1 end
				world.rares[#world.rares + 1] = { id = #world.rares + 1, x = x, z = z, y = height(x, z), biome = want, slime = slime.name, value = slime.value, active = on }
				break
			end
		end
	end

	-- Justicia: el valor total (nodos + cofres) por sector queda cerca del promedio. Los raros son bono de suerte.
	local rf = base:fork("fair")
	local function sector_totals()
		local tot = {}
		for s = 1, 8 do tot[s] = 0 end
		local function add(o, v) local s = World.sectorOf(world, o.x, o.z); tot[s] = tot[s] + v end
		for _, n in ipairs(world.nodes) do if not n.removed then add(n, n.value) end end
		for _, c in ipairs(world.chests) do add(c, c.value) end
		return tot
	end
	for _ = 1, 600 do
		local tot, sum = sector_totals(), 0
		for s = 1, 8 do sum = sum + tot[s] end
		local mean, changed = sum / 8, false
		for s = 1, 8 do
			if tot[s] > mean * (1 + cfg.fair_band) then
				local worst
				for _, n in ipairs(world.nodes) do
					if not n.removed and World.sectorOf(world, n.x, n.z) == s and (not worst or n.value < worst.value) then worst = n end
				end
				if worst then worst.removed = true; changed = true end
			elseif tot[s] < mean * (1 - cfg.fair_band) then
				for _ = 1, 400 do
					local x, z = inSector(rf, s)
					if World.sectorOf(world, x, z) == s and walkable(x, z) and farFromGoal(x, z, 1.5) and clearOfVolcano(x, z) then
						world.nodes[#world.nodes + 1] = { id = #world.nodes + 1, kind = "cristal", value = 3, x = x, z = z, y = height(x, z), biome = biome(x, z) }
						changed = true; break
					end
				end
			end
		end
		if not changed then break end
	end
	local kept = {}
	for _, n in ipairs(world.nodes) do if not n.removed then n.id = #kept + 1; kept[#kept + 1] = n end end
	world.nodes = kept
	world.sector_totals = sector_totals()
	return world
end

-- Rejilla de alturas y biomas para construir el terreno (por trozos) en Roblox.
function World.grid(world)
	local n = math.floor(world.size / world.cfg.cell)
	local heights, biomes = {}, {}
	for iz = 1, n do
		heights[iz], biomes[iz] = {}, {}
		for ix = 1, n do
			local x, z = (ix - 0.5) * world.cfg.cell, (iz - 0.5) * world.cfg.cell
			local h = world.height(x, z)
			heights[iz][ix], biomes[iz][ix] = h, world.biome(x, z, h)
		end
	end
	return heights, biomes, n
end

-- Fraccion de cada bioma SOBRE LA ISLA (el mar no cuenta), mas cuentas utiles.
function World.stats(world)
	local count, land = {}, 0
	local _, biomes, n = World.grid(world)
	for _, b in ipairs(World.BIOMES) do count[b] = 0 end
	for iz = 1, n do for ix = 1, n do
		local b = biomes[iz][ix]
		count[b] = count[b] + 1
		if b ~= "mar" then land = land + 1 end
	end end
	local frac = {}
	for _, b in ipairs(World.LAND_BIOMES) do frac[b] = count[b] / land end
	local active = 0
	for _, r in ipairs(world.rares) do if r.active then active = active + 1 end end
	return { biome_fraction = frac, island_fraction = land / (n * n), nodes = #world.nodes, chests = #world.chests,
		rares_active = active, has_volcano = world.volcano ~= nil, sector_totals = world.sector_totals }
end

return World
