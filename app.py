import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
from src.models.recommender import ContentBasedRecommender
from src.models.semantic_engine import SemanticEngine
from src.logger import get_logger

logger = get_logger(__name__)

# Set up the page
st.set_page_config(
    page_title="AI Song Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize AI Engines
@st.cache_resource
def load_brains():
    """
    Load the AI Models into memory.
    Cached so we don't reload on every button click.
    """
    try:
        recommender = ContentBasedRecommender()
        recommender.load_model()
        
        semantic_engine = SemanticEngine()
        semantic_engine.load_from_disk()
        
        return recommender, semantic_engine
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return None, None

recommender, semantic_engine = load_brains()

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1DB954; text-align: center; margin-bottom: 1rem; }
    .chat-container { background-color: #1a1a1a; border-radius: 15px; padding: 20px; margin: 10px 0; }
    .user-message { background-color: #2d2d2d; padding: 15px; border-radius: 15px; margin: 10px 0; border-left: 4px solid #1DB954; }
    .ai-message { background-color: #363636; padding: 15px; border-radius: 15px; margin: 10px 0; border-left: 4px solid #7289da; }
    .song-card { background-color: #282828; border-radius: 10px; padding: 15px; margin: 10px 0; border: 1px solid #404040; }
    .history-item:hover { background-color: #2d2d2d; }
    .platform-buttons { display: flex; gap: 10px; margin-top: 10px; }
    .spotify-btn { background-color: #1DB954; color: white; padding: 8px 15px; border-radius: 20px; text-decoration: none; font-size: 0.9rem; }
    .youtube-btn { background-color: #FF0000; color: white; padding: 8px 15px; border-radius: 20px; text-decoration: none; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

def generate_links(song_name, artist):
    q = f"{song_name} {artist}"
    return {
        "spotify": f"https://open.spotify.com/search/{q.replace(' ', '%20')}",
        "youtube": f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"
    }

def get_recommendations(user_input):
    """
    Intelligent Router:
    1. Checks if input is a Mood ("Sad", "Workout") -> Uses Semantic Engine
    2. Checks if input is a Song Name -> Uses Recommender Engine
    """
    if not recommender or not semantic_engine:
        return "⚠️ AI Models are not loaded. Please run training scripts first!", []

    # Heuristic: Is it a mood or a song?
    # For now, we search both and see what returns better confidence
    
    # 1. Try Semantic Search first (Good for moods/descriptions)
    semantic_results = semantic_engine.search(user_input, top_k=5)
    
    # 2. Try Exact Song Match
    # We check if the user input matches a song in our DB
    exact_match_results = recommender.recommend(user_input)
    
    final_recs = []
    
    # If we found an exact song match, that takes priority
    if exact_match_results:
        response_text = f"I found the song '{user_input}'! Here are some similar tracks:"
        raw_recs = exact_match_results
    else:
        # Otherwise, treat it as a semantic query (Description/Mood)
        response_text = f"Here are some songs matching the vibe '{user_input}':"
        raw_recs = semantic_results
        
    # Format for UI
    for r in raw_recs:
        links = generate_links(r['name'], r['artist'])
        final_recs.append({
            "name": r['name'],
            "artist": r['artist'],
            "score": r.get('score', r.get('similarity_score', 0)),
            "spotify_url": links['spotify'],
            "youtube_url": links['youtube']
        })
        
    return response_text, final_recs

def display_song(song, index):
    with st.container():
        st.markdown(f'<div class="song-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{index + 1}. {song['name']}**")
            st.write(f"🎤 {song['artist']}")
            if 'score' in song:
                confidence = int(song['score'] * 100)
                st.write(f"🎯 Match: {confidence}%")
        with col2:
            st.markdown(
                f'<div class="platform-buttons">'
                f'<a href="{song["spotify_url"]}" target="_blank" class="spotify-btn">Spotify</a>'
                f'<a href="{song["youtube_url"]}" target="_blank" class="youtube-btn">YouTube</a>'
                f'</div>', unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.markdown("## 💬 AI Music Brain")
        if st.button("🆕 New Chat"):
            st.session_state.chat_history = []
            st.rerun()
            
        st.markdown("### 🎭 Quick Moods")
        if st.button("😢 Sad"): st.session_state.quick_mood = "sad songs about heartbreak"
        if st.button("⚡ Workout"): st.session_state.quick_mood = "high energy gym music"
        if st.button("🧠 Focus"): st.session_state.quick_mood = "lofi study music"

    st.markdown('<h1 class="main-header">🎵 AI Music Recommender</h1>', unsafe_allow_html=True)

    # Handle Quick Moods
    if hasattr(st.session_state, 'quick_mood'):
        user_input = st.session_state.quick_mood
        del st.session_state.quick_mood
        handle_input(user_input)

    # History
    for msg in st.session_state.chat_history:
        div_class = "user-message" if msg['type'] == 'user' else "ai-message"
        st.markdown(f'<div class="{div_class}"><b>{msg["type"].title()}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        if 'recs' in msg:
            for i, r in enumerate(msg['recs']):
                display_song(r, i)

    # Input
    user_input = st.chat_input("Describe a vibe ('sad rain') or name a song...")
    if user_input:
        handle_input(user_input)

def handle_input(text):
    st.session_state.chat_history.append({"type": "user", "content": text})
    
    with st.spinner("🧠 AI is thinking..."):
        time.sleep(0.5)
        response_text, recs = get_recommendations(text)
        
        st.session_state.chat_history.append({
            "type": "ai", 
            "content": response_text,
            "recs": recs
        })
    st.rerun()

if __name__ == "__main__":
    main()
