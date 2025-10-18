# Python code to get mouse position in x,y coordinates, in real time
from pynput.mouse import Controller
import time
mouse = Controller()
while True:
    x, y = mouse.position
    print(f"Mouse position: ({x}, {y})")
    time.sleep(0.5)

