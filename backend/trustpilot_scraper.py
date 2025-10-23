"""
Trustpilot Review Scraper
Scrapes product reviews from Trustpilot.com using direct URL search
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
from datetime import datetime
from urllib.parse import quote

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
    Scrape reviews from Trustpilot using direct URL search parameter
    Only returns reviews that match the product-specific keywords
    
    Args:
        product_name: Product name to search for (e.g., "Dr Martens 1460", "Timberland 6 inch")
        max_reviews: Maximum number of reviews to scrape
    
    Returns:
        List of review dictionaries (only product-specific reviews)
    """
    driver = None
    reviews = []
    
    try:
        print(f"🔍 Scraping Trustpilot for: {product_name}")
        
        driver = setup_driver()
        
        # Determine the brand/company from the product name
        product_lower = product_name.lower()
        
        # Map brands to their Trustpilot URLs - try multiple regions
        brand_urls = {
            'dr martens': [
                'https://www.trustpilot.com/review/www.drmartens.com',
                'https://uk.trustpilot.com/review/www.drmartens.com'
            ],
            'dr. martens': [
                'https://www.trustpilot.com/review/www.drmartens.com',
                'https://uk.trustpilot.com/review/www.drmartens.com'
            ],
            'drmartens': [
                'https://www.trustpilot.com/review/www.drmartens.com',
                'https://uk.trustpilot.com/review/www.drmartens.com'
            ],
            'timberland': [
                'https://www.trustpilot.com/review/www.timberland.com',
                'https://uk.trustpilot.com/review/www.timberland.co.uk'
            ],
            'solovair': [
                'https://uk.trustpilot.com/review/www.solovair.co.uk',
                'https://www.trustpilot.com/review/www.solovair.co.uk'
            ],
            'red wing': [
                'https://www.trustpilot.com/review/www.redwingshoes.com',
                'https://uk.trustpilot.com/review/www.redwingshoes.com'
            ],
            'redwing': [
                'https://www.trustpilot.com/review/www.redwingshoes.com',
                'https://uk.trustpilot.com/review/www.redwingshoes.com'
            ],
            'birkenstock': [
                'https://www.trustpilot.com/review/www.birkenstock.com',
                'https://uk.trustpilot.com/review/www.birkenstock.co.uk'
            ],
            'clarks': [
                'https://www.trustpilot.com/review/www.clarks.com',
                'https://uk.trustpilot.com/review/www.clarks.co.uk'
            ],
            'ugg': [
                'https://www.trustpilot.com/review/www.ugg.com',
                'https://uk.trustpilot.com/review/www.ugg.co.uk'
            ],
        }
        
        # Find matching brand URLs
        brand_urls_to_try = []
        brand_found = None
        for brand, urls in brand_urls.items():
            if brand in product_lower:
                brand_urls_to_try = urls
                brand_found = brand
                break
        
        if not brand_urls_to_try:
            print(f"⚠️ No Trustpilot page found for brand in: {product_name}")
            print(f"ℹ️ Supported brands: Dr Martens, Timberland, Solovair, Red Wing, Birkenstock, Clarks, UGG")
            return []
        
        # Extract product-specific keywords for search
        search_keywords = []
        
        # Common product identifiers
        keywords_to_extract = [
            '1460', '1461', '2976', 'jadon', 'sinclair', 'chelsea', 'jadons',
            '6 inch', '6-inch', '6in', 'premium', 'yellow boot', 'wheat',
            'classic', 'original', 'vegan', 'leather', 'smooth', 'nappa'
        ]
        
        for keyword in keywords_to_extract:
            if keyword in product_lower:
                search_keywords.append(keyword)
        
        # Debug output
        print(f"📝 DEBUG: Product name: '{product_name}'")
        print(f"📝 DEBUG: Product lowercase: '{product_lower}'")
        print(f"📝 DEBUG: Keywords found: {search_keywords}")
        
        # IMPORTANT: Only search if we have specific product keywords
        if not search_keywords:
            print(f"⚠️ No specific product keywords found in '{product_name}'")
            print(f"⚠️ Will not return general brand reviews. Returning empty list.")
            return []
        
        search_query = search_keywords[0]  # Use the most specific keyword
        print(f"🔎 Searching Trustpilot with keyword: '{search_query}'")
        print(f"📝 DEBUG: Brand URLs to try: {brand_urls_to_try}")
        
        # Try each brand URL until we find one with reviews
        trustpilot_url = None
        review_elements = []
        
        for base_url in brand_urls_to_try:
            try:
                # Use Trustpilot's built-in ?search= parameter
                # This loads a page with ONLY reviews containing the keyword
                search_url = f"{base_url}?search={quote(search_query)}"
                
                print(f"🌐 Trying URL: {search_url}")
                driver.get(search_url)
                
                # Wait for page to load
                time.sleep(4)
                
                # Check if page loaded successfully
                if "404" in driver.title or "not found" in driver.title.lower():
                    print(f"   ⚠️ 404 - trying next URL...")
                    continue
                
                # Accept cookies if present
                try:
                    cookie_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                    )
                    cookie_button.click()
                    time.sleep(1)
                    print(f"   ✅ Accepted cookies")
                except:
                    pass
                
                # Try multiple selectors for review cards
                selectors_to_try = [
                    'article[data-service-review-card-paper]',
                    'div[data-service-review-card]',
                    'article.review',
                    'div.review-card',
                    'section[class*="review"]',
                    'div[class*="styles_reviewCard"]',
                    'div[data-service-review]'
                ]
                
                for selector in selectors_to_try:
                    review_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if review_elements and len(review_elements) > 0:
                        print(f"   ✅ Found {len(review_elements)} review elements using selector: {selector}")
                        trustpilot_url = base_url
                        break
                
                if review_elements and len(review_elements) > 0:
                    break  # Found working URL with reviews
                else:
                    print(f"   ⚠️ No reviews found - trying next URL...")
                    
            except Exception as e:
                print(f"   ⚠️ Error with URL: {e}")
                continue
        
        if not trustpilot_url or not review_elements:
            print(f"❌ Could not find any Trustpilot reviews for '{search_query}'")
            print(f"   Tried {len(brand_urls_to_try)} URL(s) for {brand_found}")
            print(f"   This means either:")
            print(f"   1. Trustpilot has no reviews mentioning '{search_query}' for this brand")
            print(f"   2. The brand's Trustpilot page doesn't exist or has changed")
            print(f"   💡 Suggestion: Try manually visiting: {brand_urls_to_try[0]}?search={quote(search_query)}")
            return []
        
        print(f"✅ Using Trustpilot URL: {trustpilot_url}")
        print(f"📜 Extracting review data from search results...")
        
        # Scroll to load more reviews
        print(f"🔄 Scrolling to load more reviews...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        pages_loaded = 0
        max_pages = 5
        
        while pages_loaded < max_pages and len(reviews) < max_reviews:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            pages_loaded += 1
            
            # Refresh review elements after scrolling
            for selector in selectors_to_try:
                new_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if new_elements and len(new_elements) > len(review_elements):
                    review_elements = new_elements
                    print(f"   📊 Loaded {len(review_elements)} total reviews")
                    break
        
        print(f"📊 Total review elements: {len(review_elements)}")
        
        reviews_extracted = 0
        
        for idx, review_elem in enumerate(review_elements):
            if len(reviews) >= max_reviews:
                break
            
            try:
                # Scroll element into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", review_elem)
                time.sleep(0.3)
                
                # Try to expand "Read more" button
                try:
                    read_more = review_elem.find_elements(By.CSS_SELECTOR, 
                        "button[class*='show-more'], button[class*='ShowMore'], button[data-show-more-trigger]")
                    if read_more:
                        try:
                            driver.execute_script("arguments[0].click();", read_more[0])
                            time.sleep(0.5)
                        except:
                            pass
                except:
                    pass
                
                # Extract rating (default to None if not found)
                rating = None
                try:
                    rating_elem = review_elem.find_element(By.CSS_SELECTOR, 'div[data-service-review-rating]')
                    rating_img = rating_elem.find_element(By.TAG_NAME, 'img')
                    rating_alt = rating_img.get_attribute('alt')
                    if rating_alt and 'Rated' in rating_alt:
                        rating = int(rating_alt.split()[1])
                except:
                    try:
                        star_images = review_elem.find_elements(By.CSS_SELECTOR, 'img[alt*="star"]')
                        filled = [s for s in star_images if 'filled' in s.get_attribute('src').lower() or 'full' in s.get_attribute('src').lower()]
                        if filled:
                            rating = len(filled)
                    except:
                        pass
                
                # Extract title
                title = ""
                title_selectors = [
                    'h2[data-service-review-title-typography]',
                    'h2[class*="title"]',
                    'h3[class*="title"]',
                    '[data-service-review-title]'
                ]
                
                for selector in title_selectors:
                    try:
                        title_elem = review_elem.find_element(By.CSS_SELECTOR, selector)
                        title = title_elem.text.strip()
                        if title and len(title) > 3:
                            break
                    except:
                        continue
                
                # If no title found, try h2/h3 tags
                if not title:
                    try:
                        headings = review_elem.find_elements(By.CSS_SELECTOR, 'h2, h3')
                        for h in headings:
                            t = h.text.strip()
                            if t and len(t) > 3:
                                title = t
                                break
                    except:
                        pass
                
                # Extract review text - MULTIPLE METHODS
                text = ""
                
                # Method 1: Known text selectors
                text_selectors = [
                    'p[data-service-review-text-typography]',
                    'div[data-service-review-text]',
                    'p[class*="typography_body"]',
                    '[data-review-content-body]'
                ]
                
                for selector in text_selectors:
                    try:
                        text_elems = review_elem.find_elements(By.CSS_SELECTOR, selector)
                        if text_elems:
                            texts = [t.text.strip() for t in text_elems if len(t.text.strip()) > 10]
                            if texts:
                                text = ' '.join(texts)
                                break
                    except:
                        continue
                
                # Method 2: All <p> tags
                if not text or len(text) < 20:
                    try:
                        paragraphs = review_elem.find_elements(By.TAG_NAME, 'p')
                        para_texts = []
                        for p in paragraphs:
                            p_text = p.text.strip()
                            if (len(p_text) > 15 and 
                                'Date of experience' not in p_text and
                                'Report' not in p_text):
                                para_texts.append(p_text)
                        if para_texts:
                            text = ' '.join(para_texts)
                    except:
                        pass
                
                # Method 3: Full element text with filtering
                if not text or len(text) < 20:
                    try:
                        all_text = review_elem.text.strip()
                        lines = all_text.split('\n')
                        content_lines = []
                        for line in lines:
                            line = line.strip()
                            if (len(line) > 15 and
                                'Date of experience' not in line and
                                'Report' not in line and
                                'Helpful' not in line and
                                not line.isdigit()):
                                content_lines.append(line)
                        
                        if content_lines:
                            text = ' '.join(content_lines[:5])  # Take first 5 meaningful lines
                    except:
                        pass
                
                # Use title as fallback
                if (not text or len(text) < 20) and title:
                    text = title
                
                # Skip if still no content
                if not text or len(text) < 20:
                    if idx < 3:
                        print(f"[DEBUG] Review #{idx+1}: Skipped - insufficient text (len={len(text) if text else 0})")
                    continue
                
                # Debug first few extractions
                if idx < 3:
                    print(f"[DEBUG] Review #{idx+1}:")
                    print(f"        Title: '{title[:60] if title else 'N/A'}'")
                    print(f"        Text: '{text[:100]}...'")
                    print(f"        Rating: {rating}/5")
                
                # Extract author
                author = "Anonymous"
                author_selectors = [
                    'span[data-consumer-name-typography]',
                    'a[data-consumer-profile-link]',
                    '[data-consumer-name]'
                ]
                
                for selector in author_selectors:
                    try:
                        author_elem = review_elem.find_element(By.CSS_SELECTOR, selector)
                        author = author_elem.text.strip()
                        if author:
                            break
                    except:
                        continue
                
                # Extract date
                date = datetime.now().strftime('%Y-%m-%d')
                try:
                    time_elem = review_elem.find_element(By.CSS_SELECTOR, 'time')
                    date_str = time_elem.get_attribute('datetime')
                    if date_str:
                        date = date_str[:10]
                except:
                    pass
                
                # Extract verification
                verified = False
                try:
                    verified_badge = review_elem.find_elements(By.CSS_SELECTOR, 
                        'div[data-service-review-verification-badge], [data-verification-badge]')
                    verified = len(verified_badge) > 0
                except:
                    pass
                
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
                
                reviews_extracted += 1
                
                if reviews_extracted == 1:
                    print(f"\n✅ First review extracted successfully!")
                    print(f"   Title: {title[:80] if title else 'N/A'}")
                    print(f"   Text: {text[:150]}...")
                    print(f"   Rating: {rating}/5\n")
                
            except Exception as e:
                if idx < 3:
                    print(f"⚠️ Error extracting review #{idx+1}: {e}")
                continue
        
        if len(reviews) == 0:
            print(f"⚠️ No product-specific reviews extracted for '{search_query}'")
            print(f"   The Trustpilot search may not have returned relevant results")
        else:
            print(f"✅ Successfully scraped {len(reviews)} product-specific Trustpilot reviews")
            print(f"   Keyword: '{search_query}'")
            print(f"   Source: {trustpilot_url}")
        
        return reviews
        
    except Exception as e:
        print(f"❌ Error scraping Trustpilot: {e}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        if driver:
            driver.quit()

# Test function
if __name__ == "__main__":
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("="*60)
    print("Testing Trustpilot Review Scraper (Direct URL Search)")
    print("="*60)
    
    test_queries = [
        "Dr Martens 1460",
        "Timberland 6 inch boot",
    ]
    
    for test_query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: {test_query}")
        print(f"{'='*60}\n")
        
        reviews = scrape_trustpilot_reviews(test_query, max_reviews=15)
        
        if reviews:
            print(f"\n{'='*40}")
            print(f"Summary:")
            print(f"{'='*40}")
            print(f"  Total reviews: {len(reviews)}")
            print(f"  Average rating: {sum(r['rating'] for r in reviews) / len(reviews):.1f}/5")
            print(f"  Verified: {sum(1 for r in reviews if r.get('verified'))}/{len(reviews)}")
            
            print(f"\nSample review:")
            sample = reviews[0]
            print(f"  Author: {sample['author']}")
            print(f"  Rating: {'⭐' * sample['rating']}")
            print(f"  Date: {sample['date']}")
            if sample.get('title'):
                print(f"  Title: {sample['title'][:80]}")
            print(f"  Text: {sample['text'][:200]}...")
        else:
            print(f"\n❌ No reviews found")
        
        time.sleep(3)
        time.sleep(2)