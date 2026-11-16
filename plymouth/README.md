## Plymouth
Plymouth is a graphical boot system and logger for Linux that provides a smooth, flicker-free startup and shutdown animation.

To setup the theme take a look on [Arch wiki page](https://wiki.archlinux.org/title/Plymouth#Configuration), how to setup and test. 

#### Tux theme
![Tux nightshift Plymouth theme](./showcase/tux.gif)

#### Installing the theme
Copy the theme into `/usr/share/plymouth/themes/` — do not symlink it to this repo.
`mkinitcpio` stores a symlinked theme under its `/home/...` path, which is not mounted
during early boot, so Plymouth finds an empty theme directory and shows nothing.

Use `tux-theme-build/install.sh` (run with sudo), or by hand:

```sh
sudo install -d /usr/share/plymouth/themes/tux
sudo install -m 644 themes/tux/* /usr/share/plymouth/themes/tux/
sudo plymouth-set-default-theme -R tux
```
