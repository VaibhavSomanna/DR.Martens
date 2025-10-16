from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from textblob import TextBlob
from datetime import datetime
from openai import OpenAI
import json
from scraper import scrape_google_maps_reviews, scrape_from_place_id
from amazon_scraper import scrape_amazon_reviews

load_dotenv()

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_PLACES_API_URL = "https://maps.googleapis.com/maps/api/place"

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

def search_place(query):
    """Search for a place using Google Places API"""
    url = f"{GOOGLE_PLACES_API_URL}/findplacefromtext/json"
    params = {
        'input': query,
        'inputtype': 'textquery',
        'fields': 'place_id,name,formatted_address,rating',
        'key': GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"Google API Response: {data}")  # Debug logging
        
        if data.get('candidates'):
            return data['candidates'][0]
        return None
    except Exception as e:
        print(f"Error searching place: {e}")
        return None

def get_place_reviews(place_id):
    """Get reviews for a place using Google Places API"""
    url = f"{GOOGLE_PLACES_API_URL}/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,rating,reviews,user_ratings_total,formatted_address',
        'key': GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result'):
            return data['result']
        return None
    except Exception as e:
        print(f"Error getting place reviews: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Search for Dr. Martens stores"""
    data = request.get_json()
    query = data.get('query', 'Dr. Martens')
    
    if not GOOGLE_API_KEY:
        return jsonify({
            "error": "Google API key not configured"
        }), 500
    
    place = search_place(query)
    
    if place:
        # Return in the format frontend expects: { results: [...] }
        return jsonify({
            "success": True,
            "results": [place]  # Frontend expects results array
        })
    else:
        return jsonify({
            "success": False,
            "error": "No place found",
            "results": []  # Return empty array instead of 404
        }), 200  # Return 200 instead of 404 so frontend doesn't error

@app.route('/api/reviews', methods=['POST'])
def get_reviews():
    """Get and analyze reviews for a place - Enhanced with scraping"""
    data = request.get_json()
    place_id = data.get('place_id')
    use_scraper = data.get('use_scraper', True)  # Default to scraping for more reviews
    max_reviews = data.get('max_reviews', 50)  # Default to 50 reviews
    
    if not place_id:
        return jsonify({
            "error": "place_id is required"
        }), 400
    
    if not GOOGLE_API_KEY:
        return jsonify({
            "error": "Google API key not configured"
        }), 500
    
    # First, get place details from Google Places API
    place_data = get_place_reviews(place_id)
    
    if not place_data:
        return jsonify({
            "error": "Could not fetch place details"
        }), 404
    
    place_name = place_data.get('name', 'Dr. Martens')
    place_address = place_data.get('formatted_address', '')
    
    analyzed_reviews = []
    data_source = "google_places_api"
    
    if use_scraper:
        # Use Selenium scraper for more reviews
        print(f"\n🕷️ Scraping reviews for: {place_name}")
        print(f"   Target: {max_reviews} reviews")
        
        try:
            # Try scraping from place_id first
            scraped_reviews = scrape_from_place_id(place_id, max_reviews=max_reviews)
            
            # If that fails, try with place name
            if not scraped_reviews:
                print("   Trying with place name...")
                scraped_reviews = scrape_google_maps_reviews(place_name, location="", max_reviews=max_reviews)
            
            if scraped_reviews:
                print(f"✅ Scraped {len(scraped_reviews)} reviews successfully")
                data_source = "web_scraping"
                
                # Analyze sentiment for scraped reviews (pass rating for better accuracy)
                for review in scraped_reviews:
                    rating = review.get('rating', 0)
                    sentiment_data = analyze_sentiment(review.get('text', ''), rating=rating)
                    analyzed_reviews.append({
                        "author": review.get('author', 'Anonymous'),
                        "rating": rating,
                        "text": review.get('text', ''),
                        "time": review.get('date', 'Unknown'),
                        "sentiment": sentiment_data
                    })
            else:
                print("⚠️ Scraping failed, falling back to Google Places API")
                use_scraper = False
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            print("   Falling back to Google Places API")
            use_scraper = False
    
    # Fall back to Google Places API if scraping is disabled or failed
    if not use_scraper or not analyzed_reviews:
        print(f"📍 Using Google Places API (limited to 5 reviews)")
        reviews = place_data.get('reviews', [])
        data_source = "google_places_api"
        
        for review in reviews:
            rating = review.get('rating', 0)
            sentiment_data = analyze_sentiment(review.get('text', ''), rating=rating)
            analyzed_reviews.append({
                "author": review.get('author_name'),
                "rating": rating,
                "text": review.get('text'),
                "time": review.get('relative_time_description'),
                "sentiment": sentiment_data
            })
    
    # Calculate overall statistics
    total_reviews = len(analyzed_reviews)
    positive_count = sum(1 for r in analyzed_reviews if r['sentiment']['sentiment'] == 'positive')
    negative_count = sum(1 for r in analyzed_reviews if r['sentiment']['sentiment'] == 'negative')
    neutral_count = sum(1 for r in analyzed_reviews if r['sentiment']['sentiment'] == 'neutral')
    
    avg_rating = place_data.get('rating', 0)
    if analyzed_reviews:
        avg_polarity = sum(r['sentiment']['polarity'] for r in analyzed_reviews) / total_reviews
    else:
        avg_polarity = 0
    
    return jsonify({
        "success": True,
        "place": {
            "name": place_name,
            "address": place_address,
            "rating": avg_rating,
            "total_ratings": place_data.get('user_ratings_total')
        },
        "reviews": analyzed_reviews,
        "statistics": {
            "total": total_reviews,
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "avg_rating": avg_rating,
            "avg_polarity": round(avg_polarity, 2)
        },
        "data_source": data_source,
        "scraping_enabled": use_scraper
    })

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
    Get reviews from both Google Maps (location) and Amazon (product)
    Returns separate review lists but combined AI insights
    """
    try:
        data = request.get_json()
        google_query = data.get('google_query', '')
        amazon_query = data.get('amazon_query', '')
        max_reviews = data.get('max_reviews', 30)
        
        if not google_query and not amazon_query:
            return jsonify({
                'error': 'At least one query (Google or Amazon) is required'
            }), 400
        
        google_reviews = []
        amazon_reviews = []
        google_place_info = None
        amazon_product_info = None
        
        # Fetch Google Maps reviews
        if google_query:
            print(f"🗺️ Fetching Google Maps reviews for: {google_query}")
            
            # Search for place
            place = search_place(google_query)
            if place:
                place_id = place.get('place_id')
                google_place_info = {
                    'name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'rating': place.get('rating')
                }
                
                # Get place details
                place_data = get_place_reviews(place_id)
                if place_data:
                    google_place_info['rating'] = place_data.get('rating')
                    google_place_info['total_ratings'] = place_data.get('user_ratings_total')
                    
                    # Try scraping first
                    try:
                        scraped_reviews = scrape_from_place_id(place_id, max_reviews=max_reviews)
                        if scraped_reviews:
                            for review in scraped_reviews:
                                rating = review.get('rating', 0)
                                sentiment_data = analyze_sentiment(review.get('text', ''), rating=rating)
                                google_reviews.append({
                                    'author': review.get('author', 'Anonymous'),
                                    'rating': rating,
                                    'text': review.get('text', ''),
                                    'date': review.get('date', 'Unknown'),
                                    'sentiment': sentiment_data['sentiment'],
                                    'polarity': sentiment_data['polarity'],
                                    'subjectivity': sentiment_data['subjectivity'],
                                    'source': 'google_maps'
                                })
                    except Exception as e:
                        print(f"⚠️ Scraping failed, using API: {e}")
                        # Fallback to API
                        for review in place_data.get('reviews', []):
                            rating = review.get('rating', 0)
                            sentiment_data = analyze_sentiment(review.get('text', ''), rating=rating)
                            google_reviews.append({
                                'author': review.get('author_name'),
                                'rating': rating,
                                'text': review.get('text'),
                                'date': review.get('relative_time_description'),
                                'sentiment': sentiment_data['sentiment'],
                                'polarity': sentiment_data['polarity'],
                                'subjectivity': sentiment_data['subjectivity'],
                                'source': 'google_maps'
                            })
        
        # Fetch Amazon reviews
        if amazon_query:
            print(f"🛒 Fetching Amazon reviews for: {amazon_query}")
            
            try:
                product_info, reviews = scrape_amazon_reviews(amazon_query, max_reviews=max_reviews)
                amazon_product_info = product_info
                
                for review in reviews:
                    rating = review.get('rating')
                    sentiment_data = analyze_sentiment(review.get('text', ''))
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
        
        # Combine all reviews for overall statistics
        all_reviews = google_reviews + amazon_reviews
        
        if not all_reviews:
            return jsonify({
                'error': 'No reviews found from either source'
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
            if review['rating'] > 0:
                total_rating += review['rating']
                rating_count += 1
        
        statistics = {
            'total_reviews': len(all_reviews),
            'google_reviews_count': len(google_reviews),
            'amazon_reviews_count': len(amazon_reviews),
            'sentiment_distribution': sentiment_counts,
            'average_polarity': round(total_polarity / len(all_reviews), 2),
            'average_subjectivity': round(total_subjectivity / len(all_reviews), 2),
            'average_rating': round(total_rating / rating_count, 2) if rating_count > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'google': {
                'place_info': google_place_info,
                'reviews': google_reviews,
                'count': len(google_reviews)
            },
            'amazon': {
                'product_info': amazon_product_info,
                'reviews': amazon_reviews,
                'count': len(amazon_reviews)
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
        
        if not use_demo:
            try:
                # Scrape Amazon reviews
                product_info, reviews = scrape_amazon_reviews(product_query, max_reviews=max_reviews)
            except Exception as scrape_error:
                error_msg = str(scrape_error)
                if "login" in error_msg.lower() or "blocked" in error_msg.lower():
                    print("⚠️ Amazon blocked scraping, using demo data as fallback...")
                    use_demo = True
                else:
                    raise
        
        # Use demo data if requested or if scraping failed
        if use_demo or not reviews:
            from amazon_demo_data import generate_demo_reviews, generate_demo_product_info
            print("📊 Using demo data for demonstration...")
            product_info = generate_demo_product_info(product_query)
            reviews = generate_demo_reviews(product_query, count=max_reviews)
        
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
