# Detection Parameter Tuning Guide

## Complete Parameter Overview

The detection pipeline has three stages, each with adjustable parameters:

### Stage 1: Preprocessing Parameters

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| **blur_kernel_size** | (5, 5) | (3,3)-(9,9) | Gaussian blur kernel (must be odd) |
| **blur_sigma** | 0 | 0-2.0 | Gaussian blur sigma (0=auto) |
| **use_clahe** | True | - | Enable contrast enhancement |
| **clahe_clip_limit** | 2.0 | 1.0-4.0 | CLAHE contrast amplification |
| **clahe_tile_grid_size** | (8, 8) | (4,4)-(16,16) | CLAHE tile grid size |
| **use_morphology** | False | - | Enable morphological operations |
| **morph_operation** | "close" | dilate/erode/open/close | Morphology type |
| **morph_kernel_size** | (3, 3) | (3,3)-(7,7) | Morphology kernel size |
| **morph_iterations** | 1 | 1-3 | Morphology repetitions |

### Stage 2: Edge Detection (Canny) Parameters

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| **canny_low_threshold** | 50 | 10-100 | Threshold for weak edges |
| **canny_high_threshold** | 150 | 30-300 | Threshold for strong edges |
| **canny_aperture_size** | 3 | 3, 5, 7 | Sobel kernel aperture size |
| **canny_l2_gradient** | False | - | Use L2 norm instead of L1 |

### Stage 3: Line Detection (Hough) Parameters

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| **hough_rho** | 1.0 | 0.5-2.0 | Accumulator distance resolution (pixels) |
| **hough_theta** | π/180 | π/180-π/36 | Accumulator angle resolution (radians) |
| **hough_threshold** | 50 | 10-150 | Minimum votes for line detection |
| **min_line_length** | 50 | 10-200 | Minimum pixels for valid line |
| **max_line_gap** | 10 | 5-50 | Maximum gap to connect line segments |

### Stage 4: Post-Processing Parameters

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| **min_line_length** | 30 | 10-100 | Minimum line length after merging |
| **angle_tolerance** | 10 | 1-20 | Angular difference for grouping (degrees) |
| **distance_tolerance** | 15 | 5-30 | Perpendicular distance for merging (pixels) |
| **overlap_ratio** | 0.0 | 0.0-1.0 | Minimum overlap for merging (0=collinear) |
| **duplicate_distance** | 10 | 5-20 | Endpoint distance for deduplication (pixels) |

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

### Preprocessing Parameters

#### Gaussian Blur

**blur_kernel_size** (Default: (5, 5))

- Must be odd integers (3, 5, 7, 9, 11, ...)
- Larger kernel = more blur = slower edges but cleaner
- Smaller kernel = less blur = preserves detail

**Recommendations**:
- Clean images: (3, 3) or (5, 5)
- Noisy images: (7, 7) or (9, 9)
- Very noisy: (9, 9) or (11, 11)

**blur_sigma** (Default: 0)

- Controls blur intensity
- 0 = let OpenCV calculate automatically
- Higher values = stronger blur effect
- Rarely needs adjustment with default kernel size

#### CLAHE Parameters

**use_clahe** (Default: True)

Enable/disable contrast enhancement. Recommended to keep enabled for:
- Low contrast images
- Uneven lighting (shadows)
- Underexposed photos

Disable if:
- Already high contrast
- Noisy background (CLAHE amplifies noise)
- Processing speed is critical

**clahe_clip_limit** (Default: 2.0)

Controls contrast amplification. Higher = more contrast.

```
Low contrast image:
  Before: ░░░░░░░░░░░░░░░░  (flat)
  Low (1.0): ░░░▓▓▓░░░░      (slight enhancement)
  Mid (2.0): ░░▓▓▓░░░░░░     (balanced)
  High (4.0): ░▓█▓░░░░░░░    (aggressive)
```

**When to adjust**:
- Lower (1.0-1.5): Avoid over-enhancement, subtle changes
- Keep default (2.0): Good balance
- Raise (3.0-4.0): Very low contrast input

**clahe_tile_grid_size** (Default: (8, 8))

Number of tiles for local contrast enhancement.

```
More tiles (16×16): Finer local contrast, higher computation
Default (8×8): Balanced
Fewer tiles (4×4): Coarser contrast, faster
```

**When to adjust**:
- Smaller grids (4×4): Fast processing, coarse contrast
- Keep default (8×8): Good balance
- Larger grids (16×16): Very fine local contrast detail

#### Morphological Operations

**use_morphology** (Default: False)

Enable/disable morphological operations (dilation/erosion).

Enable if:
- Edges have small gaps (shadows, lighting artifacts)
- Need to fill holes in edges
- Merging post-processor leaves gaps

Disable if:
- Already good edge connectivity
- Want to preserve all fine details

**morph_operation** (Default: "close")

Available operations:
- **"dilate"**: Expand white regions (thicken edges)
- **"erode"**: Shrink white regions (thin edges, remove noise)
- **"open"**: Erode then dilate (remove small noise)
- **"close"**: Dilate then erode (fill small holes) ← usually best

**morph_kernel_size** (Default: (3, 3))

Size of the morphology kernel.

```
Smaller (3×3): Subtle effect, preserves detail
Default (3×3): Typical choice
Larger (5×5, 7×7): Stronger effect, removes more
```

**morph_iterations** (Default: 1)

Number of times to apply the operation.

```
1 iteration: Mild effect
2-3 iterations: Strong effect
>3: Risk of over-processing
```

#### Preprocessing Presets

**For clean, high-contrast images**:
```python
config = PreprocessorConfig(
    use_clahe=False,              # skip enhancement
    blur_kernel_size=(5, 5),
    use_morphology=False,
)
```

**For low-contrast images** (shadows, underexposed):
```python
config = PreprocessorConfig(
    use_clahe=True,
    clahe_clip_limit=3.0,         # more aggressive
    clahe_tile_grid_size=(8, 8),
    blur_kernel_size=(5, 5),
    use_morphology=False,
)
```

**For noisy background** (texture):
```python
config = PreprocessorConfig(
    use_clahe=True,
    blur_kernel_size=(7, 7),      # more blur
    use_morphology=True,
    morph_operation="open",       # remove noise
    morph_iterations=1,
)
```

**For fragmented edges** (broken lines):
```python
config = PreprocessorConfig(
    use_clahe=True,
    use_morphology=True,
    morph_operation="close",      # fill gaps
    morph_kernel_size=(5, 5),
    morph_iterations=1,
)
```

---

## Canny Edge Detection Parameters

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

## Post-Processing Parameters

### Line Filtering and Merging

#### min_line_length (Default: 30)

Minimum line length after post-processing (filters short noise).

```
Low (10-20px): Keep fine details, all wire segments
Default (30px): Good balance, removes noise
High (50-100px): Only substantial lines
```

**When to adjust**:
- Lower: Detect thin wires, small wire segments
- Higher: Cleaner output, remove short noise

#### angle_tolerance (Default: 10.0 degrees)

Maximum angular difference for lines to be grouped as same orientation.

```
Tight (3-5°): Strict grouping, preserve fine direction changes
Default (10°): Good for typical wires
Loose (15-20°): Merge more aggressively, ignore small bends
```

**Effect**:
```
Tight (5°):
  ●───●  ●───●  ●───●  (lines grouped: 45°, 50°, 55° separately)

Default (10°):
  ●───────●  ●───●  (lines grouped: 45°/50°/55° together, 92° separate)

Loose (20°):
  ●──────────────●  (too aggressive, unrelated lines merge)
```

**When to adjust**:
- Lower: Preserve fine wire bends, complex geometry
- Higher: Merge fragmented wires, clean output

#### distance_tolerance (Default: 15.0 pixels)

Maximum perpendicular distance between lines for merging.

```
Tight (5-10px): Only merge if almost touching
Default (15px): Good for typical wire spacing
Loose (20-30px): Merge from further apart
```

**Visual**:
```
Tight (5px):
  ●──●  ●──●     (gap=8px, distance_tol=5 → NO merge)
       gap

Default (15px):
  ●──●  ●──●     (gap=8px, distance_tol=15 → MERGE)
       gap

Loose (25px):
  ●──●        ●──●  (gap=20px, distance_tol=25 → MERGE)
       gap
```

**When to adjust**:
- Lower: Wires are well-separated, avoid false merges
- Higher: Wires have gaps from shadows, need to merge

#### overlap_ratio (Default: 0.0)

Minimum overlap along shared direction for two segments to merge.

```
0.0: Merge if collinear (any overlap)
0.3: Require 30% overlap
0.5: Require 50% overlap
1.0: Require complete containment
```

**Visual**:
```
Two lines:
  Line 1: ●────────●    (20px long)
  Line 2:      ●────●   (15px long, starts 40% along Line 1)

Overlap ratio = 60% (12px / 20px min)

overlap_ratio=0.0: MERGE (collinear)
overlap_ratio=0.3: MERGE (60% > 30%)
overlap_ratio=0.5: MERGE (60% > 50%)
overlap_ratio=0.7: NO MERGE (60% < 70%)
```

**Recommendations**:
- Keep 0.0 (default): Most robust for wire detection
- Use 0.3+ only if too many lines merge

#### duplicate_distance (Default: 10.0 pixels)

Maximum endpoint distance for lines to be considered duplicates.

```
Tight (5px): Very strict, only exact duplicates
Default (10px): Typical Hough overlap tolerance
Loose (15-20px): Remove more duplicates
```

**When to adjust**:
- Lower: If Hough creates slightly offset duplicates
- Higher: Aggressive deduplication

### Post-Processing Presets

**Conservative** (preserve details):
```python
config = PostprocessorConfig(
    min_line_length=20.0,
    angle_tolerance=5.0,         # strict grouping
    distance_tolerance=10.0,     # tight merging
    overlap_ratio=0.3,           # require overlap
    duplicate_distance=8.0,
)
```

**Balanced** (default):
```python
config = PostprocessorConfig(
    min_line_length=30.0,
    angle_tolerance=10.0,
    distance_tolerance=15.0,
    overlap_ratio=0.0,           # merge if collinear
    duplicate_distance=10.0,
)
```

**Aggressive** (cleanup):
```python
config = PostprocessorConfig(
    min_line_length=50.0,
    angle_tolerance=15.0,
    distance_tolerance=25.0,
    overlap_ratio=0.0,
    duplicate_distance=15.0,
)
```

**For complex geometry** (many wire bends):
```python
config = PostprocessorConfig(
    min_line_length=20.0,
    angle_tolerance=3.0,         # very strict, preserve angles
    distance_tolerance=12.0,
    overlap_ratio=0.2,
    duplicate_distance=8.0,
)
```

**For simple geometry** (few straight sections):
```python
config = PostprocessorConfig(
    min_line_length=40.0,
    angle_tolerance=15.0,        # aggressive grouping
    distance_tolerance=20.0,
    overlap_ratio=0.0,
    duplicate_distance=12.0,
)
```

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
