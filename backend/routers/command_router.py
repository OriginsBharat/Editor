"""Handles API endpoints for processing user commands."""

import os
import uuid
import shutil
import logging
import cv2
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.services import llm_service
from backend.services.ocr_service import extract_frames_from_video, detect_text_in_frames
from backend.services.inpainting_service import inpaint_frames
from backend.services.video_utils import reassemble_video

# --- Logging Setup ---
log = logging.getLogger(__name__)

router = APIRouter()
VIDEO_PROCESSING_DIR = "video_processing"
VIDEO_OUTPUT_DIR = "video_output"

# Ensure the directories for processing and output exist
os.makedirs(VIDEO_PROCESSING_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

@router.post("/process-video")
async def process_video_endpoint(
    video_file: UploadFile = File(...),
    command: str = Form(...)
):
    """
    Consolidated endpoint to accept a video and a command.
    It orchestrates the entire video processing pipeline based on the command.
    """
    if not video_file.filename:
        raise HTTPException(status_code=422, detail="No video file provided.")
    if not command:
        raise HTTPException(status_code=422, detail="No command provided.")

    log.info("Received command: '%s' for video: '%s'", command, video_file.filename)

    # Create a unique path for the video file to avoid conflicts
    unique_id = uuid.uuid4()
    video_extension = os.path.splitext(video_file.filename)[1]
    temp_video_filename = f"{unique_id}{video_extension}"
    temp_video_path = os.path.join(VIDEO_PROCESSING_DIR, temp_video_filename)

    # Save the uploaded video file securely
    try:
        log.info("Saving uploaded video to: %s", temp_video_path)
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
            buffer.flush()
            os.fsync(buffer.fileno())
        log.info("Video saved and flushed to disk successfully.")
    finally:
        video_file.file.close()

    if not os.path.exists(temp_video_path):
        log.error("CRITICAL: Video file was not found after saving: %s", temp_video_path)
        raise HTTPException(status_code=500, detail="Failed to save the uploaded video file.")

    try:
        # --- LLM Integration ---
        llm_response = llm_service.parse_command(command)
        action = llm_response.get("action")

        if action == "remove_text":
            log.info("Action 'remove_text' recognized. Starting video processing pipeline.")

            # 1. Extract frames
            frames = extract_frames_from_video(temp_video_path)
            if not frames:
                raise HTTPException(status_code=500, detail="Could not extract frames from video.")

            # 2. Detect text
            detection_results = detect_text_in_frames(frames)
            if not detection_results:
                log.info("No text detected. Returning original video as output for verification.")
                # For verification purposes, copy the original video to the output
                # to confirm the end-to-end pipeline is connected.
                output_video_filename = f"output_{unique_id}.mp4"
                output_video_path = os.path.join("video_output", output_video_filename)
                shutil.copyfile(temp_video_path, output_video_path)
                return {
                    "message": "No text was detected, original video returned.",
                    "output_path": output_video_filename, # Return just the filename
                    "text_detections": 0
                }

            # 3. Inpaint frames
            inpainted_frames = inpaint_frames(frames, detection_results)
            if not inpainted_frames:
                raise HTTPException(status_code=500, detail="Inpainting process failed.")

            # 4. Re-assemble video
            output_video_filename = f"output_{unique_id}.mp4"
            output_video_path = os.path.join("video_output", output_video_filename)

            # Get the original video's FPS
            cap = cv2.VideoCapture(temp_video_path)
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()

            reassemble_video(inpainted_frames, output_video_path, original_fps)

            log.info("Video processing pipeline completed successfully.")
            return {
                "message": "Text removal process completed successfully.",
                "output_path": output_video_filename, # Return just the filename
                "text_detections": len(detection_results)
            }

        log.warning("LLM did not return a recognized action. Response: %s", llm_response)
        # For now, just return the LLM's response if the action isn't recognized
        return llm_response

    finally:
        # --- Cleanup ---
        # Ensure the temporary video file is always deleted
        log.info("Cleaning up temporary file: %s", temp_video_path)
        os.remove(temp_video_path)
