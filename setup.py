"""
Angle Measurement Tool - Main Application

This module provides an interactive GUI for measuring angles in images, webcam feeds,
and video files. Users can mark three points to determine the angle formed at the center
point using the dot product method. The application supports multiple input sources via
trackbar-based mode switching and provides features for clearing measurements and saving
annotated results.

Key Features:
    - Multi-source support: Image, webcam, and video streams
    - Interactive point marking via mouse clicks
    - Real-time angle calculation and visualization
    - Keyboard shortcuts for clearing and saving results
    - Automatic frame resizing for consistent display

Main Functions:
    - mousePoints(): Handles mouse click events for point marking
    - getAngle(): Calculates and displays angle from three points
    - gradient(): Computes slope between two points (utility function)
    - Main loop: Manages input source switching and user interactions
"""

import cv2
import math
import imutils
import numpy as np
from utils.image import Image
from utils.webcam import Webcam
from utils.video import Video
from utils.file import Filename


# Initialize input sources
path, img = Image.main()
path2, cam = Webcam.main()
path3, video = Video.main()
pointsList = []



def mousePoints(event, x, y, flags, params):
    """
    Mouse callback function for marking points on the displayed image.

    Handles left mouse button clicks to mark points for angle measurement. When three
    points are marked, they form an angle at the second point. Visual feedback includes:
    - Red circles at clicked points
    - Red lines connecting consecutive points within each angle measurement

    Args:
        event: OpenCV mouse event type. Processes cv2.EVENT_LBUTTONDOWN for clicks.
        x (int): X-coordinate of mouse position in image pixels.
        y (int): Y-coordinate of mouse position in image pixels.
        flags: Additional mouse event flags (unused in current implementation).
        params: Additional parameters passed to callback (unused).

    Side Effects:
        - Appends [x, y] coordinates to pointsList
        - Draws circles and lines on the global img variable
        - Maintains point groupings for angle calculation (every 3 points form one angle)
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        size = len(pointsList)
        # Draw connecting line between first and current point of each angle group
        if size != 0 and size % 3 != 0:
            cv2.line(img, tuple(pointsList[round((size-1)/3)*3]), (x, y), (0, 0, 255), 2)
        # Mark clicked point with red circle
        cv2.circle(img, (x, y), 5, (0, 0, 255), cv2.FILLED)
        pointsList.append([x, y])
        

def gradient(pt1, pt2):
    """
    Calculate the slope (gradient) between two points.

    Computes the slope m = (y2 - y1) / (x2 - x1) for the line connecting two points.
    Handles vertical lines by assigning a near-zero denominator to avoid division by zero.

    Args:
        pt1 (list or tuple): First point as [x, y] or (x, y) coordinates.
        pt2 (list or tuple): Second point as [x, y] or (x, y) coordinates.

    Returns:
        float: The slope of the line connecting pt1 and pt2.
               Very large value (~10^-54) for nearly vertical lines.

    Note:
        This function is currently unused in the main algorithm but is retained
        for potential future enhancements. The angle calculation uses vector
        operations (dot product) instead of slopes.
    """
    valuem1 = pt2[0] - pt1[0]
    valuem2 = pt2[1] - pt1[1]

    # Handle vertical line case (x2 == x1)
    if pt2[0] == pt1[0]:
        valuem1 = 0.000000000000000000000000000000000000000000000000000000001

    return valuem2 / valuem1

def getAngle(pointsList):
    """
    Calculate and display the angle formed by three points.

    Computes the angle at the center point (pt2) formed by the rays from pt2 to pt1
    and from pt2 to pt3. Uses the vector dot product method for robust numerical
    stability. The calculated angle is displayed on the image at the vertex location.

    Algorithm:
        1. Extract the last three points from pointsList (pt1, pt2, pt3)
        2. Create vectors: ba = pt2 - pt1, bc = pt3 - pt1
        3. Compute angle using: cos(θ) = (ba · bc) / (|ba| × |bc|)
        4. Convert from radians to degrees and round to nearest integer
        5. Render angle value on image at the vertex point

    Args:
        pointsList (list): List of points where each point is [x, y]. Function uses
                          the last three points: pointsList[-3:].

    Returns:
        None (modifies global img variable by drawing angle text)

    Side Effects:
        - Modifies global img variable by rendering text annotation
        - Displays the calculated angle value near the first marked point
    """
    pt1, pt2, pt3 = pointsList[-3:]
    a = np.array(pt2)
    b = np.array(pt1)
    c = np.array(pt3)

    # Calculate vectors from the vertex (pt2) to the other two points
    ba = a - b
    bc = c - b

    # Compute angle using dot product formula
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    angle = math.degrees(angle)
    angle = round(angle)

    # Display the angle value on the image
    cv2.putText(img, str(abs(angle)), (pt1[0] - 40, pt1[1] - 20), cv2.FONT_HERSHEY_COMPLEX,
                1.5, (0, 0, 255), 2)

def null(x):
    """
    Null callback function for OpenCV trackbars.

    Used as a placeholder callback for trackbars that don't require action on value changes.
    This allows trackbars to function without triggering specific behavior.

    Args:
        x (int): Trackbar position value (required by OpenCV trackbar callback signature).
    """
    pass




# ============================================================================
# Main Application Loop
# ============================================================================
# Creates the OpenCV window with trackbars to switch between input sources.
# The trackbars allow users to select from different input modes:
#   - Image: Static image from file
#   - Camera: Live webcam feed
#   - Video: Video file playback
# Only one source can be active at a time (mutual exclusivity enforced).
# ============================================================================

cv2.namedWindow("Angle Measurement")
# arguments: trackbar_name, window_name, default_value, max_value, callback_fn
# cv2.createTrackbar("Angle measure from Image","Angle Measurement",0,1,null)
cv2.createTrackbar("Camera", "Angle Measurement", 0, 1, null)
cv2.createTrackbar("Video", "Angle Measurement", 0, 1, null)
pos = 0
gallery_img = img

while True:

    # get Trackbar position
    #pos = cv2.getTrackbarPos("Angle measure from Image", "Angle Measurement")
    pos2 = cv2.getTrackbarPos("Camera", "Angle Measurement")
    pos3 = cv2.getTrackbarPos("Video","Angle Measurement")
    if pos3 == 1:
        pos2 = 0
    elif pos2 == 1:
        pos3 = 0    
    
    #key value singnal detector
    key = cv2.waitKey(1) & 0xFF    
    #pos2 = cv2.getTrackbarPos("Switch Video", "My pet")
    if pos == 0:

        if len(pointsList) % 3 == 0 and len(pointsList) !=0:
            getAngle(pointsList)
        
        cv2.imshow('Angle Measurement',img)    
        cv2.setMouseCallback('Angle Measurement',mousePoints)

        if key == ord('c'):
            pointsList = []
            img = cv2.imread(path)
            img = imutils.resize(img, height=650)
        elif key == ord('s'):
            file_name = Filename.main()
            file_name = str(file_name)
            cv2.imwrite('result/'+ file_name+'.png', img)    
        elif key == ord('q') or key == 27:
            break
               

    if pos2 == 1:
        __, img = cam.read()
        img = imutils.resize(img, height=650)

        if len(pointsList) % 3 == 0 and len(pointsList) !=0:
            getAngle(pointsList)
        
        cv2.imshow('Angle Measurement',img)    
        cv2.setMouseCallback('Angle Measurement',mousePoints)
        if key == ord('c'):
            pointsList = []
            img = cv2.imread(path2)

        elif key == ord('s'):
            file_name = Filename.main()
            file_name = str(file_name)
            cv2.imwrite('result/'+ file_name+'.png', img)    
            
    if pos3 == 1:
        try:
            __, img = video.read()
            img = imutils.resize(img, height=650)   
            if len(pointsList) % 3 == 0 and len(pointsList) !=0:
                getAngle(pointsList)
            
            cv2.imshow('Angle Measurement',img)    
            cv2.setMouseCallback('Angle Measurement',mousePoints)
            if key == ord('c'):
                pointsList = []
                img = cv2.imread(path3)

            elif key ==ord('s'):
                file_name = Filename.main()
                file_name = str(file_name)
                cv2.imwrite('result/'+ file_name+'.png', img)
        except:
            pos = 0
            pos3 = 0
            img = gallery_img
            if len(pointsList) % 3 == 0 and len(pointsList) !=0:
                getAngle(pointsList)
        
            cv2.imshow('Angle Measurement',img)    
            cv2.setMouseCallback('Angle Measurement',mousePoints)

            if key == ord('c'):
                pointsList = []
                img = cv2.imread(path)
                img = imutils.resize(img, height=650)
            elif key == ord('s'):
                file_name = Filename.main()
                file_name = str(file_name)
                cv2.imwrite('result/'+ file_name+'.png', img)    
            elif key == ord('q') or key == 27:
                break
                              
    

cam.release()
cv2.destroyAllWindows()    




   
                