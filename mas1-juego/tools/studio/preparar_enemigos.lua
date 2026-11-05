-- Barra de comandos de Studio (modo edición), después de importar los FBX de los enemigos con el 3D Importer (uno a uno; cada modelo
-- se llama como su archivo: globo, nube, nubarron, cometa, ovni, meteorito, y queda en Workspace). Para cada uno:
--   1. lo gira sobre la vertical para que su cara (párpado Lid_R respecto a Body) mire a -Z, el frente que espera client/Entidades;
--   2. pone el pivote en el centro de su caja, con los ejes del mundo;
--   3. ancla las piezas y lo mete en ReplicatedStorage.MAS1_Enemigos.
-- Después: Ctrl+S y python tools/extraer_rbxmx.py build/Mas1-prueba.rbxlx ReplicatedStorage/MAS1_Enemigos assets/MAS1_Enemigos.rbxmx
-- (ver PUNTO-DE-RETOMA.md). Se pega entero en la barra de comandos y se ejecuta con Ctrl+Enter.
local RS = game:GetService("ReplicatedStorage")
local carpeta = RS:FindFirstChild("MAS1_Enemigos") or Instance.new("Folder")
carpeta.Name = "MAS1_Enemigos"
carpeta.Parent = RS
for _, tipo in ipairs({ "globo", "nube", "nubarron", "cometa", "ovni", "meteorito" }) do
	local m = workspace:FindFirstChild(tipo)
	if not (m and m:IsA("Model")) then
		print("FALTA", tipo)
		continue
	end
	local lid, body = m:FindFirstChild("Lid_R", true), m:FindFirstChild("Body", true)
	local parte = m.PrimaryPart or m:FindFirstChildWhichIsA("MeshPart", true)
	m.PrimaryPart = parte
	if lid and body then
		local f = lid.WorldPosition - body.WorldPosition
		local yaw = math.atan2(-f.X, -f.Z) -- CFrame.Angles(0, yaw, 0).LookVector apunta a la cara
		local p = m:GetPivot().Position
		m:PivotTo(CFrame.new(p) * CFrame.Angles(0, -yaw, 0) * CFrame.new(-p) * m:GetPivot())
	end
	local caja = m:GetBoundingBox()
	parte.PivotOffset = parte.CFrame:ToObjectSpace(CFrame.new(caja.Position))
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then d.Anchored = true end
	end
	m:PivotTo(CFrame.new())
	m.Parent = carpeta
	local cara = lid and body and (lid.WorldPosition - body.WorldPosition):Dot(m:GetPivot().LookVector) or 0
	print("LISTO", tipo, "cara hacia -Z:", cara > 0, "tamaño", m:GetExtentsSize())
end
