# Google Places API → YouTube & Trustpilot Migration Guide

## ✅ What Has Been Completed

### 1. **New Scrapers Created**

#### YouTube Scraper (`backend/youtube_scraper.py`)
- Uses YouTube Data API v3 (official Google API)
- Searches for product review videos
- Extracts comments from top 10 relevant videos
- Returns: author, text, date, likes, video metadata
- **Function:** `scrape_youtube_reviews(query, max_results=50)`

#### Trustpilot Scraper (`backend/trustpilot_scraper.py`)
- Uses Selenium (same as Amazon scraper)
- Scrapes https://www.trustpilot.com/review/www.drmartens.com
- Extracts verified purchase reviews with 1-5 star ratings
- Returns: author, rating, title, text, date, verified status
- **Function:** `scrape_trustpilot_reviews(product_name, max_reviews=50)`

### 2. **Backend Updates (`backend/app.py`)**

#### Removed:
- ❌ Google Places API integration
- ❌ `search_place()` function
- ❌ `get_place_reviews()` function
- ❌ `/api/search` endpoint (now returns deprecation message)
- ❌ `/api/reviews` endpoint (now returns deprecation message)
- ❌ Google Maps references in `/api/combined-analysis`

#### Added:
- ✅ `/api/youtube/search` - Search YouTube for product reviews
- ✅ `/api/trustpilot/search` - Search Trustpilot for verified reviews
- ✅ Updated `/api/combined-analysis` to use 4 sources:
  - YouTube (video reviews + comments)
  - Amazon (product reviews)
  - Reddit (community discussions)
  - Trustpilot (verified purchase reviews)

### 3. **Environment Variables Updated (`backend/.env`)**
- ❌ Removed: `GOOGLE_API_KEY` (exposed key deleted for security)
- ✅ Added: `YOUTUBE_API_KEY="your_youtube_api_key_here"` (placeholder)

### 4. **Dependencies Updated (`backend/requirements.txt`)**
- ✅ Added: `google-api-python-client==2.108.0` (for YouTube Data API)

---

## 🔧 What You Need to Do

### Step 1: Get YouTube Data API v3 Key

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **"YouTube Data API v3"**
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create API credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
5. **Security:** Restrict the API key
   - Click on the created key
   - Add IP restrictions (your server IP) or HTTP referrer restrictions
6. Copy the API key

### Step 2: Update Environment Variables

Edit `backend/.env` and replace the placeholder:

```env
YOUTUBE_API_KEY="your_actual_youtube_api_key_here"
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `google-api-python-client==2.108.0` needed for YouTube API.

### Step 4: Update Frontend

The frontend still references Google Maps. You need to update these files:

#### `frontend/src/pages/UnifiedSearch.jsx`

**Current:** Calls 3 sources (Google, Amazon, Reddit)  
**Update to:** Call 4 sources (YouTube, Amazon, Reddit, Trustpilot)

**Changes needed:**
1. Replace Google Maps API call with YouTube:
   ```javascript
   // OLD
   axios.post('http://localhost:5000/api/search', { query })
   
   // NEW
   axios.post('http://localhost:5000/api/youtube/search', { query, max_reviews: 50 })
   ```

2. Add Trustpilot API call:
   ```javascript
   axios.post('http://localhost:5000/api/trustpilot/search', { query, max_reviews: 50 })
   ```

3. Update state variables:
   ```javascript
   // Replace googleData with youtubeData and add trustpilotData
   const [youtubeData, setYoutubeData] = useState(null);
   const [trustpilotData, setTrustpilotData] = useState(null);
   ```

4. Update Promise.all to fetch all 4 sources:
   ```javascript
   const [youtubeRes, amazonRes, redditRes, trustpilotRes] = await Promise.all([
     axios.post('http://localhost:5000/api/youtube/search', { query, max_reviews: 50 }),
     axios.post('http://localhost:5000/api/amazon/search', { query, max_reviews: 50 }),
     axios.post('http://localhost:5000/api/reddit/search', { query, max_posts: 50 }),
     axios.post('http://localhost:5000/api/trustpilot/search', { query, max_reviews: 50 })
   ]);
   ```

5. Update source cards display (replace Google with YouTube and add Trustpilot)

#### `frontend/src/components/ReviewCard.jsx`

Add badges for YouTube and Trustpilot:

**YouTube badge:**
```jsx
{source === 'youtube' && (
  <span className="source-badge youtube">
    <Video size={12} /> YouTube
  </span>
)}
```

**Trustpilot badge:**
```jsx
{source === 'trustpilot' && (
  <span className="source-badge trustpilot">
    <Star size={12} /> Trustpilot
  </span>
)}
```

Display video title for YouTube reviews:
```jsx
{source === 'youtube' && review.video_title && (
  <div className="video-info">
    Video: {review.video_title}
  </div>
)}
```

Display verified badge for Trustpilot:
```jsx
{source === 'trustpilot' && review.verified && (
  <span className="verified-badge">✓ Verified Purchase</span>
)}
```

#### `frontend/src/components/ReviewCard.css`

Add styling for new source badges:

```css
.source-badge.youtube {
  background: #FF0000;
  color: white;
}

.source-badge.trustpilot {
  background: #00B67A;
  color: white;
}

.video-info {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.verified-badge {
  background: #4CAF50;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-left: 8px;
}
```

### Step 5: Test the System

1. Start the backend:
   ```bash
   cd backend
   python app.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Test search with "Dr Martens 1460 boots" and verify:
   - ✅ YouTube returns video review comments
   - ✅ Amazon returns product reviews
   - ✅ Reddit returns community posts
   - ✅ Trustpilot returns verified reviews
   - ✅ All sources analyzed by AI sentiment
   - ✅ Combined statistics show all 4 sources

---

## 📊 Data Source Comparison

| Source | Type | Best For | Verification |
|--------|------|----------|--------------|
| **YouTube** ✅ | Video reviews + comments | Visual product demonstrations, in-depth reviews | YouTube account |
| **Amazon** ✅ | Product reviews | Purchase experience, product quality | Verified purchase badge |
| **Reddit** ✅ | Community discussions | Honest opinions, long-term durability | Community karma |
| **Trustpilot** ✅ | Business reviews | Overall brand experience, verified customers | Verified purchase |
| ~~Google Places~~ ❌ | Location reviews | Store experience (NOT product-focused) | Google account |

**Why the change?**  
Google Places API provided store/location reviews, which don't help Dr. Martens management analyze **product performance**. The new sources all focus on product-specific feedback, which is more valuable for business strategy decisions.

---

## 🔒 Security Notes

1. **YouTube API Key:** Restrict by IP address or domain in Google Cloud Console
2. **API Quota:** YouTube Data API has daily quotas (10,000 units/day by default)
3. **Rate Limiting:** Consider implementing rate limiting on your endpoints
4. **Exposed Keys:** The old Google API key was exposed in `.env` and has been removed

---

## 🎯 Expected Results

After migration, your system will:
- ✅ Aggregate reviews from 4 product-focused sources
- ✅ Provide comprehensive sentiment analysis using GPT-4o-mini
- ✅ Generate strategic AI insights for management
- ✅ Display verified purchase badges (Trustpilot, Amazon)
- ✅ Show video context for YouTube reviews
- ✅ Focus on product quality, not store experience

---

## ❓ Troubleshooting

### "Import 'googleapiclient.discovery' could not be resolved"
**Solution:** Run `pip install google-api-python-client`

### "YouTube API quota exceeded"
**Solution:** Wait 24 hours for quota reset, or request quota increase in Google Cloud Console

### "No YouTube reviews found"
**Solution:** Check if `YOUTUBE_API_KEY` is set correctly in `.env`, verify API is enabled in Google Cloud Console

### "Trustpilot reviews not loading"
**Solution:** Trustpilot may have anti-bot measures. The scraper uses same anti-detection as Amazon scraper. Consider adding delays or rotating user agents.

### Frontend shows Google Maps option
**Solution:** Update `UnifiedSearch.jsx` to replace Google Maps UI with YouTube and add Trustpilot

---

## 📞 Support

If you encounter issues:
1. Check backend console for error messages
2. Verify all API keys are set in `.env`
3. Ensure all dependencies are installed (`pip install -r requirements.txt`)
4. Test each endpoint individually using Postman or curl
5. Check browser console for frontend errors

---

## 🚀 Next Steps

1. ✅ Get YouTube API key
2. ✅ Update `.env` with YouTube API key
3. ✅ Install dependencies (`pip install -r requirements.txt`)
4. ✅ Update frontend (UnifiedSearch.jsx, ReviewCard.jsx, ReviewCard.css)
5. ✅ Test all 4 data sources
6. ✅ Deploy to production (remember to set environment variables on server)

Good luck with your product-focused sentiment analysis system! 🎉
