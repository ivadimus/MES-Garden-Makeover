import cv2
import os

src = r"c:\Users\vadimt\OneDrive - Playtika Ltd\Desktop\Recording 2026-09-22 184618.mp4"
out = os.path.join(os.path.dirname(__file__), "_wipe-ref")
os.makedirs(out, exist_ok=True)

cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
print(f"video {w}x{h} fps={fps:.2f} frames={n} dur={n / max(fps, 1):.2f}s")

indices = sorted(set([0, 1, 2, 3, 4, 5, 6, 8, 10] + [int(i * (n - 1) / 14) for i in range(15)]))
saved = []
for idx in indices:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok:
        continue
    scale = 720 / max(frame.shape[1], 1)
    if scale < 1:
        frame = cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)))
    path = os.path.join(out, f"frame_{idx:04d}.jpg")
    cv2.imwrite(path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    saved.append(path)

cap.release()
print("saved", len(saved))
for p in saved:
    print(p)
