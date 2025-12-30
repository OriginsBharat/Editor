"""
This service handles the Optical Character Recognition (OCR) part of the video processing pipeline.
It is responsible for detecting text in video frames.
"""
import cv2
from paddleocr import PaddleOCR
from typing import List, Dict, Any

# Initialize the PaddleOCR engine for Chinese and English
# This is done once when the module is loaded to be efficient.
# The models are automatically downloaded on the first run.
print("Initializing PaddleOCR engine...")
ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch')
print("PaddleOCR engine initialized successfully.")

def extract_frames_from_video(video_path: str, interval_seconds: int = 1) -> List[Any]:
    """
    Extracts frames from a video file at a specified interval.

    Args:
        video_path: The path to the video file.
        interval_seconds: The interval in seconds at which to extract frames.

    Returns:
        A list of video frames (as numpy arrays).
    """
    frames = []
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return frames

    fps = video_capture.get(cv2.CAP_PROP_FPS)
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

    Args:
        frames: A list of video frames (as numpy arrays).

    Returns:
        A list of dictionaries, where each dictionary contains the OCR
        results for a single frame.
    """
    detection_results = []
    for i, frame in enumerate(frames):
        print(f"Processing frame {i+1}/{len(frames)}...")
        result = ocr_engine.ocr(frame, cls=True)

        # The result from PaddleOCR is a list of lists of detections for each frame.
        # We process it to be more structured.
        frame_detections = []
        if result and result[0] is not None:
            for line in result[0]:
                box = line[0]
                text, confidence = line[1]
                frame_detections.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bounding_box": box
                })

        if frame_detections:
            detection_results.append({
                "frame_number": i,
                "detections": frame_detections
            })

    return detection_results
