import streamlit as st
import pandas as pd
import numpy as np
import cv2 
import time
from datetime import datetime
from src.models.recommender import ContentBasedRecommender
from src.models.semantic_engine import SemanticEngine
from src.models.emotion import EmotionDetector
from src.logger import get_logger

logger = get_logger(__name__)

# Set up the page
st.set_page_config(
    page_title="Ultra AI DJ",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize AI Engines
@st.cache_resource
def load_brains():
    """
    Load all 3 Brains: Math, Language, and Vision.
    """
    try:
        recommender = ContentBasedRecommender()
        recommender.load_model()
        
        semantic_engine = SemanticEngine()
        semantic_engine.load_from_disk()
        
        emotion_detector = EmotionDetector()
        
        return recommender, semantic_engine, emotion_detector
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return None, None, None

recommender, semantic_engine, emotion_detector = load_brains()

# Custom CSS (Enhanced)
st.markdown("""
<style>
    .main-header { 
        font-size: 3rem; 
        background: -webkit-linear-gradient(#1DB954, #1ed760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center; 
        font-weight: 800;
        margin-bottom: 1rem; 
    }
    .user-message { background-color: #2e2e2e; padding: 15px; border-radius: 15px; margin: 10px 0; border-right: 4px solid #1DB954; text-align: right; }
    .ai-message { background-color: #1a1a1a; padding: 20px; border-radius: 15px; margin: 10px 0; border-left: 4px solid #1DB954; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .song-card { background-color: #212121; border-radius: 12px; padding: 15px; margin: 10px 0; border: 1px solid #333; transition: transform 0.2s; }
    .song-card:hover { transform: scale(1.02); border-color: #1DB954; }
    .spotify-btn { background-color: #1DB954; color: white; padding: 8px 15px; border-radius: 20px; text-decoration: none; font-weight: bold; }
    .youtube-btn { background-color: #FF0000; color: white; padding: 8px 15px; border-radius: 20px; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def generate_links(song_name, artist):
    q = f"{song_name} {artist}"
    return {
        "spotify": f"https://open.spotify.com/search/{q.replace(' ', '%20')}",
        "youtube": f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"
    }

def therapeutic_response(emotion, user_input):
    """Generates a caring, human-like response based on emotion."""
    if emotion == "sad":
        return [
            "I noticed you're looking a bit down. I've curated a playlist that feels like a warm hug. 🌧️💜",
            "It's okay not to be okay. Let music speak what words can't. Here are some tracks to help you heal.",
            "I see pain in those eyes. Let's process it together with these beautiful, melancholic masterpieces."
        ]
    elif emotion == "happy":
        return [
            "Your smile is contagious! Let's amplify that joy with some absolute bangers! 🎉",
            "You're glowing! Locking in this vibe with these high-energy tracks!",
            "Love the energy! Here is the perfect soundtrack for your winning mood."
        ]
    elif emotion == "angry":
        return [
            "I sense some fire. Let's channel that rage into power. 🎸🔥",
            "Vent it out. These aggressive tracks will help you release that steam.",
            "Don't hold it in. Scream it out with these intense selections."
        ]
    else:
        # Default based on text
        return [
            f"I hear you. Diving deep into the '{user_input}' universe for you.",
            f"Got it. check out these gems inspired by '{user_input}'.",
            f"Excellent taste. Here is a curated selection just for you."
        ]

def get_recommendations(user_input, emotion=None, language="All", region="Global"):
    """
    The Master Algorithm.
    Combines: User Text + Facial Emotion + Language Filters + Diversity Logic.
    """
    if not recommender:
        return "⚠️ Brains initializing... please wait.", []

    # 1. Update Query based on Filters
    search_query = user_input
    if emotion:
        search_query += f" {emotion} mood"
    if language != "All":
        search_query += f" {language} song"
    
    # 2. Semantic Search (Main Results)
    # Fetch MORE than needed so we can filter/shuffle
    raw_results = semantic_engine.search(search_query, top_k=50)
    
    # 3. Apply Diversity / "Explore-Exploit"
    # We want mostly what they asked for, but some surprises
    
    final_recs = []
    seen_songs = set()
    
    # Add top 20 matches (Exploit)
    for r in raw_results[:20]:
        if r['name'] not in seen_songs:
            final_recs.append(r)
            seen_songs.add(r['name'])
            
    # Add 5 random "Palette Cleansers" from Math Model if possible
    # (Simplified here to just shuffle the tail of semantic results)
    import random
    surprise_pool = raw_results[20:]
    random.shuffle(surprise_pool)
    for r in surprise_pool[:5]:
         if r['name'] not in seen_songs:
            final_recs.append(r)
            seen_songs.add(r['name'])

    # Format
    display_recs = []
    for r in final_recs:
        links = generate_links(r['name'], r['artist'])
        display_recs.append({
            "name": r['name'],
            "artist": r['artist'],
            "score": r.get('score', 0),
            "tags": r.get('tags', ''),
            "spotify_url": links['spotify'],
            "youtube_url": links['youtube']
        })
        
    return display_recs

def display_song(song, index):
    with st.container():
        st.markdown(f'<div class="song-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{index + 1}. {song['name']}**")
            st.write(f"🎤 {song['artist']}")
            # st.caption(f"Tags: {song['tags']}")
        with col2:
            st.markdown(f'<a href="{song["spotify_url"]}" target="_blank" class="spotify-btn">Spotify</a>', unsafe_allow_html=True)
            st.write("") # Spacer
            st.markdown(f'<a href="{song["youtube_url"]}" target="_blank" class="youtube-btn">YouTube</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # --- SIDEBAR CONFIG ---
    with st.sidebar:
        st.markdown("## ⚙️ DJ Settings")
        
        # 1. Filters
        st.markdown("### 🌍 Region & Language")
        language = st.selectbox("Language", ["All", "Hindi", "Punjabi", "English", "Korean (K-Pop)", "Spanish"])
        region = st.selectbox("Region", ["Global", "India", "USA", "UK"])
        
        st.markdown("---")
        st.markdown("### 📸 Face Scanner")
        mode = st.radio("Camera Mode", ["Snapshot (Fast)", "Real-Time (Experimental)"])
        
        captured_emotion = None
        
        if mode == "Snapshot (Fast)":
            img_file = st.camera_input("Scan your vibe")
            if img_file is not None:
                bytes_data = img_file.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                with st.spinner("🧠 Reading your face..."):
                    captured_emotion = emotion_detector.detect_emotion(cv2_img)
                    if captured_emotion:
                        st.success(f"Detected: {captured_emotion.upper()} 😲")
                        
        else:
            # Real-Time Mode Logic
            from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
            
            st.warning("Running Face AI on video stream... Click 'Start' below.")
            
            # Simple processor to check emotion every 30 frames
            class EmotionProcessor(VideoTransformerBase):
                def __init__(self):
                    self.frame_count = 0
                    
                def transform(self, frame):
                    self.frame_count += 1
                    img = frame.to_ndarray(format="bgr24")
                    
                    # Only analyze every 30th frame to prevent lag
                    if self.frame_count % 30 == 0:
                        try:
                           # We can't easily return data to Streamlit main thread from here
                           # But we can draw on the frame
                           pass
                        except:
                            pass
                            
                    return img

            ctx = webrtc_streamer(key="example", video_processor_factory=EmotionProcessor)
            st.info("Real-time mode is viewing-only. For music updates, please use Snapshot mode for now as it is more stable.")
        
        st.markdown("---")
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()

    # --- MAIN PAGE ---
    st.markdown('<h1 class="main-header">🎧 Ultra AI DJ</h1>', unsafe_allow_html=True)
    
    # Processing Logic
    user_input = st.chat_input("How are you feeling?")
    
    # Trigger 1: Camera Photo Taken
    if captured_emotion and 'last_emotion' not in st.session_state:
        st.session_state.last_emotion = captured_emotion # Prevent loops
        handle_input(f"I am feeling {captured_emotion}", emotion=captured_emotion, lang=language, reg=region)
    
    # Trigger 2: Text Input
    if user_input:
        handle_input(user_input, emotion=None, lang=language, reg=region)

    # Display History
    for msg in st.session_state.chat_history:
        div_class = "user-message" if msg['type'] == 'user' else "ai-message"
        st.markdown(f'<div class="{div_class}"><b>{msg["type"]}</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
        
        if 'recs' in msg:
            st.markdown("###  🎹 Curated Playlist")
            for i, r in enumerate(msg['recs']):
                display_song(r, i)

def handle_input(text, emotion=None, lang="All", reg="Global"):
    # Add User Message
    st.session_state.chat_history.append({"type": "User", "content": text})
    
    import random
    
    # AI Logic
    with st.spinner(f"🧠 DJ is mixing (Filter: {lang})..."):
        # 1. Generate Message
        responses = therapeutic_response(emotion, text)
        ai_msg = random.choice(responses)
        
        # 2. Get Songs
        recs = get_recommendations(text, emotion=emotion, language=lang, region=reg)
        
        # Add AI Message
        st.session_state.chat_history.append({
            "type": "AI DJ", 
            "content": ai_msg,
            "recs": recs
        })
    st.rerun()

if __name__ == "__main__":
    main()
