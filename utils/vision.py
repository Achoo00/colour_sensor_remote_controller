import cv2
import numpy as np
import json
import time
from typing import List, Dict, Any, Optional

# Try to import the anilist module
try:
    from modules.anilist import show_currently_watching, load_anime_list_from_cache
    ANILIST_AVAILABLE = True
except ImportError:
    ANILIST_AVAILABLE = False

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
        
        # Optional: Visual debugging
        # cv2.imshow(f"{color_name} mask", mask)
        
        if count > 50:  # Minimum threshold
            return color_name
    return None


def load_anime_progress(use_cache: bool = True) -> List[Dict[str, Any]]:
    """Load the anime progress from AniList API or cache.
    
    Args:
        use_cache: If True, try to use cached data first before making API calls
    """
    if not ANILIST_AVAILABLE:
        print("⚠️  AniList module not available, falling back to local data")
        return _load_local_anime_data()
    
    try:
        # First try to get from cache if enabled
        if use_cache:
            cached_data = load_anime_list_from_cache()
            if cached_data:
                return cached_data
        
        # If no cache or cache disabled, fetch from API
        print("🔄 Fetching anime list from AniList...")
        anime_list = show_currently_watching() or []
        return anime_list
        
    except Exception as e:
        print(f"⚠️  Error fetching from AniList: {e}")
        # Fall back to local data if available
        return _load_local_anime_data()

def _load_local_anime_data() -> List[Dict[str, Any]]:
    """Fallback function to load anime data from local JSON file."""
    try:
        with open("anime_progress.json", "r") as f:
            data = json.load(f)
            return data.get("anime_list", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Error loading local anime data: {e}")
        return []


def draw_anime_list(frame: np.ndarray, anime_list: List[Dict[str, Any]], start_y: int = 100) -> None:
    """Draw the anime list on the frame.
    
    Args:
        frame: The frame to draw on
        anime_list: List of anime dictionaries with title, progress, and total_episodes
        start_y: Y-coordinate to start drawing the list
    """
    if not anime_list:
        return
    
    # Draw semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, start_y - 30), (400, start_y + len(anime_list) * 40 + 10), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Draw header
    cv2.putText(frame, "Currently Watching:", (10, start_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Draw each anime entry
    for i, anime in enumerate(anime_list):
        y = start_y + 30 + (i * 35)
        if y > frame.shape[0] - 30:  # Don't draw beyond frame height
            break
            
        # Draw progress bar background
        bar_width = 200
        bar_x, bar_y = 20, y + 20
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + 10), (100, 100, 100), -1)
        
        # Draw progress
        if anime.get('total_episodes', 0) > 0:
            progress = anime.get('progress', 0)
            progress_ratio = progress / anime['total_episodes']
            progress_width = int(bar_width * progress_ratio)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + 10), (0, 200, 0), -1)
        
        # Draw text
        title = anime.get('title', 'Unknown')[0:25]  # Limit title length
        total_eps = anime.get('total_episodes', 0)
        progress_text = f"{anime.get('progress', 0)}/{total_eps if total_eps > 0 else '?'}"
        
        cv2.putText(frame, f"{i+1}. {title}", (20, y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, progress_text, (bar_x + bar_width + 10, y + 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

