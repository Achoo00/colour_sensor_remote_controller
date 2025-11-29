import time
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from utils.vision import detect_color

class VisionWorker(QThread):
    """
    Worker thread for handling vision processing or simulation input.
    Emits 'color_detected' signal when a configured color is found.
    """
    color_detected = pyqtSignal(str)
    
    def __init__(self, roi, color_config, cooldown=1.0):
        super().__init__()
        self.roi = roi
        self.color_config = color_config
        self.cooldown = cooldown
        self.running = True
        self.cap = None
        self.last_detection_time = 0
        self.simulation_mode = False

    def run(self):
        # Attempt to open the camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("⚠️ Camera not found. Switching to Simulation Mode.")
            self.simulation_mode = True
        else:
            print("📷 Camera initialized successfully.")

        print(f"🟢 Vision Worker started. Mode: {'Simulation' if self.simulation_mode else 'Camera'}")

        while self.running:
            current_time = time.time()
            
            if self.simulation_mode:
                # In simulation mode, we read from stdin.
                # Note: input() is blocking. This means the thread will block here until user types something.
                # This is acceptable for the requested "Simulation Mode".
                try:
                    print("Simulate Color > ", end="", flush=True)
                    color = input().strip().lower()
                    
                    if not self.running:
                        break
                        
                    if color in self.color_config:
                        self.color_detected.emit(color)
                    elif color:
                        print(f"Ignored '{color}' (not in config)")
                        
                except (EOFError, KeyboardInterrupt):
                    break
                except Exception as e:
                    print(f"Error in simulation input: {e}")
            else:
                ret, frame = self.cap.read()
                if ret:
                    color = detect_color(frame, self.roi, self.color_config)
                    if color:
                        # Debounce logic
                        if (current_time - self.last_detection_time) > self.cooldown:
                            self.color_detected.emit(color)
                            self.last_detection_time = current_time
                
                # Sleep to reduce CPU usage (approx 20 FPS)
                self.msleep(50)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()
