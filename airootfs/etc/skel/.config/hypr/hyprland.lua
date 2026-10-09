-- hyprarch · Hyprland 0.55+ (configuración en Lua)
-- Neón verde / carmesí sobre fondo casi negro.
-- Los colores salen de colors.lua, que genera el comando `hyprarch-theme` (SUPER+T).

-------------------------------------------------------------
-- Interruptores rápidos
-------------------------------------------------------------
local ROTATING_BORDER = true   -- borde con degradado que gira (más "neón"; gasta algo más de batería)

-------------------------------------------------------------
-- Modo activo: normal | gamer | cine | estudio | trabajo   (lo cambia `hyprarch-mode`)
-- Cada modo cambia animaciones, efectos y espacios; los colores y el fondo los pone el tema.
-------------------------------------------------------------
local MODE = "normal"
do
    local f = io.open((os.getenv("HOME") or "") .. "/.config/hyprarch/mode", "r")
    if f then
        local m = (f:read("l") or ""):match("^%s*([a-z]+)%s*$")
        f:close()
        if m then MODE = m end
    end
end
-- dur: multiplica la duración de las animaciones (menos = más rápido)
local PRESETS = {
    -- normal = "fresco": más aire entre ventanas, borde finísimo, sombra suave en vez de neón, resortes con rebote
    normal  = { dur = 1.0,  blur = true,  shadow = true,  glow = false, spring = true,  rotate = false, gaps_in = 7, gaps_out = 20, border = 1 },
    gamer   = { dur = 0.55, blur = false, shadow = false, glow = false, spring = false, rotate = false, gaps_in = 4, gaps_out = 8,  border = 2 },
    cine    = { dur = 2.2,  blur = true,  shadow = true,  glow = false, spring = false, rotate = false, gaps_in = 0, gaps_out = 0,  border = 0 },
    estudio = { dur = 1.5,  blur = true,  shadow = true,  glow = false, spring = false, rotate = false, gaps_in = 6, gaps_out = 16, border = 1 },
    trabajo = { dur = 0.8,  blur = false, shadow = true,  glow = false, spring = false, rotate = false, gaps_in = 4, gaps_out = 8,  border = 2 },
}
-- Equipos modestos: el perfil "lite" (lo decide hyprarch-perf según RAM, procesador y gráfica, o la elección de la persona)
-- quita desenfoque, sombras y brillos y acorta las animaciones SOLO en el modo normal; los equipos buenos no cambian.
PRESETS.lite = { dur = 0.55, blur = false, shadow = false, glow = false, spring = false, rotate = false, gaps_in = 4, gaps_out = 10, border = 1 }
local PERF = "full"
do
    local f = io.open((os.getenv("HOME") or "") .. "/.config/hyprarch/perf.effective", "r")
    if f then
        PERF = (f:read("l") or "full"):match("^%s*(%a+)") or "full"
        f:close()
    end
end
local P = PRESETS[MODE] or PRESETS.normal
if PERF == "lite" and MODE == "normal" then P = PRESETS.lite end

-- Idioma: distribución de teclado elegida con hyprarch-lang (archivo "capa [variante]"); por defecto latam + es + us
local KB_LAYOUT, KB_VARIANT = "latam,es,us", ""
do
    local f = io.open((os.getenv("HOME") or "") .. "/.config/hyprarch/keyboard", "r")
    if f then
        local l, v = (f:read("l") or ""):match("^(%S+)%s*(%S*)")
        f:close()
        if l then
            KB_LAYOUT = (l == "us") and "us" or (l .. ",us")
            KB_VARIANT = (v and v ~= "" and v ~= "-") and (v .. ((l == "us") and "" or ",")) or ""
        end
    end
end

-------------------------------------------------------------
-- Colores (los cambia hyprarch-theme)
-------------------------------------------------------------
local ok, C = pcall(require, "colors")
if not ok or type(C) ~= "table" then
    C = {
        accent   = "rgba(39ff14ee)",
        accent2  = "rgba(ff1f4bee)",
        inactive = "rgba(1b221eaa)",
        glow     = "rgba(39ff1455)",
        shadow   = "rgba(000000b0)",
    }
end

-------------------------------------------------------------
-- Monitores y programas
-------------------------------------------------------------
-- En una máquina virtual la escala "auto" elige 2 y todo se ve gigante: ahí usamos 1.
local function sh(cmd)
    local f = io.popen(cmd)
    if not f then return "" end
    local s = f:read("*a") or ""
    f:close()
    return (s:gsub("%s+$", ""))
end
local virt  = sh("systemd-detect-virt 2>/dev/null")
local in_vm = (virt ~= "" and virt ~= "none")

-- Resolución y tamaño elegidos con hyprarch-display (archivo "WxH@Hz escala"); sin archivo, la recomendada
local D_MODE, D_SCALE = "preferred", (in_vm and "1" or "auto")
do
    local f = io.open((os.getenv("HOME") or "") .. "/.config/hyprarch/display", "r")
    if f then
        local m, s = (f:read("l") or ""):match("^(%d+x%d+@?[%d%.]*)%s+([%d%.]+)")
        f:close()
        if m then D_MODE, D_SCALE = m, s end
    end
end
hl.monitor({
    output   = "",
    mode     = D_MODE,
    position = "auto",
    scale    = D_SCALE,
})

local terminal = "kitty"
local menu     = "hyprarch-start"         -- el menú de inicio (se abre y se cierra del todo; no queda nada residente)
local files    = "thunar"
local browser  = "hyprarch-browser open"   -- el navegador que elegiste en el primer inicio
local scripts  = (os.getenv("HOME") or "") .. "/.config/hypr/scripts"

-------------------------------------------------------------
-- Autoarranque
-------------------------------------------------------------
hl.on("hyprland.start", function()
    -- Animación de entrada con sonido (una vez por arranque; se apaga con: echo off > ~/.config/hyprarch/intro)
    hl.exec_cmd("env GSK_RENDERER=cairo LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so hyprarch-intro --once")
    -- Asistente de primer inicio: aparece cuando termina la animación de entrada (solo la primera vez)
    hl.exec_cmd("bash -c 'sleep 8; hyprarch-welcome'")
    hl.exec_cmd(scripts .. "/wallpaper.sh")
    -- Portátiles: apaga la pantalla y bloquea tras un rato sin usar (si hypridle está instalado)
    hl.exec_cmd("bash -c 'command -v hypridle >/dev/null && exec hypridle'")
    hl.exec_cmd("waybar")
    hl.exec_cmd("mako")
    hl.exec_cmd("nm-applet --indicator")
    hl.exec_cmd("blueman-applet")
    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface color-scheme prefer-dark")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface gtk-theme Adwaita-dark")
    hl.exec_cmd(scripts .. "/welcome.sh")
    -- Hyro: la presencia de Claude en pantalla (necesita gtk4-layer-shell precargado)
    -- (GSK_RENDERER=cairo: la ventanita es chica y así se redibuja bien también en máquinas virtuales)
    hl.exec_cmd("env GSK_RENDERER=cairo LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so claude-presence daemon")
    -- Botones de la ventana activa (minimizar, maximizar, cerrar). En C (~6 MB); si faltara, la versión de respaldo en Python.
    -- Con el perfil lite no arranca (se decide antes de cargar nada); ~/.config/hyprarch/wbar = on/off lo fuerza.
    hl.exec_cmd("sh -c 'hyprarch-wbar || hyprarch-wbar-py'")
    -- La isla de Hyro: un botón arriba, centrado, que se despliega con una animación (esconde al de la esquina)
    -- (su salida queda en ~/.cache/hyprarch-buddy/island.log: el reporte la incluye para ver por qué falla un chat)
    hl.exec_cmd("sh -c 'mkdir -p ~/.cache/hyprarch-buddy; exec env GSK_RENDERER=cairo LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so hyprarch-island >>~/.cache/hyprarch-buddy/island.log 2>&1'")
    hl.exec_cmd("sh -c 'sleep 30; hyprarch-browser apply --quiet'")   -- si elegiste un navegador y faltaba Internet, se instala ahora
end)

-------------------------------------------------------------
-- Entorno
-------------------------------------------------------------
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "Adwaita")
hl.env("MOZ_ENABLE_WAYLAND", "1")
-- Gráfica(s) del equipo (Intel, AMD, NVIDIA): variables propias de cada una (vídeo por hardware, portátiles híbridos…)
do
    local p = io.popen("hyprarch-gpu env 2>/dev/null")
    if p then
        for line in p:lines() do
            local k, v = line:match("^([A-Z_a-z0-9]+)=(.+)$")
            if k then hl.env(k, v) end
        end
        p:close()
    end
end
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
-- Colores del menú de Wi-Fi (nmtui, usa "newt"): verde/negro con la paleta ANSI del tema
hl.env("NEWT_COLORS",
    "root=,black window=green,black border=green,black title=brightgreen,black " ..
    "button=black,green actbutton=black,brightgreen compactbutton=green,black " ..
    "checkbox=green,black actcheckbox=black,green entry=brightgreen,black disentry=gray,black " ..
    "label=green,black listbox=green,black actlistbox=black,green sellistbox=black,green " ..
    "actsellistbox=black,brightgreen textbox=green,black acttextbox=black,green " ..
    "emptyscale=black,black fullscale=black,green helpline=green,black roottext=green,black shadow=black,black")

if in_vm then
    -- Gráficos virtuales (VirtualBox/VMware): sin esto kitty y otras apps se cierran al abrir.
    -- En hardware real (Intel) esto NO se aplica.
    hl.env("LIBGL_ALWAYS_SOFTWARE", "1")
end

-------------------------------------------------------------
-- Apariencia
-------------------------------------------------------------
hl.config({
    general = {
        gaps_in  = P.gaps_in,
        gaps_out = P.gaps_out,
        border_size = P.border,
        col = {
            active_border   = { colors = { C.accent, C.accent2 }, angle = 45 },
            inactive_border = C.inactive,
        },
        resize_on_border = true,
        allow_tearing = false,
        layout = "dwindle",
    },

    decoration = {
        rounding       = 16,
        rounding_power = 2,
        active_opacity   = 1.0,
        inactive_opacity = 0.92,

        shadow = {
            enabled      = P.shadow,
            range        = 34,
            render_power = 3,
            color        = C.shadow,
        },

        -- Brillo de neón alrededor de la ventana activa
        glow = {
            enabled      = P.glow,
            range        = 14,
            render_power = 2,
            color        = C.glow,
        },

        -- Blur: la terminal (kitty) es translúcida y se desenfoca sola
        blur = {
            enabled           = P.blur,
            size              = 9,
            passes            = 3,
            vibrancy          = 0.2,
            noise             = 0.02,
            ignore_opacity    = true,
            new_optimizations = true,
            popups            = true,
        },
    },

    animations = {
        enabled = true,
    },

    dwindle = {
        preserve_split = true,
    },

    misc = {
        force_default_wallpaper  = 0,
        disable_hyprland_logo    = true,
        disable_splash_rendering = true,
    },
})

-------------------------------------------------------------
-- Animaciones: rápidas ("snappy") con rebotes ligeros
-------------------------------------------------------------
-- Curvas
hl.curve("snap",     { type = "bezier", points = { {0.16, 1.0},  {0.30, 1.0} } })   -- arranca fuerte y frena suave
hl.curve("softback", { type = "bezier", points = { {0.25, 1.25}, {0.50, 1.0} } })   -- se pasa un poco y vuelve
hl.curve("bounce",   { type = "bezier", points = { {0.34, 1.45}, {0.64, 1.0} } })   -- rebote más marcado
hl.curve("linear",   { type = "bezier", points = { {0, 0},       {1, 1} } })
hl.curve("pop",      { type = "spring", mass = 1, stiffness = 300, dampening = 22 }) -- resorte con rebote ligero

-- Cada modo escala la duración (P.dur): gamer = seco y rápido, cine/estudio = lento y suave.
-- Los rebotes y resortes solo se usan en el modo normal.
local function A(leaf, speed, curve, extra)
    local t = { leaf = leaf, enabled = true, speed = speed * P.dur }
    if curve == "pop" then
        if P.spring then t.spring = "pop" else t.bezier = "snap" end
    elseif not P.spring and (curve == "bounce" or curve == "softback") then
        t.bezier = "snap"
    else
        t.bezier = curve
    end
    if extra then for k, v in pairs(extra) do t[k] = v end end
    hl.animation(t)
end

-- Ventanas: abren con resorte, cierran rápido
A("global",      6,   "snap")
A("windows",     5,   "pop")
A("windowsIn",   5,   "pop",  { style = "popin 60%" })
A("windowsOut",  3.5, "snap", { style = "popin 70%" })
A("windowsMove", 5,   "pop")

-- Fundidos
A("fade",        4,   "snap")
A("fadeIn",      3,   "snap")
A("fadeOut",     2.5, "snap")
A("fadeSwitch",  4,   "snap")

-- Barra, lanzador y notificaciones: entran con rebote
A("layers",      4,   "bounce")
A("layersIn",    4,   "bounce", { style = "popin 80%" })
A("layersOut",   3,   "snap",   { style = "fade" })

-- Espacios de trabajo: deslizan con un pequeño pasarse
A("workspaces",       5, "softback", { style = "slidefade 20%" })
A("specialWorkspace", 5, "softback", { style = "slidefadevert 20%" })

-- Bordes
A("border",      8,   "snap")
hl.animation({ leaf = "borderangle", enabled = ROTATING_BORDER and P.rotate, speed = 60, bezier = "linear", style = "loop" })

-------------------------------------------------------------
-- Entrada
-------------------------------------------------------------
hl.config({
    input = {
        kb_layout  = KB_LAYOUT,
        kb_variant = KB_VARIANT,
        kb_options = "grp:alt_shift_toggle",
        follow_mouse = 1,
        sensitivity  = 0,
        repeat_rate  = 35,
        repeat_delay = 300,
        touchpad = {
            natural_scroll = true,
            tap_to_click   = true,
        },
    },
})

hl.gesture({
    fingers   = 3,
    direction = "horizontal",
    action    = "workspace",
})

-------------------------------------------------------------
-- Atajos  (SUPER = tecla Windows)
-------------------------------------------------------------
local mod = "SUPER"

-- Aplicaciones
hl.bind(mod .. " + Return", hl.dsp.exec_cmd(terminal))
-- La tecla Super (Windows) SOLA abre el menú de inicio, como en Windows: se dispara al SOLTARLA y solo si no se usó en un
-- atajo combinado (Super + otra tecla no lo abre). Pulsarla de nuevo lo cierra.
hl.bind(mod .. " + Super_L", hl.dsp.exec_cmd(menu), { release = true })
hl.bind(mod .. " + B",      hl.dsp.exec_cmd(browser))
hl.bind(mod .. " + E",      hl.dsp.exec_cmd(files))
hl.bind(mod .. " + X",      hl.dsp.exec_cmd("hyprarch-control"))                                    -- centro de control (volumen, Wi-Fi, modos…)
hl.bind(mod .. " + N",      hl.dsp.exec_cmd("hyprarch-wifi"))                                       -- redes Wi-Fi (panel animado, sin terminal)
hl.bind(mod .. " + A",      hl.dsp.exec_cmd("hyprarch-ai ask"))             -- caja rápida: una pregunta suelta, sin guardar nada
hl.bind(mod .. " + I", hl.dsp.exec_cmd("hyprarch-apps"))                                              -- instalar apps y juegos (menú)
hl.bind(mod .. " + SHIFT + A", hl.dsp.exec_cmd("hyprarch-ai open float"))                               -- chat flotante
-- Modos (cada atajo alterna entre ese modo y el normal)
hl.bind(mod .. " + SHIFT + G", hl.dsp.exec_cmd("hyprarch-mode toggle gamer"))
hl.bind(mod .. " + SHIFT + C", hl.dsp.exec_cmd("hyprarch-mode toggle cine"))
hl.bind(mod .. " + SHIFT + U", hl.dsp.exec_cmd("hyprarch-mode toggle estudio"))
hl.bind(mod .. " + SHIFT + W", hl.dsp.exec_cmd("hyprarch-mode toggle trabajo"))
hl.bind(mod .. " + SHIFT + N", hl.dsp.exec_cmd("hyprarch-mode normal"))
hl.bind(mod .. " + T",      hl.dsp.exec_cmd("hyprarch-theme"))                                            -- colores (rueda animada)
hl.bind(mod .. " + comma",  hl.dsp.exec_cmd("hyprarch-settings"))   -- Ajustes del sistema
hl.bind(mod .. " + S",      hl.dsp.exec_cmd("hyprarch-start"))   -- buscar apps, como en Windows (el shader CRT ya no tiene atajo: scripts/toggle-shader.sh)
hl.bind(mod .. " + F1",     hl.dsp.exec_cmd(scripts .. "/keybinds.sh"))
hl.bind(mod .. " + Escape", hl.dsp.exec_cmd(scripts .. "/powermenu.sh"))
hl.bind(mod .. " + L",      hl.dsp.exec_cmd("hyprlock"))
hl.bind(mod .. " + V",         hl.dsp.exec_cmd(scripts .. "/clipboard.sh"))   -- historial del portapapeles (como en Windows)

-- Ventanas
hl.bind(mod .. " + Q",       hl.dsp.window.close())
hl.bind(mod .. " + C",       hl.dsp.window.close())
hl.bind("ALT + F4",          hl.dsp.window.close())
hl.bind(mod .. " + SHIFT + F", hl.dsp.window.float({ action = "toggle" }))      -- ventana flotante / en mosaico
hl.bind(mod .. " + F",       hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }))
hl.bind(mod .. " + J",       hl.dsp.layout("togglesplit"))
hl.bind("ALT + Tab",         hl.dsp.window.cycle_next({}))
hl.bind(mod .. " + Tab",     hl.dsp.focus({ workspace = "previous" }))

-- Sistema
hl.bind(mod .. " + SHIFT + R", hl.dsp.exec_cmd("hyprctl reload"))
hl.bind(mod .. " + SHIFT + E", hl.dsp.exit())

-- Capturas
hl.bind("Print",         hl.dsp.exec_cmd(scripts .. "/screenshot.sh area"))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd(scripts .. "/screenshot.sh full"))
hl.bind(mod .. " + SHIFT + S", hl.dsp.exec_cmd(scripts .. "/screenshot.sh area"))   -- recorte de pantalla (como en Windows)

-- Ventanas al estilo Windows (hyprarch-win): ajustar a un lado, maximizar, restaurar / minimizar
hl.bind(mod .. " + left",  hl.dsp.exec_cmd("hyprarch-win left"))
hl.bind(mod .. " + right", hl.dsp.exec_cmd("hyprarch-win right"))
hl.bind(mod .. " + up",    hl.dsp.exec_cmd("hyprarch-win max"))
hl.bind(mod .. " + down",  hl.dsp.exec_cmd("hyprarch-win down"))
hl.bind(mod .. " + M",          hl.dsp.exec_cmd("hyprarch-win minimize"))
hl.bind(mod .. " + SHIFT + M",  hl.dsp.exec_cmd("hyprarch-win restore"))

-- Foco entre ventanas (con Alt, porque Super + flechas ajusta la ventana)
hl.bind(mod .. " + ALT + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mod .. " + ALT + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mod .. " + ALT + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mod .. " + ALT + down",  hl.dsp.focus({ direction = "down" }))

-- Mover ventana
hl.bind(mod .. " + SHIFT + left",  hl.dsp.window.move({ direction = "left" }))
hl.bind(mod .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(mod .. " + SHIFT + up",    hl.dsp.window.move({ direction = "up" }))
hl.bind(mod .. " + SHIFT + down",  hl.dsp.window.move({ direction = "down" }))

-- Redimensionar
hl.bind(mod .. " + CTRL + left",  hl.dsp.window.resize({ x = -40, y = 0,   relative = true }), { repeating = true })
hl.bind(mod .. " + CTRL + right", hl.dsp.window.resize({ x = 40,  y = 0,   relative = true }), { repeating = true })
hl.bind(mod .. " + CTRL + up",    hl.dsp.window.resize({ x = 0,   y = -40, relative = true }), { repeating = true })
hl.bind(mod .. " + CTRL + down",  hl.dsp.window.resize({ x = 0,   y = 40,  relative = true }), { repeating = true })

-- Espacios de trabajo
for i = 1, 10 do
    local key = i % 10 -- el 10 es la tecla 0
    hl.bind(mod .. " + " .. key,          hl.dsp.focus({ workspace = i }))
    hl.bind(mod .. " + SHIFT + " .. key,  hl.dsp.window.move({ workspace = i }))
end
hl.bind(mod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Mover / redimensionar con el mouse
hl.bind(mod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Teclas multimedia (con aviso en pantalla)
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd(scripts .. "/osd.sh vol-up"),      { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd(scripts .. "/osd.sh vol-down"),    { locked = true, repeating = true })
hl.bind("XF86AudioMute",         hl.dsp.exec_cmd(scripts .. "/osd.sh mute"),        { locked = true })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd(scripts .. "/osd.sh bright-up"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(scripts .. "/osd.sh bright-down"), { locked = true, repeating = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })

-------------------------------------------------------------
-- Reglas de ventanas y capas
-------------------------------------------------------------
-- Ignorar pedidos de maximizar de las apps
hl.window_rule({
    name  = "suppress-maximize-events",
    match = { class = ".*" },
    suppress_event = "maximize",
})

-- Ventanas auxiliares de hyprarch (tema, red, monitor): flotantes y centradas
hl.window_rule({
    name  = "hyprarch-utility",
    match = { class = "^(hyprarch-.*)$" },
    float  = true,
    center = true,
    size   = { 860, 520 },
})

-- Ventana de configuración de modos: más grande que las auxiliares
hl.window_rule({
    name   = "hyprarch-modes-win",
    match  = { class = "^(hyprarch-modes)$" },
    float  = true,
    center = true,
    size   = { 1040, 720 },
})

-- El chat con la IA es una ventana de trabajo (hay que poder verla junto al navegador al iniciar sesión,
-- pegar códigos, etc.): en mosaico y no flotante encima de todo.
hl.window_rule({
    name  = "hyprarch-ai-tiled",
    match = { class = "^(hyprarch-ai)$" },
    float = false,
})

-- Formas de hablar con la IA: chat flotante (abajo a la derecha), pantalla completa y respuesta rápida
hl.window_rule({
    name  = "hyprarch-ai-float",
    match = { class = "^(hyprarch-ai-float)$" },
    float = true,
    size  = { 340, 440 },
    move  = { "monitor_w-window_w-24", "monitor_h-window_h-24" },
})
hl.window_rule({
    name  = "hyprarch-ai-full",
    match = { class = "^(hyprarch-ai-full)$" },
    float = false,
})
hl.window_rule({
    name   = "hyprarch-ai-answer",
    match  = { class = "^(hyprarch-ai-answer)$" },
    float  = true,
    center = true,
    size   = { 640, 420 },
})

-- Diálogos típicos: flotantes
hl.window_rule({
    name  = "float-dialogs",
    match = { class = "^(pavucontrol|blueman-manager|nm-connection-editor|polkit-gnome-authentication-agent-1)$" },
    float  = true,
    center = true,
})

-- Blur detrás de la barra, el lanzador y las notificaciones.
-- Solo si el perfil lo permite (P.blur): en equipos modestos es lo que MÁS CPU gasta (se recalcula con cada
-- actualización de la barra, incluso en reposo) y ahí la barra se ve igual de bien con el fondo translúcido.
if P.blur then
    hl.layer_rule({ name = "blur-waybar",        match = { namespace = "waybar" },         blur = true, ignore_alpha = 0.2 })
    hl.layer_rule({ name = "blur-launcher",      match = { namespace = "launcher" },       blur = true, ignore_alpha = 0.2 })
    hl.layer_rule({ name = "blur-notifications", match = { namespace = "notifications" },  blur = true, ignore_alpha = 0.2 })
end
