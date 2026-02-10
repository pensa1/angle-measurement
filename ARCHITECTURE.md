# Architecture Documentation

## Project Overview

The Angle Measurement Tool is being refactored from a monolithic structure into a modular, maintainable architecture. This document describes both the current state and the target architecture.

## Current Project Structure

```
angle-measurement/
├── setup.py                    # Main application (currently monolithic)
├── README.md                   # Project overview
├── requirements.txt            # Python dependencies
├── ARCHITECTURE.md             # This file
├── AGENT_TEAM_PLAN.md         # Team structure and responsibilities
├── AGENT_MODEL_ASSIGNMENT.md  # Model selection strategy
├── utils/
│   ├── __init__.py
│   ├── image.py               # Image loading and preprocessing
│   ├── webcam.py              # Webcam stream initialization
│   ├── video.py               # Video file loading
│   └── file.py                # Filename generation utilities
├── img/
│   └── sample.jpg             # Sample image for testing
├── video/
│   └── sample.mp4             # Sample video for testing
└── result/
    └── (saved measurement results)
```

## Planned Modular Architecture

The application is being refactored into the following modular structure:

```
angle-measurement/
├── core/
│   ├── __init__.py
│   ├── geometry.py            # Vector math, line operations, angle calculations
│   └── measurements.py        # Data structures for storing measurements
├── detection/
│   ├── __init__.py
│   ├── preprocessor.py        # Image preprocessing (blur, normalization, etc.)
│   ├── line_detector.py       # Canny edge detection + Hough Transform
│   └── postprocessor.py       # Line merging, filtering, and refinement
├── ui/
│   ├── __init__.py
│   ├── window_manager.py      # OpenCV window and trackbar management
│   ├── mouse_handler.py       # Interactive point/line editing
│   ├── renderer.py            # Drawing lines, angles, and annotations
│   └── mode_controller.py     # Mode switching (Manual/Auto/Hybrid)
├── workflows/
│   ├── __init__.py
│   ├── manual_mode.py         # User manually clicks points
│   ├── auto_mode.py           # Automatic line detection
│   └── hybrid_mode.py         # User refines detected lines
├── io/
│   ├── __init__.py
│   ├── image_loader.py        # Image file I/O
│   ├── webcam_stream.py       # Webcam stream management
│   ├── video_stream.py        # Video file stream management
│   └── file_saver.py          # Result file saving
├── utils/
│   ├── __init__.py
│   ├── geometry_helpers.py    # Intersection, distance, projection utilities
│   └── parameters.py          # Configuration and parameter management
├── tests/
│   ├── __init__.py
│   ├── test_geometry.py       # Geometry function tests
│   ├── test_detection.py      # Detection pipeline tests
│   ├── test_ui.py             # UI interaction tests
│   └── fixtures/              # Test images and synthetic data
├── setup.py                   # Main entry point
├── main.py                    # Application controller (to be created)
├── ARCHITECTURE.md            # This file
├── ALGORITHMS.md              # Algorithm explanations
├── PARAMETERS.md              # Parameter tuning guide
└── README.md                  # User documentation
```

## Module Responsibilities

### `core/` - Geometry and Calculations

**Purpose**: Encapsulate all geometric calculations and data structures.

**Key Components**:
- **geometry.py**:
  - `Line` class: Represents a line with endpoints and provides methods (length, angle, intersection)
  - Angle calculation algorithms (dot product, vector operations)
  - Vector utilities (normalize, cross product, projection)
  - Line intersection detection
  - Distance calculations

- **measurements.py**:
  - `Measurement` class: Stores angle, endpoints, confidence, and metadata
  - `MeasurementSet` class: Collection of related measurements
  - Export utilities (to CSV, JSON, etc.)

**Dependencies**: numpy, mathematical libraries

**Used By**: detection, ui, workflows modules

---

### `detection/` - Line Detection Pipeline

**Purpose**: Implement computer vision algorithms for automatic line detection.

**Key Components**:
- **preprocessor.py**:
  - Image normalization and denoising
  - Contrast enhancement
  - Gamma correction
  - Adaptive preprocessing based on image characteristics

- **line_detector.py**:
  - Canny edge detection with adaptive thresholds
  - Hough Transform for line detection
  - Parameter optimization
  - Edge detection tuning

- **postprocessor.py**:
  - Line merging (combining fragmented detections)
  - Line filtering (removing noise, short lines)
  - Clustering similar lines
  - Line validation and ranking

**Dependencies**: OpenCV, numpy, core/geometry

**Used By**: workflows (auto mode), ui (preview)

---

### `ui/` - User Interface and Interaction

**Purpose**: Manage all user-facing interface elements and interactions.

**Key Components**:
- **window_manager.py**:
  - OpenCV window creation and management
  - Trackbar creation and management
  - Frame display and refresh
  - Window lifecycle

- **mouse_handler.py**:
  - Mouse event handling (clicks, drag, release)
  - Point marking and selection
  - Line endpoint editing
  - Visual feedback for interactions

- **renderer.py**:
  - Draw circles for marked points
  - Draw lines between points
  - Draw calculated angles
  - Text annotation rendering
  - Color-coded visual feedback

- **mode_controller.py**:
  - Mode state management (Manual/Auto/Hybrid)
  - Mode-specific UI adjustments
  - Trackbar synchronization
  - Input source switching

**Dependencies**: OpenCV, core/geometry

**Uses**: window_manager, mouse_handler, renderer, mode_controller

---

### `workflows/` - Application Workflows

**Purpose**: Orchestrate the application flow for different measurement modes.

**Key Components**:
- **manual_mode.py**:
  - User clicks three points
  - Display angle calculation in real-time
  - Handle clear/reset

- **auto_mode.py**:
  - Run detection pipeline on input
  - Display detected lines
  - Automatic angle calculation

- **hybrid_mode.py**:
  - Start with automatic detection
  - Allow user to refine lines
  - Edit line endpoints, add/remove lines
  - Final angle calculation

**Dependencies**: detection, ui, core/geometry

---

### `io/` - Input/Output Handling

**Purpose**: Manage all file and stream I/O operations.

**Key Components**:
- **image_loader.py**: Load images from disk (uses utils/image.py)
- **webcam_stream.py**: Manage webcam capture (uses utils/webcam.py)
- **video_stream.py**: Manage video file playback (uses utils/video.py)
- **file_saver.py**: Save annotated results and measurements

**Dependencies**: OpenCV, utils modules, file system

**Used By**: Main application, workflows

---

### `utils/` - Helper Utilities

**Purpose**: Provide general-purpose utilities used across modules.

**Key Components**:
- **geometry_helpers.py**:
  - Line-point distance
  - Line-line intersection
  - Point projection onto line
  - Parallel/perpendicular line detection

- **parameters.py**:
  - Configuration management
  - Parameter validation
  - Default values for detection/UI parameters

**Used By**: All modules

---

### `tests/` - Testing Infrastructure

**Purpose**: Comprehensive test coverage for all modules.

**Components**:
- **test_geometry.py**: Unit tests for geometry functions
- **test_detection.py**: Integration tests for detection pipeline
- **test_ui.py**: UI interaction and rendering tests
- **fixtures/**: Test images, synthetic data, reference outputs

---

## Data Flow

### Manual Mode Flow

```
User Input (Mouse Clicks)
    ↓
ui/mouse_handler.py (capture coordinates)
    ↓
ui/renderer.py (draw points and lines)
    ↓
core/geometry.py (calculate angle at every 3 points)
    ↓
ui/renderer.py (display angle text)
    ↓
io/file_saver.py (save on user request)
```

### Auto Mode Flow

```
Input Source (Image/Video/Webcam)
    ↓
io/ modules (load frame)
    ↓
detection/preprocessor.py (enhance image)
    ↓
detection/line_detector.py (detect lines)
    ↓
detection/postprocessor.py (merge/filter lines)
    ↓
core/geometry.py (calculate angles between lines)
    ↓
ui/renderer.py (display results)
    ↓
io/file_saver.py (save on user request)
```

### Hybrid Mode Flow

```
(Starts as Auto Mode)
    ↓
(Lines displayed to user)
    ↓
User Refines Lines (drag endpoints, add/remove)
    ↓
ui/mouse_handler.py (capture interactions)
    ↓
core/geometry.py (update angles)
    ↓
ui/renderer.py (update display)
    ↓
io/file_saver.py (save refined result)
```

## Module Dependencies

```
┌─────────────────────────────────────────┐
│           Main Application              │
│  (setup.py or main.py orchestrator)     │
└────────────────┬────────────────────────┘
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
    ┌────────┐ ┌──────┐ ┌─────────┐
    │   UI   │ │  IO  │ │Workflows│
    └────┬───┘ └──┬───┘ └────┬────┘
         │        │          │
         └────┬───┴──────┬───┘
              ↓          ↓
          ┌────────┐  ┌──────────┐
          │ CORE   │  │DETECTION │
          │(center)│  │          │
          └────────┘  └──────────┘
              ↑
              │
          ┌───────────┐
          │  UTILS    │
          └───────────┘
```

**Key Principles**:
- **CORE** is at the center - all geometric operations flow through it
- **DETECTION** is independent, can be upgraded/swapped
- **UI** uses CORE for calculations, independent of DETECTION in Manual mode
- **IO** is independent, pluggable input/output sources
- **UTILS** supports all layers
- **WORKFLOWS** orchestrate the combinations

## Technology Stack

- **Python**: 3.x
- **Computer Vision**: OpenCV (cv2)
- **Numerical Computing**: NumPy
- **Image Processing**: imutils
- **Testing**: pytest
- **Documentation**: Markdown

## Design Patterns

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Pass dependencies to functions rather than global imports
3. **Strategy Pattern**: Different detection/UI strategies (Manual/Auto/Hybrid)
4. **Factory Pattern**: Create Line, Measurement objects through constructors
5. **Observer Pattern**: UI updates on data changes (future event system)

## Performance Targets

- **Detection**: < 500ms per frame
- **UI Responsiveness**: < 50ms for interactive operations
- **Memory**: Efficient frame buffering, minimal copies
- **Real-time**: 30 FPS for webcam/video streams

## Future Enhancements

1. **Real-time Parameter Tuning**: Adjust detection parameters via trackbars
2. **CSV/JSON Export**: Save multiple measurements to structured formats
3. **Measurement History**: Track and display previous measurements
4. **Angle Statistics**: Calculate averages, standard deviations across measurements
5. **Multi-angle Detection**: Automatically find and measure multiple angles
6. **ROI Selection**: User-defined region of interest for detection
7. **GPU Acceleration**: CUDA support for OpenCV operations
8. **Configuration Files**: Load/save parameter presets

## Version History

- **v0.1** (Current): Monolithic setup.py with basic manual angle measurement
- **v1.0** (Target): Modular architecture with manual/auto/hybrid modes
- **v2.0** (Future): Advanced features and optimizations

---

**Last Updated**: 2026-02-10
**Maintained By**: Documentation Agent
