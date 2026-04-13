import sys
sys.path.append(r'd:\versight\versight_with_backend\versight\backend')
import json
from model import DeepfakeDetector

try:
    print("Loading detector...")
    detector = DeepfakeDetector()
    print("Analyzing...")
    result = detector.analyze_video('C:\\Users\\THINKPAD\\Downloads\\test_clip.mp4')
    
    # Save the output to a raw file
    with open("direct_output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print("Keys in top-level JSON:", list(result.keys()))
    print("Keys in details object:", list(result.get('details', {}).keys()))
    print("Gemini Logic Context text:", result.get('gemini_context', 'NOT FOUND!'))
except Exception as e:
    print("Error:", e)
