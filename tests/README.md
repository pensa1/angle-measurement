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
- **Status**: Skeleton tests created, waiting for `detection/` module implementation
- **Test count**: 25+ test stubs
- **Coverage areas**: Preprocessing, Canny edge detection, Hough transform, line merging

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

## Troubleshooting

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
