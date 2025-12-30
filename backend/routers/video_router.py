"""Handles API endpoints for uploading and managing video files."""

import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

VIDEO_PROCESSING_DIR = Path("video_processing")
VIDEO_PROCESSING_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Accepts a video file and saves it to the video_processing directory.
    """
    destination_path = VIDEO_PROCESSING_DIR / file.filename
    try:
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "message": "Video uploaded successfully"}
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"File error during upload: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during upload: {e}") from e
    finally:
        if file and not file.file.closed:
            file.file.close()
