#!/bin/sh
# Install the tux Plymouth theme and make it the boot splash.
set -e

THEME=tux
SRC="$(cd "$(dirname "$0")" && pwd)/$THEME"
DEST=/usr/share/plymouth/themes/$THEME

[ "$(id -u)" = 0 ] || { echo "run me with sudo"; exit 1; }
[ -d "$SRC" ] || { echo "theme not built yet -- run: python3 make_plymouth.py"; exit 1; }

echo ":: installing $SRC -> $DEST"
rm -rf "$DEST"
install -d -m 755 "$DEST"
install -m 644 "$SRC"/* "$DEST"/

if command -v plymouth-set-default-theme >/dev/null 2>&1; then
    echo ":: setting default theme and rebuilding the initramfs"
    plymouth-set-default-theme -R "$THEME"
elif command -v dracut >/dev/null 2>&1; then
    echo ":: dracut detected -- set plymouth.theme=$THEME and rebuilding"
    dracut -f
else
    echo "!! could not find plymouth-set-default-theme; rebuild your initramfs by hand"
    exit 1
fi

echo ":: done.  Reboot to see it."
echo "   The kernel command line needs 'quiet splash' (yours already has it)."
