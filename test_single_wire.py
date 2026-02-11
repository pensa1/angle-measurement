#!/usr/bin/env python3
"""
Quick test of wire bend detection on a single image.
"""
import cv2
import numpy as np
from detection import LineDetector
from detection.postprocessor import LinePostprocessor
from pathlib import Path

def test_single_image(img_path):
    """Test detection on a single wire bend image."""

    # Read the image from the conversation
    # For now, use the existing sample to demonstrate
    img = cv2.imread(str(img_path))

    if img is None:
        print(f"❌ Could not load image from {img_path}")
        # Try to find any PNG in test_images
        test_dir = Path("test_images")
        pngs = list(test_dir.glob("*.png"))
        if pngs:
            print(f"Found {len(pngs)} PNG files, trying first one...")
            img = cv2.imread(str(pngs[0]))
            img_path = pngs[0]

    if img is None:
        print("❌ No valid images found")
        return

    print(f"📸 Testing: {img_path}")
    print(f"   Image size: {img.shape[1]}×{img.shape[0]} pixels")
    print()

    # Create detector
    detector = LineDetector()
    postprocessor = LinePostprocessor()

    # Run detection
    print("🔍 Running detection...")
    result = detector.detect(img)
    print(f"   ✓ Raw lines detected: {len(result.lines)}")

    # Merge lines
    merged = postprocessor.merge_lines(result.lines)
    print(f"   ✓ After merging: {len(merged)} lines")

    # Find angles
    if len(merged) >= 2:
        # Get the two longest lines
        sorted_lines = sorted(merged, key=lambda l: l.length(), reverse=True)
        line1 = sorted_lines[0]
        line2 = sorted_lines[1]

        # Calculate angle
        angle = line1.angle_between(line2)
        complement = 180 - angle

        print(f"\n📐 Angle measurement:")
        print(f"   Between two longest lines: {angle:.1f}° (or {complement:.1f}°)")

        # Find intersection
        intersection = line1.intersection(line2)

        # Create visualization
        vis = img.copy()

        # Draw all merged lines in green
        for line in merged:
            cv2.line(vis,
                    (int(line.x1), int(line.y1)),
                    (int(line.x2), int(line.y2)),
                    (0, 255, 0), 3)

        # Draw main two lines in red
        cv2.line(vis,
                (int(line1.x1), int(line1.y1)),
                (int(line1.x2), int(line1.y2)),
                (0, 0, 255), 5)
        cv2.line(vis,
                (int(line2.x1), int(line2.y1)),
                (int(line2.x2), int(line2.y2)),
                (0, 0, 255), 5)

        # Draw intersection point
        if intersection:
            ix, iy = intersection
            cv2.circle(vis, (int(ix), int(iy)), 15, (255, 0, 255), -1)

            # Add angle text
            cv2.putText(vis, f"{angle:.1f}°",
                       (int(ix) + 30, int(iy) - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 4)

        # Save result
        output_path = Path("test_images") / "detection_result.png"
        cv2.imwrite(str(output_path), vis)
        print(f"\n💾 Saved visualization: {output_path}")

        return vis, angle
    else:
        print("⚠️  Not enough lines detected to measure angle")
        return None, None

if __name__ == "__main__":
    # Try to detect the wire bend
    img_path = "img/sample.jpg"  # fallback

    # Check for test images first
    test_dir = Path("test_images")
    if test_dir.exists():
        pngs = list(test_dir.glob("*.png"))
        if pngs:
            img_path = pngs[0]

    test_single_image(img_path)
