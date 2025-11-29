import pyautogui
import time

print("Starting in 3 seconds…")
time.sleep(3)

print("Searching for image…")
location = pyautogui.locateOnScreen("screenshots/play_btn.png", confidence=0.4)

if location:
    x, y = pyautogui.center(location)
    print("Found! Clicking…")
    pyautogui.click(x, y)
else:
    print("Image not found.")
