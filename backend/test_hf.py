from transformers import pipeline
import time

print("Loading prithivMLmods/Deep-Fake-Detector-Model...")
t0 = time.time()
try:
    pipe = pipeline("image-classification", model="prithivMLmods/Deep-Fake-Detector-Model")
    print(f"Loaded successfully in {time.time()-t0:.2f}s!")
    from PIL import Image
    import numpy as np
    dummy = Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8))
    out = pipe(dummy)
    print("Inference output structure:")
    print(out)
    print("Test passed.")
except Exception as e:
    print(f"Error loading model: {e}")
