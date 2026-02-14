"""
This module provides utility functions for video processing, such as re-assembling
frames back into a video file.
"""
import logging
from typing import List
import cv2
import os

log = logging.getLogger(__name__)

def reassemble_video(frames: List, output_path: str, fps: float):
    """
    Re-assembles a list of frames into a video file.

    Args:
        frames: A list of video frames (as numpy arrays).
        output_path: The path to save the output video file.
        fps: The frames per second of the output video.
    """
    if not frames:
        log.error("Cannot reassemble video: The frame list is empty.")
        return

    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    log.info("Re-assembling video to %s...", output_path)
    for frame in frames:
        writer.write(frame)

    writer.release()
    log.info("Video re-assembled successfully.")

def burn_subtitle_onto_frame(frame, text: str):
    """
    Burns a single line of text onto a frame with a standard subtitle style.
    Style: White text with a black outline for readability.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (255, 255, 255)  # White
    outline_color = (0, 0, 0) # Black

    # Get text size to position it correctly
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

    # Position subtitle at the bottom center of the frame
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = frame.shape[0] - 50 # 50 pixels from the bottom

    # Draw the black outline first
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, outline_color, thickness * 2, cv2.LINE_AA)
    # Draw the white text on top
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
