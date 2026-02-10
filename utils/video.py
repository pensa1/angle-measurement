"""
Video Utility Module

Handles loading and setup of video files for angle measurement. Provides functionality
to open video files and prepare them for frame-by-frame processing with angle tracking.
"""

import cv2
import imutils


class Video:
    """
    Utility class for accessing video file streams.

    Encapsulates video file initialization logic, providing a standardized interface
    for the main application to access and process video frames.
    """

    @staticmethod
    def main():
        """
        Initialize and return a VideoCapture object for a sample video file.

        Opens a predefined sample video file from the video/ directory using
        OpenCV's VideoCapture. The returned object can be used to read frames
        sequentially from the video.

        Returns:
            tuple: A tuple containing:
                - path2 (str): The file path to the video file ('video/sample.mp4')
                - cam (cv2.VideoCapture): OpenCV VideoCapture object for the video
        """
        path2 = 'video/sample.mp4'
        cam = cv2.VideoCapture(path2)

        return path2, cam
