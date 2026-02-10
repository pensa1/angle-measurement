"""
Synthetic test image generation for angle measurement testing.

This module creates test images with lines at known angles, intersections,
and various geometric configurations for validation purposes.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, List


def create_blank_image(width: int = 400, height: int = 400,
                       background_color: Tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    """Create a blank image with specified dimensions and background color.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        background_color: BGR color tuple for background

    Returns:
        Blank image as numpy array
    """
    return np.full((height, width, 3), background_color, dtype=np.uint8)


def draw_line_by_angle(image: np.ndarray, center: Tuple[int, int],
                       angle_degrees: float, length: int = 150,
                       color: Tuple[int, int, int] = (0, 0, 0),
                       thickness: int = 2) -> np.ndarray:
    """Draw a line from a center point at a specified angle.

    Args:
        image: Image to draw on
        center: Center point (x, y) of the line
        angle_degrees: Angle in degrees (0° = horizontal right, 90° = vertical up)
        length: Line length in pixels
        color: BGR color tuple
        thickness: Line thickness in pixels

    Returns:
        Image with line drawn
    """
    angle_radians = np.radians(angle_degrees)
    cx, cy = center

    # Calculate endpoints
    half_length = length // 2
    x1 = int(cx - half_length * np.cos(angle_radians))
    y1 = int(cy - half_length * np.sin(angle_radians))
    x2 = int(cx + half_length * np.cos(angle_radians))
    y2 = int(cy + half_length * np.sin(angle_radians))

    cv2.line(image, (x1, y1), (x2, y2), color, thickness)
    return image


def create_single_angle_image(angle: float, filename: str = None) -> np.ndarray:
    """Create an image with two lines forming a specific angle.

    Args:
        angle: Angle between lines in degrees
        filename: Optional filename to save the image

    Returns:
        Image with two lines forming the specified angle
    """
    img = create_blank_image()
    center = (200, 200)

    # Draw first line horizontally (0 degrees)
    draw_line_by_angle(img, center, 0, length=180, color=(0, 0, 0), thickness=3)

    # Draw second line at specified angle
    draw_line_by_angle(img, center, angle, length=180, color=(0, 0, 0), thickness=3)

    # Add text annotation
    cv2.putText(img, f"{angle} degrees", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def create_intersecting_lines_image(angles: List[float], filename: str = None) -> np.ndarray:
    """Create an image with multiple lines intersecting at a center point.

    Args:
        angles: List of angles in degrees for each line
        filename: Optional filename to save the image

    Returns:
        Image with intersecting lines
    """
    img = create_blank_image()
    center = (200, 200)

    colors = [(0, 0, 0), (50, 50, 50), (100, 100, 100)]

    for i, angle in enumerate(angles):
        color = colors[i % len(colors)]
        draw_line_by_angle(img, center, angle, length=180, color=color, thickness=2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def create_parallel_lines_image(angle: float = 45, spacing: int = 50,
                                count: int = 3, filename: str = None) -> np.ndarray:
    """Create an image with parallel lines at a specified angle.

    Args:
        angle: Angle of the parallel lines in degrees
        spacing: Spacing between lines in pixels
        count: Number of parallel lines
        filename: Optional filename to save the image

    Returns:
        Image with parallel lines
    """
    img = create_blank_image()

    angle_radians = np.radians(angle)

    # Calculate perpendicular offset direction
    offset_x = int(spacing * np.cos(angle_radians + np.pi/2))
    offset_y = int(spacing * np.sin(angle_radians + np.pi/2))

    # Draw parallel lines
    base_center = (200, 200 - (count-1) * spacing // 2)

    for i in range(count):
        center = (base_center[0] + i * offset_x, base_center[1] + i * offset_y)
        draw_line_by_angle(img, center, angle, length=250, color=(0, 0, 0), thickness=2)

    cv2.putText(img, f"Parallel at {angle} deg", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def create_perpendicular_lines_image(filename: str = None) -> np.ndarray:
    """Create an image with perpendicular lines (90 degrees).

    Args:
        filename: Optional filename to save the image

    Returns:
        Image with perpendicular lines
    """
    return create_single_angle_image(90, filename)


def create_vertical_line_image(filename: str = None) -> np.ndarray:
    """Create an image with a single vertical line (edge case).

    Args:
        filename: Optional filename to save the image

    Returns:
        Image with a vertical line
    """
    img = create_blank_image()
    center = (200, 200)
    draw_line_by_angle(img, center, 90, length=300, color=(0, 0, 0), thickness=3)

    cv2.putText(img, "Vertical line (90 deg)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def create_horizontal_line_image(filename: str = None) -> np.ndarray:
    """Create an image with a single horizontal line (edge case).

    Args:
        filename: Optional filename to save the image

    Returns:
        Image with a horizontal line
    """
    img = create_blank_image()
    center = (200, 200)
    draw_line_by_angle(img, center, 0, length=300, color=(0, 0, 0), thickness=3)

    cv2.putText(img, "Horizontal line (0 deg)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def create_collinear_lines_image(filename: str = None) -> np.ndarray:
    """Create an image with collinear lines (edge case).

    Args:
        filename: Optional filename to save the image

    Returns:
        Image with collinear lines
    """
    img = create_blank_image()

    # Draw two line segments on the same line
    cv2.line(img, (50, 200), (180, 200), (0, 0, 0), 3)
    cv2.line(img, (220, 200), (350, 200), (50, 50, 50), 3)

    cv2.putText(img, "Collinear lines (0/180 deg)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def create_different_length_lines_image(filename: str = None) -> np.ndarray:
    """Create an image with lines of different lengths at various angles.

    Args:
        filename: Optional filename to save the image

    Returns:
        Image with lines of different lengths
    """
    img = create_blank_image()
    center = (200, 200)

    # Lines with different lengths
    lengths = [80, 120, 160, 200]
    angles = [0, 45, 90, 135]

    for length, angle in zip(lengths, angles):
        draw_line_by_angle(img, center, angle, length=length,
                          color=(0, 0, 0), thickness=2)

    cv2.putText(img, "Different length lines", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if filename:
        cv2.imwrite(filename, img)

    return img


def generate_all_test_images(output_dir: str = None) -> None:
    """Generate all test images and save them to the specified directory.

    Args:
        output_dir: Directory to save test images. If None, uses fixtures directory.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic test images...")

    # Standard angles
    standard_angles = [30, 45, 60, 90, 120, 135, 150, 180]
    for angle in standard_angles:
        filename = output_dir / f"angle_{angle}_degrees.png"
        create_single_angle_image(angle, str(filename))
        print(f"  Created: {filename.name}")

    # Edge cases
    filename = output_dir / "vertical_line.png"
    create_vertical_line_image(str(filename))
    print(f"  Created: {filename.name}")

    filename = output_dir / "horizontal_line.png"
    create_horizontal_line_image(str(filename))
    print(f"  Created: {filename.name}")

    filename = output_dir / "collinear_lines.png"
    create_collinear_lines_image(str(filename))
    print(f"  Created: {filename.name}")

    # Parallel lines
    for angle in [0, 45, 90]:
        filename = output_dir / f"parallel_lines_{angle}_degrees.png"
        create_parallel_lines_image(angle, spacing=50, count=3, filename=str(filename))
        print(f"  Created: {filename.name}")

    # Multiple intersecting lines
    filename = output_dir / "intersecting_lines.png"
    create_intersecting_lines_image([0, 45, 90, 135], str(filename))
    print(f"  Created: {filename.name}")

    # Different length lines
    filename = output_dir / "different_lengths.png"
    create_different_length_lines_image(str(filename))
    print(f"  Created: {filename.name}")

    print(f"\nAll test images generated in: {output_dir}")
    print(f"Total images: {len(list(output_dir.glob('*.png')))}")


if __name__ == "__main__":
    generate_all_test_images()
