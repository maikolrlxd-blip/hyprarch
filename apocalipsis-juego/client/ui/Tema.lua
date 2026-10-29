-- Tema visual de Luto (estilo Poli Pintado): paneles oscuros con esquinas ambar, tipografia condensada, colores apagados y sucios.
-- Todo se construye por codigo (sin imagenes). Modulo de cliente; SIN PROBAR EN STUDIO.
local TweenService = game:GetService("TweenService")
local Tema = {}

Tema.col = {
	fondo = Color3.fromRGB(22, 23, 27), linea = Color3.fromRGB(91, 93, 99), txt = Color3.fromRGB(232, 228, 216), mut = Color3.fromRGB(154, 151, 140),
	rojo = Color3.fromRGB(179, 58, 58), ambar = Color3.fromRGB(227, 185, 92), verde = Color3.fromRGB(111, 157, 98), negro = Color3.fromRGB(14, 14, 16),
}
Tema.fuente = Enum.Font.Oswald

local function n(clase, props, padre)
	local o = Instance.new(clase)
	for k, v in pairs(props or {}) do o[k] = v end
	if padre then o.Parent = padre end
	return o
end
Tema.n = n

function Tema.escala(gui) -- UIScale segun la altura de la pantalla (movil y escritorio)
	local sc = n("UIScale", {}, gui)
	local function ajustar()
		local cam = workspace.CurrentCamera
		if cam then sc.Scale = math.clamp(cam.ViewportSize.Y / 900, 0.6, 1.5) end
	end
	ajustar()
	if workspace.CurrentCamera then workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(ajustar) end
	return sc
end

-- Esquina en L (ambar) para los paneles
local function esquina(panel, arriba, izq)
	local ax, ay = izq and 0 or 1, arriba and 0 or 1
	local col = Tema.col.ambar
	n("Frame", { Size = UDim2.fromOffset(14, 2), AnchorPoint = Vector2.new(ax, ay), Position = UDim2.new(ax, izq and -3 or 3, ay, arriba and -3 or 3), BackgroundColor3 = col, BorderSizePixel = 0 }, panel)
	n("Frame", { Size = UDim2.fromOffset(2, 14), AnchorPoint = Vector2.new(ax, ay), Position = UDim2.new(ax, izq and -3 or 3, ay, arriba and -3 or 3), BackgroundColor3 = col, BorderSizePixel = 0 }, panel)
end

function Tema.panel(padre, props)
	props = props or {}
	props.BackgroundColor3 = props.BackgroundColor3 or Tema.col.fondo
	props.BackgroundTransparency = props.BackgroundTransparency or 0.15
	props.BorderSizePixel = 0
	local p = n("Frame", props, padre)
	n("UIStroke", { Color = Tema.col.linea, Thickness = 1, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, p)
	esquina(p, true, true); esquina(p, false, false)
	return p
end

function Tema.etiqueta(padre, props)
	props = props or {}
	props.BackgroundTransparency = 1
	props.Font = props.Font or Tema.fuente
	props.TextColor3 = props.TextColor3 or Tema.col.txt
	props.TextSize = props.TextSize or 18
	props.Text = props.Text and string.upper(props.Text) or ""
	return n("TextLabel", props, padre)
end

function Tema.barra(padre, props)
	local marco = n("Frame", props, padre)
	marco.BackgroundColor3 = Tema.col.negro; marco.BorderSizePixel = 0
	n("UIStroke", { Color = Color3.new(0, 0, 0), Thickness = 1 }, marco)
	local relleno = n("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = Tema.col.verde, BorderSizePixel = 0 }, marco)
	local b = { marco = marco, relleno = relleno }
	function b.set(p, color)
		p = math.clamp(p, 0, 1)
		TweenService:Create(relleno, TweenInfo.new(0.18, Enum.EasingStyle.Quad), { Size = UDim2.fromScale(p, 1) }):Play()
		if color then relleno.BackgroundColor3 = color end
	end
	return b
end

-- Verde > 60 %, ambar 30-60 %, rojo < 30 %
function Tema.colorVida(p)
	if p > 0.6 then return Tema.col.verde elseif p > 0.3 then return Tema.col.ambar else return Tema.col.rojo end
end

return Tema
