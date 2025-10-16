import './AIInsights.css'

export default function AIInsights({
  insights,
  onGenerateInsights,
  loading = false,
  error = '',
  hasReviews = false,
  reviews = []
}) {
  const handleGenerate = () => {
    if (!loading && onGenerateInsights) {
      onGenerateInsights()
    }
  }

  const downloadReport = async () => {
    if (!insights) return

    try {
      const response = await fetch('http://localhost:5000/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          insights,
          location: reviews[0]?.author || 'Dr. Martens Store'
        })
      })
      const data = await response.json()

      if (data.success) {
        const blob = new Blob([data.report], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `DrMartens-Report-${new Date().toISOString().split('T')[0]}.md`
        a.click()
        URL.revokeObjectURL(url)
      }
    } catch (err) {
      console.error('Error downloading report:', err)
    }
  }

  if (!insights) {
    return (
      <div className="ai-insights-card">
        <div className="insights-header">
          <h2 className="insights-title">
            <span className="brain-icon">🧠</span>
            AI-Powered Insights
          </h2>
        </div>
        <p className="insights-description">
          Generate deep insights using GPT-4 to understand customer sentiment, identify trends, and get actionable recommendations.
        </p>
        {error && <div className="error-banner">{error}</div>}
        <button
          onClick={handleGenerate}
          disabled={loading || !hasReviews || !onGenerateInsights}
          className="btn-generate"
        >
          {loading ? '🔄 Analyzing Reviews...' : '✨ Generate AI Insights'}
        </button>
      </div>
    )
  }

  return (
    <div className="insights-container">
      <div className="summary-card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="brain-icon">🧠</span>
            Executive Summary
          </h2>
          <div className="card-actions">
            <button
              onClick={handleGenerate}
              className="btn-regenerate"
              disabled={loading}
            >
              {loading ? '🔄 Refreshing...' : '🔄 Regenerate Insights'}
            </button>
            <button onClick={downloadReport} className="btn-download">
              📥 Download Report
            </button>
          </div>
        </div>
        <p className="summary-text">{insights.executive_summary}</p>
      </div>

      <div className="section-card">
        <h3 className="section-title">
          <span>📊</span> Key Themes
        </h3>
        <div className="themes-grid">
          {insights.key_themes?.map((theme, idx) => (
            <div key={idx} className="theme-card">
              <div className="theme-header">
                <h4 className="theme-name">{theme.theme}</h4>
                <span className={`sentiment-badge ${theme.sentiment}`}>
                  {theme.sentiment}
                </span>
              </div>
              <p className="theme-description">{theme.description}</p>
              <span className="theme-frequency">Frequency: {theme.frequency}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="dual-section">
        <div className="section-card strengths-card">
          <h3 className="section-title">
            <span>💪</span> Customer Strengths
          </h3>
          <div className="items-list">
            {insights.strengths?.map((strength, idx) => (
              <div key={idx} className="item-card">
                <div className="item-header">
                  <h4 className="item-title">{strength.strength}</h4>
                  <span className={`impact-badge ${strength.impact}`}>
                    {strength.impact} impact
                  </span>
                </div>
                <p className="item-example">"{strength.examples}"</p>
              </div>
            ))}
          </div>
        </div>

        <div className="section-card pain-points-card">
          <h3 className="section-title">
            <span>⚠️</span> Pain Points
          </h3>
          <div className="items-list">
            {insights.pain_points?.map((pain, idx) => (
              <div key={idx} className="item-card">
                <div className="item-header">
                  <h4 className="item-title">{pain.issue}</h4>
                  <span className={`severity-badge ${pain.severity}`}>
                    {pain.severity}
                  </span>
                </div>
                <p className="item-recommendation">
                  <strong>Solution:</strong> {pain.recommendation}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="section-card recommendations-card">
        <h3 className="section-title">
          <span>💡</span> Actionable Recommendations
        </h3>
        <div className="recommendations-list">
          {insights.recommendations?.map((rec, idx) => (
            <div key={idx} className="recommendation-card">
              <div className="recommendation-content">
                <span className={`priority-badge ${rec.priority}`}>
                  {rec.priority.toUpperCase()}
                </span>
                <div className="recommendation-details">
                  <h4 className="recommendation-action">{rec.action}</h4>
                  <p className="recommendation-impact">{rec.expected_impact}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="section-card">
        <h3 className="section-title">
          <span>👥</span> Customer Personas
        </h3>
        <div className="personas-grid">
          {insights.customer_personas?.map((persona, idx) => (
            <div key={idx} className="persona-card">
              <h4 className="persona-type">{persona.type}</h4>
              <p className="persona-characteristics">{persona.characteristics}</p>
              <p className="persona-needs"><strong>Values:</strong> {persona.needs}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="section-card competitive-card">
        <h3 className="section-title">🎯 Competitive Intelligence</h3>
        <div className="competitive-content">
          <div className="competitive-item">
            <h4 className="competitive-subtitle">Unique Strengths</h4>
            <p>{insights.competitive_insights?.unique_strengths}</p>
          </div>
          <div className="competitive-item">
            <h4 className="competitive-subtitle">Areas for Improvement</h4>
            <p>{insights.competitive_insights?.areas_for_improvement}</p>
          </div>
          <div className="competitive-item">
            <h4 className="competitive-subtitle">Market Positioning</h4>
            <p>{insights.competitive_insights?.market_positioning}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
