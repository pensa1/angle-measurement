"""
Window Manager Module

Manages OpenCV windows and trackbars for the angle measurement tool.
Provides parameter tuning interface with real-time updates and callback system.

Classes:
    WindowManager: Main window and trackbar management
    DetectionParameters: Data class for detection parameter values

Key Features:
    - Window creation and management
    - Trackbar controls for detection parameters
    - Real-time parameter updates via callbacks
    - Keyboard shortcut handling
    - Multi-window layout support
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple, Any


@dataclass
class DetectionParameters:
    """
    Container for line detection parameters.

    Attributes:
        canny_low: Lower threshold for Canny edge detection (0-255)
        canny_high: Upper threshold for Canny edge detection (0-255)
        hough_threshold: Hough transform threshold (0-200)
        min_line_length: Minimum line length in pixels (10-200)
        max_line_gap: Maximum gap between line segments (0-50)
    """
    canny_low: int = 50
    canny_high: int = 150
    hough_threshold: int = 50
    min_line_length: int = 50
    max_line_gap: int = 10

    def to_dict(self) -> Dict[str, int]:
        """Convert parameters to dictionary."""
        return {
            'canny_low': self.canny_low,
            'canny_high': self.canny_high,
            'hough_threshold': self.hough_threshold,
            'min_line_length': self.min_line_length,
            'max_line_gap': self.max_line_gap
        }

    @classmethod
    def from_dict(cls, params: Dict[str, int]) -> 'DetectionParameters':
        """Create parameters from dictionary."""
        return cls(
            canny_low=params.get('canny_low', 50),
            canny_high=params.get('canny_high', 150),
            hough_threshold=params.get('hough_threshold', 50),
            min_line_length=params.get('min_line_length', 50),
            max_line_gap=params.get('max_line_gap', 10)
        )


class WindowManager:
    """
    Manages OpenCV windows and trackbars for parameter tuning.

    Provides an interface for creating windows with parameter controls,
    handling real-time updates, and managing keyboard shortcuts.

    Attributes:
        window_name: Name of the main OpenCV window
        parameters: Current detection parameter values
        callbacks: Dictionary of parameter change callbacks

    Example:
        >>> manager = WindowManager("Parameter Tuning")
        >>> manager.create_detection_trackbars()
        >>>
        >>> # Register callback for parameter changes
        >>> def on_param_change(params):
        ...     print(f"Parameters updated: {params}")
        >>> manager.add_callback(on_param_change)
        >>>
        >>> # Main loop
        >>> while True:
        ...     manager.show_image(image)
        ...     key = manager.wait_key(1)
        ...     if key == 'q':
        ...         break
    """

    # Default parameter values
    DEFAULT_PARAMS = DetectionParameters()

    # Parameter presets for different lighting conditions
    PRESETS = {
        'default': DetectionParameters(50, 150, 50, 50, 10),
        'bright': DetectionParameters(80, 200, 60, 40, 8),
        'dark': DetectionParameters(30, 100, 40, 60, 15),
        'high_contrast': DetectionParameters(100, 250, 70, 30, 5),
    }

    def __init__(self, window_name: str = "Angle Measurement"):
        """
        Initialize the window manager.

        Args:
            window_name: Name for the main OpenCV window
        """
        self.window_name = window_name
        self.parameters = DetectionParameters()
        self.callbacks: Dict[str, Callable[[DetectionParameters], None]] = {}
        self._trackbars_created = False
        self._window_created = False
        self._show_help = False

    def create_window(self, width: Optional[int] = None,
                     height: Optional[int] = None) -> None:
        """
        Create the main OpenCV window.

        Args:
            width: Optional window width (None for auto)
            height: Optional window height (None for auto)
        """
        if not self._window_created:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            if width and height:
                cv2.resizeWindow(self.window_name, width, height)
            self._window_created = True

    def create_detection_trackbars(self,
                                   on_change: Optional[Callable[[DetectionParameters], None]] = None) -> None:
        """
        Create trackbars for detection parameters.

        Creates trackbars for:
        - Canny Low Threshold (0-255)
        - Canny High Threshold (0-255)
        - Hough Threshold (0-200)
        - Min Line Length (10-200)
        - Max Line Gap (0-50)

        Args:
            on_change: Optional callback function called when parameters change
        """
        if not self._window_created:
            self.create_window()

        if self._trackbars_created:
            return

        if on_change:
            self.add_callback('detection', on_change)

        # Create trackbars with default values
        cv2.createTrackbar(
            "Canny Low",
            self.window_name,
            self.parameters.canny_low,
            255,
            self._on_canny_low_change
        )

        cv2.createTrackbar(
            "Canny High",
            self.window_name,
            self.parameters.canny_high,
            255,
            self._on_canny_high_change
        )

        cv2.createTrackbar(
            "Hough Thresh",
            self.window_name,
            self.parameters.hough_threshold,
            200,
            self._on_hough_threshold_change
        )

        cv2.createTrackbar(
            "Min Line Len",
            self.window_name,
            self.parameters.min_line_length,
            200,
            self._on_min_line_length_change
        )

        cv2.createTrackbar(
            "Max Line Gap",
            self.window_name,
            self.parameters.max_line_gap,
            50,
            self._on_max_line_gap_change
        )

        self._trackbars_created = True

    def _on_canny_low_change(self, value: int) -> None:
        """Internal callback for Canny low threshold trackbar."""
        self.parameters.canny_low = value
        # Ensure canny_low <= canny_high
        if self.parameters.canny_low > self.parameters.canny_high:
            self.parameters.canny_high = self.parameters.canny_low
            cv2.setTrackbarPos("Canny High", self.window_name, self.parameters.canny_high)
        self._notify_callbacks()

    def _on_canny_high_change(self, value: int) -> None:
        """Internal callback for Canny high threshold trackbar."""
        self.parameters.canny_high = value
        # Ensure canny_high >= canny_low
        if self.parameters.canny_high < self.parameters.canny_low:
            self.parameters.canny_low = self.parameters.canny_high
            cv2.setTrackbarPos("Canny Low", self.window_name, self.parameters.canny_low)
        self._notify_callbacks()

    def _on_hough_threshold_change(self, value: int) -> None:
        """Internal callback for Hough threshold trackbar."""
        self.parameters.hough_threshold = value
        self._notify_callbacks()

    def _on_min_line_length_change(self, value: int) -> None:
        """Internal callback for min line length trackbar."""
        # Ensure minimum value of 10
        self.parameters.min_line_length = max(10, value)
        if value < 10:
            cv2.setTrackbarPos("Min Line Len", self.window_name, 10)
        self._notify_callbacks()

    def _on_max_line_gap_change(self, value: int) -> None:
        """Internal callback for max line gap trackbar."""
        self.parameters.max_line_gap = value
        self._notify_callbacks()

    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks of parameter changes."""
        for callback in self.callbacks.values():
            callback(self.parameters)

    def add_callback(self, name: str, callback: Callable[[DetectionParameters], None]) -> None:
        """
        Register a callback function for parameter changes.

        Args:
            name: Unique identifier for the callback
            callback: Function to call when parameters change.
                     Receives DetectionParameters object as argument.
        """
        self.callbacks[name] = callback

    def remove_callback(self, name: str) -> None:
        """
        Remove a registered callback.

        Args:
            name: Identifier of the callback to remove
        """
        self.callbacks.pop(name, None)

    def get_parameters(self) -> DetectionParameters:
        """
        Get current detection parameters.

        Returns:
            Current DetectionParameters object
        """
        return self.parameters

    def set_parameters(self, params: DetectionParameters) -> None:
        """
        Set detection parameters and update trackbars.

        Args:
            params: New parameter values
        """
        self.parameters = params

        if self._trackbars_created:
            cv2.setTrackbarPos("Canny Low", self.window_name, params.canny_low)
            cv2.setTrackbarPos("Canny High", self.window_name, params.canny_high)
            cv2.setTrackbarPos("Hough Thresh", self.window_name, params.hough_threshold)
            cv2.setTrackbarPos("Min Line Len", self.window_name, params.min_line_length)
            cv2.setTrackbarPos("Max Line Gap", self.window_name, params.max_line_gap)

    def load_preset(self, preset_name: str) -> bool:
        """
        Load a parameter preset.

        Args:
            preset_name: Name of preset ('default', 'bright', 'dark', 'high_contrast')

        Returns:
            True if preset loaded successfully, False otherwise
        """
        if preset_name in self.PRESETS:
            self.set_parameters(self.PRESETS[preset_name])
            return True
        return False

    def reset_to_defaults(self) -> None:
        """Reset all parameters to default values."""
        self.set_parameters(self.DEFAULT_PARAMS)

    def show_image(self, image: np.ndarray) -> None:
        """
        Display an image in the window.

        Args:
            image: Image to display (numpy array)
        """
        if not self._window_created:
            self.create_window()

        # Add help overlay if enabled
        if self._show_help:
            image = self._add_help_overlay(image.copy())

        cv2.imshow(self.window_name, image)

    def wait_key(self, delay: int = 1) -> Optional[str]:
        """
        Wait for keyboard input and handle shortcuts.

        Args:
            delay: Wait time in milliseconds

        Returns:
            Key character if printable key pressed, None otherwise

        Keyboard shortcuts:
            'r' - Reset parameters to defaults
            't' - Toggle edge visualization (handled by caller)
            'd' - Toggle detection overlay (handled by caller)
            's' - Save current parameters (handled by caller)
            'h' - Toggle help overlay
            'q' or ESC - Quit
        """
        key = cv2.waitKey(delay) & 0xFF

        if key == 255:  # No key pressed
            return None

        # Handle special keys
        if key == 27:  # ESC
            return 'q'
        elif key == ord('r'):
            self.reset_to_defaults()
            return 'r'
        elif key == ord('h'):
            self._show_help = not self._show_help
            return 'h'
        elif key in [ord('t'), ord('d'), ord('s'), ord('q')]:
            return chr(key)
        elif 32 <= key < 127:  # Printable ASCII
            return chr(key)

        return None

    def _add_help_overlay(self, image: np.ndarray) -> np.ndarray:
        """
        Add help text overlay to image.

        Args:
            image: Image to annotate

        Returns:
            Image with help overlay
        """
        overlay = image.copy()
        h, w = image.shape[:2]

        # Semi-transparent background
        cv2.rectangle(overlay, (10, 10), (400, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)

        # Help text
        help_text = [
            "KEYBOARD SHORTCUTS:",
            "",
            "r - Reset parameters to defaults",
            "t - Toggle edge visualization",
            "d - Toggle detection overlay",
            "s - Save current parameters",
            "h - Toggle this help",
            "q/ESC - Quit",
            "",
            "Presets: 1-Default, 2-Bright",
            "         3-Dark, 4-High Contrast"
        ]

        y = 30
        for line in help_text:
            cv2.putText(
                image, line, (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 1, cv2.LINE_AA
            )
            y += 20

        return image

    def destroy(self) -> None:
        """Clean up and close the window."""
        if self._window_created:
            cv2.destroyWindow(self.window_name)
            self._window_created = False
            self._trackbars_created = False

    @staticmethod
    def destroy_all_windows() -> None:
        """Close all OpenCV windows."""
        cv2.destroyAllWindows()


class MultiWindowManager:
    """
    Manages multiple windows for side-by-side comparison.

    Useful for showing original image, edge detection, and final detection
    results simultaneously.

    Example:
        >>> manager = MultiWindowManager()
        >>> manager.create_windows(['Original', 'Edges', 'Detected'])
        >>> manager.show('Original', original_img)
        >>> manager.show('Edges', edges_img)
        >>> manager.show('Detected', detected_img)
    """

    def __init__(self):
        """Initialize multi-window manager."""
        self.windows: Dict[str, str] = {}

    def create_windows(self, window_names: list) -> None:
        """
        Create multiple windows.

        Args:
            window_names: List of window names to create
        """
        for name in window_names:
            cv2.namedWindow(name, cv2.WINDOW_NORMAL)
            self.windows[name] = name

    def show(self, window_name: str, image: np.ndarray) -> None:
        """
        Display image in specified window.

        Args:
            window_name: Name of window
            image: Image to display
        """
        if window_name in self.windows:
            cv2.imshow(window_name, image)
        else:
            # Create window if it doesn't exist
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            self.windows[window_name] = window_name
            cv2.imshow(window_name, image)

    def arrange_windows(self, layout: str = 'horizontal') -> None:
        """
        Arrange windows on screen.

        Args:
            layout: 'horizontal' or 'vertical' arrangement
        """
        # Note: Window positioning is OS-dependent and may not work on all systems
        x_offset = 0
        y_offset = 0
        window_width = 640
        window_height = 480

        for i, name in enumerate(self.windows.keys()):
            if layout == 'horizontal':
                cv2.moveWindow(name, x_offset, 0)
                x_offset += window_width
            else:  # vertical
                cv2.moveWindow(name, 0, y_offset)
                y_offset += window_height

    def destroy_all(self) -> None:
        """Close all managed windows."""
        for name in self.windows.keys():
            cv2.destroyWindow(name)
        self.windows.clear()
