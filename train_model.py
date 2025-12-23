import pandas as pd
from src.config import Config
from src.models.recommender import ContentBasedRecommender
from src.logger import get_logger

logger = get_logger(__name__)

def train_and_test():
    """
    1. Load Data
    2. Train Model
    3. Test a Recommendation
    """
    logger.info("🚀 Starting Model Training...")
    
    # 1. Load Data
    if not Config.RAW_DATA_PATH.exists():
        logger.error(f"❌ Data file not found at {Config.RAW_DATA_PATH}. Run collector first!")
        return

    df = pd.read_csv(Config.RAW_DATA_PATH)
    logger.info(f"📊 Loaded {len(df)} songs for training")
    
    # 2. Train
    recommender = ContentBasedRecommender()
    recommender.train(df)
    
    # 3. Test
    test_song = df.iloc[0]['name']
    logger.info(f"🧪 Testing recommendations for: {test_song}")
    
    recs = recommender.recommend(test_song)
    
    for i, r in enumerate(recs):
        logger.info(f"   {i+1}. {r['name']} (Score: {r['similarity_score']:.2f})")

if __name__ == "__main__":
    train_and_test()
