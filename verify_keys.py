import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Force reload
load_dotenv(override=True)

cid = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
secret = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()

print(f"🔹 Testing Credentials...")
try:
    auth_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # 1. Search (Known Good)
    res = sp.search(q="Test", limit=1)
    track_id = res['tracks']['items'][0]['id']
    print(f"✅ Search Working. Track ID: {track_id}")
    
    # 2. Audio Features (Suspect)
    print(f"🔹 Testing Audio Features for {track_id}...")
    features = sp.audio_features(track_id)
    print(f"✅ Audio Features: {features}")
    
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__} - {e}")
    if hasattr(e, 'http_response'):
         print(f"Detailed: {e.http_response.content}")
