from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from textblob import TextBlob
from datetime import datetime
from openai import OpenAI
import json
from amazon_scraper import scrape_amazon_reviews
from reddit_scraper import scrape_reddit_reviews
from youtube_scraper import scrape_youtube_reviews
from trustpilot_scraper import scrape_trustpilot_reviews

load_dotenv()

app = Flask(__name__)
CORS(app)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def analyze_sentiment(text, rating=None, use_ai=True):
    """
    Analyze sentiment using AI (GPT-4o) for accurate multi-language context understanding
    Falls back to keyword + TextBlob if AI unavailable
    """
    # Try AI-based sentiment analysis first (multilingual + context-aware)
    if use_ai and client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Faster, cheaper model for sentiment
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analyzer. Analyze the overall sentiment of product reviews considering context, sarcasm, and mixed emotions. Respond with ONLY a JSON object: {\"sentiment\": \"positive\"|\"negative\"|\"neutral\", \"confidence\": 0.0-1.0, \"reasoning\": \"brief explanation\"}"
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this review sentiment:\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            sentiment = result.get('sentiment', 'neutral')
            confidence = result.get('confidence', 0.5)
            
            # Calculate polarity based on sentiment and confidence
            if sentiment == 'positive':
                polarity = 0.3 + (confidence * 0.7)
            elif sentiment == 'negative':
                polarity = -0.3 - (confidence * 0.7)
            else:
                polarity = 0.0
            
            return {
                "sentiment": sentiment,
                "polarity": round(polarity, 2),
                "subjectivity": 0.5,  # Not calculated by AI
                "confidence": round(confidence, 2),
                "method": "ai"
            }
        except Exception as e:
            print(f"⚠️ AI sentiment analysis failed, using fallback: {e}")
    
    # Fallback: Keyword + TextBlob analysis
    try:
        # Enhanced keyword lists for better detection
        negative_keywords = [
            'disappointed', 'frustrat', 'terrible', 'awful', 'horrible', 'worst',
            'broken', 'defective', 'poor', 'bad', 'never', 'waste', 'useless',
            'angry', 'annoying', 'annoyed', 'upset', 'unhappy', 'unsatisfied',
            'misleading', 'lied', 'fake', 'scam', 'fraud', 'avoid', 'warning',
            'regret', 'hate', 'disappoint', 'not recommend', 'don\'t buy',
            'cheap', 'poorly made', 'fell apart', 'uncomfortable', 'painful'
        ]
        
        positive_keywords = [
            'excellent', 'amazing', 'love', 'perfect', 'great', 'awesome',
            'fantastic', 'wonderful', 'best', 'recommend', 'happy', 'satisfied',
            'quality', 'comfortable', 'beautiful', 'impressed', 'exceeded',
            'worth', 'favorite', 'highly recommend', 'outstanding', 'superb',
            'pleased', 'delighted', 'brilliant', 'sturdy', 'durable', 'stylish'
        ]
        
        text_lower = text.lower()
        
        # Count keyword matches
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        
        # Use TextBlob for polarity
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Decision logic (prioritize text content over rating)
        # 1. Strong keyword signal wins
        if positive_count > negative_count + 2:
            sentiment = "positive"
            polarity = max(polarity, 0.3)
        elif negative_count > positive_count + 2:
            sentiment = "negative"
            polarity = min(polarity, -0.3)
        # 2. Moderate keyword signal
        elif positive_count > negative_count:
            sentiment = "positive"
            polarity = max(polarity, 0.2)
        elif negative_count > positive_count:
            sentiment = "negative"
            polarity = min(polarity, -0.2)
        # 3. TextBlob polarity as fallback (more lenient thresholds)
        elif polarity > 0.05:
            sentiment = "positive"
        elif polarity < -0.05:
            sentiment = "negative"
        # 4. Use rating only if text is truly neutral
        elif rating is not None:
            if rating <= 2:
                sentiment = "negative"
                polarity = -0.3
            elif rating >= 4:
                sentiment = "positive"
                polarity = 0.3
            else:
                sentiment = "neutral"
        else:
            sentiment = "neutral"
            
        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 2),
            "subjectivity": round(blob.sentiment.subjectivity, 2),
            "method": "keyword+textblob"
        }
    except Exception as e:
        return {
            "sentiment": "neutral",
            "polarity": 0,
            "subjectivity": 0,
            "error": str(e),
            "method": "error"
        }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/youtube/search', methods=['POST'])
def search_youtube():
    """Search YouTube for product review videos and extract comments"""
    try:
        data = request.json
        query = data.get('query', '')
        max_reviews = data.get('max_reviews', 50)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"🎥 YouTube search for: {query}")
        
        reviews = scrape_youtube_reviews(query, max_reviews=max_reviews)
        
        if not reviews:
            return jsonify({
                'success': True,
                'reviews': [],
                'total': 0,
                'source': 'youtube',
                'error': 'No YouTube reviews found'
            })
        
        # Analyze sentiment for each review
        analyzed_reviews = []
        for review in reviews:
            sentiment_data = analyze_sentiment(review.get('text', ''))
            review['sentiment'] = sentiment_data
            analyzed_reviews.append(review)
        
        return jsonify({
            'success': True,
            'reviews': analyzed_reviews,
            'total': len(analyzed_reviews),
            'source': 'youtube'
        })
        
    except Exception as e:
        print(f"Error in YouTube search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': True,
            'reviews': [],
            'total': 0,
            'source': 'youtube',
            'error': str(e)
        })

@app.route('/api/trustpilot/search', methods=['POST'])
def search_trustpilot():
    """Search Trustpilot for product reviews"""
    try:
        data = request.json
        query = data.get('query', 'Dr Martens')
        max_reviews = data.get('max_reviews', 50)
        
        print(f"🔍 Trustpilot search for: {query}")
        
        reviews = scrape_trustpilot_reviews(query, max_reviews=max_reviews)
        
        if not reviews:
            return jsonify({
                'success': True,
                'reviews': [],
                'total': 0,
                'source': 'trustpilot',
                'error': 'No Trustpilot reviews found'
            })
        
        # Analyze sentiment for each review
        analyzed_reviews = []
        for review in reviews:
            sentiment_data = analyze_sentiment(review.get('text', ''), rating=review.get('rating'))
            review['sentiment'] = sentiment_data
            analyzed_reviews.append(review)
        
        return jsonify({
            'success': True,
            'reviews': analyzed_reviews,
            'total': len(analyzed_reviews),
            'source': 'trustpilot'
        })
        
    except Exception as e:
        print(f"Error in Trustpilot search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': True,
            'reviews': [],
            'total': 0,
            'source': 'trustpilot',
            'error': str(e)
        })

@app.route('/api/search', methods=['POST'])
def search():
    """Deprecated - kept for backwards compatibility"""
    return jsonify({
        "success": False,
        "error": "Google Places API has been removed. Use YouTube or Trustpilot endpoints instead.",
        "alternatives": [
            "/api/youtube/search",
            "/api/trustpilot/search",
            "/api/amazon/search",
            "/api/reddit/search"
        ]
    }), 400

@app.route('/api/reviews', methods=['POST'])
def get_reviews():
    """Deprecated - Google Places API removed"""
    return jsonify({
        "error": "Google Places API has been removed. Use /api/youtube/search or /api/trustpilot/search instead."
    }), 400

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze text sentiment"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({
            "error": "text is required"
        }), 400
    
    sentiment_data = analyze_sentiment(text)
    
    return jsonify({
        "success": True,
        "text": text,
        "analysis": sentiment_data
    })

@app.route('/api/ai-insights', methods=['POST'])
def get_ai_insights():
    """Generate comprehensive AI insights from reviews using OpenAI"""
    try:
        data = request.json
        reviews = data.get('reviews', [])
        
        if not reviews:
            return jsonify({'error': 'No reviews provided'}), 400
        
        if not client:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Prepare reviews text - handle both sentiment formats
        reviews_text = []
        for r in reviews[:30]:
            rating = r.get('rating', 'N/A')
            text = r.get('text', 'No text')
            
            # Handle different sentiment formats
            sentiment_data = r.get('sentiment')
            if isinstance(sentiment_data, dict):
                sentiment = sentiment_data.get('sentiment', 'unknown')
            elif isinstance(sentiment_data, str):
                sentiment = sentiment_data
            else:
                sentiment = 'unknown'
            
            reviews_text.append(f"Rating: {rating}/5\nReview: {text}\nSentiment: {sentiment}")
        
        reviews_text = "\n\n".join(reviews_text)
        
        prompt = f"""Analyze these Dr. Martens customer reviews and provide a comprehensive business intelligence report:

{reviews_text}

Provide a detailed analysis in the following JSON format:
{{
    "executive_summary": "2-3 sentence high-level overview of customer sentiment and key findings",
    "key_themes": [
        {{"theme": "Theme name", "sentiment": "positive/negative/mixed", "frequency": "high/medium/low", "description": "Brief explanation"}},
        // 4-6 themes
    ],
    "strengths": [
        {{"strength": "What customers love", "impact": "high/medium/low", "examples": "Quote or paraphrase"}},
        // 3-4 strengths
    ],
    "pain_points": [
        {{"issue": "Problem area", "severity": "high/medium/low", "recommendation": "Actionable solution"}},
        // 3-4 pain points
    ],
    "recommendations": [
        {{"priority": "high/medium/low", "action": "Specific recommendation", "expected_impact": "What it will achieve"}},
        // 4-5 recommendations
    ],
    "customer_personas": [
        {{"type": "Customer type", "characteristics": "Key traits", "needs": "What they value most"}},
        // 2-3 personas
    ],
    "sentiment_drivers": {{
        "positive_drivers": ["Factor 1", "Factor 2", "Factor 3"],
        "negative_drivers": ["Factor 1", "Factor 2", "Factor 3"]
    }},
    "competitive_insights": {{
        "unique_strengths": "What sets Dr. Martens apart",
        "areas_for_improvement": "Where competitors might be winning",
        "market_positioning": "How customers perceive the brand"
    }},
    "trend_analysis": {{
        "emerging_patterns": "What's changing in customer sentiment",
        "seasonal_factors": "Any time-based patterns observed",
        "prediction": "What to watch for next"
    }}
}}

Be specific, data-driven, and actionable. Use customer language where relevant. Return ONLY the JSON object, no additional text."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business intelligence analyst specializing in customer sentiment analysis. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        insights = json.loads(response.choices[0].message.content)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'generated_at': datetime.now().isoformat(),
            'reviews_analyzed': len(reviews)
        })
        
    except Exception as e:
        print(f"Error generating insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_reviews():
    """Chat assistant for asking questions about reviews using OpenAI"""
    try:
        data = request.json
        question = data.get('question', '')
        reviews = data.get('reviews', [])
        chat_history = data.get('history', [])
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if not client:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        reviews_text = "\n\n".join([
            f"Rating: {r.get('rating', 'N/A')}/5\nReview: {r.get('text', 'No text')}"
            for r in reviews[:30]
        ])
        
        messages = [
            {"role": "system", "content": f"""You are an AI assistant analyzing Dr. Martens customer reviews. 
            
Here are the reviews to analyze:

{reviews_text}

Answer questions based on these reviews. Be specific, cite examples when relevant, and provide actionable insights."""}
        ]
        
        # Add chat history
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return jsonify({
            'success': True,
            'answer': response.choices[0].message.content,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reddit/search', methods=['POST'])
def reddit_search():
    """Search Reddit for product/place discussions"""
    try:
        data = request.json
        query = data.get('query', '')
        max_reviews = data.get('max_reviews', 50)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"🔍 Reddit search for: {query}")
        
        # Scrape Reddit reviews
        reviews = scrape_reddit_reviews(query, max_reviews=max_reviews)
        
        if not reviews:
            return jsonify({
                'success': False,
                'error': 'No Reddit discussions found',
                'reviews': []
            }), 200
        
        # Analyze sentiment for each review using AI
        analyzed_reviews = []
        for review in reviews:
            sentiment_result = analyze_sentiment(review.get('text', ''))
            analyzed_reviews.append({
                'author': review.get('author'),
                'text': review.get('text'),
                'title': review.get('title'),
                'date': review.get('date'),
                'score': review.get('score'),
                'url': review.get('url'),
                'subreddit': review.get('subreddit'),
                'type': review.get('type'),
                'sentiment': sentiment_result['sentiment'],
                'polarity': sentiment_result['polarity'],
                'subjectivity': sentiment_result.get('subjectivity', 0.5)
            })
        
        return jsonify({
            'success': True,
            'reviews': analyzed_reviews,
            'total': len(analyzed_reviews),
            'source': 'reddit'
        })
        
    except Exception as e:
        print(f"❌ Reddit search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'reviews': []
        }), 200

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate a professional PDF-ready report using OpenAI"""
    try:
        data = request.json
        insights = data.get('insights', {})
        location = data.get('location', 'Dr. Martens Store')
        
        if not client:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        prompt = f"""Create a professional executive report based on these insights for {location}:

{json.dumps(insights, indent=2)}

Format as a clean, professional business report with:
- Executive Summary
- Key Findings (bullet points)
- Detailed Analysis (sections with headers)
- Actionable Recommendations (prioritized list)
- Conclusion

Use markdown formatting for structure. Make it suitable for presentation to executives."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional business report writer specializing in customer experience analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        return jsonify({
            'success': True,
            'report': response.choices[0].message.content,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combined-analysis', methods=['POST'])
def combined_analysis():
    """
    Get reviews from all sources: YouTube, Amazon, Reddit, and Trustpilot
    Returns separate review lists but combined AI insights
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_reviews = data.get('max_reviews', 30)
        
        if not query:
            return jsonify({
                'error': 'Query is required'
            }), 400
        
        youtube_reviews = []
        amazon_reviews = []
        reddit_reviews = []
        trustpilot_reviews = []
        
        # Fetch YouTube reviews
        try:
            print(f"🎥 Fetching YouTube reviews for: {query}")
            youtube_data = scrape_youtube_reviews(query, max_reviews=max_reviews)
            
            for review in youtube_data:
                sentiment_data = analyze_sentiment(review.get('text', ''))
                youtube_reviews.append({
                    'author': review.get('author', 'Anonymous'),
                    'text': review.get('text', ''),
                    'date': review.get('date', 'Unknown'),
                    'likes': review.get('likes', 0),
                    'video_title': review.get('video_title', ''),
                    'video_url': review.get('video_url', ''),
                    'sentiment': sentiment_data['sentiment'],
                    'polarity': sentiment_data['polarity'],
                    'subjectivity': sentiment_data['subjectivity'],
                    'source': 'youtube'
                })
        except Exception as e:
            print(f"⚠️ YouTube fetching failed: {e}")
        
        # Fetch Amazon reviews
        try:
            print(f"🛒 Fetching Amazon reviews for: {query}")
            product_info, reviews = scrape_amazon_reviews(query, max_reviews=max_reviews)
            
            for review in reviews:
                rating = review.get('rating')
                sentiment_data = analyze_sentiment(review.get('text', ''), rating=rating)
                amazon_reviews.append({
                    'author': review.get('author', 'Anonymous'),
                    'rating': rating or 0,
                    'title': review.get('title', ''),
                    'text': review.get('text', ''),
                    'date': review.get('date', 'Unknown'),
                    'verified': review.get('verified', False),
                    'sentiment': sentiment_data['sentiment'],
                    'polarity': sentiment_data['polarity'],
                    'subjectivity': sentiment_data['subjectivity'],
                    'source': 'amazon'
                })
        except Exception as e:
            print(f"⚠️ Amazon scraping failed: {e}")
        
        # Fetch Reddit reviews
        try:
            print(f"📱 Fetching Reddit reviews for: {query}")
            reddit_data = scrape_reddit_reviews(query, max_posts=max_reviews)
            
            for post in reddit_data:
                sentiment_data = analyze_sentiment(post.get('text', ''))
                reddit_reviews.append({
                    'author': post.get('author', 'Anonymous'),
                    'title': post.get('title', ''),
                    'text': post.get('text', ''),
                    'score': post.get('score', 0),
                    'subreddit': post.get('subreddit', ''),
                    'date': post.get('date', 'Unknown'),
                    'sentiment': sentiment_data['sentiment'],
                    'polarity': sentiment_data['polarity'],
                    'subjectivity': sentiment_data['subjectivity'],
                    'source': 'reddit'
                })
        except Exception as e:
            print(f"⚠️ Reddit fetching failed: {e}")
        
        # Fetch Trustpilot reviews
        try:
            print(f"� Fetching Trustpilot reviews for: {query}")
            trustpilot_data = scrape_trustpilot_reviews(query, max_reviews=max_reviews)
            
            for review in trustpilot_data:
                sentiment_data = analyze_sentiment(review.get('text', ''), rating=review.get('rating'))
                trustpilot_reviews.append({
                    'author': review.get('author', 'Anonymous'),
                    'rating': review.get('rating', 0),
                    'title': review.get('title', ''),
                    'text': review.get('text', ''),
                    'date': review.get('date', 'Unknown'),
                    'verified': review.get('verified', False),
                    'sentiment': sentiment_data['sentiment'],
                    'polarity': sentiment_data['polarity'],
                    'subjectivity': sentiment_data['subjectivity'],
                    'source': 'trustpilot'
                })
        except Exception as e:
            print(f"⚠️ Trustpilot fetching failed: {e}")
        
        # Combine all reviews for overall statistics
        all_reviews = youtube_reviews + amazon_reviews + reddit_reviews + trustpilot_reviews
        
        if not all_reviews:
            return jsonify({
                'error': 'No reviews found from any source'
            }), 404
        
        # Calculate combined statistics
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        total_polarity = 0
        total_subjectivity = 0
        total_rating = 0
        rating_count = 0
        
        for review in all_reviews:
            sentiment_counts[review['sentiment']] += 1
            total_polarity += review['polarity']
            total_subjectivity += review['subjectivity']
            if review.get('rating', 0) > 0:
                total_rating += review['rating']
                rating_count += 1
        
        statistics = {
            'total_reviews': len(all_reviews),
            'youtube_reviews_count': len(youtube_reviews),
            'amazon_reviews_count': len(amazon_reviews),
            'reddit_reviews_count': len(reddit_reviews),
            'trustpilot_reviews_count': len(trustpilot_reviews),
            'sentiment_distribution': sentiment_counts,
            'average_polarity': round(total_polarity / len(all_reviews), 2),
            'average_subjectivity': round(total_subjectivity / len(all_reviews), 2),
            'average_rating': round(total_rating / rating_count, 2) if rating_count > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'youtube': {
                'reviews': youtube_reviews,
                'count': len(youtube_reviews)
            },
            'amazon': {
                'reviews': amazon_reviews,
                'count': len(amazon_reviews)
            },
            'reddit': {
                'reviews': reddit_reviews,
                'count': len(reddit_reviews)
            },
            'trustpilot': {
                'reviews': trustpilot_reviews,
                'count': len(trustpilot_reviews)
            },
            'combined_statistics': statistics,
            'all_reviews': all_reviews  # For AI insights
        })
        
    except Exception as e:
        print(f"❌ Error in combined analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/amazon/search', methods=['POST'])
def amazon_search():
    """Search for Amazon product and get reviews"""
    try:
        data = request.get_json()
        product_query = data.get('query', '')
        max_reviews = data.get('max_reviews', 50)
        use_demo = data.get('use_demo', False)  # Option to use demo data
        
        if not product_query:
            return jsonify({'error': 'Product query is required'}), 400
        
        print(f"🛒 Searching Amazon for: {product_query}")
        
        # Try real scraping first, fallback to demo data if blocked
        product_info = None
        reviews = []
        
        try:
            product_info, reviews = scrape_amazon_reviews(product_query, max_reviews=max_reviews)
            print(f"✅ Found {len(reviews)} Amazon reviews")
        except Exception as scrape_error:
            print(f"⚠️ Amazon scraping error: {scrape_error}")
            reviews = []
        
        if not reviews:
            return jsonify({
                'success': False,
                'error': 'No reviews found for this product'
            }), 404
        
        # Analyze sentiment for each review
        analyzed_reviews = []
        for review in reviews:
            rating = review.get('rating', 0)
            sentiment_data = analyze_sentiment(review.get('text', ''), rating=rating)
            analyzed_reviews.append({
                'author': review.get('author', 'Anonymous'),
                'rating': rating,
                'title': review.get('title', ''),
                'text': review.get('text', ''),
                'date': review.get('date', 'Unknown'),
                'verified': review.get('verified', False),
                'sentiment': sentiment_data['sentiment'],
                'polarity': sentiment_data['polarity'],
                'subjectivity': sentiment_data['subjectivity']
            })
        
        return jsonify({
            'success': True,
            'product_info': product_info,
            'reviews': analyzed_reviews,
            'total': len(analyzed_reviews),
            'is_demo_data': use_demo
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in Amazon search: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Provide helpful error message
        if "Could not access Amazon" in error_msg:
            return jsonify({
                'error': 'Unable to connect to Amazon. Please check your internet connection and try again.',
                'details': error_msg
            }), 503
        elif "Could not find product" in error_msg or "Could not find any products" in error_msg:
            return jsonify({
                'error': f'No products found for "{product_query}". Try a different search term.',
                'details': error_msg
            }), 404
        else:
            return jsonify({
                'error': 'An error occurred while scraping Amazon reviews. The site may be temporarily unavailable.',
                'details': error_msg[:300]
            }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
