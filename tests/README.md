# Test Suite Documentation

This directory contains the comprehensive test suite for the angle measurement project, including unit tests, integration tests, and synthetic test fixtures.

## Directory Structure

```
tests/
├── __init__.py                      # Package initialization
├── README.md                        # This file
├── test_geometry.py                 # Unit tests for geometry calculations
├── test_detection.py                # Unit tests for line detection
├── test_workflows.py                # Integration tests for complete workflows
└── fixtures/                        # Test fixtures and synthetic images
    ├── __init__.py
    ├── create_test_images.py        # Synthetic image generator
    └── *.png                        # Generated test images
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_geometry.py
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only geometry tests
pytest -m geometry

# Run only detection tests
pytest -m detection
```

### Run with Coverage Report
```bash
# Terminal coverage report
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Verbose Mode
```bash
pytest -v
```

### Run Tests and Stop on First Failure
```bash
pytest -x
```

## Test Markers

Tests are organized using pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests across modules
- `@pytest.mark.geometry` - Tests for geometry calculations
- `@pytest.mark.detection` - Tests for line detection
- `@pytest.mark.ui` - Tests for user interface
- `@pytest.mark.slow` - Tests that take more than 1 second
- `@pytest.mark.fixture` - Tests that require synthetic image fixtures

## Synthetic Test Images

The `fixtures/create_test_images.py` script generates synthetic test images with lines at known angles. These images are used for validation and regression testing.

### Generate Test Images

```bash
cd tests/fixtures
python create_test_images.py
```

This will generate:
- **Standard angle images**: 30°, 45°, 60°, 90°, 120°, 135°, 150°, 180°
- **Edge case images**: Vertical lines, horizontal lines, collinear lines
- **Parallel line images**: Parallel lines at various angles
- **Complex images**: Multiple intersecting lines, different length lines

### Test Image Specifications

- **Size**: 400x400 pixels (small and fast)
- **Background**: White (255, 255, 255)
- **Line color**: Black (0, 0, 0) or grayscale
- **Line thickness**: 2-3 pixels
- **Format**: PNG (lossless)

## Test Coverage Requirements

The project aims for **80% or higher** test coverage across all modules:

- `core/` - Core geometry and measurement functions
- `detection/` - Line detection algorithms
- `ui/` - User interface components
- `utils/` - Utility functions

## Writing New Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<Functionality>`
- Test functions: `test_<what_is_being_tested>`

### Example Test Structure

```python
import pytest

@pytest.mark.unit
@pytest.mark.geometry
def test_angle_calculation_perpendicular():
    """Test angle calculation for perpendicular lines."""
    # Arrange
    line1 = {"x1": 0, "y1": 0, "x2": 10, "y2": 0}
    line2 = {"x1": 0, "y1": 0, "x2": 0, "y2": 10}

    # Act
    angle = calculate_angle(line1, line2)

    # Assert
    assert abs(angle - 90.0) < 0.01  # Within tolerance
```

### Using Fixtures

```python
@pytest.fixture
def sample_image():
    """Fixture providing a sample test image."""
    return cv2.imread("tests/fixtures/angle_90_degrees.png")

def test_detection_with_fixture(sample_image):
    """Test using the fixture."""
    assert sample_image is not None
    # Test detection on sample_image
```

## Test Development Workflow

1. **Write tests first** (TDD approach) - Define expected API and behavior
2. **Tests should be skipped initially** - Use `pytest.skip()` while waiting for implementation
3. **Implement functionality** - Core Algorithms Agent, Detection Agent, etc.
4. **Update tests** - Remove `pytest.skip()` and implement actual assertions
5. **Verify coverage** - Ensure coverage requirements are met
6. **Document edge cases** - Add tests for corner cases and error conditions

## Current Test Status

### test_geometry.py
- **Status**: Skeleton tests created, waiting for `core/geometry.py` implementation
- **Test count**: 40+ test stubs
- **Coverage areas**: Angle calculation, distance, line intersection, vector math, edge cases

### test_detection.py
- **Status**: ✅ FULLY ACTIVATED AND PASSING (Phase 2 Complete)
- **Test count**: 22 tests (all passing)
- **Coverage**: 81% of detection module
- **Coverage areas**:
  - Image preprocessing (grayscale, blur, CLAHE) - 3 tests
  - Canny edge detection - 3 tests
  - Hough line detection - 4 tests
  - Line merging and filtering - 4 tests
  - Parameter tuning and adaptation - 2 tests
  - Integration and performance - 3 tests
  - Edge cases (no lines, noise, poor lighting) - 3 tests
- **Performance**: Average 7.3ms per frame (target: <500ms) ✅
- **Integration**: Full pipeline tested with sample.jpg successfully

### test_workflows.py
- **Status**: Skeleton tests created, waiting for full pipeline integration
- **Test count**: 10+ test stubs
- **Coverage areas**: Auto detection, manual mode, hybrid mode, export

## Performance Requirements

Tests should be fast and focused:

- **Unit tests**: < 1 second each
- **Integration tests**: < 5 seconds each (mark as `@pytest.mark.slow` if longer)
- **Full suite**: Should complete in < 1 minute

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```bash
# CI command
pytest --cov --cov-fail-under=80 --tb=short
```

This will:
- Run all tests
- Generate coverage report
- Fail if coverage drops below 80%
- Show short traceback for failures

## Running Detection Tests

The detection tests validate the complete line detection pipeline. All 22 tests are now active and passing.

### Quick Start

```bash
# Run all detection tests
python -m pytest tests/test_detection.py -v

# Run with coverage
python -m pytest tests/test_detection.py --cov=detection --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_detection.py::TestCannyEdgeDetection -v

# Run performance tests
python -m pytest tests/test_detection.py::TestDetectionQuality::test_detection_performance -v -s
```

### Test Categories

#### Preprocessing Tests (3 tests)
- `test_grayscale_conversion` - RGB to grayscale conversion
- `test_gaussian_blur` - Noise reduction via Gaussian blur
- `test_contrast_enhancement` - CLAHE contrast enhancement

#### Canny Edge Detection Tests (3 tests)
- `test_canny_basic` - Basic Canny edge detection
- `test_canny_threshold_adaptation` - Adaptive threshold selection
- `test_canny_on_synthetic_images` - Edge detection on fixtures

#### Hough Line Detection Tests (4 tests)
- `test_hough_line_detection_basic` - Basic Hough transform
- `test_hough_probabilistic` - Probabilistic Hough line detection
- `test_hough_on_90_degree_lines` - Detection on perpendicular lines
- `test_hough_on_parallel_lines` - Detection on parallel lines

#### Line Merging Tests (4 tests)
- `test_merge_collinear_segments` - Merging collinear segments
- `test_filter_short_lines` - Filtering by minimum length
- `test_remove_duplicate_lines` - Deduplication
- `test_merge_nearby_parallel_lines` - Merging parallel lines

#### Parameter Tuning Tests (2 tests)
- `test_adaptive_threshold_selection` - Auto-tuning Canny thresholds
- `test_parameter_optimization` - Parameter updates and optimization

#### Integration Tests (3 tests)
- `test_detection_accuracy_known_angles` - Accuracy on synthetic images
- `test_false_positive_rate` - False positive validation
- `test_detection_performance` - Speed benchmarking (<500ms target)

#### Edge Case Tests (3 tests)
- `test_no_lines_detected` - Handling blank images
- `test_very_noisy_image` - Robustness to noise
- `test_poor_lighting` - Low contrast handling

### Performance Metrics

Based on test results:
- **Average detection time**: 7.3ms per frame
- **Maximum detection time**: 27.4ms per frame
- **Coverage**: 81% of detection module
- **Target performance**: <500ms (achieved: 1.5% of target)

### Example: Full Pipeline Integration

```python
import cv2
from detection.line_detector import LineDetector
from detection.postprocessor import LinePostprocessor

# Load image
img = cv2.imread('img/sample.jpg')

# Detect lines
detector = LineDetector()
result = detector.detect(img)
print(f'Detected {len(result.lines)} lines in {result.detection_time_ms:.1f}ms')

# Post-process
pp = LinePostprocessor()
processed = pp.process(result.lines)
print(f'After filtering: {len(processed)} lines')

# Find angles
angles = pp.find_angles(processed)
best_angle = pp.find_best_angle(processed)
print(f'Best angle: {best_angle.angle_degrees:.1f}°')
```

## Troubleshooting

### Detection Tests

#### Test fixtures not found
Make sure test fixtures exist:
```bash
ls tests/fixtures/*.png
```

If missing, regenerate:
```bash
cd tests/fixtures
python create_test_images.py
```

#### Performance test fails
The performance test expects detection to complete in <500ms on average and <1000ms maximum. If failing:
- Check if running on slow hardware
- Verify no background processes consuming CPU
- Test images are small (400x400), should be fast

#### Coverage seems low
Detection coverage of 81% is good for initial implementation. Uncovered lines are:
- Error handling paths (difficult to trigger in normal operation)
- Optional morphology operations (disabled by default)
- Advanced parameter tuning helpers

### Import Errors

If you get import errors, ensure the project root is in your Python path:

```python
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### Fixture Image Not Found

Generate test images first:

```bash
cd tests/fixtures
python create_test_images.py
```

### Coverage Not Working

Install pytest-cov:

```bash
pip install pytest-cov
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contact

For questions about tests:
- **Testing & Integration Agent**: Responsible for test infrastructure
- **Core Algorithms Agent**: For geometry test cases
- **Detection Agent**: For detection test cases

---

**Last Updated**: 2026-02-10
**Test Framework**: pytest >= 7.0.0
**Coverage Tool**: pytest-cov >= 4.0.0
**Target Coverage**: 80%+
