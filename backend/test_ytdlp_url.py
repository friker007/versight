import yt_dlp

def test():
    url = "https://www.instagram.com/reels/CUshqengb-n/"
    ydl_opts = {
        'format': 'best',
        'quiet': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("Direct URL:")
        print(info.get('url'))

if __name__ == "__main__":
    test()
