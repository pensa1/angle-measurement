"""
Core geometry module for the angle-measurement project.

Provides robust geometric primitives and calculations including line segment
representation, angle computation between points and lines, intersection
detection, and distance metrics. All angle values are in degrees.

This module extracts and enhances the angle calculation logic originally
found in setup.py (lines 39-56) and adds a comprehensive set of geometric
utilities needed by the Detection, UI, and Testing agents.

Classes:
    Line: Represents a 2D line segment with geometric properties and methods.
    AngleCalculator: Calculates angles between points and lines.

Functions:
    distance_between_points: Euclidean distance between two points.
    distance_point_to_line: Shortest distance from a point to a line segment.
    find_line_intersection: Compute intersection point of two lines.
    are_lines_parallel: Check whether two lines are approximately parallel.

Example usage::

    >>> from core.geometry import Line, AngleCalculator
    >>> line_a = Line(0, 0, 10, 0)
    >>> line_b = Line(0, 0, 0, 10)
    >>> AngleCalculator.calculate_angle_between_lines(line_a, line_b)
    90.0
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple, Union

import numpy as np


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Point = Union[Tuple[float, float], List[float], np.ndarray]
"""A 2D point represented as a tuple, list, or numpy array of (x, y)."""


# ---------------------------------------------------------------------------
# Helper: coerce any point-like input to a numpy float64 array of shape (2,)
# ---------------------------------------------------------------------------

def _as_point(pt: Point) -> np.ndarray:
    """Convert a point-like object to a numpy float64 array of shape (2,).

    Parameters
    ----------
    pt : Point
        A 2-element sequence representing (x, y).

    Returns
    -------
    np.ndarray
        A 1-D float64 array ``[x, y]``.

    Raises
    ------
    ValueError
        If *pt* does not contain exactly 2 elements.
    """
    arr = np.asarray(pt, dtype=np.float64).ravel()
    if arr.shape[0] != 2:
        raise ValueError(
            f"Expected a 2-element point (x, y), got shape {arr.shape}"
        )
    return arr


# ---------------------------------------------------------------------------
# Line class
# ---------------------------------------------------------------------------

class Line:
    """A 2D line segment defined by two endpoints.

    The line is stored internally as ``[x1, y1, x2, y2]`` and provides
    convenient properties for geometric queries (length, orientation angle,
    midpoint) as well as methods for intersection, distance, and parallelism
    checks.

    Parameters
    ----------
    x1 : float
        X-coordinate of the first endpoint.
    y1 : float
        Y-coordinate of the first endpoint.
    x2 : float
        X-coordinate of the second endpoint.
    y2 : float
        Y-coordinate of the second endpoint.

    Attributes
    ----------
    x1, y1, x2, y2 : float
        Endpoint coordinates.

    Examples
    --------
    >>> line = Line(0, 0, 3, 4)
    >>> line.length
    5.0
    >>> line.midpoint
    (1.5, 2.0)
    """

    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    # -- Representation -----------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Line(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Line):
            return NotImplemented
        return (
            math.isclose(self.x1, other.x1)
            and math.isclose(self.y1, other.y1)
            and math.isclose(self.x2, other.x2)
            and math.isclose(self.y2, other.y2)
        )

    # -- Convenience accessors ----------------------------------------------

    @property
    def pt1(self) -> np.ndarray:
        """First endpoint as a numpy array ``[x1, y1]``."""
        return np.array([self.x1, self.y1], dtype=np.float64)

    @property
    def pt2(self) -> np.ndarray:
        """Second endpoint as a numpy array ``[x2, y2]``."""
        return np.array([self.x2, self.y2], dtype=np.float64)

    @property
    def as_array(self) -> np.ndarray:
        """Line as a flat numpy array ``[x1, y1, x2, y2]``."""
        return np.array(
            [self.x1, self.y1, self.x2, self.y2], dtype=np.float64
        )

    @property
    def direction(self) -> np.ndarray:
        """Unit direction vector from pt1 to pt2.

        Returns
        -------
        np.ndarray
            Normalised direction vector of shape (2,).

        Raises
        ------
        ZeroDivisionError
            If the line has zero length (pt1 == pt2).
        """
        d = self.pt2 - self.pt1
        norm = np.linalg.norm(d)
        if norm == 0.0:
            raise ZeroDivisionError(
                "Cannot compute direction of a zero-length line."
            )
        return d / norm

    # -- Properties ---------------------------------------------------------

    @property
    def length(self) -> float:
        """Euclidean length of the line segment.

        Returns
        -------
        float
            Non-negative distance between the two endpoints.

        Examples
        --------
        >>> Line(0, 0, 3, 4).length
        5.0
        >>> Line(1, 1, 1, 1).length
        0.0
        """
        return float(np.linalg.norm(self.pt2 - self.pt1))

    @property
    def angle(self) -> float:
        """Orientation angle of the line segment in degrees.

        The angle is measured counter-clockwise from the positive x-axis to
        the direction vector (pt1 -> pt2) and is normalised to the range
        [0, 360).

        Returns
        -------
        float
            Angle in degrees in [0, 360).

        Raises
        ------
        ZeroDivisionError
            If the line has zero length.

        Examples
        --------
        >>> Line(0, 0, 1, 0).angle
        0.0
        >>> Line(0, 0, 0, 1).angle
        90.0
        >>> Line(0, 0, -1, 0).angle
        180.0
        """
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        if dx == 0.0 and dy == 0.0:
            raise ZeroDivisionError(
                "Cannot compute angle of a zero-length line."
            )
        deg = math.degrees(math.atan2(dy, dx))
        return deg % 360.0

    @property
    def midpoint(self) -> Tuple[float, float]:
        """Midpoint of the line segment.

        Returns
        -------
        tuple of float
            ``(mx, my)`` coordinates of the midpoint.

        Examples
        --------
        >>> Line(0, 0, 4, 6).midpoint
        (2.0, 3.0)
        """
        return (
            (self.x1 + self.x2) / 2.0,
            (self.y1 + self.y2) / 2.0,
        )

    # -- Methods ------------------------------------------------------------

    def intersection(self, other: "Line") -> Optional[Tuple[float, float]]:
        """Compute the intersection point of the infinite lines through each segment.

        Uses the parametric intersection of two line segments extended to
        infinite lines. If the lines are parallel (or coincident), returns
        ``None``.

        Parameters
        ----------
        other : Line
            Another line segment.

        Returns
        -------
        tuple of float or None
            ``(x, y)`` intersection point, or ``None`` if the lines are
            parallel or coincident.

        Examples
        --------
        >>> Line(0, 0, 2, 2).intersection(Line(0, 2, 2, 0))
        (1.0, 1.0)
        >>> Line(0, 0, 1, 0).intersection(Line(0, 1, 1, 1)) is None
        True
        """
        return find_line_intersection(self, other)

    def distance_to_point(self, point: Point) -> float:
        """Shortest distance from *point* to the closest point on this segment.

        The closest point is clamped to the segment (not the infinite line).

        Parameters
        ----------
        point : Point
            A 2-element (x, y) sequence.

        Returns
        -------
        float
            Non-negative distance.

        Examples
        --------
        >>> Line(0, 0, 10, 0).distance_to_point((5, 3))
        3.0
        >>> Line(0, 0, 10, 0).distance_to_point((-5, 0))
        5.0
        """
        return distance_point_to_line(point, self)

    def is_parallel(self, other: "Line", tolerance: float = 1.0) -> bool:
        """Check whether this line is approximately parallel to *other*.

        Two lines are considered parallel when the acute angle between them
        is less than or equal to *tolerance* degrees.

        Parameters
        ----------
        other : Line
            Another line segment.
        tolerance : float, optional
            Maximum allowed angular deviation in degrees (default ``1.0``).

        Returns
        -------
        bool
            ``True`` if the lines are approximately parallel.

        Examples
        --------
        >>> Line(0, 0, 10, 0).is_parallel(Line(0, 5, 10, 5))
        True
        >>> Line(0, 0, 10, 0).is_parallel(Line(0, 0, 10, 10))
        False
        """
        return are_lines_parallel(self, other, tolerance=tolerance)

    def closest_point_on_segment(self, point: Point) -> Tuple[float, float]:
        """Return the closest point on this segment to the given *point*.

        The result is clamped to the segment endpoints.

        Parameters
        ----------
        point : Point
            A 2-element (x, y) sequence.

        Returns
        -------
        tuple of float
            ``(x, y)`` coordinates of the closest point on the segment.
        """
        p = _as_point(point)
        a = self.pt1
        b = self.pt2
        ab = b - a
        ab_sq = float(np.dot(ab, ab))

        if ab_sq == 0.0:
            # Zero-length segment: closest point is the single point itself.
            return (self.x1, self.y1)

        # Parameter t of the projection clamped to [0, 1].
        t = float(np.dot(p - a, ab) / ab_sq)
        t = max(0.0, min(1.0, t))

        proj = a + t * ab
        return (float(proj[0]), float(proj[1]))

    # -- Factory methods ----------------------------------------------------

    @classmethod
    def from_points(
        cls, pt1: Point, pt2: Point
    ) -> "Line":
        """Create a Line from two point-like objects.

        Parameters
        ----------
        pt1, pt2 : Point
            Endpoints as (x, y).

        Returns
        -------
        Line

        Examples
        --------
        >>> Line.from_points((1, 2), (3, 4))
        Line(x1=1.0, y1=2.0, x2=3.0, y2=4.0)
        """
        a = _as_point(pt1)
        b = _as_point(pt2)
        return cls(float(a[0]), float(a[1]), float(b[0]), float(b[1]))

    @classmethod
    def from_array(cls, arr: Union[np.ndarray, List[float]]) -> "Line":
        """Create a Line from a flat ``[x1, y1, x2, y2]`` array.

        Parameters
        ----------
        arr : array-like
            A 4-element sequence.

        Returns
        -------
        Line

        Raises
        ------
        ValueError
            If *arr* does not contain exactly 4 elements.

        Examples
        --------
        >>> Line.from_array([10, 20, 30, 40])
        Line(x1=10.0, y1=20.0, x2=30.0, y2=40.0)
        """
        a = np.asarray(arr, dtype=np.float64).ravel()
        if a.shape[0] != 4:
            raise ValueError(
                f"Expected 4 elements [x1, y1, x2, y2], got {a.shape[0]}"
            )
        return cls(float(a[0]), float(a[1]), float(a[2]), float(a[3]))


# ---------------------------------------------------------------------------
# AngleCalculator class
# ---------------------------------------------------------------------------

class AngleCalculator:
    """Static methods for computing angles between points and lines.

    All returned angles are in **degrees**.

    This class encapsulates the angle-computation logic originally found in
    ``setup.py`` (the ``getAngle`` function) and extends it with additional
    methods for computing angles between ``Line`` objects.

    Methods
    -------
    calculate_angle_3_points(pt1, pt2, pt3)
        Angle at *pt1* formed by rays pt1->pt2 and pt1->pt3.
    calculate_angle_between_lines(line1, line2)
        Acute angle between two line segments.
    """

    @staticmethod
    def calculate_angle_3_points(
        pt1: Point, pt2: Point, pt3: Point
    ) -> float:
        """Calculate the angle at *pt1* formed by rays pt1->pt2 and pt1->pt3.

        This is the enhanced version of the ``getAngle()`` function from
        ``setup.py``. It uses the dot-product formula:

        .. math::

            \\theta = \\arccos\\!\\left(
                \\frac{\\vec{v_1} \\cdot \\vec{v_2}}
                     {|\\vec{v_1}|\\,|\\vec{v_2}|}
            \\right)

        where :math:`\\vec{v_1} = pt2 - pt1` and :math:`\\vec{v_2} = pt3 - pt1`.

        Parameters
        ----------
        pt1 : Point
            The vertex of the angle (the point *at which* the angle is measured).
        pt2 : Point
            Endpoint of the first ray.
        pt3 : Point
            Endpoint of the second ray.

        Returns
        -------
        float
            The angle in degrees, in the range [0, 180].

        Raises
        ------
        ValueError
            If *pt1* coincides with *pt2* or *pt3* (zero-length ray).

        Notes
        -----
        The original ``getAngle`` in ``setup.py`` used ``pointsList[-3:]``
        and drew text on an image. This method is a pure-math extraction
        with no side effects.

        Examples
        --------
        >>> AngleCalculator.calculate_angle_3_points((0, 0), (1, 0), (0, 1))
        90.0
        >>> AngleCalculator.calculate_angle_3_points((0, 0), (1, 0), (1, 0))
        0.0
        >>> AngleCalculator.calculate_angle_3_points((0, 0), (1, 0), (-1, 0))
        180.0
        """
        vertex = _as_point(pt1)
        a = _as_point(pt2)
        b = _as_point(pt3)

        va = a - vertex  # vector from vertex to pt2
        vb = b - vertex  # vector from vertex to pt3

        norm_va = float(np.linalg.norm(va))
        norm_vb = float(np.linalg.norm(vb))

        if norm_va == 0.0:
            raise ValueError(
                "pt1 and pt2 are coincident; cannot form a ray."
            )
        if norm_vb == 0.0:
            raise ValueError(
                "pt1 and pt3 are coincident; cannot form a ray."
            )

        cosine = float(np.dot(va, vb) / (norm_va * norm_vb))
        # Clamp to [-1, 1] to guard against floating-point drift.
        cosine = max(-1.0, min(1.0, cosine))

        angle_rad = math.acos(cosine)
        return math.degrees(angle_rad)

    @staticmethod
    def calculate_angle_between_lines(
        line1: Line, line2: Line
    ) -> float:
        """Calculate the acute angle between two line segments.

        The angle is computed from the direction vectors of the two segments,
        ignoring orientation (i.e. the result is always in [0, 90]).

        Parameters
        ----------
        line1 : Line
            First line segment.
        line2 : Line
            Second line segment.

        Returns
        -------
        float
            The acute angle in degrees, in the range [0, 90].

        Raises
        ------
        ZeroDivisionError
            If either line has zero length.

        Examples
        --------
        >>> l1 = Line(0, 0, 10, 0)
        >>> l2 = Line(0, 0, 0, 10)
        >>> AngleCalculator.calculate_angle_between_lines(l1, l2)
        90.0

        >>> l3 = Line(0, 0, 10, 10)
        >>> AngleCalculator.calculate_angle_between_lines(l1, l3)
        45.0
        """
        d1 = line1.direction  # unit vector; raises if zero-length
        d2 = line2.direction

        cosine = float(np.dot(d1, d2))
        # Clamp to [-1, 1].
        cosine = max(-1.0, min(1.0, cosine))

        angle_deg = math.degrees(math.acos(abs(cosine)))
        return angle_deg


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def distance_between_points(pt1: Point, pt2: Point) -> float:
    """Euclidean distance between two 2D points.

    Parameters
    ----------
    pt1 : Point
        First point (x, y).
    pt2 : Point
        Second point (x, y).

    Returns
    -------
    float
        Non-negative distance.

    Examples
    --------
    >>> distance_between_points((0, 0), (3, 4))
    5.0
    >>> distance_between_points((1, 1), (1, 1))
    0.0
    """
    a = _as_point(pt1)
    b = _as_point(pt2)
    return float(np.linalg.norm(b - a))


def distance_point_to_line(point: Point, line: Line) -> float:
    """Shortest distance from *point* to the line **segment** *line*.

    The nearest point on the segment is clamped to the endpoints, so this
    is the distance to the *segment*, not the infinite line.

    Parameters
    ----------
    point : Point
        A 2-element (x, y) sequence.
    line : Line
        The line segment.

    Returns
    -------
    float
        Non-negative distance.

    Examples
    --------
    >>> distance_point_to_line((5, 5), Line(0, 0, 10, 0))
    5.0
    >>> distance_point_to_line((-3, 0), Line(0, 0, 10, 0))
    3.0
    """
    closest = line.closest_point_on_segment(point)
    return distance_between_points(point, closest)


def find_line_intersection(
    line1: Line, line2: Line
) -> Optional[Tuple[float, float]]:
    """Compute the intersection of two **infinite** lines through the segments.

    Uses the standard determinant formula for line-line intersection.

    Parameters
    ----------
    line1 : Line
        First line segment (extended to an infinite line).
    line2 : Line
        Second line segment (extended to an infinite line).

    Returns
    -------
    tuple of float or None
        ``(x, y)`` intersection coordinates, or ``None`` if the lines are
        parallel or coincident (determinant is zero).

    Notes
    -----
    This function does **not** check whether the intersection point lies
    within the finite segments. Use the returned coordinates together with
    each segment's bounding box if you need segment-segment intersection.

    Examples
    --------
    >>> find_line_intersection(Line(0, 0, 2, 2), Line(0, 2, 2, 0))
    (1.0, 1.0)

    >>> find_line_intersection(Line(0, 0, 1, 0), Line(0, 1, 1, 1)) is None
    True
    """
    # Direction vectors.
    d1x = line1.x2 - line1.x1
    d1y = line1.y2 - line1.y1
    d2x = line2.x2 - line2.x1
    d2y = line2.y2 - line2.y1

    denom = d1x * d2y - d1y * d2x

    if abs(denom) < 1e-12:
        # Lines are parallel (or coincident).
        return None

    # Vector from line1.pt1 to line2.pt1.
    dx = line2.x1 - line1.x1
    dy = line2.y1 - line1.y1

    t = (dx * d2y - dy * d2x) / denom

    ix = line1.x1 + t * d1x
    iy = line1.y1 + t * d1y

    return (ix, iy)


def are_lines_parallel(
    line1: Line,
    line2: Line,
    tolerance: float = 1.0,
) -> bool:
    """Check whether two lines are approximately parallel.

    Two line segments are considered parallel when the acute angle between
    their direction vectors is at most *tolerance* degrees.

    Parameters
    ----------
    line1 : Line
        First line segment.
    line2 : Line
        Second line segment.
    tolerance : float, optional
        Maximum angular deviation in degrees (default ``1.0``).

    Returns
    -------
    bool
        ``True`` if the lines are parallel within the tolerance.

    Raises
    ------
    ZeroDivisionError
        If either line has zero length.
    ValueError
        If *tolerance* is negative.

    Examples
    --------
    >>> are_lines_parallel(Line(0, 0, 10, 0), Line(0, 5, 10, 5))
    True
    >>> are_lines_parallel(Line(0, 0, 10, 0), Line(0, 0, 10, 1), tolerance=5.0)
    True
    >>> are_lines_parallel(Line(0, 0, 10, 0), Line(0, 0, 0, 10))
    False
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    try:
        angle = AngleCalculator.calculate_angle_between_lines(line1, line2)
    except ZeroDivisionError:
        raise  # propagate zero-length errors

    return angle <= tolerance


# ---------------------------------------------------------------------------
# Legacy-compatible helpers (mirroring setup.py signatures)
# ---------------------------------------------------------------------------

def gradient(pt1: Point, pt2: Point) -> float:
    """Calculate the slope (gradient) of the line through two points.

    This is a robust replacement for the ``gradient()`` function in
    ``setup.py``. Vertical lines return ``float('inf')`` instead of using
    an epsilon hack.

    Parameters
    ----------
    pt1 : Point
        First point (x, y).
    pt2 : Point
        Second point (x, y).

    Returns
    -------
    float
        The slope dy/dx, or ``float('inf')`` for vertical lines, or
        ``float('nan')`` if both points are coincident.

    Examples
    --------
    >>> gradient((0, 0), (1, 1))
    1.0
    >>> gradient((0, 0), (0, 5))
    inf
    >>> import math
    >>> math.isnan(gradient((3, 3), (3, 3)))
    True
    """
    a = _as_point(pt1)
    b = _as_point(pt2)
    dx = b[0] - a[0]
    dy = b[1] - a[1]

    if dx == 0.0:
        if dy == 0.0:
            return float("nan")
        return float("inf") if dy > 0 else float("-inf")

    return dy / dx
