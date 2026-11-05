-- Cañon del lobby: al activar el aviso del cañon (E, toque o mando) pide el lanzamiento al servidor; y cuando alguien sale disparado
-- (efecto "lanzamiento" junto al cañon) el «Cañón pajarero» de Codex hace su retroceso: el clip Launch_recoil de Blender, en
-- src/ClipsEquipo.lua. Sus piezas estan ancladas y unidas a RootPart con Motor6D (asi las monto el 3D Importer): mientras dura el clip,
-- en este cliente, se apagan los Motor6D de las piezas que se mueven y cada una va a raiz * D * C0 * C1:Inverse(); al acabar vuelven
-- a su sitio y se encienden. El retroceso SIN PROBAR EN STUDIO (05/11: sin permiso de pantalla para el Studio nuevo).
local PPS, Players, RS, RunService = game:GetService("ProximityPromptService"), game:GetService("Players"), game:GetService("ReplicatedStorage"),
	game:GetService("RunService")
local Mas1 = RS:WaitForChild("Mas1")
local Red = require(Mas1:WaitForChild("Red"))
local Clips = require(Mas1:WaitForChild("Clips"))
local accion = Red.evento("MAS1_Accion")
local efecto = Red.evento("MAS1_Efecto")
local plr = Players.LocalPlayer
PPS.PromptTriggered:Connect(function(prompt, jugador)
	if jugador == plr and prompt.Parent and prompt.Parent.Name == "MAS1_Canon" and plr:GetAttribute("EnVuelo") ~= true then
		accion:FireServer("lanzar")
	end
end)

local moduloEquipo = Mas1:FindFirstChild("ClipsEquipo")
local equipo = moduloEquipo and require(moduloEquipo)
local clipsCanon = equipo and Clips.preparar(equipo.clips.Canon)
local RETROCESO = clipsCanon and clipsCanon.Launch_recoil
local PIEZAS = equipo and equipo.piezas.Canon or {}
local CERCA_CANON = 60 -- studs: un lanzamiento a esta distancia del cañon sale de el
local enMarcha = false

local function retroceso(canon)
	local raiz = canon.PrimaryPart
	if not raiz or enMarcha then return end
	local mover = {} -- { motor, pieza, reposo (respecto a la raiz), fotogramas }
	for _, m in ipairs(canon:GetDescendants()) do
		if m:IsA("Motor6D") and m.Part0 == raiz and m.Part1 then
			local f = RETROCESO.huesos[PIEZAS[m.Part1.Name] or ""]
			if f then mover[#mover + 1] = { m = m, p = m.Part1, reposo = m.C0 * m.C1:Inverse(), f = f } end
		end
	end
	if #mover == 0 then return end
	enMarcha = true
	local escala = canon:GetScale()
	for _, x in ipairs(mover) do x.m.Enabled = false end
	local t0 = os.clock()
	local con
	con = RunService.RenderStepped:Connect(function()
		local t = os.clock() - t0
		local fase = math.min(t / RETROCESO.dur, 1) * (RETROCESO.n - 1)
		local i = math.floor(fase)
		local a = fase - i
		for _, x in ipairs(mover) do
			local d = x.f[i + 1]:Lerp(x.f[math.min(i + 2, RETROCESO.n)], a)
			x.p.CFrame = raiz.CFrame * (d - d.Position + d.Position * escala) * x.reposo
		end
		if t >= RETROCESO.dur then
			con:Disconnect()
			for _, x in ipairs(mover) do
				x.p.CFrame = raiz.CFrame * x.reposo
				x.m.Enabled = true
			end
			enMarcha = false
		end
	end)
end

efecto.OnClientEvent:Connect(function(tipo, pos)
	if tipo ~= "lanzamiento" or not RETROCESO or typeof(pos) ~= "Vector3" then return end
	local lobby = workspace:FindFirstChild("MAS1_Lobby")
	local canon = lobby and lobby:FindFirstChild("CanonPajarero")
	if canon and canon.PrimaryPart and (canon.PrimaryPart.Position - pos).Magnitude < CERCA_CANON then retroceso(canon) end
end)
