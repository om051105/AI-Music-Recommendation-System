MOOD_TO_FEATURES = {
    'happy': {
        'target_valence': 0.8,
        'target_energy': 0.7,
        'target_danceability': 0.7,
        'min_valence': 0.6,
        'min_energy': 0.5
    },
    'sad': {
        'target_valence': 0.2,
        'target_energy': 0.3,
        'target_danceability': 0.3,
        'max_valence': 0.4,
        'max_energy': 0.5
    },
    'energetic': {
        'target_valence': 0.7,
        'target_energy': 0.9,
        'target_danceability': 0.8,
        'min_energy': 0.7,
        'min_danceability': 0.6
    },
    'calm': {
        'target_valence': 0.5,
        'target_energy': 0.2,
        'target_danceability': 0.3,
        'max_energy': 0.4,
        'min_acousticness': 0.5
    },
    'focused': {
        'target_valence': 0.5,
        'target_energy': 0.5,
        'target_instrumentalness': 0.7,
        'min_instrumentalness': 0.4,
        'max_speechiness': 0.3
    }
}

MOOD_GENRES = {
    'happy': ['pop', 'dance', 'disco'],
    'sad': ['acoustic', 'sad', 'piano'],
    'energetic': ['rock', 'electronic', 'work-out'],
    'calm': ['ambient', 'chill', 'classical'],
    'focused': ['instrumental', 'classical', 'jazz']
}