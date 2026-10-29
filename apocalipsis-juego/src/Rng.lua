-- Generador pseudoaleatorio determinista (Park-Miller). Solo aritmetica de enteros exactos (< 2^53),
-- asi da LOS MISMOS numeros en Lua 5.x y en Luau (Roblox): misma semilla = mismo mundo.
local Rng = {}
Rng.__index = Rng
local M = 2147483647

function Rng.new(seed)
	seed = math.floor(seed) % M
	if seed == 0 then seed = 1 end
	return setmetatable({ s = seed }, Rng)
end

function Rng:next() -- decimal en (0,1)
	self.s = (self.s * 16807) % M
	return self.s / M
end

function Rng:int(a, b) return a + math.floor(self:next() * (b - a + 1)) end
function Rng:range(a, b) return a + (b - a) * self:next() end
function Rng:chance(p) return self:next() < p end
function Rng:pick(list) return list[self:int(1, #list)] end

-- Flujo derivado e independiente (para que cambiar una parte no altere las demas).
function Rng:fork(label)
	local h = self.s
	for i = 1, #label do h = (h * 31 + string.byte(label, i)) % M end
	return Rng.new(h)
end

-- Mezcla de una lista (Fisher-Yates), devuelve una copia.
function Rng:shuffle(list)
	local out = {}
	for i = 1, #list do out[i] = list[i] end
	for i = #out, 2, -1 do
		local j = self:int(1, i)
		out[i], out[j] = out[j], out[i]
	end
	return out
end

return Rng
