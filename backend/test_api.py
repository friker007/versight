import requests
import json
import sys

filepath = r"C:\Users\THINKPAD\Downloads\test_clip.mp4"

print(f"Uploading: {filepath}")
print("Sending to http://localhost:8081/api/analyze/upload ...")

with open(filepath, "rb") as f:
    r = requests.post(
        "http://localhost:8081/api/analyze/upload",
        files={"file": ("test_clip.mp4", f, "video/mp4")},
        timeout=300
    )

if r.status_code != 200:
    print(f"Error {r.status_code}: {r.text}")
    sys.exit(1)

data = r.json()

# Print summary (excluding large base64 fields)
summary = {k: v for k, v in data.items() if k not in ("per_frame", "face_crops")}
print("\n=== DETECTION RESULTS ===")
print(json.dumps(summary, indent=2))

print(f"\nFrames analyzed: {len(data.get('per_frame', []))}")
print(f"Face crops returned: {len(data.get('face_crops', []))}")

# Print per-frame scores
if data.get("per_frame"):
    print("\n--- Per-Frame Scores ---")
    for fr in data["per_frame"]:
        flag = "🔴" if fr["score"] > 55 else "🟢"
        print(f"  {flag} Frame #{fr['frame_index']:>5} @ {fr['timestamp']:>6.2f}s  →  {fr['score']:>5.1f}%  ({fr['faces_detected']} faces)")

print("\nDone!")
