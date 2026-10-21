import cv2
import os
import numpy as np

src = r"c:\Users\vadimt\OneDrive - Playtika Ltd\Desktop\watermarked_preview.mp4"
out = os.path.join(os.path.dirname(__file__), "splash-frames")
os.makedirs(out, exist_ok=True)

for name in os.listdir(out):
    if name.startswith("splash_"):
        os.remove(os.path.join(out, name))

cap = cv2.VideoCapture(src)
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
print(f"frames={n} fps={fps}")

# One splash cycle (~35 frames); video loops the effect.
CYCLE_START = 0
CYCLE_END = 34  # inclusive

frames_bgr = []
alphas = []
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if CYCLE_START <= i <= CYCLE_END:
        frames_bgr.append(frame.copy())
        b, g, r = cv2.split(frame)
        lum = r.astype(np.int16) + g.astype(np.int16) + b.astype(np.int16)
        chroma = np.maximum(
            np.maximum(
                np.abs(r.astype(np.int16) - g.astype(np.int16)),
                np.abs(g.astype(np.int16) - b.astype(np.int16)),
            ),
            np.abs(r.astype(np.int16) - b.astype(np.int16)),
        )
        # Keep blue/cyan splash + white highlights; drop black bg + grey watermark.
        is_blue = (
            (b.astype(np.int16) > 70)
            & (b.astype(np.int16) >= r.astype(np.int16) + 15)
        )
        is_highlight = (lum > 500) & (chroma < 40)  # white shine on splash
        is_bright_blue = (lum > 180) & (b.astype(np.int16) > r.astype(np.int16))
        # Grey watermark: mid lum, low chroma
        is_watermark = (lum > 80) & (lum < 280) & (chroma < 18)
        keep = (is_blue | is_highlight | is_bright_blue) & (~is_watermark)
        # Also keep connected bright pixels that are part of splash body
        mid = (lum > 160) & (chroma > 20) & (~is_watermark)
        keep = keep | mid
        alpha = np.zeros(g.shape, np.uint8)
        alpha[keep] = 255
        # Clean small noise
        kernel = np.ones((3, 3), np.uint8)
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
        alpha_f = alpha.astype(np.float32) / 255.0
        alpha_f = cv2.GaussianBlur(alpha_f, (0, 0), 0.9)
        alphas.append((alpha_f * 255).astype(np.uint8))
    i += 1
cap.release()

ys_all, xs_all = [], []
for a in alphas:
    ys, xs = np.where(a > 20)
    if len(xs):
        xs_all.append(xs)
        ys_all.append(ys)
if not xs_all:
    raise SystemExit("no splash pixels found")
xs = np.concatenate(xs_all)
ys = np.concatenate(ys_all)
pad = 12
h0, w0 = frames_bgr[0].shape[:2]
x0, x1 = max(0, int(xs.min()) - pad), min(w0 - 1, int(xs.max()) + pad)
y0, y1 = max(0, int(ys.min()) - pad), min(h0 - 1, int(ys.max()) + pad)
print(f"bbox {x0},{y0}..{x1},{y1} size={x1 - x0 + 1}x{y1 - y0 + 1}")
print(f"extracted {len(frames_bgr)} frames")

for idx, (frame, alpha) in enumerate(zip(frames_bgr, alphas)):
    b, g, r = cv2.split(frame)
    rgba = cv2.merge([b, g, r, alpha])
    crop = rgba[y0 : y1 + 1, x0 : x1 + 1]
    cv2.imwrite(os.path.join(out, f"splash_{idx:02d}.png"), crop)

duration_ms = int(round(len(frames_bgr) / fps * 1000))
with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
    f.write(
        '{"count": %d, "fps": %.3f, "durationMs": %d}\n'
        % (len(frames_bgr), fps, duration_ms)
    )

print("wrote", len(frames_bgr), "frames, durationMs=", duration_ms)
