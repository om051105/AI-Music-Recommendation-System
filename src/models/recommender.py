import pandas as pd
import numpy as np
import joblib
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
from src.config import Config
from src.models.pipeline import MusicPipeline
from src.logger import get_logger

logger = get_logger(__name__)

class ContentBasedRecommender:
    """
    The Brain (Phase 2).
    
    Uses 'Vector Space' logic. 
    Every song is a point in 7-dimensional space (Dance, Energy, etc.).
    We find the nearest points to recommend similar music.
    """
    
    def __init__(self):
        self.model = NearestNeighbors(metric='cosine', algorithm='brute')
        self.pipeline = MusicPipeline.get_pipeline()
        self.data = None
        self.features_matrix = None
        
        # Where to save the "Brain" (Serialized Model)
        self.model_path = Config.DATA_DIR / "models" / "recommender.pkl"
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

    def train(self, data: pd.DataFrame):
        """
        Training the model.
        1. Learn the scaling (Fit Pipeline)
        2. Transform data into vectors
        3. Fit the NearestNeighbor index
        """
        logger.info("🧠 Training Recommender Model...")
        self.data = data.reset_index(drop=True)
        
        # Transform: Raw Data -> Normalized Vectors
        self.features_matrix = self.pipeline.fit_transform(self.data)
        
        # Fit: Create the spatial index
        self.model.fit(self.features_matrix)
        
        # Save: Persistence
        self.save_model()
        logger.info("✅ Model Trained and Saved")

    def recommend(self, song_name: str, n_recommendations=5):
        """
        The magic function.
        1. Find the song in our database.
        2. Get its vector.
        3. Ask model: "Who are the nearest neighbors?"
        """
        if self.data is None:
            self.load_model()
            
        # Case insensitive search
        song_idx = self.data.index[self.data['name'].str.lower() == song_name.lower()].tolist()
        
        if not song_idx:
            logger.warning(f"⚠️ Song not found: {song_name}")
            return []
            
        song_idx = song_idx[0]
        
        # Get the vector for this song
        song_vector = self.features_matrix[song_idx].reshape(1, -1)
        
        # Find neighbors (distance, index)
        distances, indices = self.model.kneighbors(song_vector, n_neighbors=n_recommendations+1)
        
        # Format results
        recommendations = []
        for i in range(1, len(indices[0])): # Skip 0 because it's the song itself
            idx = indices[0][i]
            dist = distances[0][i]
            song = self.data.iloc[idx]
            
            recommendations.append({
                'name': song['name'],
                'artist': song['artist'],
                'similarity_score': 1 - dist, # Convert distance to similarity %
                'spotify_id': song.get('id', '')
            })
            
        return recommendations

    def save_model(self):
        """Save the fitted model and data to disk"""
        state = {
            'pipeline': self.pipeline,
            'model': self.model,
            'data': self.data,
            'features': self.features_matrix
        }
        joblib.dump(state, self.model_path)
        
    def load_model(self):
        """Load the model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError("Brain not found! Run training first.")
            
        logger.info("loading model from disk...")
        state = joblib.load(self.model_path)
        self.pipeline = state['pipeline']
        self.model = state['model']
        self.data = state['data']
        self.features_matrix = state['features']
