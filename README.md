# Final Project

An AI-powered emotion detection web application built with **Python 3**, **Flask**, and **IBM Watson NLP**. The system evaluates English text and determines the emotional probabilities across five categories: **anger**, **disgust**, **fear**, **joy**, and **sadness**, identifying the **dominant emotion**.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup (Windows)](#installation-and-setup-windows)
- [Running the Application](#running-the-application)
- [Running Unit Tests](#running-unit-tests)
- [Static Code Analysis (Pylint)](#static-code-analysis-pylint)
- [API Usage & Endpoints](#api-usage--endpoints)
- [Limitations & Upstream Service Behavior](#limitations--upstream-service-behavior)

---

## Overview

This project implements the final project for the IBM AI Developer Professional Certificate course. It packages an emotion detection client into a reusable Python module (`EmotionDetection`), exposes the model through a Flask web server, and provides an interactive web interface with robust input validation and error handling.

---

## Features

- **IBM Watson NLP Integration**: Communicates with the Watson NLP `EmotionPredict` service using aggregated emotion workflows.
- **Emotion Scoring**: Calculates probabilities for `anger`, `disgust`, `fear`, `joy`, and `sadness`, determining the `dominant_emotion`.
- **Reusable Package**: Modular package `EmotionDetection` exportable across Python applications.
- **Web Interface**: Clean user interface with real-time analysis, structured emotion cards, and dominant emotion highlighting.
- **Input Validation & Error Handling**: Gracefully handles blank/whitespace text, HTTP error status codes, network timeouts, and upstream outages.
- **Mocked Unit Test Suite**: Comprehensive tests using `unittest` and `unittest.mock` for high reliability without external network dependencies.
- **Clean Code Standard**: 10.00/10 Pylint score adhering to PEP 8 standards.

---

## Project Structure

```
oaqjp-final-project-emb-ai/
│
├── EmotionDetection/
│   ├── __init__.py               # Exports emotion_detector
│   └── emotion_detection.py      # Core IBM Watson NLP integration logic
│
├── static/
│   ├── mywebscript.js            # Client-side asynchronous interaction
│   └── style.css                 # Application styling
│
├── templates/
│   └── index.html                # Main application web interface
│
├── test_emotion_detection.py     # Unittest suite with mocked API responses
├── server.py                     # Flask web server and routing
├── requirements.txt              # Production and testing dependencies
├── README.md                     # Project documentation
├── LICENSE                       # Project license
└── .gitignore                    # Git ignore file for Python & environments
```

---

## Prerequisites

- **Python**: Version 3.10 or higher.
- **Git**: Installed and available in your PATH.
- **Windows PowerShell** or **Command Prompt**.

---

## Installation and Setup (Windows)

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd c:\Users\Dell\OneDrive\Desktop\IBM_flask
   ```

2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Running the Application

To start the Flask development server on port 5000:

```powershell
python server.py
```

The application will start at:
- Local Web Interface: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Network Interface: `http://0.0.0.0:5000`

Press `CTRL + C` in the terminal to stop the server.

---

## Running Unit Tests

The test suite uses Python's standard `unittest` framework with `unittest.mock` to simulate upstream IBM Watson responses:

```powershell
python -m unittest -v
```

### Test Coverage Summary
- Joy, anger, disgust, sadness, and fear emotion detection.
- Dominant emotion computation.
- Empty, `None`, and whitespace string inputs.
- HTTP error handling (e.g. 400, 404, 500, 503).
- Network timeouts (`ConnectTimeout`) and network connection failures.
- Malformed JSON responses and missing schema keys.
- Flask home page route (`/`).
- Flask `/emotionDetector` query parameter, JSON format, empty input, and POST payload handling.

---

## Static Code Analysis (Pylint)

To analyze the code using Pylint:

```powershell
pylint EmotionDetection/emotion_detection.py server.py test_emotion_detection.py
```

Target Score: **10.00 / 10**

---

## API Usage & Endpoints

### 1. Home Page
- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns the web UI (`index.html`).

---

### 2. Emotion Detector Endpoint
- **URL**: `/emotionDetector`
- **Methods**: `GET`, `POST`
- **Parameters / Payload**:
  - `textToAnalyze` (query parameter or JSON body): The text to analyze.
  - `format` (optional query parameter, e.g. `format=json`): Request JSON response.

#### Example GET Request (Default Text Output):
```http
GET /emotionDetector?textToAnalyze=I+am+so+happy+today HTTP/1.1
Host: 127.0.0.1:5000
```

#### Expected 200 OK Response:
```text
For the given statement, the system response is 'anger': 0.005, 'disgust': 0.002, 'fear': 0.003, 'joy': 0.968 and 'sadness': 0.046. The dominant emotion is joy.
```

#### Example GET Request with JSON Format:
```http
GET /emotionDetector?textToAnalyze=I+am+so+happy+today&format=json HTTP/1.1
Host: 127.0.0.1:5000
```

#### Expected JSON 200 OK Response:
```json
{
  "anger": 0.005,
  "disgust": 0.002,
  "fear": 0.003,
  "joy": 0.968,
  "sadness": 0.046,
  "dominant_emotion": "joy"
}
```

#### Error Handling (Blank / Invalid Input or Upstream Failure):
- **Status Code**: `400 Bad Request`
- **Response Body**:
  ```text
  Invalid text! Please try again!
  ```

---

## Limitations & Upstream Service Behavior

- **IBM Watson Sandbox Endpoint**: The target endpoint (`https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict`) resolves to internal IBM Skills Network private network IP addresses (`10.241.x.x`). Outside the IBM Cloud lab environment, requests to this URL will time out (`ConnectTimeout`).
- **Failure Representation**: When the upstream service is unreachable, times out, returns an HTTP error, or receives blank input, `emotion_detector` consistently returns:
  ```python
  {
      "anger": None,
      "disgust": None,
      "fear": None,
      "joy": None,
      "sadness": None,
      "dominant_emotion": None
  }
  ```
- **No Fabricated Data**: The application never fabricates emotion scores when the upstream Watson NLP service is inaccessible. In such cases, the server returns an HTTP 400 response with `"Invalid text! Please try again!"`.
