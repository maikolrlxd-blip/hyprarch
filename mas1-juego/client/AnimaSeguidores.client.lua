-- Aleteo de las mallas de mascotas y alas que pone client/Seguidores.client.lua (modelos «Mas1Mascota_<id>» y «Mas1Alas» del
-- Workspace, sacados de ReplicatedStorage.MAS1_Modelos). Todavia no hay ids de Animation subidas, asi que mueve los huesos de las
-- alas (Wing_, Mid_, Tip_) con Bone.Transform: el eje de giro es el frente del modelo visto desde cada hueso, y el signo sale del lado
-- en que queda el hueso (las alas de Codex llaman R al lado izquierdo). Las mascotas aletean siempre; las alas del jugador, en vuelo
-- (mas con turbo) y casi quietas en tierra. Los modelos de piezas provisionales no tienen huesos: no se tocan.
local Players, RunService = game:GetService("Players"), game:GetService("RunService")
local cache = setmetatable({}, { __mode = "k" }) -- [modelo] = { huesos = {{hueso, eje, lado, retraso}}, fase }

local function preparar(m)
	local piv = m:GetPivot()
	local lista = {}
	for _, b in ipairs(m:GetDescendants()) do
		if b:IsA("Bone") and (b.Name:match("^Wing_") or b.Name:match("^Mid_") or b.Name:match("^Tip_")) then
			lista[#lista + 1] = {
				hueso = b,
				eje = b.WorldCFrame:VectorToObjectSpace(piv.LookVector), -- con Transform aun sin tocar
				lado = (b.WorldPosition - piv.Position):Dot(piv.RightVector) >= 0 and 1 or -1, -- +: baja el ala derecha
				retraso = b.Name:match("^Tip_") and 0.7 or b.Name:match("^Mid_") and 0.35 or 0, -- la punta va detras del hombro
			}
		end
	end
	return { huesos = lista, fase = math.random() * 2 * math.pi }
end

local function duenoDe(m) -- las alas van pegadas a la espalda de su jugador
	local p = m:GetPivot().Position
	for _, plr in ipairs(Players:GetPlayers()) do
		local c = plr.Character
		local t = c and (c:FindFirstChild("UpperTorso") or c:FindFirstChild("Torso") or c:FindFirstChild("HumanoidRootPart"))
		if t and (t.Position - p).Magnitude < 6 then return plr end
	end
end

RunService.RenderStepped:Connect(function()
	local t = os.clock()
	for _, m in ipairs(workspace:GetChildren()) do
		local mascota = m.Name:sub(1, 12) == "Mas1Mascota_"
		if m:IsA("Model") and (mascota or m.Name == "Mas1Alas") then
			local c = cache[m]
			if not c then
				c = preparar(m)
				cache[m] = c
			end
			if #c.huesos > 0 then
				local amp, frec
				if mascota then
					amp, frec = math.rad(32), 2.2
				else
					local dueno = duenoDe(m)
					local vuela = dueno and dueno:GetAttribute("EnVuelo") == true
					local boost = dueno and dueno:GetAttribute("Boost") == true
					if vuela then
						amp, frec = math.rad(boost and 30 or 20), boost and 2.6 or 1.4
					else
						amp, frec = math.rad(4), 0.5
					end
				end
				for _, h in ipairs(c.huesos) do
					local a = amp * (h.retraso > 0 and 0.6 or 1) * math.sin(t * frec * 2 * math.pi + c.fase - h.retraso)
					h.hueso.Transform = CFrame.fromAxisAngle(h.eje, h.lado * a)
				end
			end
		end
	end
end)
