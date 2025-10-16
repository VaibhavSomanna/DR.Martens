import { useState } from 'react'
import axios from 'axios'
import { ShoppingBag, Package, Star, CheckCircle } from 'lucide-react'
import '../App.css'
import './AmazonPage.css'
import ReviewCard from '../components/ReviewCard'
import Statistics from '../components/Statistics'
import SentimentChart from '../components/SentimentChart'
import AIInsights from '../components/AIInsights'
import ChatAssistant from '../components/ChatAssistant'

const API_URL = 'http://localhost:5000/api'

function AmazonPage() {
  const [query, setQuery] = useState('Dr Martens 1460 boots')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [productInfo, setProductInfo] = useState(null)
  const [reviews, setReviews] = useState([])

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a product name')
      return
    }

    setLoading(true)
    setError(null)
    setProductInfo(null)
    setReviews([])

    try {
      const response = await axios.post(`${API_URL}/amazon/search`, {
        query: query.trim(),
        max_reviews: 50
      })

      if (response.data.success) {
        setProductInfo(response.data.product_info)
        setReviews(response.data.reviews)
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while fetching Amazon reviews')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const calculateStatistics = () => {
    if (reviews.length === 0) return null

    const sentimentCounts = {
      positive: reviews.filter(r => r.sentiment === 'positive').length,
      neutral: reviews.filter(r => r.sentiment === 'neutral').length,
      negative: reviews.filter(r => r.sentiment === 'negative').length
    }

    const avgRating = reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
    const avgPolarity = reviews.reduce((sum, r) => sum + r.polarity, 0) / reviews.length
    const verifiedCount = reviews.filter(r => r.verified).length

    return {
      total_reviews: reviews.length,
      verified_purchases: verifiedCount,
      sentiment_distribution: sentimentCounts,
      average_rating: avgRating.toFixed(1),
      average_polarity: avgPolarity.toFixed(2)
    }
  }

  const statistics = calculateStatistics()

  return (
    <div className="amazon-page">
      <header className="header amazon-header">
        <div className="header-icon">
          <ShoppingBag size={48} />
        </div>
        <h1>🛒 Amazon Product Reviews</h1>
        <p>Analyze customer reviews from Amazon products</p>
      </header>

      <div className="search-container">
        <div className="search-box">
          <Package className="search-icon" size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for product (e.g., 'Dr Martens 1460 boots')"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading} className="search-button">
            {loading ? 'Searching...' : 'Search Product'}
          </button>
        </div>

        <div className="search-hint">
          <p>💡 <strong>Tip:</strong> Enter product name or model. We'll scrape 50+ real customer reviews from Amazon.</p>
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Scraping Amazon reviews...</p>
          <p className="loading-subtext">This may take 1-2 minutes</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
        </div>
      )}

      {productInfo && (
        <div className="product-info">
          <div className="product-header">
            <ShoppingBag className="product-icon" size={32} />
            <div className="product-details">
              <h2>{productInfo.name}</h2>
              <div className="product-meta">
                <span className="product-rating">
                  <Star className="star-icon" size={18} fill="#f59e0b" color="#f59e0b" />
                  {productInfo.rating}/5
                </span>
                <span className="product-total">
                  ({productInfo.total_ratings.toLocaleString()} total ratings)
                </span>
              </div>
            </div>
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
          <AIInsights reviews={reviews} />

          <div className="reviews-container">
            <div className="reviews-header">
              <h2>Customer Reviews ({reviews.length})</h2>
              <div className="verified-badge-info">
                <CheckCircle size={16} />
                <span>{statistics.verified_purchases} Verified Purchases</span>
              </div>
            </div>
            <div className="reviews-grid">
              {reviews.map((review, index) => (
                <ReviewCard 
                  key={index} 
                  review={review}
                  showVerified={true}
                />
              ))}
            </div>
          </div>

          <ChatAssistant reviews={reviews} />
        </>
      )}

      {!loading && !error && reviews.length === 0 && (
        <div className="empty-state">
          <ShoppingBag size={64} className="empty-icon" />
          <p>👆 Search for an Amazon product to see reviews and AI analysis</p>
          <p className="empty-subtext">Try: "Dr Martens 1460 boots" or "Nike Air Max 90"</p>
        </div>
      )}
    </div>
  )
}

export default AmazonPage
