import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.chdir(os.path.dirname(__file__))

from model import DeepfakeDetector

print("Initializing detector...")
t0 = time.time()
detector = DeepfakeDetector()
print(f"Init took {time.time()-t0:.2f}s")

video = r"C:\Users\THINKPAD\Downloads\test_clip.mp4"
print(f"\nAnalyzing: {video}")
t1 = time.time()
result = detector.analyze_video(video)
elapsed = time.time() - t1
print(f"Analysis took {elapsed:.2f}s")

# Print summary (no base64 blobs)
summary = {k: v for k, v in result.items() if k not in ("per_frame", "face_crops")}
print("\n=== RESULTS ===")
print(json.dumps(summary, indent=2))
print(f"\nFrames: {len(result.get('per_frame',[]))}")
print(f"Face crops: {len(result.get('face_crops',[]))}")

if result.get("per_frame"):
    print("\n--- Per-Frame ---")
    for fr in result["per_frame"]:
        flag = "!!" if fr["score"] > 55 else "ok"
        print(f"  [{flag}] #{fr['frame_index']:>5} @ {fr['timestamp']:>6.2f}s -> {fr['score']:>5.1f}%  ({fr['faces_detected']} faces)")
