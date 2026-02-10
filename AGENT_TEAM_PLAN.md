# Agent Team Structure for Angle Measurement Project

## Team Overview
This document defines the specialized agent team for developing the automatic angle measurement tool with OpenCV line detection.

## Project Goal
Build a tool to automatically detect lines in wire bender images, measure angles between them, with user refinement capabilities.

---

## 🤖 Agent Team Members

### 1. Detection Specialist Agent
**Role**: Computer Vision & Line Detection Expert

**Responsibilities**:
- Implement Canny edge detection pipeline
- Implement Hough Transform for line detection
- Develop line merging and filtering algorithms
- Optimize detection parameters
- Handle edge cases (poor lighting, noise, etc.)

**Key Deliverables**:
- `detection/preprocessor.py` - Image preprocessing pipeline
- `detection/line_detector.py` - Core line detection with Canny + Hough
- `detection/postprocessor.py` - Line merging and filtering
- Parameter tuning algorithms

**Initial Tasks** (Phase 1-2):
1. Research optimal Canny and Hough parameters for wire bender images
2. Implement basic line detection pipeline
3. Create line merging algorithm for fragmented detections
4. Add parameter auto-tuning based on image characteristics

**Dependencies**:
- Needs Core Algorithms Agent for geometry utilities
- Provides detected lines to UI Agent for rendering

---

### 2. UI/UX Agent
**Role**: User Interface & Interaction Designer

**Responsibilities**:
- Design and implement user interaction modes (Manual/Auto/Hybrid)
- Create intuitive line editing interface
- Implement mouse callbacks and keyboard shortcuts
- Design visual feedback and annotations
- Manage window layouts and trackbars

**Key Deliverables**:
- `ui/window_manager.py` - OpenCV window and trackbar management
- `ui/mouse_handler.py` - Interactive line editing (click, drag, delete)
- `ui/renderer.py` - Drawing lines, angles, annotations
- `ui/mode_controller.py` - Mode switching logic

**Initial Tasks** (Phase 1, 3):
1. Refactor existing mouse callback system from setup.py
2. Design mode switching interface (Manual/Auto/Hybrid)
3. Implement click-and-drag line endpoint editing
4. Add visual feedback for selected/hovered lines
5. Create parameter tuning trackbars for detection settings

**Dependencies**:
- Uses Core Algorithms Agent for angle calculations
- Uses Detection Agent's line detection results
- Coordinates with Testing Agent for UI testing

---

### 3. Core Algorithms Agent
**Role**: Geometry & Mathematics Expert

**Responsibilities**:
- Extract and enhance geometry calculations
- Implement robust angle measurement algorithms
- Provide utility functions (distance, intersection, etc.)
- Create data structures for measurements
- Ensure numerical stability and edge case handling

**Key Deliverables**:
- `core/geometry.py` - Angle calculations, vector math, Line class
- `core/measurements.py` - Data structures for storing measurements
- `utils/geometry_helpers.py` - Intersection, distance, projection utilities

**Initial Tasks** (Phase 1):
1. Extract angle calculation from setup.py (lines 39-56)
2. Create Line class with methods (length, angle, intersection, distance)
3. Implement robust angle-between-lines calculation
4. Add line intersection and parallel line detection
5. Write comprehensive unit tests for all geometry functions

**Dependencies**:
- Foundation for all other agents
- Provides geometry utilities to Detection and UI agents
- Works closely with Testing Agent for validation

---

### 4. Documentation Agent
**Role**: Technical Writer & Documentation Specialist

**Responsibilities**:
- Document code with docstrings and comments
- Create and maintain technical documentation
- Write user guides and tutorials
- Explain algorithms and parameters
- Keep documentation in sync with code changes

**Key Deliverables**:
- Docstrings for all modules, classes, and functions
- `ARCHITECTURE.md` - System design and module relationships
- `ALGORITHMS.md` - Explanation of Canny, Hough, line merging
- `PARAMETERS.md` - Guide to tuning detection parameters
- Updated `README.md` with usage instructions

**Initial Tasks** (Throughout all phases):
1. Add docstrings to existing code in setup.py
2. Create ARCHITECTURE.md documenting module structure
3. Document detection pipeline in ALGORITHMS.md
4. Create parameter tuning guide (PARAMETERS.md)
5. Update README.md with usage examples and screenshots

**Dependencies**:
- Reviews code from all agents
- Coordinates with all agents to understand implementation
- Works independently but reviews all deliverables

---

### 5. Testing & Integration Agent
**Role**: Quality Assurance & Integration Specialist

**Responsibilities**:
- Design and implement test suite
- Create test fixtures (synthetic images, test cases)
- Perform integration testing
- Set up CI/CD if needed
- Validate detection quality
- Performance testing and optimization

**Key Deliverables**:
- `tests/test_geometry.py` - Unit tests for geometry calculations
- `tests/test_detection.py` - Line detection algorithm tests
- `tests/test_ui.py` - UI interaction tests
- `tests/fixtures/` - Test images and synthetic data
- Test coverage reports

**Initial Tasks** (Phase 1, ongoing):
1. Set up pytest infrastructure
2. Create synthetic test images (lines at known angles)
3. Write unit tests for geometry module
4. Create integration tests for detection pipeline
5. Establish test coverage requirements (target: 80%+)

**Dependencies**:
- Tests all other agents' deliverables
- Coordinates with all agents for test requirements
- Provides test fixtures for Detection Agent

---

### 6. DevOps & Release Agent
**Role**: CI/CD & Release Management Specialist

**Responsibilities**:
- Set up GitHub Actions for automated testing
- Configure continuous integration pipeline
- Manage release process and versioning
- Create and manage pull requests
- Generate changelogs and release notes
- Set up code quality checks (linting, formatting)

**Key Deliverables**:
- `.github/workflows/ci.yml` - GitHub Actions CI pipeline
- `.github/workflows/release.yml` - Release automation
- Version management and semantic versioning
- Automated changelog generation
- PR templates and issue templates

**Initial Tasks** (Phase 2):
1. Set up GitHub Actions workflow for pytest
2. Configure automated test execution on push/PR
3. Add test coverage reporting (Codecov integration)
4. Set up linting (flake8, black, mypy)
5. Create PR and issue templates

**Later Tasks** (Phase 4):
1. Create v1.0 release with proper versioning
2. Generate changelog from commit history
3. Create final PR to main branch
4. Tag release with semantic versioning
5. Set up automated release notes

**Dependencies**:
- Works with Testing Agent for CI/CD pipeline
- Coordinates with Documentation Agent for release notes
- Supports all agents with automated quality checks

---

## 📋 Work Distribution by Phase

### Phase 1: Foundation Refactoring (Week 1)

**Core Algorithms Agent** (Lead):
- Extract geometry from setup.py → core/geometry.py
- Create Line class and utility functions
- Write comprehensive unit tests

**Testing Agent**:
- Set up test infrastructure (pytest, fixtures)
- Create test cases for geometry functions
- Establish coverage requirements

**UI Agent**:
- Refactor mouse handling from setup.py
- Create window_manager.py skeleton
- Plan mode switching architecture

**Documentation Agent**:
- Add docstrings to existing setup.py code
- Create initial ARCHITECTURE.md
- Document project structure

**Detection Agent**:
- Research Canny/Hough parameters
- Experiment with sample images
- Plan detection pipeline architecture

**Deliverables**: Clean modular foundation, geometry module tested, architecture documented

---

### Phase 2: Automatic Line Detection (Weeks 2-3)

**Detection Agent** (Lead):
- Implement preprocessing pipeline (preprocessor.py)
- Implement line detection (line_detector.py)
- Create line merging algorithm (postprocessor.py)
- Add parameter auto-tuning

**UI Agent**:
- Create parameter tuning trackbars
- Implement real-time detection preview
- Add visual feedback for detected lines

**Testing Agent**:
- Create detection quality tests
- Test with various lighting conditions
- Performance testing (target: <500ms)
- Create visual regression tests

**Core Algorithms Agent**:
- Support Detection Agent with geometry utilities
- Optimize angle calculation performance
- Add line filtering utilities

**Documentation Agent**:
- Document detection pipeline in ALGORITHMS.md
- Create PARAMETERS.md tuning guide
- Add detection examples to README.md

**DevOps Agent**:
- Set up GitHub Actions CI/CD pipeline
- Configure automated pytest execution
- Add test coverage reporting (Codecov)
- Set up linting and code quality checks
- Create PR and issue templates

**Deliverables**: Working auto-detection, parameter tuning UI, comprehensive tests, CI/CD pipeline

---

### Phase 3: User Interaction & Refinement (Week 4)

**UI Agent** (Lead):
- Implement Hybrid mode
- Create interactive line editing (drag endpoints)
- Add line selection/deletion
- Implement smart snapping to edges

**Detection Agent**:
- Optimize detection for interactive use
- Add ROI (Region of Interest) support
- Fine-tune performance

**Core Algorithms Agent**:
- Add snapping algorithms (snap to edge, intersection)
- Improve line intersection detection
- Add line validation utilities

**Testing Agent**:
- Test user interaction scenarios
- Validate line editing accuracy
- Test mode switching

**Documentation Agent**:
- Create user guide for Hybrid mode
- Document keyboard shortcuts
- Add usage examples with screenshots

**Deliverables**: Hybrid mode working, intuitive line editing, user documentation

---

### Phase 4: Polish & CSV Export (Week 5) - Optional

**All Agents**:
- Bug fixes and refinements
- Performance optimization
- CSV export implementation (if requested)
- Final documentation updates
- Comprehensive testing

**Deliverables**: Production-ready tool, complete documentation, test suite

---

## 🔄 Coordination Strategy

### Daily Sync Points
- **Morning**: Review previous day's progress, identify blockers
- **Evening**: Commit code, update documentation, prepare next day's tasks

### Communication Channels
- **Code Reviews**: All agents review each other's PRs before merge
- **Shared Context**: All agents have access to AGENT_TEAM_PLAN.md
- **Interface Contracts**: Clear API boundaries defined in ARCHITECTURE.md

### Dependency Management
1. **Phase 1**: Core Algorithms Agent completes geometry module first (foundation)
2. **Phase 2**: Detection Agent uses Core's geometry utilities
3. **Phase 3**: UI Agent integrates Detection and Core modules
4. **Throughout**: Testing Agent validates all deliverables
5. **Throughout**: Documentation Agent documents all changes

### Conflict Resolution
- **Orchestrator** (Project Lead) makes final decisions on:
  - Architecture changes
  - Priority shifts
  - Resource allocation
  - Timeline adjustments

---

## 🎯 Success Metrics

### Technical Metrics
- **Detection Quality**: >90% line detection rate on test images
- **False Positive Rate**: <20%
- **Performance**: <500ms per frame
- **Test Coverage**: >80%

### User Experience Metrics
- **Mode Switching**: <200ms transition time
- **Drag Interaction**: <50ms latency
- **Parameter Tuning**: Real-time preview

### Code Quality Metrics
- **Modularity**: Low coupling between modules
- **Documentation**: All public APIs documented
- **Tests**: All critical paths covered

---

## 🚀 Getting Started

### For Each Agent
1. Read this AGENT_TEAM_PLAN.md
2. Review ARCHITECTURE.md (to be created)
3. Read existing setup.py to understand current implementation
4. Check assigned Phase 1 tasks
5. Coordinate with dependent agents
6. Begin implementation

### Initial Coordination Meeting
- All agents review project goals
- Clarify module boundaries
- Establish coding standards
- Set up git branch strategy
- Define PR review process

---

## 📞 Agent Contact Points

**For Geometry Questions**: Core Algorithms Agent
**For Detection Issues**: Detection Specialist Agent
**For UI/UX Decisions**: UI/UX Agent
**For Documentation**: Documentation Agent
**For Testing Strategies**: Testing & Integration Agent
**For Overall Direction**: Project Lead (Orchestrator)

---

**Last Updated**: 2026-02-10
**Project Status**: Team Setup Phase
**Next Milestone**: Complete Phase 1 Foundation
