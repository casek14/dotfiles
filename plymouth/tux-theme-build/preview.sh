#!/bin/sh
# Preview the installed theme without rebooting.
#
#   ./preview.sh            splash for 20s
#   ./preview.sh 8          splash for 8s
#   ./preview.sh 20 pass    splash, then the LUKS-style password prompt
#
# Under X11 (or XWayland with DISPLAY set) plymouthd opens a window.  On a bare
# VT it draws on the console -- switch to a spare one (ctrl+alt+F3) first.
set -e
SECS=${1:-20}

[ "$(id -u)" = 0 ] || { echo "run me with sudo -E (keep DISPLAY for the windowed preview)"; exit 1; }

cleanup() { plymouth --quit 2>/dev/null || true; }
trap cleanup EXIT INT TERM

plymouthd --debug --mode=boot
plymouth --show-splash

if [ "$2" = "pass" ]; then
    sleep "$SECS"
    plymouth --ask-for-password --prompt="Enter passphrase for /dev/nvme0n1p2:" --number-of-tries=1 >/dev/null || true
    sleep 6
else
    sleep "$SECS"
fi
