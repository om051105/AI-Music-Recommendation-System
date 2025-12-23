import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Centralized configuration management.
    Using Pathlib for robust OS-agnostic paths.
    """
    
    # Spotify Credentials
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    # Data Settings
    # __file__ is src/config.py -> parent is src/ -> parent is root
    ROOT_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT_DIR / "data"
    
    # Paths (We use these objects directly)
    RAW_DATA_PATH = DATA_DIR / "raw" / "songs_raw.csv"
    PROCESSED_DATA_PATH = DATA_DIR / "processed" / "songs_processed.csv"
    
    # Validation
    @classmethod
    def validate(cls):
        """
        Industrial apps fail FAST.
        """
        if not cls.SPOTIFY_CLIENT_ID:
            raise ValueError("❌ CRITICAL: SPOTIFY_CLIENT_ID is missing from .env")
        if not cls.SPOTIFY_CLIENT_SECRET:
            raise ValueError("❌ CRITICAL: SPOTIFY_CLIENT_SECRET is missing from .env")

# Run validation on import
Config.validate()
