-- Ejecutar en la barra de comandos de Studio con el Model importado de LaLamentadora_Estatico.fbx SELECCIONADO.
-- Lo deja como rig R15: HumanoidRootPart invisible, Motor6D en cada articulacion (nombres R15) y Humanoid R15.
-- Luego se mueve a ServerStorage.LUTO_Plantillas. Generado por tools/build_zombi.py.
local m = game:GetService("Selection"):Get()[1]
assert(m and m:IsA("Model"), "Selecciona el Model importado de la zombi")
m.Name = "Jefe_lamentadora"
local off = m:FindFirstChild("UpperTorso", true).Position - Vector3.new(-0.061, 7.472, -0.132)  -- donde lo dejo el importador
local J = {
	HumanoidRootPart = Vector3.new(0.000, 5.163, -0.000),
	LowerTorso = Vector3.new(0.000, 5.163, -0.000),
	UpperTorso = Vector3.new(0.000, 6.125, -0.000),
	Head = Vector3.new(-0.079, 8.803, -0.367),
	LeftUpperArm = Vector3.new(-1.181, 7.700, -0.257),
	LeftLowerArm = Vector3.new(-1.474, 5.621, 0.095),
	LeftHand = Vector3.new(-1.663, 3.778, -0.047),
	RightUpperArm = Vector3.new(1.059, 7.700, -0.257),
	RightLowerArm = Vector3.new(1.474, 5.621, 0.095),
	RightHand = Vector3.new(1.663, 3.778, -0.047),
	LeftUpperLeg = Vector3.new(-0.543, 5.110, -0.000),
	LeftLowerLeg = Vector3.new(-0.438, 2.835, -0.035),
	LeftFoot = Vector3.new(-0.403, 0.525, 0.035),
	RightUpperLeg = Vector3.new(0.543, 5.110, -0.000),
	RightLowerLeg = Vector3.new(0.438, 2.835, -0.035),
	RightFoot = Vector3.new(0.403, 0.525, 0.035),
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
h.HipHeight = 4.163  -- de la base del HumanoidRootPart al suelo
h.Parent = m
m.PrimaryPart = hrp
print("Jefe_lamentadora lista como R15")
