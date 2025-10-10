import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from config.constants import AUDIO_FEATURES
from config.mood_mappings import MOOD_TO_FEATURES, MOOD_GENRES

class MusicRecommender:
    def __init__(self, spotify_client):
        self.sp = spotify_client
        self.scaler = StandardScaler()
    
    def get_song_recommendations(self, base_track_data, n_recommendations=5):
        """Get recommendations based on song similarity"""
        try:
            # Get Spotify recommendations
            recommendations = self.sp.sp.recommendations(
                seed_tracks=[base_track_data['id']],
                limit=20
            )
            
            # Extract features for recommended tracks
            recommended_tracks = []
            for track in recommendations['tracks']:
                track_features = self.sp.get_track_features(track['id'])
                if track_features:
                    recommended_tracks.append(track_features)
            
            if len(recommended_tracks) < n_recommendations:
                return recommended_tracks
            
            # Use ML to find most similar tracks
            base_features = np.array([[base_track_data[feature] for feature in AUDIO_FEATURES]])
            rec_features = np.array([[track[feature] for feature in AUDIO_FEATURES] for track in recommended_tracks])
            
            # Normalize features
            all_features = np.vstack([base_features, rec_features])
            normalized_features = self.scaler.fit_transform(all_features)
            
            base_normalized = normalized_features[0].reshape(1, -1)
            rec_normalized = normalized_features[1:]
            
            # Calculate similarity
            similarities = cosine_similarity(base_normalized, rec_normalized)[0]
            
            # Get top recommendations
            top_indices = np.argsort(similarities)[::-1][:n_recommendations]
            final_recommendations = [recommended_tracks[i] for i in top_indices]
            
            return final_recommendations
            
        except Exception as e:
            raise Exception(f"Error in song recommendations: {e}")
    
    def get_mood_recommendations(self, mood, n_recommendations=5):
        """Get recommendations based on mood"""
        try:
            if mood not in MOOD_TO_FEATURES:
                raise ValueError(f"Unsupported mood: {mood}")
            
            mood_config = MOOD_TO_FEATURES[mood]
            genres = MOOD_GENRES.get(mood, ['pop'])
            
            recommendations = self.sp.sp.recommendations(
                seed_genres=genres[:2],
                limit=n_recommendations,
                **{k: v for k, v in mood_config.items() if k.startswith('target_')}
            )
            
            recommended_tracks = []
            for track in recommendations['tracks']:
                track_features = self.sp.get_track_features(track['id'])
                if track_features:
                    recommended_tracks.append(track_features)
            
            return recommended_tracks
            
        except Exception as e:
            raise Exception(f"Error in mood recommendations: {e}")
    
    def get_artist_recommendations(self, artist_id, n_recommendations=5):
        """Get recommendations based on artist"""
        try:
            recommendations = self.sp.sp.recommendations(
                seed_artists=[artist_id],
                limit=n_recommendations
            )
            
            recommended_tracks = []
            for track in recommendations['tracks']:
                track_features = self.sp.get_track_features(track['id'])
                if track_features:
                    recommended_tracks.append(track_features)
            
            return recommended_tracks
            
        except Exception as e:
            raise Exception(f"Error in artist recommendations: {e}")