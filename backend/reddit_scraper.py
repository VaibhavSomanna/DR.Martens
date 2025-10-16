"""
Reddit Review Scraper using PRAW (Python Reddit API Wrapper)
Scrapes posts and comments from relevant subreddits
"""
import praw
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def setup_reddit():
    """Initialize Reddit API client for read-only access"""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'DrMartensReviewAnalyzer/1.0')
    
    if not client_id or not client_secret:
        raise ValueError("Reddit API credentials not found in .env file")
    
    # Initialize Reddit client (works with 'web app' type from reddit.com/prefs/apps)
    # Note: Make sure your Reddit app is type "web app" not "script"!
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        # Grant type for read-only access with web apps
        redirect_uri='http://localhost:8080'
    )
    
    return reddit

def scrape_reddit_reviews(query, max_reviews=50):
    """
    Search Reddit for posts/comments about a product or place
    
    Args:
        query: Search term (e.g., "Dr Martens 1460 boots")
        max_reviews: Maximum number of reviews to collect
    
    Returns:
        List of review dictionaries
    """
    try:
        reddit = setup_reddit()
        reviews = []
        
        print(f"🔍 Searching Reddit for: {query}")
        
        # Relevant subreddits for product reviews
        subreddits = [
            'BuyItForLife',
            'malefashionadvice',
            'femalefashionadvice',
            'frugalmalefashion',
            'frugalfemalefashion',
            'fashionreps',
            'sneakers',
            'goodyearwelt',
            'rawdenim',
            'DrMartens',
            'Boots',
            'fashion'
        ]
        
        # Search across multiple subreddits
        subreddit_str = '+'.join(subreddits)
        subreddit = reddit.subreddit(subreddit_str)
        
        # Search for relevant posts
        search_results = subreddit.search(query, limit=20, sort='relevance', time_filter='all')
        
        posts_processed = 0
        for post in search_results:
            if len(reviews) >= max_reviews:
                break
            
            # Extract post itself as a review
            if post.selftext and len(post.selftext) > 50 and post.selftext != '[removed]':
                reviews.append({
                    'author': str(post.author) if post.author else 'Anonymous',
                    'text': post.selftext[:1500],  # Limit length
                    'title': post.title,
                    'date': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d'),
                    'score': post.score,
                    'url': f"https://reddit.com{post.permalink}",
                    'subreddit': str(post.subreddit),
                    'type': 'post'
                })
                posts_processed += 1
            
            # Extract top comments from the post
            try:
                post.comments.replace_more(limit=0)  # Remove "load more comments"
                for comment in post.comments.list()[:5]:  # Top 5 comments per post
                    if len(reviews) >= max_reviews:
                        break
                    
                    if (comment.body and 
                        len(comment.body) > 30 and 
                        comment.body not in ['[deleted]', '[removed]']):
                        reviews.append({
                            'author': str(comment.author) if comment.author else 'Anonymous',
                            'text': comment.body[:1500],
                            'title': f"Comment on: {post.title[:50]}...",
                            'date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
                            'score': comment.score,
                            'url': f"https://reddit.com{comment.permalink}",
                            'subreddit': str(post.subreddit),
                            'type': 'comment'
                        })
            except Exception as e:
                print(f"⚠️ Error processing comments: {e}")
                continue
        
        print(f"✅ Successfully scraped {len(reviews)} Reddit reviews from {posts_processed} posts")
        return reviews
        
    except Exception as e:
        print(f"❌ Error scraping Reddit: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def scrape_subreddit_reviews(subreddit_name, query, max_reviews=50):
    """
    Search a specific subreddit for reviews
    
    Args:
        subreddit_name: Name of subreddit (e.g., "DrMartens")
        query: Search term
        max_reviews: Maximum number of reviews
    
    Returns:
        List of review dictionaries
    """
    try:
        reddit = setup_reddit()
        reviews = []
        
        print(f"🔍 Searching r/{subreddit_name} for: {query}")
        
        subreddit = reddit.subreddit(subreddit_name)
        search_results = subreddit.search(query, limit=20, sort='relevance', time_filter='all')
        
        for post in search_results:
            if len(reviews) >= max_reviews:
                break
            
            # Add post
            if post.selftext and len(post.selftext) > 50:
                reviews.append({
                    'author': str(post.author) if post.author else 'Anonymous',
                    'text': post.selftext[:1500],
                    'title': post.title,
                    'date': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d'),
                    'score': post.score,
                    'url': f"https://reddit.com{post.permalink}",
                    'subreddit': subreddit_name,
                    'type': 'post'
                })
            
            # Add comments
            try:
                post.comments.replace_more(limit=0)
                for comment in post.comments.list()[:5]:
                    if len(reviews) >= max_reviews:
                        break
                    
                    if comment.body and len(comment.body) > 30 and comment.body != '[deleted]':
                        reviews.append({
                            'author': str(comment.author) if comment.author else 'Anonymous',
                            'text': comment.body[:1500],
                            'title': f"Comment on: {post.title[:50]}...",
                            'date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
                            'score': comment.score,
                            'url': f"https://reddit.com{comment.permalink}",
                            'subreddit': subreddit_name,
                            'type': 'comment'
                        })
            except Exception as e:
                print(f"⚠️ Error processing comments: {e}")
                continue
        
        print(f"✅ Found {len(reviews)} reviews from r/{subreddit_name}")
        return reviews
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the scraper
    print("=" * 60)
    print("Testing Reddit Review Scraper")
    print("=" * 60)
    
    reviews = scrape_reddit_reviews("Dr Martens 1460 boots", max_reviews=20)
    
    if reviews:
        print(f"\n✅ SUCCESS! Scraped {len(reviews)} reviews\n")
        print("Sample review:")
        print(f"  Author: {reviews[0]['author']}")
        print(f"  Subreddit: r/{reviews[0]['subreddit']}")
        print(f"  Score: {reviews[0]['score']} upvotes")
        print(f"  Date: {reviews[0]['date']}")
        print(f"  Type: {reviews[0]['type']}")
        print(f"  Text: {reviews[0]['text'][:150]}...")
    else:
        print("\n❌ No reviews found")
