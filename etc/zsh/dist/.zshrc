#!/usr/bin/env zsh

## Credits:
## https://github.com/tpope/dotfiles
## https://github.com/LukeSmithXYZ/voidrice
## https://github.com/jeffreytse/zsh-vi-mode/blob/master/zsh-vi-mode.zsh

## base dir
zsh_custom_dir="/etc/zsh/dist"

## history
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000

# Base for any shell
source ${zsh_custom_dir}/.shrc

autoload -U colors && colors	# Load colors

## prompt
if test -f ${zsh_custom_dir}/.zshrc_prompt; then
  source ${zsh_custom_dir}/.zshrc_prompt
fi

## completion
if test -f ${zsh_custom_dir}/.zshrc_completions; then
  source ${zsh_custom_dir}/.zshrc_completions
fi

## key bindings
if test -f ${zsh_custom_dir}/.zshrc_bindkeys; then
  source ${zsh_custom_dir}/.zshrc_bindkeys
fi

## enable auto-suggestions based on the history
if test -f /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh; then
  source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
  # change suggestion color
  ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#999'
fi

## highlight commands as you type
if test -f /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh &&
  [ "$color_prompt" = yes ]
then
  source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fi

## enable command-not-found if installed
if test -f /etc/zsh_command_not_found; then
  source /etc/zsh_command_not_found
fi

