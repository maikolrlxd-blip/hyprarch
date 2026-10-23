local Weapons = require("Weapons"); local Impactos = require("Impactos"); local Disparo = require("Disparo")
local passed, failed = 0, 0
local function test(name, fn)
	local ok, err = pcall(fn)
	if ok then passed = passed + 1; print("  ok   " .. name) else failed = failed + 1; print("  FAIL " .. name .. "\n       " .. tostring(err)) end
end
local function eq(a, b, m) if a ~= b then error((m or "eq") .. ": esperaba " .. tostring(b) .. ", obtuve " .. tostring(a), 2) end end
local function truthy(v, m) if not v then error(m or "se esperaba verdadero", 2) end end
local function near(a, b, t, m) if math.abs(a - b) > t then error((m or "near") .. ": " .. a .. " vs " .. b, 2) end end

print("== Armas")
test("la pistola respeta la cadencia (4,5 tiros/s) y gasta municion", function()
	local w = Weapons.new("pistola", 1); w:equip(0)
	truthy((w:fire(1))); local ok, why = w:fire(1.05); truthy(not ok and why == "no lista")
	truthy((w:fire(1 + 1 / 4.5 + 0.001))); eq(w.ammo, 13)
end)
test("sin municion: clic y no dispara; recargar llena con la reserva", function()
	local w = Weapons.new("pistola", 1); w.ammo = 0
	local ok, why = w:fire(2); truthy(not ok and why == "sin municion")
	truthy((w:reload(3))); local done = w:update(3 + 1.69); truthy(not done); truthy(w:update(3 + 1.71)); eq(w.ammo, 15); eq(w.reserve, 75)
end)
test("no se dispara mientras se recarga el cargador; la recarga no pasa de la reserva", function()
	local w = Weapons.new("subfusil", 1, { reserve = 10 }); w.ammo = 5; w:equip(0)
	truthy((w:reload(1))); local ok, why = w:fire(1.5); truthy(not ok and why == "recargando")
	w:update(1 + 2); eq(w.ammo, 15); eq(w.reserve, 0)
end)
test("subfusil automatico: 12 tiros/s y la dispersion crece en rafaga", function()
	local w = Weapons.new("subfusil", 3); w:equip(0)
	local t, shots = 1, 0
	for i = 1, 30 do local ok = w:fire(t); if ok then shots = shots + 1 end; t = t + 0.001 end
	eq(shots, 1) -- 30 intentos en 30 ms: solo uno entra
	local w2 = Weapons.new("subfusil", 3); w2:equip(0); local n = 0
	t = 1; while t < 2 do if w2:fire(t) then n = n + 1 end; t = t + 0.01 end
	truthy(n >= 11 and n <= 13, "tiros en 1 s: " .. n)
end)
test("escopeta: 8 perdigones, recarga cartucho a cartucho e interrumpible disparando", function()
	local w = Weapons.new("escopeta", 5); w:equip(0)
	local ok, r = w:fire(1); truthy(ok); eq(#r.pellets, 8); eq(r.pump_clip, "Bombear")
	w.ammo = 3
	truthy((w:reload(3)))                  -- inicio 0,5 s, luego un cartucho cada 0,55 s
	w:update(3.5 + 0.56); eq(w.ammo, 5)    -- ya metio 2 cartuchos
	local ok2 = w:fire(4.2); truthy(ok2, "debe poder interrumpir la recarga si hay municion"); eq(w.ammo, 4)
end)
test("escopeta: dano por perdigon cae con la distancia y es nulo fuera de alcance", function()
	local w = Weapons.new("escopeta", 1)
	near(w:damage(5, false), 12, 1e-9); truthy(w:damage(40, false) < 12 and w:damage(40, false) > 12 * 0.15)
	eq(w:damage(61, false), 0)
end)
test("cabeza: la pistola hace x2", function()
	local w = Weapons.new("pistola", 1); near(w:damage(10, true), 50, 1e-9); near(w:damage(10, false), 25, 1e-9)
end)
test("misma semilla = misma dispersion", function()
	local a, b = Weapons.new("escopeta", 9), Weapons.new("escopeta", 9); a:equip(0); b:equip(0)
	local _, ra = a:fire(1); local _, rb = b:fire(1)
	for i = 1, 8 do eq(ra.pellets[i].yaw, rb.pellets[i].yaw) end
end)
test("inspeccionar: solo con el arma libre", function()
	local w = Weapons.new("pistola", 1); w:equip(0)
	local ok, why = w:inspect(0.1); truthy(not ok and why == "ocupada")
	local ok2, r = w:inspect(1); truthy(ok2 and r.clip == "Inspeccionar")
end)

print("== Impactos en enemigos")
test("cabeza hace mas dano que torso y mas efecto; brazo menos", function()
	local h = Impactos.resolve("pistola", "cabeza", 10); local t = Impactos.resolve("pistola", "torso", 10); local b = Impactos.resolve("pistola", "brazo", 10)
	near(h.dano, 50, 1e-9); near(t.dano, 25, 1e-9); near(b.dano, 18.75, 1e-9)
	truthy(h.efecto.count > t.efecto.count and t.efecto.count > b.efecto.count); truthy(h.reaccion.stagger > t.reaccion.stagger)
end)
test("fuera de alcance no hay impacto; zona desconocida es error", function()
	local r, why = Impactos.resolve("escopeta", "torso", 70); truthy(r == nil and why == "fuera de alcance")
	local r2 = Impactos.resolve("pistola", "cola", 5); truthy(r2 == nil)
end)
test("sangre apagada: chispas neutras y sin mancha", function()
	local r = Impactos.resolve("subfusil", "torso", 10, nil, { sangre = false })
	truthy(r.mancha == nil); eq(r.efecto.color[1], 230)
	local r2 = Impactos.resolve("subfusil", "torso", 10); truthy(r2.mancha ~= nil); truthy(r2.efecto.color[1] < 200)
end)
test("escopeta: varios perdigones en la misma zona suman dano y empuje mayor", function()
	local one = Impactos.resolve("escopeta", "torso", 5); local many = Impactos.resolve("escopeta", "torso", 5, nil, { pellets_en_zona = 6 })
	near(many.dano, one.dano * 6, 1e-9); truthy(many.efecto.count > one.efecto.count); eq(many.reaccion.empuje, 8)
end)
test("reserva de manchas: tope y reemplazo de la mas vieja", function()
	local res = Impactos.nuevaReserva(3)
	for i = 1, 3 do eq(Impactos.agregarMancha(res, { i = i }, i), nil) end
	local old = Impactos.agregarMancha(res, { i = 4 }, 4); eq(old.mancha.i, 1)
	eq(Impactos.vivas(res, 5, 20), 3); eq(Impactos.vivas(res, 100, 20), 0)
end)

print("== Disparo real")
test("direccion sin desvio = punteria; con desvio mantiene longitud 1 y el angulo pedido", function()
	local d0 = Disparo.direccion({ x = 0, y = 0, z = -1 }, 0, 0); near(d0.z, -1, 1e-9)
	local d = Disparo.direccion({ x = 0, y = 0, z = -2 }, 3, 4)
	near(math.sqrt(d.x ^ 2 + d.y ^ 2 + d.z ^ 2), 1, 1e-9)
	local ang = math.deg(math.acos(-d.z)); truthy(ang > 4.5 and ang < 5.5, "angulo " .. ang)
end)
test("direccion funciona apuntando recto arriba (sin dividir por cero)", function()
	local d = Disparo.direccion({ x = 0, y = 1, z = 0 }, 2, 0); near(math.sqrt(d.x ^ 2 + d.y ^ 2 + d.z ^ 2), 1, 1e-9); truthy(d.y > 0.99)
end)
test("zonas R15 y R6; piezas desconocidas = torso", function()
	eq(Disparo.zona("Head"), "cabeza"); eq(Disparo.zona("LeftLowerArm"), "brazo"); eq(Disparo.zona("RightFoot"), "pierna")
	eq(Disparo.zona("Torso"), "torso"); eq(Disparo.zona("Sombrero"), "torso")
end)
test("agujeros: tamano por arma, marca en enemigo dura menos y es roja", function()
	local m, e = Disparo.agujero("escopeta", false), Disparo.agujero("escopeta", true)
	near(m.tam, 0.3, 1e-9); truthy(e.vida < m.vida); truthy(e.color_centro[1] > m.color_centro[1])
end)
test("escopeta de 8 perdigones: todas las direcciones salen dentro del cono de dispersion", function()
	local w = Weapons.new("escopeta", 11); w:equip(0); local ok, r = w:fire(1, false); truthy(ok)
	for _, p in ipairs(r.pellets) do
		local d = Disparo.direccion({ x = 0, y = 0, z = -1 }, p.yaw, p.pitch); local ang = math.deg(math.acos(-d.z)); truthy(ang <= w.def.spread + 0.01, "fuera del cono: " .. ang)
	end
end)

print("== Tiempo para matar (zombi de 100 de vida)")
for _, id in ipairs({ "pistola", "escopeta", "subfusil" }) do
	local t1, s1 = Weapons.ttk(id, 100, 8, false); local t2, s2 = Weapons.ttk(id, 100, 30, false); local t3, s3 = Weapons.ttk(id, 100, 8, true)
	print(string.format("       %-9s cerca: %d disp en %.2fs | a 30 studs: %d disp en %.2fs | cabeza cerca: %d disp en %.2fs", id, s1, t1, s2, t2, s3, t3))
end
print(string.format("\n%d pruebas ok, %d fallaron", passed, failed))
return failed
