import cv2
import numpy as np

def detect_color(frame, roi, color_config):
    """
    Detect the dominant color in the Region of Interest (ROI).
    
    Args:
        frame: The full video frame from the webcam
        roi: Region of Interest as [x, y, width, height]
        color_config: Dictionary mapping color names to their HSV ranges
                     e.g., {"red": {"lower": [170, 195, 75], "upper": [180, 255, 255]}, ...}
    
    Returns:
        The name of the detected color (string) or None if no color matches
    """
    x, y, w, h = roi
    roi_frame = frame[y:y+h, x:x+w]
    
    if roi_frame.size == 0:
        return None
    
    hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)
    detected_color = None
    max_pixels = 0
    
    for color_name, color_range in color_config.items():
        lower = np.array(color_range["lower"])
        upper = np.array(color_range["upper"])
        mask = cv2.inRange(hsv, lower, upper)
        count = cv2.countNonZero(mask)
        
        if count > max_pixels:
            max_pixels = count
            detected_color = color_name
    
    # Only return a color if there's a meaningful match
    # Require at least 20% of ROI pixels to match for detection
    if max_pixels > (w * h * 0.2):
        return detected_color
    
    return None

