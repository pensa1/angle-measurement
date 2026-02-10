"""
Core module for angle measurement geometry and data structures.

This package provides the foundational geometry calculations, line representation,
angle measurement algorithms, and data structures used throughout the
angle-measurement project.

Modules:
    geometry: Line class, AngleCalculator, and geometric utility functions.
    measurements: Data structures for storing angle measurements and detection results.
"""

from core.geometry import Line, AngleCalculator
from core.measurements import Measurement, LineDetectionResult

__all__ = [
    "Line",
    "AngleCalculator",
    "Measurement",
    "LineDetectionResult",
]
