# Test Quick Start Guide

## For Developers

### First Time Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify test infrastructure
python -m pytest --collect-only
# Should show: 71 tests collected
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific category
python -m pytest -m geometry    # 39 geometry tests
python -m pytest -m detection   # 22 detection tests
python -m pytest -m integration # 10 integration tests
```

### For Core Algorithms Agent
```bash
# Run geometry tests only
python -m pytest tests/test_geometry.py -v

# Remove pytest.skip() from tests as you implement functions
# Run tests frequently during development
```

### For Detection Agent
```bash
# Run detection tests only
python -m pytest tests/test_detection.py -v

# Use synthetic fixtures in tests/fixtures/*.png
# Test with known angles for validation
```

### Viewing Test Images
```bash
# Test images are in tests/fixtures/
ls tests/fixtures/*.png

# View an image (if display available)
# python -c "import cv2; cv2.imshow('Test', cv2.imread('tests/fixtures/angle_90_degrees.png')); cv2.waitKey(0)"
```

### Current Status
- ✅ Infrastructure ready
- ✅ 71 tests defined
- ✅ 16 synthetic images generated
- ⏳ Tests waiting for implementation (all currently skipped)

### Test-Driven Development Workflow
1. Pick a test function
2. Remove the `pytest.skip()` line
3. Implement the actual test logic
4. Run the test: `python -m pytest tests/test_geometry.py::TestAngleCalculation::test_angle_between_two_lines_perpendicular -v`
5. Implement the feature to make the test pass
6. Repeat

### Need Help?
See `tests/README.md` for detailed documentation.
