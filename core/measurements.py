"""
Data structures for storing angle measurements and line detection results.

This module provides lightweight, immutable-friendly data containers used
throughout the angle-measurement project to pass results between the
Detection, Core, and UI layers.

Classes:
    Measurement: A single angle measurement with metadata.
    LineDetectionResult: Collection of detected lines from an image frame.

Example usage::

    >>> from core.measurements import Measurement, LineDetectionResult
    >>> from core.geometry import Line
    >>> m = Measurement(
    ...     angle_degrees=45.0,
    ...     vertex=(100, 200),
    ...     line1=Line(100, 200, 50, 100),
    ...     line2=Line(100, 200, 200, 150),
    ... )
    >>> m.angle_degrees
    45.0
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from core.geometry import Line


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

@dataclass
class Measurement:
    """A single angle measurement taken between two line segments.

    This stores the computed angle together with all the geometric context
    needed to render, export, or audit the measurement.

    Parameters
    ----------
    angle_degrees : float
        The measured angle in degrees.
    vertex : tuple of float
        The (x, y) point at which the angle is measured.
    line1 : Line
        First line segment forming the angle.
    line2 : Line
        Second line segment forming the angle.
    label : str, optional
        An optional human-readable label (e.g. ``"Angle #1"``).
    timestamp : float, optional
        Unix timestamp when the measurement was taken.  Defaults to the
        current time at instantiation.
    confidence : float, optional
        A confidence score in [0, 1] indicating reliability of the
        measurement (e.g. based on detection quality).  ``None`` means
        the measurement was user-specified (manual mode).

    Examples
    --------
    >>> m = Measurement(
    ...     angle_degrees=90.0,
    ...     vertex=(0, 0),
    ...     line1=Line(0, 0, 1, 0),
    ...     line2=Line(0, 0, 0, 1),
    ... )
    >>> m.angle_degrees
    90.0
    >>> m.is_automatic
    False
    """

    angle_degrees: float
    vertex: Tuple[float, float]
    line1: Line
    line2: Line
    label: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    confidence: Optional[float] = None

    # -- Derived properties -------------------------------------------------

    @property
    def is_automatic(self) -> bool:
        """Whether this measurement was produced by automatic detection.

        Returns ``True`` when a *confidence* score is present, implying
        the measurement came from the detection pipeline rather than
        manual user input.
        """
        return self.confidence is not None

    @property
    def is_acute(self) -> bool:
        """Whether the measured angle is acute (< 90 degrees)."""
        return self.angle_degrees < 90.0

    @property
    def is_right(self) -> bool:
        """Whether the measured angle is approximately a right angle.

        Uses a 0.5-degree tolerance.
        """
        return abs(self.angle_degrees - 90.0) <= 0.5

    @property
    def is_obtuse(self) -> bool:
        """Whether the measured angle is obtuse (> 90 degrees)."""
        return self.angle_degrees > 90.0

    def __repr__(self) -> str:
        label_str = f", label={self.label!r}" if self.label else ""
        conf_str = (
            f", confidence={self.confidence:.2f}"
            if self.confidence is not None
            else ""
        )
        return (
            f"Measurement(angle={self.angle_degrees:.1f}deg"
            f", vertex={self.vertex}"
            f"{label_str}{conf_str})"
        )


# ---------------------------------------------------------------------------
# LineDetectionResult
# ---------------------------------------------------------------------------

@dataclass
class LineDetectionResult:
    """Container for results produced by the line detection pipeline.

    Stores the set of detected ``Line`` objects along with associated
    metadata so the UI and measurement layers can consume and display them.

    Parameters
    ----------
    lines : list of Line
        Detected line segments.
    source_shape : tuple of int, optional
        The ``(height, width)`` of the source image.  Useful for
        coordinate normalisation and bounds checking.
    detection_time_ms : float, optional
        Wall-clock time in milliseconds that the detection step took.
    parameters : dict, optional
        A snapshot of the detection parameters used (e.g. Canny thresholds,
        Hough parameters) for reproducibility.

    Examples
    --------
    >>> result = LineDetectionResult(
    ...     lines=[Line(0, 0, 100, 0), Line(0, 0, 0, 100)],
    ...     source_shape=(480, 640),
    ...     detection_time_ms=23.5,
    ... )
    >>> len(result)
    2
    """

    lines: List[Line] = field(default_factory=list)
    source_shape: Optional[Tuple[int, int]] = None
    detection_time_ms: Optional[float] = None
    parameters: dict = field(default_factory=dict)

    # -- Convenience --------------------------------------------------------

    def __len__(self) -> int:
        """Number of detected lines."""
        return len(self.lines)

    def __iter__(self):
        """Iterate over detected lines."""
        return iter(self.lines)

    def __getitem__(self, index: int) -> Line:
        """Access a detected line by index."""
        return self.lines[index]

    def add_line(self, line: Line) -> None:
        """Append a line to the detection results.

        Parameters
        ----------
        line : Line
            The line segment to add.
        """
        self.lines.append(line)

    def remove_line(self, index: int) -> Line:
        """Remove and return the line at *index*.

        Parameters
        ----------
        index : int
            Position of the line to remove.

        Returns
        -------
        Line
            The removed line.

        Raises
        ------
        IndexError
            If *index* is out of range.
        """
        return self.lines.pop(index)

    def filter_by_length(self, min_length: float = 0.0) -> "LineDetectionResult":
        """Return a new result containing only lines at least *min_length* long.

        Parameters
        ----------
        min_length : float, optional
            Minimum segment length (default ``0.0`` keeps all).

        Returns
        -------
        LineDetectionResult
            Filtered copy sharing the same metadata.
        """
        filtered = [ln for ln in self.lines if ln.length >= min_length]
        return LineDetectionResult(
            lines=filtered,
            source_shape=self.source_shape,
            detection_time_ms=self.detection_time_ms,
            parameters=dict(self.parameters),
        )

    def __repr__(self) -> str:
        shape_str = (
            f", shape={self.source_shape}" if self.source_shape else ""
        )
        time_str = (
            f", {self.detection_time_ms:.1f}ms"
            if self.detection_time_ms is not None
            else ""
        )
        return (
            f"LineDetectionResult({len(self.lines)} lines{shape_str}{time_str})"
        )
