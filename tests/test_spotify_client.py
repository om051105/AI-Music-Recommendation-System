import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

# Test your credentials directly
client_id = "your_NEW_client_id_here"
client_secret = "your_NEW_client_secret_here"

try:
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, 
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Test search
    results = sp.search(q='Blinding Lights', type='track', limit=1)
    st.success("✅ Spotify connection successful!")
    st.write(f"Found: {results['tracks']['items'][0]['name']}")
    
except Exception as e:
    st.error(f"❌ Failed: {e}")