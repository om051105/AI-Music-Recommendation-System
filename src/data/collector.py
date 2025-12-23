import pandas as pd
import numpy as np
import random
from src.data.spotify_client import SpotifyHandler
from src.config import Config
from src.logger import get_logger

logger = get_logger(__name__)

def generate_synthetic_features(query):
    """
    If Spotify blocks 'audio_features' (403 Error), we generate plausible
    values based on the search query that found the song.
    This creates a 'Silver' dataset (Noisy but useful) instead of 'Gold' (Perfect).
    """
    q_lower = query.lower()
    
    # Defaults (Middle of road)
    valence = 0.5
    energy = 0.5
    dance = 0.5
    tempo = 120
    
    # Heuristics
    if 'sad' in q_lower or 'calm' in q_lower:
        valence = random.uniform(0.1, 0.4)
        energy = random.uniform(0.1, 0.4)
        dance = random.uniform(0.3, 0.5)
        tempo = random.uniform(70, 100)
    elif 'happy' in q_lower or 'pop' in q_lower:
        valence = random.uniform(0.6, 0.9)
        energy = random.uniform(0.6, 0.9)
        dance = random.uniform(0.6, 0.9)
        tempo = random.uniform(100, 130)
    elif 'rock' in q_lower or 'workout' in q_lower or 'hip-hop' in q_lower:
        valence = random.uniform(0.4, 0.7)
        energy = random.uniform(0.8, 1.0)
        dance = random.uniform(0.5, 0.8)
        tempo = random.uniform(120, 150)
        
    return {
        'danceability': dance,
        'energy': energy,
        'valence': valence,
        'tempo': tempo,
        'acousticness': random.random(),
        'instrumentalness': random.random() if 'study' in q_lower else random.uniform(0, 0.3)
    }

def run_pipeline():
    logger.info("🚀 Starting Data Ingestion Pipeline (Resilient Mode)...")
    
    handler = SpotifyHandler()
    all_tracks = []
    
    queries = [
        "genre:pop year:2023",
        "genre:rock",
        "genre:hip-hop",
        "genre:jazz",
        "mood:sad",
        "mood:happy",
        "workout",
        "study music"
    ]
    
    for q in queries:
        logger.info(f"🔍 Searching for: {q}")
        try:
            results = handler.sp.search(q=q, type='track', limit=40)
            
            for item in results['tracks']['items']:
                try:
                    # Generic Metadata
                    track_info = {
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'id': item['id'],
                        'popularity': item['popularity'],
                        'search_tag': q
                    }
                    
                    # Try fetch Real Features
                    features = None
                    try:
                        features_list = handler.sp.audio_features(item['id'])
                        if features_list:
                            features = features_list[0]
                    except Exception:
                        pass # Expecting 403 here
                    
                    if features:
                        # Use Real
                        track_info.update({
                            'danceability': features['danceability'],
                            'energy': features['energy'],
                            'valence': features['valence'],
                            'tempo': features['tempo'],
                            'instrumentalness': features['instrumentalness'],
                            'is_synthetic': False
                        })
                    else:
                        # Fallback to Synthetic
                        syn = generate_synthetic_features(q)
                        track_info.update(syn)
                        track_info['is_synthetic'] = True
                        
                    all_tracks.append(track_info)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Search failed for {q}: {e}")

    df = pd.DataFrame(all_tracks)
    if not df.empty:
        df = df.drop_duplicates(subset=['id'])
        Config.RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(Config.RAW_DATA_PATH, index=False)
        
        # Stats
        real_count = len(df[df['is_synthetic'] == False])
        syn_count = len(df[df['is_synthetic'] == True])
        logger.info(f"✅ Pipeline Complete. Total: {len(df)}")
        logger.info(f"   Real Features: {real_count}")
        logger.info(f"   Synthetic Features: {syn_count} (Generated due to API blocks)")
        
    else:
        logger.error("❌ No data collected!")

if __name__ == "__main__":
    run_pipeline()
