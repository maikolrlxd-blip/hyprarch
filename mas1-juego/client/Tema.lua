-- Tema de interfaz de «+1 de lanzamiento por segundo»: paneles gruesos con contorno oscuro y sombra dura, colores vivos, tipografia redondeada.
-- Todo por codigo, sin imagenes. SIN PROBAR EN STUDIO.
local TweenService = game:GetService("TweenService")
local T = {}
T.col = {
	tinta = Color3.fromRGB(28, 21, 48), crema = Color3.fromRGB(255, 247, 224), sol = Color3.fromRGB(255, 210, 63), cielo = Color3.fromRGB(78, 200, 255),
	menta = Color3.fromRGB(61, 220, 151), rosa = Color3.fromRGB(255, 93, 143), violeta = Color3.fromRGB(124, 92, 255), morado = Color3.fromRGB(58, 44, 99),
}
T.fuente = Enum.Font.FredokaOne

local function n(clase, props, padre)
	local o = Instance.new(clase); for k, v in pairs(props or {}) do o[k] = v end; if padre then o.Parent = padre end; return o
end
T.n = n

function T.escala(gui)
	local sc = n("UIScale", {}, gui)
	local function aj() local cam = workspace.CurrentCamera; if cam then sc.Scale = math.clamp(cam.ViewportSize.Y / 900, 0.55, 1.4) end end
	aj(); if workspace.CurrentCamera then workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(aj) end
end

-- Panel con contorno oscuro (UIStroke 5), esquinas redondeadas y sombra dura debajo
function T.panel(padre, props, color)
	props = props or {}
	local sombra = n("Frame", { Size = props.Size, Position = props.Position, AnchorPoint = props.AnchorPoint, BackgroundColor3 = T.col.tinta, BorderSizePixel = 0 }, padre)
	sombra.Position = props.Position + UDim2.fromOffset(0, 7); n("UICorner", { CornerRadius = UDim.new(0, 18) }, sombra)
	props.BackgroundColor3 = color or T.col.violeta; props.BorderSizePixel = 0
	local p = n("Frame", props, padre)
	n("UICorner", { CornerRadius = UDim.new(0, 18) }, p); n("UIStroke", { Color = T.col.tinta, Thickness = 5, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, p)
	p.Destroying:Connect(function() sombra:Destroy() end)
	return p, sombra
end

function T.texto(padre, props)
	props = props or {}; props.BackgroundTransparency = 1; props.Font = props.Font or T.fuente
	props.TextColor3 = props.TextColor3 or T.col.crema; props.TextSize = props.TextSize or 24
	props.TextStrokeColor3 = props.TextStrokeColor3 or T.col.tinta; props.TextStrokeTransparency = props.TextStrokeTransparency or 0.55
	return n("TextLabel", props, padre)
end

function T.barra(padre, props)
	local marco = n("Frame", props, padre); marco.BackgroundColor3 = T.col.morado; marco.BorderSizePixel = 0; marco.ClipsDescendants = true
	n("UICorner", { CornerRadius = UDim.new(0, 18) }, marco); n("UIStroke", { Color = T.col.tinta, Thickness = 5 }, marco)
	local relleno = n("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = T.col.sol, BorderSizePixel = 0 }, marco)
	n("UICorner", { CornerRadius = UDim.new(0, 14) }, relleno)
	local b = { marco = marco, relleno = relleno }
	function b.set(p, color)
		TweenService:Create(relleno, TweenInfo.new(0.15, Enum.EasingStyle.Quad), { Size = UDim2.fromScale(math.clamp(p, 0, 1), 1) }):Play()
		if color then relleno.BackgroundColor3 = color end
	end
	return b
end

-- Boton redondo grande (movil): llama a alAplastar al pulsarlo y se hunde unos pixeles
function T.boton(padre, props, color, alAplastar)
	local b = n("TextButton", props, padre); b.BackgroundColor3 = color; b.AutoButtonColor = false; b.BorderSizePixel = 0; b.Font = T.fuente
	b.TextColor3 = T.col.crema; b.TextStrokeColor3 = T.col.tinta; b.TextStrokeTransparency = 0.4; b.TextScaled = true
	n("UICorner", { CornerRadius = UDim.new(1, 0) }, b); n("UIStroke", { Color = T.col.tinta, Thickness = 6 }, b)
	b.MouseButton1Down:Connect(function() b.Size = b.Size - UDim2.fromOffset(6, 6); if alAplastar then alAplastar() end end)
	b.MouseButton1Up:Connect(function() b.Size = props.Size end)
	return b
end

return T
