-- Mascotas que te siguen y alas puestas de «+1 de lanzamiento por segundo» (todo en el cliente, para todos los jugadores).
-- Lee los atributos del jugador: MascotasEq (ids separados por coma, hasta 3) y Alas (id equipado). Si existen las mallas importadas en
-- ReplicatedStorage.MAS1_Modelos.Mascotas.<id> / .Alas.<id>, las usa; si no, dibuja piezas provisionales con el color de su rareza.
-- Las mascotas flotan alrededor y detras, con balanceo; en vuelo se acercan y se agrupan. SIN PROBAR EN STUDIO.
local Players, RS, RunService = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService")
local Mas1 = RS:WaitForChild("Mas1")
local M = require(Mas1:WaitForChild("Mascotas"))
local COLOR = { comun = Color3.fromRGB(190, 190, 200), poco_comun = Color3.fromRGB(110, 210, 120), raro = Color3.fromRGB(80, 160, 255),
	epico = Color3.fromRGB(170, 100, 255), legendario = Color3.fromRGB(255, 190, 40), mitico = Color3.fromRGB(255, 80, 140), robux = Color3.fromRGB(255, 120, 40) }
local ALAS_COLOR = { iniciales = Color3.fromRGB(245, 235, 210), roboticas = Color3.fromRGB(235, 240, 250), avanzadas = Color3.fromRGB(32, 36, 70) }

local function modelos(carpeta, id)
	local m = RS:FindFirstChild("MAS1_Modelos")
	local c = m and m:FindFirstChild(carpeta)
	return c and c:FindFirstChild(id)
end

local estado = {} -- [plr] = { mascotas = {{id, modelo}}, alas = modelo, idAlas, clave }

local function pieza(tam, color, forma)
	local p = Instance.new("Part")
	p.Size, p.Color, p.Material = tam, color, Enum.Material.SmoothPlastic
	p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery, p.Massless = true, false, false, false, true
	if forma then p.Shape = forma end
	return p
end

local function nuevaMascota(id)
	local d = M.get(id)
	local plantilla = modelos("Mascotas", id)
	local m
	if plantilla then
		m = plantilla:Clone()
	else -- provisional: bola con ojos y el color de la rareza
		m = Instance.new("Model")
		local cuerpo = pieza(Vector3.new(2.2, 2.2, 2.2), COLOR[d and d.rareza or "comun"], Enum.PartType.Ball)
		cuerpo.Name = "Cuerpo"
		cuerpo.Parent = m
		for _, dx in ipairs({ -0.5, 0.5 }) do
			local o = pieza(Vector3.new(0.35, 0.35, 0.2), Color3.fromRGB(28, 21, 48))
			o.CFrame = CFrame.new(dx, 0.3, -1.05)
			o.Parent = m
			o:SetAttribute("rel", true)
		end
		m.PrimaryPart = cuerpo
	end
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery, p.Massless = true, false, false, false, true end
	end
	m.Name = "Mas1Mascota_" .. id
	m.Parent = workspace
	return m
end

local function nuevasAlas(id)
	local plantilla = modelos("Alas", id)
	local m
	if plantilla then
		m = plantilla:Clone()
	else -- provisional: dos alas de cuña
		m = Instance.new("Model")
		local c = ALAS_COLOR[id] or Color3.fromRGB(240, 240, 240)
		for i, lado in ipairs({ -1, 1 }) do
			local a = pieza(Vector3.new(0.3, 4, 3), c)
			a.Name = i == 1 and "AlaI" or "AlaD"
			a.Parent = m
		end
		m.PrimaryPart = m:FindFirstChildWhichIsA("BasePart")
	end
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery, p.Massless = true, false, false, false, true end
	end
	m.Name = "Mas1Alas"
	m.Parent = workspace
	return m
end

local function limpiar(plr)
	local e = estado[plr]
	if not e then return end
	for _, x in ipairs(e.mascotas) do x.modelo:Destroy() end
	if e.alas then e.alas:Destroy() end
	estado[plr] = nil
end

local function sincronizar(plr)
	local clave = (plr:GetAttribute("MascotasEq") or "") .. "|" .. (plr:GetAttribute("Alas") or "")
	local e = estado[plr]
	if e and e.clave == clave then return end
	limpiar(plr)
	e = { mascotas = {}, clave = clave, idAlas = plr:GetAttribute("Alas") or "" }
	for id in string.gmatch(plr:GetAttribute("MascotasEq") or "", "[^,]+") do
		if #e.mascotas < M.MAX_EQUIPADAS and M.get(id) then e.mascotas[#e.mascotas + 1] = { id = id, modelo = nuevaMascota(id) } end
	end
	if e.idAlas ~= "" then e.alas = nuevasAlas(e.idAlas) end
	estado[plr] = e
end

RunService.RenderStepped:Connect(function(dt)
	local t = os.clock()
	for _, plr in ipairs(Players:GetPlayers()) do
		local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
		if not hrp then limpiar(plr) continue end
		sincronizar(plr)
		local e = estado[plr]
		if not e then continue end
		local vuela = plr:GetAttribute("EnVuelo") == true
		local boost = plr:GetAttribute("Boost") == true
		-- mascotas: arco detras y arriba; en vuelo, mas pegadas y alineadas con la direccion
		local n = #e.mascotas
		for i, x in ipairs(e.mascotas) do
			local ang = (i - (n + 1) / 2) * 0.9
			local radio = vuela and 5 or 6
			local alto = 2.5 + math.sin(t * 2.2 + i * 1.7) * 0.5 + (vuela and 1 or 0)
			local off = Vector3.new(math.sin(ang) * radio, alto, math.cos(ang) * radio * (vuela and 1.4 or 0.9))
			local objetivo = hrp.CFrame * CFrame.new(off) * CFrame.Angles(0, math.rad(vuela and 0 or 180), 0)
			local actual = x.modelo:GetPivot()
			x.modelo:PivotTo(actual:Lerp(objetivo, 1 - math.exp(-(boost and 14 or 9) * dt)))
		end
		-- alas: pegadas a la espalda; aletean al volar
		if e.alas then
			local torso = plr.Character:FindFirstChild("UpperTorso") or plr.Character:FindFirstChild("Torso") or hrp
			local abre = vuela and (0.35 + (boost and 0.35 or 0.15) * math.sin(t * (boost and 14 or 7))) or 0.15 + 0.03 * math.sin(t * 1.5)
			local base = torso.CFrame * CFrame.new(0, 0.4, 0.7)
			if e.alas.PrimaryPart and #e.alas:GetChildren() == 2 and not modelos("Alas", e.idAlas) then
				local ai, ad = e.alas:FindFirstChild("AlaI"), e.alas:FindFirstChild("AlaD")
				if ai then ai.CFrame = base * CFrame.new(-2, 0, 0) * CFrame.Angles(0, 0, -abre) end
				if ad then ad.CFrame = base * CFrame.new(2, 0, 0) * CFrame.Angles(0, 0, abre) end
			else
				e.alas:PivotTo(base)
			end
		end
	end
end)

Players.PlayerRemoving:Connect(limpiar)
