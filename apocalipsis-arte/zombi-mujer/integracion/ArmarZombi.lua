-- Ejecutar en la barra de comandos de Studio con el Model importado de ZombiMujer_Estatico.fbx SELECCIONADO.
-- Lo deja como rig R15: HumanoidRootPart invisible, Motor6D en cada articulacion (nombres R15) y Humanoid R15.
-- Luego se mueve a ServerStorage.LUTO_Plantillas. Generado por tools/build_zombi.py.
local m = game:GetService("Selection"):Get()[1]
assert(m and m:IsA("Model"), "Selecciona el Model importado de la zombi")
m.Name = "Zombi_Mujer"
local off = m:FindFirstChild("UpperTorso", true).Position - Vector3.new(0.000, 4.181, -0.078)  -- donde lo dejo el importador
local J = {
	HumanoidRootPart = Vector3.new(0.000, 2.950, -0.000),
	LowerTorso = Vector3.new(0.000, 2.950, -0.000),
	UpperTorso = Vector3.new(0.000, 3.500, -0.000),
	Head = Vector3.new(0.000, 4.900, -0.020),
	LeftUpperArm = Vector3.new(-0.640, 4.400, -0.000),
	LeftLowerArm = Vector3.new(-0.790, 3.520, 0.040),
	LeftHand = Vector3.new(-0.870, 2.740, -0.020),
	RightUpperArm = Vector3.new(0.640, 4.400, -0.000),
	RightLowerArm = Vector3.new(0.790, 3.520, 0.040),
	RightHand = Vector3.new(0.870, 2.740, -0.020),
	LeftUpperLeg = Vector3.new(-0.310, 2.920, -0.000),
	LeftLowerLeg = Vector3.new(-0.250, 1.620, -0.020),
	LeftFoot = Vector3.new(-0.230, 0.300, 0.020),
	RightUpperLeg = Vector3.new(0.310, 2.920, -0.000),
	RightLowerLeg = Vector3.new(0.250, 1.620, -0.020),
	RightFoot = Vector3.new(0.230, 0.300, 0.020),
}
local hrp = Instance.new("Part")
hrp.Name = "HumanoidRootPart"; hrp.Size = Vector3.new(2, 2, 1); hrp.Transparency = 1; hrp.CanCollide = false
hrp.CFrame = CFrame.new(J.HumanoidRootPart + off); hrp.Parent = m
for _, d in ipairs(m:GetDescendants()) do
	if d:IsA("BasePart") then d.Anchored = false; d.CanCollide = false end
end
local function motor(nombre, p0, p1, junta)
	local a, b = m:FindFirstChild(p0, true), m:FindFirstChild(p1, true)
	local j = CFrame.new(junta + off)
	local mt = Instance.new("Motor6D")
	mt.Name = nombre; mt.Part0 = a; mt.Part1 = b; mt.C0 = a.CFrame:Inverse() * j; mt.C1 = b.CFrame:Inverse() * j
	mt.Parent = b
end
motor("Root", "HumanoidRootPart", "LowerTorso", J.LowerTorso)
motor("Waist", "LowerTorso", "UpperTorso", J.UpperTorso)
motor("Neck", "UpperTorso", "Head", J.Head)
motor("LeftShoulder", "UpperTorso", "LeftUpperArm", J.LeftUpperArm)
motor("LeftElbow", "LeftUpperArm", "LeftLowerArm", J.LeftLowerArm)
motor("LeftWrist", "LeftLowerArm", "LeftHand", J.LeftHand)
motor("RightShoulder", "UpperTorso", "RightUpperArm", J.RightUpperArm)
motor("RightElbow", "RightUpperArm", "RightLowerArm", J.RightLowerArm)
motor("RightWrist", "RightLowerArm", "RightHand", J.RightHand)
motor("LeftHip", "LowerTorso", "LeftUpperLeg", J.LeftUpperLeg)
motor("LeftKnee", "LeftUpperLeg", "LeftLowerLeg", J.LeftLowerLeg)
motor("LeftAnkle", "LeftLowerLeg", "LeftFoot", J.LeftFoot)
motor("RightHip", "LowerTorso", "RightUpperLeg", J.RightUpperLeg)
motor("RightKnee", "RightUpperLeg", "RightLowerLeg", J.RightLowerLeg)
motor("RightAnkle", "RightLowerLeg", "RightFoot", J.RightFoot)
local h = Instance.new("Humanoid")
h.RigType = Enum.HumanoidRigType.R15
h.HipHeight = 1.950  -- de la base del HumanoidRootPart al suelo
h.Parent = m
m.PrimaryPart = hrp
print("Zombi_Mujer lista como R15")
