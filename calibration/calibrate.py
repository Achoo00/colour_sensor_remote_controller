import cv2
import numpy as np
import json
from pathlib import Path

def save_calibration(color_name, hsv_min, hsv_max):
    """Save calibration results to a JSON file."""
    calibration = {
        "hsv_lower": hsv_min.tolist(),
        "hsv_upper": hsv_max.tolist()
    }
    
    output_dir = Path("calibration")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "results.json"
    
    # Load existing calibrations if any
    if output_path.exists():
        with open(output_path, 'r') as f:
            existing = json.load(f)
    else:
        existing = {}
    
    # Update with new calibration
    existing[color_name] = calibration
    
    # Save back to file
    with open(output_path, 'w') as f:
        json.dump(existing, f, indent=2)
    print(f"✅ Saved calibration for {color_name}")

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Load ROI from config if available
    try:
        with open("config/global.json", 'r') as f:
            config = json.load(f)
            roi = config.get("roi", [100, 100, 200, 200])  # [x, y, w, h]
    except FileNotFoundError:
        roi = [100, 100, 200, 200]  # Default ROI
    
    # Window setup
    cv2.namedWindow('Calibration')
    cv2.namedWindow('HSV Mask')
    
    # Initialize variables
    color_name = input("Enter color name to calibrate (e.g., red, yellow): ").lower()
    samples = []
    
    print("\nControls:")
    print("SPACE - Add current ROI values to calibration")
    print("S - Save calibration")
    print("Q - Quit without saving")
    print("\nPosition the color in the ROI rectangle and press SPACE to sample...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
            
        # Draw ROI rectangle
        x, y, w, h = roi
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Extract ROI and convert to HSV
        roi_region = frame[y:y+h, x:x+w]
        hsv_roi = cv2.cvtColor(roi_region, cv2.COLOR_BGR2HSV)
        
        # If we have samples, show the current mask
        if samples:
            # Calculate min and max HSV values from samples
            hsv_min = np.min(samples, axis=0)
            hsv_max = np.max(samples, axis=0)
            
            # Create mask
            mask = cv2.inRange(hsv_roi, hsv_min, hsv_max)
            cv2.imshow('HSV Mask', mask)
            
            # Show the HSV ranges
            print(f"\rCurrent HSV range: {hsv_min} to {hsv_max}", end='')
        
        # Show the main window
        cv2.imshow('Calibration', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nCalibration cancelled")
            break
        elif key == ord(' '):
            # Add current ROI average to samples
            hsv_values = np.mean(hsv_roi, axis=(0, 1))
            samples.append(hsv_values)
            print(f"\nSample {len(samples)} added: {hsv_values}")
        elif key == ord('s') and samples:
            # Calculate final HSV ranges
            hsv_min = np.min(samples, axis=0)
            hsv_max = np.max(samples, axis=0)
            
            # Add some tolerance to the ranges
            tolerance = 10
            hsv_min = np.maximum(hsv_min - tolerance, 0)
            hsv_max = np.minimum(hsv_max + tolerance, 255)
            
            # Save calibration
            save_calibration(color_name, hsv_min, hsv_max)
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
