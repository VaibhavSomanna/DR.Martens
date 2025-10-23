import React from 'react'
import './Statistics.css'

function Statistics({ statistics }) {
  if (!statistics) {
    return null
  }

  const total = statistics.total ?? 0
  const positive = statistics.positive ?? statistics.sentiment?.positive ?? 0
  const neutral = statistics.neutral ?? statistics.sentiment?.neutral ?? 0
  const negative = statistics.negative ?? statistics.sentiment?.negative ?? 0

  const getPercentage = (count) => {
    return total > 0
      ? ((count / total) * 100).toFixed(1)
      : '0.0'
  }

  const avgRatingValue = Number(statistics.average_rating ?? statistics.avg_rating ?? 0)
  const averageRating = avgRatingValue.toFixed(1)

  const polarityBase = statistics.avg_polarity ?? statistics.sentiment_polarity
  const computedPolarity = total > 0 ? (positive - negative) / total : 0
  const avgPolarityValue = Number.isFinite(Number(polarityBase)) ? Number(polarityBase) : computedPolarity
  const avgPolarity = avgPolarityValue.toFixed(2)

  const polarityDescriptor = avgPolarityValue > 0.1 ? 'Mostly Positive'
    : avgPolarityValue < -0.1 ? 'Mostly Negative'
    : 'Mostly Neutral'

  return (
    <div className="statistics-container">
      <h2>📊 Analysis Overview</h2>
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{total}</div>
          <div className="stat-label">Total Reviews</div>
        </div>

        <div className="stat-card positive">
          <div className="stat-icon">😊</div>
          <div className="stat-value">{positive}</div>
          <div className="stat-label">Positive ({getPercentage(positive)}%)</div>
          <div className="stat-bar">
            <div 
              className="stat-bar-fill positive-fill" 
              style={{ width: `${getPercentage(positive)}%` }}
            ></div>
          </div>
        </div>

        <div className="stat-card neutral">
          <div className="stat-icon">😐</div>
          <div className="stat-value">{neutral}</div>
          <div className="stat-label">Neutral ({getPercentage(neutral)}%)</div>
          <div className="stat-bar">
            <div 
              className="stat-bar-fill neutral-fill" 
              style={{ width: `${getPercentage(neutral)}%` }}
            ></div>
          </div>
        </div>

        <div className="stat-card negative">
          <div className="stat-icon">😞</div>
          <div className="stat-value">{negative}</div>
          <div className="stat-label">Negative ({getPercentage(negative)}%)</div>
          <div className="stat-bar">
            <div 
              className="stat-bar-fill negative-fill" 
              style={{ width: `${getPercentage(negative)}%` }}
            ></div>
          </div>
        </div>

        <div className="stat-card polarity">
          <div className="stat-icon">📈</div>
          <div className="stat-value">{avgPolarity}</div>
          <div className="stat-label">Avg Polarity</div>
          <div className="polarity-info">
            {polarityDescriptor}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Statistics
