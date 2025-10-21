"""
Trustpilot Review Scraper
Scrapes product reviews from Trustpilot.com
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime

def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver

def scrape_trustpilot_reviews(product_name, max_reviews=50):
    """
    Scrape reviews from Trustpilot for Dr. Martens
    
    Args:
        product_name: Product name to search for (e.g., "Dr Martens")
        max_reviews: Maximum number of reviews to scrape
    
    Returns:
        List of review dictionaries
    """
    driver = None
    reviews = []
    
    try:
        print(f"🔍 Scraping Trustpilot for: {product_name}")
        
        driver = setup_driver()
        
        # Navigate to Dr. Martens Trustpilot page
        # Note: You may need to find the specific company URL
        trustpilot_url = "https://www.trustpilot.com/review/www.drmartens.com"
        
        print(f"🌐 Opening Trustpilot page...")
        driver.get(trustpilot_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Accept cookies if present
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            time.sleep(1)
        except:
            print("No cookie banner found or already accepted")
        
        # Scroll to load more reviews
        last_height = driver.execute_script("return document.body.scrollHeight")
        pages_loaded = 0
        max_pages = 5  # Load up to 5 pages worth of reviews
        
        while pages_loaded < max_pages and len(reviews) < max_reviews:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            pages_loaded += 1
        
        print("📜 Extracting review data...")
        
        # Find all review cards
        review_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-service-review-card-paper]')
        
        if not review_elements:
            # Try alternative selector
            review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-service-review-card]')
        
        print(f"✅ Found {len(review_elements)} review elements")
        
        for review_elem in review_elements[:max_reviews]:
            try:
                # Extract rating (stars)
                try:
                    rating_elem = review_elem.find_element(By.CSS_SELECTOR, 'div[data-service-review-rating]')
                    rating_img = rating_elem.find_element(By.TAG_NAME, 'img')
                    rating_text = rating_img.get_attribute('alt')
                    # Extract number from "Rated X out of 5 stars"
                    rating = int(rating_text.split()[1]) if rating_text else 5
                except:
                    rating = 5  # Default if can't find rating
                
                # Extract review title
                try:
                    title_elem = review_elem.find_element(By.CSS_SELECTOR, 'h2[data-service-review-title-typography]')
                    title = title_elem.text
                except:
                    title = ""
                
                # Extract review text
                try:
                    text_elem = review_elem.find_element(By.CSS_SELECTOR, 'p[data-service-review-text-typography]')
                    text = text_elem.text
                except:
                    text = title  # Use title if no body text
                
                if not text or len(text) < 10:
                    continue
                
                # Extract author
                try:
                    author_elem = review_elem.find_element(By.CSS_SELECTOR, 'span[data-consumer-name-typography]')
                    author = author_elem.text
                except:
                    author = "Anonymous"
                
                # Extract date
                try:
                    date_elem = review_elem.find_element(By.CSS_SELECTOR, 'time')
                    date_str = date_elem.get_attribute('datetime')
                    date = date_str[:10] if date_str else datetime.now().strftime('%Y-%m-%d')
                except:
                    date = datetime.now().strftime('%Y-%m-%d')
                
                # Extract verification status
                try:
                    verified_elem = review_elem.find_element(By.CSS_SELECTOR, 'div[data-service-review-verification-badge]')
                    verified = True
                except:
                    verified = False
                
                reviews.append({
                    'author': author,
                    'rating': rating,
                    'title': title,
                    'text': text,
                    'date': date,
                    'verified': verified,
                    'source': 'trustpilot',
                    'url': trustpilot_url
                })
                
            except Exception as e:
                print(f"⚠️ Error extracting review: {e}")
                continue
        
        print(f"✅ Successfully scraped {len(reviews)} Trustpilot reviews")
        return reviews
        
    except Exception as e:
        print(f"❌ Error scraping Trustpilot: {e}")
        import traceback
        traceback.print_exc()
        return reviews
        
    finally:
        if driver:
            driver.quit()

# Test function
if __name__ == "__main__":
    print("="*60)
    print("Testing Trustpilot Review Scraper")
    print("="*60)
    
    test_query = "Dr Martens"
    print(f"🔍 Scraping Trustpilot for: {test_query}")
    print()
    
    reviews = scrape_trustpilot_reviews(test_query, max_reviews=20)
    
    if reviews:
        print(f"\n✅ Successfully scraped {len(reviews)} reviews")
        print(f"   Average rating: {sum(r['rating'] for r in reviews) / len(reviews):.1f}/5")
        
        # Show statistics
        verified_count = sum(1 for r in reviews if r.get('verified'))
        print(f"   Verified purchases: {verified_count}/{len(reviews)}\n")
        
        # Show sample
        sample = reviews[0]
        print(f"📝 Sample Review:")
        print(f"   Author: {sample['author']}")
        print(f"   Rating: {'⭐' * sample['rating']}")
        print(f"   Date: {sample['date']}")
        print(f"   Verified: {'✅' if sample.get('verified') else '❌'}")
        if sample.get('title'):
            print(f"   Title: {sample['title']}")
        print(f"   Text: {sample['text'][:200]}...")
    else:
        print("\n❌ No reviews found")
