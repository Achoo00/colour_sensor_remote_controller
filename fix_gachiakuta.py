from pathlib import Path
from core.download_tracker import download_tracker

def fix_gachiakuta():
    anime_title = "Gachiakuta"
    episode = 16
    video_path = Path(r"C:\Users\amaha\Videos\Anime\Gachiakuta\Gachiakuta - S01E16.mp4")
    
    # Ensure the file exists
    if not video_path.exists():
        print(f"Error: File not found at {video_path}")
        return
    
    # Update the download status
    download_tracker.update_status(
        anime_title=anime_title,
        episode=episode,
        status="downloaded",
        progress=100,
        file_path=str(video_path)
    )
    
    # Verify the update
    status = download_tracker.get_status(anime_title, episode)
    print(f"Updated status for {anime_title} Episode {episode}:")
    print(f"Status: {status.status}")
    print(f"File Path: {status.file_path}")
    print(f"Exists: {Path(status.file_path).exists() if status.file_path else 'N/A'}")

if __name__ == "__main__":
    fix_gachiakuta()