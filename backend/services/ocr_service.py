"""
This service handles the Optical Character Recognition (OCR) part of the video processing pipeline.
It is responsible for detecting text in video frames.
"""
import logging
from typing import List, Dict, Any
import cv2
from paddleocr import PaddleOCR

# --- Logging Setup ---
log = logging.getLogger(__name__)

# --- Lazy Loading for PaddleOCR Model ---
OCR_ENGINE = None

def _get_ocr_engine():
    """
    Initializes and returns the PaddleOCR engine instance.
    This function ensures the model is only loaded once.
    """
    global OCR_ENGINE
    if OCR_ENGINE is None:
        log.info("Lazy loading the PaddleOCR engine...")
        # Initialize the PaddleOCR engine with the updated parameter
        OCR_ENGINE = PaddleOCR(use_textline_orientation=True, lang='ch')
        log.info("PaddleOCR engine loaded successfully.")
    return OCR_ENGINE

def extract_frames_from_video(video_path: str, interval_seconds: int = 1) -> List[Any]:
    """
    Extracts frames from a video file at a specified interval.
    """
    frames = []
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        log.error("Could not open video file at %s", video_path)
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
        log.info("Processing frame %d/%d for text detection...", i + 1, len(frames))
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
            log.info("Found %d text instances in frame %d.", len(frame_detections), i + 1)
            detection_results.append({
                "frame_number": i,
                "detections": frame_detections
            })

    return detection_results
