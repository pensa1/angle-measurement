"""
Image Utility Module

Handles loading and preparing images for angle measurement. Provides functionality
to load images from disk and apply standard preprocessing (resizing) for consistent
display and processing.
"""

import cv2
import imutils


class Image:
    """
    Utility class for loading and preparing images.

    This class encapsulates image loading logic, providing a standardized interface
    for the main application to access image data with consistent preprocessing.
    """

    @staticmethod
    def main():
        """
        Load a sample image and resize it to a standard height.

        Loads a predefined sample image from the img/ directory and resizes it
        to maintain a consistent display height of 600 pixels while preserving
        aspect ratio.

        Returns:
            tuple: A tuple containing:
                - path (str): The file path to the loaded image ('img/sample.jpg')
                - img (numpy.ndarray): The loaded and resized image as a BGR array
        """
        path = 'img/sample.jpg'
        img = cv2.imread(path)
        img = imutils.resize(img, height=600)

        return path, img

