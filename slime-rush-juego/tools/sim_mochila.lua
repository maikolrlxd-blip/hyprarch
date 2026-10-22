-- Simulacion de economia: 24 bots avaros compitiendo por recursos (velocidad 16 studs/s) para elegir tamano de mochila y tiempos.
-- Uso: python3 tools/sim_mochila.py
local World = require("World")
local function d(a, b) return math.sqrt((a.x - b.x) ^ 2 + (a.z - b.z) ^ 2) end
local function sim(seed, backpack, explore)
	local w = World.generate(seed)
	local items = {}
	for _, nd in ipairs(w.nodes) do items[#items + 1] = { x = nd.x, z = nd.z, v = nd.value, slots = 1 } end
	for _, c in ipairs(w.chests) do items[#items + 1] = { x = c.x, z = c.z, v = c.value, slots = #c.loot } end
	local bots = {}
	for i = 1, 24 do bots[i] = { pos = { x = w.goal.x + math.cos(i) * 20, z = w.goal.z + math.sin(i) * 20 }, t = 0, used = 0, v = 0, full_at = nil, n = 0 } end
	local taken = {}
	local active = true
	while active do
		active = false
		local pick, pt = nil, 1e9
		for i, b in ipairs(bots) do if not b.done and b.t < pt then pick, pt = i, b.t end end
		if not pick then break end
		local b = bots[pick]; active = true
		local best, bs
		for k, it in ipairs(items) do
			if not taken[k] and b.used + it.slots <= backpack then
				local sc = it.v / (d(b.pos, it) / 16 + 2); if not bs or sc > bs then best, bs = k, sc end
			end
		end
		if not best then b.done = true; b.full_at = b.full_at or b.t
		else
			local it = items[best]; local arrive = b.t + d(b.pos, it) / 16 + 1.2
			if arrive > explore then b.done = true
			else
				taken[best] = pick; b.t = arrive; b.pos = { x = it.x, z = it.z }; b.used = b.used + it.slots; b.v = b.v + it.v; b.n = b.n + 1
				if b.used >= backpack then b.done = true; b.full_at = b.t end
			end
		end
	end
	local full, tt, vs = 0, 0, {}
	for _, b in ipairs(bots) do if b.full_at and b.used >= backpack - 1 then full = full + 1; tt = tt + b.full_at end; vs[#vs + 1] = b.v end
	table.sort(vs)
	local left = 0; for k = 1, #items do if not taken[k] then left = left + items[k].v end end
	return full, full > 0 and tt / full or 0, vs[1], vs[#vs], vs[12], left
end
local out = {}
for _, bp in ipairs({ 12, 20, 30, 40 }) do
	local F, T, lo, hi, med, left = 0, 0, 0, 0, 0, 0
	for _, seed in ipairs({ 1, 2, 3, 4, 5 }) do
		local f, t, a, b, m, l = sim(seed, bp, 360); F = F + f; T = T + t; lo = lo + a; hi = hi + b; med = med + m; left = left + l
	end
	out[#out + 1] = string.format("mochila %2d: llenan %4.1f/24 bots en %3.0fs de media | valor peor %3.0f mediana %3.0f mejor %3.0f | sobra en mapa %4.0f",
		bp, F / 5, T / 5, lo / 5, med / 5, hi / 5, left / 5)
end
return table.concat(out, "\n")
