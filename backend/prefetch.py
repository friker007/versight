from transformers import pipeline
import time

print("Starting synchronous ViT pre-fetch...")
t0 = time.time()
try:
    pipe = pipeline("image-classification", model="prithivMLmods/Deep-Fake-Detector-Model")
    print(f"Model successfully saved to HuggingFace cache in {time.time()-t0:.2f} seconds.")
except Exception as e:
    print(f"Fetch failed: {e}")
