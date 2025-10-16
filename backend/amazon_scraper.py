"""
Amazon Review Scraper using Selenium
Scrapes customer reviews from Amazon product pages
NOTE: Amazon has strong bot detection - scrapes only from product page (8-10 reviews)
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def setup_driver():
    """Setup Chrome driver with optimal options for Amazon"""
    chrome_options = Options()
    
    # Run in visible mode (not headless) to avoid bot detection
    # chrome_options.add_argument('--headless=new')  # DISABLED - Amazon blocks headless
    
    # Essential options for stability
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')  # Suppress logs
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    
    # Anti-detection options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Realistic user agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Additional anti-detection preferences
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Enhanced anti-detection scripts
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            "platform": "Windows",
            "acceptLanguage": "en-US,en;q=0.9"
        })
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        driver.execute_script("window.chrome = { runtime: {} }")
        
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        raise

def scrape_amazon_reviews(product_name, max_reviews=20):
    """
    Scrape reviews from Amazon by searching for a product
    NOTE: Only scrapes ~8-10 reviews from product page due to Amazon's login requirements
    
    Args:
        product_name: Name of the product (e.g., "Dr. Martens 1460 boots")
        max_reviews: Maximum number of reviews to scrape (default 20, but will get ~8-10)
    
    Returns:
        Tuple of (product_info dict, reviews list)
    """
    driver = setup_driver()
    reviews = []
    product_info = {
        'name': product_name,
        'url': '',
        'rating': 0,
        'total_ratings': 0
    }
    
    try:
        # Visit Amazon homepage first to establish session
        print(f"🏠 Visiting Amazon homepage to establish session...")
        try:
            driver.get("https://www.amazon.com")
            time.sleep(2)
            print("✅ Session established")
        except Exception as e:
            print(f"❌ Failed to load Amazon homepage: {e}")
            raise Exception(f"Could not access Amazon. Please check your internet connection.")
        
        # Search for product on Amazon
        search_query = product_name.replace(' ', '+')
        search_url = f"https://www.amazon.com/s?k={search_query}"
        
        print(f"🔍 Searching Amazon for: {product_name}")
        
        try:
            driver.get(search_url)
            print("✅ Loaded Amazon search page")
        except Exception as e:
            print(f"❌ Failed to load Amazon search: {e}")
            raise Exception(f"Could not access Amazon search.")
        
        time.sleep(3)
        
        # Check if page loaded correctly
        try:
            driver.find_element(By.TAG_NAME, "body")
            print("✅ Page body loaded")
        except:
            raise Exception("Amazon page did not load properly.")
        
        # Click on first product result - try multiple selectors
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']"))
            )
            print("✅ Search results loaded")
            
            first_product = None
            selectors = [
                "h2 a.a-link-normal",
                "h2.a-size-mini a",
                "div.s-product-image-container a",
                "a.s-link-style"
            ]
            
            for selector in selectors:
                try:
                    first_product = driver.find_element(By.CSS_SELECTOR, selector)
                    if first_product:
                        print(f"✅ Found product with selector: {selector}")
                        break
                except:
                    continue
            
            if not first_product:
                raise Exception("Could not find any products in search results")
            
            product_url = first_product.get_attribute('href')
            product_info['url'] = product_url
            
            # Extract product title
            try:
                product_title = first_product.text.strip()
                if product_title:
                    product_info['name'] = product_title
                    print(f"✅ Found product: {product_title[:60]}...")
            except:
                print("⚠️ Could not extract product title from link")
            
            print(f"🔗 Navigating to product page...")
            driver.get(product_url)
            time.sleep(3)
            
            # Get overall rating
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, "span.a-icon-alt")
                rating_text = rating_element.get_attribute('textContent')
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    product_info['rating'] = float(rating_match.group(1))
            except:
                pass
            
            # Get total ratings count
            try:
                ratings_count = driver.find_element(By.CSS_SELECTOR, "#acrCustomerReviewText")
                count_text = ratings_count.text
                count_match = re.search(r'([\d,]+)', count_text)
                if count_match:
                    product_info['total_ratings'] = int(count_match.group(1).replace(',', ''))
            except:
                pass
            
        except Exception as e:
            print(f"❌ Could not find product: {str(e)[:200]}")
            driver.quit()
            raise Exception(f"Amazon search failed: {str(e)[:200]}")
        
        # Scrape reviews from product page (avoid login page)
        print("📜 Scraping reviews from product page...")
        time.sleep(2)
        
        # Scroll down to load reviews section
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
        except:
            pass
        
        # Try multiple selectors for review containers
        review_elements = []
        review_selectors = [
            "div[data-hook='review']",
            "div[data-hook='review-collapsed']",
            "div.review",
            "div[id^='customer_review']"
        ]
        
        for selector in review_selectors:
            try:
                review_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if review_elements:
                    print(f"   ✅ Found {len(review_elements)} reviews with selector: {selector}")
                    break
            except:
                continue
        
        # Process found reviews
        for element in review_elements:
            if len(reviews) >= max_reviews:
                break
            
            try:
                review_data = {}
                
                # Extract rating
                try:
                    rating_selectors = [
                        "i[data-hook='review-star-rating'] span",
                        "i.review-rating span",
                        "span.a-icon-alt"
                    ]
                    rating_text = None
                    for sel in rating_selectors:
                        try:
                            rating_element = element.find_element(By.CSS_SELECTOR, sel)
                            rating_text = rating_element.get_attribute('textContent') or rating_element.text
                            if rating_text:
                                break
                        except:
                            continue
                    
                    if rating_text:
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        review_data['rating'] = float(rating_match.group(1)) if rating_match else 0
                    else:
                        review_data['rating'] = 0
                except:
                    review_data['rating'] = 0
                
                # Extract review title
                try:
                    title_selectors = [
                        "a[data-hook='review-title'] span",
                        "a[data-hook='review-title']",
                        "div[data-hook='review-title'] span"
                    ]
                    review_data['title'] = ""
                    for sel in title_selectors:
                        try:
                            title_element = element.find_element(By.CSS_SELECTOR, sel)
                            title = title_element.text.strip()
                            if title:
                                review_data['title'] = title
                                break
                        except:
                            continue
                except:
                    review_data['title'] = ""
                
                # Extract review text
                try:
                    text_selectors = [
                        "span[data-hook='review-body'] span",
                        "span[data-hook='review-body']",
                        "div.reviewText span"
                    ]
                    review_data['text'] = ""
                    for sel in text_selectors:
                        try:
                            text_element = element.find_element(By.CSS_SELECTOR, sel)
                            text = text_element.text.strip()
                            if text:
                                review_data['text'] = text
                                break
                        except:
                            continue
                except:
                    review_data['text'] = ""
                
                # Extract author name
                try:
                    author_selectors = [
                        "span.a-profile-name",
                        "div.a-profile-name"
                    ]
                    review_data['author'] = "Anonymous"
                    for sel in author_selectors:
                        try:
                            author_element = element.find_element(By.CSS_SELECTOR, sel)
                            author = author_element.text.strip()
                            if author:
                                review_data['author'] = author
                                break
                        except:
                            continue
                except:
                    review_data['author'] = "Anonymous"
                
                # Extract date
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, "span[data-hook='review-date']")
                    review_data['date'] = date_element.text.strip()
                except:
                    review_data['date'] = "Unknown"
                
                # Extract verified purchase status
                try:
                    verified = element.find_element(By.CSS_SELECTOR, "span[data-hook='avp-badge']")
                    review_data['verified'] = True
                except:
                    review_data['verified'] = False
                
                # Only add reviews with text
                if review_data['text'] and len(review_data['text']) > 10:
                    reviews.append(review_data)
                    
            except Exception as e:
                print(f"   ⚠️ Error extracting review: {e}")
                continue
        
        print(f"✅ Successfully scraped {len(reviews)} reviews from product page")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
    
    return product_info, reviews

if __name__ == "__main__":
    # Test the scraper
    print("=" * 60)
    print("Testing Amazon Review Scraper")
    print("=" * 60)
    
    # Test with product name
    product_info, reviews = scrape_amazon_reviews("Dr Martens 1460 boots", max_reviews=20)
    
    if reviews:
        print(f"\n✅ SUCCESS! Scraped {len(reviews)} reviews\n")
        print(f"Product: {product_info['name'][:60]}")
        print(f"Rating: {product_info['rating']}/5")
        print(f"Total Ratings: {product_info['total_ratings']}")
        print("\nSample review:")
        print(f"  Author: {reviews[0]['author']}")
        print(f"  Rating: {reviews[0]['rating']}/5")
        print(f"  Title: {reviews[0]['title']}")
        print(f"  Date: {reviews[0]['date']}")
        print(f"  Verified: {reviews[0]['verified']}")
        print(f"  Text: {reviews[0]['text'][:150]}...")
    else:
        print("\n❌ No reviews found. Check the product name and try again.")
