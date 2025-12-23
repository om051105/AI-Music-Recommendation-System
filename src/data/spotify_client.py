import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from src.config import Config
from src.logger import get_logger

logger = get_logger(__name__)

class SpotifyHandler:
    """
    Industrial-Grade Spotify API Handler.
    """
    
    def __init__(self):
        try:
            self.client_credentials_manager = SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID, 
                client_secret=Config.SPOTIFY_CLIENT_SECRET
            )
            self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
            logger.info("✅ Spotify Client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Spotify Client: {e}")
            raise

    def fetch_playlist_tracks(self, playlist_id, limit=50):
        """
        Fetches tracks from a specific playlist.
        Industrial Pattern: Batch processing.
        """
        try:
            results = self.sp.playlist_items(playlist_id, limit=limit)
            tracks_data = []
            
            for item in results['items']:
                track = item['track']
                if not track: continue
                
                # Get features for this specific track
                features = self.sp.audio_features(track['id'])[0]
                
                if features:
                    track_info = {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'id': track['id'],
                        'popularity': track['popularity'],
                        'danceability': features['danceability'],
                        'energy': features['energy'],
                        'valence': features['valence'],
                        'tempo': features['tempo'],
                        'instrumentalness': features['instrumentalness']
                    }
                    tracks_data.append(track_info)
            
            logger.info(f"📦 Batch fetched {len(tracks_data)} songs from playlist {playlist_id}")
            return tracks_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching playlist {playlist_id}. Type: {type(e).__name__}, Msg: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
