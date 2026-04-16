import os
import sys
import subprocess
import urllib.request
import shutil
import uuid

def execute_extraction(url: str, output_dir: str = "temp_uploads") -> str:
    """
    Highly resilient media extractor designed for Windows.
    Bypasses handle inheritance and path character issues by using multiple flags
    and explicit subprocess sandbox isolation.
    """
    os.makedirs(output_dir, exist_ok=True)
    temp_filename = f"{uuid.uuid4()}"
    downloaded_file = os.path.join(output_dir, f"{temp_filename}.mp4")
    
    # Locate the embedded yt-dlp binary
    ytdlp_exe = os.path.join(os.path.dirname(sys.executable), "yt-dlp.exe")
    if not os.path.exists(ytdlp_exe):
        ytdlp_exe = "yt-dlp"

    # --restrict-filenames: Avoids ":" and "/" issues in extraction metadata
    # --no-cache-dir: Prevents the "Errno 22" invalid argument when looking for %TEMP%
    # --no-warnings: Keep stdout clean for direct URL extraction
    # --no-check-certificates: Helps in some corporate/VPN environments
    cmd = [
        ytdlp_exe, 
        "-g", 
        "--no-cache-dir", 
        "--restrict-filenames", 
        "--no-warnings", 
        "--no-check-certificates",
        url
    ]

    try:
        # Use subprocess.run with full isolation
        # stdin=subprocess.DEVNULL prevents inheriting broken parent process pipes (Errno 22)
        proc = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        direct_url = proc.stdout.strip().split('\n')[0] # Get the first video URL if multiple
        
        if not direct_url or not direct_url.startswith("http"):
            raise Exception("No direct playable URL resolved.")

        # Stream the payload directly to disk
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(direct_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response, open(downloaded_file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        if not os.path.exists(downloaded_file) or os.path.getsize(downloaded_file) < 1000:
            raise Exception("Resolved file is missing or corrupted.")

        return downloaded_file

    except subprocess.CalledProcessError as e:
        stderr_snippet = e.stderr[:200] if e.stderr else "No stderr"
        raise Exception(f"yt-dlp subprocess failed: {stderr_snippet}")
    except Exception as e:
        raise Exception(f"Extraction protocol failure: {str(e)}")
