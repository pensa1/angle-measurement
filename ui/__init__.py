"""
UI Module for Angle Measurement Tool

This module provides user interface components for the angle measurement tool,
including window management, trackbar controls, rendering utilities, and
interactive parameter tuning.

Components:
    - WindowManager: OpenCV window and trackbar management
    - Renderer: Visual rendering of lines, angles, and annotations
    - Parameter tuning interface with real-time feedback

Key Features:
    - Real-time parameter adjustment via trackbars
    - Visual feedback for detected and manual lines
    - Keyboard shortcuts for common operations
    - Multi-view display (original, edges, detection)
    - Interactive line editing and refinement

Usage Example:
    >>> from ui.window_manager import WindowManager
    >>> from ui.renderer import Renderer
    >>>
    >>> # Create window with parameter trackbars
    >>> manager = WindowManager("Parameter Tuning")
    >>> manager.create_detection_trackbars()
    >>>
    >>> # Render detected lines
    >>> renderer = Renderer()
    >>> annotated = renderer.draw_lines(image, lines, color=(0, 255, 0))
    >>>
    >>> # Display
    >>> manager.show_image(annotated)
"""

from ui.window_manager import WindowManager
from ui.renderer import Renderer

__all__ = ['WindowManager', 'Renderer']

__version__ = '1.0.0'
