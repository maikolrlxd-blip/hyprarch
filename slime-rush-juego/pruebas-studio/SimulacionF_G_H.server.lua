-- Simulacion F/G/H SIN pantalla. SOLO para correr en una COPIA de QA (no esta mapeada en default.project.json).
-- Uso: pega este Script en ServerScriptService de la copia (o mapealo con Rojo en una copia) y pulsa Play.
-- Crea su PROPIA partida (World/Rules/Combat desde ReplicatedStorage.SlimeRush) con dos jugadores falsos y un
-- reloj virtual: no espera tiempo real, no toca server/ ni client/ ni el Workspace. Imprime SR_TEST en Output.
local RS = game:GetService("ReplicatedStorage")
local SR = RS:WaitForChild("SlimeRush")
local World, Rules, Combat = require(SR.World), require(SR.Rules), require(SR.Combat)

local SEED = 1234
local TEST = { size = 512, cell = 16, node_count = 40, players = 8,
	chests = { comun = 3, musgoso = 0, dorado = 0, oculto = 0 }, rare_sites = 0, volcano_chance = 0 }

local pass, fail = 0, 0
local function check(name, cond, detail)
	if cond then pass = pass + 1 else fail = fail + 1 end
	print(string.format("SR_TEST %s %s%s", cond and "PASS" or "FAIL", name, detail and (" | " .. tostring(detail)) or ""))
end
local function shows(v) if type(v) == "table" then return "tabla" end return tostring(v) end

local function run()
	-- 1) Mundo
	local c0 = os.clock()
	local world = World.generate(SEED, TEST)
	local ms = math.floor((os.clock() - c0) * 1000 + 0.5)
	check("mundo generado", world and world.goal and #world.nodes > 0, "ms=" .. ms .. " nodos=" .. #world.nodes .. " cofres=" .. #world.chests)
	check("hay aparicion para 2 jugadores", world.spawns[1] ~= nil and world.spawns[2] ~= nil)

	local rules = Rules.new(world, nil, SEED)
	local combat = Combat.new(rules)
	local cfg = rules.cfg
	local T0 = 1000
	local now = T0 - 1
	check("fase antes de empezar", rules:phase(now) == "generating", rules:phase(now))
	check("addPlayer 1", rules:addPlayer(1, now) == true)
	check("addPlayer 2", rules:addPlayer(2, now) == true)
	combat:addPlayer(1); combat:addPlayer(2)
	rules:start(T0)
	now = T0 + 0.1
	check("fase cuenta atras", rules:phase(now) == "countdown", rules:phase(now))
	local ok, why = rules:collectNode(1, 1, world.nodes[1], now)
	check("no se recoge en la cuenta atras", ok == false, why)

	-- 2) Explorar y recoger (E)
	now = T0 + cfg.countdown + 1
	check("fase explorar", rules:phase(now) == "explore", rules:phase(now))
	ok, why = rules:collectNode(1, 1, { x = world.nodes[1].x + 100, z = world.nodes[1].z }, now)
	check("E: muy lejos se rechaza", ok == false, why)
	for i = 1, 3 do
		ok, why = rules:collectNode(1, i, { x = world.nodes[i].x, z = world.nodes[i].z }, now)
		check("E: jugador 1 recoge nodo " .. i, ok == true, shows(why))
	end
	ok, why = rules:collectNode(2, 1, { x = world.nodes[1].x, z = world.nodes[1].z }, now)
	check("E: nodo ya recogido se rechaza", ok == false, why)
	for i = 4, 5 do
		ok, why = rules:collectNode(2, i, { x = world.nodes[i].x, z = world.nodes[i].z }, now)
		check("E: jugador 2 recoge nodo " .. i, ok == true, shows(why))
	end
	check("mochila J1=3, J2=2", #rules.players[1].items == 3 and #rules.players[2].items == 2,
		#rules.players[1].items .. "/" .. #rules.players[2].items)

	-- 3) Meta cerrada en explorar
	local goalPos = { x = world.goal.x, z = world.goal.z }
	ok, why = rules:startDeposit(1, goalPos, now)
	check("H: la meta aun no se abre en explorar", ok == false, why)

	-- 4) Golpear (F) x5 hasta inconsciente
	local p1, p2 = { x = 100, z = 100 }, { x = 103, z = 100 }
	local last
	for i = 1, 5 do
		ok, last = combat:punch(1, 2, p1, p2, now)
		check("F: golpe " .. i, ok == true, ok and ("hp=" .. last.hp .. " ko=" .. tostring(last.knocked_out)) or last)
		if i == 1 then
			local ok2, why2 = combat:punch(1, 2, p1, p2, now + 0.05)
			check("F: la cadencia rechaza el golpe inmediato", ok2 == false, why2)
		end
		now = now + 1 / combat.cfg.attack_rate + 0.1
	end
	check("F: el 5o golpe deja inconsciente", last and last.knocked_out == true and last.hp == 0, last and ("hp=" .. last.hp))
	check("J2 inconsciente", rules:isDowned(2, now) == true)
	ok, why = combat:punch(2, 1, p2, p1, now)
	check("F: un inconsciente no golpea", ok == false, why)
	ok, why = combat:punch(1, 2, { x = 100, z = 100 }, { x = 160, z = 100 }, now)
	check("F: fuera de alcance se rechaza", ok == false, why)

	-- 5) Saquear (G) a un inconsciente
	local before1, before2 = #rules.players[1].items, #rules.players[2].items
	ok, last = rules:lootDowned(1, 2, p1, p2, now)
	check("G: saqueo al inconsciente", ok == true, ok and ("robados=" .. #last.stolen) or last)
	check("G: los objetos pasaron de J2 a J1", ok == true and #rules.players[1].items == before1 + #last.stolen
		and #rules.players[2].items == before2 - #last.stolen, #rules.players[1].items .. "/" .. #rules.players[2].items)
	ok, why = rules:lootDowned(1, 2, p1, p2, now + 0.1)
	check("G: la espera entre saqueos", ok == false, why)
	ok, why = rules:lootDowned(1, 2, p1, { x = 200, z = 200 }, now + 5)
	check("G: muy lejos se rechaza", ok == false, why)

	-- 6) Despertar e inmunidad
	now = now + cfg.downed_time + 0.5
	check("J2 despierta tras downed_time", rules:isDowned(2, now) == false)
	check("vida de J2 vuelve a " .. combat.cfg.max_hp, combat:getHp(2, now) == combat.cfg.max_hp, combat:getHp(2, now))
	ok, why = combat:punch(1, 2, p1, p2, now)
	check("F: inmunidad al despertar", ok == false, why)

	-- 7) Regreso: deposito (H)
	now = T0 + cfg.countdown + cfg.explore + 1
	check("fase regreso", rules:phase(now) == "return", rules:phase(now))
	check("el regreso ya esta abierto", rules:return_opens_in(now) == nil)
	ok, why = rules:startDeposit(1, { x = world.goal.x + cfg.goal_radius + 50, z = world.goal.z }, now)
	check("H: fuera de la meta se rechaza", ok == false, why)

	-- deposito de J2 interrumpido por una derrota
	ok, why = rules:startDeposit(2, goalPos, now)
	check("H: J2 empieza deposito", ok == true, why)
	ok, last = rules:knockOut(1, 2, now + 0.5)
	check("derrota interrumpe el deposito de J2", ok == true and rules.players[2].depositing == nil, shows(last))
	ok, why = rules:finishDeposit(2, goalPos, now + cfg.deposit_time + 1)
	check("H: J2 no puede terminar (inconsciente/interrumpido)", ok == false, why)

	-- deposito exitoso de J1
	ok, why = rules:startDeposit(1, goalPos, now + 1)
	check("H: J1 empieza deposito", ok == true, why)
	ok, why = rules:finishDeposit(1, goalPos, now + 1.2)
	check("H: no termina antes de deposit_time", ok == false, why)
	local items1 = #rules.players[1].items
	ok, last = rules:finishDeposit(1, goalPos, now + 1 + cfg.deposit_time + 0.1)
	check("H: deposito con exito dentro de la ventana de regreso", ok == true and last.rank == 1,
		ok and ("rank=" .. last.rank .. " bonus=" .. last.bonus .. " score=" .. last.score .. " objetos=" .. items1) or last)
	check("la mochila de J1 queda vacia", #rules.players[1].items == 0)
	ok, why = rules:collectNode(1, 6, world.nodes[6], now + 20)
	check("quien ya deposito no puede recoger", ok == false, why)

	-- 8) Entrar tarde, colapso y resultados
	ok, why = rules:addPlayer(3, now)
	check("entrar tarde se rechaza", ok == false, why)
	ok, why = rules:finalScores(now)
	check("no hay resultados antes del colapso", ok == false, why)
	now = T0 + cfg.countdown + cfg.explore + cfg.return_window + 1
	check("fase colapso", rules:phase(now) == "collapse", rules:phase(now))
	check("calendario de desastres no vacio", #rules:disasterSchedule() > 0, #rules:disasterSchedule())
	ok, last = rules:finalScores(now)
	check("resultados finales", ok == true and #last == 2, ok and #last or last)
	if ok then
		for _, r in ipairs(last) do
			print(string.format("SR_TEST RESULTADO puesto=%d jugador=%d puntos=%d llego=%s perdio=%d (valor %d)",
				r.place, r.id, r.score, tostring(r.arrived), r.lost, r.lost_value))
		end
		check("J1 gana y J2 no llego pierde todo", last[1].id == 1 and last[1].score > 0 and last[2].id == 2
			and last[2].score == 0 and last[2].arrived == false)
	end
	now = T0 + cfg.countdown + cfg.explore + cfg.return_window + cfg.collapse + 1
	check("fase terminada", rules:phase(now) == "ended", rules:phase(now))
end

local good, err = xpcall(run, debug.traceback)
if not good then
	fail = fail + 1
	print("SR_TEST FAIL error de ejecucion | " .. tostring(err))
end
print(string.format("SR_TEST RESUMEN %s: %d PASS, %d FAIL", fail == 0 and "PASS" or "FAIL", pass, fail))
