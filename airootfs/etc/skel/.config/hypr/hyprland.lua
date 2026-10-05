-- hyprarch · Hyprland 0.55+ (configuración en Lua)
-- Neón verde / carmesí sobre fondo casi negro.
-- Los colores salen de colors.lua, que genera el comando `hyprarch-theme` (SUPER+T).

-------------------------------------------------------------
-- Interruptores rápidos
-------------------------------------------------------------
local ROTATING_BORDER = true   -- borde con degradado que gira (más "neón"; gasta algo más de batería)

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
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})

local terminal = "kitty"
local menu     = "fuzzel"
local files    = "thunar"
local browser  = "firefox"
local scripts  = (os.getenv("HOME") or "") .. "/.config/hypr/scripts"

-------------------------------------------------------------
-- Autoarranque
-------------------------------------------------------------
hl.on("hyprland.start", function()
    hl.exec_cmd(scripts .. "/wallpaper.sh")
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
end)

-------------------------------------------------------------
-- Entorno
-------------------------------------------------------------
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "Adwaita")
hl.env("MOZ_ENABLE_WAYLAND", "1")
hl.env("LIBVA_DRIVER_NAME", "iHD")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")

-------------------------------------------------------------
-- Apariencia
-------------------------------------------------------------
hl.config({
    general = {
        gaps_in  = 5,
        gaps_out = 12,
        border_size = 2,
        col = {
            active_border   = { colors = { C.accent, C.accent2 }, angle = 45 },
            inactive_border = C.inactive,
        },
        resize_on_border = true,
        allow_tearing = false,
        layout = "dwindle",
    },

    decoration = {
        rounding       = 12,
        rounding_power = 2,
        active_opacity   = 1.0,
        inactive_opacity = 0.94,

        shadow = {
            enabled      = true,
            range        = 18,
            render_power = 3,
            color        = C.shadow,
        },

        -- Brillo de neón alrededor de la ventana activa
        glow = {
            enabled      = true,
            range        = 14,
            render_power = 2,
            color        = C.glow,
        },

        -- Blur: la terminal (kitty) es translúcida y se desenfoca sola
        blur = {
            enabled           = true,
            size              = 6,
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
        vfr = true,
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

-- Ventanas: abren con resorte, cierran rápido
hl.animation({ leaf = "global",       enabled = true, speed = 6,   bezier = "snap" })
hl.animation({ leaf = "windows",      enabled = true, speed = 5,   spring = "pop" })
hl.animation({ leaf = "windowsIn",    enabled = true, speed = 5,   spring = "pop",  style = "popin 60%" })
hl.animation({ leaf = "windowsOut",   enabled = true, speed = 3.5, bezier = "snap", style = "popin 70%" })
hl.animation({ leaf = "windowsMove",  enabled = true, speed = 5,   spring = "pop" })

-- Fundidos
hl.animation({ leaf = "fade",         enabled = true, speed = 4,   bezier = "snap" })
hl.animation({ leaf = "fadeIn",       enabled = true, speed = 3,   bezier = "snap" })
hl.animation({ leaf = "fadeOut",      enabled = true, speed = 2.5, bezier = "snap" })
hl.animation({ leaf = "fadeSwitch",   enabled = true, speed = 4,   bezier = "snap" })

-- Barra, lanzador y notificaciones: entran con rebote
hl.animation({ leaf = "layers",       enabled = true, speed = 4,   bezier = "bounce" })
hl.animation({ leaf = "layersIn",     enabled = true, speed = 4,   bezier = "bounce", style = "popin 80%" })
hl.animation({ leaf = "layersOut",    enabled = true, speed = 3,   bezier = "snap",   style = "fade" })

-- Espacios de trabajo: deslizan con un pequeño pasarse
hl.animation({ leaf = "workspaces",   enabled = true, speed = 5,   bezier = "softback", style = "slidefade 20%" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 5, bezier = "softback", style = "slidefadevert 20%" })

-- Bordes
hl.animation({ leaf = "border",       enabled = true, speed = 8,   bezier = "snap" })
hl.animation({ leaf = "borderangle",  enabled = ROTATING_BORDER, speed = 60, bezier = "linear", style = "loop" })

-------------------------------------------------------------
-- Entrada
-------------------------------------------------------------
hl.config({
    input = {
        kb_layout  = "latam,es,us",
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
hl.bind(mod .. " + D",      hl.dsp.exec_cmd(menu))
hl.bind(mod .. " + B",      hl.dsp.exec_cmd(browser))
hl.bind(mod .. " + E",      hl.dsp.exec_cmd(files))
hl.bind(mod .. " + N",      hl.dsp.exec_cmd(scripts .. "/once.sh hyprarch-nmtui nmtui"))
hl.bind(mod .. " + T",      hl.dsp.exec_cmd(scripts .. "/once.sh hyprarch-theme hyprarch-theme"))
hl.bind(mod .. " + F1",     hl.dsp.exec_cmd(scripts .. "/keybinds.sh"))
hl.bind(mod .. " + Escape", hl.dsp.exec_cmd(scripts .. "/powermenu.sh"))
hl.bind(mod .. " + SHIFT + V", hl.dsp.exec_cmd("cliphist list | fuzzel --dmenu --prompt 'Portapapeles > ' | cliphist decode | wl-copy"))

-- Ventanas
hl.bind(mod .. " + Q",       hl.dsp.window.close())
hl.bind(mod .. " + C",       hl.dsp.window.close())
hl.bind("ALT + F4",          hl.dsp.window.close())
hl.bind(mod .. " + V",       hl.dsp.window.float({ action = "toggle" }))
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

-- Foco
hl.bind(mod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mod .. " + down",  hl.dsp.focus({ direction = "down" }))

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

-- Diálogos típicos: flotantes
hl.window_rule({
    name  = "float-dialogs",
    match = { class = "^(pavucontrol|blueman-manager|nm-connection-editor|polkit-gnome-authentication-agent-1)$" },
    float  = true,
    center = true,
})

-- Blur detrás de la barra, el lanzador y las notificaciones
hl.layer_rule({ name = "blur-waybar",        match = { namespace = "waybar" },         blur = true, ignore_alpha = 0.2 })
hl.layer_rule({ name = "blur-launcher",      match = { namespace = "launcher" },       blur = true, ignore_alpha = 0.2 })
hl.layer_rule({ name = "blur-notifications", match = { namespace = "notifications" },  blur = true, ignore_alpha = 0.2 })
