import streamlit as st
from datetime import datetime
import time

def display_track(track, show_preview=True):
    """Display track information in a formatted way"""
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        if track.get('image'):
            st.image(track['image'], width=80)
    
    with col2:
        st.write(f"**{track['name']}**")
        st.write(f"by {track['artist']}")
        st.write(f"Album: {track.get('album', 'N/A')}")
        st.write(f"Popularity: {track.get('popularity', 'N/A')}/100")
        
        # Display audio features if available
        if 'danceability' in track:
            cols = st.columns(4)
            with cols[0]:
                st.metric("Dance", f"{track['danceability']:.2f}")
            with cols[1]:
                st.metric("Energy", f"{track['energy']:.2f}")
            with cols[2]:
                st.metric("Valence", f"{track['valence']:.2f}")
            with cols[3]:
                st.metric("Tempo", f"{track['tempo']:.0f}")
    
    with col3:
        if show_preview and track.get('preview_url'):
            st.audio(track['preview_url'])
        if track.get('external_url'):
            st.markdown(f"[Open in Spotify]({track['external_url']})")

def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="AI Music Recommendation System",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_css():
    """Load custom CSS styles"""
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
    </style>
    """, unsafe_allow_html=True)