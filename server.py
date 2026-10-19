"""Flask Web Server for Emotion Detection.

This module initializes a Flask web application that serves a web interface
for users to submit text and provides an /emotionDetector endpoint that calls
the EmotionDetection package and returns formatted results.
"""

from typing import Tuple, Union
from flask import Flask, Response, jsonify, render_template, request
from EmotionDetection.emotion_detection import emotion_detector

app = Flask("Emotion Detector")


@app.route("/")
def render_index_page() -> str:
    """Render the application homepage."""
    return render_template("index.html")


@app.route("/emotionDetector", methods=["GET", "POST"])
def detect_emotion() -> Union[Tuple[str, int], Tuple[Response, int]]:
    """Analyze emotions in the input text provided via query param or POST body.

    Returns:
        A formatted message containing individual emotion scores and the dominant emotion,
        or an HTTP 400 error if input is invalid or upstream service fails.
    """
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        text_to_analyze = payload.get("textToAnalyze") or request.form.get("textToAnalyze")
    else:
        text_to_analyze = request.args.get("textToAnalyze")

    if not text_to_analyze or not str(text_to_analyze).strip():
        return "Invalid text! Please try again!", 400

    response_data = emotion_detector(text_to_analyze)
    dominant_emotion = response_data.get("dominant_emotion")

    if dominant_emotion is None:
        return "Invalid text! Please try again!", 400

    wants_json = (
        request.args.get("format") == "json"
        or request.headers.get("Accept") == "application/json"
    )
    if wants_json:
        return jsonify(response_data), 200

    formatted_message = (
        f"For the given statement, the system response is 'anger': {response_data['anger']}, "
        f"'disgust': {response_data['disgust']}, 'fear': {response_data['fear']}, "
        f"'joy': {response_data['joy']} and 'sadness': {response_data['sadness']}. "
        f"The dominant emotion is {dominant_emotion}."
    )
    return formatted_message, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
