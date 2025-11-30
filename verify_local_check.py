import os
import re

ANIME_LIBRARY_PATH = r"C:\Users\amaha\Videos\Anime"

def find_local_episode(title, episode):
    """Search for a local file matching the title and episode."""
    try:
        # Sanitize title for folder name (remove illegal chars)
        safe_title = "".join(c for c in title if c not in r'<>:"/\|?*')
        anime_dir = os.path.join(ANIME_LIBRARY_PATH, safe_title)
        
        if not os.path.exists(anime_dir):
            # Try case-insensitive search for directory
            if os.path.exists(ANIME_LIBRARY_PATH):
                for d in os.listdir(ANIME_LIBRARY_PATH):
                    if d.lower() == safe_title.lower():
                        anime_dir = os.path.join(ANIME_LIBRARY_PATH, d)
                        break
        
        if not os.path.exists(anime_dir):
            print(f"⚠️ Directory not found: {anime_dir}")
            return None
            
        print(f"📂 Searching in: {anime_dir}")
        
        # Search patterns for episode
        files = os.listdir(anime_dir)
        video_extensions = ['.mp4', '.mkv', '.avi']
        
        target_patterns = [
            f"E{episode:02d}",      # E05
            f"E{episode}",          # E5
            f"Episode {episode:02d}", # Episode 05
            f"Episode {episode}",     # Episode 5
            f" {episode:02d} ",       # " 05 "
            f" {episode} ",           # " 5 "
        ]
        
        for f in files:
            if not any(f.lower().endswith(ext) for ext in video_extensions):
                continue
                
            # Check if file matches any pattern
            if re.search(fr"[sS]\d+[eE]{episode:02d}\b", f) or \
               re.search(fr"[eE]{episode:02d}\b", f) or \
               re.search(fr"\b{episode}\b", f): 
                
                return os.path.join(anime_dir, f)
        
        return None
        
    except Exception as e:
        print(f"❌ Error searching for local file: {e}")
        return None

# Test Cases
print("Test 1: Gachiakuta Episode 15 (Should exist)")
result = find_local_episode("Gachiakuta", 15)
print(f"Result: {result}")

print("\nTest 2: Gachiakuta Episode 99 (Should NOT exist)")
result = find_local_episode("Gachiakuta", 99)
print(f"Result: {result}")

print("\nTest 3: Non-existent Anime (Should NOT exist)")
result = find_local_episode("Fake Anime", 1)
print(f"Result: {result}")
