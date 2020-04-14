#!/bin/bash

## Copyright (C) 2018 - 2020 ENCRYPTED SUPPORT LP <adrelanos@riseup.net>
## Copyright (C) 2018 Algernon <33966997+Algernon-01@users.noreply.github.com>
## See the file COPYING for copying conditions.

set -e

## lsblk --all
##
## NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
## sda      8:0    0  100G  1 disk
##
## 1 means read-only
## 0 means read-write

## Using sudo because hide-hardware-info.service makes this only readable by
## root, not user.
## https://forums.whonix.org/t/restrict-hardware-information-to-root-testers-wanted/8618/13
if sudo --non-interactive /bin/lsblk --all --raw --output RO | grep "0" ; then
   ## Output of lsblk did not contain zero ("0"), meaning no read-write devices found.
   ## In other words, all disks are set set to read-only.
   echo "<img>/usr/share/icons/gnome-colors-common/16x16/actions/dialog-apply.png</img>"
   ## Show "Live" next to info symbol in systray.
   echo "<txt>Live</txt>"

   if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
      ## case: Whonix VM
      echo "<tool>Live mode is enabled. All changes to the disk will be gone after a reboot. See: https://whonix.org/wiki/Whonix_Live or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://whonix.org/wiki/Whonix_Live</click>"
      echo "<txtclick>x-www-browser https://whonix.org/wiki/Whonix_Live</txtclick>"
   else
      ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
      echo "<tool>Live mode is enabled. All changes to the disk will be gone after a reboot. See: https://whonix.org/wiki/grub-live or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://whonix.org/wiki/grub-live</click>"
      echo "<txtclick>x-www-browser https://whonix.org/wiki/grub-live</txtclick>"
   fi

   exit 0
fi

if grep -qs "boot=live" /proc/cmdline; then
   ## grub-live is enabled.
   echo "<img>/usr/share/icons/Adwaita/16x16/status/dialog-warning.png</img>"
   echo "<txt>Live</txt>"

   if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
      ## case: Whonix VM
      echo "<tool>Live mode is enabled but it is still possible to write to the disk. Please power off the machine and set the disk to read-only. See: https://whonix.org/wiki/Whonix_Live or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://whonix.org/wiki/Whonix_Live</click>"
      echo "<txtclick>x-www-browser https://whonix.org/wiki/Whonix_Live</txtclick>"
   else
      ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
      echo "<tool>Live mode is enabled but it is still possible to write to the disk. Please power off the machine and set the disk to read-only, if possible. See: https://whonix.org/wiki/grub-live or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://whonix.org/wiki/grub-live</click>"
      echo "<txtclick>x-www-browser https://whonix.org/wiki/grub-live</txtclick>"
   fi

   exit 0
fi

## Live mode is disabled.
echo "<img>/usr/share/icons/gnome-colors-common/22x22/status/gtk-info.png</img>"
## Do not show "Persistent" next to info symbol in systray.
#echo "<txt>Persistent</txt>"

if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
   ## case: Whonix VM
   echo "<tool>You are using persistent mode. All changes to the disk will be preserved after a reboot. For using live mode, see: https://whonix.org/wiki/Whonix_Live or click on the icon for more information.</tool>"
   echo "<click>x-www-browser https://whonix.org/wiki/Whonix_Live</click>"
   echo "<txtclick>x-www-browser https://whonix.org/wiki/Whonix_Live<txtclick>"
else
   ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
   echo "<tool>You are using persistent mode. All changes to the disk will be preserved after a reboot. For using live mode, see: https://whonix.org/wiki/grub-live or click on the icon for more information.</tool>"
   echo "<click>x-www-browser https://whonix.org/wiki/grub-live</click>"
   echo "<txtclick>x-www-browser https://whonix.org/wiki/grub-live<txtclick>"
fi

exit 0
