import os
import sys
# Make sure we can load the project code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import DeepfakeDetector
import cv2
from PIL import Image
import numpy as np

def run_tests():
    print("Loading model...")
    detector = DeepfakeDetector()
    print("Model loaded.")

    # Create a dummy frame (random noise simulating an image)
    frame_np = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
    frame_pil = Image.fromarray(frame_np)

    print("\n--- Testing evaluate_frame_general ---")
    gen_score = detector.evaluate_frame_general(frame_pil)
    print(f"gen_score: {gen_score}")

    print("\n--- Testing noise_residual_analysis ---")
    noise_score = detector.noise_residual_analysis(frame_np)
    print(f"noise_score: {noise_score}")

    print("\n--- Testing spectral_decay_analysis ---")
    spec_score = detector.spectral_decay_analysis(frame_np)
    print(f"spec_score: {spec_score}")

if __name__ == "__main__":
    run_tests()
