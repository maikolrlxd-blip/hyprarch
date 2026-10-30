-- Control del vuelo en el cliente de «+1 de lanzamiento por segundo». El cliente mueve su propio personaje (asi responde al instante)
-- con src/Manejo.lua; el servidor (server/Partida.server.lua) lleva la energia, el boost y los puntos, y devuelve atras al que vaya
-- mas rapido de lo permitido. Aqui tambien van la camara de persecucion (se aleja con la velocidad, abre el campo de vision con el
-- boost y se inclina un poco en los giros), un boton LANZAR y un cartel de resultado PROVISIONALES (la interfaz buena la hace
-- Claude nube con MAS1_Resultado y los atributos de CONTRATO.md).
-- Mandos: W o joystick arriba = boost; A/D = a los lados; Espacio o salto = subir; S, Ctrl o joystick abajo = bajar;
-- F o el boton LANZAR = lanzarse (en el suelo). Golpear: clic o los botones del HUD (client/HudVuelo.client.lua). SIN PROBAR EN STUDIO.
local Players, RS, RunService, UIS = game:GetService("Players"), game:GetService("ReplicatedStorage"), game:GetService("RunService"), game:GetService("UserInputService")
local plr = Players.LocalPlayer
local Mas1 = RS:WaitForChild("Mas1")
local V = require(Mas1:WaitForChild("Vuelo"))
local Manejo = require(Mas1:WaitForChild("Manejo"))
local Red = require(Mas1:WaitForChild("Red"))
local T = require(script.Parent:WaitForChild("Tema"))
local accion = Red.evento("MAS1_Accion")
local C = V.CFG
local cam = workspace.CurrentCamera

-- mandos: el modulo de control de Roblox da el mismo vector con teclado, joystick de movil y mando
local controles
task.spawn(function()
	local ok, pm = pcall(function() return require(plr:WaitForChild("PlayerScripts"):WaitForChild("PlayerModule")) end)
	if ok and pm then controles = pm:GetControls() end
end)
local ultimoSalto = 0
UIS.JumpRequest:Connect(function() ultimoSalto = os.clock() end) -- Espacio y boton de salto del movil y del mando

local function mandos()
	local mv = controles and controles:GetMoveVector() or Vector3.zero
	return {
		lateral = math.clamp(mv.X, -1, 1),
		boost = mv.Z < -0.5,
		bajar = mv.Z > 0.5 or UIS:IsKeyDown(Enum.KeyCode.LeftControl),
		subir = UIS:IsKeyDown(Enum.KeyCode.Space) or os.clock() - ultimoSalto < 0.25,
	}
end

-- vuelo: el personaje en estado Physics, con una velocidad lineal y una orientacion que se fijan cada fotograma
local vuelo
local esperaFin = false -- aterrizo aqui: no volver a empezar hasta que el servidor cierre el vuelo
local camPos, fov = nil, 70

local function empezar()
	local char = plr.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	if not (hum and hrp) or hum.Health <= 0 then return end
	hum:ChangeState(Enum.HumanoidStateType.Physics)
	hum.AutoRotate = false
	local att = Instance.new("Attachment")
	att.Name = "Mas1Vuelo"
	att.Parent = hrp
	local lv = Instance.new("LinearVelocity")
	lv.Attachment0 = att
	lv.MaxForce = math.huge
	lv.RelativeTo = Enum.ActuatorRelativeTo.World
	lv.VelocityConstraintMode = Enum.VelocityConstraintMode.Vector
	lv.VectorVelocity = Vector3.zero
	lv.Parent = hrp
	local ao = Instance.new("AlignOrientation")
	ao.Mode = Enum.OrientationAlignmentMode.OneAttachment
	ao.Attachment0 = att
	ao.MaxTorque = math.huge
	ao.Responsiveness = 30
	ao.CFrame = hrp.CFrame.Rotation
	ao.Parent = hrp
	vuelo = { m = Manejo.nuevo(), att = att, lv = lv, ao = ao, hum = hum, hrp = hrp, boost = false }
	camPos = nil
	cam.CameraType = Enum.CameraType.Scriptable
end

local function terminar()
	if not vuelo then return end
	vuelo.lv:Destroy()
	vuelo.ao:Destroy()
	vuelo.att:Destroy()
	if vuelo.hum.Parent and vuelo.hum.Health > 0 then
		vuelo.hum.AutoRotate = true
		vuelo.hum:ChangeState(Enum.HumanoidStateType.GettingUp)
	end
	if vuelo.boost then accion:FireServer("boost", false) end
	vuelo = nil
	cam.CameraType = Enum.CameraType.Custom
	cam.FieldOfView = 70
	fov = 70
end

RunService:BindToRenderStep("Mas1Vuelo", Enum.RenderPriority.Camera.Value + 1, function(dt)
	local enVuelo = plr:GetAttribute("EnVuelo") == true
	if not enVuelo then esperaFin = false end
	if enVuelo and not vuelo and not esperaFin then empezar() end
	if not enVuelo and vuelo then terminar() end
	if not vuelo then return end
	if not vuelo.hrp.Parent or vuelo.hum.Health <= 0 then terminar() return end
	local e = mandos()
	if e.boost ~= vuelo.boost then
		vuelo.boost = e.boost
		accion:FireServer("boost", e.boost)
	end
	local info = { planeando = plr:GetAttribute("Planeando") == true, boost = plr:GetAttribute("Boost") == true,
		impulso = plr:GetAttribute("Impulso") or 1 }
	local p = vuelo.hrp.Position
	local m = Manejo.paso(vuelo.m, dt, e, info, p.X, p.Y, C)
	vuelo.lv.VectorVelocity = Vector3.new(m.vx, m.vy, -m.vf)
	-- tumbado hacia delante (como un superheroe), mirando hacia donde va y alabeado en los giros
	local dir = Vector3.new(m.vx * 0.3, m.vy * 0.3, -math.max(m.vf, 1)).Unit
	vuelo.ao.CFrame = CFrame.lookAt(Vector3.zero, dir) * CFrame.Angles(0, 0, m.alabeo) * CFrame.Angles(math.rad(-65) + m.cabeceo, 0, 0)
	-- camara: detras y por encima, mas lejos cuanto mas rapido
	local objetivo = p + Vector3.new(0, 1.5, 0)
	local deseo = objetivo + Vector3.new(-m.vx * 0.12 + 3, 3 + m.vf * 0.01, 13 + m.vf * 0.06) -- baja y algo de lado: se ve el cuerpo tumbado
	camPos = camPos and camPos:Lerp(deseo, 1 - math.exp(-8 * dt)) or deseo
	fov += ((info.boost and 88 or info.planeando and 66 or 74) - fov) * (1 - math.exp(-4 * dt))
	cam.FieldOfView = fov
	cam.CFrame = CFrame.lookAt(camPos, objetivo + Vector3.new(m.vx * 0.2, 0, -16)) * CFrame.Angles(0, 0, m.alabeo * 0.2)
	if info.planeando and p.Y < C.suelo + 3.3 then -- toco el suelo: el servidor cierra el vuelo y paga
		terminar()
		esperaFin = true
	end
end)

-- boton LANZAR y tecla F (PROVISIONAL hasta el cañon de la Pradera)
local gui = T.n("ScreenGui", { Name = "Mas1Lanzar", ResetOnSpawn = false, IgnoreGuiInset = true }, plr:WaitForChild("PlayerGui"))
T.escala(gui)
local function pedirLanzar()
	if plr:GetAttribute("EnVuelo") ~= true then accion:FireServer("lanzar") end
end
local boton = T.boton(gui, { Size = UDim2.fromOffset(260, 100), AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -40),
	Text = "¡LANZAR!" }, T.col.rosa, pedirLanzar)
local function verBoton() boton.Visible = plr:GetAttribute("EnVuelo") ~= true end
plr:GetAttributeChangedSignal("EnVuelo"):Connect(verBoton)
verBoton()
UIS.InputBegan:Connect(function(i, gp)
	if not gp and i.KeyCode == Enum.KeyCode.F then pedirLanzar() end
end)

-- el cartel de resultado vive en client/Resultados.client.lua
