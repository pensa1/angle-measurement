"""
Detection module for automatic line detection using Canny and Hough Transform.

This module provides automatic line detection capabilities for the angle
measurement tool using OpenCV's Canny edge detection and Probabilistic
Hough Transform.

Modules:
    preprocessor: Image preprocessing pipeline (grayscale, blur, CLAHE, etc.)
    line_detector: Core Canny + Hough Transform line detection
    postprocessor: Line merging, filtering, and angle detection

Example usage::

    >>> import cv2
    >>> from detection import LineDetector
    >>>
    >>> img = cv2.imread("img/sample.jpg")
    >>> detector = LineDetector()
    >>> result = detector.detect(img)
    >>>
    >>> print(f"Detected {len(result.lines)} lines")
    >>> print(f"Found {len(result.angle_measurements)} angle measurements")
"""

from detection.line_detector import LineDetector, LineDetectorConfig
from detection.postprocessor import LinePostprocessor, PostprocessorConfig
from detection.preprocessor import ImagePreprocessor, PreprocessorConfig

__all__ = [
    "LineDetector",
    "LineDetectorConfig",
    "LinePostprocessor",
    "PostprocessorConfig",
    "ImagePreprocessor",
    "PreprocessorConfig",
]
