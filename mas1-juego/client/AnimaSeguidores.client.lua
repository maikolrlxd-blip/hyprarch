-- Animacion de las mallas de mascotas y alas que pone client/Seguidores.client.lua (modelos «Mas1Mascota_<id>» y «Mas1Alas» del
-- Workspace, sacados de ReplicatedStorage.MAS1_Modelos) con los clips DE VERDAD de Blender: src/ClipsHuesos.lua, generado por
-- mas1-arte/tools/clips_a_lua.py, guarda el Bone.Transform de cada hueso animado (15 fotogramas por segundo), ya pasado a los ejes
-- de los huesos de Roblox (no son los de Blender), y aqui se pone interpolando. Sin publicar una Animation por clip. Maikol (01/11):
-- con el aleteo inventado «las alas solo se mueven adelante y atras, abrazando al jugador»; ahora es el Flap de Blender (recoger ->
-- extender -> impulsar). Comprobado en Studio: Roblox compone CFrame * Transform, como supone clips_a_lua.py.
-- Mascotas: Fly siempre. Alas del jugador: Flap en vuelo (mas rapido con turbo), Glide al planear y, en tierra, Glide despacio (alas
-- abiertas, no pegadas al cuerpo). Los modelos de piezas provisionales no tienen huesos: no se tocan.
local Players, RS, RunService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService")
local Mas1 = RS:WaitForChild("Mas1")
local Clips = require(Mas1:WaitForChild("Clips"))
local CLIPS = require(Mas1:WaitForChild("ClipsHuesos"))
local cache = setmetatable({}, { __mode = "k" }) -- [modelo] = { id, huesos = {nombre = Bone}, clips = {clip = preparado} }

local function duenoDe(m) -- las alas van pegadas a la espalda de su jugador
	local p = m:GetPivot().Position
	for _, plr in ipairs(Players:GetPlayers()) do
		local c = plr.Character
		local t = c and (c:FindFirstChild("UpperTorso") or c:FindFirstChild("Torso") or c:FindFirstChild("HumanoidRootPart"))
		if t and (t.Position - p).Magnitude < 6 then return plr end
	end
end

local function aplicar(c, clip, t, escala) -- en bucle; los huesos sin datos en el clip vuelven a reposo
	Clips.aplicar(c.huesos, c.clips[clip], t, escala, true)
end

RunService.RenderStepped:Connect(function()
	local reloj = os.clock()
	for _, m in ipairs(workspace:GetChildren()) do
		local mascota = m.Name:sub(1, 12) == "Mas1Mascota_"
		if m:IsA("Model") and (mascota or m.Name == "Mas1Alas") then
			local c = cache[m]
			local dueno = not mascota and duenoDe(m) or nil
			local id = mascota and m.Name:sub(13) or (dueno and dueno:GetAttribute("Alas")) or nil
			if not c or c.id ~= id then
				c = { id = id, huesos = Clips.huesos(m), clips = id and Clips.preparar(CLIPS[id]), fase = math.random() * 3 }
				cache[m] = c
			end
			if c.clips and next(c.huesos) then
				local escala = m:GetScale()
				if mascota then
					aplicar(c, "Fly", reloj + c.fase, escala)
				else
					local vuela = dueno and dueno:GetAttribute("EnVuelo") == true
					if vuela and dueno:GetAttribute("Planeando") then
						aplicar(c, "Glide", reloj, escala)
					elseif vuela then
						aplicar(c, "Flap", reloj * (dueno:GetAttribute("Boost") and 1.6 or 1), escala)
					else
						aplicar(c, "Glide", reloj * 0.5, escala)
					end
				end
			end
		end
	end
end)
