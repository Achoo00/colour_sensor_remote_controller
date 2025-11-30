import feedparser
import urllib.parse

class NyaaManager:
    """
    Manager for searching Nyaa.si RSS feeds.
    """
    def __init__(self, base_url="https://nyaa.si/"):
        self.base_url = base_url

    def search_anime(self, title, episode, quality="1080p", trusted_only=True):
        """
        Search for a specific anime episode.
        
        Args:
            title (str): Anime title.
            episode (int or str): Episode number.
            quality (str): Resolution (e.g., "1080p").
            trusted_only (bool): Whether to filter for trusted uploaders.
            
        Returns:
            list: List of dictionaries containing 'title', 'link' (magnet), 'seeders'.
        """
        # Construct search query
        # c=1_2 is Anime - Translated
        # f=2 is Trusted Only (if trusted_only is True)
        
        # Clean title for search (remove special chars if needed)
        clean_title = title.replace(":", "").replace("-", " ")
        
        # Pad episode number (e.g., 5 -> 05)
        ep_str = str(episode).zfill(2)
        
        query = f"{clean_title} {ep_str} {quality}"
        encoded_query = urllib.parse.quote(query)
        
        filter_code = "2" if trusted_only else "0"
        rss_url = f"{self.base_url}?page=rss&q={encoded_query}&c=1_2&f={filter_code}"
        
        print(f"🔍 Searching Nyaa: {query}")
        
        try:
            feed = feedparser.parse(rss_url)
            results = []
            
            for entry in feed.entries:
                # Nyaa RSS usually puts seeders/leechers in nyaa_seeders/nyaa_leechers
                # but feedparser might put them in different fields depending on version
                seeders = 0
                if hasattr(entry, 'nyaa_seeders'):
                    seeders = int(entry.nyaa_seeders)
                
                results.append({
                    'title': entry.title,
                    'link': entry.link, # This is usually the magnet link or .torrent download
                    'seeders': seeders,
                    'size': entry.nyaa_size if hasattr(entry, 'nyaa_size') else "Unknown"
                })
            
            # Sort by seeders desc
            results.sort(key=lambda x: x['seeders'], reverse=True)
            return results
            
        except Exception as e:
            print(f"❌ Error searching Nyaa: {e}")
            return []
