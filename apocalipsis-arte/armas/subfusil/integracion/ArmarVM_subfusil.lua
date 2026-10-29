-- Generado por tools/exportar_viewmodel_roblox.py: no editar a mano.
-- Barra de comandos de Studio, con el Model importado de Subfusil_VM_Roblox.fbx SELECCIONADO.
-- Lo deja como plantilla del viewmodel en ReplicatedStorage.LUTO_VM.subfusil: PrimaryPart "Raiz" en la camara (origen),
-- una pieza invisible "Camara" y un Motor6D por hueso (los clips son KeyframeSequence con esos mismos nombres).
local m = game:GetService("Selection"):Get()[1]
assert(m and m:IsA("Model"), "Selecciona el Model importado del viewmodel")
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Name = d.Name:gsub("^%s+", ""):gsub("%s+$", "") end end
m.Name = "subfusil"
local function pieza(n) local p = m:FindFirstChild(n, true); assert(p, "falta la pieza " .. n); return p end
-- el importador 3D de Studio deja las mallas giradas 180 grados en Y respecto a Blender (comprobado el 2026-10-23 con el mapa,
-- la zombi y estos viewmodels): se deshace girando las piezas alrededor del eje vertical de "Arma"
do local c = pieza("Arma").Position; local rot = CFrame.new(c.X, 0, c.Z) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-c.X, 0, -c.Z)
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.CFrame = rot * d.CFrame end end end
-- el importador puede mover el modelo: se alinea con el centro esperado de "Arma"
local off = pieza("Arma").Position - Vector3.new(0.36000, -0.64585, -1.30115)
local U = {
	Camara = CFrame.new(0.00000, 0.00000, 0.00000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Arma = CFrame.new(0.36000, -0.86000, -1.00000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Cargador = CFrame.new(0.36000, -0.59231, -1.50862, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Palanca = CFrame.new(0.21277, -0.36923, -1.39262, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Cerrojo = CFrame.new(0.48715, -0.37369, -1.50415, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Gatillo = CFrame.new(0.36000, -0.64585, -1.29446, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	Casquillo = CFrame.new(0.36000, -0.38708, -1.39262, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	RightUpperArm = CFrame.new(0.90000, -1.00000, 0.90000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	RightLowerArm = CFrame.new(1.05926, -1.44166, -0.14979, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	RightHand = CFrame.new(0.40000, -0.96000, -0.81000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	LeftUpperArm = CFrame.new(-0.85000, -1.00000, 0.10000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	LeftLowerArm = CFrame.new(-0.68821, -1.34291, -0.98570, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
	LeftHand = CFrame.new(0.04000, -0.71000, -1.40000, 1.00000, 0.00000, 0.00000, 0.00000, 0.00000, 1.00000, 0.00000, -1.00000, 0.00000),
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
motor("Cargador", "Arma")
motor("Palanca", "Arma")
motor("Cerrojo", "Arma")
motor("Gatillo", "Arma")
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
local viejo = carpeta:FindFirstChild("subfusil"); if viejo and viejo ~= m then viejo.Parent = game:GetService("ServerStorage") end
m.Parent = carpeta
print("LUTO_VM.subfusil listo:", #m:GetDescendants(), "descendientes")
