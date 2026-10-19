"""EmotionDetection Package.

Exposes the emotion_detector function for analyzing emotions in text
using the IBM Watson NLP EmotionPredict service.
"""

from .emotion_detection import emotion_detector

__all__ = ["emotion_detector"]
