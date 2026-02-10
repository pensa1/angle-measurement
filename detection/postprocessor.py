"""
Post-processing for detected line segments.

Handles line merging, filtering, deduplication, and angle extraction.
The goal is to reduce the fragmented output of the Hough Transform into
a clean, minimal set of meaningful line segments suitable for angle
measurement.

Algorithms:
    * **Line grouping**: cluster lines by similar orientation angle.
    * **Collinear merging**: within each angle group, merge segments that
      are close in perpendicular distance and overlap along their shared
      direction.
    * **Short-line filtering**: discard segments shorter than a threshold.
    * **Duplicate removal**: remove lines whose endpoints are nearly
      identical.
    * **Angle extraction**: compute pairwise angles between the remaining
      lines using :mod:`core.geometry`.

Classes:
    PostprocessorConfig: Parameter container.
    LinePostprocessor: Stateless transformer for post-processing.

Example usage::

    >>> from detection.postprocessor import LinePostprocessor
    >>> pp = LinePostprocessor()
    >>> merged = pp.merge_lines(raw_lines)
    >>> filtered = pp.filter_short_lines(merged, min_length=40)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Optional, Tuple

import numpy as np

from core.geometry import (
    AngleCalculator,
    Line,
    are_lines_parallel,
    distance_point_to_line,
    find_line_intersection,
)
from core.measurements import LineDetectionResult, Measurement


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class PostprocessorConfig:
    """Configuration for the line post-processing pipeline.

    Parameters
    ----------
    angle_tolerance : float
        Maximum angular difference (degrees) for two lines to be
        considered in the same orientation group.  Default ``10.0``.
    distance_tolerance : float
        Maximum perpendicular distance (pixels) between two lines for
        them to be merge candidates.  Default ``15.0``.
    overlap_ratio : float
        Minimum ratio of overlap along the shared direction for two
        segments to be merged.  ``0.0`` means any collinear pair is
        merged; ``1.0`` requires full overlap.  Default ``0.0``.
    min_line_length : float
        Lines shorter than this are discarded during filtering.
        Default ``30.0``.
    duplicate_distance : float
        Maximum endpoint distance (pixels) for two lines to be
        considered duplicates.  Default ``10.0``.
    """

    angle_tolerance: float = 10.0
    distance_tolerance: float = 15.0
    overlap_ratio: float = 0.0
    min_line_length: float = 30.0
    duplicate_distance: float = 10.0


# ---------------------------------------------------------------------------
# LinePostprocessor
# ---------------------------------------------------------------------------

class LinePostprocessor:
    """Post-process detected lines: merge, filter, deduplicate.

    Parameters
    ----------
    config : PostprocessorConfig, optional
        Tuning parameters.  Uses defaults when omitted.
    """

    def __init__(self, config: Optional[PostprocessorConfig] = None) -> None:
        self.config = config or PostprocessorConfig()

    # -- Orientation helpers ------------------------------------------------

    @staticmethod
    def _line_orientation(line: Line) -> float:
        """Return the orientation of *line* in [0, 180) degrees.

        Lines pointing in opposite directions are considered to have
        the same orientation.
        """
        dx = line.x2 - line.x1
        dy = line.y2 - line.y1
        if dx == 0.0 and dy == 0.0:
            return 0.0
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 180.0

    @staticmethod
    def _angular_distance(a: float, b: float) -> float:
        """Minimum angular distance between two angles in [0, 180)."""
        diff = abs(a - b)
        return min(diff, 180.0 - diff)

    # -- Grouping -----------------------------------------------------------

    def group_by_angle(
        self,
        lines: List[Line],
        tolerance: Optional[float] = None,
    ) -> Dict[float, List[Line]]:
        """Group lines by similar orientation angle.

        Lines whose orientations differ by at most *tolerance* degrees
        are placed in the same group.  The group key is the mean
        orientation of its members (in degrees).

        Parameters
        ----------
        lines : list of Line
            Input line segments.
        tolerance : float, optional
            Override the config ``angle_tolerance``.

        Returns
        -------
        dict
            Mapping from representative angle to list of lines in that
            group.
        """
        tol = tolerance if tolerance is not None else self.config.angle_tolerance

        if not lines:
            return {}

        orientations = [self._line_orientation(ln) for ln in lines]
        assigned = [False] * len(lines)
        groups: Dict[float, List[Line]] = {}

        for i in range(len(lines)):
            if assigned[i]:
                continue

            # Start a new group seeded with lines[i]
            group = [lines[i]]
            group_angles = [orientations[i]]
            assigned[i] = True

            for j in range(i + 1, len(lines)):
                if assigned[j]:
                    continue
                if self._angular_distance(orientations[i], orientations[j]) <= tol:
                    group.append(lines[j])
                    group_angles.append(orientations[j])
                    assigned[j] = True

            # Representative angle = circular mean of group
            rep_angle = self._circular_mean(group_angles)
            groups[rep_angle] = group

        return groups

    @staticmethod
    def _circular_mean(angles_deg: List[float]) -> float:
        """Compute the circular mean of angles in [0, 180)."""
        # Use doubled-angle trick for axial data
        rads = [math.radians(2 * a) for a in angles_deg]
        sx = sum(math.cos(r) for r in rads)
        sy = sum(math.sin(r) for r in rads)
        mean_rad = math.atan2(sy, sx) / 2.0
        return math.degrees(mean_rad) % 180.0

    # -- Perpendicular distance between two line segments -------------------

    @staticmethod
    def _perpendicular_distance(line1: Line, line2: Line) -> float:
        """Average perpendicular distance between two line segments.

        Computed as the mean of the four endpoint-to-segment distances.
        """
        d1 = distance_point_to_line(line1.midpoint, line2)
        d2 = distance_point_to_line(line2.midpoint, line1)
        return (d1 + d2) / 2.0

    # -- Projection overlap -------------------------------------------------

    @staticmethod
    def _projection_overlap(line1: Line, line2: Line) -> float:
        """Compute the 1-D overlap ratio of two segments projected onto
        the principal direction.

        Returns a value in [0, 1] where 0 means no overlap and 1 means
        one segment is entirely contained in the other.
        """
        # Use the direction of the longer segment as the projection axis.
        ref = line1 if line1.length >= line2.length else line2

        dx = ref.x2 - ref.x1
        dy = ref.y2 - ref.y1
        norm = math.hypot(dx, dy)
        if norm == 0:
            return 0.0

        ux, uy = dx / norm, dy / norm

        def project(pt: Tuple[float, float]) -> float:
            return pt[0] * ux + pt[1] * uy

        # Project all four endpoints
        projs = sorted([
            project((line1.x1, line1.y1)),
            project((line1.x2, line1.y2)),
        ])
        projs2 = sorted([
            project((line2.x1, line2.y1)),
            project((line2.x2, line2.y2)),
        ])

        overlap_start = max(projs[0], projs2[0])
        overlap_end = min(projs[1], projs2[1])
        overlap = max(0.0, overlap_end - overlap_start)

        min_span = min(projs[1] - projs[0], projs2[1] - projs2[0])
        if min_span == 0:
            return 0.0

        return overlap / min_span

    # -- Core merging -------------------------------------------------------

    def _merge_two_lines(self, line1: Line, line2: Line) -> Line:
        """Merge two approximately collinear segments into one.

        The merged line spans from the outermost projected endpoint to the
        other outermost endpoint along the principal direction.
        """
        # Principal direction from the longer line
        ref = line1 if line1.length >= line2.length else line2
        dx = ref.x2 - ref.x1
        dy = ref.y2 - ref.y1
        norm = math.hypot(dx, dy)
        if norm == 0:
            return line1

        ux, uy = dx / norm, dy / norm

        points = [
            (line1.x1, line1.y1),
            (line1.x2, line1.y2),
            (line2.x1, line2.y1),
            (line2.x2, line2.y2),
        ]

        projections = [(p[0] * ux + p[1] * uy, p) for p in points]
        projections.sort(key=lambda t: t[0])

        # Outermost endpoints
        start = projections[0][1]
        end = projections[-1][1]
        return Line(start[0], start[1], end[0], end[1])

    def merge_lines(
        self,
        lines: List[Line],
        angle_tolerance: Optional[float] = None,
        distance_tolerance: Optional[float] = None,
    ) -> List[Line]:
        """Merge nearby collinear / parallel line segments.

        Algorithm
        ---------
        1. Group lines by orientation (within *angle_tolerance*).
        2. Within each group, greedily merge pairs whose perpendicular
           distance is within *distance_tolerance* and whose projection
           overlap meets the configured :attr:`PostprocessorConfig.overlap_ratio`.
        3. Repeat until no more merges happen.

        Parameters
        ----------
        lines : list of Line
            Raw detected line segments.
        angle_tolerance : float, optional
            Override config value.
        distance_tolerance : float, optional
            Override config value.

        Returns
        -------
        list of Line
            Merged line segments (typically fewer than the input).
        """
        if not lines:
            return []

        a_tol = angle_tolerance if angle_tolerance is not None else self.config.angle_tolerance
        d_tol = distance_tolerance if distance_tolerance is not None else self.config.distance_tolerance

        groups = self.group_by_angle(lines, tolerance=a_tol)
        merged_all: List[Line] = []

        for _angle, group in groups.items():
            merged = self._merge_group(group, d_tol)
            merged_all.extend(merged)

        return merged_all

    def _merge_group(self, lines: List[Line], distance_tolerance: float) -> List[Line]:
        """Greedily merge collinear segments within one orientation group."""
        if len(lines) <= 1:
            return list(lines)

        merged = list(lines)
        changed = True

        while changed:
            changed = False
            new_merged: List[Line] = []
            used = [False] * len(merged)

            for i in range(len(merged)):
                if used[i]:
                    continue

                current = merged[i]
                for j in range(i + 1, len(merged)):
                    if used[j]:
                        continue

                    perp_dist = self._perpendicular_distance(current, merged[j])
                    if perp_dist <= distance_tolerance:
                        overlap = self._projection_overlap(current, merged[j])
                        # With overlap_ratio 0.0, any collinear pair merges;
                        # with positive overlap_ratio, segments must overlap.
                        if overlap >= self.config.overlap_ratio or perp_dist < distance_tolerance * 0.5:
                            current = self._merge_two_lines(current, merged[j])
                            used[j] = True
                            changed = True

                new_merged.append(current)
                used[i] = True

            merged = new_merged

        return merged

    # -- Filtering ----------------------------------------------------------

    def filter_short_lines(
        self,
        lines: List[Line],
        min_length: Optional[float] = None,
    ) -> List[Line]:
        """Remove lines shorter than *min_length*.

        Parameters
        ----------
        lines : list of Line
            Input line segments.
        min_length : float, optional
            Override the config ``min_line_length``.

        Returns
        -------
        list of Line
            Filtered list.
        """
        ml = min_length if min_length is not None else self.config.min_line_length
        return [ln for ln in lines if ln.length >= ml]

    def filter_by_angle(
        self,
        lines: List[Line],
        min_angle: float = 0.0,
        max_angle: float = 180.0,
    ) -> List[Line]:
        """Keep only lines whose orientation is between *min_angle* and *max_angle*.

        Parameters
        ----------
        lines : list of Line
        min_angle : float
            Minimum orientation in degrees [0, 180).
        max_angle : float
            Maximum orientation in degrees [0, 180).

        Returns
        -------
        list of Line
        """
        result = []
        for ln in lines:
            orient = self._line_orientation(ln)
            if min_angle <= orient <= max_angle:
                result.append(ln)
        return result

    def remove_duplicates(
        self,
        lines: List[Line],
        distance_threshold: Optional[float] = None,
    ) -> List[Line]:
        """Remove duplicate line detections.

        Two lines are considered duplicates when both pairs of endpoints
        are within *distance_threshold* pixels of each other (in either
        direction).

        Parameters
        ----------
        lines : list of Line
        distance_threshold : float, optional
            Override the config ``duplicate_distance``.

        Returns
        -------
        list of Line
            Deduplicated list.
        """
        thr = distance_threshold if distance_threshold is not None else self.config.duplicate_distance

        if not lines:
            return []

        unique: List[Line] = [lines[0]]

        for candidate in lines[1:]:
            is_dup = False
            for existing in unique:
                # Check both endpoint orderings
                d_fwd = max(
                    math.hypot(candidate.x1 - existing.x1, candidate.y1 - existing.y1),
                    math.hypot(candidate.x2 - existing.x2, candidate.y2 - existing.y2),
                )
                d_rev = max(
                    math.hypot(candidate.x1 - existing.x2, candidate.y1 - existing.y2),
                    math.hypot(candidate.x2 - existing.x1, candidate.y2 - existing.y1),
                )
                if min(d_fwd, d_rev) <= thr:
                    is_dup = True
                    break
            if not is_dup:
                unique.append(candidate)

        return unique

    # -- Full post-processing pipeline --------------------------------------

    def process(self, lines: List[Line]) -> List[Line]:
        """Run the complete post-processing pipeline.

        The pipeline is:
        1. Filter out short lines
        2. Remove duplicates
        3. Merge nearby collinear / parallel segments

        Parameters
        ----------
        lines : list of Line

        Returns
        -------
        list of Line
            Cleaned, merged line segments.
        """
        if not lines:
            return []

        result = self.filter_short_lines(lines)
        result = self.remove_duplicates(result)
        result = self.merge_lines(result)
        return result

    def process_result(
        self, detection_result: LineDetectionResult
    ) -> LineDetectionResult:
        """Apply post-processing to a :class:`LineDetectionResult`.

        Parameters
        ----------
        detection_result : LineDetectionResult

        Returns
        -------
        LineDetectionResult
            A new result with post-processed lines and the same metadata.
        """
        processed = self.process(detection_result.lines)
        return LineDetectionResult(
            lines=processed,
            source_shape=detection_result.source_shape,
            detection_time_ms=detection_result.detection_time_ms,
            parameters=dict(detection_result.parameters),
        )

    # -- Angle extraction ---------------------------------------------------

    def find_angles(
        self,
        lines: List[Line],
    ) -> List[Measurement]:
        """Compute angles between all pairs of lines.

        For each pair the intersection point (of infinite lines) is used
        as the vertex.  If the lines are parallel the pair is skipped.

        Parameters
        ----------
        lines : list of Line
            Cleaned line segments.

        Returns
        -------
        list of Measurement
            One measurement for each non-parallel line pair.
        """
        measurements: List[Measurement] = []

        for i, j in combinations(range(len(lines)), 2):
            l1 = lines[i]
            l2 = lines[j]

            # Skip near-parallel pairs
            try:
                angle = AngleCalculator.calculate_angle_between_lines(l1, l2)
            except ZeroDivisionError:
                continue

            if angle < 1.0:
                continue  # nearly parallel -- skip

            vertex = find_line_intersection(l1, l2)
            if vertex is None:
                # Parallel -- use midpoint of the gap instead
                mx = (l1.midpoint[0] + l2.midpoint[0]) / 2.0
                my = (l1.midpoint[1] + l2.midpoint[1]) / 2.0
                vertex = (mx, my)

            measurements.append(
                Measurement(
                    angle_degrees=angle,
                    vertex=vertex,
                    line1=l1,
                    line2=l2,
                    label=f"Angle #{len(measurements) + 1}",
                    confidence=0.8,  # default confidence for auto-detected
                )
            )

        return measurements

    def find_best_angle(
        self,
        lines: List[Line],
    ) -> Optional[Measurement]:
        """Return the single most prominent angle measurement.

        Heuristic: choose the angle formed by the two longest lines.

        Parameters
        ----------
        lines : list of Line

        Returns
        -------
        Measurement or None
            The measurement, or ``None`` if fewer than two lines exist.
        """
        if len(lines) < 2:
            return None

        # Sort by length descending, take top two
        sorted_lines = sorted(lines, key=lambda ln: ln.length, reverse=True)
        l1 = sorted_lines[0]
        l2 = sorted_lines[1]

        try:
            angle = AngleCalculator.calculate_angle_between_lines(l1, l2)
        except ZeroDivisionError:
            return None

        vertex = find_line_intersection(l1, l2)
        if vertex is None:
            mx = (l1.midpoint[0] + l2.midpoint[0]) / 2.0
            my = (l1.midpoint[1] + l2.midpoint[1]) / 2.0
            vertex = (mx, my)

        return Measurement(
            angle_degrees=angle,
            vertex=vertex,
            line1=l1,
            line2=l2,
            label="Best angle",
            confidence=0.9,
        )
