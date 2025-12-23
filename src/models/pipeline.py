from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
import pandas as pd
from src.logger import get_logger

logger = get_logger(__name__)

class MusicPipeline:
    """
    Industrial ML Pipeline.
    
    Why: In 'notebook code', people just hack dataframes. 
    In Industrial code, we define a strict 'Recipe' (Pipeline) that guarantees
    new data is treated EXACTLY like training data.
    """
    
    @staticmethod
    def get_pipeline():
        """
        Returns a Scikit-Learn Pipeline for numeric feature engineering.
        """
        # The specific audio features we care about (The "DNA" of the song)
        numeric_features = [
            'danceability', 'energy', 'valence', 'tempo', 
            'acousticness', 'instrumentalness', 'popularity'
        ]
        
        # The Recipe:
        # 1. Imputer: If a value is missing (NaN), convert it to the Mean (Average).
        # 2. Scaler: Squeeze all numbers (like Tempo 150 and Energy 0.8) into the same range (approx -1 to 1).
        #    This prevents "Loudness" or "Tempo" from dominating the math just because they are big numbers.
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])
        
        # We only apply this to the numeric columns. We ignore Name/Artist for the math part.
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features)
            ])
            
        return preprocessor
