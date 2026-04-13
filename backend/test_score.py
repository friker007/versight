import requests
url = 'http://localhost:8081/api/analyze/upload'
try:
    with open('C:\\Users\\THINKPAD\\Downloads\\test_clip.mp4', 'rb') as f:
        r = requests.post(url, files={'file': f}, timeout=120)
    if r.status_code == 200:
        d = r.json()
        print('Logical Consistency:', d.get('details', {}).get('logical_consistency', 'NOT FOUND'), '%')
        print('Gemini Reason:', d.get('gemini_context', 'NOT FOUND'))
    else:
        print('Error:', r.status_code, r.text)
except Exception as e:
    print('Request failed:', e)
