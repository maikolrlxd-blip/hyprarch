-- Pruebas de Combat y de una partida completa con bots (Capa 1). Lua puro.
local World, Rules, Combat = require("World"), require("Rules"), require("Combat")
local passed, failed = 0, 0
local function test(name, fn)
	local ok, err = pcall(fn)
	if ok then passed = passed + 1; print("  ok   " .. name)
	else failed = failed + 1; print("  FAIL " .. name .. "\n       " .. tostring(err)) end
end
local function eq(a, b, msg) if a ~= b then error((msg or "eq") .. ": esperaba " .. tostring(b) .. ", obtuve " .. tostring(a), 2) end end
local function truthy(v, msg) if not v then error(msg or "se esperaba verdadero", 2) end end

print("== Combate (Capa 1)")
local function setup(n)
	local w = World.generate(7)
	local r = Rules.new(w, nil, 7); local c = Combat.new(r)
	for i = 1, n do r:addPlayer(i, 0); c:addPlayer(i) end
	r:start(0)
	return w, r, c, 10 -- 10 s: fase explorar
end
local A, B = { x = 0, z = 0 }, { x = 3, z = 0 }

test("5 golpes derrotan (100 hp, 20 de dano) y dejan inconsciente", function()
	local _, r, c, t = setup(2)
	for i = 1, 4 do local ok, d = c:punch(1, 2, A, B, t + i * 0.6); truthy(ok); truthy(not d.knocked_out) end
	local ok, d = c:punch(1, 2, A, B, t + 5 * 0.6)
	truthy(ok and d.knocked_out); truthy(r:isDowned(2, t + 3.1))
end)
test("la cadencia limita: 2 golpes por segundo", function()
	local _, _, c, t = setup(2)
	truthy(c:punch(1, 2, A, B, t)); local ok, why = c:punch(1, 2, A, B, t + 0.1); truthy(not ok and why == "espera")
	truthy(c:punch(1, 2, A, B, t + 0.51))
end)
test("alcance, auto-golpe e inconscientes no pueden golpear ni ser golpeados", function()
	local _, r, c, t = setup(3)
	local ok, why = c:punch(1, 2, A, { x = 50, z = 0 }, t); truthy(not ok and why == "muy lejos")
	ok, why = c:punch(1, 1, A, A, t); truthy(not ok)
	r:knockOut(1, 2, t)
	ok, why = c:punch(3, 2, A, B, t + 1); truthy(not ok and why == "ya esta inconsciente")
	ok, why = c:punch(2, 3, B, A, t + 1); truthy(not ok and why == "estas inconsciente")
end)
test("al despertar recupera la vida y tiene inmunidad", function()
	local _, r, c, t = setup(2)
	for i = 1, 5 do c:punch(1, 2, A, B, t + i * 0.6) end
	local up = t + 3 + r.cfg.downed_time + 0.1
	eq(c:getHp(2, up), 100)
	local ok, why = c:punch(1, 2, A, B, up); truthy(not ok and why == "inmune")
end)
test("el golpe devuelve empuje alejando a la victima", function()
	local _, _, c, t = setup(2)
	local ok, d = c:punch(1, 2, A, B, t); truthy(ok and d.push.x > 0 and d.push.z == 0)
end)

print("== Partida completa con bots (determinista)")
local function playMatch(seed, nbots)
	local w = World.generate(seed)
	local r = Rules.new(w, { explore = 60, return_window = 40, collapse = 10, countdown = 1 }, seed)
	local c = Combat.new(r)
	for i = 1, nbots do r:addPlayer(i, 0); c:addPlayer(i) end
	r:start(0)
	local pos, goal = {}, w.goal
	for i = 1, nbots do pos[i] = { x = w.spawns[i].x, z = w.spawns[i].z } end
	local kos, loots, collected = 0, 0, 0
	local t = 2
	while t < 60 + 1 do -- fase de exploracion: cada bot recoge su nodo mas cercano libre y a veces pelea
		for i = 1, nbots do
			local best, bd
			for id, nd in ipairs(w.nodes) do
				if not r.taken_nodes[id] then
					local d = math.abs(nd.x - pos[i].x) + math.abs(nd.z - pos[i].z)
					if not bd or d < bd then best, bd = id, d end
				end
			end
			if best and not r:isDowned(i, t) then
				local nd = w.nodes[best]; pos[i] = { x = nd.x, z = nd.z }
				if r:collectNode(i, best, pos[i], t) then collected = collected + 1 end
			end
			local j = i % nbots + 1
			if (math.floor(t) + i) % 7 == 0 then
				for k = 1, 5 do
					local ok, d = c:punch(i, j, pos[i], { x = pos[i].x + 2, z = pos[i].z }, t + k * 0.55)
					if ok and d.knocked_out then kos = kos + 1; local ok2 = r:lootDowned(i, j, pos[i], { x = pos[i].x + 2, z = pos[i].z }, t + 3.2); if ok2 then loots = loots + 1 end end
				end
			end
		end
		t = t + 5
	end
	eq(r:phase(61.5), "return")
	for i = 1, nbots do
		local tt = 62 + i
		pos[i] = { x = goal.x + 4, z = goal.z }
		if r:startDeposit(i, pos[i], tt) then r:finishDeposit(i, pos[i], tt + 2.1) end
	end
	local ok, res = r:finalScores(1 + 60 + 40 + 1)
	truthy(ok, "finalScores")
	return res, kos, loots, collected
end
test("una partida de 12 bots termina con puntajes, derrotas y saqueos, sin errores", function()
	local res, kos, loots, collected = playMatch(5, 12)
	eq(#res, 12); truthy(collected > 50, "recogieron " .. collected)
	local arrived = 0; for _, x in ipairs(res) do if x.arrived then arrived = arrived + 1 end end
	truthy(arrived >= 6, "llegaron " .. arrived)
	print(string.format("       %d recogidos, %d derrotas, %d saqueos, %d llegaron; ganador %s con %d", collected, kos, loots, arrived, res[1].id, res[1].score))
end)
test("la misma semilla da la misma partida", function()
	local a, b = playMatch(5, 12), playMatch(5, 12)
	for i = 1, #a do eq(a[i].id, b[i].id); eq(a[i].score, b[i].score) end
end)

print(string.format("\n%d pruebas ok, %d fallaron", passed, failed))
return failed
