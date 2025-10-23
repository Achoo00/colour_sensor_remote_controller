import os
import json
import time
import requests

# === CONFIGURATION ===
USERNAME = "Ach00"  # ← change this
CACHE_FILE = "anime_progress.json"
CACHE_TTL = 3600  # 1 hour in seconds

# === GRAPHQL QUERY ===
QUERY = """
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

def fetch_anime_list(username):
    url = "https://graphql.anilist.co"
    response = requests.post(url, json={"query": QUERY, "variables": {"username": username}})
    response.raise_for_status()
    data = response.json()
    
    # Parse out relevant data
    anime_list = []
    for lst in data["data"]["MediaListCollection"]["lists"]:
        for entry in lst["entries"]:
            media = entry["media"]
            anime_list.append({
                "title": media["title"]["english"] or media["title"]["romaji"],
                "progress": entry["progress"],
                "total_episodes": media["episodes"],
                "url": media["siteUrl"]
            })
    return anime_list


def load_cached_data():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if time.time() - data["timestamp"] > CACHE_TTL:
        return None
    return data["anime_list"]


def save_cache(anime_list):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "anime_list": anime_list
        }, f, indent=2)


def main():
    anime_list = load_cached_data()
    if anime_list is None:
        print("⏳ Fetching fresh data from AniList...")
        anime_list = fetch_anime_list(USERNAME)
        save_cache(anime_list)
    else:
        print("💾 Loaded from cache.")

    print("\n🎬 Currently Watching:")
    for anime in anime_list:
        progress = anime["progress"]
        total = anime["total_episodes"] or "?"
        print(f"  - {anime['title']} ({progress}/{total})")
        print(f"    {anime['url']}")


if __name__ == "__main__":
    main()
