# API Endpoints Reference

## 🎯 Active Endpoints

### YouTube Search
```http
POST /api/youtube/search
Content-Type: application/json

{
  "query": "Dr Martens 1460 boots",
  "max_reviews": 50
}
```

**Response:**
```json
{
  "success": true,
  "reviews": [
    {
      "author": "string",
      "text": "string",
      "date": "YYYY-MM-DD",
      "likes": 0,
      "video_title": "string",
      "video_url": "string",
      "channel": "string",
      "video_views": 0,
      "video_likes": 0,
      "sentiment": {
        "sentiment": "positive|neutral|negative",
        "polarity": 0.5,
        "subjectivity": 0.5,
        "confidence": "high|medium|low"
      }
    }
  ],
  "total": 0,
  "source": "youtube"
}
```

---

### Trustpilot Search
```http
POST /api/trustpilot/search
Content-Type: application/json

{
  "query": "Dr Martens",
  "max_reviews": 50
}
```

**Response:**
```json
{
  "success": true,
  "reviews": [
    {
      "author": "string",
      "rating": 5,
      "title": "string",
      "text": "string",
      "date": "YYYY-MM-DD",
      "verified": true,
      "url": "string",
      "sentiment": {
        "sentiment": "positive|neutral|negative",
        "polarity": 0.5,
        "subjectivity": 0.5,
        "confidence": "high|medium|low"
      }
    }
  ],
  "total": 0,
  "source": "trustpilot"
}
```

---

### Amazon Search
```http
POST /api/amazon/search
Content-Type: application/json

{
  "query": "Dr Martens 1460",
  "max_reviews": 50
}
```

**Response:**
```json
{
  "success": true,
  "product_info": {
    "name": "string",
    "rating": 4.5,
    "total_reviews": 1000,
    "url": "string"
  },
  "reviews": [
    {
      "author": "string",
      "rating": 5,
      "title": "string",
      "text": "string",
      "date": "string",
      "verified": true,
      "sentiment": {
        "sentiment": "positive|neutral|negative",
        "polarity": 0.5,
        "subjectivity": 0.5
      }
    }
  ],
  "total": 0
}
```

---

### Reddit Search
```http
POST /api/reddit/search
Content-Type: application/json

{
  "query": "Dr Martens",
  "max_posts": 50
}
```

**Response:**
```json
{
  "success": true,
  "reviews": [
    {
      "author": "string",
      "title": "string",
      "text": "string",
      "score": 100,
      "subreddit": "string",
      "date": "YYYY-MM-DD",
      "url": "string",
      "sentiment": {
        "sentiment": "positive|neutral|negative",
        "polarity": 0.5,
        "subjectivity": 0.5
      }
    }
  ],
  "total": 0,
  "source": "reddit"
}
```

---

### Combined Analysis (All 4 Sources)
```http
POST /api/combined-analysis
Content-Type: application/json

{
  "query": "Dr Martens 1460 boots",
  "max_reviews": 30
}
```

**Response:**
```json
{
  "success": true,
  "youtube": {
    "reviews": [...],
    "count": 0
  },
  "amazon": {
    "reviews": [...],
    "count": 0
  },
  "reddit": {
    "reviews": [...],
    "count": 0
  },
  "trustpilot": {
    "reviews": [...],
    "count": 0
  },
  "combined_statistics": {
    "total_reviews": 0,
    "youtube_reviews_count": 0,
    "amazon_reviews_count": 0,
    "reddit_reviews_count": 0,
    "trustpilot_reviews_count": 0,
    "sentiment_distribution": {
      "positive": 0,
      "neutral": 0,
      "negative": 0
    },
    "average_polarity": 0.0,
    "average_subjectivity": 0.0,
    "average_rating": 0.0
  },
  "all_reviews": [...]
}
```

---

### AI Insights
```http
POST /api/ai-insights
Content-Type: application/json

{
  "reviews": [...],
  "context": {
    "query": "Dr Martens 1460 boots",
    "total_reviews": 150,
    "sentiment_distribution": {...}
  }
}
```

**Response:**
```json
{
  "success": true,
  "insights": {
    "summary": "string",
    "strengths": ["string"],
    "weaknesses": ["string"],
    "recommendations": ["string"],
    "sentiment_analysis": "string",
    "trends": "string"
  }
}
```

---

### Management Report
```http
POST /api/management-report
Content-Type: application/json

{
  "reviews": [...],
  "statistics": {...},
  "insights": {...}
}
```

**Response:**
```json
{
  "success": true,
  "report": "# Executive Summary\n\n...",
  "generated_at": "2024-01-01T12:00:00"
}
```

---

## ❌ Deprecated Endpoints

### Google Places Search (Removed)
```http
POST /api/search
```
**Returns:** Error message directing to use YouTube or Trustpilot

### Google Places Reviews (Removed)
```http
POST /api/reviews
```
**Returns:** Error message directing to use YouTube or Trustpilot

---

## 🔧 Testing with curl

### Test YouTube Search
```bash
curl -X POST http://localhost:5000/api/youtube/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Dr Martens 1460 boots", "max_reviews": 10}'
```

### Test Trustpilot Search
```bash
curl -X POST http://localhost:5000/api/trustpilot/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Dr Martens", "max_reviews": 10}'
```

### Test Combined Analysis
```bash
curl -X POST http://localhost:5000/api/combined-analysis \
  -H "Content-Type: application/json" \
  -d '{"query": "Dr Martens 1460", "max_reviews": 10}'
```

---

## 📝 Notes

1. All endpoints return sentiment analysis using GPT-4o-mini
2. YouTube requires `YOUTUBE_API_KEY` in `.env`
3. Trustpilot uses Selenium (may be slower due to page loading)
4. Amazon uses Selenium (may be slower due to page loading)
5. Reddit uses official PRAW library (fastest)
6. Combined analysis fetches all sources in parallel
7. All endpoints handle errors gracefully and return partial results if some sources fail
