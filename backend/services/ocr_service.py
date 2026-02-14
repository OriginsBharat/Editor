"""
This service handles the Optical Character Recognition (OCR) part of the video processing pipeline.
It is responsible for detecting text in video frames.
"""
import logging
from typing import List, Dict, Any
import cv2
# from paddleocr import PaddleOCR # Removed from top-level to enable true lazy loading
from langdetect import detect, LangDetectException

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
        from paddleocr import PaddleOCR  # Import is now inside the function
        # Initialize the PaddleOCR engine with the correct parameter
        OCR_ENGINE = PaddleOCR(use_angle_cls=True, lang='ch')
        log.info("PaddleOCR engine loaded successfully.")
    return OCR_ENGINE

from typing import Tuple

def extract_frames_from_video(video_path: str) -> Tuple[List[Any], float]:
    """
    Extracts ALL frames from a video file and returns them along with the video's FPS.
    If FPS metadata is missing or invalid, it defaults to a standard 30.0 FPS.
    """
    frames = []
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        log.error("Could not open video file: %s", video_path)
        return frames, 0.0 # Return empty list and 0.0 fps on failure

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 0:
        log.warning("Video FPS metadata is missing or zero, defaulting to 30.0 FPS.")
        fps = 30.0

    frame_count = 0
    while True:
        success, frame = video_capture.read()
        if not success:
            break # End of video
        frames.append(frame)
        frame_count += 1

    video_capture.release()
    log.info("Successfully extracted %d frames at %.2f FPS.", frame_count, fps)
    return frames, fps

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
                    log.info("OCR detected text: '%s' with confidence: %f", text, confidence)

                    # Use a robust language detection library to specifically target Chinese.
                    # The old method (checking unicode range) incorrectly removed Japanese Kanji.
                    try:
                        lang = detect(text)
                        if lang == 'zh-cn':
                            log.info("Confirmed as Simplified Chinese. Adding for removal.")
                            frame_detections.append({
                                "text": text,
                                "confidence": float(confidence),
                                "bounding_box": box
                            })
                        else:
                            log.info("Detected language ('%s') is not Chinese. Keeping text.", lang)
                    except LangDetectException:
                        log.warning("Could not detect language for text: '%s'. Assuming it's not Chinese.", text)
                else:
                    log.warning("Skipping detection with unexpected format: %s", rec_info)

        if frame_detections:
            log.info("Found %d Chinese text instances in frame %d.", len(frame_detections), i + 1)
            detection_results.append({
                "frame_number": i,
                "detections": frame_detections
            })

    return detection_results
