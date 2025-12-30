"""Handles API endpoints for processing user commands."""

import os
from typing import Dict
from fastapi import APIRouter, Body, HTTPException
from backend.services import llm_service, ocr_service

router = APIRouter()
VIDEO_PROCESSING_DIR = "video_processing"

@router.post("/command")
async def process_command(payload: Dict[str, str] = Body(...)):
    """
    Accepts a command and a video filename.
    If the command is to remove text, it triggers the OCR service on the video.
    """
    command = payload.get("command")
    video_filename = payload.get("video_filename")

    if not command:
        raise HTTPException(status_code=422, detail="Command not provided")
    if not video_filename:
        raise HTTPException(status_code=422, detail="Video filename not provided")

    # Get the structured command from the LLM
    llm_response = llm_service.parse_command(command)

    if llm_response.get("error"):
        return llm_response

    # If the action is 'remove_text', start the OCR pipeline
    if llm_response.get("action") == "remove_text":
        video_path = os.path.join(VIDEO_PROCESSING_DIR, video_filename)

        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail=f"Video file not found: {video_filename}")

        print(f"Starting OCR process for {video_path}...")
        frames = ocr_service.extract_frames_from_video(video_path, interval_seconds=1)
        if not frames:
            return {"message": "No frames were extracted from the video."}

        detection_results = ocr_service.detect_text_in_frames(frames)
        if not detection_results:
            return {"message": "No text was detected in the specified language."}

        return {"ocr_results": detection_results}

    return llm_response
