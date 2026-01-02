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
        # Initialize the PaddleOCR engine with the correct parameter
        OCR_ENGINE = PaddleOCR(use_angle_cls=True, lang='ch')
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
        # Fallback for videos with missing FPS metadata
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
    The result format from ocr() is a list for each image:
    [
        [box, (text, confidence)],
        [box, (text, confidence)],
        ...
    ]
    Each 'box' is a list of 4 points (vertices of the bounding box).
    """
    ocr_engine = _get_ocr_engine()
    detection_results = []

    for i, frame in enumerate(frames):
        log.info("Processing frame %d/%d for text detection...", i + 1, len(frames))
        # The `use_angle_cls` parameter in the constructor handles classification.
        # The `ocr` method itself does not take a 'cls' argument.
        result = ocr_engine.ocr(frame)

        frame_detections = []
        # The result is a list of lines, where each line contains detections
        if result and result[0] is not None:
            for line in result[0]:
                box = line[0]
                rec_info = line[1]

                # Add a check to ensure rec_info is a tuple/list with two elements
                if isinstance(rec_info, (list, tuple)) and len(rec_info) == 2:
                    text, confidence = rec_info
                    log.info("OCR detected text: '%s' with confidence: %f", text, confidence) # DEBUG LOG

                    # We are only interested in removing Chinese text for this project
                    # A simple heuristic: check if the text contains Chinese characters.
                    if any('\u4e00' <= char <= '\u9fff' for char in text):
                        frame_detections.append({
                            "text": text,
                            "confidence": float(confidence),
                            "bounding_box": box
                        })
                else:
                    log.warning("Skipping detection with unexpected format: %s", rec_info)

        if frame_detections:
            log.info("Found %d Chinese text instances in frame %d.", len(frame_detections), i + 1)
            detection_results.append({
                "frame_number": i,
                "detections": frame_detections
            })

    return detection_results
