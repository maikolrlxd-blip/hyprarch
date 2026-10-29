-- Viewmodel de primera persona de Luto: brazos + arma (modelo de Blender) pegados a la camara, con las animaciones publicadas
-- (src/Animaciones.lua). Plantillas en ReplicatedStorage.LUTO_VM: Model "pistola", "escopeta", "subfusil" (PrimaryPart "Raiz" en el origen
-- de la camara y un AnimationController con Animator; ver apocalipsis-arte/tools/exportar_viewmodel_roblox.py). El Tool de tercera persona
-- lo pone el servidor. Probado en Studio el 2026-10-23.
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
-- Desplazamiento del viewmodel respecto a la camara (X derecha, Y arriba, -Z delante) sobre la colocacion de Blender: mas abajo, a la
-- derecha y algo mas lejos para que no tape el centro de la pantalla (Maikol, 2026-10-23). Para probar otros valores en Play sin
-- reiniciar: atributo Vector3 "LUTO_VMOffset" del LocalPlayer (manda sobre esta tabla).
local OFFSET = {
	pistola = Vector3.new(0.5, -0.38, -0.4),
	escopeta = Vector3.new(0.15, -0.08, -0.15),
	subfusil = Vector3.new(0.15, -0.08, -0.15),
}
local actual = nil -- { id, modelo, pistas, partes, visible }

local function quitar() if actual then actual.modelo:Destroy(); actual = nil end end

local function mostrar(visible)
	actual.visible = visible
	for _, p in ipairs(actual.partes) do p.LocalTransparencyModifier = visible and 0 or 1 end
end

local function colocar(id)
	quitar()
	local carpeta = RS:FindFirstChild("LUTO_VM"); local tpl = carpeta and carpeta:FindFirstChild(id)
	if not tpl then return end
	local m = tpl:Clone()
	local partes = {}
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = false; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true; d.CastShadow = false
			local clave = COLORES[d.Name]; if clave then d.Color = Color3.fromRGB(table.unpack(Apariencia.BASE[clave])) end
			partes[#partes + 1] = d
		end
	end
	if not m.PrimaryPart then m.PrimaryPart = m:FindFirstChildWhichIsA("BasePart", true) end
	-- la raiz anclada: suelta, la fisica la hacia caer, acumulaba velocidad aunque se recolocara cada fotograma y Roblox acababa
	-- borrandola por debajo del mapa (el arma "desaparecia de la nada")
	m.PrimaryPart.Anchored = true
	m:PivotTo(cam.CFrame)
	m.Parent = cam -- antes de cargar las pistas: el Animator solo las carga dentro del juego
	local animator = m:FindFirstChildWhichIsA("Animator", true)
	if not animator then
		local ctl = m:FindFirstChildOfClass("AnimationController") or Instance.new("AnimationController", m)
		animator = Instance.new("Animator", ctl)
	end
	local pistas = {}
	for nombre, aid in pairs(Animaciones[id] or {}) do
		if aid ~= "" then
			local a = Instance.new("Animation"); a.AnimationId = aid
			local ok, pista = pcall(function() return animator:LoadAnimation(a) end)
			if ok then pista.Priority = PRIORIDAD[nombre] or Enum.AnimationPriority.Action; pistas[nombre] = pista
			else warn("LUTO viewmodel: no se pudo cargar " .. id .. "." .. nombre .. ": " .. tostring(pista)) end
		end
	end
	if pistas.Reposo then pistas.Reposo.Looped = true; pistas.Reposo:Play() end
	actual = { id = id, modelo = m, pistas = pistas, partes = partes, visible = true }
end

REstado.OnClientEvent:Connect(function(s) if s.arma and (not actual or actual.id ~= s.arma) then colocar(s.arma) end end)

RAnim.OnClientEvent:Connect(function(d)
	if not actual or typeof(d) ~= "table" then return end
	local pista = actual.pistas[d.clip]; if not pista then return end
	for nombre, p in pairs(actual.pistas) do if nombre ~= "Reposo" and p ~= pista then p:Stop(0.05) end end
	pista:Play(0.03)
end)

-- Solo en primera persona: el viewmodel sigue a la camara y se ocultan el cuerpo y el arma del personaje (la camara en tercera persona ve
-- el Tool). En tercera persona el viewmodel se esconde sin sacarlo del juego: asi sus pistas siguen cargadas.
RunService:BindToRenderStep("LutoViewmodel", Enum.RenderPriority.Camera.Value + 1, function()
	cam = workspace.CurrentCamera
	local primera = (cam.Focus.Position - cam.CFrame.Position).Magnitude < 1.5
	if actual then
		if actual.modelo.Parent ~= cam then actual.modelo.Parent = cam end
		if primera ~= actual.visible then mostrar(primera) end
		if primera then
			local o = plr:GetAttribute("LUTO_VMOffset")
			if typeof(o) ~= "Vector3" then o = OFFSET[actual.id] or Vector3.zero end
			actual.modelo:PivotTo(cam.CFrame * CFrame.new(o))
		end
	end
	local ch = plr.Character
	if ch and actual and primera then
		for _, d in ipairs(ch:GetDescendants()) do if d:IsA("BasePart") then d.LocalTransparencyModifier = 1 end end
	end
end)
