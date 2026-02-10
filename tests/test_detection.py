"""
Unit tests for line detection algorithms.

These tests validate the Canny edge detection, Hough transform line detection,
line merging, and filtering algorithms.
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestPreprocessing:
    """Tests for image preprocessing pipeline."""

    @pytest.mark.unit
    @pytest.mark.detection
    def test_grayscale_conversion(self):
        """Test RGB to grayscale conversion."""
        from detection.preprocessor import ImagePreprocessor

        # Create a color test image
        color_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        color_image[:, :, 0] = 255  # Blue channel

        preprocessor = ImagePreprocessor()
        gray = preprocessor.to_grayscale(color_image)

        # Verify output is grayscale (2D)
        assert len(gray.shape) == 2, "Output should be 2D grayscale"
        assert gray.shape == (100, 100), "Shape should match input dimensions"
        assert gray.dtype == np.uint8, "Output should be uint8"

        # Test with already grayscale image
        gray_input = np.ones((50, 50), dtype=np.uint8) * 200
        gray_output = preprocessor.to_grayscale(gray_input)
        assert gray_output.shape == (50, 50), "Grayscale input should pass through"

        # Test error handling
        with pytest.raises(ValueError):
            preprocessor.to_grayscale(None)

    @pytest.mark.unit
    @pytest.mark.detection
    def test_gaussian_blur(self):
        """Test Gaussian blur application."""
        from detection.preprocessor import ImagePreprocessor, PreprocessorConfig

        # Create test image
        test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

        config = PreprocessorConfig(blur_kernel_size=(5, 5), blur_sigma=0)
        preprocessor = ImagePreprocessor(config)

        blurred = preprocessor.apply_gaussian_blur(test_image)

        # Verify output properties
        assert blurred.shape == test_image.shape, "Shape should be preserved"
        assert blurred.dtype == np.uint8, "Dtype should be preserved"

        # Blurred image should have lower variance (smoother)
        assert np.var(blurred) <= np.var(test_image), "Blur should reduce variance"

        # Test with custom parameters
        custom_blur = preprocessor.apply_gaussian_blur(test_image, kernel_size=(7, 7), sigma=1.5)
        assert custom_blur.shape == test_image.shape, "Custom blur should preserve shape"

        # Test error handling
        with pytest.raises(ValueError):
            preprocessor.apply_gaussian_blur(None)

    @pytest.mark.unit
    @pytest.mark.detection
    def test_contrast_enhancement(self):
        """Test image contrast enhancement."""
        from detection.preprocessor import ImagePreprocessor, PreprocessorConfig

        # Create low-contrast test image
        low_contrast = np.random.randint(100, 150, (100, 100), dtype=np.uint8)

        config = PreprocessorConfig(clahe_clip_limit=2.0, clahe_tile_grid_size=(8, 8))
        preprocessor = ImagePreprocessor(config)

        enhanced = preprocessor.apply_clahe(low_contrast)

        # Verify output properties
        assert enhanced.shape == low_contrast.shape, "Shape should be preserved"
        assert enhanced.dtype == np.uint8, "Dtype should be uint8"

        # Enhanced image should have higher standard deviation (more contrast)
        assert np.std(enhanced) >= np.std(low_contrast), "CLAHE should increase contrast"

        # Test error handling - CLAHE requires single channel
        with pytest.raises(ValueError):
            color_image = np.ones((100, 100, 3), dtype=np.uint8)
            preprocessor.apply_clahe(color_image)

        with pytest.raises(ValueError):
            preprocessor.apply_clahe(None)


class TestCannyEdgeDetection:
    """Tests for Canny edge detection."""

    @pytest.mark.unit
    @pytest.mark.detection
    def test_canny_basic(self):
        """Test basic Canny edge detection."""
        from detection.line_detector import LineDetector

        # Create simple test image with edges
        test_image = np.zeros((100, 100), dtype=np.uint8)
        # Draw a horizontal line
        test_image[40:60, :] = 255

        detector = LineDetector()
        edges = detector.canny_edges(test_image)

        # Verify output properties
        assert edges.shape == test_image.shape, "Edge map should match input shape"
        assert edges.dtype == np.uint8, "Edge map should be uint8"

        # Should detect edges around the line boundaries
        edge_pixels = np.sum(edges > 0)
        assert edge_pixels > 0, "Should detect some edges"

        # Test with custom thresholds
        edges_high = detector.canny_edges(test_image, low=100, high=200)
        assert edges_high.shape == test_image.shape, "Custom thresholds should work"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_canny_threshold_adaptation(self):
        """Test adaptive threshold selection for Canny."""
        from detection.line_detector import LineDetector

        # Create test image
        test_image = np.random.randint(0, 255, (200, 200), dtype=np.uint8)

        detector = LineDetector()
        low, high = detector.suggest_canny_thresholds(test_image)

        # Verify reasonable threshold values
        assert low > 0, "Low threshold should be positive"
        assert high > low, "High threshold should be greater than low"
        assert low < 255, "Low threshold should be in valid range"
        assert high <= 255, "High threshold should be in valid range"

        # Test auto_detect
        result = detector.auto_detect(test_image)
        assert result is not None, "Auto detect should return a result"
        assert isinstance(result.lines, list), "Should return a list of lines"

    @pytest.mark.unit
    @pytest.mark.detection
    @pytest.mark.fixture
    def test_canny_on_synthetic_images(self):
        """Test Canny detection on synthetic test images."""
        from detection.line_detector import LineDetector

        # Test on a fixture with known lines
        fixture_path = project_root / "tests/fixtures/angle_90_degrees.png"
        image = cv2.imread(str(fixture_path))
        assert image is not None, f"Failed to load fixture: {fixture_path}"

        detector = LineDetector()
        edges = detector.canny_edges(image)

        # Should detect edges in the synthetic image
        edge_pixels = np.sum(edges > 0)
        assert edge_pixels > 100, "Should detect significant edges in synthetic image"

        # Test edges are concentrated in expected regions (not just noise)
        edge_ratio = edge_pixels / (edges.shape[0] * edges.shape[1])
        assert 0.001 < edge_ratio < 0.5, "Edge density should be reasonable"


class TestHoughLineDetection:
    """Tests for Hough Transform line detection."""

    @pytest.mark.unit
    @pytest.mark.detection
    def test_hough_line_detection_basic(self):
        """Test basic Hough line detection."""
        from detection.line_detector import LineDetector

        # Create test image with a clear horizontal line
        test_image = np.zeros((200, 200), dtype=np.uint8)
        test_image[95:105, 20:180] = 255  # Thick horizontal line

        detector = LineDetector()
        edges = detector.canny_edges(test_image)
        hough_output = detector.hough_lines(edges)

        # Should detect at least one line segment
        assert hough_output is not None, "Hough should return result"
        assert len(hough_output.shape) == 3, "Hough output should be 3D array"

        if hough_output.size > 0:
            assert hough_output.shape[2] == 4, "Each line should have 4 coordinates"

        # Convert to Line objects
        lines = detector.hough_to_lines(hough_output)
        assert isinstance(lines, list), "Should return a list of Line objects"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_hough_probabilistic(self):
        """Test probabilistic Hough line detection."""
        from detection.line_detector import LineDetector
        from core.geometry import Line

        # Create test image with multiple line segments
        test_image = np.zeros((300, 300), dtype=np.uint8)
        test_image[50:55, 50:250] = 255  # Horizontal
        test_image[50:250, 150:155] = 255  # Vertical

        detector = LineDetector()
        result = detector.detect(test_image)

        # Should detect lines
        assert len(result.lines) >= 1, "Should detect at least one line"
        assert all(isinstance(ln, Line) for ln in result.lines), "All should be Line objects"

        # Verify detection result metadata
        assert result.source_shape == (300, 300), "Source shape should be recorded"
        assert result.detection_time_ms > 0, "Detection time should be measured"
        assert "canny_low" in result.parameters, "Parameters should be recorded"

    @pytest.mark.unit
    @pytest.mark.detection
    @pytest.mark.fixture
    def test_hough_on_90_degree_lines(self):
        """Test Hough detection on perpendicular lines fixture."""
        from detection.line_detector import LineDetector

        fixture_path = project_root / "tests/fixtures/angle_90_degrees.png"
        image = cv2.imread(str(fixture_path))
        assert image is not None, f"Failed to load fixture: {fixture_path}"

        detector = LineDetector()
        result = detector.detect(image)

        # Should detect at least 2 lines (horizontal and vertical)
        assert len(result.lines) >= 2, f"Should detect at least 2 lines, got {len(result.lines)}"

        # Verify lines have reasonable properties
        for line in result.lines:
            assert line.length > 20, "Detected lines should have meaningful length"

    @pytest.mark.unit
    @pytest.mark.detection
    @pytest.mark.fixture
    def test_hough_on_parallel_lines(self):
        """Test Hough detection on parallel lines fixture."""
        from detection.line_detector import LineDetector

        fixture_path = project_root / "tests/fixtures/parallel_lines_0_degrees.png"
        image = cv2.imread(str(fixture_path))
        assert image is not None, f"Failed to load fixture: {fixture_path}"

        detector = LineDetector()
        result = detector.detect(image)

        # Should detect multiple parallel lines
        assert len(result.lines) >= 1, f"Should detect at least 1 line, got {len(result.lines)}"

        # Verify detection completed in reasonable time
        assert result.detection_time_ms < 5000, "Detection should complete in under 5s"


class TestLineMerging:
    """Tests for line merging and filtering algorithms."""

    @pytest.mark.unit
    @pytest.mark.detection
    def test_merge_collinear_segments(self):
        """Test merging of collinear line segments."""
        from detection.postprocessor import LinePostprocessor
        from core.geometry import Line

        # Create collinear line segments that should be merged
        lines = [
            Line(10, 10, 50, 10),  # Horizontal segment 1
            Line(55, 10, 100, 10),  # Horizontal segment 2 (slight gap, should merge)
        ]

        pp = LinePostprocessor()
        merged = pp.merge_lines(lines)

        # Should merge into fewer lines
        assert len(merged) <= len(lines), "Merging should not increase line count"

        # Test with segments that should NOT merge (different angles)
        lines2 = [
            Line(10, 10, 50, 10),  # Horizontal
            Line(10, 10, 10, 50),  # Vertical
        ]
        merged2 = pp.merge_lines(lines2)
        assert len(merged2) == 2, "Different angle lines should not merge"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_filter_short_lines(self):
        """Test filtering out short line segments."""
        from detection.postprocessor import LinePostprocessor
        from core.geometry import Line

        # Create lines with different lengths
        lines = [
            Line(0, 0, 100, 0),   # Long line (length 100)
            Line(0, 10, 5, 10),   # Short line (length 5)
            Line(0, 20, 50, 20),  # Medium line (length 50)
            Line(0, 30, 10, 30),  # Short line (length 10)
        ]

        pp = LinePostprocessor()
        filtered = pp.filter_short_lines(lines, min_length=30)

        # Should keep only lines >= 30 pixels
        assert len(filtered) == 2, f"Should keep 2 lines, kept {len(filtered)}"
        assert all(ln.length >= 30 for ln in filtered), "All filtered lines should meet minimum"

        # Test with default config
        filtered2 = pp.filter_short_lines(lines)
        assert len(filtered2) >= 1, "Should keep at least one line with defaults"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_remove_duplicate_lines(self):
        """Test removal of duplicate line detections."""
        from detection.postprocessor import LinePostprocessor
        from core.geometry import Line

        # Create duplicate and near-duplicate lines
        lines = [
            Line(10, 10, 100, 10),
            Line(11, 10, 101, 10),  # Near duplicate
            Line(10, 10, 100, 10),  # Exact duplicate
            Line(50, 50, 150, 50),  # Different line
        ]

        pp = LinePostprocessor()
        unique = pp.remove_duplicates(lines)

        # Should remove duplicates
        assert len(unique) < len(lines), "Should remove duplicate lines"
        assert len(unique) >= 2, "Should keep at least 2 distinct lines"

        # Test with no duplicates
        lines2 = [
            Line(0, 0, 100, 0),
            Line(0, 100, 100, 100),
        ]
        unique2 = pp.remove_duplicates(lines2)
        assert len(unique2) == len(lines2), "Should keep all unique lines"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_merge_nearby_parallel_lines(self):
        """Test merging of nearby parallel line segments."""
        from detection.postprocessor import LinePostprocessor
        from core.geometry import Line

        # Create nearby parallel lines
        lines = [
            Line(10, 10, 100, 10),  # Horizontal line 1
            Line(10, 12, 100, 12),  # Parallel, very close
        ]

        pp = LinePostprocessor()
        merged = pp.merge_lines(lines)

        # These should potentially merge (they're nearly collinear)
        assert len(merged) >= 1, "Should return at least one line"

        # Test grouping by angle
        groups = pp.group_by_angle(lines)
        assert len(groups) >= 1, "Should group parallel lines"

        # All lines in a group should have similar angles
        for angle, group in groups.items():
            assert len(group) > 0, "Groups should not be empty"


class TestParameterTuning:
    """Tests for parameter auto-tuning algorithms."""

    @pytest.mark.unit
    @pytest.mark.detection
    def test_adaptive_threshold_selection(self):
        """Test adaptive threshold selection based on image statistics."""
        from detection.line_detector import LineDetector

        # Create images with different characteristics (add some variation to avoid uniform images)
        bright_image = np.ones((200, 200), dtype=np.uint8) * 200
        bright_image[50:100, 50:100] = 180  # Add some variation

        dark_image = np.ones((200, 200), dtype=np.uint8) * 50
        dark_image[50:100, 50:100] = 70  # Add some variation

        mixed_image = np.random.randint(0, 255, (200, 200), dtype=np.uint8)

        detector = LineDetector()

        # Test threshold suggestion on different images
        low1, high1 = detector.suggest_canny_thresholds(bright_image)
        low2, high2 = detector.suggest_canny_thresholds(dark_image)
        low3, high3 = detector.suggest_canny_thresholds(mixed_image)

        # All should return valid thresholds (allowing for edge case where uniform images might have high=low)
        for low, high in [(low1, high1), (low2, high2), (low3, high3)]:
            assert low >= 1, f"Low threshold too small: {low}"
            assert high >= low, f"High threshold should be >= low: low={low}, high={high}"
            assert high <= 255, f"High threshold out of range: {high}"

        # Mixed image should have reasonable thresholds
        assert 0 < low3 < high3 <= 255, "Mixed image should have valid distinct thresholds"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_parameter_optimization(self):
        """Test parameter optimization for different image types."""
        from detection.line_detector import LineDetector, LineDetectorConfig
        from detection.preprocessor import ImagePreprocessor

        # Create test image
        test_image = np.random.randint(0, 255, (200, 200), dtype=np.uint8)

        # Test different configurations
        config1 = LineDetectorConfig(canny_low_threshold=30, canny_high_threshold=100)
        config2 = LineDetectorConfig(canny_low_threshold=80, canny_high_threshold=200)

        detector1 = LineDetector(config1)
        detector2 = LineDetector(config2)

        result1 = detector1.detect(test_image)
        result2 = detector2.detect(test_image)

        # Both should complete successfully
        assert result1 is not None, "Config 1 should work"
        assert result2 is not None, "Config 2 should work"

        # Test parameter updates
        detector1.update_canny_thresholds(50, 150)
        assert detector1.config.canny_low_threshold == 50
        assert detector1.config.canny_high_threshold == 150

        detector1.update_hough_params(threshold=60, min_line_length=40)
        assert detector1.config.hough_threshold == 60
        assert detector1.config.min_line_length == 40


class TestDetectionQuality:
    """Tests for detection quality metrics."""

    @pytest.mark.integration
    @pytest.mark.detection
    @pytest.mark.fixture
    def test_detection_accuracy_known_angles(self):
        """Test detection accuracy on images with known angles."""
        from detection.line_detector import LineDetector
        from detection.postprocessor import LinePostprocessor

        # Test on fixtures with known angles
        test_angles = [30, 45, 60, 90, 120, 135]
        detector = LineDetector()
        pp = LinePostprocessor()

        successful_detections = 0
        total_tests = len(test_angles)

        for angle in test_angles:
            fixture_path = project_root / f"tests/fixtures/angle_{angle}_degrees.png"
            if not fixture_path.exists():
                continue

            image = cv2.imread(str(fixture_path))
            if image is None:
                continue

            result = detector.detect(image)
            processed = pp.process(result.lines)

            # Should detect at least 2 lines for angle measurement
            if len(processed) >= 2:
                successful_detections += 1

        # Should successfully detect lines in most fixtures
        success_rate = successful_detections / total_tests if total_tests > 0 else 0
        assert success_rate >= 0.5, f"Detection rate too low: {success_rate:.1%}"

    @pytest.mark.integration
    @pytest.mark.detection
    @pytest.mark.fixture
    def test_false_positive_rate(self):
        """Test false positive rate on test images."""
        from detection.line_detector import LineDetector
        from detection.postprocessor import LinePostprocessor

        # Test on synthetic images with known line counts
        fixture_path = project_root / "tests/fixtures/horizontal_line.png"
        image = cv2.imread(str(fixture_path))
        assert image is not None, f"Failed to load fixture: {fixture_path}"

        detector = LineDetector()
        result = detector.detect(image)

        # Should detect reasonable number of lines (not thousands)
        assert len(result.lines) < 100, f"Too many lines detected: {len(result.lines)}"

        # After post-processing, should have very few lines
        pp = LinePostprocessor()
        processed = pp.process(result.lines)
        assert len(processed) < 20, f"Too many lines after processing: {len(processed)}"

    @pytest.mark.integration
    @pytest.mark.detection
    @pytest.mark.slow
    def test_detection_performance(self):
        """Test detection speed (should be <500ms per frame)."""
        from detection.line_detector import LineDetector
        from detection.postprocessor import LinePostprocessor
        import time

        # Load a fixture image
        fixture_path = project_root / "tests/fixtures/angle_90_degrees.png"
        image = cv2.imread(str(fixture_path))
        assert image is not None, "Failed to load test image"

        detector = LineDetector()
        pp = LinePostprocessor()

        # Run detection multiple times and measure performance
        iterations = 5
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            result = detector.detect(image)
            processed = pp.process(result.lines)
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Should complete in under 500ms on average
        assert avg_time < 500, f"Average detection time too slow: {avg_time:.1f}ms"

        # Maximum should also be reasonable (allowing for some variance)
        assert max_time < 1000, f"Maximum detection time too slow: {max_time:.1f}ms"

        # Print performance info for documentation
        print(f"\nPerformance metrics:")
        print(f"  Average: {avg_time:.1f}ms")
        print(f"  Min: {min(times):.1f}ms")
        print(f"  Max: {max_time:.1f}ms")


class TestEdgeCases:
    """Tests for edge cases in detection."""

    @pytest.mark.unit
    @pytest.mark.detection
    def test_no_lines_detected(self):
        """Test handling when no lines are detected."""
        from detection.line_detector import LineDetector
        from detection.postprocessor import LinePostprocessor

        # Create blank image with no edges
        blank_image = np.ones((100, 100), dtype=np.uint8) * 128

        detector = LineDetector()
        result = detector.detect(blank_image)

        # Should handle gracefully with empty result
        assert result is not None, "Should return result even with no lines"
        assert isinstance(result.lines, list), "Lines should be a list"
        assert result.detection_time_ms > 0, "Detection time should be measured"

        # Test postprocessor with empty lines
        pp = LinePostprocessor()
        processed = pp.process([])
        assert processed == [], "Processing empty list should return empty list"

        angles = pp.find_angles([])
        assert angles == [], "Should return empty angles for no lines"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_very_noisy_image(self):
        """Test detection on very noisy images."""
        from detection.line_detector import LineDetector
        from detection.preprocessor import ImagePreprocessor, PreprocessorConfig

        # Create very noisy image
        noisy_image = np.random.randint(0, 255, (200, 200), dtype=np.uint8)

        # Test with preprocessing (should help with noise)
        detector = LineDetector()
        result = detector.detect(noisy_image)

        assert result is not None, "Should handle noisy images"
        assert isinstance(result.lines, list), "Should return a list"

        # Test noise estimation
        preprocessor = ImagePreprocessor()
        noise_level = preprocessor.estimate_noise_level(noisy_image)
        assert noise_level >= 0, "Noise level should be non-negative"

        # Very noisy images should have high noise level
        assert noise_level > 1.0, "Random noise should be detected as noisy"

    @pytest.mark.unit
    @pytest.mark.detection
    def test_poor_lighting(self):
        """Test detection under poor lighting conditions."""
        from detection.line_detector import LineDetector
        from detection.preprocessor import ImagePreprocessor, PreprocessorConfig

        # Create low-contrast image (poor lighting simulation)
        low_contrast = np.random.randint(100, 150, (200, 200), dtype=np.uint8)

        # CLAHE should help with poor lighting
        config = PreprocessorConfig(use_clahe=True, clahe_clip_limit=3.0)
        preprocessor = ImagePreprocessor(config)

        enhanced = preprocessor.preprocess(low_contrast)
        assert enhanced is not None, "Preprocessing should handle poor lighting"

        # Test image statistics
        stats = preprocessor.analyze_image_stats(low_contrast)
        assert "mean" in stats, "Should compute mean"
        assert "std" in stats, "Should compute std"
        assert "contrast_ratio" in stats, "Should compute contrast ratio"

        # Low contrast image should have low contrast ratio
        assert stats["contrast_ratio"] < 0.5, "Should detect low contrast"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
