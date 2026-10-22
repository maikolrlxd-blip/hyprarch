-- Ruido de valor 2D con semilla, determinista y portable (no usa math.noise de Roblox).
-- Todas las cuentas intermedias se mantienen < 2^53 para ser exactas en Lua y Luau.
local Noise = {}
local M = 2147483647

local function hash(ix, iy, seed)
	local h = (ix * 73856093 + iy * 19349663 + seed * 83492791) % M
	h = (h * 16807 + 12345) % M
	h = (h * 48271) % M
	return h / M
end

local function smooth(t) return t * t * (3 - 2 * t) end

-- seed debe ser un entero chico (< 65537).
function Noise.value(x, y, seed)
	local x0, y0 = math.floor(x), math.floor(y)
	local fx, fy = smooth(x - x0), smooth(y - y0)
	local a, b = hash(x0, y0, seed), hash(x0 + 1, y0, seed)
	local c, d = hash(x0, y0 + 1, seed), hash(x0 + 1, y0 + 1, seed)
	local top, bot = a + (b - a) * fx, c + (d - c) * fx
	return top + (bot - top) * fy
end

function Noise.fbm(x, y, seed, octaves, lacunarity, gain)
	octaves, lacunarity, gain = octaves or 4, lacunarity or 2, gain or 0.5
	local amp, freq, sum, norm = 1, 1, 0, 0
	for i = 1, octaves do
		sum = sum + Noise.value(x * freq, y * freq, seed + i * 101) * amp
		norm = norm + amp
		amp, freq = amp * gain, freq * lacunarity
	end
	return sum / norm
end

return Noise
