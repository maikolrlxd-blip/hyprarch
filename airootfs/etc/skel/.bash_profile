[[ -f ~/.bashrc ]] && . ~/.bashrc

# Idioma elegido con hyprarch-lang (LANG para todos los programas de la sesión)
if [[ -r ${XDG_CONFIG_HOME:-$HOME/.config}/locale.conf ]]; then
  set -a; . "${XDG_CONFIG_HOME:-$HOME/.config}/locale.conf"; set +a
fi

# Autoarranque de Hyprland en la primera consola (tty1)
if [[ -z $WAYLAND_DISPLAY && ${XDG_VTNR:-0} -eq 1 ]]; then
  # Perfil de rendimiento (ligero en equipos modestos); debe estar listo antes de leer la configuración de Hyprland
  command -v hyprarch-perf >/dev/null 2>&1 && hyprarch-perf auto >/dev/null 2>&1
  if command -v start-hyprland >/dev/null 2>&1; then
    start-hyprland
  else
    Hyprland
  fi
fi
