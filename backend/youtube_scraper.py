"""
YouTube Video Review Scraper using YouTube Data API v3
Extracts video comments and metadata for product reviews
"""
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

load_dotenv()

def setup_youtube():
    """Initialize YouTube API client"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        raise ValueError("YouTube API key not found in .env file")
    
    return build('youtube', 'v3', developerKey=api_key)

def scrape_youtube_reviews(query, max_reviews=50):
    """
    Search YouTube for product review videos and extract comments
    
    Args:
        query: Search term (e.g., "Dr Martens 1460 boots review")
        max_reviews: Maximum number of comments to collect
    
    Returns:
        List of review dictionaries with video metadata and comments
    """
    try:
        youtube = setup_youtube()
        reviews = []
        
        print(f"🎥 Searching YouTube for: {query}")
        
        # Search for relevant videos
        search_response = youtube.search().list(
            q=query + " review",
            part='id,snippet',
            type='video',
            maxResults=10,  # Get top 10 videos
            order='relevance',
            relevanceLanguage='en'
        ).execute()
        
        video_ids = []
        for item in search_response.get('items', []):
            video_ids.append(item['id']['videoId'])
        
        if not video_ids:
            print("⚠️ No YouTube videos found for query")
            return reviews
        
        print(f"✅ Found {len(video_ids)} YouTube videos")
        
        # Get comments from each video
        comments_collected = 0
        for video_id in video_ids:
            if comments_collected >= max_reviews:
                break
            
            try:
                # Get video details
                video_response = youtube.videos().list(
                    part='snippet,statistics',
                    id=video_id
                ).execute()
                
                if not video_response['items']:
                    continue
                
                video_info = video_response['items'][0]
                video_title = video_info['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                channel_title = video_info['snippet']['channelTitle']
                view_count = int(video_info['statistics'].get('viewCount', 0))
                like_count = int(video_info['statistics'].get('likeCount', 0))
                
                # Get comments from this video
                comments_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(10, max_reviews - comments_collected),
                    order='relevance',
                    textFormat='plainText'
                ).execute()
                
                for item in comments_response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    
                    # Only include comments with meaningful length
                    comment_text = comment['textDisplay']
                    if len(comment_text) < 30:
                        continue
                    
                    reviews.append({
                        'author': comment['authorDisplayName'],
                        'text': comment_text,
                        'date': comment['publishedAt'][:10],
                        'rating': 0,  # YouTube doesn't have star ratings
                        'likes': comment.get('likeCount', 0),
                        'video_title': video_title,
                        'video_url': video_url,
                        'channel': channel_title,
                        'video_views': view_count,
                        'video_likes': like_count,
                        'source': 'youtube'
                    })
                    
                    comments_collected += 1
                    if comments_collected >= max_reviews:
                        break
                
            except HttpError as e:
                if 'commentsDisabled' in str(e):
                    print(f"⚠️ Comments disabled for video {video_id}")
                else:
                    print(f"❌ Error fetching comments for video {video_id}: {e}")
                continue
        
        print(f"✅ Successfully scraped {len(reviews)} YouTube comments")
        return reviews
        
    except Exception as e:
        print(f"❌ Error scraping YouTube: {e}")
        import traceback
        traceback.print_exc()
        return []

# Test function
if __name__ == "__main__":
    print("="*60)
    print("Testing YouTube Review Scraper")
    print("="*60)
    
    test_query = "Dr Martens 1460 boots"
    print(f"🔍 Searching YouTube for: {test_query}")
    print()
    
    reviews = scrape_youtube_reviews(test_query, max_reviews=20)
    
    if reviews:
        print(f"\n✅ Successfully scraped {len(reviews)} reviews")
        print(f"   From {len(set(r['video_title'] for r in reviews))} different videos\n")
        
        # Show sample
        sample = reviews[0]
        print(f"💬 Sample Comment:")
        print(f"   Video: {sample['video_title']}")
        print(f"   Channel: {sample['channel']}")
        print(f"   Author: {sample['author']}")
        print(f"   Likes: {sample['likes']}")
        print(f"   Date: {sample['date']}")
        print(f"   Text: {sample['text'][:200]}...")
        print(f"   URL: {sample['video_url']}")
    else:
        print("\n❌ No reviews found")
