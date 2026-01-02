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
