# tux — Plymouth theme

The Tux animation as a boot splash. Same renderer as `tux.gif`, but a boot
splash can't be one linear clip: it has to fill an unknown amount of time and
then get out of the way. So it is built as two pieces:

| asset        | plays          | contents                                        |
|--------------|----------------|-------------------------------------------------|
| `intro-*.png`| once, ~5.5 s   | dark room → light flicks on → walk over → sit    |
| `loop-*.png` | forever, 2.8 s | typing at the desk, seamless                     |

When the boot finishes, Plymouth fades out wherever it happens to be.

## Build

    python3 make_plymouth.py

Options:

    --scale 1.5     bigger frames (640x400 * scale); costs RAM, see below
    --every 2       keep every 2nd intro frame — halves RAM, choppier walk
    --out DIR       where to build (default ./tux)

The generator prints exactly what it produced, including the runtime cost.

## Install

    sudo ./install.sh

That copies the theme to `/usr/share/plymouth/themes/tux`, makes it the
default, and rebuilds the initramfs (`plymouth-set-default-theme -R`). It
changes two things on your system: the default Plymouth theme and the
initramfs. To go back:

    sudo plymouth-set-default-theme -R darth_vader

Your kernel command line already has `quiet splash`, and `plymouth` is already
in your mkinitcpio `HOOKS` ahead of `sd-encrypt`, which is the ordering the
password prompt needs. Nothing else to change.

## Preview without rebooting

    sudo -E ./preview.sh 20          # splash for 20s
    sudo -E ./preview.sh 12 pass     # then show the passphrase prompt

Under X11 — or XWayland, if `DISPLAY` is set and you keep it with `sudo -E` —
plymouthd opens a window. On a bare console it draws on the VT, so switch to a
spare one (ctrl+alt+F3) first. The script always quits plymouthd on the way
out, including on ctrl+C.

## Disk passphrase

Your root is LUKS, so the splash must be able to ask for the passphrase.
`tux.script` implements `DisplayPassword`, `DisplayQuestion`,
`DisplayNormal`, and the message callbacks. The prompt appears under the
vignette; each typed character adds a dot (`bullet.png`, an image rather than
a font glyph, so it works even if the label plugin is missing). Tux keeps
typing while you do.

**Test the prompt with `preview.sh 12 pass` before you trust it at boot.** If
anything ever goes wrong, plymouth's own fallback still works: press ESC at
boot for the text prompt.

## Cost

At the default size, 118 frames of 640x400:

* **~3 MiB** added to the initramfs (the PNGs)
* **~115 MiB** of RAM while plymouthd runs — it decodes every frame to RGBA up
  front, then frees it all when the splash quits

That is fine on a normal desktop. On a small machine, build with `--every 2`
(~59 MiB) or `--scale 0.75` (~65 MiB).

## How it fits together

The frames are rendered with `FLAT_BG = True`, which turns off the vignette and
paints a flat `#050609` background. The `.script` then sets Plymouth's window
to that exact colour, so the centred 640x400 sprite has no visible edge at any
resolution — every border pixel of every frame is precisely the window colour.
The lamp flex fades out over the top 96 rows instead of being cut off, so it
reads as disappearing into a dark ceiling rather than stopping in mid-air.

The typing loop is seamless by construction: flippers cycle every 4 frames,
the body bob every 8, the screen flicker every 4, and the steam covers exactly
two periods across the 40-frame loop — all of which divide into 40. The
generator asserts nothing, but `loop-39` → `loop-0` is a pixel-exact match.

Playback timing: Plymouth calls `refresh_callback` at 50 Hz, and the script
advances `Math.Int(tick * fps / 50)` so the animation runs at the same 14.29 fps
as the GIF regardless of that.

Edit `tux.script.in` (the template), not `tux/tux.script` — the
generator overwrites the latter and substitutes the frame counts, fps, frame
size and background colour into it.

## Other distros

`install.sh` handles mkinitcpio and dracut. On Debian/Ubuntu, copy the theme
directory into `/usr/share/plymouth/themes/`, then:

    sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth \
        default.plymouth /usr/share/plymouth/themes/tux/tux.plymouth 200
    sudo update-alternatives --config default.plymouth
    sudo update-initramfs -u
