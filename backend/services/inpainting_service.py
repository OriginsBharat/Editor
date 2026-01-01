"""
This service handles the inpainting of video frames to remove detected text.
It uses the LaMa (Large Mask Inpainting) model.
"""
import os
import cv2
import torch
import numpy as np
import logging
from typing import List, Dict, Any
from .lama import LaMa

# --- Logging Setup ---
log = logging.getLogger(__name__)

# --- Lazy Loading for LaMa Model ---
# This variable will hold the model instance. It is initialized to None.
_lama_model = None

def _get_lama_model():
    """
    Initializes and returns the LaMa model instance.
    This function ensures the model is only loaded once.
    """
    global _lama_model
    if _lama_model is None:
        log.info("Lazy loading the LaMa inpainting model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Using device: {device}")
        _lama_model = LaMa(device)
        log.info("LaMa model loaded successfully.")
    return _lama_model

def inpaint_frames(frames: List[np.ndarray], detections: List[Dict[str, Any]]) -> List[np.ndarray]:
    """
    Applies inpainting to a list of frames based on text detection results.
    """
    # Get the model instance (it will be loaded on the first call)
    lama_model = _get_lama_model()

    inpainted_frames = []
    detection_map = {d["frame_number"]: d["detections"] for d in detections}

    for i, frame in enumerate(frames):
        if i in detection_map:
            log.info(f"Inpainting frame {i}...")
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)

            for detection in detection_map[i]:
                box = np.array(detection["bounding_box"], dtype=np.int32)
                cv2.fillPoly(mask, [box], 255)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            inpainted_frame_rgb = lama_model(frame_rgb, mask)

            inpainted_frame_bgr = cv2.cvtColor(inpainted_frame_rgb, cv2.COLOR_RGB2BGR)
            inpainted_frames.append(inpainted_frame_bgr)
        else:
            inpainted_frames.append(frame)

    return inpainted_frames
