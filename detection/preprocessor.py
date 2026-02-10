"""
Image preprocessing pipeline for line detection.

Provides a configurable preprocessing chain that converts raw input images
into edge-ready representations optimised for Canny / Hough analysis.

Pipeline stages (in order):
    1. Grayscale conversion
    2. Gaussian blur (noise reduction)
    3. CLAHE (Contrast Limited Adaptive Histogram Equalisation)
    4. Optional morphological operations (dilation / erosion)

Classes:
    PreprocessorConfig: Parameter container for the preprocessing pipeline.
    ImagePreprocessor: Stateless transformer that applies the pipeline.

Example usage::

    >>> import cv2
    >>> from detection.preprocessor import ImagePreprocessor, PreprocessorConfig
    >>> img = cv2.imread("img/sample.jpg")
    >>> preprocessor = ImagePreprocessor()
    >>> gray = preprocessor.preprocess(img)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class PreprocessorConfig:
    """Configuration parameters for the image preprocessing pipeline.

    Parameters
    ----------
    blur_kernel_size : tuple of int
        Kernel size for Gaussian blur.  Must be odd integers.
        Default ``(5, 5)``.
    blur_sigma : float
        Standard deviation for Gaussian blur.  ``0`` lets OpenCV choose
        automatically.  Default ``0``.
    clahe_clip_limit : float
        Contrast limit for CLAHE tiles.  Higher values produce more
        contrast.  Default ``2.0``.
    clahe_tile_grid_size : tuple of int
        Number of tiles in each dimension for CLAHE.  Default ``(8, 8)``.
    use_clahe : bool
        Whether to apply CLAHE enhancement.  Default ``True``.
    use_morphology : bool
        Whether to apply morphological operations.  Default ``False``.
    morph_kernel_size : tuple of int
        Kernel size for morphological operations.  Default ``(3, 3)``.
    morph_operation : str
        One of ``"dilate"``, ``"erode"``, ``"open"``, ``"close"``.
        Default ``"close"`` (fills small gaps in edges).
    morph_iterations : int
        Number of morphological iterations.  Default ``1``.
    """

    blur_kernel_size: Tuple[int, int] = (5, 5)
    blur_sigma: float = 0.0
    clahe_clip_limit: float = 2.0
    clahe_tile_grid_size: Tuple[int, int] = (8, 8)
    use_clahe: bool = True
    use_morphology: bool = False
    morph_kernel_size: Tuple[int, int] = (3, 3)
    morph_operation: str = "close"
    morph_iterations: int = 1


# ---------------------------------------------------------------------------
# ImagePreprocessor
# ---------------------------------------------------------------------------

class ImagePreprocessor:
    """Configurable image preprocessing pipeline.

    Each method performs a single, testable transformation.  The
    :meth:`preprocess` convenience method chains them according to
    the current :class:`PreprocessorConfig`.

    Parameters
    ----------
    config : PreprocessorConfig, optional
        Configuration parameters.  Uses defaults when omitted.
    """

    def __init__(self, config: Optional[PreprocessorConfig] = None) -> None:
        self.config = config or PreprocessorConfig()

    # -- Individual pipeline stages -----------------------------------------

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert an image to single-channel grayscale.

        If the input is already single-channel it is returned unchanged.

        Parameters
        ----------
        image : np.ndarray
            BGR or grayscale image.

        Returns
        -------
        np.ndarray
            Grayscale image of shape ``(H, W)``.

        Raises
        ------
        ValueError
            If *image* is empty or ``None``.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        if len(image.shape) == 2:
            return image.copy()
        if len(image.shape) == 3 and image.shape[2] == 1:
            return image[:, :, 0].copy()

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def apply_gaussian_blur(
        self,
        image: np.ndarray,
        kernel_size: Optional[Tuple[int, int]] = None,
        sigma: Optional[float] = None,
    ) -> np.ndarray:
        """Apply Gaussian blur for noise reduction.

        Parameters
        ----------
        image : np.ndarray
            Input image (grayscale or colour).
        kernel_size : tuple of int, optional
            Override the config kernel size.
        sigma : float, optional
            Override the config sigma.

        Returns
        -------
        np.ndarray
            Blurred image.

        Raises
        ------
        ValueError
            If *image* is empty or ``None``.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        ksize = kernel_size or self.config.blur_kernel_size
        sig = sigma if sigma is not None else self.config.blur_sigma
        return cv2.GaussianBlur(image, ksize, sig)

    def apply_clahe(
        self,
        image: np.ndarray,
        clip_limit: Optional[float] = None,
        tile_grid_size: Optional[Tuple[int, int]] = None,
    ) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalisation (CLAHE).

        The input *must* be a single-channel (grayscale) image.

        Parameters
        ----------
        image : np.ndarray
            Grayscale image of shape ``(H, W)``.
        clip_limit : float, optional
            Override the config clip limit.
        tile_grid_size : tuple of int, optional
            Override the config tile grid size.

        Returns
        -------
        np.ndarray
            Contrast-enhanced grayscale image.

        Raises
        ------
        ValueError
            If *image* is empty, ``None``, or not single-channel.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")
        if len(image.shape) != 2:
            raise ValueError(
                "CLAHE requires a single-channel image; "
                f"got shape {image.shape}."
            )

        cl = clip_limit if clip_limit is not None else self.config.clahe_clip_limit
        tg = tile_grid_size or self.config.clahe_tile_grid_size

        clahe = cv2.createCLAHE(clipLimit=cl, tileGridSize=tg)
        return clahe.apply(image)

    def apply_morphology(
        self,
        image: np.ndarray,
        operation: Optional[str] = None,
        kernel_size: Optional[Tuple[int, int]] = None,
        iterations: Optional[int] = None,
    ) -> np.ndarray:
        """Apply a morphological operation.

        Parameters
        ----------
        image : np.ndarray
            Input image (typically grayscale or binary).
        operation : str, optional
            One of ``"dilate"``, ``"erode"``, ``"open"``, ``"close"``.
            Defaults to the config value.
        kernel_size : tuple of int, optional
            Override the config morphology kernel size.
        iterations : int, optional
            Override the config iteration count.

        Returns
        -------
        np.ndarray
            Morphologically transformed image.

        Raises
        ------
        ValueError
            If *image* is empty/``None`` or *operation* is unknown.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        op = operation or self.config.morph_operation
        ksize = kernel_size or self.config.morph_kernel_size
        iters = iterations if iterations is not None else self.config.morph_iterations

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize)

        ops = {
            "dilate": lambda: cv2.dilate(image, kernel, iterations=iters),
            "erode": lambda: cv2.erode(image, kernel, iterations=iters),
            "open": lambda: cv2.morphologyEx(
                image, cv2.MORPH_OPEN, kernel, iterations=iters
            ),
            "close": lambda: cv2.morphologyEx(
                image, cv2.MORPH_CLOSE, kernel, iterations=iters
            ),
        }

        if op not in ops:
            raise ValueError(
                f"Unknown morphological operation {op!r}. "
                f"Choose from {list(ops.keys())}."
            )

        return ops[op]()

    # -- Full pipeline ------------------------------------------------------

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Run the full preprocessing pipeline.

        Applies grayscale conversion, Gaussian blur, optional CLAHE,
        and optional morphological operations according to the current
        :attr:`config`.

        Parameters
        ----------
        image : np.ndarray
            BGR or grayscale input image.

        Returns
        -------
        np.ndarray
            Preprocessed grayscale image ready for edge detection.

        Raises
        ------
        ValueError
            If *image* is empty or ``None``.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        result = self.to_grayscale(image)
        result = self.apply_gaussian_blur(result)

        if self.config.use_clahe:
            result = self.apply_clahe(result)

        if self.config.use_morphology:
            result = self.apply_morphology(result)

        return result

    # -- Image analysis helpers ---------------------------------------------

    @staticmethod
    def analyze_image_stats(image: np.ndarray) -> dict:
        """Compute basic statistics about a grayscale image.

        Useful for adaptive parameter tuning.

        Parameters
        ----------
        image : np.ndarray
            Grayscale image of shape ``(H, W)``.

        Returns
        -------
        dict
            Keys: ``mean``, ``std``, ``median``, ``min``, ``max``,
            ``contrast_ratio``.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        gray = image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        mean_val = float(np.mean(gray))
        std_val = float(np.std(gray))
        median_val = float(np.median(gray))
        min_val = int(np.min(gray))
        max_val = int(np.max(gray))
        contrast_ratio = float(max_val - min_val) / 255.0 if max_val > min_val else 0.0

        return {
            "mean": mean_val,
            "std": std_val,
            "median": median_val,
            "min": min_val,
            "max": max_val,
            "contrast_ratio": contrast_ratio,
        }

    @staticmethod
    def estimate_noise_level(image: np.ndarray) -> float:
        """Estimate the noise level of a grayscale image.

        Uses the Laplacian variance method: a higher variance indicates
        more texture/edges, while a very low variance indicates a mostly
        flat (possibly blurry) image.  For noise estimation the median
        absolute deviation of the Laplacian is used, which is more robust
        to actual edges.

        Parameters
        ----------
        image : np.ndarray
            Grayscale image.

        Returns
        -------
        float
            Estimated noise sigma.  Typical values: 0-5 clean, 5-15
            moderate noise, >15 heavy noise.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or None.")

        gray = image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sigma = float(np.median(np.abs(laplacian)) * 1.4826)
        return sigma
