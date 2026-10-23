-- PROVISIONAL (solo para probar el disparo antes de tener el zombi): maniquies de bloques con nombres de piezas R15, vida 100 y la etiqueta "Zombi".
local Collection = game:GetService("CollectionService")
local COLOR = Color3.fromRGB(150, 160, 140)

local function pieza(modelo, nombre, tam, pos, forma)
	local p = Instance.new("Part"); p.Name = nombre; p.Size = tam; p.Position = pos; p.Anchored = true; p.Color = COLOR
	p.Material = Enum.Material.SmoothPlastic; if forma then p.Shape = forma end; p.Parent = modelo; return p
end

local function crear(base)
	local m = Instance.new("Model"); m.Name = "Maniqui"
	pieza(m, "Head", Vector3.new(1.6, 1.6, 1.6), base + Vector3.new(0, 4.6, 0), Enum.PartType.Ball)
	pieza(m, "UpperTorso", Vector3.new(2, 1.6, 1), base + Vector3.new(0, 3.4, 0))
	pieza(m, "LowerTorso", Vector3.new(2, 0.9, 1), base + Vector3.new(0, 2.15, 0))
	pieza(m, "HumanoidRootPart", Vector3.new(2, 2, 1), base + Vector3.new(0, 3, 0)).Transparency = 1
	pieza(m, "LeftUpperArm", Vector3.new(1, 1.4, 1), base + Vector3.new(-1.5, 3.5, 0))
	pieza(m, "RightUpperArm", Vector3.new(1, 1.4, 1), base + Vector3.new(1.5, 3.5, 0))
	pieza(m, "LeftUpperLeg", Vector3.new(1, 2, 1), base + Vector3.new(-0.5, 1, 0))
	pieza(m, "RightUpperLeg", Vector3.new(1, 2, 1), base + Vector3.new(0.5, 1, 0))
	local h = Instance.new("Humanoid"); h.MaxHealth = 100; h.Health = 100; h.Parent = m
	Collection:AddTag(m, "Zombi"); m.Parent = workspace
	h.Died:Connect(function() task.wait(1.5); m:Destroy(); task.wait(3); crear(base) end)
end

for i = -2, 1 do crear(Vector3.new(i * 7 + 3.5, 0, -30)) end
