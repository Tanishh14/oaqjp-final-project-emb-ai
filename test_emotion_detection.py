# pylint: disable=duplicate-code
"""Unit tests for the EmotionDetection package and Flask application.

Covers:
- Emotion detection logic for various emotion categories
- Dominant emotion selection
- Handling of empty / whitespace input
- HTTP error responses from upstream
- Network timeouts and connection exceptions
- Malformed / unexpected API responses
- Flask homepage and /emotionDetector endpoint behavior
"""

import unittest
from unittest.mock import MagicMock, patch
import requests

from EmotionDetection.emotion_detection import emotion_detector
from server import app


def _build_watson_response(
    anger: float = 0.0,
    disgust: float = 0.0,
    fear: float = 0.0,
    joy: float = 0.0,
    sadness: float = 0.0,
) -> dict:
    """Helper function to build a mock Watson NLP response payload."""
    return {
        "emotionPredictions": [
            {
                "emotion": {
                    "anger": anger,
                    "disgust": disgust,
                    "fear": fear,
                    "joy": joy,
                    "sadness": sadness,
                },
                "target": "",
            }
        ],
        "producerId": {
            "name": "Aggregated Emotion Workflow",
            "version": "0.0.1",
        },
    }


class TestEmotionDetection(unittest.TestCase):
    """Test suite for the core emotion_detector function."""

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_joy_detection(self, mock_post: MagicMock) -> None:
        """Test joy detection and dominant emotion selection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _build_watson_response(
            anger=0.01, disgust=0.01, fear=0.01, joy=0.95, sadness=0.02
        )
        mock_post.return_value = mock_response

        result = emotion_detector("I am glad this happened")
        self.assertEqual(result["dominant_emotion"], "joy")
        self.assertAlmostEqual(result["joy"], 0.95)

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_anger_detection(self, mock_post: MagicMock) -> None:
        """Test anger detection and dominant emotion selection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _build_watson_response(
            anger=0.91, disgust=0.02, fear=0.03, joy=0.01, sadness=0.03
        )
        mock_post.return_value = mock_response

        result = emotion_detector("I am really mad about this")
        self.assertEqual(result["dominant_emotion"], "anger")
        self.assertAlmostEqual(result["anger"], 0.91)

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_disgust_detection(self, mock_post: MagicMock) -> None:
        """Test disgust detection and dominant emotion selection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _build_watson_response(
            anger=0.02, disgust=0.88, fear=0.05, joy=0.01, sadness=0.04
        )
        mock_post.return_value = mock_response

        result = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result["dominant_emotion"], "disgust")
        self.assertAlmostEqual(result["disgust"], 0.88)

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_sadness_detection(self, mock_post: MagicMock) -> None:
        """Test sadness detection and dominant emotion selection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _build_watson_response(
            anger=0.02, disgust=0.01, fear=0.03, joy=0.02, sadness=0.92
        )
        mock_post.return_value = mock_response

        result = emotion_detector("I am so sad about this")
        self.assertEqual(result["dominant_emotion"], "sadness")
        self.assertAlmostEqual(result["sadness"], 0.92)

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_fear_detection(self, mock_post: MagicMock) -> None:
        """Test fear detection and dominant emotion selection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _build_watson_response(
            anger=0.03, disgust=0.01, fear=0.91, joy=0.01, sadness=0.04
        )
        mock_post.return_value = mock_response

        result = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result["dominant_emotion"], "fear")
        self.assertAlmostEqual(result["fear"], 0.91)

    def test_empty_and_whitespace_input(self) -> None:
        """Test that empty string, None, and whitespace return all None values."""
        for empty_val in ["", None, "    ", "\n\t"]:
            result = emotion_detector(empty_val)
            self.assertIsNone(result["dominant_emotion"])
            self.assertIsNone(result["anger"])
            self.assertIsNone(result["disgust"])
            self.assertIsNone(result["fear"])
            self.assertIsNone(result["joy"])
            self.assertIsNone(result["sadness"])

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_http_error_response(self, mock_post: MagicMock) -> None:
        """Test that HTTP errors (e.g. 400 or 500) return all None values."""
        for code in [400, 404, 500, 503]:
            mock_response = MagicMock()
            mock_response.status_code = code
            mock_post.return_value = mock_response

            result = emotion_detector("Some sample text")
            self.assertIsNone(result["dominant_emotion"])
            self.assertIsNone(result["joy"])

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_network_failure_and_timeout(self, mock_post: MagicMock) -> None:
        """Test that network exceptions or timeouts return all None values."""
        mock_post.side_effect = requests.exceptions.ConnectTimeout("Connection timed out")
        result = emotion_detector("Some sample text")
        self.assertIsNone(result["dominant_emotion"])

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        result = emotion_detector("Some sample text")
        self.assertIsNone(result["dominant_emotion"])

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_malformed_and_unexpected_response(self, mock_post: MagicMock) -> None:
        """Test handling of invalid JSON and unexpected schema shapes."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        self.assertIsNone(emotion_detector("Text")["dominant_emotion"])

        mock_response.json.side_effect = None
        mock_response.json.return_value = {"something": "else"}
        self.assertIsNone(emotion_detector("Text")["dominant_emotion"])

        mock_response.json.return_value = {"emotionPredictions": []}
        self.assertIsNone(emotion_detector("Text")["dominant_emotion"])


class TestFlaskServer(unittest.TestCase):
    """Test suite for the Flask web application routes."""

    def setUp(self) -> None:
        """Set up the Flask test client."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page(self) -> None:
        """Test that the home page loads successfully with 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Emotion Detection", response.data)

    @patch("server.emotion_detector")
    def test_emotion_detector_success_string(self, mock_detector: MagicMock) -> None:
        """Test successful emotion detection returns expected formatted text."""
        mock_detector.return_value = {
            "anger": 0.01,
            "disgust": 0.02,
            "fear": 0.03,
            "joy": 0.90,
            "sadness": 0.04,
            "dominant_emotion": "joy",
        }
        response = self.client.get("/emotionDetector?textToAnalyze=I+am+so+happy")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The dominant emotion is joy.", response.data)
        self.assertIn(b"'joy': 0.9", response.data)

    @patch("server.emotion_detector")
    def test_emotion_detector_json_format(self, mock_detector: MagicMock) -> None:
        """Test json formatting when format=json query parameter is present."""
        mock_detector.return_value = {
            "anger": 0.01,
            "disgust": 0.02,
            "fear": 0.03,
            "joy": 0.90,
            "sadness": 0.04,
            "dominant_emotion": "joy",
        }
        response = self.client.get("/emotionDetector?textToAnalyze=I+am+so+happy&format=json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["dominant_emotion"], "joy")
        self.assertEqual(data["joy"], 0.90)

    def test_emotion_detector_missing_and_blank_input(self) -> None:
        """Test that missing or blank text returns HTTP 400."""
        resp_missing = self.client.get("/emotionDetector")
        self.assertEqual(resp_missing.status_code, 400)
        self.assertIn(b"Invalid text! Please try again!", resp_missing.data)

        resp_blank = self.client.get("/emotionDetector?textToAnalyze=")
        self.assertEqual(resp_blank.status_code, 400)
        self.assertIn(b"Invalid text! Please try again!", resp_blank.data)

        resp_spaces = self.client.get("/emotionDetector?textToAnalyze=+++")
        self.assertEqual(resp_spaces.status_code, 400)
        self.assertIn(b"Invalid text! Please try again!", resp_spaces.data)

    @patch("server.emotion_detector")
    def test_emotion_detector_upstream_failure(self, mock_detector: MagicMock) -> None:
        """Test that an upstream detector failure returns HTTP 400."""
        mock_detector.return_value = {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }
        response = self.client.get("/emotionDetector?textToAnalyze=Some+valid+text")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid text! Please try again!", response.data)

    @patch("server.emotion_detector")
    def test_emotion_detector_post_method(self, mock_detector: MagicMock) -> None:
        """Test POST request with JSON payload to /emotionDetector."""
        mock_detector.return_value = {
            "anger": 0.85,
            "disgust": 0.05,
            "fear": 0.05,
            "joy": 0.01,
            "sadness": 0.04,
            "dominant_emotion": "anger",
        }
        response = self.client.post(
            "/emotionDetector",
            json={"textToAnalyze": "I am furious"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The dominant emotion is anger.", response.data)


if __name__ == "__main__":
    unittest.main()
