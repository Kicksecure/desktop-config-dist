#!/bin/sh

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if [ -f '/usr/share/qubes/marker-vm' ]; then
  ## https://github.com/QubesOS/qubes-issues/issues/3366
  true "$0: Qubes does not support Wayland yet. Not setting GDK_BACKEND and QT_QPA_PLATFORM, ok."
else
  ## Fix wlroots glitches with virtualized graphics
  if [ "$(systemd-detect-virt 2>/dev/null)" != 'none' ]; then
    export WLR_RENDERER='pixman'
  fi

  ## Make gtk3 use Wayland by default
  export GDK_BACKEND=wayland

  ## Make Qt use Wayland by default
  export QT_QPA_PLATFORM=wayland
fi

## Indicate to Kicksecure sessions that the profile scripts have been run.
export PROFILE_SCRIPTS_WERE_SOURCED='yes'

if [ -z "$XDG_CONFIG_DIRS" ]; then
  XDG_CONFIG_DIRS="/etc:/etc/xdg:/usr/share"
  export XDG_CONFIG_DIRS
fi
if [ -z "$XDG_DATA_DIRS" ]; then
  XDG_DATA_DIRS="/usr/local/share/:/usr/share/"
  export XDG_DATA_DIRS
fi

if ! printf '%s\n' "$XDG_CONFIG_DIRS" | grep -- "/usr/share/desktop-config-dist" >/dev/null 2>/dev/null; then
  export XDG_CONFIG_DIRS="/usr/share/desktop-config-dist/:$XDG_CONFIG_DIRS"
fi
