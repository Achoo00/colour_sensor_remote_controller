import subprocess
import json
import shutil

class YouTubeManager:
    """
    Manager for handling YouTube playlist data fetching using yt-dlp.
    """
    def __init__(self):
        # Check if yt-dlp is available
        self.ytdlp_path = shutil.which("yt-dlp")
        if not self.ytdlp_path:
            # Fallback: try running as python module
            self.ytdlp_cmd = ["python", "-m", "yt_dlp"]
        else:
            self.ytdlp_cmd = [self.ytdlp_path]

    def get_playlist_items(self, playlist_url, max_items=10):
        """
        Fetch items from a YouTube playlist.
        
        Args:
            playlist_url (str): The URL of the playlist.
            max_items (int): Maximum number of items to fetch.
            
        Returns:
            list: List of video dictionaries.
        """
        cmd = self.ytdlp_cmd + [
            "--dump-json",
            "--flat-playlist",
            "--no-warnings",
            "--playlist-end", str(max_items),
            playlist_url
        ]
        
        try:
            # Run yt-dlp and capture output
            # encoding='utf-8' is important for non-ASCII titles
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                check=True
            )
            
            items = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        
                        # Extract best thumbnail if available, or default
                        thumbnails = data.get('thumbnails', [])
                        thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
                        
                        items.append({
                            'id': data.get('id'),
                            'title': data.get('title', 'Unknown Title'),
                            'thumbnail': thumbnail_url,
                            'url': f"https://www.youtube.com/watch?v={data.get('id')}",
                            'duration': data.get('duration')
                        })
                    except json.JSONDecodeError:
                        continue
                        
            return items
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running yt-dlp: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error fetching YouTube playlist: {e}")
            return []
