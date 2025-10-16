import { useState } from 'react'
import axios from 'axios'
import { Search, MapPin, ShoppingBag, TrendingUp, TrendingDown, Minus, Loader } from 'lucide-react'
import Statistics from '../components/Statistics'
import SentimentChart from '../components/SentimentChart'
import ReviewCard from '../components/ReviewCard'
import AIInsights from '../components/AIInsights'
import ChatAssistant from '../components/ChatAssistant'
import './UnifiedSearch.css'

function UnifiedSearch() {
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Combined data
  const [allReviews, setAllReviews] = useState([])
  const [googleData, setGoogleData] = useState(null)
  const [amazonData, setAmazonData] = useState(null)
  const [statistics, setStatistics] = useState(null)
  const [activeFilter, setActiveFilter] = useState('all')
  
  // AI features
  const [insights, setInsights] = useState(null)
  const [insightsLoading, setInsightsLoading] = useState(false)
  const [insightsError, setInsightsError] = useState('')
  const [showChat, setShowChat] = useState(false)

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query')
      return
    }

    setLoading(true)
    setError('')
    setAllReviews([])
    setGoogleData(null)
    setAmazonData(null)
  setStatistics(null)
  setInsights(null)
  setInsightsLoading(false)
  setInsightsError('')

    try {
      // Search both sources in parallel
      const [googleResponse, amazonResponse] = await Promise.all([
        // Google Maps search
        axios.post('http://localhost:5000/api/search', {
          query: searchQuery,
          use_scraping: true
        }).catch(err => {
          console.log('Google search failed:', err.message)
          return { error: true, message: err.message }
        }),
        
        // Amazon search
        axios.post('http://localhost:5000/api/amazon/search', {
          query: searchQuery,
          max_reviews: 50,
          use_demo: false // Try real first, will fallback automatically
        }).catch(err => {
          console.log('Amazon search failed:', err.message)
          return { error: true, message: err.message }
        })
      ])
      
      console.log('Google response:', googleResponse.error ? 'FAILED' : 'SUCCESS')
      console.log('Amazon response:', amazonResponse.error ? 'FAILED' : 'SUCCESS')

      const combinedReviews = []
      let googleReviews = []
      let amazonReviews = []

      // Process Google Maps results
      if (!googleResponse.error && googleResponse.data?.results?.length > 0) {
        console.log('Processing Google Maps results...')
        const place = googleResponse.data.results[0]
        setGoogleData({
          name: place.name,
          address: place.formatted_address,
          rating: place.rating,
          total_reviews: place.user_ratings_total
        })

        // Fetch Google reviews
        try {
          const reviewsResponse = await axios.post('http://localhost:5000/api/reviews', {
            place_id: place.place_id,
            use_scraping: true
          })
          
          if (reviewsResponse.data?.reviews) {
            googleReviews = reviewsResponse.data.reviews.map(review => ({
              ...review,
              source: 'google_maps'
            }))
            console.log(`✅ Got ${googleReviews.length} Google reviews`)
          }
        } catch (err) {
          console.error('Error fetching Google reviews:', err)
        }
      } else {
        console.log('⚠️ No Google Maps results found')
      }

      // Process Amazon results
      if (!amazonResponse.error && amazonResponse.data?.success) {
        console.log('Processing Amazon results...')
        setAmazonData({
          name: amazonResponse.data.product_info.name,
          rating: amazonResponse.data.product_info.rating,
          total_reviews: amazonResponse.data.product_info.total_ratings,
          is_demo: amazonResponse.data.is_demo_data
        })

        amazonReviews = amazonResponse.data.reviews.map(review => ({
          ...review,
          source: 'amazon'
        }))
        console.log(`✅ Got ${amazonReviews.length} Amazon reviews`)
      } else {
        console.log('⚠️ No Amazon results found')
      }

      // Combine all reviews
      combinedReviews.push(...googleReviews, ...amazonReviews)
      console.log(`📊 Total combined reviews: ${combinedReviews.length}`)
      console.log('Google reviews:', googleReviews.length)
      console.log('Amazon reviews:', amazonReviews.length)
      console.log('Combined array:', combinedReviews)
      
      setAllReviews(combinedReviews)
      console.log('✅ setAllReviews() called')

      // Calculate combined statistics
      if (combinedReviews.length > 0) {
        console.log('✅ Calculating statistics...')
        const sentimentCounts = combinedReviews.reduce((acc, review) => {
          const sentiment = review.sentiment?.sentiment || review.sentiment || 'neutral'
          acc[sentiment] = (acc[sentiment] || 0) + 1
          return acc
        }, {})

        const ratingValues = combinedReviews
          .map(review => review.rating)
          .filter(ratingValue => typeof ratingValue === 'number' && ratingValue > 0)

        const avgRating = ratingValues.length > 0
          ? ratingValues.reduce((sum, ratingValue) => sum + ratingValue, 0) / ratingValues.length
          : null

        setStatistics({
          total: combinedReviews.length,
          google_count: googleReviews.length,
          amazon_count: amazonReviews.length,
          average_rating: avgRating ? avgRating.toFixed(1) : null,
          sentiment: sentimentCounts,
          positive: sentimentCounts.positive || 0,
          negative: sentimentCounts.negative || 0,
          neutral: sentimentCounts.neutral || 0
        })

        // Generate AI insights
        console.log('🤖 Generating AI insights...')
        await generateInsights(combinedReviews)
        console.log('✅ Search complete! Ready to render.')
      } else {
        console.log('⚠️ No reviews found from either source')
        setError('No reviews found from either source. Try a different search query.')
      }

    } catch (err) {
      console.error('❌ Search error:', err)
      console.error('Error stack:', err.stack)
      setError('An error occurred while searching. Please try again.')
    } finally {
      console.log('🏁 Setting loading=false')
      setLoading(false)
    }
  }

  const generateInsights = async (reviews) => {
    if (!reviews || reviews.length === 0) {
      setInsights(null)
      return
    }

    setInsightsLoading(true)
    setInsightsError('')

    try {
      const response = await axios.post('http://localhost:5000/api/ai-insights', {
        reviews: reviews.map(r => ({
          text: r.text,
          rating: r.rating,
          sentiment: r.sentiment?.sentiment || r.sentiment
        }))
      })
      if (response.data?.success && response.data.insights) {
        setInsights(response.data.insights)
      } else {
        setInsights(null)
        setInsightsError(response.data?.error || 'Could not generate insights for this query.')
      }
    } catch (err) {
      console.error('Error generating insights:', err)
      setInsights(null)
      setInsightsError('Failed to generate AI insights. Please try again.')
    } finally {
      setInsightsLoading(false)
    }
  }

  const getFilteredReviews = () => {
    if (activeFilter === 'all') return allReviews
    return allReviews.filter(review => {
      const sentiment = review.sentiment?.sentiment || review.sentiment || 'neutral'
      return sentiment === activeFilter
    })
  }

  const getSentimentStats = (filter) => {
    const reviews = filter === 'all' ? allReviews : allReviews.filter(r => {
      const sentiment = r.sentiment?.sentiment || r.sentiment || 'neutral'
      return sentiment === filter
    })
    return reviews.length
  }

  console.log('🔄 Component render - loading:', loading, 'allReviews.length:', allReviews.length, 'error:', error)

  return (
    <div className="unified-search">
      <div className="hero-section">
        <h1>🔍 Unified Review Search</h1>
        <p>Search once, get insights from Google Maps AND Amazon</p>
        
        <div className="search-box">
          <input
            type="text"
            placeholder="Search for products or stores (e.g., 'Dr Martens 1460 boots' or 'Dr Martens Camden London')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            disabled={loading}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? <Loader className="spinner" /> : <Search />}
            {loading ? 'Searching...' : 'Search Both Sources'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner">
            <Loader className="spinner" size={48} />
            <p>Searching Google Maps and Amazon...</p>
            <p className="loading-subtext">This may take 30-60 seconds</p>
          </div>
        </div>
      )}

      {!loading && allReviews.length > 0 && (
        <>
          {console.log('🎨 Rendering results section with', allReviews.length, 'reviews')}
          {/* Source Cards */}
          <div className="source-summary">
            <h2>📊 Search Results</h2>
            <div className="source-cards">
              {googleData && (
                <div className="source-card google-card">
                  <div className="source-icon">
                    <MapPin size={32} />
                  </div>
                  <div className="source-info">
                    <h3>{googleData.name}</h3>
                    <p className="source-address">{googleData.address}</p>
                    <div className="source-stats">
                      <span>⭐ {googleData.rating}/5</span>
                      <span>• {statistics?.google_count || 0} reviews analyzed</span>
                    </div>
                  </div>
                </div>
              )}

              {amazonData && (
                <div className="source-card amazon-card">
                  <div className="source-icon">
                    <ShoppingBag size={32} />
                  </div>
                  <div className="source-info">
                    <h3>{amazonData.name}</h3>
                    {amazonData.is_demo && (
                      <p className="demo-badge">📊 Demo Data</p>
                    )}
                    <div className="source-stats">
                      <span>⭐ {amazonData.rating}/5</span>
                      <span>• {statistics?.amazon_count || 0} reviews analyzed</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Concise Summary */}
          <div className="concise-summary">
            <h2>📋 Quick Summary</h2>
            <div className="summary-cards">
              <div className="summary-card">
                <div className="summary-number">{statistics?.total || 0}</div>
                <div className="summary-label">Total Reviews</div>
              </div>
              <div className="summary-card">
                <div className="summary-number">{statistics?.average_rating ?? 'N/A'}</div>
                <div className="summary-label">Average Rating</div>
              </div>
              <div className="summary-card positive">
                <div className="summary-number">{statistics?.positive || 0}</div>
                <div className="summary-label">
                  <TrendingUp size={16} /> Positive
                </div>
              </div>
              <div className="summary-card negative">
                <div className="summary-number">{statistics?.negative || 0}</div>
                <div className="summary-label">
                  <TrendingDown size={16} /> Negative
                </div>
              </div>
              <div className="summary-card neutral">
                <div className="summary-number">{statistics?.neutral || 0}</div>
                <div className="summary-label">
                  <Minus size={16} /> Neutral
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Summary with AI Snapshot */}
          <div className="detailed-summary">
            <h2>🤖 AI Snapshot</h2>
            {insightsLoading && (
              <p className="insights-status">Generating AI summary…</p>
            )}
            {!insightsLoading && insightsError && (
              <div className="error-message insights-error">{insightsError}</div>
            )}
            {insights && !insightsError && (
              <div className="executive-summary-card">
                <h3>Executive Summary</h3>
                <p>{insights.executive_summary}</p>
              </div>
            )}
            <div className="insights-grid">
              <div className="insight-section">
                <SentimentChart statistics={statistics} />
              </div>
              <div className="insight-section">
                <Statistics statistics={statistics} />
              </div>
            </div>
          </div>

          {/* Review Filters */}
          <div className="reviews-section">
            <div className="reviews-header">
              <h2>📝 All Reviews ({getFilteredReviews().length})</h2>
              <div className="filter-tabs">
                <button
                  className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('all')}
                >
                  All ({allReviews.length})
                </button>
                <button
                  className={`filter-tab positive ${activeFilter === 'positive' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('positive')}
                >
                  <TrendingUp size={16} /> Positive ({getSentimentStats('positive')})
                </button>
                <button
                  className={`filter-tab negative ${activeFilter === 'negative' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('negative')}
                >
                  <TrendingDown size={16} /> Negative ({getSentimentStats('negative')})
                </button>
                <button
                  className={`filter-tab neutral ${activeFilter === 'neutral' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('neutral')}
                >
                  <Minus size={16} /> Neutral ({getSentimentStats('neutral')})
                </button>
              </div>
            </div>

            <div className="reviews-grid">
              {getFilteredReviews().map((review, index) => (
                <ReviewCard
                  key={`${review.source}-${index}`}
                  review={review}
                  showSource={true}
                  showVerified={review.source === 'amazon'}
                />
              ))}
            </div>
          </div>

          {/* Chat Assistant */}
          <div className="deep-insights-section">
            <h2>🧠 Key Insights & Recommendations</h2>
            <AIInsights
              insights={insights}
              loading={insightsLoading}
              error={insightsError}
              hasReviews={allReviews.length > 0}
              reviews={allReviews}
              onGenerateInsights={() => generateInsights(allReviews)}
            />
          </div>

          {/* Chat Assistant */}
          <div className="chat-section">
            <button 
              className="chat-toggle"
              onClick={() => setShowChat(!showChat)}
            >
              {showChat ? '✖ Close Chat' : '💬 Ask Questions About Reviews'}
            </button>
            {showChat && <ChatAssistant reviews={allReviews} />}
          </div>
        </>
      )}

      {!loading && allReviews.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h2>Search for Products or Stores</h2>
          <p>Enter a product name (e.g., "Dr Martens boots") or store location (e.g., "Dr Martens Camden London")</p>
          <p>We'll search both Google Maps and Amazon to give you comprehensive insights!</p>
        </div>
      )}
    </div>
  )
}

export default UnifiedSearch
