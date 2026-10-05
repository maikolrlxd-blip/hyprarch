#!/usr/bin/env bash
# Alterna el shader de pantalla CRT (SUPER+S). Apagado por defecto.
# Si se ve lento (p. ej. en VM), usar hyprarch-lite.frag cambiando el nombre abajo.
set -euo pipefail

reply="$(hyprctl eval '
    local base = os.getenv("XDG_CONFIG_HOME")
    if not base or base == "" then
        base = assert(os.getenv("HOME")) .. "/.config"
    end
    local shader = base .. "/hypr/shaders/hyprarch-crt.frag"
    local current = hl.get_config("decoration.screen_shader")
    assert(type(current) == "string", "no se pudo leer decoration.screen_shader")
    if current == shader then
        hl.config({ decoration = { screen_shader = "" } })
    else
        local file, err = io.open(shader, "rb")
        assert(file, err)
        file:close()
        hl.config({ decoration = { screen_shader = shader } })
    end
')"

printf '%s\n' "$reply"
[[ "$reply" == "ok" ]]
