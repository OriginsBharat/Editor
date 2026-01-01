"""
This service handles the Optical Character Recognition (OCR) part of the video processing pipeline.
It is responsible for detecting text in video frames.
"""
import cv2
import os
import logging
from paddleocr import PaddleOCR
from typing import List, Dict, Any

# --- Logging Setup ---
log = logging.getLogger(__name__)

# --- Lazy Loading for PaddleOCR Model ---
_ocr_engine = None

def _get_ocr_engine():
    """
    Initializes and returns the PaddleOCR engine instance.
    This function ensures the model is only loaded once.
    """
    global _ocr_engine
    if _ocr_engine is None:
        log.info("Lazy loading the PaddleOCR engine...")
        # Initialize the PaddleOCR engine with the updated parameter
        _ocr_engine = PaddleOCR(use_textline_orientation=True, lang='ch')
        log.info("PaddleOCR engine loaded successfully.")
    return _ocr_engine

def extract_frames_from_video(video_path: str, interval_seconds: int = 1) -> List[Any]:
    """
    Extracts frames from a video file at a specified interval.
    """
    frames = []
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        log.error(f"Could not open video file at {video_path}")
        return frames

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        frame_interval = 1
    else:
        frame_interval = int(fps * interval_seconds)

    frame_count = 0

    while True:
        success, frame = video_capture.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            frames.append(frame)

        frame_count += 1

    video_capture.release()
    return frames

def detect_text_in_frames(frames: List[Any]) -> List[Dict[str, Any]]:
    """
    Detects Chinese text in a list of video frames using PaddleOCR.
    """
    ocr_engine = _get_ocr_engine()
    detection_results = []

    for i, frame in enumerate(frames):
        log.info(f"Processing frame {i+1}/{len(frames)} for text detection...")
        result = ocr_engine.predict(frame)

        frame_detections = []
        if result and result[0] is not None:
            texts = result[0].get('rec_texts', [])
            scores = result[0].get('rec_scores', [])
            boxes = result[0].get('dt_polys', [])

            for text, score, box in zip(texts, scores, boxes):
                frame_detections.append({
                    "text": text,
                    "confidence": float(score),
                    "bounding_box": box
                })

        if frame_detections:
            log.info(f"Found {len(frame_detections)} text instances in frame {i+1}.")
            detection_results.append({
                "frame_number": i,
                "detections": frame_detections
            })

    return detection_results
