-- Barra de comandos de Studio. Corrige el giro de 180 grados en Y con el que el importador 3D de Studio deja los FBX de apocalipsis-arte
-- (exportados con ejes -Z delante / Y arriba): comprobado el 2026-10-23. Los Parts creados por script (colisiones, marcadores,
-- HumanoidRootPart, Raiz) estaban bien y las mallas giradas: el almacen visual salia en (-82, -56) con su colision en (82, 46) y la
-- zombi miraba hacia atras de su HumanoidRootPart (andaba de espaldas).
-- Gira cada MeshPart 180 grados alrededor del eje vertical de una pieza de referencia y recalcula los Motor6D para que las
-- articulaciones (marcos de union) no se muevan: las animaciones publicadas siguen valiendo. No hace nada si el modelo ya tiene el
-- atributo Girado180. Los scripts nuevos de montaje (exportar_viewmodel_roblox.py) ya incluyen la correccion.
local function girar(modelo, ref)
	if modelo:GetAttribute("Girado180") then return "ya" end
	local c = ref.Position
	local rot = CFrame.new(c.X, 0, c.Z) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-c.X, 0, -c.Z)
	local J, motores = {}, {}
	for _, m in ipairs(modelo:GetDescendants()) do
		if m:IsA("Motor6D") and m.Part0 and m.Part1 then J[m] = m.Part0.CFrame * m.C0; motores[#motores + 1] = m; m.Enabled = false end
	end
	local n = 0
	for _, p in ipairs(modelo:GetDescendants()) do
		if p:IsA("MeshPart") then p.CFrame = rot * p.CFrame; n = n + 1 end
	end
	for _, m in ipairs(motores) do local j = J[m]; m.C0 = m.Part0.CFrame:Inverse() * j; m.C1 = m.Part1.CFrame:Inverse() * j; m.Enabled = true end
	modelo:SetAttribute("Girado180", true)
	return n .. "p/" .. #motores .. "m"
end
local P, RS, o = game:GetService("ServerStorage").LUTO_Plantillas, game:GetService("ReplicatedStorage"), {}
o[#o + 1] = "Mapa " .. girar(P.Mapa, P.Mapa:FindFirstChild("Calle_Cruce_60_01", true))
for _, n in ipairs({ "Zombi_Mujer", "Jefe_lamentadora", "Jefe_alta" }) do
	local z = P:FindFirstChild(n); if z then o[#o + 1] = n .. " " .. girar(z, z:FindFirstChild("UpperTorso", true)) end
end
-- plantillas de armas montadas con los scripts viejos (sin la correccion incluida)
local vm = RS:FindFirstChild("LUTO_VM")
if vm then for _, v in ipairs(vm:GetChildren()) do o[#o + 1] = "VM." .. v.Name .. " " .. girar(v, v:FindFirstChild("Arma")) end end
local armas = RS:FindFirstChild("LUTO_Armas")
if armas then
	for _, t in ipairs(armas:GetChildren()) do
		if not t:GetAttribute("GripCorregido") then
			local g = t.Grip.Position; t.Grip = CFrame.new(-g.X, g.Y, -g.Z) * CFrame.Angles(0, math.pi, 0); t:SetAttribute("GripCorregido", true)
		end
		o[#o + 1] = "Tool." .. t.Name .. " grip " .. tostring(t.Grip.Position)
	end
end
print("LUTO girar180:", table.concat(o, " | "))
