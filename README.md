# 🎵 Industrial AI Music Recommendation System

A state-of-the-art Music Recommendation Engine built with **Industrial Engineering Practices**.
It goes beyond simple `if/else` logic, using **Machine Learning (Scikit-Learn)** and **Deep Learning (Transformers)** to understand both the *math* and the *meaning* of music.

## 🚀 Features

### 1. 🧠 The "Brain" (Machine Learning)
*   **Content-Based Filtering**: uses Cosine Similarity on audio features.
*   **Vector Space**: Maps every song to a 7D mathematical point based on Danceability, Energy, Valence, etc.
*   **Scalable**: Uses `StandardScaler` pipelines to handle data correctly.

### 2. 🗣️ The "Soul" (Deep Learning)
*   **Semantic Search**: You can search for abstract concepts like *"songs for a rainy heartbreak"* or *"music to focus on coding"*.
*   **Language Models**: Uses `sentence-transformers` (BERT-based) to understand the *meaning* of your query, not just keyword matching.

### 3. 🏭 Industrial Architecture
*   **Robust Data Pipeline**: Fetches data from Spotify. If the API fails (403), it automatically falls back to a "Synthetic Generator" so development never stops.
*   **Modular Code**: Organized into `src/` (Source), separating Data, Models, and Config.
*   **Security**: Credentials are encrypted in `.env`, never hardcoded.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
*   Python 3.10+
*   Spotify Developer Account (Client ID/Secret)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here
```

---

## 🏃‍♂️ How to Run

### Phase 1: Data Ingestion (The Truck)
Fetch data from Spotify and build the raw dataset.
```bash
python -m src.data.collector
```
*Output: `data/raw/songs_raw.csv`*

### Phase 2: Train ML Model (The Brain)
Train the Mathematical Recommender (Cosine Similarity).
```bash
python train_model.py
```
*Output: `data/models/recommender.pkl`*

### Phase 3: Train Semantic Engine (The Soul)
Index songs using the Deep Learning Transformer.
```bash
python train_semantic.py
```
*Output: `data/models/semantic_index.pkl`*

### Phase 4: Run the App
Launch the Streamlit Interface.
```bash
streamlit run app.py
```

---

## 📂 Project Structure
```text
project/
├── src/
│   ├── config.py           # Central Control Room
│   ├── logger.py           # Verification logs
│   ├── data/
│   │   ├── spotify_client.py # Robust API Handler
│   │   └── collector.py      # ETL Pipeline
│   └── models/
│       ├── pipeline.py       # Scikit-Learn Processor
│       ├── recommender.py    # Math Engine (ML)
│       └── semantic_engine.py# Deep Learning Engine (All-MiniLM)
├── data/
│   ├── raw/                # The CSV data
│   └── models/             # The Saved Brains (.pkl)
└── requirements.txt
```

---

## 🧠 Technical Deep Dive
*   **Embedding**: We convert text ("Sad Song") into a vector of 384 numbers.
*   **Cosine Similarity**: We measure the angle between the Query Vector and Song Vectors. Small angle = High Similarity.
*   **Hybrid Fallback**: If Spotify restricts API access, the system generates plausible feature data to ensure the ML pipeline remains testable (`src/data/collector.py`).