import pandas as pd
from src.data.spotify_client import SpotifyHandler
from src.config import Config
from src.logger import get_logger

logger = get_logger(__name__)

def run_pipeline():
    logger.info("🚀 Starting Data Ingestion Pipeline...")
    
    handler = SpotifyHandler()
    all_tracks = []
    
    # List of popular playlists to build our diverse dataset
    target_playlists = [
        "37i9dQZF1DXcBWIGoYBM5M", # Today's Top Hits
        "37i9dQZF1DX7qK8ma5wgG1", # Sad Songs
        "37i9dQZF1DX76Wlfdnj7AP", # Beast Mode (Workout)
        "37i9dQZF1DX3rxVfibe1L0", # Mood Booster
    ]
    
    for pid in target_playlists:
        logger.info(f"📥 Flexing playlist: {pid}")
        tracks = handler.fetch_playlist_tracks(pid, limit=20)
        all_tracks.extend(tracks)
    
    # Save to CSV
    df = pd.DataFrame(all_tracks)
    
    # Ensure directory exists using Pathlib
    # RAW_DATA_PATH is a Path object now
    Config.RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(Config.RAW_DATA_PATH, index=False)
    logger.info(f"✅ Data Pipeline Complete. Saved {len(df)} songs to {Config.RAW_DATA_PATH}")

if __name__ == "__main__":
    run_pipeline()
