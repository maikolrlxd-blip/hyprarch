-- Generado por tools/exportar_viewmodel_roblox.py: no editar a mano.
-- Barra de comandos de Studio, con el Model importado de Escopeta_VM_Roblox.fbx SELECCIONADO.
-- Lo deja como plantilla del viewmodel en ReplicatedStorage.LUTO_VM.escopeta: PrimaryPart "Raiz" en la camara (origen),
-- una pieza invisible "Camara" y un Motor6D por hueso (los clips son KeyframeSequence con esos mismos nombres).
local m = game:GetService("Selection"):Get()[1]
assert(m and m:IsA("Model"), "Selecciona el Model importado del viewmodel")
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Name = d.Name:gsub("^%s+", ""):gsub("%s+$", "") end end
m.Name = "escopeta"
local function pieza(n) local p = m:FindFirstChild(n, true); assert(p, "falta la pieza " .. n); return p end
-- el importador 3D de Studio deja las mallas giradas 180 grados en Y respecto a Blender (comprobado el 2026-10-23 con el mapa,
-- la zombi y estos viewmodels): se deshace girando las piezas alrededor del eje vertical de "Arma"
do local c = pieza("Arma").Position; local rot = CFrame.new(c.X, 0, c.Z) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-c.X, 0, -c.Z)
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.CFrame = rot * d.CFrame end end end
-- el importador puede mover el modelo: se alinea con el centro esperado de "Arma"
local off = pieza("Arma").Position - Vector3.new(0.32000, -0.68000, -1.45960)
local U = {
	Camara = CFrame.new(0.00000, 0.00000, 0.00000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Arma = CFrame.new(0.32000, -0.58000, -0.70000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Bomba = CFrame.new(0.32000, -0.61636, -2.28788, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Cerrojo = CFrame.new(0.36990, -0.48303, -1.25354, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Gatillo = CFrame.new(0.32000, -0.72141, -1.01515, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Cartucho = CFrame.new(0.32000, -0.61636, -1.26566, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Casquillo = CFrame.new(0.32000, -0.65273, -1.29394, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	RightUpperArm = CFrame.new(0.90000, -1.05000, 0.70000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	RightLowerArm = CFrame.new(1.21941, -1.52753, -0.46616, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	RightHand = CFrame.new(0.37000, -0.68000, -0.48000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	LeftUpperArm = CFrame.new(-0.85000, -1.05000, -0.20000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	LeftLowerArm = CFrame.new(-0.75923, -1.53948, -1.40090, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	LeftHand = CFrame.new(0.06000, -0.89000, -1.99000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
}
for _, d in ipairs(m:GetDescendants()) do
	if d:IsA("BasePart") then d.Anchored = false; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true; d.CastShadow = false end
end
local function aux(nombre, marco) local p = Instance.new("Part"); p.Name = nombre; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Transparency = 1
	p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Massless = true; p.CastShadow = false; p.CFrame = marco; p.Parent = m; return p end
local raiz = aux("Raiz", CFrame.new(off))           -- la camara: ejes de Roblox sin giro (mira a -Z)
aux("Camara", U.Camara + off)
local function motor(hijo, padre_)
	local a, b = (padre_ and pieza(padre_) or raiz), pieza(hijo)
	local j = U[hijo] + off
	local mt = Instance.new("Motor6D"); mt.Name = hijo; mt.Part0 = a; mt.Part1 = b
	mt.C0 = a.CFrame:Inverse() * j; mt.C1 = b.CFrame:Inverse() * j; mt.Parent = b
end
motor("Camara", nil)
motor("Arma", "Camara")
motor("Bomba", "Arma")
motor("Cerrojo", "Arma")
motor("Gatillo", "Arma")
motor("Cartucho", "Arma")
motor("Casquillo", "Arma")
motor("RightUpperArm", "Arma")
motor("RightLowerArm", "RightUpperArm")
motor("RightHand", "RightLowerArm")
motor("LeftUpperArm", "Arma")
motor("LeftLowerArm", "LeftUpperArm")
motor("LeftHand", "LeftLowerArm")
raiz.Anchored = true                                 -- en la plantilla; el script del juego lo desancla y lo pega a la camara
m.PrimaryPart = raiz; m.WorldPivot = raiz.CFrame
local ctl = m:FindFirstChildOfClass("AnimationController") or Instance.new("AnimationController", m)
if not ctl:FindFirstChildOfClass("Animator") then Instance.new("Animator", ctl) end
local RS = game:GetService("ReplicatedStorage")
local carpeta = RS:FindFirstChild("LUTO_VM") or Instance.new("Folder"); carpeta.Name = "LUTO_VM"; carpeta.Parent = RS
local viejo = carpeta:FindFirstChild("escopeta"); if viejo and viejo ~= m then viejo.Parent = game:GetService("ServerStorage") end
m.Parent = carpeta
print("LUTO_VM.escopeta listo:", #m:GetDescendants(), "descendientes")
