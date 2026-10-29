-- Disparo real de Luto: direccion de cada bala (con dispersion), zona del cuerpo por nombre de pieza y agujeros de bala. Modulo PURO.
local Disparo = {}

-- Vectores como tablas {x=,y=,z=}.
local function norm(v) local m = math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z); if m < 1e-9 then return { x = 0, y = 0, z = -1 } end return { x = v.x / m, y = v.y / m, z = v.z / m } end
local function cross(a, b) return { x = a.y * b.z - a.z * b.y, y = a.z * b.x - a.x * b.z, z = a.x * b.y - a.y * b.x } end

-- Direccion de una bala: aim (unitario) desviado 'yaw' y 'pitch' GRADOS respecto a la punteria (los entrega Weapons:fire).
function Disparo.direccion(aim, yaw, pitch)
	aim = norm(aim)
	local up = math.abs(aim.y) > 0.99 and { x = 1, y = 0, z = 0 } or { x = 0, y = 1, z = 0 }
	local right = norm(cross(aim, up)); local up2 = cross(right, aim)
	local ty, tp = math.tan(math.rad(yaw)), math.tan(math.rad(pitch))
	return norm({ x = aim.x + right.x * ty + up2.x * tp, y = aim.y + right.y * ty + up2.y * tp, z = aim.z + right.z * ty + up2.z * tp })
end

-- Zona del cuerpo segun el nombre de la pieza (R15 y R6).
local ZONAS = {
	Head = "cabeza",
	UpperTorso = "torso", LowerTorso = "torso", HumanoidRootPart = "torso", Torso = "torso",
	LeftUpperArm = "brazo", LeftLowerArm = "brazo", LeftHand = "brazo", RightUpperArm = "brazo", RightLowerArm = "brazo", RightHand = "brazo",
	["Left Arm"] = "brazo", ["Right Arm"] = "brazo",
	LeftUpperLeg = "pierna", LeftLowerLeg = "pierna", LeftFoot = "pierna", RightUpperLeg = "pierna", RightLowerLeg = "pierna", RightFoot = "pierna",
	["Left Leg"] = "pierna", ["Right Leg"] = "pierna",
}
function Disparo.zona(nombrePieza) return ZONAS[nombrePieza] or "torso" end -- accesorios y piezas desconocidas cuentan como torso

-- Agujeros de bala: lo que se dibuja DONDE da la bala (en paredes, suelo y tambien una marca en el enemigo).
Disparo.AGUJERO = {
	tam = { pistola = 0.45, escopeta = 0.3, subfusil = 0.38 }, -- diametro en studs
	vida_mapa = 40, vida_enemigo = 1.5, max_mapa = 150, max_enemigo = 40,
	color_centro = { 18, 18, 20 }, color_borde = { 70, 68, 66 }, borde = 1.6, -- el borde (astillado) es 1,6 veces el hueco
	-- marca en el enemigo: pequena, oscura y pegada al cuerpo; se borra en 1,5 s (antes era casi tan grande como la cabeza)
	factor_enemigo = 0.4, borde_enemigo = 1.35, centro_enemigo = { 55, 8, 12 }, borde_color_enemigo = { 85, 14, 18 },
}
function Disparo.agujero(weaponId, sobreEnemigo)
	local a = Disparo.AGUJERO
	local tam = (a.tam[weaponId] or 0.4) * (sobreEnemigo and a.factor_enemigo or 1)
	return { tam = tam, borde = sobreEnemigo and a.borde_enemigo or a.borde, vida = sobreEnemigo and a.vida_enemigo or a.vida_mapa,
		color_centro = sobreEnemigo and a.centro_enemigo or a.color_centro, color_borde = sobreEnemigo and a.borde_color_enemigo or a.color_borde }
end

return Disparo
