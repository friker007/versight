import requests
import json
import time

url = "http://127.0.0.1:8081/api/analyze/url"
# W3Schools sample video
payload = {"url": "https://www.w3schools.com/html/mov_bbb.mp4"}

print(f"Sending to {url} ...")
t0 = time.time()
try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Response HTTP Status: {response.status_code} in {time.time()-t0:.2f}s")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
