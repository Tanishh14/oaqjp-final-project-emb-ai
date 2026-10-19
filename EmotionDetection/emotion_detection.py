"""Emotion detection module using IBM Watson NLP EmotionPredict service.

This module provides the `emotion_detector` function which submits text
to the Watson NLP EmotionPredict endpoint and parses the resulting emotion
probabilities (anger, disgust, fear, joy, sadness) to identify the dominant emotion.
"""

from typing import Any, Dict, Optional
import requests

WATSON_EMOTION_URL = (
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
WATSON_MODEL_ID = "emotion_aggregated-workflow_lang_en_stock"
EMOTION_KEYS = ("anger", "disgust", "fear", "joy", "sadness")


def _empty_emotion_response() -> Dict[str, Optional[Any]]:
    """Return a consistent dictionary representing failure or blank input."""
    result: Dict[str, Optional[Any]] = {key: None for key in EMOTION_KEYS}
    result["dominant_emotion"] = None
    return result


def emotion_detector(text_to_analyse: Optional[str]) -> Dict[str, Optional[Any]]:
    """Analyze the emotions expressed in the provided text.

    Args:
        text_to_analyse: The input text to be evaluated.

    Returns:
        A dictionary containing emotion scores for 'anger', 'disgust', 'fear',
        'joy', 'sadness', and the string label of the 'dominant_emotion'.
        If the input is empty or the upstream service fails, returns None for all keys.
    """
    if not text_to_analyse or not str(text_to_analyse).strip():
        return _empty_emotion_response()

    payload = {"raw_document": {"text": text_to_analyse}}
    headers = {"grpc-metadata-mm-model-id": WATSON_MODEL_ID}

    try:
        response = requests.post(
            WATSON_EMOTION_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        if response.status_code == 400 or response.status_code != 200:
            return _empty_emotion_response()

        data = response.json()
        predictions = data.get("emotionPredictions", [])
        emotions = predictions[0].get("emotion", {}) if predictions else {}
        if not emotions:
            return _empty_emotion_response()

        scores: Dict[str, Optional[Any]] = {
            key: float(emotions.get(key, 0.0)) for key in EMOTION_KEYS
        }
        scores["dominant_emotion"] = max(
            EMOTION_KEYS,
            key=lambda k: scores[k] or 0.0,
        )
        return scores
    except (
        requests.exceptions.RequestException,
        TimeoutError,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
    ):
        return _empty_emotion_response()
