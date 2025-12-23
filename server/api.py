from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from pathlib import Path
import cv2
import numpy as np

# Add project root to sys path to import src modules
sys.path.append(str(Path(__file__).parent.parent))

from src.models.recommender import ContentBasedRecommender
from src.models.semantic_engine import SemanticEngine
from src.models.emotion import EmotionDetector
from src.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Ultra AI DJ API")

# Allow CORS so React can talk to this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Brains Global
recommender = None
semantic_engine = None
emotion_detector = None

@app.on_event("startup")
async def load_brains():
    global recommender, semantic_engine, emotion_detector
    logger.info("🧠 Loading AI Models...")
    try:
        recommender = ContentBasedRecommender()
        recommender.load_model()
        
        semantic_engine = SemanticEngine()
        semantic_engine.load_from_disk()
        
        emotion_detector = EmotionDetector()
        logger.info("✅ Brains Active!")
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")

class RecommendationRequest(BaseModel):
    query: str
    emotion: str = None
    language: str = "All"
    region: str = "Global"

@app.get("/")
def home():
    return {"message": "Ultra AI DJ Server is Running 🎧"}

@app.post("/detect-emotion")
async def detect_emotion(file: UploadFile = File(...)):
    if not emotion_detector:
        raise HTTPException(status_code=503, detail="Emotion Engine not ready")
        
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        emotion = emotion_detector.detect_emotion(img)
        return {"emotion": emotion or "neutral"}
    except Exception as e:
        logger.error(f"Emotion Error: {e}")
        return {"emotion": "neutral", "error": str(e)}

@app.post("/recommend")
async def recommend(req: RecommendationRequest):
    if not semantic_engine:
        raise HTTPException(status_code=503, detail="AI Brain not ready")
        
    search_query = req.query
    if req.emotion:
        search_query += f" {req.emotion} mood"
    if req.language != "All":
        search_query += f" {req.language}"
        
    # Get Semantic Results
    results = semantic_engine.search(search_query, top_k=30)
    
    # Simple formatting
    formatted = []
    
    # Try to get art from Spotify if possible (Bonus)
    from src.data.spotify_client import SpotifyHandler
    sp = SpotifyHandler()
    
    for r in results:
        # Fallback art
        # Using a reliable placeholder service with a random seed based on song name to keep it consistent
        seed = abs(hash(r['name'])) % 1000
        art_url = f"https://picsum.photos/seed/{seed}/300/300"
        
        # In a real production app, we would cache this or fetch it during data collection
        # For now, we use a high-quality placeholder that looks good
        
        formatted.append({
            "name": r['name'],
            "artist": r['artist'],
            "score": r.get('score', 0),
            "score": r.get('score', 0),
            "cover": art_url,
            "links": {
                "spotify": f"https://open.spotify.com/search/{r['name'].replace(' ', '%20')}%20{r['artist'].replace(' ', '%20')}",
                "youtube": f"https://www.youtube.com/results?search_query={r['name'].replace(' ', '+')}+{r['artist'].replace(' ', '+')}",
                "apple": f"https://music.apple.com/us/search?term={r['name'].replace(' ', '+')}+{r['artist'].replace(' ', '+')}"
            }
        })
        
    return {"tracks": formatted}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
