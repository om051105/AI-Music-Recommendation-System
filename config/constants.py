# Spotify API constants
SPOTIFY_SCOPE = "user-read-private user-read-email"
SPOTIFY_REDIRECT_URI = "http://localhost:8501"

# Audio features for ML model
AUDIO_FEATURES = [
    'danceability', 'energy', 'valence', 'acousticness',
    'instrumentalness', 'liveness', 'speechiness', 'tempo'
]

# Recommendation settings
MAX_RECOMMENDATIONS = 10
DEFAULT_RECOMMENDATIONS = 5

# App settings
CACHE_TIMEOUT = 3600  # 1 hour