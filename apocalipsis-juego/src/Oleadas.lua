-- Oleadas infinitas de Luto: que zombis hay en cada ronda y cuanto escalan. Modulo PURO. Valores PROVISIONALES para ajustar jugando.
local Rng = script and require(script.Parent.Rng) or require("Rng")
local Oleadas = {}

Oleadas.JEFE_CADA = 15
Oleadas.JEFES = { "lamentadora", "alta" } -- tipos de mujer infectada (el primero: La Lamentadora, larga y deformada)

-- Configuracion de una ronda. seed solo sirve para elegir el jefe (determinista).
function Oleadas.config(ronda, seed)
	local esJefe = ronda % Oleadas.JEFE_CADA == 0
	local k = ronda - 1
	local cfg = {
		ronda = ronda, esJefe = esJefe,
		cantidad = math.min(5 + 2 * k, 80),              -- zombis comunes en la ronda
		simultaneos = math.min(3 + k, 30),               -- tope de zombis vivos a la vez (la ronda 1 llega poco a poco)
		hp = math.floor(100 * (1 + 0.12 * k)),
		velocidad = math.min(8 + 0.25 * k, 14),          -- studs/s (el jugador anda a 16)
		dano = math.floor(5 + 0.7 * k),                  -- por golpe (cada ~1,2 s); ronda 1 = 5
		recompensa = 10 + 2 * (k // 5),                  -- monedas por zombi
		intervalo = math.max(0.6, 3.0 - 0.1 * k),        -- segundos entre apariciones (ronda 1: 3 s)
	}
	if esJefe then
		local n = ronda // Oleadas.JEFE_CADA
		local tipo = Oleadas.JEFES[Rng.new((seed or 1) * 7919 + ronda):int(1, #Oleadas.JEFES)]
		cfg.jefe = { tipo = tipo, hp = 2500 * (1 + 0.5 * (n - 1)), velocidad = tipo == "alta" and 11 or 8, dano = 25 + 5 * (n - 1),
			escala = 1.8, recompensa = 150 * n }
		cfg.cantidad = cfg.cantidad // 2                  -- el jefe viene acompanado de menos comunes
	end
	return cfg
end

-- Moneda del lobby que se gana al terminar la partida: por la ronda alcanzada y por cada jefe derrotado.
function Oleadas.monedasLobby(rondaMax, jefesDerrotados)
	return math.floor((rondaMax - 1) ^ 1.3) + 25 * jefesDerrotados
end

return Oleadas
