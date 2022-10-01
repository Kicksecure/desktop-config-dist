# Configuration for Derivative Desktop #

Sets desktop and display setting, wallpaper and desktop icons.
Sets icon theme and style.
Settings for the default panel aka task bar, like panel position/color/size
and panel plugins/shortcuts.

Autologin for user 'user' setting in lightdm.

Live check systray indicator which indicates the status of grub-live, whether
the system was booted into persistent or live mode. See also:
https://www.kicksecure.com/wiki/grub-live

Adds start menu entries for web browser, terminal emulator, file manager.

Sets Whisker Menu for better usability.

Disable maximize windows when moving to top for better privacy.

Disables thumbnails for better security.

Disables save on exit for better privacy.

Ships `zsh` derivative configuration settings folder `/etc/zsh/dist`.
Set environment variable `ZDOTDIR=/etc/zsh/dist` through use of file
`/usr/lib/systemd/system.conf.d/30_kicksecure-desktop-config-dist-zsh.conf`.
But does not configure `zsh` as default shell.
(That is up to package `dist-base-files`.)

## How to install `desktop-config-dist` using apt-get ##

1\. Download the APT Signing Key.

```
wget https://www.kicksecure.com/derivative.asc
```

Users can [check the Signing Key](https://www.kicksecure.com/wiki/Signing_Key) for better security.

2\. Add the APT Signing Key..

```
sudo cp ~/derivative.asc /usr/share/keyrings/derivative.asc
```

3\. Add the derivative repository.

```
echo "deb [signed-by=/usr/share/keyrings/derivative.asc] https://deb.kicksecure.com bullseye main contrib non-free" | sudo tee /etc/apt/sources.list.d/derivative.list
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

See instructions.

NOTE: Replace `generic-package` with the actual name of this package `desktop-config-dist`.

* **A)** [easy](https://www.kicksecure.com/wiki/Dev/Build_Documentation/generic-package/easy), _OR_
* **B)** [including verifying software signatures](https://www.kicksecure.com/wiki/Dev/Build_Documentation/generic-package)

## Contact ##

* [Free Forum Support](https://forums.kicksecure.com)
* [Professional Support](https://www.kicksecure.com/wiki/Professional_Support)

## Donate ##

`desktop-config-dist` requires [donations](https://www.kicksecure.com/wiki/Donate) to stay alive!
