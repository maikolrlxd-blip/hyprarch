-- Impacto de las balas en los enemigos (Luto): QUE pasa al acertar. Modulo PURO: decide zona, dano, reaccion, efecto, sonido y manchas.
-- El cliente/servidor de Roblox dibuja lo que aqui se especifica (ver client/ImpactoFX.lua). Sangre ESTILIZADA (particulas y manchas que
-- se desvanecen), sin desmembramiento; el modo 'sangre = false' la sustituye por chispas neutras (opcion de accesibilidad / clasificacion).
local Weapons = script and require(script.Parent.Weapons) or require("Weapons")

local Impactos = {}

Impactos.ZONAS = { cabeza = { mult = 1.0, stagger = 0.9, fx = "grande" }, torso = { mult = 1.0, stagger = 0.25, fx = "medio" },
	brazo = { mult = 0.75, stagger = 0.1, fx = "chico" }, pierna = { mult = 0.75, stagger = 0.35, fx = "chico" } }

-- Especificacion de efectos (para ParticleEmitter): cantidad, velocidad, vida, tamano, color. Valores PROVISIONALES.
Impactos.FX = {
	chico = { count = 6, speed = 14, life = 0.35, size = 0.35, color = { 150, 20, 25 } },
	medio = { count = 12, speed = 18, life = 0.45, size = 0.5, color = { 135, 15, 22 } },
	grande = { count = 22, speed = 24, life = 0.6, size = 0.65, color = { 120, 10, 20 } },
}
Impactos.NEUTRO = { color = { 230, 210, 120 } } -- chispas amarillas cuando la sangre esta apagada

Impactos.MANCHAS = { max = 60, vida = 20, tam_min = 1.5, tam_max = 3.5 } -- tope de manchas en el mapa y segundos antes de desvanecerse

-- Resuelve un impacto. weaponId: 'pistola'|'escopeta'|'subfusil'; zona: clave de ZONAS; dist en studs; normal = {x,y,z} de la superficie golpeada;
-- opts.sangre (por defecto true), opts.pellets_en_zona (escopeta: perdigones que dieron a la misma zona, se suman).
function Impactos.resolve(weaponId, zona, dist, normal, opts)
	opts = opts or {}
	local def, z = Weapons.DEFS[weaponId], Impactos.ZONAS[zona]
	if not def or not z then return nil, "arma o zona desconocida" end
	local mult = Weapons.falloff(def, dist)
	if mult <= 0 then return nil, "fuera de alcance" end
	local n = opts.pellets_en_zona or 1
	local base = def.damage * mult * z.mult * (zona == "cabeza" and def.headshot or 1) * n
	local sangre = opts.sangre ~= false
	local fx = Impactos.FX[z.fx]
	return {
		dano = base, zona = zona, cabeza = zona == "cabeza",
		reaccion = { clip = "Golpeado", stagger = z.stagger, empuje = def.pellets > 1 and 8 or 3 }, -- probabilidad de tambalearse y empuje (studs)
		efecto = { count = fx.count * (n > 1 and 1.5 or 1), speed = fx.speed, life = fx.life, size = fx.size,
			color = sangre and fx.color or Impactos.NEUTRO.color, direccion = normal or { x = 0, y = 1, z = 0 } },
		sonido = "impacto_zombi", marcador = "marcador_impacto",
		mancha = sangre and { tam = Impactos.MANCHAS.tam_min + (Impactos.MANCHAS.tam_max - Impactos.MANCHAS.tam_min) * (zona == "cabeza" and 1 or 0.5) } or nil,
	}
end

-- Reserva de manchas (decals) con tope: si se llena, desaparece la mas vieja. Anillo circular puro.
function Impactos.nuevaReserva(max) return { max = max or Impactos.MANCHAS.max, items = {}, next = 1 } end
function Impactos.agregarMancha(res, mancha, now)
	local old = res.items[res.next]; res.items[res.next] = { t = now, mancha = mancha }
	res.next = res.next % res.max + 1
	return old -- el que hay que quitar del mapa (o nil)
end
function Impactos.vivas(res, now, vida)
	local n = 0; vida = vida or Impactos.MANCHAS.vida
	for i = 1, res.max do local it = res.items[i]; if it and now - it.t < vida then n = n + 1 end end
	return n
end

return Impactos
