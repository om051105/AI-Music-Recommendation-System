import cv2
import numpy as np
from deepface import DeepFace
from src.logger import get_logger

logger = get_logger(__name__)

class EmotionDetector:
    """
    The 'Eyes' of the System.
    Uses Deep Learning (DeepFace) to analyze facial expressions.
    """
    
    def __init__(self):
        # DeepFace loads models on the first call, so we do a dummy call here
        # or we just wait for the first user interaction.
        pass

    def detect_emotion(self, image):
        """
        Analyze a webcam frame and return the dominant emotion.
        Args:
            image: numpy array (from cv2 or streamlit-webrtc)
        Returns:
            str: "happy", "sad", "neutral", etc.
        """
        try:
            # DeepFace expects BGR or RGB. Streamlit WebRTC gives RGB.
            # Convert to BGR for OpenCV standard if needed, but DeepFace handles numpy arrays.
            
            # Analyze
            # actions=['emotion'] makes it faster (skips age/gender/race)
            analysis = DeepFace.analyze(img_path=image, actions=['emotion'], enforce_detection=False)
            
            if not analysis:
                return None
                
            # Get dominant emotion
            # DeepFace returns a list of dictionaries (one for each face)
            dominant_emotion = analysis[0]['dominant_emotion']
            
            logger.info(f"📸 Detected Emotion: {dominant_emotion}")
            return dominant_emotion
            
        except Exception as e:
            logger.error(f"❌ Emotion Detection Failed: {e}")
            return None
