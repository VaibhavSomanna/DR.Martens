"""
Test script to verify AI insights endpoint
"""
import requests
import json

# Test data with both sentiment formats
test_reviews_nested = [
    {
        "text": "Great boots, very comfortable after break-in",
        "rating": 5,
        "sentiment": {
            "sentiment": "positive",
            "polarity": 0.8
        }
    },
    {
        "text": "Terrible quality, fell apart quickly",
        "rating": 1,
        "sentiment": {
            "sentiment": "negative",
            "polarity": -0.6
        }
    }
]

test_reviews_string = [
    {
        "text": "Great boots, very comfortable after break-in",
        "rating": 5,
        "sentiment": "positive"
    },
    {
        "text": "Terrible quality, fell apart quickly",
        "rating": 1,
        "sentiment": "negative"
    }
]

def test_endpoint(reviews, test_name):
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/ai-insights',
            json={'reviews': reviews},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            print(f"\nInsights preview:")
            print(data.get('insights', '')[:200] + "...")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("Testing AI Insights Endpoint")
    
    # Test with nested sentiment
    test_endpoint(test_reviews_nested, "Nested Sentiment Format")
    
    # Test with string sentiment
    test_endpoint(test_reviews_string, "String Sentiment Format")
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
