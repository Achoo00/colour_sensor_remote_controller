"""Anime selector for the color controller."""
try:
    from .anilist import show_currently_watching
except ImportError:
    # Fallback if anilist module is not available
    def show_currently_watching():
        return []

class AnimeSelector:
    """Handles anime selection from the user's currently watching list."""
    
    def __init__(self):
        """Initialize the anime selector with the user's currently watching list."""
        self.anime_list = []
        self.selected_index = 0
        self.load_anime_list()
        
    def load_anime_list(self):
        """Load the user's currently watching anime list with fallback to sample data."""
        try:
            self.anime_list = show_currently_watching() or []
            
            # If no anime found, use sample data
            if not self.anime_list:
                print("⚠️  No anime found in your currently watching list. Using sample data.")
                self.anime_list = [
                    {
                        'title': 'Sample Anime 1',
                        'progress': 3,
                        'episodes': 12,
                        'url': 'https://example.com/anime1',
                        'id': 1
                    },
                    {
                        'title': 'Sample Anime 2',
                        'progress': 5,
                        'episodes': 24,
                        'url': 'https://example.com/anime2',
                        'id': 2
                    }
                ]
                
        except Exception as e:
            print(f"❌ Error loading anime list: {e}")
            # Fallback to sample data on error
            print("⚠️  Using sample data due to error.")
            self.anime_list = [
                {
                    'title': 'Sample Anime 1',
                    'progress': 3,
                    'episodes': 12,
                    'url': 'https://example.com/anime1',
                    'id': 1
                }
            ]
    
    def move_selection(self, direction):
        """Move the selection up or down in the list."""
        if not self.anime_list:
            print("⚠️  No anime available to select.")
            return False

        try:
            # First, print debug info
            print(f"\n📋 Total anime in list: {len(self.anime_list)}")
            print(f"📌 Current index: {self.selected_index}")
            
            # Validate current index first
            if self.selected_index < 0 or self.selected_index >= len(self.anime_list):
                print("⚠️  Current index out of bounds, resetting to 0")
                self.selected_index = 0
            
            # Move selection - use modulo to ensure we wrap around correctly
            if direction == "up":
                self.selected_index = (self.selected_index - 1) % len(self.anime_list)
            else:  # down
                self.selected_index = (self.selected_index + 1) % len(self.anime_list)
            
            print(f"🔄 New index: {self.selected_index}")
            self.display_selection_with_context()
            return True
            
        except Exception as e:
            print(f"❌ Error moving selection: {e}")
            import traceback
            traceback.print_exc()
            # Reset to first item on error
            self.selected_index = 0
            return False
    
    def get_current_anime(self):
        """Get the currently selected anime with validation."""
        try:
            if not self.anime_list:
                print("⚠️  No anime available.")
                return None
                
            if self.selected_index < 0 or self.selected_index >= len(self.anime_list):
                print(f"⚠️  Invalid selection index: {self.selected_index}")
                self.selected_index = 0  # Reset to first item if invalid
                
            return self.anime_list[self.selected_index]
            
        except Exception as e:
            print(f"❌ Error getting current anime: {e}")
            return None
    
    def display_selection_with_context(self):
        """Display the list with the current selection highlighted."""
        if not self.anime_list:
            print("⚠️  No anime available to display.")
            return

        print("\n" + "=" * 60)
        for i, anime in enumerate(self.anime_list):
            title = anime.get('title', 'Unknown Title')
            if i == self.selected_index:
                print(f"➡️  {i+1}. {title} ⬅️")
            else:
                print(f"    {i+1}. {title}")
        print("=" * 60)
        print("🔴 Move Down  |  🟡 Move Up  |  Red+Yellow: Select")

    def display_current_selection(self):
        """Display the currently selected anime with validation."""
        try:
            if not self.anime_list:
                print("⚠️  No anime available to display.")
                return
            
            # Don't modify selected_index here, just validate it
            if self.selected_index < 0 or self.selected_index >= len(self.anime_list):
                print(f"⚠️  Invalid selection index: {self.selected_index}")
                return
            
            anime = self.anime_list[self.selected_index]
            title = anime.get('title', 'Unknown Title')
            progress = anime.get('progress', 0)
            episodes = anime.get('episodes', anime.get('total_episodes', '?'))
            url = anime.get('url', 'https://anilist.co')
            
            print("\n" + "=" * 60)
            print(f"📺 {title}")
            print(f"📊 Progress: {progress}/{episodes} episodes")
            if url and url != 'https://anilist.co':  # Only show URL if it's not the default
                print(f"🔗 {url}")
            print("=" * 60)
            print("🔴 Move Down  |  🟡 Move Up  |  Red+Yellow: Select")
            
        except Exception as e:
            print(f"❌ Error displaying anime information: {e}")
            print("💡 The anime data might be incomplete or corrupted.")

