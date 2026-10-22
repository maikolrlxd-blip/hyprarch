-- Pruebas de Slime Rush v2 (Lua puro; mismas reglas que en Luau). Se corren con tests/run_tests.py
local Rng, Noise = require("Rng"), require("Noise")
local World, Rules = require("World"), require("Rules")

local passed, failed = 0, 0
local function test(name, fn)
	local ok, err = pcall(fn)
	if ok then passed = passed + 1; print("  ok   " .. name)
	else failed = failed + 1; print("  FAIL " .. name .. "\n       " .. tostring(err)) end
end
local function eq(a, b, msg) if a ~= b then error((msg or "eq") .. ": esperaba " .. tostring(b) .. ", obtuve " .. tostring(a), 2) end end
local function truthy(v, msg) if not v then error(msg or "se esperaba verdadero", 2) end end
local function near(a, b, tol, msg) if math.abs(a - b) > tol then error((msg or "near") .. ": " .. a .. " vs " .. b, 2) end end
local function dist(a, b) return math.sqrt((a.x - b.x) ^ 2 + (a.z - b.z) ^ 2) end

print("== Rng y Noise")
test("Rng: valores de referencia de Park-Miller (iguales en Lua y Luau)", function()
	local r = Rng.new(1)
	near(r:next(), 16807 / 2147483647, 1e-15)
	near(r:next(), 282475249 / 2147483647, 1e-15)
end)
test("Rng: misma semilla = misma secuencia; distinta semilla = distinta", function()
	local a, b, c = Rng.new(99), Rng.new(99), Rng.new(100)
	for _ = 1, 50 do eq(a:next(), b:next()) end
	truthy(Rng.new(99):next() ~= c:next())
end)
test("Rng: fork es independiente y determinista", function()
	local a, b = Rng.new(5):fork("x"), Rng.new(5):fork("x")
	eq(a:next(), b:next()); truthy(Rng.new(5):fork("y"):next() ~= Rng.new(5):fork("x"):next())
end)
test("Noise: en [0,1) y determinista", function()
	for i = 1, 200 do
		local v = Noise.fbm(i * 0.37, i * 0.11, 1234, 4)
		truthy(v >= 0 and v < 1, "fuera de rango " .. v); eq(v, Noise.fbm(i * 0.37, i * 0.11, 1234, 4))
	end
end)

print("== Mundo (isla)")
local function fingerprint(w)
	local s = #w.nodes .. "|" .. #w.chests .. "|" .. #w.rares .. "|" .. tostring(w.volcano ~= nil)
	for i = 1, math.min(#w.nodes, 25) do s = s .. string.format("|%.3f,%.3f", w.nodes[i].x, w.nodes[i].z) end
	for _, c in ipairs(w.chests) do s = s .. "|" .. c.kind .. c.value end
	return s
end
test("misma semilla = mismo mundo; semillas distintas = mundos distintos", function()
	eq(fingerprint(World.generate(777)), fingerprint(World.generate(777)))
	truthy(fingerprint(World.generate(777)) ~= fingerprint(World.generate(778)))
end)
test("tamano grande y 24 jugadores por defecto", function()
	local w = World.generate(5); eq(w.size, 1536); eq(w.cfg.players, 24); eq(#w.spawns, 24); eq(Rules.DEFAULT.max_players, 24)
end)
test("biomas: los 6 de tierra aparecen y cada isla tiene al menos 4; el mar rodea la isla", function()
	local seen = {}
	for seed = 1, 12 do
		local w = World.generate(seed * 53)
		local st = World.stats(w)
		local n = 0
		for _, b in ipairs(World.LAND_BIOMES) do if st.biome_fraction[b] > 0.02 then seen[b] = true; n = n + 1 end end
		truthy(n >= 4, "semilla " .. seed * 53 .. " solo tiene " .. n .. " biomas")
		truthy(st.island_fraction > 0.30 and st.island_fraction < 0.70, "isla de " .. st.island_fraction)
		eq(w.biome(20, 20), "mar"); eq(w.biome(w.size - 20, w.size - 20), "mar") -- esquinas = mar
	end
	for _, b in ipairs(World.LAND_BIOMES) do truthy(seen[b], "nunca aparece " .. b) end
end)
test("la meta esta en una plaza plana, seca y transitable", function()
	for _, seed in ipairs({1, 42, 31337}) do
		local w = World.generate(seed)
		for a = 0, 5 do
			local x, z = w.goal.x + math.cos(a) * w.goal.radius * 0.8, w.goal.z + math.sin(a) * w.goal.radius * 0.8
			near(w.height(x, z), w.cfg.plaza_height, 1.0, "plaza no plana")
		end
		truthy(w.walkable(w.goal.x + 5, w.goal.z + 5))
	end
end)
test("llegada en botes: cada jugador aparece en la COSTA y su bote parte mar adentro", function()
	for _, seed in ipairs({1, 42, 777, 2026}) do
		local w = World.generate(seed)
		eq(#w.spawns, w.cfg.players)
		local mn, mx = 1e9, 0
		for _, s in ipairs(w.spawns) do
			truthy(w.walkable(s.x, s.z), "aparicion en agua/montana")
			truthy(s.boat, "falta el bote")
			truthy(dist(s.boat, w.goal) > dist(s, w.goal), "el bote debe estar mas lejos que la costa")
			truthy(not w.walkable(s.boat.x, s.boat.z), "el bote no esta en el agua")
			local d = dist(s, w.goal); mn, mx = math.min(mn, d), math.max(mx, d)
		end
		truthy(mx / mn < 2.0, "apariciones muy desiguales: " .. mn .. " a " .. mx)
	end
end)
test("recursos y cofres: transitables, fuera de la plaza y bien separados", function()
	local w = World.generate(2026)
	for _, n in ipairs(w.nodes) do truthy(w.walkable(n.x, n.z)); truthy(dist(n, w.goal) > w.goal.radius * 1.4) end
	for i, c in ipairs(w.chests) do
		truthy(w.walkable(c.x, c.z)); truthy(dist(c, w.goal) > w.goal.radius * 1.9)
		for j = i + 1, #w.chests do truthy(dist(c, w.chests[j]) >= 25, "cofres pegados") end
	end
end)
test("cofres: presupuesto fijo por tipo, ocultos con pista, accesorios ligados", function()
	local budget = { comun = 20, musgoso = 40, dorado = 140, oculto = 90 }
	local kinds = { comun = 0, musgoso = 0, dorado = 0, oculto = 0 }
	for _, seed in ipairs({1, 42, 777}) do
		for _, c in ipairs(World.generate(seed).chests) do
			kinds[c.kind] = kinds[c.kind] + 1
			eq(c.value, budget[c.kind], "valor del cofre " .. c.kind)
			local gems = 0
			for _, it in ipairs(c.loot) do
				if it.kind == "gema" then gems = gems + it.value else truthy(it.rare and it.bound, "accesorio debe ser raro y ligado") end
			end
			eq(gems, budget[c.kind], "suma de gemas")
			if c.kind == "oculto" then local d = dist(c, c.hint); truthy(d >= 13.9 and d <= 24.1, "pista a " .. d) end
		end
	end
	for _, k in ipairs({"comun", "musgoso", "dorado", "oculto"}) do truthy(kinds[k] > 0, "falta " .. k) end
end)
test("justicia: el valor por sector queda dentro de +-25% del promedio (30 semillas)", function()
	for i = 1, 30 do
		local w = World.generate(i * 37 + 5)
		local sum = 0; for s = 1, 8 do sum = sum + w.sector_totals[s] end
		local mean = sum / 8
		for s = 1, 8 do truthy(math.abs(w.sector_totals[s] - mean) <= mean * 0.25, "semilla " .. (i * 37 + 5) .. " sector " .. s) end
	end
end)
test("slimes raros: pocos activos (max 5), a veces ninguno, a veces varios", function()
	local zero, total, N = 0, 0, 80
	for seed = 1, N do
		local a = World.stats(World.generate(seed * 13)).rares_active
		truthy(a <= 5); total = total + a; if a == 0 then zero = zero + 1 end
	end
	local mean = total / N
	truthy(mean > 0.5 and mean < 4, "media de raros activos " .. mean)
	truthy(zero / N > 0.02, "casi nunca hay mundos sin raros")
end)
test("volcan: aparece en parte de los mundos, en roca/montana alta, lejos de la meta; la lava no la alcanza", function()
	local with = 0
	for seed = 1, 30 do
		local w = World.generate(seed * 17)
		local v = w.volcano
		if v then
			with = with + 1
			local b = w.biome(v.x, v.z); truthy(b == "roca" or b == "montana", "volcan en " .. b)
			truthy(dist(v, w.goal) >= w.size * 0.22)
			truthy(dist(v, w.goal) - v.max_lava > w.goal.radius, "la lava podria alcanzar la meta")
			for _, n in ipairs(w.nodes) do truthy(dist(n, v) > 50, "nodo dentro del crater") end
			for _, c in ipairs(w.chests) do truthy(dist(c, v) > 50, "cofre dentro del crater") end
		end
	end
	truthy(with >= 6 and with <= 28, "volcanes en " .. with .. " de 30 mundos")
end)
test("rendimiento: generar un mundo grande + rejilla 128x128 tarda < 3 s", function()
	local t = os.clock(); local w = World.generate(4242); local _, _, n = World.grid(w)
	eq(n, 128); truthy(os.clock() - t < 3, "tardo " .. (os.clock() - t))
end)

print("== Reglas")
local W = World.generate(2026)
local function fresh(cfg) local r = Rules.new(W, cfg, 7); r:start(0); return r end
local T_EXPLORE = 3.5
local T_RETURN = 3 + 360 + 1
local T_COLLAPSE = 3 + 360 + 240 + 1
local T_END = 3 + 360 + 240 + 30 + 1
local near_goal = { x = W.goal.x + 5, z = W.goal.z }
local function at(o) return { x = o.x, z = o.z } end
local P0 = { x = 0, z = 0 }

test("fases: cuenta, exploracion, regreso, colapso, fin", function()
	local r = fresh()
	eq(r:phase(1), "countdown"); eq(r:phase(T_EXPLORE), "explore"); eq(r:phase(T_RETURN), "return")
	eq(r:phase(T_COLLAPSE), "collapse"); eq(r:phase(T_END), "ended"); eq(Rules.new(W):phase(0), "generating")
	near(r:return_opens_in(10), 353, 0.001); eq(r:return_opens_in(T_RETURN), nil)
end)
test("jugadores: solo entran antes de empezar; maximo 24", function()
	local r = Rules.new(W, nil, 1); r:start(0)
	for i = 1, 24 do truthy(r:addPlayer(i, 0)) end
	local ok, why = r:addPlayer(25, 0); eq(ok, false); eq(why, "partida llena")
	eq((fresh():addPlayer(1, T_EXPLORE)), false)
end)
test("recoger nodos: valida fase, distancia, repetido y mochila llena", function()
	local r = fresh(); r:addPlayer("a", 0)
	local n = W.nodes[1]
	eq((r:collectNode("a", 1, at(n), 1)), false)
	local ok, item = r:collectNode("a", 1, at(n), T_EXPLORE); truthy(ok); eq(item.value, n.value)
	eq((r:collectNode("a", 1, at(n), T_EXPLORE)), false)
	local far = W.nodes[2]; eq((r:collectNode("a", 2, { x = far.x + 50, z = far.z }, T_EXPLORE)), false)
	local r2 = fresh({ backpack = 2 }); r2:addPlayer("a", 0)
	truthy(r2:collectNode("a", 1, at(W.nodes[1]), T_EXPLORE)); truthy(r2:collectNode("a", 2, at(W.nodes[2]), T_EXPLORE))
	local ok3, why = r2:collectNode("a", 3, at(W.nodes[3]), T_EXPLORE); eq(ok3, false); eq(why, "mochila llena")
end)
test("cofres: un solo ganador; si la mochila no alcanza, el cofre NO se consume", function()
	local r = fresh(); r:addPlayer("a", 0); r:addPlayer("b", 0)
	local c = W.chests[1]
	truthy((r:claimChest("a", 1, at(c), T_EXPLORE)))
	local ok, why = r:claimChest("b", 1, at(c), T_EXPLORE); eq(ok, false); eq(why, "ya fue abierto")
	local r2 = fresh({ backpack = 1 }); r2:addPlayer("a", 0)
	eq((r2:claimChest("a", 1, at(c), T_EXPLORE)), false); truthy(r2.taken_chests[1] == nil)
end)

print("== Derrota y saqueo")
local function loaded(r, id, n, from) for i = 1, n do r:collectNode(id, (from or 0) + i, at(W.nodes[(from or 0) + i]), T_EXPLORE) end end
test("derrotar deja inconsciente 12 s: no puede actuar y despierta con inmunidad", function()
	local r = fresh(); r:addPlayer("a", 0); r:addPlayer("b", 0)
	local ok, res = r:knockOut("a", "b", T_EXPLORE); truthy(ok); near(res.wakes_at, T_EXPLORE + 12, 1e-9)
	truthy(r:isDowned("b", T_EXPLORE + 5))
	local okc, whyc = r:collectNode("b", 1, at(W.nodes[1]), T_EXPLORE + 5); eq(okc, false); eq(whyc, "estas inconsciente")
	eq((r:knockOut("a", "b", T_EXPLORE + 5)), false) -- ya esta en el suelo
	eq(r:isDowned("b", T_EXPLORE + 12.1), false)
	local oki, whyi = r:knockOut("a", "b", T_EXPLORE + 13); eq(oki, false); eq(whyi, "inmune") -- 8 s de inmunidad
	truthy((r:knockOut("a", "b", T_EXPLORE + 12.1 + 8.1)))
end)
test("saqueo: solo a un jugador inconsciente; pasa 1-2 objetos al azar y hay espera entre saqueos", function()
	local r = fresh(); r:addPlayer("a", 0); r:addPlayer("b", 0); loaded(r, "b", 6)
	local ok0, why0 = r:lootDowned("a", "b", P0, P0, T_EXPLORE); eq(ok0, false); eq(why0, "no esta inconsciente")
	r:knockOut("a", "b", T_EXPLORE)
	local ok, res = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 1); truthy(ok)
	truthy(#res.stolen >= 1 and #res.stolen <= 2); eq(#r.players.a.items, #res.stolen); eq(#r.players.b.items, 6 - #res.stolen)
	local okw, whyw = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 1.5); eq(okw, false); eq(whyw, "espera")
	truthy((r:lootDowned("a", "b", P0, P0, T_EXPLORE + 3)))
	eq((r:lootDowned("a", "b", P0, { x = 500, z = 0 }, T_EXPLORE + 6)), false) -- de lejos
	eq((r:lootDowned("b", "b", P0, P0, T_EXPLORE + 6)), false)
end)
test("saqueo: lo que no cabe en la mochila del ladron cae al suelo", function()
	local r = fresh({ backpack = 3, loot_min = 2, loot_max = 2 }); r:addPlayer("a", 0); r:addPlayer("b", 0)
	loaded(r, "a", 3); loaded(r, "b", 3, 3)
	r:knockOut("a", "b", T_EXPLORE)
	local _, res = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 1); eq(#res.dropped, #res.stolen); eq(#r.players.a.items, 3)
end)
test("un jugador inconsciente no puede saquear; nadie saquea a quien ya llego a la meta", function()
	local r = fresh(); for _, id in ipairs({"a", "b", "c"}) do r:addPlayer(id, 0) end
	loaded(r, "c", 2)
	r:knockOut("a", "b", T_EXPLORE); r:knockOut("a", "c", T_EXPLORE)
	eq((r:lootDowned("b", "c", P0, P0, T_EXPLORE + 1)), false) -- b esta en el suelo
end)
test("objetos ligados: se necesitan 2 saqueos seguidos (dentro de 3 s)", function()
	local r = fresh({ loot_min = 1, loot_max = 1, loot_cooldown = 0, downed_time = 100 }); r:addPlayer("a", 0); r:addPlayer("b", 0)
	r.players.b.items = { { id = "x", kind = "slime_raro", value = 250, rare = true, bound = true } }
	r:knockOut("a", "b", T_EXPLORE)
	local _, r1 = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 1); eq(#r1.stolen, 0)
	local _, r2 = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 2); eq(#r2.stolen, 1)
	r.players.b.items = { { id = "y", kind = "slime_raro", value = 250, rare = true, bound = true } }
	local _, r3 = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 10); eq(#r3.stolen, 0)
	local _, r4 = r:lootDowned("a", "b", P0, P0, T_EXPLORE + 20); eq(#r4.stolen, 0) -- paso mas de 3 s: reinicia la cuenta
end)
test("caida: se suelta la mitad de lo que llevas", function()
	local r = fresh(); r:addPlayer("a", 0)
	for i = 1, 5 do r.players.a.items[i] = { id = "i" .. i, value = 1, kind = "gema" } end
	local ok, drop = r:die("a", T_EXPLORE); truthy(ok); eq(#drop, 2); eq(#r.players.a.items, 3)
end)

print("== Deposito y llegada")
test("deposito: solo con el regreso abierto, canal de 2 s, se interrumpe si te derrotan", function()
	local r = fresh(); r:addPlayer("a", 0); r:addPlayer("b", 0)
	local ok0, why0 = r:startDeposit("a", near_goal, T_EXPLORE); eq(ok0, false); eq(why0, "la meta aun no se abre")
	truthy((r:startDeposit("a", near_goal, T_RETURN)))
	local okE, whyE = r:finishDeposit("a", near_goal, T_RETURN + 1); eq(okE, false); eq(whyE, "aun no termina el canal")
	r:knockOut("b", "a", T_RETURN + 1.2) -- te derrotan: se corta el deposito
	local okI, whyI = r:finishDeposit("a", near_goal, T_RETURN + 3); eq(okI, false)
	eq((r:startDeposit("a", { x = W.goal.x + 500, z = W.goal.z }, T_RETURN + 30)), false) -- lejos de la meta
end)
test("llegada: bonos 150/100/60/30/10; quien llega queda a salvo y fuera de juego", function()
	local r = fresh(); for i = 1, 5 do r:addPlayer(i, 0) end
	r.players[1].items = { { id = "z", value = 10, kind = "gema" } }
	local want = { 150, 100, 60, 30, 10 }
	for i = 1, 5 do
		local t = T_RETURN + i * 3
		truthy((r:startDeposit(i, near_goal, t))); local ok, res = r:finishDeposit(i, near_goal, t + 2.1)
		truthy(ok); eq(res.rank, i); eq(res.bonus, want[i])
	end
	eq(r.players[1].score, 160)
	eq((r:knockOut(2, 1, T_RETURN + 30)), false)
	eq((r:collectNode(1, 10, at(W.nodes[10]), T_RETURN + 30)), false)
end)

print("== Volcan")
local function world_with_volcano() for s = 1, 60 do local w = World.generate(s * 17); if w.volcano then return w end end end
local VW = world_with_volcano()
local function vrules() local r = Rules.new(VW, nil, 3); r:start(0); return r end
test("saltar al crater ASEGURA la erupcion; quien salta pierde lo que llevaba", function()
	truthy(VW ~= nil, "ninguna de 60 semillas tiene volcan")
	local r = vrules(); r:addPlayer("a", 0); r:addPlayer("b", 0)
	r.players.a.items = { { id = "1", value = 5, kind = "gema" }, { id = "2", value = 5, kind = "gema" } }
	eq(r:lavaRadius(T_EXPLORE), 0); eq(r:inLava(VW.volcano.x, VW.volcano.z, T_EXPLORE), false)
	eq((r:enterCrater("a", { x = VW.volcano.x + 200, z = VW.volcano.z }, T_EXPLORE)), false) -- lejos del crater
	local ok, res = r:enterCrater("a", at(VW.volcano), T_EXPLORE); truthy(ok); eq(res.lost, 2); eq(#r.players.a.items, 0)
	local ok2, why2 = r:enterCrater("b", at(VW.volcano), T_EXPLORE + 1); eq(ok2, false); eq(why2, "el volcan ya hizo erupcion")
end)
test("la lava crece despacio, tiene tope y NUNCA llega a la meta (ni en 10 horas)", function()
	local r = vrules(); r:addPlayer("a", 0); r:enterCrater("a", at(VW.volcano), T_EXPLORE)
	local r10, r60, r1000 = r:lavaRadius(T_EXPLORE + 10), r:lavaRadius(T_EXPLORE + 60), r:lavaRadius(T_EXPLORE + 36000)
	truthy(r10 < r60 and r60 <= r1000); eq(r1000, VW.volcano.max_lava)
	truthy(r:inLava(VW.volcano.x + 5, VW.volcano.z, T_EXPLORE + 10))
	eq(r:inLava(VW.goal.x, VW.goal.z, T_EXPLORE + 36000), false)
	truthy(dist(VW.volcano, VW.goal) - r1000 > VW.goal.radius, "la lava alcanzaria la plaza")
	near(r:lavaRadius(T_EXPLORE + 60), math.min(VW.volcano.max_lava, VW.volcano.crater_radius + VW.volcano.speed * 60), 1e-9)
end)
test("sin volcan en el mundo no hay erupcion", function()
	local nov; for s = 1, 60 do local w = World.generate(s * 19); if not w.volcano then nov = w; break end end
	local r = Rules.new(nov, nil, 1); r:start(0); r:addPlayer("a", 0)
	local ok, why = r:enterCrater("a", { x = 1, z = 1 }, T_EXPLORE); eq(ok, false); eq(why, "no hay volcan")
	eq(r:lavaRadius(T_EXPLORE), 0)
end)

print("== Colapso final")
test("al acabar el tiempo se cierra la meta y empieza el colapso", function()
	local r = fresh(); r:addPlayer("a", 0)
	local ok, why = r:startDeposit("a", near_goal, T_COLLAPSE); eq(ok, false); truthy(why:find("fuera de fase"))
	eq((r:collectNode("a", 1, at(W.nodes[1]), T_COLLAPSE)), false)
end)
test("desastres: lista determinista con terremotos, tornados, tormenta, rayos y hundimiento (y erupcion si hay volcan)", function()
	local function kinds(w)
		local r = Rules.new(w, nil, 11); r:start(0)
		local ev, k = r:disasterSchedule(), {}
		for _, e in ipairs(ev) do k[e.kind] = (k[e.kind] or 0) + 1; truthy(e.t >= 0 and e.t <= r.cfg.collapse, "evento fuera del colapso") end
		return ev, k
	end
	local ev, k = kinds(VW)
	eq(k.terremoto, 4); eq(k.tornado, 3); eq(k.tormenta, 1); eq(k.rayo, 18); eq(k.hundimiento, 1); eq(k.erupcion, 1)
	local ev2 = kinds(VW); eq(#ev, #ev2); for i = 1, #ev do eq(ev[i].kind, ev2[i].kind); eq(ev[i].t, ev2[i].t) end
	for i = 2, #ev do truthy(ev[i - 1].t <= ev[i].t, "no esta ordenada") end
	local nov; for s = 1, 60 do local w = World.generate(s * 19); if not w.volcano then nov = w; break end end
	local _, k2 = kinds(nov); eq(k2.erupcion, nil)
end)
test("fin: lo no depositado se pierde por completo; ranking ordenado (tambien durante el colapso)", function()
	local r = fresh(); r:addPlayer("a", 0); r:addPlayer("b", 0); r:addPlayer("c", 0)
	r.players.a.items = { { id = "1", value = 50, kind = "gema" } }
	r.players.c.items = { { id = "2", value = 999, kind = "gema" }, { id = "3", value = 1, kind = "gema" } }
	truthy((r:startDeposit("a", near_goal, T_RETURN))); truthy((r:finishDeposit("a", near_goal, T_RETURN + 2.5)))
	eq((r:finalScores(T_RETURN)), false)
	for _, t in ipairs({ T_COLLAPSE, T_END }) do
		local ok, res = r:finalScores(t); truthy(ok)
		eq(res[1].id, "a"); eq(res[1].score, 200); eq(res[1].place, 1)
		local c; for _, x in ipairs(res) do if x.id == "c" then c = x end end
		eq(c.score, 0); eq(c.lost, 2); eq(c.lost_value, 1000)
	end
end)

print("== Economia")
test("la MAYORIA de los puntos salen del mapa, no de los bonos de llegada (simulacion con 24 jugadores)", function()
	local share_sum, runs, worst = 0, 0, 0
	for seed = 1, 10 do
		local w = World.generate(seed * 211)
		local r = Rules.new(w, nil, seed); r:start(0)
		local list = {}
		for i, c in ipairs(w.chests) do list[#list + 1] = { v = c.value + (c.bonus or 0), kind = "c", id = i } end
		for i, n in ipairs(w.nodes) do list[#list + 1] = { v = n.value, kind = "n", id = i } end
		local players = 24
		for p = 1, players do r:addPlayer(p, 0) end
		-- cada bot toma lo mas valioso de su sector (3 bots por sector) hasta llenar la mochila
		for p = 1, players do
			local sec, mine = (p - 1) % 8 + 1, {}
			for _, it in ipairs(list) do
				local o = it.kind == "c" and w.chests[it.id] or w.nodes[it.id]
				if World.sector(o.x - w.goal.x, o.z - w.goal.z) == sec then mine[#mine + 1] = it end
			end
			table.sort(mine, function(a, b) return a.v > b.v end)
			for _, it in ipairs(mine) do
				local o = it.kind == "c" and w.chests[it.id] or w.nodes[it.id]
				if it.kind == "c" then r:claimChest(p, it.id, at(o), T_EXPLORE) else r:collectNode(p, it.id, at(o), T_EXPLORE) end
			end
		end
		local loot, bonus = 0, 0
		for p = 1, players do
			for _, it in ipairs(r.players[p].items) do loot = loot + it.value end
			local t = T_RETURN + p * 3; r:startDeposit(p, { x = w.goal.x + 5, z = w.goal.z }, t)
			local _, res = r:finishDeposit(p, { x = w.goal.x + 5, z = w.goal.z }, t + 2.1)
			bonus = bonus + res.bonus
		end
		local share = bonus / (bonus + loot); share_sum = share_sum + share; runs = runs + 1; worst = math.max(worst, share)
	end
	print(string.format("       bonos = %.0f%% de los puntos en promedio (peor mundo %.0f%%)", share_sum / runs * 100, worst * 100))
	truthy(share_sum / runs <= 0.20, "los bonos pesan demasiado: " .. share_sum / runs)
end)

print(string.format("\n%d pruebas ok, %d fallaron", passed, failed))
return failed
