import requests
import json
import time
import os

def check():
    print("Checking server health...")
    api_root = "http://127.0.0.1:8010"
    try:
        hr = requests.get(f"{api_root}/health", timeout=5)
        print(f"Health check status: {hr.status_code}, Response: {hr.json()}")
    except Exception as e:
        print(f"Server appears down: {e}")
        return

    print("Hitting stream analysis API...")
    try:
        url = f"{api_root}/api/analyze/stream/url"
        # Using a reliable test video (Big Buck Bunny)
        payload = {"url": "https://www.youtube.com/watch?v=aqz-KE-BPKQ"}
        r = requests.post(url, json=payload, stream=True, timeout=120)
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    data = json.loads(decoded_line[6:])
                    print(f"[EVENT] Status: {data.get('status')}, Step: {data.get('step', 'N/A')}")
                    if data.get('status') == 'complete':
                        print("\nANALYSIS COMPLETE!")
                        print(f"Final Score: {data['result']['score']}")
                        print(f"Deepfake Detected: {data['result']['is_deepfake']}")
    except Exception as e:
        print("Request failed:", e)

    time.sleep(2)
    if os.path.exists("error_trace.txt"):
        with open("error_trace.txt", "r") as f:
            print("\nTRACEBACK:")
            print(f.read())
    else:
        print("\nNo error_trace.txt found.")

if __name__ == "__main__":
    check()
