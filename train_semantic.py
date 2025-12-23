import pandas as pd
from src.config import Config
from src.models.semantic_engine import SemanticEngine
from src.logger import get_logger

logger = get_logger(__name__)

def train_semantic():
    logger.info("🚀 Starting Semantic Indexing (Deep Learning)...")
    
    # 1. Load Data
    if not Config.RAW_DATA_PATH.exists():
        logger.error(f"❌ Data file not found at {Config.RAW_DATA_PATH}. Run collector first!")
        return

    df = pd.read_csv(Config.RAW_DATA_PATH)
    logger.info(f"📊 Loaded {len(df)} songs for indexing")
    
    # 2. Train (Encode)
    engine = SemanticEngine()
    engine.train(df)
    
    # 3. Test
    test_query = "songs for a rainy breakup"
    logger.info(f"🧪 Testing Semantic Search: '{test_query}'")
    
    results = engine.search(test_query)
    
    for i, r in enumerate(results):
        logger.info(f"   {i+1}. {r['name']} by {r['artist']} (Confidence: {r['score']:.2f})")

if __name__ == "__main__":
    train_semantic()
