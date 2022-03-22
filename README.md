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
## How to install `desktop-config-dist` using apt-get ##

1\. Download the APT Signing Key.

```
wget https://www.whonix.org/derivative.asc
```

Users can [check Whonix Signing Key](https://www.whonix.org/wiki/Whonix_Signing_Key) for better security.

2\. Add the APT Signing Key..

```
sudo cp ~/derivative.asc /usr/share/keyrings/derivative.asc
```

3\. Add the derivative repository.

```
echo "deb [signed-by=/usr/share/keyrings/derivative.asc] https://deb.whonix.org bullseye main contrib non-free" | sudo tee /etc/apt/sources.list.d/derivative.list
```

4\. Update your package lists.

```
sudo apt-get update
```

5\. Install `desktop-config-dist`.

```
sudo apt-get install desktop-config-dist
```

## How to Build deb Package from Source Code ##

Can be build using standard Debian package build tools such as:

```
dpkg-buildpackage -b
```

See instructions. (Replace `generic-package` with the actual name of this package `desktop-config-dist`.)

* **A)** [easy](https://www.whonix.org/wiki/Dev/Build_Documentation/generic-package/easy), _OR_
* **B)** [including verifying software signatures](https://www.whonix.org/wiki/Dev/Build_Documentation/generic-package)

## Contact ##

* [Free Forum Support](https://forums.whonix.org)
* [Professional Support](https://www.whonix.org/wiki/Professional_Support)

## Donate ##

`desktop-config-dist` requires [donations](https://www.whonix.org/wiki/Donate) to stay alive!
