-- Reproduce en Bone.Transform los clips de Blender que convierte mas1-arte/tools/clips_a_lua.py: src/ClipsHuesos.lua (mascotas y
-- alas) y src/ClipsEnemigos.lua (enemigos). Cada clip trae n fotogramas a 15 por segundo y, por hueso animado, 7 numeros por fotograma
-- (posicion en studs a escala 1 y cuaternion), ya en los ejes de los huesos de Roblox. Lo usan client/AnimaSeguidores.client.lua y
-- client/Entidades.client.lua.
local Clips = {}
local preparados = setmetatable({}, { __mode = "k" }) -- [datos de una pieza] = sus clips con los fotogramas en CFrame

-- los clips de una pieza ({ Clip = { n, dur, huesos } }) con cada fotograma en CFrame; se calcula una vez por tabla de datos
function Clips.preparar(datos)
	if not datos then return nil end
	local listo = preparados[datos]
	if listo then return listo end
	listo = {}
	for nombre, clip in pairs(datos) do
		local huesos = {}
		for hueso, v in pairs(clip.huesos) do
			local lista = {}
			for i = 0, clip.n - 1 do
				local k = i * 7
				lista[i + 1] = CFrame.new(v[k + 1], v[k + 2], v[k + 3], v[k + 4], v[k + 5], v[k + 6], v[k + 7])
			end
			huesos[hueso] = lista
		end
		listo[nombre] = { n = clip.n, dur = clip.dur, huesos = huesos }
	end
	preparados[datos] = listo
	return listo
end

-- los huesos de un modelo por su nombre
function Clips.huesos(modelo)
	local t = {}
	for _, b in ipairs(modelo:GetDescendants()) do
		if b:IsA("Bone") then t[b.Name] = b end
	end
	return t
end

-- pone el clip en el instante t (segundos). bucle: vuelve a empezar al acabar; si no, se queda en el ultimo fotograma. escala: la del
-- modelo (Model:GetScale()), que agranda los desplazamientos. encima: solo toca los huesos que trae el clip (el parpadeo sobre el
-- reposo); sin el, los huesos sin datos vuelven a su postura de reposo
function Clips.aplicar(huesos, clip, t, escala, bucle, encima)
	if not clip then return end
	local avance = bucle and (t % clip.dur) / clip.dur or math.clamp(t / clip.dur, 0, 1)
	local fase = avance * (clip.n - 1)
	local i = math.floor(fase)
	local a = fase - i
	for nombre, hueso in pairs(huesos) do
		local lista = clip.huesos[nombre]
		if lista then
			local cf = lista[i + 1]:Lerp(lista[math.min(i + 2, clip.n)], a)
			hueso.Transform = escala == 1 and cf or (cf - cf.Position + cf.Position * escala)
		elseif not encima then
			hueso.Transform = CFrame.identity
		end
	end
end

return Clips
