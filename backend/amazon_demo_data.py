"""
Demo data generator for Amazon reviews
Used as fallback when Amazon blocks scraping
"""
import random
from datetime import datetime, timedelta

def generate_demo_reviews(product_name, count=50):
    """
    Generate realistic demo reviews for demonstration purposes
    """
    
    # Dr. Martens specific review templates
    positive_reviews = [
        {
            "title": "Love these boots!",
            "text": "These are exactly what I expected from Dr. Martens. The leather quality is exceptional and they're built to last. Yes, there's a break-in period, but it's worth it. After a few weeks, they're the most comfortable boots I own.",
            "rating": 5.0
        },
        {
            "title": "Quality craftsmanship",
            "text": "The stitching and leather quality are top-notch. These boots feel substantial and well-made. I've had mine for 6 months and they still look brand new. Definitely worth the investment.",
            "rating": 5.0
        },
        {
            "title": "Classic style that never goes out of fashion",
            "text": "I've been wanting a pair of Doc Martens for years and finally pulled the trigger. They're everything I hoped for - stylish, durable, and iconic. The yellow stitching is a nice touch.",
            "rating": 5.0
        },
        {
            "title": "Great boots once broken in",
            "text": "The break-in period was about 2 weeks of occasional wear. Now they're super comfortable and I wear them almost every day. The air-cushioned sole provides great support.",
            "rating": 4.0
        },
        {
            "title": "Excellent quality",
            "text": "The leather is thick and high quality. These boots are heavy-duty and feel like they'll last for years. I'm very impressed with the construction and attention to detail.",
            "rating": 5.0
        },
        {
            "title": "Worth every penny",
            "text": "Yes, they're expensive, but the quality justifies the price. These are boots you'll have for decades. The Goodyear welt construction means they can be resoled multiple times.",
            "rating": 5.0
        },
        {
            "title": "Very comfortable after breaking in",
            "text": "Took about 3 weeks to fully break in, but now they're incredibly comfortable. The cushioned insole provides great arch support. I can walk all day in these without any issues.",
            "rating": 4.0
        },
        {
            "title": "Iconic and durable",
            "text": "These boots are an investment piece. The smooth leather can be polished to look brand new even after years of wear. I love the classic design and how versatile they are.",
            "rating": 5.0
        }
    ]
    
    negative_reviews = [
        {
            "title": "Sizing runs large",
            "text": "I ordered my usual size and they're way too big. I have to wear thick socks to make them fit. Wish I had sized down. Also, the break-in period is brutal - my heels were covered in blisters.",
            "rating": 2.0
        },
        {
            "title": "Extremely stiff",
            "text": "After 3 weeks of wearing them, they're still incredibly stiff and uncomfortable. The leather hasn't softened at all. Starting to wonder if they'll ever break in properly.",
            "rating": 2.0
        },
        {
            "title": "Overpriced",
            "text": "For the price, I expected better quality. The leather feels cheap and plasticky. I've had $50 boots that felt more premium than these. Very disappointed.",
            "rating": 1.0
        },
        {
            "title": "Uncomfortable",
            "text": "These boots are so uncomfortable. The sole is hard as a rock and provides no cushioning. My feet hurt after wearing them for just a couple hours. Would not recommend.",
            "rating": 2.0
        },
        {
            "title": "Not worth the hype",
            "text": "Everyone raves about Doc Martens but I don't see what the big deal is. They're heavy, stiff, and take forever to break in. There are much more comfortable boots out there.",
            "rating": 2.0
        }
    ]
    
    neutral_reviews = [
        {
            "title": "Good but not great",
            "text": "These boots are decent quality but nothing special. They're comfortable enough once broken in, but the break-in period is longer than I expected. Overall, they're fine.",
            "rating": 3.0
        },
        {
            "title": "Mixed feelings",
            "text": "The quality seems good but I'm not sure about the fit. They feel a bit roomy even though I sized down. The leather is nice but I expected it to be softer. Still deciding if I'll keep them.",
            "rating": 3.0
        }
    ]
    
    # Generate review authors
    first_names = ["Sarah", "Mike", "Jessica", "David", "Emily", "Chris", "Amanda", "John", "Rachel", "Tom", "Lauren", "James", "Nicole", "Brian", "Ashley"]
    last_initials = ["M.", "S.", "J.", "K.", "R.", "L.", "W.", "B.", "C.", "H."]
    
    # Mix reviews based on typical Amazon distribution (70% positive, 20% negative, 10% neutral)
    all_reviews = []
    
    # Calculate distribution
    positive_count = int(count * 0.70)
    negative_count = int(count * 0.20)
    neutral_count = count - positive_count - negative_count
    
    # Add reviews
    for _ in range(positive_count):
        template = random.choice(positive_reviews)
        all_reviews.append({
            **template,
            "author": f"{random.choice(first_names)} {random.choice(last_initials)}",
            "date": generate_random_date(),
            "verified": random.choice([True, True, True, False])  # 75% verified
        })
    
    for _ in range(negative_count):
        template = random.choice(negative_reviews)
        all_reviews.append({
            **template,
            "author": f"{random.choice(first_names)} {random.choice(last_initials)}",
            "date": generate_random_date(),
            "verified": random.choice([True, True, False])  # 66% verified
        })
    
    for _ in range(neutral_count):
        template = random.choice(neutral_reviews)
        all_reviews.append({
            **template,
            "author": f"{random.choice(first_names)} {random.choice(last_initials)}",
            "date": generate_random_date(),
            "verified": random.choice([True, False])  # 50% verified
        })
    
    # Shuffle to randomize order
    random.shuffle(all_reviews)
    
    return all_reviews

def generate_random_date():
    """Generate a random date within the last 12 months"""
    days_ago = random.randint(1, 365)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("Reviewed in the United States on %B %d, %Y")

def generate_demo_product_info(product_name):
    """Generate demo product info"""
    return {
        'name': product_name,
        'url': 'https://www.amazon.com/demo-product',
        'rating': round(random.uniform(4.0, 4.5), 1),
        'total_ratings': random.randint(5000, 15000)
    }

if __name__ == "__main__":
    # Test the generator
    print("=" * 60)
    print("Testing Demo Data Generator")
    print("=" * 60)
    
    product_info = generate_demo_product_info("Dr. Martens 1460 Boots")
    reviews = generate_demo_reviews("Dr. Martens 1460 Boots", count=20)
    
    print(f"\n✅ Generated {len(reviews)} demo reviews")
    print(f"\nProduct: {product_info['name']}")
    print(f"Rating: {product_info['rating']}/5")
    print(f"Total Ratings: {product_info['total_ratings']}")
    print("\nSample reviews:")
    for i, review in enumerate(reviews[:3], 1):
        print(f"\n{i}. {review['author']} - {'⭐' * int(review['rating'])}")
        print(f"   Title: {review['title']}")
        print(f"   Date: {review['date']}")
        print(f"   Verified: {'✅' if review['verified'] else '❌'}")
        print(f"   Text: {review['text'][:100]}...")
