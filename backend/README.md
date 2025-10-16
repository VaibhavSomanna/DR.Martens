# Dr. Martens Review Analysis System - Backend

This is the Flask backend for the Dr. Martens review analysis system. It extracts reviews from Google Places API and performs sentiment analysis.

## Features

- Search for Dr. Martens stores using Google Places API
- Extract reviews from Google Places
- Sentiment analysis using TextBlob
- REST API endpoints for frontend integration
- CORS enabled for cross-origin requests

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download TextBlob corpora:
```bash
python -m textblob.download_corpora
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Add your Google Places API key to `.env`:
   - Go to https://console.cloud.google.com/apis/credentials
   - Create or select a project
   - Enable the Places API
   - Create an API key
   - Add it to your `.env` file

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns server status

### Search Place
- **POST** `/api/search`
- Body: `{"query": "Dr. Martens Store Location"}`
- Returns place information including place_id

### Get Reviews
- **POST** `/api/reviews`
- Body: `{"place_id": "place_id_from_search"}`
- Returns reviews with sentiment analysis

### Analyze Text
- **POST** `/api/analyze`
- Body: `{"text": "text to analyze"}`
- Returns sentiment analysis for the provided text

## Example Usage

```python
import requests

# Search for a place
response = requests.post('http://localhost:5000/api/search', 
    json={"query": "Dr. Martens New York"})
place_id = response.json()['place']['place_id']

# Get reviews
response = requests.post('http://localhost:5000/api/reviews',
    json={"place_id": place_id})
print(response.json())
```
