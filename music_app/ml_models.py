"""
AI Emotion Classification Module

Sử dụng pre-trained DistilBERT model để phân loại cảm xúc từ lyrics.
Model: cardiffnlp/twitter-roberta-base-emotion (Hugging Face)

Cách hoạt động:
1. Tokenization: Chuyển text thành token IDs
2. Encoding: DistilBERT xử lý và trích xuất features
3. Classification: Neural network phân loại vào 4 emotions
"""

from transformers import pipeline
from dotenv import load_dotenv
import torch
import logging
import os

# Suppress Hugging Face authentication warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HTTP_HUB_OFFLINE"] = "0"

# --- HF TOKEN INTEGRATION ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
# ----------------------------

logger = logging.getLogger(__name__)


class EmotionClassifier:
    """
    AI Model để phân loại cảm xúc từ lyrics
    
    Attributes:
        _classifier: Hugging Face pipeline instance (lazy loaded)
    
    Methods:
        predict(lyrics): Phân tích lyrics → return {'emotion': 'happy', 'confidence': 0.85}
    """
    
    def __init__(self):
        """
        Initialize classifier (model chưa được load)
        Model sẽ được load lần đầu gọi predict() → Lazy loading
        """
        self._classifier = None
        logger.info("EmotionClassifier initialized (model not loaded yet)")
    
    @property
    def classifier(self):
        """
        Lazy loading: Chỉ load model khi cần thiết
        
        Returns:
            pipeline: Hugging Face text-classification pipeline
        
        Giải thích:
        - Lần đầu: Load model từ Hugging Face (~500MB download)
        - Các lần sau: Sử dụng cached instance
        - Tránh load model khi khởi động server (tiết kiệm memory)
        """
        if self._classifier is None:
            logger.info("Loading emotion classification model (first time)...")
            try:
                self._classifier = pipeline(
                    task="text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    top_k=None,
                    truncation=True  # Quan trọng: Tự động cắt lời bài hát nếu quá dài
                )
                logger.info("Model loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
        
        return self._classifier
    
    def predict(self, lyrics):
        """
        Phân tích cảm xúc từ lyrics
        
        Args:
            lyrics (str): Lời bài hát
        
        Returns:
            dict: {
                'emotion': 'happy',      # One of: happy, sad, relaxed, contemplative
                'confidence': 0.85       # Float 0.0-1.0
            }
            None: Nếu lyrics không hợp lệ (quá ngắn, rỗng)
        
        Flow:
        1. Validate input (check lyrics có đủ dài không)
        2. Truncate lyrics nếu quá dài (model limit: 512 tokens)
        3. Gọi model để predict
        4. Map output labels sang 4 emotions của ta
        5. Return emotion + confidence
        """
        
        # Validation: Check lyrics có hợp lệ không
        if not lyrics:
            logger.warning("Empty lyrics provided")
            return None
        
        lyrics_clean = lyrics.strip()
        
        if len(lyrics_clean) < 20:
            logger.warning(f"Lyrics too short ({len(lyrics_clean)} chars)")
            return None
        
        # Truncate lyrics nếu quá dài (BERT models có limit ~512 tokens)
        # Estimate: 1 token ≈ 4 characters → 512 tokens ≈ 2048 chars
        MAX_CHARS = 2000
        if len(lyrics_clean) > MAX_CHARS:
            lyrics_truncated = lyrics_clean[:MAX_CHARS]
            logger.info(f"Truncated lyrics from {len(lyrics_clean)} to {MAX_CHARS} chars")
        else:
            lyrics_truncated = lyrics_clean
        
        try:
            # Call AI model
            logger.info(f"Analyzing lyrics ({len(lyrics_truncated)} chars)...")
            results = self.classifier(lyrics_truncated, truncation=True)[0]
            
            # Emotion mapping: Map từ model labels sang 4 emotions của ta
            emotion_map = {
                'joy': 'happy',
                'optimism': 'happy',
                'love': 'happy',
                'surprise': 'happy',
                'excitement': 'happy',
                'amusement': 'happy',
                'gratitude': 'happy',
                'pride': 'happy',
                
                'sadness': 'sad',
                'anger': 'sad',
                'fear': 'sad',
                'disgust': 'sad',
                'disappointment': 'sad',
                'remorse': 'sad',
                'grief': 'sad',
                
                'calm': 'relaxed',
                'relief': 'relaxed',
                'neutral': 'relaxed',
                'approval': 'relaxed',
                'caring': 'relaxed',
                
                'curiosity': 'contemplative',
                'confusion': 'contemplative',
                'realization': 'contemplative',
                'desire': 'contemplative',
                'admiration': 'contemplative',
            }
            
            # Get top emotion (highest score)
            top_result = max(results, key=lambda x: x['score'])
            
            # Map to our 4 emotions
            raw_emotion = top_result['label'].lower()
            emotion = emotion_map.get(raw_emotion, 'relaxed')
            confidence = top_result['score']
            
            logger.info(f"Prediction: {emotion} ({confidence:.2%} confidence) [raw: {raw_emotion}]")
            
            return {
                'emotion': emotion,
                'confidence': float(confidence)
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during prediction: {error_msg}")
            return {'error': error_msg}


# ============ Singleton Pattern ============
# Chỉ tạo 1 instance duy nhất của EmotionClassifier
# Lợi ích: Tránh load model nhiều lần (tiết kiệm memory + time)

_emotion_classifier_instance = None


def get_emotion_classifier():
    """
    Factory function để lấy EmotionClassifier instance
    
    Returns:
        EmotionClassifier: Singleton instance
    
    Usage:
        from music_app.ml_models import get_emotion_classifier
        
        classifier = get_emotion_classifier()
        result = classifier.predict("I'm so happy today!")
        print(result)  # {'emotion': 'happy', 'confidence': 0.85}
    """
    global _emotion_classifier_instance
    
    if _emotion_classifier_instance is None:
        logger.info("Creating EmotionClassifier singleton instance")
        _emotion_classifier_instance = EmotionClassifier()
    
    return _emotion_classifier_instance
