from modules.anilist import fetch_anime_list, load_anime_list_from_cache, ANILIST_USERNAME

class AniListManager:
    """
    Manager for handling AniList data fetching and caching.
    Wraps the existing logic from modules.anilist.
    """
    def __init__(self, username=ANILIST_USERNAME):
        self.username = username

    def get_watching_list(self, force_refresh=False):
        """
        Get the list of currently watching anime.
        
        Args:
            force_refresh (bool): If True, forces a fetch from the API.
                                  If False, tries cache first (logic handled by modules.anilist).
        
        Returns:
            list: List of anime dictionaries.
        """
        # The existing fetch_anime_list handles cache fallback if use_fallback=True.
        # If force_refresh is False, we want to prefer cache if valid.
        # However, fetch_anime_list logic is: try API, if fail -> fallback.
        # It doesn't explicitly "prefer" cache unless we call load_cached_anime first.
        
        if not force_refresh:
            # Try loading from cache first to be fast
            cached = load_anime_list_from_cache()
            if cached:
                return cached
        
        # If no cache or forced refresh, fetch from API
        return fetch_anime_list(self.username, use_fallback=True)
