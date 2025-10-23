from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from textblob import TextBlob
from datetime import datetime
from openai import OpenAI
import json
import time
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
            reddit_data = scrape_reddit_reviews(query, max_reviews=max_reviews)
            
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

@app.route('/api/competitive-analysis', methods=['POST'])
def competitive_analysis():
    """
    Compare two products side-by-side
    Triggered when query contains 'vs' or 'versus'
    Example: "Dr Martens 1460 vs Timberland 6 inch"
    """
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        # Check if query contains comparison keywords
        comparison_keywords = [' vs ', ' versus ', ' vs. ', ' compared to ', ' or ']
        is_comparison = any(keyword in query.lower() for keyword in comparison_keywords)
        
        if not is_comparison:
            return jsonify({
                'error': 'Query does not contain comparison keywords (vs, versus, etc.)',
                'success': False
            }), 400
        
        print(f"🆚 Competitive Analysis Request: {query}")
        
        # Split query into two products
        products = []
        for keyword in comparison_keywords:
            if keyword in query.lower():
                products = query.lower().split(keyword, 1)
                break
        
        product_1 = products[0].strip()
        product_2 = products[1].strip()
        
        print(f"📊 Product 1: {product_1}")
        print(f"📊 Product 2: {product_2}")
        
        # Parallel data collection for both products
        from concurrent.futures import ThreadPoolExecutor
        
        def fetch_all_reviews(product_name):
            """Fetch reviews from all sources for a product"""
            product_reviews = {
                'product_name': product_name,
                'youtube': [],
                'amazon': [],
                'reddit': [],
                'trustpilot': []
            }
            
            try:
                # YouTube
                try:
                    print(f"🎥 Fetching YouTube for: {product_name}")
                    youtube_reviews = scrape_youtube_reviews(f"{product_name} review", max_reviews=30)
                    product_reviews['youtube'] = youtube_reviews or []
                    print(f"✅ YouTube: {len(product_reviews['youtube'])} reviews")
                except Exception as e:
                    print(f"⚠️ YouTube error for {product_name}: {e}")
                
                # Add delay before next source
                print("⏳ Waiting 2 seconds before next source...")
                time.sleep(2)
                
                # Amazon
                try:
                    print(f"🛒 Fetching Amazon for: {product_name}")
                    product_info, amazon_reviews = scrape_amazon_reviews(product_name, max_reviews=20)
                    product_reviews['amazon'] = amazon_reviews or []
                    print(f"✅ Amazon: {len(product_reviews['amazon'])} reviews")
                except Exception as e:
                    print(f"⚠️ Amazon error for {product_name}: {e}")
                
                # Add delay before next source
                print("⏳ Waiting 2 seconds before next source...")
                time.sleep(2)
                
                # Reddit
                try:
                    print(f"💬 Fetching Reddit for: {product_name}")
                    reddit_reviews = scrape_reddit_reviews(product_name, max_reviews=30)
                    product_reviews['reddit'] = reddit_reviews or []
                    print(f"✅ Reddit: {len(product_reviews['reddit'])} discussions")
                except Exception as e:
                    print(f"⚠️ Reddit error for {product_name}: {e}")
                
                # Add longer delay before Trustpilot (Selenium is more sensitive)
                print("⏳ Waiting 3 seconds before Trustpilot...")
                time.sleep(3)
                
                # Trustpilot (for all supported brands) with retry and fallback
                print(f"⭐ Fetching Trustpilot for: {product_name}")
                trustpilot_reviews = []
                try:
                    trustpilot_reviews = scrape_trustpilot_reviews(product_name, max_reviews=30, max_retries=2)
                    
                    if len(trustpilot_reviews) == 0:
                        print(f"⚠️ Trustpilot returned 0 reviews for {product_name}")
                        print(f"   Analysis will continue with other sources")
                    else:
                        product_reviews['trustpilot'] = trustpilot_reviews
                        print(f"✅ Trustpilot: {len(trustpilot_reviews)} reviews")
                        
                except Exception as e:
                    print(f"⚠️ Trustpilot scraping failed completely for {product_name}: {str(e)[:100]}")
                    print(f"   Continuing with other review sources...")
                    product_reviews['trustpilot'] = []
                
            except Exception as e:
                print(f"❌ Error fetching reviews for {product_name}: {e}")
            
            return product_reviews
        
        # Fetch reviews for both products in parallel
        print("🔄 Starting parallel data collection...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_product1 = executor.submit(fetch_all_reviews, product_1)
            future_product2 = executor.submit(fetch_all_reviews, product_2)
            
            product1_data = future_product1.result()
            product2_data = future_product2.result()
        
        print("✅ Data collection complete")
        
        # Analyze sentiment for both products
        def analyze_product_reviews(product_data):
            """Analyze all reviews for a product"""
            all_reviews = []
            all_reviews.extend(product_data['youtube'])
            all_reviews.extend(product_data['amazon'])
            all_reviews.extend(product_data['reddit'])
            all_reviews.extend(product_data['trustpilot'])
            
            # Analyze sentiment for each review
            for review in all_reviews:
                if 'text' in review and review['text']:
                    sentiment_data = analyze_sentiment(review['text'], review.get('rating'))
                    review['sentiment'] = sentiment_data['sentiment']
                    review['polarity'] = sentiment_data.get('polarity', 0)
                    review['confidence'] = sentiment_data.get('confidence', 0.5)
            
            # Calculate aggregate metrics
            total_reviews = len(all_reviews)
            if total_reviews > 0:
                positive_count = sum(1 for r in all_reviews if r.get('sentiment') == 'positive')
                negative_count = sum(1 for r in all_reviews if r.get('sentiment') == 'negative')
                neutral_count = sum(1 for r in all_reviews if r.get('sentiment') == 'neutral')
                
                # Only include ratings that are not None and greater than 0
                ratings = [r.get('rating') for r in all_reviews if r.get('rating') is not None and r.get('rating') > 0]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                return {
                    'reviews': all_reviews,
                    'total_reviews': total_reviews,
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'neutral_count': neutral_count,
                    'positive_percentage': round((positive_count / total_reviews) * 100, 1),
                    'negative_percentage': round((negative_count / total_reviews) * 100, 1),
                    'neutral_percentage': round((neutral_count / total_reviews) * 100, 1),
                    'average_rating': round(avg_rating, 2),
                    'sources': {
                        'youtube': len(product_data['youtube']),
                        'amazon': len(product_data['amazon']),
                        'reddit': len(product_data['reddit']),
                        'trustpilot': len(product_data['trustpilot'])
                    }
                }
            
            return {
                'reviews': [],
                'total_reviews': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'average_rating': 0,
                'sources': {'youtube': 0, 'amazon': 0, 'reddit': 0, 'trustpilot': 0}
            }
        
        print("🔄 Analyzing sentiments...")
        product1_analysis = analyze_product_reviews(product1_data)
        product2_analysis = analyze_product_reviews(product2_data)
        
        print(f"✅ Product 1 ({product_1}): {product1_analysis['total_reviews']} reviews")
        print(f"✅ Product 2 ({product_2}): {product2_analysis['total_reviews']} reviews")
        
        # Generate AI-powered competitive insights
        ai_insights = None
        if client and (product1_analysis['total_reviews'] > 0 or product2_analysis['total_reviews'] > 0):
            try:
                print("🤖 Generating AI competitive insights...")
                
                # Sample reviews for prompt (max 10 per product)
                product1_sample = [r['text'][:200] for r in product1_analysis['reviews'][:10] if r.get('text')]
                product2_sample = [r['text'][:200] for r in product2_analysis['reviews'][:10] if r.get('text')]
                
                # Detect which product is Dr. Martens
                dr_martens_is_product_1 = 'dr' in product_1.lower() and 'mart' in product_1.lower()
                dr_martens_product = product_1 if dr_martens_is_product_1 else product_2
                competitor_product = product_2 if dr_martens_is_product_1 else product_1
                dr_martens_analysis = product1_analysis if dr_martens_is_product_1 else product2_analysis
                competitor_analysis = product2_analysis if dr_martens_is_product_1 else product1_analysis
                dr_martens_sample = product1_sample if dr_martens_is_product_1 else product2_sample
                competitor_sample = product2_sample if dr_martens_is_product_1 else product1_sample
                
                comparison_prompt = f"""You are analyzing competitive intelligence for DR. MARTENS brand management.

DR. MARTENS PRODUCT: {dr_martens_product}
- Total Reviews: {dr_martens_analysis['total_reviews']}
- Sentiment: {dr_martens_analysis['positive_percentage']}% positive, {dr_martens_analysis['negative_percentage']}% negative
- Sample Customer Reviews: {dr_martens_sample}

COMPETITOR: {competitor_product}
- Total Reviews: {competitor_analysis['total_reviews']}
- Sentiment: {competitor_analysis['positive_percentage']}% positive, {competitor_analysis['negative_percentage']}% negative
- Sample Customer Reviews: {competitor_sample}

CONTEXT: This analysis is for Dr. Martens leadership to understand competitive positioning and identify strategic opportunities.

IMPORTANT: Base your analysis ONLY on sentiment percentages and review content. DO NOT use average ratings as a criterion.Be completely honest by comparing both products fairly.

WINNER DETERMINATION:
- DO NOT declare an overall winner
- Only identify winners for EACH SPECIFIC CRITERION
- Be objective and honest about who leads in each category
- Frame insights to help Dr. Martens understand where they excel and where competitors are stronger
- Dont be partial to the competitor. If dr martens is better in a category, say so.
Provide a comprehensive competitive analysis in JSON format from DR. MARTENS' PERSPECTIVE:
{{
    "head_to_head_comparison": {{
        "quality": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - how does Dr. Martens compare?",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "comfort": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - comfort comparison",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "durability": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - longevity comparison",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "style": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - aesthetic appeal comparison",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "price": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - actual price comparison and affordability",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "value_for_money": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - price-value perception",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "break_in_period": {{
            "winner": "product name", 
            "reasoning": "Specific evidence - ease of break-in",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }},
        "overall_satisfaction": {{
            "winner": "product name",
            "reasoning": "General satisfaction from reviews without specific attribute mentions - overall happiness, recommendations, or disappointment",
            "dr_martens_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}},
            "competitor_sentiment": {{"positive_count": 0, "negative_count": 0, "positive_pct": 0, "negative_pct": 0}}
        }}
    }},
    
    "dr_martens_strengths": ["Key strength 1", "Key strength 2", "Key strength 3"],
    "dr_martens_weaknesses": ["Critical weakness 1", "Critical weakness 2", "Critical weakness 3"],
    
    "competitor_strengths": ["What competitor does well 1", "What competitor does well 2", "What competitor does well 3"],
    "competitor_weaknesses": ["Competitor weakness 1", "Competitor weakness 2", "Competitor weakness 3"],
    
    "competitive_advantages": "What Dr. Martens does BETTER than competitor (be specific)",
    "competitive_threats": "Where competitor is winning customers away from Dr. Martens",
    
    "target_audience": {{
        "dr_martens_best_for": "Customer segments where Dr. Martens wins",
        "competitor_best_for": "Customer segments where competitor wins"
    }},
    
    "price_value_analysis": "How Dr. Martens' value proposition compares to competitor",
    
    "strategic_recommendations_for_dr_martens": "TOP 3 actionable strategies Dr. Martens should implement to strengthen market position against this competitor",
    
    "market_positioning": "How Dr. Martens is positioned vs competitor in customer minds",
    
    "customer_preference_insights": "What factors drive customers to choose Dr. Martens vs competitor",
    
    "executive_summary": "3-sentence strategic summary for Dr. Martens leadership: (1) Summarize who leads in which criteria, (2) Identify key strategic opportunities based on where DM is strong/weak, (3) Provide actionable recommendation"
}}

IMPORTANT: Frame ALL insights from Dr. Martens' strategic perspective. Focus on actionable intelligence for the Dr. Martens brand. Be honest about weaknesses but solution-oriented. DO NOT mention or compare average ratings in any part of your analysis - focus only on sentiment percentages and review content.

CRITICAL: NO OVERALL WINNER - Only identify winners for each specific criterion. Be objective about who leads where. This helps Dr. Martens understand their competitive position across different attributes.

ATTRIBUTE ANALYSIS INSTRUCTIONS:

For each attribute in head_to_head_comparison, you MUST calculate sentiment metrics by:

1. **Specific Attributes (quality, comfort, durability, style, price, value_for_money, break_in_period)**:
   - Identify reviews mentioning the attribute using keywords:
     * quality → 'quality', 'craftsmanship', 'made', 'construction', 'build', 'materials', 'well-made', 'cheap quality'
     * comfort → 'comfort', 'comfortable', 'cushion', 'soft', 'painful', 'hurt', 'cozy', 'support', 'foot pain'
     * durability → 'durable', 'lasted', 'years', 'wearing', 'falling apart', 'broke', 'held up', 'worn out', 'lifetime'
     * style → 'look', 'style', 'aesthetic', 'design', 'fashion', 'trendy', 'cool', 'ugly', 'appearance'
     * price → 'price', 'expensive', 'cheap', 'affordable', 'cost', 'overpriced'
     * value_for_money → 'value', 'worth', 'money', 'investment', 'worth it', 'not worth'
     * break_in_period → 'break in', 'break-in', 'stiff', 'soften', 'first week', 'initially', 'getting used to'

2. **Overall Satisfaction (NEW)**:
   - Identify reviews that express GENERAL sentiment WITHOUT mentioning specific attributes above
   - Examples: "Love these!", "Highly recommend", "Best purchase ever", "Waste of money", "Disappointed", "Never buy again"
   - These are reviews that don't fit into specific categories but show overall happiness/disappointment
   - Count positive vs negative for general satisfaction

3. **Counting & Calculating**:
   - Count positive vs negative mentions for EACH product
   - Calculate percentages: positive_pct = (positive_count / total_mentions) * 100
   - Fill in dr_martens_sentiment and competitor_sentiment with ACTUAL counts and percentages

4. **Important Notes**:
   - A single review can mention MULTIPLE attributes (count it in each relevant category)
   - Sum of attribute counts may EXCEED total reviews (this is expected and correct)
   - Overall satisfaction captures reviews with NO specific attribute mentions

Example: If 30 reviews mention comfort for Dr Martens (23 positive, 7 negative):
"dr_martens_sentiment": {{"positive_count": 23, "negative_count": 7, "positive_pct": 76.7, "negative_pct": 23.3}}

These sentiment metrics MUST be based on the actual review data provided, not estimates."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a competitive intelligence analyst specializing in product comparison. Provide data-driven, actionable insights based solely on customer review sentiment and content. Never use or mention average ratings - focus on sentiment percentages instead."
                        },
                        {
                            "role": "user",
                            "content": comparison_prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2500,
                    response_format={"type": "json_object"}
                )
                
                ai_insights = json.loads(response.choices[0].message.content)
                print("✅ AI insights generated successfully")
                
            except Exception as e:
                print(f"⚠️ Error generating AI insights: {e}")
                import traceback
                traceback.print_exc()
                ai_insights = None
        else:
            print("⚠️ Skipping AI insights (no OpenAI client or no reviews)")
        
        # Return comprehensive comparison
        return jsonify({
            'success': True,
            'is_competitive_analysis': True,
            'query': query,
            'product_1': {
                'name': product_1,
                'analysis': product1_analysis
            },
            'product_2': {
                'name': product_2,
                'analysis': product2_analysis
            },
            'ai_insights': ai_insights,
            'comparison_summary': {
                'total_reviews_compared': product1_analysis['total_reviews'] + product2_analysis['total_reviews'],
                'sentiment_difference': round(product1_analysis['positive_percentage'] - product2_analysis['positive_percentage'], 1)
            }
        })
        
    except Exception as e:
        print(f"❌ Error in competitive analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    import sys
    
    # Allow socket reuse to prevent "address already in use" errors
    port = 4000
    
    try:
        print(f"🚀 Starting Flask server on port {port}...")
        print(f"🌐 Backend API: http://localhost:{port}")
        print(f"📊 Endpoints available:")
        print(f"   - POST /api/unified-search")
        print(f"   - POST /api/competitive-analysis")
        print(f"\n✅ Server is ready!\n")
        
        # Use threaded=True to handle multiple requests
        # Use use_reloader=False in production to avoid socket issues
        app.run(
            debug=True, 
            port=port, 
            host='127.0.0.1',
            threaded=True,
            use_reloader=False  # Prevents double-loading and socket issues
        )
    except OSError as e:
        if "WinError 10038" in str(e) or "address already in use" in str(e).lower():
            print(f"\n❌ Error: Port {port} is already in use!")
            print(f"💡 Solutions:")
            print(f"   1. Kill the existing process: taskkill /F /PID <PID>")
            print(f"   2. Find the PID: netstat -ano | findstr :{port}")
            print(f"   3. Or use a different port by changing the port variable")
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        print("\n\n👋 Server shutting down gracefully...")
        sys.exit(0)
