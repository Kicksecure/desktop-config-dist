# Configuration for Whonix Xfce Desktop #

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

1\. Download [Whonix's Signing Key]().

```
wget https://www.whonix.org/patrick.asc
```

Users can [check Whonix Signing Key](https://www.whonix.org/wiki/Whonix_Signing_Key) for better security.

2\. Add Whonix's signing key.

```
sudo apt-key --keyring /etc/apt/trusted.gpg.d/whonix.gpg add ~/patrick.asc
```

3\. Add Whonix's APT repository.

```
echo "deb https://deb.whonix.org buster main contrib non-free" | sudo tee /etc/apt/sources.list.d/whonix.list
```

4\. Update your package lists.

```
sudo apt-get update
```

5\. Install `whonix-xfce-desktop-config`.

```
sudo apt-get install whonix-xfce-desktop-config
```

## How to Build deb Package from Source Code ##

Can be build using standard Debian package build tools such as:

```
dpkg-buildpackage -b
```

See [instructions](https://www.whonix.org/wiki/Dev/Build_Documentation/whonix-xfce-desktop-config). (Replace `package-name` with the actual name of this package.)

## Contact ##

* [Free Forum Support](https://forums.whonix.org)
* [Professional Support](https://www.whonix.org/wiki/Professional_Support)

## Donate ##

`whonix-xfce-desktop-config` requires [donations](https://www.whonix.org/wiki/Donate) to stay alive!
