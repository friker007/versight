import os
import sys
# Dynamic path resolution for robust testing
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import json
from model import DeepfakeDetector

try:
    print("Loading detector...")
    detector = DeepfakeDetector()
    print("Analyzing...")
    test_vid = os.path.join(backend_dir, 'test_vid.mp4')
    if not os.path.exists(test_vid):
        raise Exception(f"Test video missing: {test_vid}")
        
    result = detector.analyze_video(test_vid)
    
    # Save the output to a raw file
    with open("direct_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print("Keys in top-level JSON:", list(result.keys()))
    print("Keys in details object:", list(result.get('details', {}).keys()))
    print("Gemini Logic Context text:", result.get('gemini_context', 'NOT FOUND!'))
except Exception as e:
    print("Error:", e)
