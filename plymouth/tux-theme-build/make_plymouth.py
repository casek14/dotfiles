#!/usr/bin/env python3
"""Build a Plymouth theme out of the Tux animation.

The GIF is one long timeline; a boot splash needs two pieces instead:

  intro-*.png   plays once   -- dark room, light on, walk over, sit down
  loop-*.png    plays foreve -- typing, seamless, until the boot finishes

Both are rendered by tux_animation.py with FLAT_BG on, so the frames sit on a
single flat colour that Plymouth also paints the rest of the screen with.
"""
import argparse, math, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tux_animation as T

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 1000.0 / T.DELAY_MS                     # 14.286, same cadence as the GIF

# dark, walk in, reach, flicker, settle, beat, walk to desk, sit, wake, -, -
INTRO_PHASES = (3, 20, 6, 3, 10, 2, 20, 9, 5, 1, 1)

# Every oscillator in the typing pose divides into this, so the loop is seamless:
# flippers 4f, body bob 8f, screen flicker 4f, steam exactly 2 periods.
LOOP_FRAMES = 40
STEAM_PERIOD = 2 * math.pi / 0.85             # with STEAM_BREATH == 0.85


def loop_frame(n):
    osc = math.sin(2 * math.pi * n / 4.0)
    cfg = T.sit_pose(y=T.SEAT_Y - T.FEET + 0.6 * math.sin(2 * math.pi * n / 8.0),
                     flip_near=74 + 7 * osc, flip_far=70 - 7 * osc)
    cfg["blink"] = n in (18, 19)
    ex = dict(L=1.0, cone=1.0, bulb=0.0, screen=1.0 + 0.05 * osc)
    return cfg, ex


def bullet_png(path, size=11, color=(206, 202, 192)):
    from PIL import Image, ImageDraw
    ss = 8
    im = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([ss, ss, (size - 1) * ss, (size - 1) * ss], fill=color + (255,))
    im.resize((size, size), Image.LANCZOS).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "tux"),
                    help="theme directory to build")
    ap.add_argument("--install-dir", default="/usr/share/plymouth/themes/tux",
                    help="path the theme will live at once installed")
    ap.add_argument("--scale", type=float, default=1.0,
                    help="frame size multiplier (1.0 = 640x400; 2.0 doubles RAM use)")
    ap.add_argument("--every", type=int, default=1,
                    help="keep only every Nth intro frame (halves RAM at N=2)")
    args = ap.parse_args()

    w = int(round(T.W * args.scale))
    h = int(round(T.H * args.scale))

    # Plymouth build: flat background, no vignette, steam that loops cleanly.
    T.FLAT_BG = True
    T.OUT_SIZE = (w, h)
    T.STEAM_BREATH = 0.85
    T.STEAM_STEP = 2 * STEAM_PERIOD / LOOP_FRAMES
    T.set_timeline(INTRO_PHASES)

    out = args.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    intro_end = T.pI[1]                       # through "screen wakes up"
    kept = list(range(0, intro_end, max(1, args.every)))
    for n, i in enumerate(kept):
        T.render(i).convert("RGB").save(os.path.join(out, "intro-%d.png" % n))

    steam0 = intro_end * T.STEAM_STEP
    for n in range(LOOP_FRAMES):
        cfg, ex = loop_frame(n)
        img = T.render_frame(cfg, ex, steam0 + n * T.STEAM_STEP)
        img.convert("RGB").save(os.path.join(out, "loop-%d.png" % n))

    bullet_png(os.path.join(out, "bullet.png"))

    bg = tuple(round(c / 255.0, 4) for c in T.BG_BOT)
    subs = {
        "@FPS@": "%.4f" % (FPS / max(1, args.every)),
        "@INTRO_COUNT@": str(len(kept)),
        "@LOOP_COUNT@": str(LOOP_FRAMES),
        "@FRAME_W@": str(w),
        "@FRAME_H@": str(h),
        "@BG_R@": str(bg[0]), "@BG_G@": str(bg[1]), "@BG_B@": str(bg[2]),
        "@THEME_DIR@": args.install_dir,
    }
    for src, dst in (("tux.script.in", "tux.script"),
                     ("tux.plymouth.in", "tux.plymouth")):
        text = open(os.path.join(HERE, src)).read()
        for k, v in subs.items():
            text = text.replace(k, v)
        open(os.path.join(out, dst), "w").write(text)

    total = len(kept) + LOOP_FRAMES
    size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
    print("theme:        %s" % out)
    print("frames:       %d intro + %d loop = %d  (%dx%d)"
          % (len(kept), LOOP_FRAMES, total, w, h))
    print("intro length: %.1fs at %.1f fps" % (len(kept) / (FPS / max(1, args.every)),
                                               FPS / max(1, args.every)))
    print("on disk:      %.1f MiB   (initramfs grows by roughly this)" % (size / 2**20))
    print("in RAM:       %.0f MiB   (%d frames x %dx%d x 4B, decoded by plymouthd)"
          % (total * w * h * 4 / 2**20, total, w, h))


if __name__ == "__main__":
    main()
