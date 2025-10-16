"""
Test script for Reddit integration
Run this to verify Reddit scraper works after adding credentials to .env
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_reddit_credentials():
    """Check if Reddit credentials are configured"""
    print("="*60)
    print("🔍 Checking Reddit API Configuration")
    print("="*60)
    
    client_id = os.getenv('REDDIT_CLIENT_ID', '')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
    user_agent = os.getenv('REDDIT_USER_AGENT', '')
    
    if not client_id or client_id == "your_reddit_client_id_here":
        print("❌ REDDIT_CLIENT_ID not configured")
        print("   Please add your Reddit client ID to backend/.env")
        return False
    else:
        print(f"✅ REDDIT_CLIENT_ID found: {client_id[:10]}...")
    
    if not client_secret or client_secret == "your_reddit_client_secret_here":
        print("❌ REDDIT_CLIENT_SECRET not configured")
        print("   Please add your Reddit client secret to backend/.env")
        return False
    else:
        print(f"✅ REDDIT_CLIENT_SECRET found: {client_secret[:10]}...")
    
    if user_agent:
        print(f"✅ REDDIT_USER_AGENT: {user_agent}")
    
    return True

def test_reddit_scraper():
    """Test the Reddit scraper"""
    from reddit_scraper import scrape_reddit_reviews
    
    print("\n" + "="*60)
    print("🧪 Testing Reddit Review Scraper")
    print("="*60)
    
    test_query = "Dr Martens 1460 boots"
    print(f"🔍 Searching Reddit for: '{test_query}'")
    print(f"   (Max reviews: 20)\n")
    
    try:
        reviews = scrape_reddit_reviews(test_query, max_reviews=20)
        
        if not reviews:
            print("⚠️  No reviews found")
            print("   This might be normal if:")
            print("   - Reddit has no discussions about this topic")
            print("   - API rate limit reached")
            print("   - Credentials are invalid")
            return False
        
        print(f"✅ Successfully scraped {len(reviews)} reviews")
        print(f"   From {len(set(r.get('subreddit') for r in reviews))} different subreddits\n")
        
        # Show statistics
        posts = [r for r in reviews if r.get('type') == 'post']
        comments = [r for r in reviews if r.get('type') == 'comment']
        total_upvotes = sum(r.get('score', 0) for r in reviews)
        
        print(f"📊 Statistics:")
        print(f"   Posts: {len(posts)}")
        print(f"   Comments: {len(comments)}")
        print(f"   Total upvotes: {total_upvotes}")
        print(f"   Average upvotes: {total_upvotes/len(reviews):.1f}")
        
        # Show sample review
        sample = reviews[0]
        print(f"\n💬 Sample Review:")
        print(f"   Author: u/{sample.get('author', 'N/A')}")
        print(f"   Subreddit: r/{sample.get('subreddit', 'N/A')}")
        print(f"   Score: {sample.get('score', 0)} upvotes")
        print(f"   Date: {sample.get('date', 'N/A')}")
        print(f"   Type: {sample.get('type', 'N/A')}")
        
        text_preview = sample.get('text', '')[:200]
        if len(sample.get('text', '')) > 200:
            text_preview += "..."
        print(f"   Text: {text_preview}")
        
        if sample.get('url'):
            print(f"   URL: {sample.get('url')}")
        
        print(f"\n{'='*60}")
        print("✅ SUCCESS! Reddit integration is working!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"\nFull error details:")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("Reddit Integration Test Suite")
    print("="*60 + "\n")
    
    # Step 1: Check credentials
    if not test_reddit_credentials():
        print("\n" + "="*60)
        print("❌ Setup Required")
        print("="*60)
        print("\nPlease complete these steps:\n")
        print("1. Go to: https://www.reddit.com/prefs/apps")
        print("2. Click 'create another app...'")
        print("3. Fill in:")
        print("   - name: DrMartensReviewAnalyzer")
        print("   - type: script")
        print("   - redirect uri: http://localhost:8080")
        print("4. Copy your client_id and client_secret")
        print("5. Update backend/.env with your credentials")
        print("\nThen run this script again!")
        return
    
    # Step 2: Test scraper
    print("\n")
    success = test_reddit_scraper()
    
    if success:
        print("\n✅ All tests passed!")
        print("   You can now use Reddit integration in the app")
        print("   Restart the backend and search for products!")
    else:
        print("\n❌ Tests failed")
        print("   Check the error messages above")
        print("   Make sure your Reddit credentials are correct")

if __name__ == "__main__":
    main()
