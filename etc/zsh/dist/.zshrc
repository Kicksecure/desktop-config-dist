#!/usr/bin/env zsh

## Credits:
## github.com/tpope/dotfiles
## github.com/LukeSmithXYZ/voidrice


# Base for any shell
source /etc/zsh/dist/.shrc

autoload -U colors && colors	# Load colors
# the host has the symbol %M, but not inserted because whonix always sets
# the host as "host"

_git_prompt_info() {
  case "$PWD" in
    /net/*|/Volumes/*) return ;;
  esac
  if [ -d .svn ]; then
    ref=.svn
  else
    ref=${$(command git symbolic-ref HEAD 2> /dev/null)#refs/heads/} || \
      ref=${$(command git rev-parse HEAD 2>/dev/null)[1][1,7]} || \
      return
  fi
  case "$TERM" in
    *-256color|xterm-kitty) branchcolor=$'\e[38;5;31m'   ;;
    *-88color|rxvt-unicode) branchcolor=$'\e[38;5;22m'   ;;
    *)                      branchcolor=$'\e[00;94m'     ;;
  esac
print -Pn '(%%{$branchcolor%%}%20>...>$ref%<<%%{\e[00m%%})'
}

_get_dist_prompt() {
  test -z "${dist_prompt}" && return
  dist_prompt_color=$'\e[00;35m'
  print -Pn '%%{\e[00m%%}%%{$dist_prompt_color%%}%20>...>$dist_prompt%<<%%{\e[00m%%} '
}

local usercolor=$'\e[00;93m'
local dircolor=$'\e[00;34m'
# Use echotc Co?
case "$TERM" in
  *-256color|xterm-kitty)
    usercolor=$'\e[38;5;184m'
    dircolor=$'\e[38;5;27m'
    ;;
  *-88color|rxvt-unicode)
    usercolor=$'\e[38;5;56m'
    dircolor=$'\e[38;5;23m'
    ;;
esac
[ $UID = '0' ] && usercolor=$'\e[00;97m'
reset_color=$'\e[00m'

## user prompt
PROMPT="%{$fg[red]%}[\$(_get_dist_prompt)%{$usercolor%}%n%{$reset_color%}%{$reset_color%} %{$dircolor%}%~%{$reset_color%}%{$fg[red]%}]%{$reset_color%}%# "
## developer prompt
#PROMPT="%{$fg[red]%}[\$(_get_dist_prompt)%{$usercolor%}%n%{$reset_color%}%{$reset_color%} %{$dircolor%}%30<...<%~%<<%{$reset_color%}\$(_git_prompt_info)%{$fg[red]%}]%{$reset_color%}%# "
## print previous command exit code
#RPS1="%(?..(%{"$'\e[01;35m'"%}%?%{$reset_color%}%)%<<)"

## necessary when there is functions inside the prompt
setopt promptsubst
setopt PRINT_EXIT_VALUE

## set window title
_set_title() {
  case "$1" in
    *install*)
      hash -r ;;
  esac
  print -Pn '\e]1;%l@%m${1+*}\a'
  print -Pn '\e]2;%n@%m:%~'
  if [ -n "$1" ]; then
    print -Pnr ' (%24>..>$1%>>)'|tr '\0-\037' '?'
  fi
  print -Pn " [%l]\a"
}

case $TERM in
  screen*)
    precmd() {
      _set_title "$@"
      if [ "$STY" -o "$TMUX" ]; then
        # print -Pn "\e]1;\a\e]1;@%m\a"
        print -Pn '\ek@\e\\'
      else
        print -Pn '\ek@%m\e\\'
      fi
    }
    preexec() {
      _set_title "$@"
      print -n "\ek"
      print -Pnr '%10>..>$1' | tr '\0-\037' '?'
      if [ "$STY" -o "$TMUX" ]; then
        print -Pn '@\e\\'
      else
        print -Pn '@%m\e\\'
      fi
    }
  ;;

  xterm*|rxvt*|Eterm*|kterm*|putty*|dtterm*|ansi*|cygwin*)
    precmd () { _set_title "$@" }
    preexec() { _set_title "$@" }
    ;;

  linux*|vt220*) ;;

  *)
    PS1="%n@%m:%~%# "
    RPS1="%(?..(%?%)%<<)"
    ;;
esac

unset hostcolor hostletter hostcode dircolor usercolor usercode reset_color



# The following lines were added by compinstall
zstyle ':completion:*' auto-description 'specify: %d'
zstyle ':completion:*' completer _expand _complete _ignored _approximate
zstyle ':completion:*' expand prefix suffix
zstyle ':completion:*' file-sort name
zstyle ':completion:*' format 'Completing %d'
zstyle ':completion:*' group-name ''
zstyle ':completion:*' ignore-parents parent pwd ..
zstyle ':completion:*' insert-unambiguous true
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' list-suffixes true
zstyle ':completion:*' matcher-list '' 'm:{[:lower:][:upper:]}={[:upper:][:lower:]}' 'r:|[._-]=** r:|=**' 'l:|=* r:|=*'
zstyle ':completion:*' menu select=1
zstyle ':completion:*' original true
zstyle ':completion:*' preserve-prefix '//[^/]##/'
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' squeeze-slashes true
zstyle ':completion:*' use-compctl true
zstyle ':completion:*' verbose true
zstyle :compinstall filename '/home/user/.zshrc'

autoload -Uz compinit
zmodload zsh/complist
compinit -u
#_comp_options+=(globdots)		# Include hidden files.
# End of lines added by compinstall

# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
setopt autocd beep extendedglob nomatch
# End of lines configured by zsh-newuser-install

## key bindings
bindkey -v
export KEYTIMEOUT=1

# Use vim keys in tab complete menu:
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history
bindkey -v '^?' backward-delete-char
# Use vim keys during insert mode:
bindkey -M viins '^A' beginning-of-line
bindkey -M viins '^B' backward-char
bindkey -M viins '^D' delete-char-or-list
bindkey -M viins '^E' end-of-line
bindkey -M viins '^F' forward-char
bindkey -M viins '^K' kill-line
bindkey -M viins '^U' vi-kill-line
bindkey -M viins '^N' down-line-or-history
bindkey -M viins '^P' up-line-or-history
bindkey -M viins '^R' history-incremental-search-backward
bindkey -M viins '^S' history-incremental-search-forward
bindkey -M viins '^T' transpose-chars
bindkey -M viins '^Y' yank
bindkey -M viins ' ' magic-space
#bindkey -M viins '^J' accept-search 2>/dev/null
bindkey -M viins '^J' accept-line 2>/dev/null
#bindkey -M viins '^J' accept-2>/dev/null
#bindkey -M isearch '^J' accept-search 2>/dev/null

# Change cursor shape for different vi modes.
function zle-keymap-select() {
  case $KEYMAP in
    viins|main) printf "\e[5 q";; # beam
    vicmd) printf "\e[1 q" ;; # block
  esac
}
zle -N zle-keymap-select
zle-line-init() {
  # initiate `vi insert` as keymap (can be removed if `bindkey -V` has
  # been set elsewhere)
  zle -K viins
  printf "\e[5 q"
}
zle -N zle-line-init

## Problem is that the cursor is still beam when entering the Vi editor.
## Found this results, but none that only edited the zshrc worked:
##  https://unix.stackexchange.com/questions/433273/changing-cursor-style-based-on-mode-in-both-zsh-and-vim
## The only result that worked is by adding this to the vimrc:
##  autocmd VimEnter * silent exec "! echo -ne '\e[1 q'"
##  autocmd VimLeave * silent exec "! echo -ne '\e[5 q'"


autoload -Uz select-word-style
select-word-style bash

change-first-word() {
  zle beginning-of-line -N
  zle kill-word
}
zle -N change-first-word
bindkey -M emacs "\ea" change-first-word

bindkey -M emacs "^XD" describe-key-briefly

fg-widget() {
  if [[ $#BUFFER -eq 0 ]]; then
    if jobs %- >/dev/null 2>&1; then
      BUFFER='fg %-'
    else
      BUFFER='fg'
    fi
    zle accept-line
  else
    zle push-input
    zle clear-screen
  fi
}
zle -N fg-widget
bindkey -M vicmd "^Z" fg-widget
bindkey -M viins "^Z" fg-widget

autoload -Uz incarg
zle -N incarg
bindkey -M vicmd "^A" incarg

bindkey -M vicmd ga what-cursor-position

new-screen() {
  [ -z "$STY" ] || screen < "$TTY"
  [ -z "$TMUX" ] || tmux new-window
}
zle -N new-screen
[[ -z "$terminfo[kf12]" ]] || bindkey "$terminfo[kf12]" new-screen

# Edit line in vim with ctrl-e:
autoload -Uz edit-command-line
zle -N edit-command-line
bindkey '^e' edit-command-line
bindkey -M vicmd '^[[P' vi-delete-char
bindkey -M vicmd '^e' edit-command-line
bindkey -M visual '^[[P' vi-delete


# The following lines were added by Whonix

# enable color support of ls, less and man, and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    # Take advantage of $LS_COLORS for completion as well
    zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
    zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
fi

# enable auto-suggestions based on the history
if test -f /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh; then
    source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
    # change suggestion color
    ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#999'
fi

if test -f /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh &&
    [ "$color_prompt" = yes ]
then
    source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fi

# enable command-not-found if installed
if test -f /etc/zsh_command_not_found; then
    source /etc/zsh_command_not_found
fi
