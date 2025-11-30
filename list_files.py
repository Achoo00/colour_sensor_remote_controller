import os

path = r"C:\Users\amaha\Videos\Anime\Gachiakuta"
try:
    if os.path.exists(path):
        print(f"Listing files in {path}:")
        for f in os.listdir(path):
            print(f)
    else:
        print(f"Path does not exist: {path}")
except Exception as e:
    print(f"Error: {e}")
