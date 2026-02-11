#!/usr/bin/env python3
"""
Test wire bender images with automatic line detection.
"""
import cv2
import numpy as np
import time
from pathlib import Path
from detection import LineDetector, LineDetectorConfig
from detection.postprocessor import LinePostprocessor, PostprocessorConfig
from core.geometry import Line

def test_wire_bend_detection():
    """Test detection on wire bender calibration images."""

    # Setup
    test_dir = Path("test_images")
    output_dir = Path("test_images/results")
    output_dir.mkdir(exist_ok=True)

    # Get all test images
    images = sorted(test_dir.glob("wire_bend_*.png"))

    if not images:
        print("❌ No wire bend images found in test_images/")
        return

    print(f"🔍 Testing detection on {len(images)} wire bender images\n")
    print("=" * 70)

    # Create detector with default config
    detector = LineDetector()
    postprocessor = LinePostprocessor()

    results = []

    for img_path in images:
        print(f"\n📸 Processing: {img_path.name}")
        print("-" * 70)

        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"❌ Failed to load {img_path}")
            continue

        h, w = img.shape[:2]
        print(f"   Image size: {w}×{h} pixels")

        # Run detection
        start_time = time.time()
        detection_result = detector.detect(img)
        detection_time = (time.time() - start_time) * 1000

        print(f"   Raw lines detected: {len(detection_result.lines)}")

        # Post-process: merge lines
        merged_lines = postprocessor.merge_lines(detection_result.lines)
        print(f"   After merging: {len(merged_lines)} lines")

        # Find angles between line pairs
        angles = []
        if len(merged_lines) >= 2:
            # Find the two longest lines (likely the main wire segments)
            sorted_lines = sorted(merged_lines, key=lambda l: l.length(), reverse=True)

            # Calculate angle between top 2 lines
            for i in range(min(len(sorted_lines), 3)):
                for j in range(i+1, min(len(sorted_lines), 4)):
                    line1 = sorted_lines[i]
                    line2 = sorted_lines[j]

                    # Calculate angle
                    angle = line1.angle_between(line2)
                    angles.append({
                        'angle': angle,
                        'line1': line1,
                        'line2': line2
                    })

        print(f"   Angle measurements: {len(angles)} found")

        # Show top angles
        if angles:
            # Sort by angle magnitude (most significant bends)
            angles_sorted = sorted(angles, key=lambda a: min(a['angle'], 180-a['angle']))

            print(f"\n   📐 Top angle measurements:")
            for idx, angle_info in enumerate(angles_sorted[:3], 1):
                angle_deg = angle_info['angle']
                # Show both the angle and its complement
                complement = 180 - angle_deg
                print(f"      {idx}. {angle_deg:.1f}° (or {complement:.1f}°)")

        print(f"\n   ⏱️  Processing time: {detection_time:.1f}ms")

        # Create visualization
        vis_img = img.copy()

        # Draw all merged lines
        for line in merged_lines:
            color = (0, 255, 0)  # Green
            thickness = 3
            cv2.line(vis_img,
                    (int(line.x1), int(line.y1)),
                    (int(line.x2), int(line.y2)),
                    color, thickness)

        # Draw top angle
        if angles:
            top_angle = angles_sorted[0]
            line1 = top_angle['line1']
            line2 = top_angle['line2']

            # Draw lines in red
            cv2.line(vis_img,
                    (int(line1.x1), int(line1.y1)),
                    (int(line1.x2), int(line1.y2)),
                    (0, 0, 255), 4)
            cv2.line(vis_img,
                    (int(line2.x1), int(line2.y1)),
                    (int(line2.x2), int(line2.y2)),
                    (0, 0, 255), 4)

            # Find intersection or closest point
            intersection = line1.intersection(line2)
            if intersection:
                ix, iy = intersection
                # Draw intersection point
                cv2.circle(vis_img, (int(ix), int(iy)), 10, (255, 0, 255), -1)

                # Add angle text
                angle_text = f"{top_angle['angle']:.1f}"
                cv2.putText(vis_img, angle_text,
                           (int(ix) + 20, int(iy) - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3)

        # Add info text
        info_text = f"Lines: {len(merged_lines)} | Time: {detection_time:.0f}ms"
        cv2.putText(vis_img, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Save result
        output_path = output_dir / f"detected_{img_path.name}"
        cv2.imwrite(str(output_path), vis_img)
        print(f"   💾 Saved visualization: {output_path}")

        # Store results
        results.append({
            'image': img_path.name,
            'size': (w, h),
            'raw_lines': len(detection_result.lines),
            'merged_lines': len(merged_lines),
            'angles': len(angles),
            'top_angle': angles_sorted[0]['angle'] if angles else None,
            'time_ms': detection_time
        })

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    for result in results:
        print(f"\n{result['image']}:")
        print(f"  Size: {result['size'][0]}×{result['size'][1]}px")
        print(f"  Lines: {result['raw_lines']} → {result['merged_lines']} (after merge)")
        print(f"  Angles: {result['angles']} measurements")
        if result['top_angle']:
            print(f"  Main angle: {result['top_angle']:.1f}°")
        print(f"  Speed: {result['time_ms']:.1f}ms")

    avg_time = np.mean([r['time_ms'] for r in results])
    print(f"\n⚡ Average processing time: {avg_time:.1f}ms")
    print(f"✅ All visualizations saved to: test_images/results/")

if __name__ == "__main__":
    test_wire_bend_detection()
