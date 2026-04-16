from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import os
import uuid
import json
import time
from model import DeepfakeDetector

app = FastAPI(title="Versight AI Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model
try:
    detector = DeepfakeDetector()
except Exception as e:
    print(f"Error initializing detector: {e}")
    detector = None

def sse_generator(generator):
    try:
        for update in generator:
            yield f"data: {json.dumps(update)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'status': 'error', 'detail': str(e)})}\n\n"

class URLRequest(BaseModel):
    url: str

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    if detector is None:
        raise HTTPException(status_code=500, detail="Deepfake detector not initialized")
        
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Analyze video
        results = detector.analyze_video(temp_path)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/analyze/url")
async def analyze_url(req: URLRequest):
    if detector is None:
        raise HTTPException(status_code=500, detail="Deepfake detector not initialized")
        
    url = req.url
    temp_filename = f"{uuid.uuid4()}"
    
    downloaded_file = None
    try:
        from yt_extractor import execute_extraction
        downloaded_file = execute_extraction(url, UPLOAD_DIR)    
        if downloaded_file and os.path.exists(downloaded_file):
            results = detector.analyze_video(downloaded_file)
            return results
        else:
            raise Exception("Failed to stream video to disk")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt_extractor error: {str(e)}")
    finally:
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)

@app.post("/api/analyze/stream/upload")
async def analyze_stream_upload(file: UploadFile = File(...)):
    if detector is None:
        raise HTTPException(status_code=500, detail="Deepfake detector not initialized")
    
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    def cleanup_generator():
        try:
            for update in sse_generator(detector.analyze_video_stream(temp_path)):
                yield update
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    return StreamingResponse(cleanup_generator(), media_type="text/event-stream")

@app.post("/api/analyze/stream/url")
async def analyze_stream_url(req: URLRequest):
    if detector is None:
        raise HTTPException(status_code=500, detail="Deepfake detector not initialized")
    
    # Simple direct download for now, same as before but streaming
    # (Note: In a production app, we'd want more robust cleanup for streaming downloads)
    # We'll use a temporary file and clean it up after the stream ends
    
    url = req.url
    
    def url_generator():
        yield f"data: {json.dumps({'status': 'processing', 'step': 'Downloading remote media', 'progress': 5, 'details': 'Injecting yt-dlp web hooks...'})}\n\n"
        
        downloaded_file = None
        try:
            from yt_extractor import execute_extraction
            downloaded_file = execute_extraction(url, UPLOAD_DIR)
            
            if downloaded_file and os.path.exists(downloaded_file):
                # Now pass it into the main analyzer
                for update in sse_generator(detector.analyze_video_stream(downloaded_file)):
                    yield update
            else:
                yield f"data: {json.dumps({'status': 'error', 'detail': 'Failed to stream video chunk to disk'})}\n\n"
        except Exception as e:
            import traceback
            print("ERROR IN ANALYZE_STREAM_URL:")
            print(traceback.format_exc())
            yield f"data: {json.dumps({'status': 'error', 'detail': f'yt_extractor error: {str(e)}'})}\n\n"
        finally:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                
    return StreamingResponse(url_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": detector is not None}
