[[ $- != *i* ]] && return

export EDITOR=nvim
export HISTCONTROL=ignoredups:erasedups

alias grep='grep --color=auto'
if [[ -n $WAYLAND_DISPLAY ]]; then
  alias ls='eza --icons --group-directories-first'
  alias ll='eza -l --icons --group-directories-first'
else
  alias ls='eza --group-directories-first'
  alias ll='eza -l --group-directories-first'
fi
alias cat='bat --paging=never'
alias vim='nvim'

[[ -f /usr/share/fzf/key-bindings.bash ]] && source /usr/share/fzf/key-bindings.bash
[[ -f /usr/share/fzf/completion.bash ]] && source /usr/share/fzf/completion.bash

command -v starship >/dev/null && eval "$(starship init bash)"
