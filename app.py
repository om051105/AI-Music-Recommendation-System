import streamlit as st
import pandas as pd
import numpy as np
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the page for web deployment
st.set_page_config(
    page_title="AI Music Recommendation System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better web appearance
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    .song-card {
        background-color: #282828;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 6px solid #1DB954;
        transition: transform 0.2s;
    }
    .song-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
    }
    .recommendation-section {
        background-color: #181818;
        padding: 25px;
        border-radius: 15px;
        margin-top: 25px;
        border: 1px solid #333;
    }
    .stButton button {
        background-color: #1DB954;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1ed760;
        transform: scale(1.05);
    }
    .spotify-link {
        color: #1DB954 !important;
        text-decoration: none;
        font-weight: bold;
    }
    .spotify-link:hover {
        color: #1ed760 !important;
        text-decoration: underline;
    }
    .feature-metric {
        background: rgba(29, 185, 84, 0.1);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 5px;
        text-align: center;
    }
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .sub-header {
            font-size: 1.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Spotify client with better error handling
@st.cache_resource
def init_spotify_client():
    # Try multiple ways to get credentials for web deployment
    client_id = (os.getenv('SPOTIFY_CLIENT_ID') or 
                st.secrets.get('SPOTIFY_CLIENT_ID') or 
                st.secrets.get('SPOTIFY_CLIENT_ID', ''))
    
    client_secret = (os.getenv('SPOTIFY_CLIENT_SECRET') or 
                    st.secrets.get('SPOTIFY_CLIENT_SECRET') or 
                    st.secrets.get('SPOTIFY_CLIENT_SECRET', ''))
    
    if not client_id or not client_secret:
        st.error("""
        🔧 **Spotify API Credentials Required**
        
        To use this music recommendation system, we need Spotify API credentials.
        If you're the admin, please set up the credentials in the deployment environment.
        
        For users: The app will be fully functional once credentials are configured.
        """)
        return None
    
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)
        
        # Test connection
        sp.search(q='test', type='track', limit=1)
        return sp
    except Exception as e:
        st.error(f"❌ Failed to connect to Spotify API: {str(e)}")
        return None

# Enhanced track features function
def get_track_features(sp, track_id):
    try:
        features = sp.audio_features(track_id)[0]
        track_info = sp.track(track_id)
        artist_info = sp.artist(track_info['artists'][0]['id'])
        
        # Extract comprehensive features for better recommendations
        feature_keys = ['danceability', 'energy', 'valence', 'acousticness', 
                       'instrumentalness', 'liveness', 'speechiness', 'tempo']
        
        track_data = {
            'id': track_id,
            'name': track_info['name'],
            'artist': track_info['artists'][0]['name'],
            'artist_id': track_info['artists'][0]['id'],
            'album': track_info['album']['name'],
            'popularity': track_info['popularity'],
            'preview_url': track_info['preview_url'],
            'external_url': track_info['external_urls']['spotify'],
            'image': track_info['album']['images'][0]['url'] if track_info['album']['images'] else None,
            'release_date': track_info['album']['release_date'],
            'genres': artist_info.get('genres', [])
        }
        
        # Add audio features
        for key in feature_keys:
            track_data[key] = features[key] if features else 0
            
        return track_data
    except Exception as e:
        st.error(f"Error getting track features: {e}")
        return None

# Enhanced search function
def search_track(sp, query):
    try:
        results = sp.search(q=query, type='track', limit=8)  # Increased limit for better UX
        tracks = []
        for item in results['tracks']['items']:
            tracks.append({
                'id': item['id'],
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'album': item['album']['name'],
                'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                'preview_url': item['preview_url'],
                'popularity': item['popularity']
            })
        return tracks
    except Exception as e:
        st.error(f"Error searching for track: {e}")
        return []

# Enhanced recommendation function with better ML
def get_recommendations(sp, base_track_data, n_recommendations=6):
    try:
        # Get similar tracks using Spotify's API with multiple seeds
        recommendations = sp.recommendations(
            seed_tracks=[base_track_data['id']],
            seed_artists=[base_track_data.get('artist_id', '')],
            limit=25
        )
        
        # Extract features for recommended tracks
        recommended_tracks = []
        for track in recommendations['tracks']:
            track_features = get_track_features(sp, track['id'])
            if track_features and track_features['id'] != base_track_data['id']:
                recommended_tracks.append(track_features)
        
        # Use ML to find the most similar ones
        if len(recommended_tracks) >= n_recommendations:
            # Prepare feature matrix with weighted features
            feature_keys = ['danceability', 'energy', 'valence', 'acousticness', 
                           'instrumentalness', 'liveness', 'speechiness', 'popularity']
            
            # Normalize features
            base_features = np.array([[base_track_data.get(key, 0) for key in feature_keys]])
            rec_features = np.array([[track.get(key, 0) for key in feature_keys] for track in recommended_tracks])
            
            # Apply weights (popularity has lower weight)
            weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.3])
            base_features = base_features * weights
            rec_features = rec_features * weights
            
            # Calculate cosine similarity
            similarities = cosine_similarity(base_features, rec_features)[0]
            
            # Get top N recommendations
            top_indices = np.argsort(similarities)[::-1][:n_recommendations]
            final_recommendations = [recommended_tracks[i] for i in top_indices]
            
            return final_recommendations
        else:
            return recommended_tracks[:n_recommendations]
            
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return []

# Enhanced mood-based recommendations
def get_recommendations_by_mood(sp, mood, n_recommendations=6):
    try:
        # Enhanced mood mappings
        mood_configs = {
            'happy': {
                'target_valence': 0.8, 'target_energy': 0.7, 'target_danceability': 0.7,
                'min_valence': 0.6, 'seed_genres': ['pop', 'dance', 'disco']
            },
            'sad': {
                'target_valence': 0.2, 'target_energy': 0.3, 'target_danceability': 0.3,
                'max_valence': 0.4, 'seed_genres': ['acoustic', 'sad', 'piano']
            },
            'energetic': {
                'target_valence': 0.7, 'target_energy': 0.9, 'target_danceability': 0.8,
                'min_energy': 0.7, 'seed_genres': ['rock', 'electronic', 'work-out']
            },
            'calm': {
                'target_valence': 0.5, 'target_energy': 0.2, 'target_danceability': 0.3,
                'max_energy': 0.4, 'seed_genres': ['ambient', 'chill', 'classical']
            },
            'focused': {
                'target_valence': 0.5, 'target_energy': 0.5, 'target_instrumentalness': 0.7,
                'min_instrumentalness': 0.4, 'seed_genres': ['instrumental', 'classical', 'jazz']
            }
        }
        
        if mood not in mood_configs:
            st.error(f"Mood '{mood}' not recognized")
            return []
            
        config = mood_configs[mood]
        
        # Get recommendations based on mood
        recommendations = sp.recommendations(
            seed_genres=config['seed_genres'],
            limit=n_recommendations,
            **{k: v for k, v in config.items() if k.startswith('target_')}
        )
        
        # Extract track info
        recommended_tracks = []
        for track in recommendations['tracks']:
            track_features = get_track_features(sp, track['id'])
            if track_features:
                recommended_tracks.append(track_features)
                
        return recommended_tracks
        
    except Exception as e:
        st.error(f"Error getting mood-based recommendations: {e}")
        return []

# Enhanced artist-based recommendations
def get_recommendations_by_artist(sp, artist_name, n_recommendations=6):
    try:
        # Search for the artist
        results = sp.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']:
            st.error(f"Artist '{artist_name}' not found")
            return []
            
        artist_id = results['artists']['items'][0]['id']
        artist_info = sp.artist(artist_id)
        
        # Get top tracks by the artist
        top_tracks = sp.artist_top_tracks(artist_id)
        seed_track = top_tracks['tracks'][0]['id'] if top_tracks['tracks'] else None
        
        # Get recommendations based on artist
        recommendations = sp.recommendations(
            seed_artists=[artist_id],
            seed_tracks=[seed_track] if seed_track else [],
            limit=n_recommendations
        )
        
        # Extract track info
        recommended_tracks = []
        for track in recommendations['tracks']:
            track_features = get_track_features(sp, track['id'])
            if track_features:
                recommended_tracks.append(track_features)
                
        return recommended_tracks
        
    except Exception as e:
        st.error(f"Error getting artist-based recommendations: {e}")
        return []

# Display track with enhanced UI
def display_track(track, show_features=False):
    with st.container():
        st.markdown('<div class="song-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            if track['image']:
                st.image(track['image'], width=100)
            else:
                st.write("🎵 No Image")
        
        with col2:
            st.write(f"**🎵 {track['name']}**")
            st.write(f"**👤 {track['artist']}**")
            st.write(f"**💿 {track.get('album', 'N/A')}**")
            
            # Popularity indicator
            popularity = track.get('popularity', 0)
            st.progress(popularity/100, text=f"Popularity: {popularity}/100")
            
            if show_features and 'danceability' in track:
                cols = st.columns(4)
                features = [
                    ('💃', 'danceability', track['danceability']),
                    ('⚡', 'energy', track['energy']),
                    ('😊', 'valence', track['valence']),
                    ('🎻', 'acoustic', track['acousticness'])
                ]
                for idx, (emoji, name, value) in enumerate(features):
                    with cols[idx]:
                        st.metric(emoji, f"{value:.2f}")
        
        with col3:
            if track['preview_url']:
                st.audio(track['preview_url'])
            else:
                st.write("🔇 No Preview")
            
            if track['external_url']:
                st.markdown(
                    f'<a href="{track["external_url"]}" target="_blank" class="spotify-link">🎧 Open in Spotify</a>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main app function
def main():
    # Header with better design
    st.markdown('<h1 class="main-header">🎵 AI Music Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; font-size: 1.3rem; color: #B3B3B3; margin-bottom: 2rem;">
        Discover your next favorite songs using advanced AI and Spotify's music intelligence
    </p>
    """, unsafe_allow_html=True)
    
    # Initialize Spotify client
    with st.spinner("Connecting to Spotify..."):
        sp = init_spotify_client()
    
    if not sp:
        st.warning("""
        ## 🚧 Setup Required
        
        This app needs Spotify API credentials to work. Here's how to set it up:
        
        1. **For Users**: Contact the app administrator to configure Spotify API credentials
        2. **For Admins**: 
           - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
           - Create an app and get Client ID & Secret
           - Add them to your deployment environment variables or Streamlit secrets
        
        The app will automatically detect when credentials are available.
        """)
        return
    
    # Sidebar with enhanced navigation
    with st.sidebar:
        st.markdown("## 🎯 Navigation")
        app_mode = st.radio(
            "Choose Recommendation Type",
            ["By Song 🎵", "By Mood 😊", "By Artist 👤"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This AI-powered system recommends music based on:
        - **Audio features** (danceability, energy, mood)
        - **Machine learning** similarity analysis
        - **Spotify's** extensive music database
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Features")
        st.markdown("""
        - 🎵 Song-based recommendations
        - 😊 Mood-based matching
        - 👤 Artist similarity
        - 🔊 Audio previews
        - 📊 Feature analysis
        """)
    
    # Main content area
    if "By Song 🎵" in app_mode:
        st.markdown('<h2 class="sub-header">🎵 Discover Similar Songs</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            song_query = st.text_input(
                "Enter a song you like:",
                placeholder="e.g., Blinding Lights by The Weeknd",
                help="Enter song title and artist for better results"
            )
        with col2:
            num_recommendations = st.slider("Number of recommendations", 3, 10, 6)
        
        if song_query:
            with st.spinner("🔍 Searching Spotify..."):
                tracks = search_track(sp, song_query)
                
            if tracks:
                st.markdown(f"### 📋 Found {len(tracks)} songs:")
                selected_track = None
                
                # Display tracks in a grid
                cols = st.columns(2)
                for i, track in enumerate(tracks):
                    with cols[i % 2]:
                        with st.container():
                            st.markdown("---")
                            col_img, col_info = st.columns([1, 2])
                            with col_img:
                                if track['image']:
                                    st.image(track['image'], width=60)
                            with col_info:
                                st.write(f"**{track['name']}**")
                                st.write(f"*{track['artist']}*")
                                
                            if st.button(f"Select →", key=f"select_{i}", use_container_width=True):
                                selected_track = track
                
                if selected_track:
                    st.markdown("---")
                    with st.spinner("🎧 Analyzing audio features and finding recommendations..."):
                        base_track = get_track_features(sp, selected_track['id'])
                        
                        if base_track:
                            # Display selected track
                            st.markdown("### 🎯 You selected:")
                            display_track(base_track, show_features=True)
                            
                            # Get and display recommendations
                            recommendations = get_recommendations(sp, base_track, num_recommendations)
                            
                            if recommendations:
                                st.markdown(f"### 💫 Recommended Songs ({len(recommendations)} found):")
                                for rec in recommendations:
                                    display_track(rec, show_features=True)
                            else:
                                st.warning("No recommendations found. Try a different song.")
    
    elif "By Mood 😊" in app_mode:
        st.markdown('<h2 class="sub-header">😊 Music for Your Mood</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            mood = st.selectbox(
                "Select your current mood:",
                ["happy", "sad", "energetic", "calm", "focused"],
                format_func=lambda x: {
                    "happy": "😊 Happy & Upbeat",
                    "sad": "😢 Sad & Melancholic", 
                    "energetic": "⚡ Energetic & Powerful",
                    "calm": "🌊 Calm & Relaxed",
                    "focused": "🎯 Focused & Productive"
                }[x]
            )
        with col2:
            num_recommendations = st.slider("Number of songs", 3, 10, 6, key="mood_slider")
        
        if st.button("🎵 Get Mood-Based Recommendations", use_container_width=True):
            with st.spinner(f"Finding perfect songs for {mood} mood..."):
                recommendations = get_recommendations_by_mood(sp, mood, num_recommendations)
                
            if recommendations:
                st.markdown(f"### 🎶 Songs for Your Mood:")
                for rec in recommendations:
                    display_track(rec, show_features=True)
            else:
                st.error("No recommendations found. Please try again.")
    
    elif "By Artist 👤" in app_mode:
        st.markdown('<h2 class="sub-header">👤 Discover Similar Artists</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            artist_query = st.text_input(
                "Enter an artist you like:",
                placeholder="e.g., Taylor Swift, The Weeknd, Drake",
                help="Enter artist name for similar music recommendations"
            )
        with col2:
            num_recommendations = st.slider("Number of songs", 3, 10, 6, key="artist_slider")
        
        if artist_query and st.button("🎸 Get Artist-Based Recommendations", use_container_width=True):
            with st.spinner(f"Finding music similar to {artist_query}..."):
                recommendations = get_recommendations_by_artist(sp, artist_query, num_recommendations)
                
            if recommendations:
                st.markdown(f"### 🎵 Songs Similar to {artist_query}:")
                for rec in recommendations:
                    display_track(rec, show_features=True)
            else:
                st.error(f"No recommendations found for artist '{artist_query}'")
    
    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #B3B3B3;'>
        <p>🎵 <b>AI Music Recommendation System</b> • Powered by Spotify API & Machine Learning</p>
        <p style='font-size: 0.9rem;'>Built with Streamlit • Feature analysis • Real-time recommendations</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()