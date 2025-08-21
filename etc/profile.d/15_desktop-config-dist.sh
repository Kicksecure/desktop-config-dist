#!/bin/sh

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Fix wlroots glitches with virtualized graphics
if [ "$(systemd-detect-virt)" != 'none' ]; then
  export WLR_RENDERER='pixman'
fi

## Make gtk3 use Wayland by default
export GDK_BACKEND=wayland

## Make Qt use Wayland by default
export QT_QPA_PLATFORM=wayland

## Indicate to Kicksecure sessions that the profile scripts have been run.
export PROFILE_SCRIPTS_WERE_SOURCED='yes'

if [ -z "$XDG_CONFIG_DIRS" ]; then
  XDG_CONFIG_DIRS="/etc:/etc/xdg:/usr/share"
fi
if [ -z "$XDG_DATA_DIRS" ]; then
  XDG_DATA_DIRS="/usr/local/share/:/usr/share/"
fi

if ! printf '%s\n' "$XDG_CONFIG_DIRS" | grep -- "/usr/share/desktop-config-dist" >/dev/null 2>/dev/null; then
  export XDG_CONFIG_DIRS="/usr/share/desktop-config-dist/:$XDG_CONFIG_DIRS"
fi
