-- PROVISIONAL y SIN PROBAR EN STUDIO. Viewmodel de primera persona de Luto: brazos + arma (modelo de Blender) pegados a la camara, con las
-- animaciones publicadas (src/Animaciones.lua). Plantillas esperadas en ReplicatedStorage.LUTO_VM: Model "pistola", "escopeta", "subfusil"
-- (con su Animator/AnimationController). Si falta la plantilla o los ids, se ve sin animar o no se muestra. El Tool de tercera persona lo pone el servidor.
local RS, RunService, Players = game:GetService("ReplicatedStorage"), game:GetService("RunService"), game:GetService("Players")
local StarterGui = game:GetService("StarterGui")
local plr = Players.LocalPlayer
pcall(function() StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack, false) end) -- el cambio de arma es con 1/2/3
local Luto = RS:WaitForChild("Luto")
local Animaciones, Apariencia = require(Luto.Animaciones), require(Luto.Apariencia)
local REstado, RAnim = RS:WaitForChild("LUTO_Estado"), RS:WaitForChild("LUTO_Anim")
local cam = workspace.CurrentCamera

local COLORES = { LeftUpperArm = "manga", LeftLowerArm = "manga", RightUpperArm = "manga", RightLowerArm = "manga", LeftHand = "piel", RightHand = "piel" }
local PRIORIDAD = { Reposo = Enum.AnimationPriority.Idle }
local actual = nil -- { id, modelo, pistas, reposo }

local function quitar() if actual then actual.modelo:Destroy(); actual = nil end end

local function colocar(id)
	quitar()
	local carpeta = RS:FindFirstChild("LUTO_VM"); local tpl = carpeta and carpeta:FindFirstChild(id)
	if not tpl then return end
	local m = tpl:Clone()
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = false; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true; d.CastShadow = false
			local clave = COLORES[d.Name]; if clave then d.Color = Color3.fromRGB(table.unpack(Apariencia.BASE[clave])) end
		end
	end
	if not m.PrimaryPart then m.PrimaryPart = m:FindFirstChildWhichIsA("BasePart", true) end
	local animator = m:FindFirstChildOfClass("Animator", true) or m:FindFirstChildWhichIsA("Animator", true)
	if not animator then
		local ctl = m:FindFirstChildOfClass("AnimationController") or m:FindFirstChildOfClass("Humanoid") or Instance.new("AnimationController", m)
		animator = ctl:FindFirstChildOfClass("Animator") or Instance.new("Animator", ctl)
	end
	local pistas = {}
	for nombre, aid in pairs(Animaciones[id] or {}) do
		if aid ~= "" then
			local a = Instance.new("Animation"); a.AnimationId = aid
			local ok, pista = pcall(function() return animator:LoadAnimation(a) end)
			if ok then pista.Priority = PRIORIDAD[nombre] or Enum.AnimationPriority.Action; pistas[nombre] = pista end
		end
	end
	if pistas.Reposo then pistas.Reposo.Looped = true; pistas.Reposo:Play() end
	m.Parent = cam
	actual = { id = id, modelo = m, pistas = pistas }
end

REstado.OnClientEvent:Connect(function(s) if s.arma and (not actual or actual.id ~= s.arma) then colocar(s.arma) end end)

RAnim.OnClientEvent:Connect(function(d)
	if not actual or typeof(d) ~= "table" then return end
	local pista = actual.pistas[d.clip]; if not pista then return end
	for nombre, p in pairs(actual.pistas) do if nombre ~= "Reposo" and p ~= pista then p:Stop(0.05) end end
	pista:Play(0.03)
end)

-- Solo en primera persona: el viewmodel sigue a la camara y se ocultan el cuerpo y el arma del personaje (la camara en tercera persona ve el Tool).
RunService:BindToRenderStep("LutoViewmodel", Enum.RenderPriority.Camera.Value + 1, function()
	cam = workspace.CurrentCamera
	local primera = (cam.Focus.Position - cam.CFrame.Position).Magnitude < 1.5
	if actual then
		actual.modelo.Parent = primera and cam or nil
		if primera and actual.modelo.PrimaryPart then actual.modelo:PivotTo(cam.CFrame) end -- el origen del modelo es la camara (ver datos.json: viewmodel_origen_arma_desde_camara)
	end
	local ch = plr.Character
	if ch and actual and primera then
		for _, d in ipairs(ch:GetDescendants()) do if d:IsA("BasePart") then d.LocalTransparencyModifier = 1 end end
	end
end)
