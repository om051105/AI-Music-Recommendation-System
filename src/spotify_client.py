import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.sp = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Spotify client with credentials"""
        try:
            if not self.client_id or not self.client_secret:
                st.error("Spotify credentials not found. Please check your .env file.")
                return None
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            return self.sp
        except Exception as e:
            st.error(f"Error initializing Spotify client: {e}")
            return None
    
    def search_track(self, query, limit=5):
        """Search for tracks by query"""
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            for item in results['tracks']['items']:
                track_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'album': item['album']['name'],
                    'release_date': item['album']['release_date'],
                    'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'preview_url': item['preview_url'],
                    'external_url': item['external_urls']['spotify']
                }
                tracks.append(track_data)
            return tracks
        except Exception as e:
            st.error(f"Error searching for track: {e}")
            return []
    
    def get_track_features(self, track_id):
        """Get audio features for a specific track"""
        try:
            features = self.sp.audio_features(track_id)[0]
            track_info = self.sp.track(track_id)
            
            track_data = {
                'id': track_id,
                'name': track_info['name'],
                'artist': track_info['artists'][0]['name'],
                'album': track_info['album']['name'],
                'popularity': track_info['popularity'],
                'preview_url': track_info['preview_url'],
                'external_url': track_info['external_urls']['spotify'],
                'image': track_info['album']['images'][0]['url'] if track_info['album']['images'] else None,
                'release_date': track_info['album']['release_date']
            }
            
            # Add audio features
            if features:
                audio_features = [
                    'danceability', 'energy', 'valence', 'acousticness',
                    'instrumentalness', 'liveness', 'speechiness', 'tempo',
                    'key', 'loudness', 'mode', 'time_signature'
                ]
                for feature in audio_features:
                    track_data[feature] = features.get(feature, 0)
            
            return track_data
        except Exception as e:
            st.error(f"Error getting track features: {e}")
            return None
    
    def get_artist_id(self, artist_name):
        """Get artist ID from name"""
        try:
            results = self.sp.search(q=artist_name, type='artist', limit=1)
            if results['artists']['items']:
                return results['artists']['items'][0]['id']
            return None
        except Exception as e:
            st.error(f"Error getting artist ID: {e}")
            return None