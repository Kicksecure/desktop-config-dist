# xfce4 Desktop config #

Sets desktop and display setting, wallpaper and desktop icons.
Sets icon theme and style.
Settings for the default panel aka task bar, like panel position/color/size
and panel plugins/shortcuts.

Autologin for user 'user' setting in lightdm.

Live check systray indicator which indicates the status of grub-live, whether
the system was booted into persistent or live mode. See also:
https://www.whonix.org/wiki/Whonix_Live

Adds start menu entries for web browser, terminal emulator, file manager.

Sets Whisker Menu for better usability.

Disable maximize windows when moving to top for better privacy.

Disables thumbnails for better security.

Disables save on exit for better privacy.

## How to install `whonix-xfce-desktop-config` using apt-get ##

1\. Add [Whonix's Signing Key](https://www.whonix.org/wiki/Whonix_Signing_Key).

```
sudo apt-key --keyring /etc/apt/trusted.gpg.d/whonix.gpg adv --keyserver hkp://ipv4.pool.sks-keyservers.net:80 --recv-keys 916B8D99C38EAF5E8ADC7A2A8D66066A2EEACCDA
```

3\. Add Whonix's APT repository.

```
echo "deb http://deb.whonix.org buster main" | sudo tee /etc/apt/sources.list.d/whonix.list
```

4\. Update your package lists.

```
sudo apt-get update
```

5\. Install `whonix-xfce-desktop-config`.

```
sudo apt-get install whonix-xfce-desktop-config
```

## How to Build deb Package ##

Replace `apparmor-profile-torbrowser` with the actual name of this package with `whonix-xfce-desktop-config` and see [instructions](https://www.whonix.org/wiki/Dev/Build_Documentation/apparmor-profile-torbrowser).

## Contact ##

* [Free Forum Support](https://forums.whonix.org)
* [Professional Support](https://www.whonix.org/wiki/Professional_Support)

## Payments ##

`whonix-xfce-desktop-config` requires [payments](https://www.whonix.org/wiki/Payments) to stay alive!
