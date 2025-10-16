import React from 'react'
import { MapPin, ShoppingBag, MessageSquare, CheckCircle } from 'lucide-react'
import './ReviewCard.css'

function ReviewCard({ review, showSource = false, showVerified = false }) {
  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '#10b981'
      case 'negative':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const getSentimentEmoji = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '😊'
      case 'negative':
        return '😞'
      default:
        return '😐'
    }
  }

  const renderStars = (rating) => {
    return '⭐'.repeat(rating)
  }

  // Handle both old and new data structure
  const sentiment = review.sentiment?.sentiment || review.sentiment
  const polarity = review.sentiment?.polarity || review.polarity
  const subjectivity = review.sentiment?.subjectivity || review.subjectivity
  const reviewTime = review.time || review.date

  return (
    <div className="review-card">
      <div className="review-header">
        <div className="author-info">
          <span className="author-name">{review.author}</span>
          <span className="review-time">{reviewTime}</span>
          {showSource && review.source && (
            <span className={`source-badge source-${review.source}`}>
              {review.source === 'google_maps' ? (
                <><MapPin size={14} /> Google Maps</>
              ) : review.source === 'reddit' ? (
                <><MessageSquare size={14} /> r/{review.subreddit}</>
              ) : (
                <><ShoppingBag size={14} /> Amazon</>
              )}
            </span>
          )}
          {showVerified && review.verified && (
            <span className="verified-badge">
              <CheckCircle size={14} /> Verified
            </span>
          )}
        </div>
        <div className="review-rating">
          {review.rating > 0 ? renderStars(review.rating) : review.score !== undefined && (
            <span className="reddit-score">⬆️ {review.score} upvotes</span>
          )}
        </div>
      </div>

      {review.title && (
        <div className="review-title">
          {review.title}
        </div>
      )}

      <div className="review-text">
        {review.text}
      </div>

      <div className="sentiment-info">
        <div 
          className="sentiment-badge"
          style={{ backgroundColor: getSentimentColor(sentiment) }}
        >
          {getSentimentEmoji(sentiment)} {sentiment?.toUpperCase()}
        </div>
        <div className="sentiment-scores">
          <span className="score-item">
            Polarity: <strong>{polarity}</strong>
          </span>
          <span className="score-item">
            Subjectivity: <strong>{subjectivity}</strong>
          </span>
        </div>
      </div>
    </div>
  )
}

export default ReviewCard
