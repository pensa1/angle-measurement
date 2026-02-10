"""
Line detection using Canny edge detection and Probabilistic Hough Transform.

This is the core detection module.  It combines a configurable Canny edge
detector with OpenCV's ``cv2.HoughLinesP`` to extract line segments from
preprocessed images and wraps the results in :class:`core.geometry.Line`
objects.

Classes:
    LineDetectorConfig: Parameter container for Canny + Hough.
    LineDetector: Orchestrates the full detection pipeline.

Example usage::

    >>> import cv2
    >>> from detection.line_detector import LineDetector
    >>> img = cv2.imread("img/sample.jpg")
    >>> detector = LineDetector()
    >>> result = detector.detect(img)
    >>> print(f"Found {len(result)} lines")
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np

from core.geometry import Line
from core.measurements import LineDetectionResult
from detection.preprocessor import ImagePreprocessor, PreprocessorConfig


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class LineDetectorConfig:
    """Configuration parameters for the Canny + Hough detection pipeline.

    Parameters
    ----------
    canny_low_threshold : int
        Lower hysteresis threshold for Canny.  Default ``50``.
    canny_high_threshold : int
        Upper hysteresis threshold for Canny.  Default ``150``.
    canny_aperture_size : int
        Sobel kernel aperture size for Canny (must be 3, 5, or 7).
        Default ``3``.
    canny_l2_gradient : bool
        Whether to use the L2 norm for gradient magnitude in Canny.
        Default ``False`` (uses the faster L1 norm).
    hough_rho : float
        Distance resolution of the accumulator in pixels.  Default ``1``.
    hough_theta : float
        Angular resolution of the accumulator in radians.  Default
        ``pi / 180`` (1 degree).
    hough_threshold : int
        Minimum number of intersections (votes) to detect a line.
        Default ``50``.
    min_line_length : float
        Minimum length of a line segment to be returned.  Default ``50``.
    max_line_gap : float
        Maximum gap between two points on the same line to link them.
        Default ``10``.
    use_preprocessing : bool
        Whether to run the :class:`ImagePreprocessor` before Canny.
        Default ``True``.
    """

    canny_low_threshold: int = 50
    canny_high_threshold: int = 150
    canny_aperture_size: int = 3
    canny_l2_gradient: bool = False
    hough_rho: float = 1.0
    hough_theta: float = np.pi / 180.0
    hough_threshold: int = 50
    min_line_length: float = 50.0
    max_line_gap: float = 10.0
    use_preprocessing: bool = True


# ---------------------------------------------------------------------------
# LineDetector
# ---------------------------------------------------------------------------

class LineDetector:
    """Detect line segments in an image using Canny edges + Hough Transform.

    The detector may optionally run a preprocessing pipeline
    (:class:`detection.preprocessor.ImagePreprocessor`) before edge
    detection.  Detected segments are returned as a
    :class:`core.measurements.LineDetectionResult` containing
    :class:`core.geometry.Line` objects.

    Parameters
    ----------
    config : LineDetectorConfig, optional
        Detection parameters.  Uses sensible defaults when omitted.
    preprocessor_config : PreprocessorConfig, optional
        Preprocessing parameters.  Ignored when
        ``config.use_preprocessing`` is ``False``.
    """

    def __init__(
        self,
        config: Optional[LineDetectorConfig] = None,
        preprocessor_config: Optional[PreprocessorConfig] = None,
    ) -> None:
        self.config = config or LineDetectorConfig()
        self._preprocessor = ImagePreprocessor(preprocessor_config)

    # -- Properties ---------------------------------------------------------

    @property
    def preprocessor(self) -> ImagePreprocessor:
        """Access the underlying :class:`ImagePreprocessor`."""
        return self._preprocessor

    # -- Core detection steps -----------------------------------------------

    def canny_edges(
        self,
        image: np.ndarray,
        low: Optional[int] = None,
        high: Optional[int] = None,
    ) -> np.ndarray:
        """Run Canny edge detection on a grayscale image.

        Parameters
        ----------
        image : np.ndarray
            Grayscale image (single channel, ``uint8``).
        low : int, optional
            Override the configured low threshold.
        high : int, optional
            Override the configured high threshold.

        Returns
        -------
        np.ndarray
            Binary edge map of the same size as *image*.

        Raises
        ------
        ValueError
            If *image* is empty or ``None``.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        # Ensure single-channel
        gray = image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        lo = low if low is not None else self.config.canny_low_threshold
        hi = high if high is not None else self.config.canny_high_threshold

        edges = cv2.Canny(
            gray,
            lo,
            hi,
            apertureSize=self.config.canny_aperture_size,
            L2gradient=self.config.canny_l2_gradient,
        )
        return edges

    def hough_lines(
        self,
        edge_image: np.ndarray,
        threshold: Optional[int] = None,
        min_line_length: Optional[float] = None,
        max_line_gap: Optional[float] = None,
    ) -> np.ndarray:
        """Run Probabilistic Hough Transform on a binary edge map.

        Parameters
        ----------
        edge_image : np.ndarray
            Binary edge image (output of Canny).
        threshold : int, optional
            Override the configured Hough threshold.
        min_line_length : float, optional
            Override the configured minimum line length.
        max_line_gap : float, optional
            Override the configured maximum gap.

        Returns
        -------
        np.ndarray
            Array of shape ``(N, 1, 4)`` where each row is
            ``[x1, y1, x2, y2]``, or an empty array if no lines are
            found.
        """
        if edge_image is None or edge_image.size == 0:
            return np.empty((0, 1, 4), dtype=np.int32)

        thr = threshold if threshold is not None else self.config.hough_threshold
        mll = min_line_length if min_line_length is not None else self.config.min_line_length
        mlg = max_line_gap if max_line_gap is not None else self.config.max_line_gap

        lines = cv2.HoughLinesP(
            edge_image,
            rho=self.config.hough_rho,
            theta=self.config.hough_theta,
            threshold=thr,
            minLineLength=mll,
            maxLineGap=mlg,
        )

        if lines is None:
            return np.empty((0, 1, 4), dtype=np.int32)

        return lines

    @staticmethod
    def hough_to_lines(hough_output: np.ndarray) -> List[Line]:
        """Convert raw Hough output to a list of :class:`core.geometry.Line`.

        Parameters
        ----------
        hough_output : np.ndarray
            Array of shape ``(N, 1, 4)`` as returned by
            ``cv2.HoughLinesP``.

        Returns
        -------
        list of Line
            Converted line segments.
        """
        if hough_output is None or hough_output.size == 0:
            return []

        lines: List[Line] = []
        for row in hough_output:
            x1, y1, x2, y2 = row[0]
            lines.append(Line(float(x1), float(y1), float(x2), float(y2)))
        return lines

    # -- High-level API -----------------------------------------------------

    def detect(self, image: np.ndarray) -> LineDetectionResult:
        """Run the full detection pipeline on an image.

        The pipeline is:

        1. (optional) Preprocessing -- grayscale, blur, CLAHE
        2. Canny edge detection
        3. Probabilistic Hough Transform
        4. Wrap results as :class:`LineDetectionResult`

        Parameters
        ----------
        image : np.ndarray
            BGR or grayscale input image.

        Returns
        -------
        LineDetectionResult
            Detected line segments and metadata.

        Raises
        ------
        ValueError
            If *image* is empty or ``None``.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        t0 = time.perf_counter()

        # 1. Preprocess
        if self.config.use_preprocessing:
            preprocessed = self._preprocessor.preprocess(image)
        else:
            preprocessed = image
            if len(preprocessed.shape) == 3:
                preprocessed = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2GRAY)

        # 2. Canny
        edges = self.canny_edges(preprocessed)

        # 3. Hough
        raw = self.hough_lines(edges)

        # 4. Convert
        lines = self.hough_to_lines(raw)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        h, w = image.shape[:2]
        return LineDetectionResult(
            lines=lines,
            source_shape=(h, w),
            detection_time_ms=elapsed_ms,
            parameters={
                "canny_low": self.config.canny_low_threshold,
                "canny_high": self.config.canny_high_threshold,
                "hough_threshold": self.config.hough_threshold,
                "min_line_length": self.config.min_line_length,
                "max_line_gap": self.config.max_line_gap,
            },
        )

    def detect_edges_only(self, image: np.ndarray) -> np.ndarray:
        """Return just the Canny edge map (useful for UI previews).

        Parameters
        ----------
        image : np.ndarray
            BGR or grayscale input image.

        Returns
        -------
        np.ndarray
            Binary edge map.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        if self.config.use_preprocessing:
            preprocessed = self._preprocessor.preprocess(image)
        else:
            preprocessed = image
            if len(preprocessed.shape) == 3:
                preprocessed = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2GRAY)

        return self.canny_edges(preprocessed)

    # -- Parameter tuning helpers -------------------------------------------

    def update_canny_thresholds(self, low: int, high: int) -> None:
        """Update Canny thresholds at runtime (e.g. from trackbar).

        Parameters
        ----------
        low : int
            New lower threshold.
        high : int
            New upper threshold.
        """
        self.config.canny_low_threshold = low
        self.config.canny_high_threshold = high

    def update_hough_params(
        self,
        threshold: Optional[int] = None,
        min_line_length: Optional[float] = None,
        max_line_gap: Optional[float] = None,
    ) -> None:
        """Update Hough parameters at runtime.

        Only the supplied arguments are changed; ``None`` values are
        ignored.
        """
        if threshold is not None:
            self.config.hough_threshold = threshold
        if min_line_length is not None:
            self.config.min_line_length = min_line_length
        if max_line_gap is not None:
            self.config.max_line_gap = max_line_gap

    def suggest_canny_thresholds(self, image: np.ndarray) -> Tuple[int, int]:
        """Suggest Canny thresholds based on Otsu's method.

        Computes the Otsu threshold on the grayscale image and derives
        low/high thresholds using the commonly recommended ratio of
        ``0.5 * otsu`` and ``1.0 * otsu``.

        Parameters
        ----------
        image : np.ndarray
            BGR or grayscale image.

        Returns
        -------
        tuple of int
            ``(low_threshold, high_threshold)``
        """
        gray = image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        otsu_thresh, _ = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        low = int(max(1, otsu_thresh * 0.5))
        high = int(otsu_thresh)
        return (low, high)

    def auto_detect(self, image: np.ndarray) -> LineDetectionResult:
        """Detect lines with automatically tuned Canny thresholds.

        Calls :meth:`suggest_canny_thresholds`, temporarily applies the
        suggested values, runs detection, then restores the originals.

        Parameters
        ----------
        image : np.ndarray
            BGR or grayscale input image.

        Returns
        -------
        LineDetectionResult
        """
        # Save originals
        orig_low = self.config.canny_low_threshold
        orig_high = self.config.canny_high_threshold

        try:
            low, high = self.suggest_canny_thresholds(image)
            self.config.canny_low_threshold = low
            self.config.canny_high_threshold = high
            return self.detect(image)
        finally:
            # Restore
            self.config.canny_low_threshold = orig_low
            self.config.canny_high_threshold = orig_high
