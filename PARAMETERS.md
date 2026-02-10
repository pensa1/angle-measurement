# Detection Parameter Tuning Guide

## Quick Start

For most wire bender images, start with these **default parameters**:

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| **Canny Low** | 50 | 10-100 | Threshold for weak edges |
| **Canny High** | 150 | 30-300 | Threshold for strong edges |
| **Hough Threshold** | 50 | 10-150 | Minimum votes for line detection |
| **Min Line Length** | 50 | 10-200 | Minimum pixels for valid line |
| **Max Line Gap** | 10 | 5-50 | Maximum gap to connect line segments |

```python
# Default configuration in code
DEFAULT_PARAMS = {
    'canny_low': 50,
    'canny_high': 150,
    'hough_threshold': 50,
    'hough_min_line_length': 50,
    'hough_max_line_gap': 10,
}
```

---

## Parameter Explanations

### Canny Edge Detection Parameters

#### Low Threshold (Default: 50)

**What it does**: Controls the detection of weak edges.

- **Lower values** (10-50): Detects more edges, including faint ones
  - Captures thin, subtle wire edges
  - More sensitive to noise
  - Better for low-contrast images

- **Higher values** (50-100): Detects only strong edges
  - Cleaner, fewer false edges
  - May miss subtle wire segments
  - Better for high-contrast images

**Visual example**:
```
Low = 20:  Many edges detected (fragmented, noisy)
    ●─●─●─●   <- Multiple segments
    │ │ │ │

Low = 50:  Balanced edge detection
    ●───●     <- Fewer, cleaner segments
    │       │

Low = 80:  Only very strong edges
    ●       ← Strong edges only
```

**When to adjust**:
- **Lower (20-40)**: If edges are fragmented, disconnected, or missing
- **Keep default (50)**: Good balance for most lighting conditions
- **Raise (60-80)**: If too much noise or false edges in background

#### High Threshold (Default: 150)

**What it does**: Controls the detection of strong/definite edges.

- **Lower values** (50-100): More aggressive edge inclusion
  - Connects more weak edges to strong ones (hysteresis)
  - Fills gaps in line segments
  - More prone to noise

- **Higher values** (150-300): More conservative edge inclusion
  - Only connects to very strong edges
  - Cleaner, more distinct lines
  - May fragment lines

**Recommended ratio**: `high = 2.5 × low`

```
If low = 50:
  - Typical high = 50 × 2.5 = 125-150
  - Avoid high = 200 (breaks ratio)

If low = 30:
  - Typical high = 30 × 2.5 = 75-90

If low = 80:
  - Typical high = 80 × 2.5 = 200-250
```

**When to adjust**:
- **Raise both thresholds**: Too many false edges, too much noise
- **Lower both thresholds**: Missing real edges, lines look disconnected
- **Adjust ratio**: Lines appear fragmented or over-connected

#### Tuning Strategy

1. **Start with defaults**: Canny Low=50, High=150
2. **Test on image**: View edge detection output
3. **If edges look fragmented**:
   - Lower low threshold to 40-50
   - Lower high threshold by same ratio
4. **If too much noise**:
   - Raise both thresholds
   - Maintain 2.5× ratio
5. **If edges disappear**:
   - Lower thresholds
   - Check lighting/contrast

---

### Hough Transform Parameters

The Hough Transform detects lines in the edge image. It votes on lines in "Hough space" and accepts lines that exceed a vote threshold.

#### Hough Threshold (Default: 50)

**What it does**: Minimum number of edge pixels that must vote for a line to be detected.

- **Lower values** (10-30): More lines detected
  - Catches shorter, fainter lines
  - More noise/false positives
  - Fragmented detection

- **Higher values** (50-150): Fewer, stronger lines detected
  - Only robust, well-defined lines
  - Cleaner results
  - May miss real lines

**Visual example**:
```
Threshold = 20 (low):
  ●─●─●  ●─●  ●  ← Many small segments detected
  ●    ●  ●    ●   (some are noise)

Threshold = 50 (default):
  ●─────●  ●─●─● ← Major lines detected
                  (noise filtered out)

Threshold = 100 (high):
  ●─────●  ← Only strongest lines
            (may miss subtle wires)
```

**When to adjust**:
- **Lower (20-40)**: Missing some wires, too few lines
- **Keep default (50)**: Good for typical images
- **Raise (70-100)**: Too much fragmentation or noise

#### Min Line Length (Default: 50)

**What it does**: Minimum pixel length for a line segment to be accepted.

- **Lower values** (10-30): Detects shorter line segments
  - Finds incomplete or bent wires
  - More fragments to merge later
  - Slower performance

- **Higher values** (50-200): Only detects longer, substantial lines
  - Fewer short fragments
  - Faster processing
  - May miss short wire sections

**Impact on detection**:
```
Min Length = 20:
  Small wire sections detected
  ●─●  ●─●  ●─●  ●─●
    ↑    ↑    ↑    ↑
  All short segments included

Min Length = 50:
  Only longer segments
  ●────●      ●────●
    ↑           ↑
  Shorter sections filtered

Min Length = 100:
  Only long continuous lines
  ●────────────●  ●────────●
        ↑                ↑
  Very long requirement
```

**When to adjust**:
- **Lower (20-40)**: Wire has many short bends, need detail
- **Keep default (50)**: Balanced for typical wire bender images
- **Raise (80-100)**: Only want major linear sections

#### Max Line Gap (Default: 10)

**What it does**: Maximum pixel gap to connect two line segments into one line.

- **Smaller values** (5-10): Strict connection
  - Lines must be nearly touching to merge
  - More fragmented results
  - Requires perfect alignment

- **Larger values** (15-50): Lenient connection
  - Fills small gaps in edges
  - Connects broken wires
  - May over-connect unrelated lines

**Visual example**:
```
Gap = 5 pixels (strict):
  ●──●  ●──●
      ↑
    gap=8px → SEPARATE lines

Gap = 10 pixels (default):
  ●──●  ●──● → ●─────●
      ↑          (connected)
    gap=8px

Gap = 30 pixels (lenient):
  ●──●      ●──● → ●───────────●
           ↑
         gap=25px → CONNECTED
```

**When to adjust**:
- **Lower (5-10)**: Wires are well-lit, clearly separated
- **Keep default (10)**: Good for typical images
- **Raise (15-25)**: Shadows create gaps in edges

---

## Troubleshooting Guide

### Problem: No Lines Detected (Empty Result)

**Causes & Solutions**:

1. **Canny thresholds too high**
   - Solution: Lower both thresholds
   - Try: Canny Low=30, High=90

2. **Hough threshold too high**
   - Solution: Lower hough threshold
   - Try: Hough Threshold=20-30

3. **Image too dark or low contrast**
   - Solution: Lower thresholds, may need better lighting
   - Try: Canny Low=20, High=70

4. **Min line length too high**
   - Solution: Reduce minimum line length
   - Try: Min Line Length=30

**Debug steps**:
```python
# Check what the preprocessor produces
from detection.preprocessor import ImagePreprocessor
preprocessor = ImagePreprocessor()
gray = preprocessor.preprocess(image)

# Check histogram
import cv2
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
# If histogram clustered at extremes (all black or white), adjust preprocessing
```

---

### Problem: Too Many False/Noise Lines

**Causes & Solutions**:

1. **Canny thresholds too low**
   - Solution: Raise both thresholds
   - Try: Canny Low=70, High=180

2. **Hough threshold too low**
   - Solution: Raise hough threshold
   - Try: Hough Threshold=80-100

3. **Background texture creating noise**
   - Solution: Increase blur, raise thresholds
   - Try: Blur kernel=7x7, Canny Low=60

4. **Min line length too low**
   - Solution: Raise minimum line length
   - Try: Min Line Length=100

**Verification**:
```python
# Count detected lines
num_lines = len(detected_lines)
if num_lines > 10:  # Suspiciously high
    raise_thresholds()
```

---

### Problem: Lines Are Fragmented (Broken into Pieces)

**Causes & Solutions**:

1. **Canny low threshold too high**
   - Solution: Lower low threshold
   - Try: Canny Low=30-40

2. **Max line gap too small**
   - Solution: Increase gap tolerance
   - Try: Max Line Gap=15-20

3. **High threshold not proportional to low**
   - Solution: Ensure high ≈ 2.5× low
   - Try: Low=40, High=100

4. **Hough threshold too high (requires too many votes)**
   - Solution: Lower hough threshold
   - Try: Hough Threshold=30-40

**Fix fragmentation**:
```python
# In postprocessor
merge_distance_threshold = 20  # pixels
angle_threshold = 5  # degrees
# Merge lines closer than these thresholds
```

---

### Problem: Over-Merged Lines (Adjacent Lines Combined)

**Causes & Solutions**:

1. **Max line gap too large**
   - Solution: Reduce gap tolerance
   - Try: Max Line Gap=5-8

2. **Postprocessor merging threshold too loose**
   - Solution: Tighten line merging parameters
   - Try: Merge distance=15px, angle threshold=3°

3. **Hough threshold too low (accepting weak lines)**
   - Solution: Raise hough threshold
   - Try: Hough Threshold=60-80

---

## Preset Configurations

Use these as starting points for different imaging scenarios:

### Bright Lighting (Well-lit workshop)

```python
PRESET_BRIGHT = {
    'canny_low': 70,
    'canny_high': 200,
    'hough_threshold': 60,
    'hough_min_line_length': 60,
    'hough_max_line_gap': 8,
}
```

**Rationale**: More aggressive thresholds due to high contrast.

### Low Lighting (Dim workshop)

```python
PRESET_DIM = {
    'canny_low': 30,
    'canny_high': 90,
    'hough_threshold': 30,
    'hough_min_line_length': 40,
    'hough_max_line_gap': 15,
}
```

**Rationale**: Lower thresholds catch fainter edges, higher gap tolerance for shadows.

### High Contrast (Strong shadows, reflections)

```python
PRESET_HIGH_CONTRAST = {
    'canny_low': 60,
    'canny_high': 180,
    'hough_threshold': 70,
    'hough_min_line_length': 50,
    'hough_max_line_gap': 5,
}
```

**Rationale**: Strong thresholds avoid shadow noise, tight gap for precision.

### Noisy Background (Textured surface)

```python
PRESET_NOISY = {
    'canny_low': 80,
    'canny_high': 220,
    'hough_threshold': 80,
    'hough_min_line_length': 100,
    'hough_max_line_gap': 5,
}
```

**Rationale**: Very conservative detection to filter texture noise.

### Fine Details (Thin wires, small bends)

```python
PRESET_FINE_DETAIL = {
    'canny_low': 40,
    'canny_high': 120,
    'hough_threshold': 30,
    'hough_min_line_length': 20,
    'hough_max_line_gap': 15,
}
```

**Rationale**: Lower thresholds catch thin wires, high gap tolerance for small curves.

---

## Advanced Tuning

### Adaptive Parameter Selection

For automated parameter adjustment based on image characteristics:

```python
from detection.preprocessor import ImagePreprocessor

stats = ImagePreprocessor.analyze_image_stats(image)
noise = ImagePreprocessor.estimate_noise_level(image)

if stats['contrast_ratio'] < 0.3:
    # Low contrast image
    use_preset('DIM')
elif noise > 15:
    # High noise
    use_preset('NOISY')
elif stats['std'] > 80:
    # High variation (good contrast)
    use_preset('HIGH_CONTRAST')
else:
    # Default
    use_preset('DEFAULT')
```

### Parameter Ranges

Safe ranges for tuning without breaking the algorithm:

| Parameter | Min | Default | Max | Step |
|-----------|-----|---------|-----|------|
| Canny Low | 10 | 50 | 100 | 5 |
| Canny High | 30 | 150 | 300 | 10 |
| Hough Threshold | 10 | 50 | 150 | 5 |
| Min Line Length | 10 | 50 | 200 | 10 |
| Max Line Gap | 5 | 10 | 50 | 5 |

### GPU Acceleration (Future)

For processing video at high FPS:

```python
# When available
USE_GPU = True
if USE_GPU:
    # CUDA-accelerated Canny + Hough
    detected_lines = cuda_hough_lines_p(edges, ...)
else:
    detected_lines = cv2.HoughLinesP(edges, ...)
```

---

## UI Parameter Tuning Interface

When the UI module is ready, parameters will be adjustable via trackbars:

**Keyboard Shortcuts**:
- **'a'** - Toggle Auto Detect mode
- **'t'** - Toggle edge visualization (show Canny edges)
- **'d'** - Toggle detection overlay (show detected lines)
- **'r'** - Reset all parameters to defaults
- **'s'** - Save current parameters as preset
- **'l'** - Load saved preset
- **'q' or ESC** - Quit application

**Trackbar Controls**:
- Canny Low Threshold (trackbar)
- Canny High Threshold (trackbar)
- Hough Threshold (trackbar)
- Min Line Length (trackbar)
- Max Line Gap (trackbar)
- Apply Morphology (toggle)
- Use CLAHE (toggle)

**Real-time Feedback**:
- Display detected line count
- Show detected angles
- Visual overlay of detected lines
- Edge map preview

---

## Best Practices

1. **Start Conservative**: Begin with higher thresholds, lower gradually
2. **Adjust One at a Time**: Change one parameter, observe effect
3. **Test on Multiple Images**: Ensure parameters generalize
4. **Use Presets First**: Try presets before manual tuning
5. **Monitor Line Count**: Too many lines (>10) usually means too-low thresholds
6. **Preserve Ratio**: Keep Canny high ≈ 2.5× low
7. **Save Good Presets**: Document working parameter sets

---

## Parameter Export/Import

Save and load parameter configurations:

```python
import json

# Save
params = {
    'name': 'My Custom Preset',
    'canny_low': 50,
    'canny_high': 150,
    'hough_threshold': 50,
    'hough_min_line_length': 50,
    'hough_max_line_gap': 10,
}
with open('presets/my_preset.json', 'w') as f:
    json.dump(params, f)

# Load
with open('presets/my_preset.json', 'r') as f:
    params = json.load(f)
    apply_parameters(params)
```

---

## References

- **Canny Edge Detection**: Canny, J. (1986). "A Computational Approach to Edge Detection"
- **Hough Transform**: Hough, P. V. (1962). "Method and Means for Recognizing Complex Patterns"
- **OpenCV Docs**: https://docs.opencv.org/master/
- **Image Processing Guide**: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/

---

**Last Updated**: 2026-02-10
**Maintained By**: Documentation Agent
**Current Version**: Phase 2 (Line Detection)
