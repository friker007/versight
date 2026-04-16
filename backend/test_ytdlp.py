import yt_dlp
import os
import uuid
import traceback

def test():
    url = "https://www.instagram.com/reels/CUshqengb-n/"
    UPLOAD_DIR = "temp_uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_filename = str(uuid.uuid4())
    temp_path_template = os.path.join(UPLOAD_DIR, f"{temp_filename}.%(ext)s")
    
    ydl_opts = {
        'outtmpl': temp_path_template,
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': False, # Set to False to see what yt-dlp is actually doing
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting info and downloading...")
            info = ydl.extract_info(url, download=True)
            print("Success!")
    except Exception as e:
        print("ERROR OCCURRED:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
