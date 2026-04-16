import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import DeepfakeDetector
import json

def run():
    print("Loading detector...")
    detector = DeepfakeDetector()
    
    # We will test on a dummy generated video to see what the score outputs.
    # Actually let's just make a very basic numpy video.
    import cv2
    import numpy as np
    
    out_path = "test_vid.mp4"
    if not os.path.exists(out_path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_path, fourcc, 30.0, (256, 256))
        for i in range(60):
            # purely random noise over time (flashing)
            frame = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
            out.write(frame)
        out.release()
    
    print("\nRunning analysis...")
    generator = detector.analyze_video_stream(out_path)
    
    for update in generator:
        if update.get("status") in ["tentative", "complete"]:
            details = update["result"]["details"]
            print(f"[{update['status']}] Details ->", json.dumps(details, indent=2))

if __name__ == "__main__":
    run()
