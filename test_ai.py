import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from music_app.ml_models import get_emotion_classifier

def test_ai():
    print("--- AI Model Test ---")
    classifier = get_emotion_classifier()
    
    test_lyrics = "I am so happy and excited today! Walking on sunshine!"
    print(f"Testing with: {test_lyrics}")
    
    result = classifier.predict(test_lyrics)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_ai()
