import { useState } from 'react'
import axios from 'axios'
import { MapPin, ShoppingBag, TrendingUp, BarChart3 } from 'lucide-react'
import './CombinedAnalysis.css'
import ReviewCard from '../components/ReviewCard'
import Statistics from '../components/Statistics'
import SentimentChart from '../components/SentimentChart'
import AIInsights from '../components/AIInsights'
import ChatAssistant from '../components/ChatAssistant'

const API_URL = 'http://localhost:5000/api'

function CombinedAnalysis() {
  const [googleQuery, setGoogleQuery] = useState('Dr. Martens Camden London')
  const [amazonQuery, setAmazonQuery] = useState('Dr Martens 1460 boots')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null)

  const handleAnalyze = async () => {
    if (!googleQuery.trim() && !amazonQuery.trim()) {
      setError('Please enter at least one query (Google or Amazon)')
      return
    }

    setLoading(true)
    setError(null)
    setData(null)

    try {
      const response = await axios.post(`${API_URL}/combined-analysis`, {
        google_query: googleQuery.trim(),
        amazon_query: amazonQuery.trim(),
        max_reviews: 30
      })

      if (response.data.success) {
        setData(response.data)
      } else {
        setError('Failed to fetch reviews')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while fetching reviews')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }



  return (
    <div className="combined-analysis">
      <header className="header-combined">
        <div className="header-content">
          <h1>🔄 Combined Review Analysis</h1>
          <p>Analyze reviews from both Google Maps locations and Amazon products</p>
        </div>
      </header>

      <div className="container">
        {/* Search Section */}
        <div className="search-section">
          <h2>🔍 Search Queries</h2>
          
          <div className="search-grid">
            <div className="search-card">
              <div className="search-card-header">
                <MapPin className="icon-google" size={24} />
                <h3>Google Maps Location</h3>
              </div>
              <input
                type="text"
                value={googleQuery}
                onChange={(e) => setGoogleQuery(e.target.value)}
                placeholder="e.g., Dr. Martens Camden London"
                className="search-input"
              />
              <p className="search-hint">Store name and location</p>
            </div>

            <div className="search-card">
              <div className="search-card-header">
                <ShoppingBag className="icon-amazon" size={24} />
                <h3>Amazon Product</h3>
              </div>
              <input
                type="text"
                value={amazonQuery}
                onChange={(e) => setAmazonQuery(e.target.value)}
                placeholder="e.g., Dr Martens 1460 boots"
                className="search-input"
              />
              <p className="search-hint">Product name or model</p>
            </div>
          </div>

          <button 
            onClick={handleAnalyze} 
            disabled={loading}
            className="analyze-button"
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                Analyzing...
              </>
            ) : (
              <>
                <TrendingUp size={20} />
                Analyze Reviews
              </>
            )}
          </button>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Fetching reviews from Google Maps and Amazon...</p>
            <p className="loading-subtext">This may take 1-2 minutes</p>
          </div>
        )}

        {/* Results */}
        {data && (
          <>
            {/* Overall Statistics */}
            <div className="stats-overview">
              <h2>📊 Overall Summary</h2>
              <div className="stats-grid">
                <div className="stat-card stat-total">
                  <BarChart3 size={32} />
                  <div>
                    <h3>{data.combined_statistics.total_reviews}</h3>
                    <p>Total Reviews</p>
                  </div>
                </div>
                <div className="stat-card stat-google">
                  <MapPin size={32} />
                  <div>
                    <h3>{data.google.count}</h3>
                    <p>Google Maps</p>
                  </div>
                </div>
                <div className="stat-card stat-amazon">
                  <ShoppingBag size={32} />
                  <div>
                    <h3>{data.amazon.count}</h3>
                    <p>Amazon</p>
                  </div>
                </div>
                <div className="stat-card stat-rating">
                  <span className="star-icon">⭐</span>
                  <div>
                    <h3>{data.combined_statistics.average_rating.toFixed(1)}</h3>
                    <p>Avg Rating</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sentiment Chart */}
            <div className="chart-section">
              <SentimentChart sentimentCounts={data.combined_statistics.sentiment_distribution} />
            </div>

            {/* AI Insights - Key Summary Only */}
            <div className="insights-section">
              <AIInsights reviews={data.all_reviews} />
            </div>

            {/* Source Information Cards */}
            <div className="source-cards">
              <div className="source-card google-card">
                <div className="source-card-header">
                  <MapPin size={32} />
                  <h3>Google Maps Location</h3>
                </div>
                {data.google.place_info && (
                  <>
                    <h4>{data.google.place_info.name}</h4>
                    <p className="source-detail">{data.google.place_info.address}</p>
                    <div className="source-stats">
                      <span>⭐ {data.google.place_info.rating}/5</span>
                      <span>{data.google.count} reviews analyzed</span>
                    </div>
                  </>
                )}
                <p className="source-note">
                  ℹ️ To view individual Google Maps reviews, visit the <strong>Google Maps</strong> page
                </p>
              </div>

              <div className="source-card amazon-card">
                <div className="source-card-header">
                  <ShoppingBag size={32} />
                  <h3>Amazon Product</h3>
                </div>
                {data.amazon.product_info && (
                  <>
                    <h4>{data.amazon.product_info.name.substring(0, 80)}...</h4>
                    <div className="source-stats">
                      <span>⭐ {data.amazon.product_info.rating}/5</span>
                      <span>{data.amazon.count} reviews analyzed</span>
                    </div>
                  </>
                )}
                <p className="source-note">
                  ℹ️ To view individual Amazon reviews, visit the <strong>Amazon</strong> page
                </p>
              </div>
            </div>

            {/* Chat Assistant with All Reviews */}
            <ChatAssistant reviews={data.all_reviews} />
          </>
        )}
      </div>
    </div>
  )
}

export default CombinedAnalysis
