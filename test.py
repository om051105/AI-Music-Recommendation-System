import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# USE YOUR ACTUAL NEW CREDENTIALS:
client_id = "e23101908564425828ea85ce98f58f9"  # Your actual NEW Client ID
client_secret = "b43c125ef73444a6a8e9f5257762abb9"  # Your actual NEW Client Secret

print("🔍 Testing NEW Spotify credentials...")
print(f"Client ID: {client_id}")

try:
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, 
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    results = sp.search(q="Blinding Lights", type="track", limit=1)
    print("✅ SUCCESS! Connected to Spotify API")
    print(f"Found: {results['tracks']['items'][0]['name']} by {results['tracks']['items'][0]['artists'][0]['name']}")
    
except Exception as e:
    print(f"❌ FAILED: {e}")