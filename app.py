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

# Hide menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
    .mood-button {
        background-color: #444;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
    }
    .mood-button:hover {
        background-color: #1DB954;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Enhanced Music Database with more songs and moods
MUSIC_DATABASE = {
    # Sad/Melancholic Songs
    "someone like you": {"artist": "Adele", "genre": "pop", "mood": "sad", "year": 2011},
    "all too well": {"artist": "Taylor Swift", "genre": "pop", "mood": "sad", "year": 2012},
    "say something": {"artist": "A Great Big World", "genre": "pop", "mood": "sad", "year": 2013},
    "hurt": {"artist": "Johnny Cash", "genre": "country", "mood": "sad", "year": 2002},
    "the sound of silence": {"artist": "Simon & Garfunkel", "genre": "folk", "mood": "sad", "year": 1964},
    "mad world": {"artist": "Gary Jules", "genre": "alternative", "mood": "sad", "year": 2001},
    
    # Happy/Upbeat Songs
    "happy": {"artist": "Pharrell Williams", "genre": "pop", "mood": "happy", "year": 2013},
    "can't stop the feeling": {"artist": "Justin Timberlake", "genre": "pop", "mood": "happy", "year": 2016},
    "good as hell": {"artist": "Lizzo", "genre": "pop", "mood": "happy", "year": 2016},
    "walking on sunshine": {"artist": "Katrina and The Waves", "genre": "pop", "mood": "happy", "year": 1985},
    
    # Energetic Songs
    "blinding lights": {"artist": "The Weeknd", "genre": "pop", "mood": "energetic", "year": 2019},
    "shape of you": {"artist": "Ed Sheeran", "genre": "pop", "mood": "energetic", "year": 2017},
    "levitating": {"artist": "Dua Lipa", "genre": "pop", "mood": "energetic", "year": 2020},
    "uptown funk": {"artist": "Mark Ronson ft. Bruno Mars", "genre": "pop", "mood": "energetic", "year": 2014},
    
    # Calm/Relaxing Songs
    "weightless": {"artist": "Marconi Union", "genre": "ambient", "mood": "calm", "year": 2011},
    "strawberry swing": {"artist": "Coldplay", "genre": "alternative", "mood": "calm", "year": 2008},
    "river flows in you": {"artist": "Yiruma", "genre": "classical", "mood": "calm", "year": 2001},
    
    # Romantic Songs
    "perfect": {"artist": "Ed Sheeran", "genre": "pop", "mood": "romantic", "year": 2017},
    "all of me": {"artist": "John Legend", "genre": "pop", "mood": "romantic", "year": 2013},
    "thinking out loud": {"artist": "Ed Sheeran", "genre": "pop", "mood": "romantic", "year": 2014},
    
    # Focus/Study Songs
    "focus music": {"artist": "Study Music", "genre": "instrumental", "mood": "focused", "year": 2020},
    "classical study": {"artist": "Mozart", "genre": "classical", "mood": "focused", "year": 1780},
}

def generate_spotify_url(song_name, artist):
    """Generate Spotify search URL"""
    query = f"{song_name} {artist}".replace(' ', '%20')
    return f"https://open.spotify.com/search/{query}"

def generate_youtube_url(song_name, artist):
    """Generate YouTube search URL"""
    query = f"{song_name} {artist}".replace(' ', '+')
    return f"https://www.youtube.com/results?search_query={query}"

def get_mood_recommendations(mood):
    """Get songs based on mood"""
    mood = mood.lower()
    mood_songs = []
    
    for song_name, song_info in MUSIC_DATABASE.items():
        if song_info["mood"] == mood:
            mood_songs.append({
                "name": song_name.title(),
                "artist": song_info["artist"],
                "genre": song_info["genre"],
                "mood": song_info["mood"],
                "year": song_info["year"],
                "spotify_url": generate_spotify_url(song_name, song_info["artist"]),
                "youtube_url": generate_youtube_url(song_name, song_info["artist"])
            })
    
    return mood_songs[:6]  # Return top 6 songs

def get_similar_songs(song_name):
    """Get similar songs based on song name"""
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
        "sad": ["sad", "cry", "tears", "lonely", "miss", "heartbreak", "broken"],
        "happy": ["happy", "sun", "smile", "dance", "party", "joy", "celebration"],
        "energetic": ["energy", "power", "strong", "fire", "burn", "pump", "workout"],
        "romantic": ["love", "heart", "kiss", "romance", "adore", "baby", "darling"],
        "calm": ["calm", "peace", "quiet", "soft", "gentle", "relax", "chill"]
    }
    
    for mood, hints in mood_hints.items():
        for hint in hints:
            if hint in name_lower:
                return mood
    return random.choice(["happy", "energetic", "calm"])

def generate_ai_response(user_input, recommendations, is_mood_based=False):
    """Generate AI-style responses based on user input"""
    user_input_lower = user_input.lower()
    
    # Mood-based responses
    if "sad" in user_input_lower or "depressed" in user_input_lower or "down" in user_input_lower:
        responses = [
            "I understand you're feeling down. Music can be a great comfort during tough times. Here are some songs that might resonate with your feelings:",
            "It's okay to feel sad sometimes. These melancholic tracks might help you process those emotions:",
            "When I'm feeling low, music always helps. Here are some beautiful sad songs that understand what you're going through:"
        ]
    elif "happy" in user_input_lower or "joy" in user_input_lower or "celebrate" in user_input_lower:
        responses = [
            "That's wonderful to hear! Let's keep those good vibes going with these uplifting tracks:",
            "Happy times call for happy music! Here are some songs to match your joyful mood:",
            "Nothing better than good music to complement a happy mood! Enjoy these upbeat recommendations:"
        ]
    elif "energetic" in user_input_lower or "energy" in user_input_lower or "workout" in user_input_lower:
        responses = [
            "Need an energy boost? These high-energy tracks will get you moving and motivated:",
            "Perfect timing for some energetic music! Here are songs that'll pump up your energy levels:",
            "Get ready to feel the power! These energetic tracks are perfect for workouts or just boosting your mood:"
        ]
    elif "calm" in user_input_lower or "relax" in user_input_lower or "peace" in user_input_lower:
        responses = [
            "Time to unwind and relax. These calming songs will help you find your peace:",
            "Perfect for a relaxing moment. Here are some serene tracks to calm your mind:",
            "Let the stress melt away with these beautifully calm and peaceful songs:"
        ]
    elif "romantic" in user_input_lower or "love" in user_input_lower:
        responses = [
            "Ah, love is in the air! Here are some romantic songs perfect for setting the mood:",
            "Nothing sets a romantic atmosphere like good music. Enjoy these love songs:",
            "For those special moments, here are some beautiful romantic tracks:"
        ]
    elif "focus" in user_input_lower or "study" in user_input_lower or "concentrate" in user_input_lower:
        responses = [
            "Time to focus! These instrumental tracks will help you concentrate and be productive:",
            "Perfect study companions! Here's some music to help you focus and get things done:",
            "Need to concentrate? These focused tracks will create the perfect environment for deep work:"
        ]
    else:
        # Generic responses for song names
        responses = [
            f"Great choice! Based on '{user_input}', here are some personalized recommendations:",
            f"I think you'll love these songs similar to '{user_input}':",
            f"Perfect taste! Here are some tracks that match the vibe of '{user_input}':"
        ]
    
    return random.choice(responses)

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
                f'<a href="{song["spotify_url"]}" target="_blank" class="spotify-btn">🎧 Open in Spotify</a>'
                f'<a href="{song["youtube_url"]}" target="_blank" class="youtube-btn">📺 Open in YouTube</a>'
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
                    st.session_state.current_search = search_item
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎭 Quick Mood Search")
        mood_col1, mood_col2 = st.columns(2)
        with mood_col1:
            if st.button("😢 Sad", use_container_width=True):
                st.session_state.quick_mood = "sad"
            if st.button("😊 Happy", use_container_width=True):
                st.session_state.quick_mood = "happy"
            if st.button("⚡ Energetic", use_container_width=True):
                st.session_state.quick_mood = "energetic"
        with mood_col2:
            if st.button("🌊 Calm", use_container_width=True):
                st.session_state.quick_mood = "calm"
            if st.button("❤️ Romantic", use_container_width=True):
                st.session_state.quick_mood = "romantic"
            if st.button("🎯 Focus", use_container_width=True):
                st.session_state.quick_mood = "focused"
        
        st.markdown("---")
        if st.button("🗑️ Delete Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.search_history = []
            st.rerun()

    # Main chat area
    st.markdown('<h1 class="main-header">🎵 AI Song Recommender</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #B3B3B3; margin-bottom: 2rem;">
        Tell me a song you like or how you're feeling, and I'll recommend perfect music for you!
    </p>
    """, unsafe_allow_html=True)
    
    # Quick mood search handler
    if hasattr(st.session_state, 'quick_mood'):
        user_input = f"I want {st.session_state.quick_mood} songs"
        del st.session_state.quick_mood
    else:
        user_input = ""
    
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
    
    # Quick examples
    st.markdown("**💡 Try saying:** 'I want sad songs', 'Play happy music', 'Energetic workout songs', or type a song name!")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Message AI Song Recommender...",
            placeholder="Examples: 'sad songs', 'happy music', 'Blinding Lights', 'romantic songs for dinner'...",
            key="user_input",
            label_visibility="collapsed",
            value=user_input
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
        with st.spinner("🎵 Analyzing your request and finding perfect songs..."):
            time.sleep(1)  # Simulate processing time
            
            # Check if it's a mood-based request
            user_input_lower = user_input.lower()
            mood_keywords = ["sad", "happy", "energetic", "calm", "romantic", "focused", "study", "workout", "chill", "relax"]
            
            is_mood_request = any(keyword in user_input_lower for keyword in mood_keywords)
            
            if is_mood_request:
                # Extract mood from request
                mood = None
                for keyword in mood_keywords:
                    if keyword in user_input_lower:
                        mood = keyword
                        break
                
                if mood:
                    if mood == "study" or mood == "workout":
                        mood = "focused" if mood == "study" else "energetic"
                    recommendations = get_mood_recommendations(mood)
                    response_text = generate_ai_response(user_input, recommendations, is_mood_based=True)
                else:
                    recommendations = get_similar_songs(user_input)
                    response_text = generate_ai_response(user_input, recommendations)
            else:
                # Treat as song name search
                recommendations = get_similar_songs(user_input)
                response_text = generate_ai_response(user_input, recommendations)
            
            # Fallback if no recommendations found
            if not recommendations:
                response_text = "I couldn't find specific recommendations. Here are some popular songs you might enjoy:"
                recommendations = get_mood_recommendations("happy")
            
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