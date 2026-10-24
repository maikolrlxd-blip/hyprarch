-- Generado por tools/exportar_viewmodel_roblox.py: no editar a mano.
-- Barra de comandos de Studio, con el Model importado de Pistola9mm_Mundo_Estatico.fbx SELECCIONADO.
-- Lo deja como Tool "pistola" en ReplicatedStorage.LUTO_Armas (Handle + piezas soldadas; Grip en el punto de agarre).
local m = game:GetService("Selection"):Get()[1]
assert(m and m:IsA("Model"), "Selecciona el Model importado del arma de mundo")
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Name = d.Name:gsub("^%s+", ""):gsub("%s+$", "") end end
local h = m:FindFirstChild("Handle", true); assert(h, "falta Handle")
-- el importador 3D deja las mallas giradas 180 grados en Y (ver ArmarVM): se deshace alrededor del eje vertical del Handle
do local c = h.Position; local rot = CFrame.new(c.X, 0, c.Z) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-c.X, 0, -c.Z)
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.CFrame = rot * d.CFrame end end end
local origen = h.Position - Vector3.new(-0.0004, -0.1024, -0.4488)   -- punto de agarre (origen del FBX), desde eventos.json
local tool = Instance.new("Tool"); tool.Name = "pistola"; tool.RequiresHandle = true; tool.CanBeDropped = false; tool.ToolTip = "Pistola9mm"
for _, d in ipairs(m:GetDescendants()) do
	if d:IsA("BasePart") then
		d.Anchored = false; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true
		local cf = d.CFrame; d.Parent = tool; d.CFrame = cf
		if d ~= h then local w = Instance.new("WeldConstraint"); w.Part0 = h; w.Part1 = d; w.Parent = d end
	end
end
tool.Grip = h.CFrame:ToObjectSpace(CFrame.new(origen))
local RS = game:GetService("ReplicatedStorage")
local carpeta = RS:FindFirstChild("LUTO_Armas") or Instance.new("Folder"); carpeta.Name = "LUTO_Armas"; carpeta.Parent = RS
local viejo = carpeta:FindFirstChild("pistola"); if viejo then viejo.Parent = game:GetService("ServerStorage") end
tool.Parent = carpeta; m.Parent = nil
print("LUTO_Armas.pistola listo: piezas", #tool:GetChildren(), "Grip", tool.Grip)
