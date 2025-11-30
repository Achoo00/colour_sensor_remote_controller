"""
Handles tracking and managing anime download status.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class DownloadStatus:
    anime_title: str
    episode: int
    status: str  # 'not_downloaded', 'downloading', 'downloaded', 'error'
    progress: float = 0.0  # 0-100
    file_path: Optional[str] = None
    quality: str = '1080p'
    source: str = 'SubsPlease'  # Default trusted source

class AnimeDownloadTracker:
    def __init__(self, base_dir: str = None):
        """
        Initialize the download tracker.
        
        Args:
            base_dir: Base directory for anime downloads (default: ~/Videos/Anime)
        """
        self.base_dir = Path.home() / 'Videos' / 'Anime' if base_dir is None else Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = '.metadata.json'
        
        # In-memory cache of download status
        self.status_cache: Dict[str, DownloadStatus] = {}
        
    def _get_anime_dir(self, anime_title: str) -> Path:
        """Get the directory for a specific anime."""
        # Sanitize the title to be filesystem-safe
        safe_title = "".join(c if c.isalnum() or c in ' -_' else '_' for c in anime_title)
        return self.base_dir / safe_title
    
    def _get_metadata_path(self, anime_title: str) -> Path:
        """Get the path to the metadata file for an anime."""
        return self._get_anime_dir(anime_title) / self.metadata_file
    
    def get_status(self, anime_title: str, episode: int) -> DownloadStatus:
        """Get the download status for a specific anime episode."""
        cache_key = f"{anime_title}_{episode}"
        
        # Check cache first
        if cache_key in self.status_cache:
            return self.status_cache[cache_key]
        
        # Check filesystem
        anime_dir = self._get_anime_dir(anime_title)
        metadata_path = self._get_metadata_path(anime_title)
        
        # Default status
        status = DownloadStatus(
            anime_title=anime_title,
            episode=episode,
            status='not_downloaded'
        )
        
        # Check if metadata exists
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Check if this episode exists in metadata
                episode_key = f"S01E{episode:02d}"
                if episode_key in metadata.get('episodes', {}):
                    ep_data = metadata['episodes'][episode_key]
                    status = DownloadStatus(
                        anime_title=anime_title,
                        episode=episode,
                        status=ep_data.get('status', 'not_downloaded'),
                        progress=ep_data.get('progress', 0.0),
                        file_path=ep_data.get('file_path'),
                        quality=ep_data.get('quality', '1080p'),
                        source=ep_data.get('source', 'Unknown')
                    )
            except Exception as e:
                print(f"Error reading metadata for {anime_title}: {e}")
        
        # Update cache
        self.status_cache[cache_key] = status
        return status
    
    def update_status(self, anime_title: str, episode: int, status: str, 
                     progress: float = None, file_path: str = None) -> None:
        """Update the download status for an anime episode."""
        anime_dir = self._get_anime_dir(anime_title)
        metadata_path = self._get_metadata_path(anime_title)
        
        # Load existing metadata or create new
        metadata = {'episodes': {}}
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        
        # Update episode data
        episode_key = f"S01E{episode:02d}"
        if episode_key not in metadata['episodes']:
            metadata['episodes'][episode_key] = {}
        
        # Update fields
        if status:
            metadata['episodes'][episode_key]['status'] = status
        if progress is not None:
            metadata['episodes'][episode_key]['progress'] = progress
        if file_path:
            metadata['episodes'][episode_key]['file_path'] = file_path
        
        # Ensure anime dir exists
        anime_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Update cache
            cache_key = f"{anime_title}_{episode}"
            self.status_cache[cache_key] = DownloadStatus(
                anime_title=anime_title,
                episode=episode,
                status=status,
                progress=progress or 0.0,
                file_path=file_path
            )
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def get_anime_list(self) -> List[str]:
        """Get a list of all tracked anime."""
        if not self.base_dir.exists():
            return []
        
        anime_list = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and (item / self.metadata_file).exists():
                anime_list.append(item.name)
        
        return anime_list

# Global instance for easy access
download_tracker = AnimeDownloadTracker()
