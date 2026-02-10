"""
Webcam Utility Module

Handles initialization and setup of webcam streams for real-time angle measurement.
Provides convenient access to the default system webcam using OpenCV's VideoCapture.
"""

import cv2
import imutils


class Webcam:
    """
    Utility class for accessing webcam streams.

    Encapsulates webcam initialization logic, providing a standardized interface
    for the main application to access live camera feeds.
    """

    @staticmethod
    def main():
        """
        Initialize and return a VideoCapture object for the default webcam.

        Opens the default system webcam (index 0) using OpenCV's VideoCapture.
        The returned object can be used to read frames from the live camera feed.

        Returns:
            tuple: A tuple containing:
                - path2 (int): The camera index (0 for default/built-in webcam)
                - cam (cv2.VideoCapture): OpenCV VideoCapture object for the webcam
        """
        path2 = 0
        cam = cv2.VideoCapture(path2)

        return path2, cam
