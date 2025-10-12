import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random
import time
from datetime import datetime

# Set up the page
st.set_page_config(
    page_title="AI Song Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for chat interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-container {
        background-color: #1a1a1a;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #1DB954;
    }
    .ai-message {
        background-color: #363636;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #7289da;
    }
    .song-card {
        background-color: #282828;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #404040;
    }
    .history-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .history-item:hover {
        background-color: #2d2d2d;
    }
    .platform-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    .spotify-btn {
        background-color: #1DB954;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        text-decoration: none;
        font-size: 0.9rem;
    }
    .youtube-btn {
        background-color: #FF0000;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        text-decoration: none;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Music database
MUSIC_DATABASE = {
    "blinding lights": {"artist": "The Weeknd", "genre": "pop", "mood": "energetic", "year": 2019},
    "shape of you": {"artist": "Ed Sheeran", "genre": "pop", "mood": "happy", "year": 2017},
    "levitating": {"artist": "Dua Lipa", "genre": "pop", "mood": "energetic", "year": 2020},
    "save your tears": {"artist": "The Weeknd", "genre": "pop", "mood": "melancholic", "year": 2020},
    "flowers": {"artist": "Miley Cyrus", "genre": "pop", "mood": "empowering", "year": 2023},
    "bohemian rhapsody": {"artist": "Queen", "genre": "rock", "mood": "epic", "year": 1975},
    "sweet child o mine": {"artist": "Guns N' Roses", "genre": "rock", "mood": "energetic", "year": 1987},
    "hotel california": {"artist": "Eagles", "genre": "rock", "mood": "calm", "year": 1976},
    "god's plan": {"artist": "Drake", "genre": "hip-hop", "mood": "confident", "year": 2018},
    "sicko mode": {"artist": "Travis Scott", "genre": "hip-hop", "mood": "energetic", "year": 2018},
    "titanium": {"artist": "David Guetta", "genre": "electronic", "mood": "energetic", "year": 2011},
    "kesariya": {"artist": "Arijit Singh", "genre": "bollywood", "mood": "romantic", "year": 2022},
    "jhoome jo pathaan": {"artist": "Vishal-Shekhar", "genre": "bollywood", "mood": "energetic", "year": 2023},
}

def generate_spotify_url(song_name, artist):
    """Generate Spotify search URL"""
    query = f"{song_name} {artist}".replace(' ', '%20')
    return f"https://open.spotify.com/search/{query}"

def generate_youtube_url(song_name, artist):
    """Generate YouTube search URL"""
    query = f"{song_name} {artist}".replace(' ', '+')
    return f"https://www.youtube.com/results?search_query={query}"

def get_similar_songs(song_name):
    song_name_lower = song_name.lower()
    
    if song_name_lower in MUSIC_DATABASE:
        song_info = MUSIC_DATABASE[song_name_lower]
        genre = song_info["genre"]
        mood = song_info["mood"]
        artist = song_info["artist"]
    else:
        genre = guess_genre(song_name)
        mood = guess_mood(song_name)
        artist = "Various Artists"
    
    similar_songs = []
    
    for other_song, other_info in MUSIC_DATABASE.items():
        if other_song != song_name_lower:
            similarity_score = 0
            
            if other_info["genre"] == genre:
                similarity_score += 3
            if other_info["mood"] == mood:
                similarity_score += 2
            if artist and other_info["artist"].lower() == artist.lower():
                similarity_score += 4
                
            if similarity_score > 0:
                similar_songs.append({
                    "name": other_song.title(),
                    "artist": other_info["artist"],
                    "genre": other_info["genre"],
                    "mood": other_info["mood"],
                    "year": other_info["year"],
                    "score": similarity_score,
                    "spotify_url": generate_spotify_url(other_song, other_info["artist"]),
                    "youtube_url": generate_youtube_url(other_song, other_info["artist"])
                })
    
    similar_songs.sort(key=lambda x: x["score"], reverse=True)
    return similar_songs[:5]

def guess_genre(song_name):
    name_lower = song_name.lower()
    genre_hints = {
        "rock": ["rock", "metal", "guitar", "band"],
        "pop": ["love", "baby", "girl", "boy", "heart"],
        "hip-hop": ["flow", "drip", "money", "flex"],
        "electronic": ["beat", "bass", "drop", "digital"],
        "bollywood": ["tum", "pyar", "dil", "ishq", "jaan"]
    }
    
    for genre, hints in genre_hints.items():
        for hint in hints:
            if hint in name_lower:
                return genre
    return random.choice(["pop", "rock", "hip-hop"])

def guess_mood(song_name):
    name_lower = song_name.lower()
    mood_hints = {
        "happy": ["happy", "sun", "smile", "dance", "party"],
        "sad": ["sad", "cry", "tears", "lonely", "miss"],
        "energetic": ["energy", "power", "strong", "fire", "burn"],
        "romantic": ["love", "heart", "kiss", "romance", "adore"],
        "calm": ["calm", "peace", "quiet", "soft", "gentle"]
    }
    
    for mood, hints in mood_hints.items():
        for hint in hints:
            if hint in name_lower:
                return mood
    return random.choice(["happy", "energetic", "calm"])

def display_song_recommendation(song, index):
    with st.container():
        st.markdown(f'<div class="song-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.write(f"**{index + 1}. {song['name']}**")
            st.write(f"🎤 **Artist:** {song['artist']}")
            st.write(f"🎵 **Genre:** {song['genre'].title()}")
            st.write(f"😊 **Mood:** {song['mood'].title()}")
            st.write(f"📅 **Year:** {song['year']}")
        
        with col2:
            st.markdown(
                f'<div class="platform-buttons">'
                f'<a href="{song["spotify_url"]}" target="_blank" class="spotify-btn">🎧 Spotify</a>'
                f'<a href="{song["youtube_url"]}" target="_blank" class="youtube-btn">📺 YouTube</a>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Sidebar - Chat History
    with st.sidebar:
        st.markdown("## 💬 AI Song Recommender")
        st.markdown("---")
        
        # Search input in sidebar
        st.markdown("### 🔍 Search Chats")
        search_history = st.text_input("", placeholder="Search chat history...", key="history_search")
        
        st.markdown("---")
        st.markdown("### 📅 Today")
        
        # New Chat button
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("### 📋 Chat History")
        
        # Display search history
        filtered_history = st.session_state.search_history
        if search_history:
            filtered_history = [item for item in st.session_state.search_history 
                              if search_history.lower() in item.lower()]
        
        if not filtered_history:
            st.info("No chat history yet. Start by searching for a song!")
        else:
            for i, search_item in enumerate(filtered_history[-10:]):  # Show last 10
                if st.button(f"🎵 {search_item}", key=f"history_{i}", use_container_width=True):
                    # Re-run the search when history item is clicked
                    st.session_state.current_search = search_item
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🤖 AI Tools")
        st.markdown("**AI Text Generator**  \n**Main AI**  \n**AI Poem Generator**  \n**AI Storyteller**  \n**ChatGPT Alternative**  \n**GPT Chat**")
        
        st.markdown("---")
        st.markdown("### ⚙️ More")
        st.markdown("**AI Code**  \n**More**")
        
        st.markdown("---")
        if st.button("🗑️ Delete Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.search_history = []
            st.rerun()

    # Main chat area
    st.markdown('<h1 class="main-header">🎵 AI Song Recommender</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #B3B3B3; margin-bottom: 2rem;">
        Tell me a song you like and I'll give you personalized recommendations
    </p>
    """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["type"] == "user":
            st.markdown(f'''
            <div class="user-message">
                <strong>You:</strong> {message["content"]}
                <br><small style="color: #888;">{message["timestamp"]}</small>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="ai-message">
                <strong>AI Recommender:</strong> {message["content"]}
                <br><small style="color: #888;">{message["timestamp"]}</small>
            </div>
            ''', unsafe_allow_html=True)
            
            # Display recommendations if it's a response with songs
            if "recommendations" in message:
                for i, song in enumerate(message["recommendations"]):
                    display_song_recommendation(song, i)
    
    # Chat input at bottom
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Message AI Song Recommender...",
            placeholder="Enter a song you like (e.g., Blinding Lights, Shape of You, Bohemian Rhapsody)...",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Handle user input
    if send_button and user_input:
        # Add user message to history
        user_message = {
            "type": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.chat_history.append(user_message)
        
        # Add to search history
        if user_input not in st.session_state.search_history:
            st.session_state.search_history.append(user_input)
        
        # Generate AI response
        with st.spinner("🎵 Analyzing your music taste..."):
            time.sleep(1)  # Simulate processing time
            
            recommendations = get_similar_songs(user_input)
            
            if recommendations:
                response_text = f"Great choice! Based on **{user_input}**, here are personalized recommendations:"
            else:
                response_text = f"I analyzed **{user_input}**. Here are some music recommendations you might enjoy:"
                # Fallback recommendations
                recommendations = get_similar_songs(random.choice(list(MUSIC_DATABASE.keys())))
            
            ai_message = {
                "type": "ai",
                "content": response_text,
                "timestamp": datetime.now().strftime("%H:%M"),
                "recommendations": recommendations
            }
            st.session_state.chat_history.append(ai_message)
        
        st.rerun()

if __name__ == "__main__":
    main()
    # Hide menu and footer completely
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)