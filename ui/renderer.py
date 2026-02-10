"""
Renderer Module

Provides visualization functions for drawing lines, angles, and annotations
on images for the angle measurement tool.

Classes:
    Renderer: Main rendering class for visual elements
    RenderConfig: Configuration for rendering styles

Key Features:
    - Draw detected and manual lines with different colors
    - Render angle measurements with arc visualization
    - Annotate angles with degree values
    - Visual feedback (hover, selection states)
    - Display statistics and metrics
    - Edge detection visualization overlay
"""

import cv2
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

from core.geometry import Line, AngleCalculator


@dataclass
class RenderConfig:
    """
    Configuration for rendering styles and colors.

    Attributes:
        detected_line_color: Color for automatically detected lines (B, G, R)
        manual_line_color: Color for manually drawn lines (B, G, R)
        selected_line_color: Color for selected lines (B, G, R)
        hover_line_color: Color for hovered lines (B, G, R)
        angle_arc_color: Color for angle arc visualization (B, G, R)
        angle_text_color: Color for angle text (B, G, R)
        text_outline_color: Color for text outline (B, G, R)
        line_thickness: Thickness of lines in pixels
        text_font: OpenCV font for text rendering
        text_scale: Scale factor for text
        text_thickness: Thickness of text
        arc_radius: Radius of angle arc in pixels
    """
    # Color scheme (BGR format for OpenCV)
    detected_line_color: Tuple[int, int, int] = (0, 255, 0)      # Green
    manual_line_color: Tuple[int, int, int] = (255, 0, 0)        # Blue
    selected_line_color: Tuple[int, int, int] = (0, 255, 255)    # Yellow
    hover_line_color: Tuple[int, int, int] = (255, 128, 0)       # Orange
    angle_arc_color: Tuple[int, int, int] = (255, 255, 0)        # Cyan
    angle_text_color: Tuple[int, int, int] = (255, 255, 255)     # White
    text_outline_color: Tuple[int, int, int] = (0, 0, 0)         # Black
    point_color: Tuple[int, int, int] = (0, 0, 255)              # Red

    # Drawing properties
    line_thickness: int = 2
    hover_line_thickness: int = 3
    selected_line_thickness: int = 4
    text_font: int = cv2.FONT_HERSHEY_SIMPLEX
    text_scale: float = 0.7
    text_thickness: int = 2
    arc_radius: int = 40
    point_radius: int = 5


class Renderer:
    """
    Handles all visual rendering for the angle measurement tool.

    Provides methods to draw lines, angles, annotations, and overlays
    with consistent styling and visual feedback.

    Attributes:
        config: Rendering configuration (colors, styles, etc.)

    Example:
        >>> renderer = Renderer()
        >>> # Draw detected lines
        >>> img_with_lines = renderer.draw_lines(image, lines, line_type='detected')
        >>> # Draw angle between two lines
        >>> img_with_angle = renderer.draw_angle_between_lines(image, line1, line2)
        >>> # Add statistics overlay
        >>> img_with_stats = renderer.draw_statistics(image, num_lines=5, fps=30.5)
    """

    def __init__(self, config: Optional[RenderConfig] = None):
        """
        Initialize the renderer.

        Args:
            config: Optional rendering configuration. Uses default if None.
        """
        self.config = config if config else RenderConfig()

    def draw_line(self,
                  image: np.ndarray,
                  line: Line,
                  color: Optional[Tuple[int, int, int]] = None,
                  thickness: Optional[int] = None,
                  line_type: str = 'detected') -> np.ndarray:
        """
        Draw a single line on the image.

        Args:
            image: Image to draw on (will be modified)
            line: Line object to draw
            color: Optional custom color (overrides line_type)
            thickness: Optional custom thickness
            line_type: Type of line ('detected', 'manual', 'selected', 'hover')

        Returns:
            Image with line drawn
        """
        # Determine color based on line type
        if color is None:
            if line_type == 'detected':
                color = self.config.detected_line_color
            elif line_type == 'manual':
                color = self.config.manual_line_color
            elif line_type == 'selected':
                color = self.config.selected_line_color
            elif line_type == 'hover':
                color = self.config.hover_line_color
            else:
                color = self.config.detected_line_color

        # Determine thickness
        if thickness is None:
            if line_type == 'hover':
                thickness = self.config.hover_line_thickness
            elif line_type == 'selected':
                thickness = self.config.selected_line_thickness
            else:
                thickness = self.config.line_thickness

        # Draw the line
        pt1 = (int(line.x1), int(line.y1))
        pt2 = (int(line.x2), int(line.y2))
        cv2.line(image, pt1, pt2, color, thickness, cv2.LINE_AA)

        return image

    def draw_lines(self,
                   image: np.ndarray,
                   lines: List[Line],
                   color: Optional[Tuple[int, int, int]] = None,
                   line_type: str = 'detected',
                   draw_endpoints: bool = False) -> np.ndarray:
        """
        Draw multiple lines on the image.

        Args:
            image: Image to draw on (will be modified)
            lines: List of Line objects to draw
            color: Optional custom color for all lines
            line_type: Type of lines ('detected', 'manual', 'selected')
            draw_endpoints: Whether to draw circles at line endpoints

        Returns:
            Image with lines drawn
        """
        result = image.copy()

        for line in lines:
            self.draw_line(result, line, color=color, line_type=line_type)

            # Optionally draw endpoints
            if draw_endpoints:
                pt1 = (int(line.x1), int(line.y1))
                pt2 = (int(line.x2), int(line.y2))
                cv2.circle(result, pt1, self.config.point_radius,
                          self.config.point_color, -1, cv2.LINE_AA)
                cv2.circle(result, pt2, self.config.point_radius,
                          self.config.point_color, -1, cv2.LINE_AA)

        return result

    def draw_angle_arc(self,
                      image: np.ndarray,
                      vertex: Tuple[int, int],
                      angle_start: float,
                      angle_end: float,
                      radius: Optional[int] = None,
                      color: Optional[Tuple[int, int, int]] = None) -> np.ndarray:
        """
        Draw an arc to visualize an angle.

        Args:
            image: Image to draw on (will be modified)
            vertex: Center point of the arc (x, y)
            angle_start: Starting angle in degrees
            angle_end: Ending angle in degrees
            radius: Optional arc radius (uses config default if None)
            color: Optional color (uses config default if None)

        Returns:
            Image with arc drawn
        """
        if radius is None:
            radius = self.config.arc_radius
        if color is None:
            color = self.config.angle_arc_color

        # OpenCV ellipse uses angles in degrees, measured clockwise from horizontal
        # We need to convert our counter-clockwise angles
        start_angle_cv = -angle_start
        end_angle_cv = -angle_end

        # Ensure we sweep in the right direction
        if end_angle_cv < start_angle_cv:
            start_angle_cv, end_angle_cv = end_angle_cv, start_angle_cv

        cv2.ellipse(
            image,
            vertex,
            (radius, radius),
            0,
            start_angle_cv,
            end_angle_cv,
            color,
            2,
            cv2.LINE_AA
        )

        return image

    def draw_angle_between_lines(self,
                                 image: np.ndarray,
                                 line1: Line,
                                 line2: Line,
                                 show_arc: bool = True,
                                 show_text: bool = True) -> np.ndarray:
        """
        Draw angle visualization between two lines.

        Args:
            image: Image to draw on (will be modified)
            line1: First line
            line2: Second line
            show_arc: Whether to draw the angle arc
            show_text: Whether to show angle value as text

        Returns:
            Image with angle visualization
        """
        result = image.copy()

        # Calculate angle between lines
        try:
            angle = AngleCalculator.calculate_angle_between_lines(line1, line2)
        except ZeroDivisionError:
            return result

        # Find intersection point (or use midpoint if parallel)
        intersection = line1.intersection(line2)
        if intersection is None:
            # Lines are parallel, use midpoint of first line
            intersection = line1.midpoint

        vertex = (int(intersection[0]), int(intersection[1]))

        # Draw arc if requested
        if show_arc:
            # Get angles of both lines
            angle1 = line1.angle
            angle2 = line2.angle

            # Draw arc between the two angles
            self.draw_angle_arc(result, vertex, angle1, angle2)

        # Draw angle text if requested
        if show_text:
            text = f"{angle:.1f}"
            self.draw_text_with_outline(
                result,
                text,
                (vertex[0] + 50, vertex[1] - 10)
            )

        return result

    def draw_angle_3_points(self,
                           image: np.ndarray,
                           pt1: Tuple[int, int],
                           pt2: Tuple[int, int],
                           pt3: Tuple[int, int],
                           show_arc: bool = True,
                           show_text: bool = True,
                           show_lines: bool = True) -> np.ndarray:
        """
        Draw angle formed by three points (angle at pt1).

        This matches the original setup.py behavior where the angle is
        measured at the first point with rays to pt2 and pt3.

        Args:
            image: Image to draw on (will be modified)
            pt1: Vertex point (where angle is measured)
            pt2: First ray endpoint
            pt3: Second ray endpoint
            show_arc: Whether to draw the angle arc
            show_text: Whether to show angle value as text
            show_lines: Whether to draw the lines forming the angle

        Returns:
            Image with angle visualization
        """
        result = image.copy()

        # Calculate angle
        try:
            angle = AngleCalculator.calculate_angle_3_points(pt1, pt2, pt3)
        except ValueError:
            return result

        # Draw lines if requested
        if show_lines:
            cv2.line(result, pt1, pt2,
                    self.config.manual_line_color, 2, cv2.LINE_AA)
            cv2.line(result, pt1, pt3,
                    self.config.manual_line_color, 2, cv2.LINE_AA)

        # Draw points
        for pt in [pt1, pt2, pt3]:
            cv2.circle(result, pt, self.config.point_radius,
                      self.config.point_color, -1, cv2.LINE_AA)

        # Draw arc if requested
        if show_arc:
            # Calculate angles for the two rays
            angle1 = math.degrees(math.atan2(pt2[1] - pt1[1], pt2[0] - pt1[0]))
            angle2 = math.degrees(math.atan2(pt3[1] - pt1[1], pt3[0] - pt1[0]))
            self.draw_angle_arc(result, pt1, angle1, angle2)

        # Draw text if requested
        if show_text:
            text = f"{int(angle)}"
            text_pos = (pt1[0] - 40, pt1[1] - 20)
            self.draw_text_with_outline(result, text, text_pos, scale=1.5)

        return result

    def draw_text_with_outline(self,
                               image: np.ndarray,
                               text: str,
                               position: Tuple[int, int],
                               color: Optional[Tuple[int, int, int]] = None,
                               outline_color: Optional[Tuple[int, int, int]] = None,
                               scale: Optional[float] = None,
                               thickness: Optional[int] = None) -> np.ndarray:
        """
        Draw text with a contrasting outline for better visibility.

        Args:
            image: Image to draw on (will be modified)
            text: Text to draw
            position: Text position (x, y)
            color: Text color (uses config default if None)
            outline_color: Outline color (uses config default if None)
            scale: Text scale (uses config default if None)
            thickness: Text thickness (uses config default if None)

        Returns:
            Image with text drawn
        """
        if color is None:
            color = self.config.angle_text_color
        if outline_color is None:
            outline_color = self.config.text_outline_color
        if scale is None:
            scale = self.config.text_scale
        if thickness is None:
            thickness = self.config.text_thickness

        font = self.config.text_font

        # Draw outline (thicker, black)
        cv2.putText(
            image, text, position, font, scale,
            outline_color, thickness + 1, cv2.LINE_AA
        )

        # Draw main text
        cv2.putText(
            image, text, position, font, scale,
            color, thickness, cv2.LINE_AA
        )

        return image

    def draw_statistics(self,
                       image: np.ndarray,
                       stats: Dict[str, Any],
                       position: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Draw statistics overlay on the image.

        Args:
            image: Image to draw on (will be modified)
            stats: Dictionary of statistics to display
                  e.g., {'lines': 5, 'angles': 3, 'fps': 30.5}
            position: Top-left position for stats (auto if None)

        Returns:
            Image with statistics overlay
        """
        result = image.copy()

        if position is None:
            position = (10, 30)

        x, y = position
        line_height = 25

        for key, value in stats.items():
            # Format the text
            if isinstance(value, float):
                text = f"{key}: {value:.2f}"
            else:
                text = f"{key}: {value}"

            self.draw_text_with_outline(
                result, text, (x, y),
                scale=0.6, thickness=1
            )
            y += line_height

        return result

    def draw_edge_overlay(self,
                         image: np.ndarray,
                         edges: np.ndarray,
                         alpha: float = 0.3) -> np.ndarray:
        """
        Overlay edge detection visualization on the original image.

        Args:
            image: Original color image
            edges: Binary edge image (single channel)
            alpha: Transparency of edge overlay (0.0 = transparent, 1.0 = opaque)

        Returns:
            Image with edge overlay
        """
        result = image.copy()

        # Convert edges to color (green overlay)
        if len(edges.shape) == 2:
            edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        else:
            edges_color = edges

        # Create green mask from edges
        mask = np.zeros_like(result)
        mask[edges_color > 0] = [0, 255, 0]  # Green

        # Blend with original image
        cv2.addWeighted(mask, alpha, result, 1.0, 0, result)

        return result

    def create_side_by_side(self,
                           images: List[np.ndarray],
                           labels: Optional[List[str]] = None,
                           padding: int = 10) -> np.ndarray:
        """
        Create a side-by-side comparison of multiple images.

        Args:
            images: List of images to display (must all be same height)
            labels: Optional list of labels for each image
            padding: Padding between images in pixels

        Returns:
            Combined image with all inputs side-by-side
        """
        if not images:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        # Ensure all images are color
        color_images = []
        for img in images:
            if len(img.shape) == 2:
                color_images.append(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))
            else:
                color_images.append(img)

        # Resize all to same height
        target_height = color_images[0].shape[0]
        resized = []
        for img in color_images:
            if img.shape[0] != target_height:
                aspect = img.shape[1] / img.shape[0]
                target_width = int(target_height * aspect)
                img = cv2.resize(img, (target_width, target_height))
            resized.append(img)

        # Add padding
        padded = []
        for img in resized:
            h, w = img.shape[:2]
            padded_img = np.zeros((h, w + padding, 3), dtype=np.uint8)
            padded_img[:, :w] = img
            padded.append(padded_img)

        # Concatenate horizontally
        result = np.hstack(padded)

        # Add labels if provided
        if labels:
            x_offset = 0
            for img, label in zip(resized, labels):
                w = img.shape[1]
                self.draw_text_with_outline(
                    result, label, (x_offset + 10, 25),
                    scale=0.7, thickness=2
                )
                x_offset += w + padding

        return result

    def highlight_line(self,
                      image: np.ndarray,
                      line: Line,
                      highlight_type: str = 'hover') -> np.ndarray:
        """
        Highlight a line with special visual effect.

        Args:
            image: Image to draw on (will be modified)
            line: Line to highlight
            highlight_type: Type of highlight ('hover', 'selected')

        Returns:
            Image with highlighted line
        """
        result = image.copy()

        if highlight_type == 'hover':
            # Draw with hover style (thicker, orange)
            self.draw_line(result, line, line_type='hover')
        elif highlight_type == 'selected':
            # Draw with selected style (thicker, yellow)
            self.draw_line(result, line, line_type='selected')
            # Also draw endpoints
            pt1 = (int(line.x1), int(line.y1))
            pt2 = (int(line.x2), int(line.y2))
            cv2.circle(result, pt1, self.config.point_radius + 2,
                      self.config.selected_line_color, -1, cv2.LINE_AA)
            cv2.circle(result, pt2, self.config.point_radius + 2,
                      self.config.selected_line_color, -1, cv2.LINE_AA)

        return result

    def draw_detection_info(self,
                           image: np.ndarray,
                           num_lines: int,
                           processing_time: Optional[float] = None,
                           params_text: Optional[str] = None) -> np.ndarray:
        """
        Draw detection information overlay.

        Args:
            image: Image to draw on (will be modified)
            num_lines: Number of lines detected
            processing_time: Optional processing time in milliseconds
            params_text: Optional parameter description text

        Returns:
            Image with info overlay
        """
        result = image.copy()

        # Create info dictionary
        info = {'Lines Detected': num_lines}

        if processing_time is not None:
            info['Processing Time'] = f"{processing_time:.1f}ms"

        # Draw statistics
        result = self.draw_statistics(result, info, position=(10, 30))

        # Draw parameter text if provided
        if params_text:
            h = image.shape[0]
            self.draw_text_with_outline(
                result, params_text, (10, h - 20),
                scale=0.5, thickness=1
            )

        return result
