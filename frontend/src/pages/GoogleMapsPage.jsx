import { useState } from 'react'
import axios from 'axios'
import '../App.css'
import ReviewCard from '../components/ReviewCard'
import Statistics from '../components/Statistics'
import SentimentChart from '../components/SentimentChart'
import AIInsights from '../components/AIInsights'
import ChatAssistant from '../components/ChatAssistant'

const API_URL = 'http://localhost:5000/api'

function App() {
  const [query, setQuery] = useState('Dr. Martens')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [placeData, setPlaceData] = useState(null)
  const [reviews, setReviews] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [useScraper, setUseScraper] = useState(true)  // Enable scraping by default
  const [dataSource, setDataSource] = useState(null)

  const handleSearch = async () => {
    setLoading(true)
    setError(null)
    setPlaceData(null)
    setReviews([])
    setStatistics(null)
    setDataSource(null)

    try {
      // First, search for the place
      const searchResponse = await axios.post(`${API_URL}/search`, { query })
      
      if (searchResponse.data.success && searchResponse.data.place) {
        const placeId = searchResponse.data.place.place_id
        
        // Then, get reviews for that place with scraping option
        const reviewsResponse = await axios.post(`${API_URL}/reviews`, {
          place_id: placeId,
          use_scraper: useScraper,
          max_reviews: 50  // Get up to 50 reviews
        })
        
        if (reviewsResponse.data.success) {
          setPlaceData(reviewsResponse.data.place)
          setReviews(reviewsResponse.data.reviews)
          setStatistics(reviewsResponse.data.statistics)
          setDataSource(reviewsResponse.data.data_source)
        }
      } else {
        setError('No place found. Try a different search query.')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while fetching reviews')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="header">
        <h1>🥾 Dr. Martens Review Analysis</h1>
        <p>Analyze customer reviews with AI-powered sentiment analysis</p>
      </header>

      <div className="search-container">
        <div className="search-box">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for Dr. Martens store (e.g., 'Dr. Martens New York')"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Search & Analyze'}
          </button>
        </div>
        
        <div className="scraper-toggle">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={useScraper}
              onChange={(e) => setUseScraper(e.target.checked)}
            />
            <span className="toggle-text">
              🕷️ Use Web Scraping (50+ reviews for better AI analysis)
            </span>
          </label>
          {!useScraper && (
            <p className="toggle-note">⚠️ Google Places API limited to 5 reviews only</p>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      )}
      
      {dataSource && (
        <div className={`data-source-badge ${dataSource === 'web_scraping' ? 'scraping' : 'api'}`}>
          {dataSource === 'web_scraping' 
            ? `✅ Scraped ${reviews.length} real reviews from Google Maps` 
            : `📍 Using Google Places API (${reviews.length} reviews)`}
        </div>
      )}

      {placeData && (
        <div className="place-info">
          <h2>{placeData.name}</h2>
          <p className="address">{placeData.address}</p>
          <div className="rating-info">
            <span className="rating">⭐ {placeData.rating}</span>
            <span className="total-ratings">({placeData.total_ratings} total ratings)</span>
          </div>
        </div>
      )}

      {statistics && (
        <>
          <Statistics statistics={statistics} />
          <SentimentChart statistics={statistics} />
        </>
      )}

      {reviews.length > 0 && (
        <>
          {/* AI Insights Section */}
          <AIInsights reviews={reviews} />

          <div className="reviews-container">
            <h2>Customer Reviews ({reviews.length})</h2>
            <div className="reviews-grid">
              {reviews.map((review, index) => (
                <ReviewCard key={index} review={review} />
              ))}
            </div>
          </div>

          {/* Chat Assistant */}
          <ChatAssistant reviews={reviews} />
        </>
      )}

      {!loading && !error && reviews.length === 0 && (
        <div className="empty-state">
          <p>👆 Search for a Dr. Martens store to see reviews and sentiment analysis</p>
        </div>
      )}
    </div>
  )
}

export default App
