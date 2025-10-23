import { useState } from 'react'
import axios from 'axios'
import { Search, ShoppingBag, MessageSquare, TrendingUp, TrendingDown, Minus, Loader } from 'lucide-react'
import Statistics from '../components/Statistics'
import SentimentChart from '../components/SentimentChart'
import ReviewCard from '../components/ReviewCard'
import AIInsights from '../components/AIInsights'
import ChatAssistant from '../components/ChatAssistant'
import CompetitiveAnalysisView from '../components/CompetitiveAnalysisView'
import './UnifiedSearch.css'

function UnifiedSearch() {
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Combined data
  const [allReviews, setAllReviews] = useState([])
  const [youtubeData, setYoutubeData] = useState(null)
  const [amazonData, setAmazonData] = useState(null)
  const [redditData, setRedditData] = useState(null)
  const [trustpilotData, setTrustpilotData] = useState(null)
  const [statistics, setStatistics] = useState(null)
  const [activeFilter, setActiveFilter] = useState('all')
  
  // Competitive analysis
  const [isCompetitiveAnalysis, setIsCompetitiveAnalysis] = useState(false)
  const [competitiveData, setCompetitiveData] = useState(null)
  
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
    
    // Reset all states
    setAllReviews([])
    setYoutubeData(null)
    setAmazonData(null)
    setRedditData(null)
    setTrustpilotData(null)
    setStatistics(null)
    setInsights(null)
    setInsightsLoading(false)
    setInsightsError('')
    setIsCompetitiveAnalysis(false)
    setCompetitiveData(null)

    try {
      // Check if query contains comparison keywords
      const comparisonKeywords = [' vs ', ' versus ', ' vs. ', ' compared to ', ' or ']
      const isComparison = comparisonKeywords.some(keyword => 
        searchQuery.toLowerCase().includes(keyword)
      )

      if (isComparison) {
        // ========================================
        // COMPETITIVE ANALYSIS MODE
        // ========================================
        console.log('🆚 Running competitive analysis...')
        setIsCompetitiveAnalysis(true)

        const response = await axios.post('http://localhost:5000/api/competitive-analysis', {
          query: searchQuery
        })

        if (response.data && response.data.success) {
          setCompetitiveData(response.data)
          console.log('✅ Competitive analysis complete')
        } else {
          throw new Error(response.data.error || 'Competitive analysis failed')
        }

      } else {
        // ========================================
        // NORMAL SINGLE-PRODUCT SEARCH MODE
        // ========================================
        console.log('🔍 Running normal product search...')
        setIsCompetitiveAnalysis(false)

      // Search all four sources in parallel
      const [youtubeResponse, amazonResponse, redditResponse, trustpilotResponse] = await Promise.all([
        // YouTube search
        axios.post('http://localhost:5000/api/youtube/search', {
          query: searchQuery,
          max_reviews: 50
        }).catch(err => {
          console.log('YouTube search failed:', err.message)
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
        }),
        
        // Reddit search
        axios.post('http://localhost:5000/api/reddit/search', {
          query: searchQuery,
          max_reviews: 50
        }).catch(err => {
          console.log('Reddit search failed:', err.message)
          return { error: true, message: err.message }
        }),
        
        // Trustpilot search
        axios.post('http://localhost:5000/api/trustpilot/search', {
          query: searchQuery,
          max_reviews: 50
        }).catch(err => {
          console.log('Trustpilot search failed:', err.message)
          return { error: true, message: err.message }
        })
      ])
      
      console.log('YouTube response:', youtubeResponse.error ? 'FAILED' : 'SUCCESS')
      console.log('Amazon response:', amazonResponse.error ? 'FAILED' : 'SUCCESS')
      console.log('Reddit response:', redditResponse.error ? 'FAILED' : 'SUCCESS')
      console.log('Trustpilot response:', trustpilotResponse.error ? 'FAILED' : 'SUCCESS')

      const combinedReviews = []
      let youtubeReviews = []
      let amazonReviews = []
      let redditReviews = []
      let trustpilotReviews = []

      // Process YouTube results
      if (!youtubeResponse.error && youtubeResponse.data?.success) {
        console.log('Processing YouTube results...')
        setYoutubeData({
          total: youtubeResponse.data.total,
          source: 'youtube'
        })

        youtubeReviews = youtubeResponse.data.reviews.map(review => ({
          ...review,
          source: 'youtube'
        }))
        console.log(`✅ Got ${youtubeReviews.length} YouTube reviews`)
      } else {
        console.log('⚠️ No YouTube results found')
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

      // Process Reddit results
      if (!redditResponse.error && redditResponse.data?.success) {
        console.log('Processing Reddit results...')
        setRedditData({
          total: redditResponse.data.total,
          source: 'reddit'
        })

        redditReviews = redditResponse.data.reviews.map(review => ({
          ...review,
          source: 'reddit',
          rating: 0 // Reddit uses upvotes, not star ratings
        }))
        console.log(`✅ Got ${redditReviews.length} Reddit discussions`)
      } else {
        console.log('⚠️ No Reddit results found')
      }

      // Process Trustpilot results
      if (!trustpilotResponse.error && trustpilotResponse.data?.success) {
        console.log('Processing Trustpilot results...')
        setTrustpilotData({
          total: trustpilotResponse.data.total,
          source: 'trustpilot'
        })

        trustpilotReviews = trustpilotResponse.data.reviews.map(review => ({
          ...review,
          source: 'trustpilot'
        }))
        console.log(`✅ Got ${trustpilotReviews.length} Trustpilot reviews`)
      } else {
        console.log('⚠️ No Trustpilot results found')
      }

      // Combine all reviews
      combinedReviews.push(...youtubeReviews, ...amazonReviews, ...redditReviews, ...trustpilotReviews)
      console.log(`📊 Total combined reviews: ${combinedReviews.length}`)
      console.log('YouTube reviews:', youtubeReviews.length)
      console.log('Amazon reviews:', amazonReviews.length)
      console.log('Reddit reviews:', redditReviews.length)
      console.log('Trustpilot reviews:', trustpilotReviews.length)
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
          youtube_count: youtubeReviews.length,
          amazon_count: amazonReviews.length,
          reddit_count: redditReviews.length,
          trustpilot_count: trustpilotReviews.length,
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
        console.log('⚠️ No reviews found from any source')
        setError('No reviews found from any source. Try a different search query.')
      }
      
      } // End of normal search mode

    } catch (err) {
      console.error('❌ Search error:', err)
      console.error('Error stack:', err.stack)
      setError(err.message || 'An error occurred while searching. Please try again.')
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
        <h1>🔍 Brand Sentiment Agent</h1>
        <p className="feature-hint">
          💡 Try: "Dr Martens 1460" or "Dr Martens 1460 vs Timberland 6 inch"
        </p>
        
        <div className="search-box">
          <input
            type="text"
            placeholder="Search for product or compare (e.g., 'Product A vs Product B')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            disabled={loading}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? <Loader className="spinner" /> : <Search />}
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner">
            <Loader className="spinner" size={48} />
            <p>
              {isCompetitiveAnalysis 
                ? 'Running competitive analysis across all sources...' 
                : 'Agent is searching...'}
            </p>
            <p className="loading-subtext">This may take 30-60 seconds</p>
          </div>
        </div>
      )}

      {/* COMPETITIVE ANALYSIS VIEW */}
      {isCompetitiveAnalysis && competitiveData && !loading && (
        <CompetitiveAnalysisView data={competitiveData} />
      )}

      {/* NORMAL SINGLE-PRODUCT VIEW */}
      {!isCompetitiveAnalysis && !loading && allReviews.length > 0 && (
        <>
          {console.log('🎨 Rendering results section with', allReviews.length, 'reviews')}
          {/* Source Cards */}
          <div className="source-summary">
            <h2>📊 Search Results</h2>
            <div className="source-cards">
              {youtubeData && (
                <div className="source-card youtube-card">
                  <div className="source-icon">
                    🎥
                  </div>
                  <div className="source-info">
                    <h3>YouTube Reviews</h3>
                    <p className="source-address">Video Comments & Reviews</p>
                    <div className="source-stats">
                      <span>💬 {statistics?.youtube_count || 0} comments analyzed</span>
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

              {redditData && (
                <div className="source-card reddit-card">
                  <div className="source-icon">
                    <MessageSquare size={32} />
                  </div>
                  <div className="source-info">
                    <h3>Reddit Discussions</h3>
                    <p className="source-address">Multiple Subreddits</p>
                    <div className="source-stats">
                      <span>💬 {statistics?.reddit_count || 0} discussions analyzed</span>
                    </div>
                  </div>
                </div>
              )}

              {trustpilotData && (
                <div className="source-card trustpilot-card">
                  <div className="source-icon">
                    ⭐
                  </div>
                  <div className="source-info">
                    <h3>Trustpilot Reviews</h3>
                    <p className="source-address">Verified Customer Reviews</p>
                    <div className="source-stats">
                      <span>✓ {statistics?.trustpilot_count || 0} verified reviews</span>
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
