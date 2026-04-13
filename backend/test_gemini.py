from PIL import Image
import numpy as np

# Create a blank red image to simulate a video frame
dummy1 = Image.fromarray(np.full((256, 256, 3), (255, 0, 0), dtype=np.uint8))
dummy2 = Image.fromarray(np.full((256, 256, 3), (0, 255, 0), dtype=np.uint8))

print("Loading DeepfakeDetector...")
from model import DeepfakeDetector
detector = DeepfakeDetector()

print("Sending context to Gemini 1.5 Flash...")
score, reason = detector.logical_forensics([dummy1, dummy2])

print(f"Gemini Anomaly Score: {score}")
print(f"Gemini Reasoning: {reason}")
