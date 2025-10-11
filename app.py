import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random

# Set up the page
st.set_page_config(
    page_title="AI Music Recommendation System - DEMO",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 2rem;
    }
    .song-card {
        background-color: #282828;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #1DB954;
    }
    .demo-mode {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1DB954;
    }
</style>
""", unsafe_allow_html=True)

# Expanded music database - covers multiple genres
MUSIC_DATABASE = {
    # Pop
    "blinding lights": {"artist": "The Weeknd", "genre": "pop", "mood": "energetic"},
    "shape of you": {"artist": "Ed Sheeran", "genre": "pop", "mood": "happy"},
    "levitating": {"artist": "Dua Lipa", "genre": "pop", "mood": "energetic"},
    "save your tears": {"artist": "The Weeknd", "genre": "pop", "mood": "melancholic"},
    "flowers": {"artist": "Miley Cyrus", "genre": "pop", "mood": "empowering"},
    
    # Rock
    "bohemian rhapsody": {"artist": "Queen", "genre": "rock", "mood": "epic"},
    "sweet child o mine": {"artist": "Guns N' Roses", "genre": "rock", "mood": "energetic"},
    "hotel california": {"artist": "Eagles", "genre": "rock", "mood": "calm"},
    "stairway to heaven": {"artist": "Led Zeppelin", "genre": "rock", "mood": "epic"},
    
    # Hip-Hop/Rap
    "god's plan": {"artist": "Drake", "genre": "hip-hop", "mood": "confident"},
    "sicko mode": {"artist": "Travis Scott", "genre": "hip-hop", "mood": "energetic"},
    "hotline bling": {"artist": "Drake", "genre": "hip-hop", "mood": "chill"},
    
    # Electronic/Dance
    "titanium": {"artist": "David Guetta", "genre": "electronic", "mood": "energetic"},
    "wake me up": {"artist": "Avicii", "genre": "electronic", "mood": "uplifting"},
    "closer": {"artist": "The Chainsmokers", "genre": "electronic", "mood": "nostalgic"},
    
    # R&B
    "blinding lights": {"artist": "The Weeknd", "genre": "r&b", "mood": "nostalgic"},
    "adore you": {"artist": "Harry Styles", "genre": "pop", "mood": "romantic"},
    
    # Bollywood (if you want Indian music)
    "kesariya": {"artist": "Arijit Singh", "genre": "bollywood", "mood": "romantic"},
    "jhoome jo pathaan": {"artist": "Vishal-Shekhar", "genre": "bollywood", "mood": "energetic"},
}

# Recommendation logic based on genre, mood, and artist similarity
def get_similar_songs(song_name, artist=None):
    song_name_lower = song_name.lower()
    
    # If song is in our database, use its attributes
    if song_name_lower in MUSIC_DATABASE:
        song_info = MUSIC_DATABASE[song_name_lower]
        genre = song_info["genre"]
        mood = song_info["mood"]
        artist = song_info["artist"]
    else:
        # For unknown songs, guess based on common patterns
        genre = guess_genre(song_name)
        mood = guess_mood(song_name)
        artist = "Various Artists"
    
    # Get recommendations based on genre and mood
    similar_songs = []
    
    for other_song, other_info in MUSIC_DATABASE.items():
        if other_song != song_name_lower:
            similarity_score = 0
            
            # Genre match
            if other_info["genre"] == genre:
                similarity_score += 3
            elif genre in other_info["genre"] or other_info["genre"] in genre:
                similarity_score += 1
                
            # Mood match
            if other_info["mood"] == mood:
                similarity_score += 2
                
            # Artist match (if same artist)
            if artist and other_info["artist"].lower() == artist.lower():
                similarity_score += 4
                
            if similarity_score > 0:
                similar_songs.append({
                    "name": other_song.title(),
                    "artist": other_info["artist"],
                    "genre": other_info["genre"],
                    "mood": other_info["mood"],
                    "score": similarity_score,
                    "reason": generate_reason(song_name, other_song.title(), genre, mood, artist, other_info["artist"])
                })
    
    # Sort by similarity score and return top 5
    similar_songs.sort(key=lambda x: x["score"], reverse=True)
    return similar_songs[:6]

def guess_genre(song_name):
    """Guess genre based on song name patterns"""
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
    """Guess mood based on song name patterns"""
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

def generate_reason(original_song, recommended_song, genre, mood, artist, rec_artist):
    reasons = [
        f"Similar {genre} genre and {mood} mood",
        f"Both have {mood} emotional vibe",
        f"Fans of {artist} also enjoy {rec_artist}",
        f"Matching {genre} musical style",
        f"Similar tempo and energy level",
        f"Complementary {mood} atmosphere",
        f"Popular among fans of {genre} music"
    ]
    return random.choice(reasons)

def get_mock_features():
    return {
        'danceability': np.random.uniform(0.3, 0.95),
        'energy': np.random.uniform(0.4, 0.98),
        'valence': np.random.uniform(0.2, 0.9),
        'acousticness': np.random.uniform(0.1, 0.8)
    }

def display_demo_track(track_info, features=None):
    with st.container():
        st.markdown('<div class="song-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.write("🎵")  # Placeholder for album art
            
        with col2:
            st.write(f"**{track_info['name']}**")
            st.write(f"by **{track_info['artist']}**")
            if 'reason' in track_info:
                st.write(f"*{track_info['reason']}*")
            
            if features:
                cols = st.columns(4)
                with cols[0]:
                    st.metric("💃", f"{features['danceability']:.2f}")
                with cols[1]:
                    st.metric("⚡", f"{features['energy']:.2f}")
                with cols[2]:
                    st.metric("😊", f"{features['valence']:.2f}")
                with cols[3]:
                    st.metric("🎻", f"{features['acousticness']:.2f}")
        
        with col3:
            st.write("🔊 Audio preview would play here")
            st.markdown('<a href="#" class="spotify-link">🎧 Open in Spotify</a>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🎵 AI Music Recommendation System - DEMO</h1>', unsafe_allow_html=True)
    
    # Demo mode notice
    with st.container():
        st.markdown('<div class="demo-mode">', unsafe_allow_html=True)
        st.warning("""
        🔧 **DEMO MODE ACTIVE**
        
        This is a demonstration of how the AI Music Recommendation System works. 
        In the full version with Spotify API access, you would get:
        - Real-time song search from millions of tracks
        - Actual audio previews
        - Live Spotify integration
        - Personalized recommendations based on your listening history
        
        *To enable full functionality, Spotify API credentials need to be configured.*
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.title("🎯 Navigation")
    app_mode = st.sidebar.radio("Choose Mode", ["By Song 🎵", "By Mood 😊", "By Artist 👤"])
    
    if app_mode == "By Song 🎵":
        st.subheader("🎵 Discover Similar Songs (Demo)")
        
        song_query = st.text_input(
            "Search for any song:",
            placeholder="Enter any song name...",
            help="Try: Blinding Lights, Sweet Child O Mine, God's Plan, Kesariya, or any song you like!"
        )
        
        if song_query:
            with st.spinner("🔍 Analyzing song and finding recommendations..."):
                # Get recommendations for ANY song
                recommendations = get_similar_songs(song_query)
                
                if recommendations:
                    st.success(f"🎯 Found {len(recommendations)} recommendations for: **{song_query.title()}**")
                    
                    # Show "selected" track
                    st.subheader("You searched for:")
                    display_demo_track(
                        {"name": song_query.title(), "artist": "Various Artists"}, 
                        get_mock_features()
                    )
                    
                    # Show recommendations
                    st.subheader("AI Recommendations:")
                    for rec_track in recommendations:
                        display_demo_track(rec_track, get_mock_features())
                        
                else:
                    st.info("💡 Try searching for popular songs like: 'Blinding Lights', 'Sweet Child O Mine', 'God's Plan', 'Kesariya'")
    
    elif app_mode == "By Mood 😊":
        st.subheader("😊 Music for Your Mood (Demo)")
        
        mood = st.selectbox("Select your mood:", 
                           ["Happy 😊", "Sad 😢", "Energetic ⚡", "Calm 🌊", "Romantic ❤️"])
        
        if st.button("Get Mood-Based Recommendations"):
            with st.spinner(f"Finding perfect {mood} songs..."):
                # Filter songs by mood
                mood_key = mood.split(" ")[0].lower()
                mood_tracks = []
                
                for song, info in MUSIC_DATABASE.items():
                    if info["mood"] == mood_key:
                        mood_tracks.append({
                            "name": song.title(),
                            "artist": info["artist"],
                            "reason": f"Perfect for {mood} mood"
                        })
                
                if mood_tracks:
                    st.success(f"🎵 Found {len(mood_tracks)} {mood} songs")
                    for track in mood_tracks[:6]:  # Show top 6
                        display_demo_track(track, get_mock_features())
    
    elif app_mode == "By Artist 👤":
        st.subheader("👤 Discover Similar Artists (Demo)")
        
        artist_query = st.text_input("Enter an artist name:", placeholder="e.g., The Weeknd, Drake, Arijit Singh")
        
        if artist_query and st.button("Get Similar Artists"):
            with st.spinner(f"Finding artists similar to {artist_query}..."):
                # Find songs by similar artists
                similar_tracks = []
                
                for song, info in MUSIC_DATABASE.items():
                    if artist_query.lower() in info["artist"].lower():
                        # This artist's songs
                        similar_tracks.append({
                            "name": song.title(),
                            "artist": info["artist"],
                            "reason": f"Direct match - same artist"
                        })
                    elif any(word in info["artist"].lower() for word in artist_query.lower().split()):
                        # Similar artist names
                        similar_tracks.append({
                            "name": song.title(),
                            "artist": info["artist"], 
                            "reason": f"Artist name similarity"
                        })
                
                if similar_tracks:
                    st.success(f"🎸 Found {len(similar_tracks)} related tracks")
                    for track in similar_tracks[:6]:
                        display_demo_track(track, get_mock_features())
                else:
                    st.info("💡 Try: The Weeknd, Drake, Ed Sheeran, Queen, Arijit Singh")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #B3B3B3;'>"
        "🎵 AI Music Recommendation System • Demo Version • "
        "Search ANY song to get AI-powered recommendations</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()