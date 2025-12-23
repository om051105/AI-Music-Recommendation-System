# Use official Python image
FROM python:3.10-slim

# Set working directory to root
WORKDIR /app

# Install system dependencies (needed for OpenCV/DeepFace)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
# We use --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Application Code
COPY . .

# Expose the Port (Render uses 10000 by default but assigns PORT env var)
CMD ["sh", "-c", "uvicorn server.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
