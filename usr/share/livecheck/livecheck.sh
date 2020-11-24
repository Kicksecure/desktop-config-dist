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

## as soon as we have at least one "0" -> not live mode

## when using snapd:
##
## dsudo /bin/lsblk --all
##
## NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
## loop0    7:0    0   55M  1 loop /snap/core18/1754
## loop1    7:1    0        0 loop
## loop2    7:2    0        0 loop
## loop3    7:3    0        0 loop
## loop4    7:4    0        0 loop
## loop5    7:5    0        0 loop
## loop6    7:6    0        0 loop
## loop7    7:7    0        0 loop
## sda      8:0    0  100G  0 disk
##   sda1   8:1    0  100G  0 part /
## sr0     11:0    1 1024M  0 rom

## when using snapd:
##
## dsudo /bin/lsblk --all
##
## 1
## 1
## 0
## 0
## 0
## 0
## 0
## 0
## 0
## 0
## 0

## Using sudo because hide-hardware-info.service makes this only readable by
## root, not user.
## https://forums.whonix.org/t/restrict-hardware-information-to-root-testers-wanted/8618/13
## This did not work with snapd
## http://forums.whonix.org/t/wickr-me-gets-whonix-stuck-in-live-mode/9834/1
#if sudo --non-interactive /bin/lsblk --noheadings --all --raw --output RO | grep --invert-match "0" ; then
## Output of lsblk does not contain zero ("0"), meaning no read-write devices found.
## In other words, all disks are set set to read-only.

## Notice if execution of lsblk fails with a non-zero exit code such as in case of missing sudoers permissions.
if ! lsblk_output="$(sudo --non-interactive /bin/lsblk --noheadings --all --raw --output RO)" ; then
   true "INFO: Running 'sudo --non-interactive /bin/lsblk --noheadings --all --raw --output RO' failed!"
   echo "<img>/usr/share/icons/gnome-colors-common/16x16/status/dialog-error.png</img>"
   echo "<txt>Error</txt>"
   if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
      ## case: Whonix VM
      echo "<tool>Do not panic. Live mode detection failed. Could not determine if booted into live mode or persistent mode. Please report this bug. See: https://www.whonix.org/wiki/Reporting_Bugs or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://www.whonix.org/wiki/Reporting_Bugs</click>"
      echo "<txtclick>x-www-browser https://www.whonix.org/wiki/Reporting_Bugs</txtclick>"
   else
      ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
      echo "<tool>Do not panic. Live mode detection failed. Could not determine if booted into live mode or persistent mode. Please report this bug. See: https://www.whonix.org/wiki/Reporting_Bugs or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://www.whonix.org/wiki/Reporting_Bugs</click>"
      echo "<txtclick>x-www-browser https://www.whonix.org/wiki/Reporting_Bugs</txtclick>"
   fi
   exit 0
fi

if echo "$lsblk_output" | grep --quiet "0" ; then
   true "INFO: If at least one '0' was found. Conclusion: not all read-only. Some read-write."

   if grep -qs "boot=live" /proc/cmdline; then
      true "INFO: grub-live is enabled."
      echo "<img>/usr/share/icons/Adwaita/16x16/status/dialog-warning.png</img>"
      echo "<txt>Live</txt>"

      if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
         ## case: Whonix VM
         echo "<tool>Live mode is enabled but it is still possible to write to the disk. Please power off the machine and set the disk to read-only. See: https://www.whonix.org/wiki/VM_Live_Mode or click on the icon for more information.</tool>"
         echo "<click>x-www-browser https://www.whonix.org/wiki/VM_Live_Mode</click>"
         echo "<txtclick>x-www-browser https://www.whonix.org/wiki/VM_Live_Mode</txtclick>"
      else
         ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
         echo "<tool>Live mode is enabled but it is still possible to write to the disk. Please power off the machine and set the disk to read-only, if possible. See: https://www.whonix.org/wiki/Host_Live_Mode or click on the icon for more information.</tool>"
         echo "<click>x-www-browser https://www.whonix.org/wiki/Host_Live_Mode</click>"
         echo "<txtclick>x-www-browser https://www.whonix.org/wiki/Host_Live_Mode</txtclick>"
      fi
   else
      true "INFO: Live mode is disabled."
      echo "<img>/usr/share/icons/gnome-colors-common/22x22/status/gtk-info.png</img>"
      ## Do not show "Persistent" next to info symbol in systray.
      #echo "<txt>Persistent</txt>"

      if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
         ## case: Whonix VM
         echo "<tool>You are using persistent mode. All changes to the disk will be preserved after a reboot. For using live mode, see: https://www.whonix.org/wiki/VM_Live_Mode or click on the icon for more information.</tool>"
         echo "<click>x-www-browser https://www.whonix.org/wiki/VM_Live_Mode</click>"
         echo "<txtclick>x-www-browser https://www.whonix.org/wiki/VM_Live_Mode<txtclick>"
      else
         ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
         echo "<tool>You are using persistent mode. All changes to the disk will be preserved after a reboot. For using live mode, see: https://www.whonix.org/wiki/Host_Live_Mode or click on the icon for more information.</tool>"
         echo "<click>x-www-browser https://www.whonix.org/wiki/Host_Live_Mode</click>"
         echo "<txtclick>x-www-browser https://www.whonix.org/wiki/Host_Live_Mode<txtclick>"
      fi
   fi
else
   true "INFO: No '0' is found. Therefore only '1' found. Conclusion: read-only."

   echo "<img>/usr/share/icons/gnome-colors-common/16x16/actions/dialog-apply.png</img>"
   ## Show "Live" next to info symbol in systray.
   echo "<txt>Live</txt>"

   if test -f /usr/share/anon-gw-base-files/gateway || test -f /usr/share/anon-ws-base-files/workstation ; then
      ## case: Whonix VM
      echo "<tool>Live mode is enabled. All changes to the disk will be gone after a reboot. See: https://www.whonix.org/wiki/VM_Live_Mode or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://www.whonix.org/wiki/VM_Live_Mode</click>"
      echo "<txtclick>x-www-browser https://www.whonix.org/wiki/VM_Live_Mode</txtclick>"
   else
      ## case: Debian hosts, Kicksecure hosts, non-Whonix hosts, Whonix-Host
      echo "<tool>Live mode is enabled. All changes to the disk will be gone after a reboot. See: https://www.whonix.org/wiki/Host_Live_Mode or click on the icon for more information.</tool>"
      echo "<click>x-www-browser https://www.whonix.org/wiki/Host_Live_Mode</click>"
      echo "<txtclick>x-www-browser https://www.whonix.org/wiki/Host_Live_Mode</txtclick>"
   fi
fi
