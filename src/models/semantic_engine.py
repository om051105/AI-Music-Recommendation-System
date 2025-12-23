from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from src.logger import get_logger
from src.config import Config
import joblib

logger = get_logger(__name__)

class SemanticEngine:
    """
    Phase 3: Deep Learning Engine.
    Uses a 'Transformer' model to understand text meaning.
    """
    
    def __init__(self):
        # We use a lightweight but powerful pre-trained model
        self.model_name = 'all-MiniLM-L6-v2'
        self.encoder = None
        self.song_embeddings = None
        self.data = None
        self.save_path = Config.DATA_DIR / "models" / "semantic_index.pkl"
        
    def load_model(self):
        """Load the massive Deep Learning model into memory"""
        if self.encoder is None:
            logger.info(f"🤖 Loading Deep Learning Model: {self.model_name}...")
            self.encoder = SentenceTransformer(self.model_name)
            logger.info("✅ Model Loaded!")

    def train(self, data: pd.DataFrame):
        """
        'Training' here means encoding all our songs into vectors.
        We combine Name + Artist + Search Tags to create a 'Description'.
        """
        self.load_model()
        self.data = data.reset_index(drop=True)
        
        # Create a rich description for each song
        # "Shape of You by Ed Sheeran [Pop, Happy]"
        descriptions = self.data.apply(
            lambda x: f"{x['name']} by {x['artist']} {x.get('search_tag', '')}", 
            axis=1
        ).tolist()
        
        logger.info(f"🧠 Encoding {len(descriptions)} songs. This involves heavy math...")
        self.song_embeddings = self.encoder.encode(descriptions, show_progress_bar=True)
        
        self.save()
        logger.info("✅ Semantic Index Built!")

    def search(self, query: str, top_k=5):
        """
        Deep Learning Search.
        1. Convert user query "sad heartbreak" to numbers.
        2. Find songs with similar meaning numbers.
        """
        if self.song_embeddings is None:
            self.load_from_disk()
            
        # Encode user query
        query_vector = self.encoder.encode([query])[0]
        
        # Calculate Cosine Similarity (Dot product for normalized vectors)
        # We use numpy for fast matrix math
        # Scores = dot(query, all_songs)
        scores = np.dot(self.song_embeddings, query_vector)
        
        # Get top K indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            song = self.data.iloc[idx]
            results.append({
                'name': song['name'],
                'artist': song['artist'],
                'score': float(scores[idx]),
                'tags': song.get('search_tag', '')
            })
            
        return results

    def save(self):
        joblib.dump({
            'embeddings': self.song_embeddings,
            'data': self.data
        }, self.save_path)

    def load_from_disk(self):
        if not self.save_path.exists():
            raise FileNotFoundError("Run training first!")
            
        self.load_model()
        saved = joblib.load(self.save_path)
        self.song_embeddings = saved['embeddings']
        self.data = saved['data']
