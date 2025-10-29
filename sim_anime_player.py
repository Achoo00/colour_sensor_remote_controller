"""Handles anime playback, URL generation, and episode management."""
import webbrowser
import os
import json
import requests
from urllib.parse import quote, urlencode
from typing import Optional, Dict, Any

# Configuration
DEFAULT_STREAMING_SERVICE = "wcoflix"  # Options: wcoflix, 9anime, gogoanime
STREAMING_SERVICES = {
    "wcoflix": {
        "base_url": "https://wcoflix.tv",
        "episode_format": "{base_url}/{name}-episode-{episode}",
        "search_url": "https://wcoflix.tv/search"
    },
    "9anime": {
        "base_url": "https://9anime.to",
        "search_url": "https://9anime.to/search"
    },
    "gogoanime": {
        "base_url": "https://gogoanime.pe",
        "search_url": "https://gogoanime.pe/search.html"
    }
}

class AnimePlayer:
    """Handles anime playback and URL generation."""
    
    def __init__(self, service: str = None):
        """Initialize the anime player with the specified streaming service.
        
        Args:
            service (str, optional): The streaming service to use. Defaults to DEFAULT_STREAMING_SERVICE.
        """
        self.service = service or DEFAULT_STREAMING_SERVICE
        if self.service not in STREAMING_SERVICES:
            print(f"⚠️  Unknown service '{service}'. Defaulting to '{DEFAULT_STREAMING_SERVICE}'.")
            self.service = DEFAULT_STREAMING_SERVICE
    
    def generate_anime_url(self, anime_name: str, episode: Optional[int] = None) -> str:
        """Generate a streaming URL for the specified anime and episode.
        
        Args:
            anime_name: The name of the anime
            episode: The episode number. If None, returns the anime's main page.
            
        Returns:
            The generated URL
        """
        try:
            service_config = STREAMING_SERVICES[self.service]
            
            # Create a URL-friendly version of the anime name
            url_name = (
                anime_name.lower()
                .replace(' ', '-')
                .replace(':', '')
                .replace("'", '')
                .replace(',', '')
                .replace('!', '')
                .replace('?', '')
            )
            
            if self.service == "wcoflix":
                if episode is not None:
                    return service_config["episode_format"].format(
                        base_url=service_config["base_url"],
                        name=url_name,
                        episode=episode
                    )
                return f"{service_config['base_url']}/{url_name}"
                
            elif self.service in ["9anime", "gogoanime"]:
                # For these services, we'll just open the search page with the anime name
                params = {"keyword": anime_name}
                return f"{service_config['search_url']}?{urlencode(params)}"
                
            return f"{service_config.get('base_url', '')}"
            
        except Exception as e:
            print(f"❌ Error generating URL: {e}")
            return ""
    
    def open_anime_episode(self, anime_name: str, episode: Optional[int] = None) -> str:
        """Open the specified anime episode in the default web browser.
        
        Args:
            anime_name: The name of the anime
            episode: The episode number. If None, opens the anime's main page.
            
        Returns:
            The URL that was opened
        """
        try:
            url = self.generate_anime_url(anime_name, episode)
            if not url:
                print("❌ Failed to generate URL for anime.")
                return ""
                
            print(f"🎬 Opening: {url}")
            webbrowser.open(url)
            return url
            
        except Exception as e:
            print(f"❌ Error opening anime: {e}")
            return ""
    
    def get_next_episode_url(self, anime_name: str, current_episode: int) -> str:
        """Get the URL for the next episode of an anime.
        
        Args:
            anime_name: The name of the anime
            current_episode: The current episode number
            
        Returns:
            URL for the next episode
        """
        return self.generate_anime_url(anime_name, current_episode + 1)
    
    def play_anime(self, anime_data: Dict[str, Any]) -> bool:
        """Play an anime based on its data.
        
        Args:
            anime_data: Dictionary containing anime info (must have 'title' and 'progress')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not anime_data:
                print("❌ No anime data provided")
                return False
                
            title = anime_data.get('title')
            if not title:
                print("❌ No title found in anime data")
                return False
                
            progress = int(anime_data.get('progress', 0))
            next_episode = progress + 1
            
            print(f"\n🎮 Now Playing: {title}")
            print(f"📺 Next Episode: {next_episode}")
            
            # Open the next episode
            url = self.open_anime_episode(title, next_episode)
            if not url:
                print("⚠️  Could not determine next episode URL")
                return False
                
            print(f"🔗 {url}")
            return True
            
        except Exception as e:
            print(f"❌ Error playing anime: {e}")
            return False

# Create a default instance for easy import
default_player = AnimePlayer()

# Module-level functions for backward compatibility
def generate_anime_url(anime_name: str, episode: Optional[int] = None) -> str:
    return default_player.generate_anime_url(anime_name, episode)

def open_anime_episode(anime_name: str, episode: Optional[int] = None) -> str:
    return default_player.open_anime_episode(anime_name, episode)

def get_next_episode(anime_name: str, current_episode: int) -> str:
    return default_player.get_next_episode_url(anime_name, current_episode)

def play_anime(anime_data: Dict[str, Any]) -> bool:
    return default_player.play_anime(anime_data)
