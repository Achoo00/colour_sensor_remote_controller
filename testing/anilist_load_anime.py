import json
import webbrowser
import re
import os

def get_next_episode_url(bookmark_url, current_episode):
    print(f"🔢 Current episode from progress: {current_episode}")
    print(f"🔗 Bookmark URL: {bookmark_url}")

    # Remove trailing slashes or query params
    bookmark_url = bookmark_url.split("?")[0].rstrip("/")

    # Determine base and path
    base_match = re.match(r"(https?://[^/]+)/(.*)", bookmark_url)
    if not base_match:
        print("❌ Invalid bookmark URL:", bookmark_url)
        return None

    base_url = base_match.group(1) + "/"
    path = base_match.group(2)

    # Remove existing episode pattern if present
    path = re.sub(r"-episode-\d+", "", path)

    # Handle suffix
    if "english-dubbed" in path:
        suffix = "-english-dubbed"
        path = path.replace("-english-dubbed", "")
    elif "english-subbed" in path:
        suffix = "-english-subbed"
        path = path.replace("-english-subbed", "")
    else:
        suffix = "-english-subbed"

    next_episode = current_episode + 1
    print(f"🔄 Calculating next episode: {current_episode} + 1 = {next_episode}")

    next_url = f"{base_url}{path}-episode-{next_episode}{suffix}"
    print(f"🔍 Generated URL: {next_url}")

    return next_url


def open_next_episode(anime_name):
    json_path = os.path.join(os.getcwd(), "anime_progress.json")
    print(f"📂 Loading JSON: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(json.dumps(data, indent=2))

    for anime in data["anime_list"]:
        if anime_name.lower() in anime["title"].lower():
            print(f"🎯 Matched: {anime['title']}")
            print(f"📘 Using progress={anime['progress']}")

            bookmark_url = anime.get("bookmark_url") or f"https://www.wcoflix.tv/{anime_name.lower().replace(' ', '-')}-english-subbed"
            next_url = get_next_episode_url(bookmark_url, anime["progress"])

            if next_url:
                print(f"🎬 Opening next episode for {anime['title']}: {next_url}")
                webbrowser.open(next_url)
            else:
                print(f"❌ Could not generate next episode URL for {anime_name}")
            return

    print(f"❌ Anime '{anime_name}' not found in cache.")


if __name__ == "__main__":
    open_next_episode("Gachiakuta")
