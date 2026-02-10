# Angle Measurement Tool

[![CI](https://github.com/pensa1/angle-measurement/workflows/CI/badge.svg)](https://github.com/pensa1/angle-measurement/actions/workflows/ci.yml)
[![Lint](https://github.com/pensa1/angle-measurement/workflows/Lint/badge.svg)](https://github.com/pensa1/angle-measurement/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/pensa1/angle-measurement/branch/main/graph/badge.svg)](https://codecov.io/gh/pensa1/angle-measurement)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<img src="result/result.png" alt="Angle Measurement Tool Result Example" width="400"/>

An interactive Python tool for measuring angles in images, video streams, and live webcam feeds. Mark three points to measure the angle formed at the center point, with support for multiple input sources and result saving.

## Features

- **Multi-source Input**: Measure angles on static images, webcam feeds, or video files
- **Interactive GUI**: Intuitive graphical interface with mouse-based point marking
- **Real-time Calculation**: Instant angle calculation using vector dot product method
- **Result Saving**: Save annotated images with measured angles for documentation
- **Flexible Workflow**: Switch between different input sources without restarting
- **Keyboard Shortcuts**: Quick commands for clearing points and saving results

## Installation

1. Clone this repository to your local machine:

   ```
   git clone https://github.com/your-username/angle-measurement-tool.git
   ```

2. Navigate to the project directory:

   ```
   cd angle-measurement-tool
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Line Detection

Automatically detect and measure angles in an image:

```python
import cv2
from detection.line_detector import LineDetector
from detection.postprocessor import LinePostprocessor

# Load image
image = cv2.imread("path/to/image.jpg")

# Detect lines
detector = LineDetector()
detection_result = detector.detect(image)

print(f"Found {len(detection_result.lines)} lines")
print(f"Detection took {detection_result.detection_time_ms:.2f}ms")

# Post-process (merge, filter)
postprocessor = LinePostprocessor()
processed_result = postprocessor.process_result(detection_result)

print(f"After post-processing: {len(processed_result.lines)} lines")

# Get angle measurements
measurements = postprocessor.find_angles(processed_result.lines)

for m in measurements:
    print(f"Angle: {m.angle_degrees:.1f}° at vertex {m.vertex}")
```

### Automatic Parameter Tuning

Let the detector suggest optimal Canny thresholds for your image:

```python
from detection.line_detector import LineDetector

detector = LineDetector()

# Suggest thresholds based on image content
low, high = detector.suggest_canny_thresholds(image)
print(f"Suggested: low={low}, high={high}")

# Use auto-detected thresholds
result = detector.auto_detect(image)
```

### Parameter Tuning

Customize detection parameters for your use case:

```python
from detection.line_detector import LineDetector, LineDetectorConfig
from detection.preprocessor import ImagePreprocessor, PreprocessorConfig

# Configure preprocessing
prep_config = PreprocessorConfig(
    use_clahe=True,              # enhance contrast
    clahe_clip_limit=2.5,        # more aggressive
    blur_kernel_size=(5, 5),
)

# Configure detection
detect_config = LineDetectorConfig(
    canny_low_threshold=40,      # lower for more edges
    canny_high_threshold=120,
    hough_threshold=40,
    min_line_length=50,
    max_line_gap=15,
)

# Create detector with custom config
detector = LineDetector(
    config=detect_config,
    preprocessor_config=prep_config
)

result = detector.detect(image)
```

### Accessing Detection Results

```python
from detection.line_detector import LineDetector

detector = LineDetector()
result = detector.detect(image)

# Access detected lines
for i, line in enumerate(result.lines):
    print(f"Line {i}:")
    print(f"  From: ({line.x1:.1f}, {line.y1:.1f})")
    print(f"  To:   ({line.x2:.1f}, {line.y2:.1f})")
    print(f"  Length: {line.length:.1f} pixels")
    print(f"  Angle: {line.angle():.1f}°")

# Access metadata
print(f"Image size: {result.source_shape}")
print(f"Detection time: {result.detection_time_ms:.2f}ms")
print(f"Parameters used: {result.parameters}")
```

### Visualizing Detection

```python
import cv2
from detection.line_detector import LineDetector

detector = LineDetector()
result = detector.detect(image)

# Draw detected lines on the image
output = image.copy()
for line in result.lines:
    pt1 = (int(line.x1), int(line.y1))
    pt2 = (int(line.x2), int(line.y2))
    cv2.line(output, pt1, pt2, (0, 255, 0), 2)

# Draw angle vertices
from detection.postprocessor import LinePostprocessor
postprocessor = LinePostprocessor()
measurements = postprocessor.find_angles(result.lines)

for m in measurements:
    cv2.circle(output, (int(m.vertex[0]), int(m.vertex[1])), 5, (0, 0, 255), -1)
    cv2.putText(output, f"{m.angle_degrees:.1f}°",
                (int(m.vertex[0]), int(m.vertex[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

cv2.imshow("Detected Lines and Angles", output)
cv2.waitKey(0)
```

## Usage

### Running the Application

```bash
python setup.py
```

### Measurement Process

1. **Select Input Source**: Use the trackbars at the top of the window to select your input source:
   - **Camera**: Switch to 1 to use your webcam
   - **Video**: Switch to 1 to use a video file

2. **Mark Points**: Click three points on the displayed image:
   - **Point 1**: First endpoint of the angle
   - **Point 2**: Vertex (the angle is measured at this point)
   - **Point 3**: Second endpoint of the angle

3. **View Result**: The calculated angle appears automatically after marking all three points

4. **Keyboard Controls**:
   - **'c'**: Clear all points and start over
   - **'s'**: Save the current annotated image with measured angle
   - **'q' or 'Esc'**: Exit the application

### Example Workflow

```
1. Start the application
2. Camera trackbar is at 0 (image mode) by default
3. Click three points on the image to form an angle
4. See the angle value displayed on the image
5. Press 's' to save the annotated image
6. Press 'c' to clear and measure another angle
7. Switch Camera trackbar to 1 to use webcam
8. Repeat steps 3-6 with live camera feed
9. Press 'q' to exit
```

## Requirements

- **Python**: 3.x
- **OpenCV (cv2)**: Computer vision library for image processing
- **NumPy**: Numerical computing for vector operations
- **imutils**: OpenCV convenience functions

### Installing Dependencies

```bash
pip install opencv-python numpy imutils
```

## Testing

The project uses pytest for testing. Test files are located in the `tests/` directory.

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Category

```bash
# Test geometry functions
pytest tests/test_geometry.py -v

# Test detection pipeline
pytest tests/test_detection.py -v

# Test UI components
pytest tests/test_ui.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Current Test Status

- Core geometry functions: In development
- Detection pipeline: Planned (Phase 2)
- UI interactions: Planned (Phase 3)

See [AGENT_TEAM_PLAN.md](AGENT_TEAM_PLAN.md) for testing phase timeline.

## File Structure

```
angle-measurement/
├── setup.py                    # Main application entry point
├── utils/
│   ├── image.py               # Image loading utilities
│   ├── webcam.py              # Webcam stream initialization
│   ├── video.py               # Video file loading
│   └── file.py                # Filename generation for saving results
├── img/
│   └── sample.jpg             # Sample image for testing
├── video/
│   └── sample.mp4             # Sample video for testing
├── result/                     # Directory for saved annotated images
├── tests/                      # Test files (in development)
├── core/                       # Geometry module (in development)
├── detection/                  # Line detection module (in development)
├── ui/                         # UI components (in development)
└── workflows/                  # Application workflows (in development)
```

## Development

This project is undergoing a refactoring from a monolithic structure into a modular, maintainable architecture. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed information about the planned structure and module responsibilities.

### Project Status

**Current Version (v0.1)**: Basic angle measurement with manual point clicking

**In Development (v1.0)**:
- Modular architecture with separate concerns
- Automatic line detection using Canny + Hough Transform
- Hybrid mode with user refinement capabilities
- Comprehensive test coverage

### Documentation

- **ARCHITECTURE.md**: Detailed system design and module responsibilities
- **ALGORITHMS.md**: Mathematical explanation of the angle calculation algorithm
- **AGENT_TEAM_PLAN.md**: Development team structure and responsibilities

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd angle-measurement

# Install dependencies
pip install -r requirements.txt

# Run tests (when available)
pytest tests/
```

### Building New Modules

When contributing new modules, follow the architecture guidelines in [ARCHITECTURE.md](ARCHITECTURE.md):

1. Place code in appropriate module directory (core/, detection/, ui/, etc.)
2. Add docstrings following Google style
3. Include unit tests in tests/
4. Update ARCHITECTURE.md if creating new modules
5. Ensure low coupling between modules

### Contributing

The project uses a multi-agent team structure for development:

1. **Core Algorithms Agent**: Geometry and mathematics
2. **Detection Specialist**: Line detection algorithms
3. **UI/UX Agent**: User interface and interactions
4. **Documentation Agent**: Code documentation and guides
5. **Testing Agent**: Quality assurance and testing

See [AGENT_TEAM_PLAN.md](AGENT_TEAM_PLAN.md) for detailed information about team responsibilities.
