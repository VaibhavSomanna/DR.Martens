import React, { useState } from 'react';
import './CompetitiveAnalysisView.css';
import { Star, Users, TrendingUp, TrendingDown, ChevronDown, ChevronUp } from 'lucide-react';

const CompetitiveAnalysisView = ({ data }) => {
  const { product_1, product_2, ai_insights, comparison_summary } = data;
  const [expandedAttribute, setExpandedAttribute] = useState(null);
  
  const toggleAttribute = (attribute) => {
    setExpandedAttribute(expandedAttribute === attribute ? null : attribute);
  };
  
  return (
    <div className="competitive-analysis-container">
      <div className="competitive-header">
        <h2>🆚 COMPETITIVE ANALYSIS</h2>
        <p className="comparison-query">
          <span className="product-name">{product_1.name}</span>
          <span className="vs-text">VS</span>
          <span className="product-name">{product_2.name}</span>
        </p>
        <div className="total-reviews">
          Based on <strong>{comparison_summary.total_reviews_compared}</strong> customer reviews from 4 sources
        </div>
      </div>
      
      {/* Side-by-Side Comparison Cards */}
      <div className="comparison-grid">
        <ProductComparisonCard 
          product={product_1}
        />
        
        <div className="vs-divider">VS</div>
        
        <ProductComparisonCard 
          product={product_2}
        />
      </div>
      
      {/* Comparison Summary Stats */}
      <div className="comparison-stats">
        <div className="stat-card">
          <h4>Sentiment Difference</h4>
          <div className="stat-value">
            {comparison_summary.sentiment_difference > 0 ? '+' : ''}{comparison_summary.sentiment_difference}%
          </div>
          <p className="stat-label">
            {Math.abs(comparison_summary.sentiment_difference) > 10 ? 'Significant' : 'Marginal'} positive sentiment gap
          </p>
        </div>
        <div className="stat-card">
          <h4>Total Reviews Analyzed</h4>
          <div className="stat-value">
            {comparison_summary.total_reviews_compared}
          </div>
          <p className="stat-label">
            From 4 independent sources
          </p>
        </div>
      </div>
      
      {/* Head-to-Head Attribute Comparison */}
      {ai_insights?.head_to_head_comparison && (
        <div className="attribute-comparison">
          <h3>📊 CRITERION-BY-CRITERION COMPARISON</h3>
          <p className="comparison-hint">Who leads where? Click on any attribute to see detailed breakdown</p>
          <div className="count-explainer-note">
            <small>
              💡 <strong>Note:</strong> Reviews can mention multiple attributes, so totals across categories may exceed the review count. 
              "Overall Satisfaction" captures general sentiment without specific attribute mentions.
            </small>
          </div>
          <div className="attributes-grid">
            {Object.entries(ai_insights.head_to_head_comparison).map(([attribute, data]) => {
              const attributeIcons = {
                'quality': '⭐',
                'comfort': '😊',
                'durability': '🛡️',
                'style': '👔',
                'price': '💰',
                'value_for_money': '💵',
                'break_in_period': '👟',
                'overall_satisfaction': '🎯'
              };
              const icon = attributeIcons[attribute] || '📍';
              const isExpanded = expandedAttribute === attribute;
              
              return (
                <div key={attribute} className={`attribute-card ${isExpanded ? 'expanded' : ''}`}>
                  <div className="attribute-header" onClick={() => toggleAttribute(attribute)}>
                    <h4>{icon} {attribute.replace(/_/g, ' ').toUpperCase()}</h4>
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </div>
                  <div className="attribute-winner">🏆 {data.winner}</div>
                  <p className="attribute-reasoning">{data.reasoning}</p>
                  
                  {isExpanded && (
                    <div className="attribute-details">
                      <div className="brand-details dr-martens-details">
                        <h5>👞 {product_1.name}</h5>
                        
                        {/* Sentiment Metrics */}
                        {data.dr_martens_sentiment && (data.dr_martens_sentiment.positive_count > 0 || data.dr_martens_sentiment.negative_count > 0) && (
                          <div className="sentiment-metrics">
                            <div className="sentiment-bar-container">
                              <div className="sentiment-bar">
                                <div 
                                  className="sentiment-positive-bar" 
                                  style={{width: `${data.dr_martens_sentiment.positive_pct || 0}%`}}
                                ></div>
                                <div 
                                  className="sentiment-negative-bar" 
                                  style={{width: `${data.dr_martens_sentiment.negative_pct || 0}%`}}
                                ></div>
                              </div>
                              <div className="sentiment-counts">
                                <span className="positive-count">
                                  ✅ {data.dr_martens_sentiment.positive_count} positive ({data.dr_martens_sentiment.positive_pct?.toFixed(1) || 0}%)
                                </span>
                                <span className="negative-count">
                                  ❌ {data.dr_martens_sentiment.negative_count} negative ({data.dr_martens_sentiment.negative_pct?.toFixed(1) || 0}%)
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        <div className="pros-cons">
                          <div className="pros">
                            <strong>✅ Positives:</strong>
                            <ul>
                              {getAttributeDetails(attribute, product_1.name, data, ai_insights, 'positive').map((point, i) => (
                                <li key={i}>{point}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="cons">
                            <strong>⚠️ Negatives:</strong>
                            <ul>
                              {getAttributeDetails(attribute, product_1.name, data, ai_insights, 'negative').map((point, i) => (
                                <li key={i}>{point}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                      
                      <div className="brand-details competitor-details">
                        <h5>🏢 {product_2.name}</h5>
                        
                        {/* Sentiment Metrics */}
                        {data.competitor_sentiment && (data.competitor_sentiment.positive_count > 0 || data.competitor_sentiment.negative_count > 0) && (
                          <div className="sentiment-metrics">
                            <div className="sentiment-bar-container">
                              <div className="sentiment-bar">
                                <div 
                                  className="sentiment-positive-bar" 
                                  style={{width: `${data.competitor_sentiment.positive_pct || 0}%`}}
                                ></div>
                                <div 
                                  className="sentiment-negative-bar" 
                                  style={{width: `${data.competitor_sentiment.negative_pct || 0}%`}}
                                ></div>
                              </div>
                              <div className="sentiment-counts">
                                <span className="positive-count">
                                  ✅ {data.competitor_sentiment.positive_count} positive ({data.competitor_sentiment.positive_pct?.toFixed(1) || 0}%)
                                </span>
                                <span className="negative-count">
                                  ❌ {data.competitor_sentiment.negative_count} negative ({data.competitor_sentiment.negative_pct?.toFixed(1) || 0}%)
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        <div className="pros-cons">
                          <div className="pros">
                            <strong>✅ Positives:</strong>
                            <ul>
                              {getAttributeDetails(attribute, product_2.name, data, ai_insights, 'positive').map((point, i) => (
                                <li key={i}>{point}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="cons">
                            <strong>⚠️ Negatives:</strong>
                            <ul>
                              {getAttributeDetails(attribute, product_2.name, data, ai_insights, 'negative').map((point, i) => (
                                <li key={i}>{point}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Strengths & Weaknesses */}
      {ai_insights && (
        <div className="strengths-weaknesses">
          <div className="product-analysis dr-martens-section">
            <h3>👞 DR. MARTENS ANALYSIS</h3>
            <div className="strengths">
              <h4>✅ COMPETITIVE STRENGTHS</h4>
              <ul>
                {ai_insights.dr_martens_strengths?.map((strength, i) => (
                  <li key={i}>{strength}</li>
                ))}
              </ul>
            </div>
            <div className="weaknesses">
              <h4>⚠️ AREAS FOR IMPROVEMENT</h4>
              <ul>
                {ai_insights.dr_martens_weaknesses?.map((weakness, i) => (
                  <li key={i}>{weakness}</li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="product-analysis competitor-section">
            <h3>🏢 COMPETITOR ANALYSIS</h3>
            <div className="strengths">
              <h4>✅ COMPETITOR STRENGTHS (Threats)</h4>
              <ul>
                {ai_insights.competitor_strengths?.map((strength, i) => (
                  <li key={i}>{strength}</li>
                ))}
              </ul>
            </div>
            <div className="weaknesses">
              <h4>⚠️ COMPETITOR WEAKNESSES (Opportunities)</h4>
              <ul>
                {ai_insights.competitor_weaknesses?.map((weakness, i) => (
                  <li key={i}>{weakness}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
      
      {/* Competitive Position Analysis */}
      {ai_insights && (
        <div className="competitive-position">
          <div className="position-card advantages">
            <h3>🎯 DR. MARTENS COMPETITIVE ADVANTAGES</h3>
            <p>{ai_insights.competitive_advantages}</p>
          </div>
          <div className="position-card threats">
            <h3>⚡ COMPETITIVE THREATS TO ADDRESS</h3>
            <p>{ai_insights.competitive_threats}</p>
          </div>
        </div>
      )}
      
      {/* Target Audience */}
      {ai_insights?.target_audience && (
        <div className="target-audience-section">
          <h3>🎯 MARKET SEGMENTATION</h3>
          <div className="audience-grid">
            <div className="audience-card dr-martens-card">
              <h4>👞 Dr. Martens Wins With</h4>
              <p>{ai_insights.target_audience.dr_martens_best_for}</p>
            </div>
            <div className="audience-card competitor-card">
              <h4>🏢 Competitor Wins With</h4>
              <p>{ai_insights.target_audience.competitor_best_for}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Price-Value Analysis */}
      {ai_insights?.price_value_analysis && (
        <div className="price-value-section">
          <h3>💰 VALUE PROPOSITION COMPARISON</h3>
          <p>{ai_insights.price_value_analysis}</p>
        </div>
      )}
      
      {/* Strategic Recommendations */}
      {ai_insights?.strategic_recommendations_for_dr_martens && (
        <div className="strategic-recommendations dr-martens-focus">
          <h3>💡 STRATEGIC RECOMMENDATIONS FOR DR. MARTENS</h3>
          <div className="recommendations-content">
            <p className="recommendations-text">{ai_insights.strategic_recommendations_for_dr_martens}</p>
          </div>
        </div>
      )}
      
      {/* Market Positioning */}
      {ai_insights?.market_positioning && (
        <div className="market-positioning">
          <h3>📈 DR. MARTENS MARKET POSITIONING</h3>
          <p>{ai_insights.market_positioning}</p>
        </div>
      )}
      
      {/* Customer Preference Insights */}
      {ai_insights?.customer_preference_insights && (
        <div className="customer-preferences">
          <h3>👥 CUSTOMER DECISION DRIVERS</h3>
          <p>{ai_insights.customer_preference_insights}</p>
        </div>
      )}
      
      {/* Executive Summary */}
      {ai_insights?.executive_summary && (
        <div className="executive-summary dr-martens-executive">
          <h3>📋 EXECUTIVE SUMMARY FOR DR. MARTENS LEADERSHIP</h3>
          <p className="executive-text">{ai_insights.executive_summary}</p>
        </div>
      )}
    </div>
  );
};

const ProductComparisonCard = ({ product }) => {
  const analysis = product.analysis;
  
  return (
    <div className="product-comparison-card">
      <h3>{product.name.toUpperCase()}</h3>
      
      <div className="product-stats">
        <div className="stat-item">
          <Users size={24} />
          <span className="stat-value">{analysis.total_reviews}</span>
          <span className="stat-label">Total Reviews</span>
        </div>
      </div>
      
      <div className="sentiment-breakdown">
        <div className="sentiment-row">
          <TrendingUp size={16} className="positive-icon" />
          <div className="sentiment-bar positive" style={{width: `${analysis.positive_percentage}%`}}>
            {analysis.positive_percentage}%
          </div>
        </div>
        <div className="sentiment-row">
          <span className="neutral-icon">—</span>
          <div className="sentiment-bar neutral" style={{width: `${analysis.neutral_percentage}%`}}>
            {analysis.neutral_percentage}%
          </div>
        </div>
        <div className="sentiment-row">
          <TrendingDown size={16} className="negative-icon" />
          <div className="sentiment-bar negative" style={{width: `${analysis.negative_percentage}%`}}>
            {analysis.negative_percentage}%
          </div>
        </div>
      </div>
      
      <div className="sources-breakdown">
        <h4>DATA SOURCES</h4>
        <div className="sources-list">
          <div className="source-item">
            <span className="source-icon">🎥</span>
            <span className="source-name">YouTube</span>
            <span className="source-count">{analysis.sources.youtube}</span>
          </div>
          <div className="source-item">
            <span className="source-icon">🛒</span>
            <span className="source-name">Amazon</span>
            <span className="source-count">{analysis.sources.amazon}</span>
          </div>
          <div className="source-item">
            <span className="source-icon">💬</span>
            <span className="source-name">Reddit</span>
            <span className="source-count">{analysis.sources.reddit}</span>
          </div>
          <div className="source-item">
            <span className="source-icon">⭐</span>
            <span className="source-name">Trustpilot</span>
            <span className="source-count">{analysis.sources.trustpilot}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to extract attribute-specific details from AI insights
const getAttributeDetails = (attribute, productName, attributeData, aiInsights, type) => {
  const isDrMartens = productName.toLowerCase().includes('dr') || productName.toLowerCase().includes('martens');
  
  // Map generic strengths/weaknesses to specific attributes
  const attributeKeywords = {
    'quality': ['quality', 'craftsmanship', 'construction', 'materials', 'built', 'made'],
    'comfort': ['comfort', 'comfortable', 'cushion', 'soft', 'cozy', 'feel'],
    'durability': ['durability', 'durable', 'last', 'wear', 'tough', 'sturdy', 'longevity'],
    'style': ['style', 'look', 'design', 'aesthetic', 'fashion', 'appearance'],
    'price': ['price', 'cost', 'expensive', 'cheap', 'affordable', 'value'],
    'value_for_money': ['value', 'worth', 'price', 'investment', 'money'],
    'break_in_period': ['break', 'stiff', 'painful', 'soften', 'wear in', 'comfort'],
    'overall_satisfaction': ['overall', 'recommend', 'love', 'happy', 'satisfied', 'disappointed', 'best', 'worst']
  };
  
  const keywords = attributeKeywords[attribute] || [];
  const points = [];
  
  // Get the appropriate list based on product
  const strengthsList = isDrMartens ? aiInsights.dr_martens_strengths : aiInsights.competitor_strengths;
  const weaknessList = isDrMartens ? aiInsights.dr_martens_weaknesses : aiInsights.competitor_weaknesses;
  
  if (type === 'positive' && strengthsList) {
    // Find strengths related to this attribute
    const related = strengthsList.filter(item => 
      keywords.some(keyword => item.toLowerCase().includes(keyword))
    );
    
    if (related.length > 0) {
      points.push(...related);
    } else if (attributeData.winner.toLowerCase().includes(productName.toLowerCase().split(' ')[0])) {
      // If this product wins but no specific strength, extract from reasoning
      points.push(attributeData.reasoning.split('.')[0] + '.');
    } else {
      points.push(`Competitive in ${attribute.replace(/_/g, ' ')}`);
    }
  }
  
  if (type === 'negative' && weaknessList) {
    // Find weaknesses related to this attribute
    const related = weaknessList.filter(item => 
      keywords.some(keyword => item.toLowerCase().includes(keyword))
    );
    
    if (related.length > 0) {
      points.push(...related);
    } else if (!attributeData.winner.toLowerCase().includes(productName.toLowerCase().split(' ')[0])) {
      // If this product loses, extract concern from reasoning
      const sentences = attributeData.reasoning.split('.');
      if (sentences.length > 1) {
        points.push(sentences[1].trim() + '.');
      } else {
        points.push(`Less favorable ${attribute.replace(/_/g, ' ')} compared to competitor`);
      }
    } else {
      points.push(`Minor concerns reported by some customers`);
    }
  }
  
  return points.slice(0, 3); // Limit to 3 points
};

export default CompetitiveAnalysisView;
