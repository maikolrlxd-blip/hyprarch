[[ -f ~/.bashrc ]] && . ~/.bashrc

# Autoarranque de Hyprland en la primera consola (tty1)
if [[ -z $WAYLAND_DISPLAY && ${XDG_VTNR:-0} -eq 1 ]]; then
  if command -v start-hyprland >/dev/null 2>&1; then
    start-hyprland
  else
    Hyprland
  fi
fi
