"""AniList API integration for the color controller."""
import os
import time
import json
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Warning: 'requests' module not available. API functionality will be limited.")

try:
    from utils.config_loader import load_json
except ImportError:
    # Fallback for when running from different context
    try:
        from config_loader import load_json
    except ImportError:
        # Final fallback - create a simple load_json function
        import json as json_module
        def load_json(path):
            with open(path, "r") as f:
                return json_module.load(f)

# AniList Configuration
ANILIST_USERNAME = "Ach00"  # Your AniList username
ANILIST_CACHE_FILE = "anime_progress.json"
ANILIST_CACHE_TTL = 3600  # 1 hour in seconds

# AniList GraphQL Query
ANILIST_QUERY = """
query ($username: String) {
  MediaListCollection(userName: $username, type: ANIME, status: CURRENT) {
    lists {
      entries {
        media {
          id
          title {
            romaji
            english
          }
          siteUrl
          episodes
        }
        progress
      }
    }
  }
}
"""

def fetch_anime_list(username, use_fallback=True):
    """Fetch currently watching anime from AniList API with fallback to cache."""
    if not REQUESTS_AVAILABLE:
        print("⚠️  Cannot fetch from API: 'requests' module not available.")
        if use_fallback:
            return load_anime_list_from_cache()
        return []
    
    try:
        url = "https://graphql.anilist.co"
        response = requests.post(
            url, 
            json={"query": ANILIST_QUERY, "variables": {"username": username}},
            timeout=10  # 10 second timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Parse out relevant data
        anime_list = []
        for media_list in data.get("data", {}).get("MediaListCollection", {}).get("lists", []):
            for entry in media_list.get("entries", []):
                try:
                    media = entry.get("media", {})
                    title = media.get("title", {})
                    
                    anime_data = {
                        "id": media.get("id", 0),
                        "title": title.get("english") or title.get("romaji", "Unknown Title"),
                        "url": media.get("siteUrl", ""),
                        "episodes": media.get("episodes", 0),
                        "progress": entry.get("progress", 0)
                    }
                    anime_list.append(anime_data)
                except Exception as e:
                    print(f"⚠️  Error parsing anime entry: {e}")
                    continue
                    
        if not anime_list and use_fallback:
            print("⚠️  No anime found in API response, trying cache...")
            return load_anime_list_from_cache()
            
        return anime_list
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error fetching from AniList API: {e}")
        if use_fallback:
            print("⚠️  Falling back to cached data...")
            return load_anime_list_from_cache()
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if use_fallback:
            return load_anime_list_from_cache()
        return []

def load_anime_list_from_cache():
    """Load anime list from the progress cache file."""
    try:
        if not os.path.exists(ANILIST_CACHE_FILE):
            print("⚠️  No cache file found")
            return []
            
        with open(ANILIST_CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Error: Cache file is not valid JSON")
                return []
            
        # If we have a cached list from a previous API call
        if isinstance(data, dict) and "anime_list" in data:
            anime_list = data["anime_list"]
            # Ensure all entries have required fields
            return [{
                'title': a.get('title', 'Unknown Title'),
                'progress': a.get('progress', 0),
                'episodes': a.get('episodes', a.get('total_episodes', '?')),
                'url': a.get('url', ''),
                'id': a.get('id', 0)
            } for a in anime_list]
            
        # If it's a direct list of anime (legacy format)
        if isinstance(data, list):
            return data
            
        return []
    except Exception as e:
        print(f"❌ Error loading from cache: {e}")
        return []

def load_cached_anime():
    """Load anime list from cache if it exists and is not expired."""
    if not os.path.exists(ANILIST_CACHE_FILE):
        return None
        
    with open(ANILIST_CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    if time.time() - cache["timestamp"] < ANILIST_CACHE_TTL:
        return cache["anime_list"]
    return None

def save_anime_cache(anime_list):
    """Save anime list to cache with current timestamp."""
    with open(ANILIST_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.time(),
            "anime_list": anime_list
        }, f, ensure_ascii=False, indent=2)

def update_episode_progress(anime_title, new_episode, anime_selector=None):
    """Update the episode progress for a specific anime.
    
    Args:
        anime_title (str): Title of the anime to update
        new_episode (int): The new episode number
        anime_selector (AnimeSelector, optional): The anime selector instance to update in-memory
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # First update the in-memory list if anime_selector is provided
        if anime_selector and hasattr(anime_selector, 'anime_list'):
            for anime in anime_selector.anime_list:
                if anime.get('title', '').lower() == anime_title.lower():
                    anime['progress'] = new_episode
                    print(f"📝 Updated in-memory progress for {anime_title} to episode {new_episode}")
        
        # Then update the cache file
        if not os.path.exists(ANILIST_CACHE_FILE):
            print("❌ No anime cache found")
            return False
            
        with open(ANILIST_CACHE_FILE, 'r+', encoding='utf-8') as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError:
                print("❌ Error: Invalid cache file format")
                return False
                
            # Find and update the anime in cache
            updated = False
            for anime in cache.get("anime_list", []):
                if anime.get("title", "").lower() == anime_title.lower():
                    anime["progress"] = new_episode
                    updated = True
                    break
                    
            if updated:
                # Save the updated cache
                f.seek(0)
                json.dump(cache, f, ensure_ascii=False, indent=2)
                f.truncate()
                print(f"✅ Updated {anime_title} to episode {new_episode} in cache")
                return True
            else:
                print(f"❌ Could not find anime in cache: {anime_title}")
                return False
                
    except Exception as e:
        print(f"❌ Error updating episode progress: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_currently_watching():
    """Display currently watching anime from AniList with fallback to cache."""
    try:
        # First try to get from cache
        anime_list = load_anime_list_from_cache()
        
        # If no cache or empty cache, try to fetch fresh data
        if not anime_list:
            print("ℹ️  No cached data found, fetching from AniList...")
            anime_list = fetch_anime_list(ANILIST_USERNAME, use_fallback=False)
            
            # Save the fresh data to cache
            if anime_list:
                save_anime_cache(anime_list)
        
        # Ensure all required fields exist in each anime entry
        validated_list = []
        for anime in anime_list or []:
            # Ensure all required fields have default values
            validated_anime = {
                'title': anime.get('title', 'Unknown Title'),
                'progress': anime.get('progress', 0),
                'episodes': anime.get('episodes', '?'),
                'url': anime.get('url', ''),
                'id': anime.get('id', 0)
            }
            validated_list.append(validated_anime)
        
        anime_list = validated_list  # Replace with validated list
        
        if not anime_list:
            print("❌ No anime found in cache or from API.")
            print(f"💡 Try checking if {ANILIST_CACHE_FILE} exists or check your internet connection.")
            return []
            
        print("\n📺 Currently Watching:")
        for idx, anime in enumerate(anime_list, 1):
            print(f"{idx}. {anime['title']} - {anime['progress']}/{anime['episodes']} episodes")
            
        return anime_list
        
    except Exception as e:
        print(f"❌ Error in show_currently_watching: {e}")
        import traceback
        traceback.print_exc()
        return []

