from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path

router = APIRouter()

VIDEO_PROCESSING_DIR = Path("video_processing")
VIDEO_PROCESSING_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Accepts a video file and saves it to the video_processing directory.
    """
    try:
        # Ensure the destination directory exists
        VIDEO_PROCESSING_DIR.mkdir(parents=True, exist_ok=True)

        # Define the full file path
        destination_path = VIDEO_PROCESSING_DIR / file.filename

        # Save the uploaded file
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "message": "Video uploaded successfully"}
    except Exception as e:
        return {"message": f"There was an error uploading the file: {e}"}
    finally:
        file.file.close()
