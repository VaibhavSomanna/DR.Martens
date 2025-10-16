"""
Google Maps Review Scraper using Selenium
Scrapes real customer reviews from Google Maps
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
    """Setup Chrome driver with optimal options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run without opening browser
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_google_maps_reviews(place_name, location="", max_reviews=50):
    """
    Scrape reviews from Google Maps by searching for a place
    
    Args:
        place_name: Name of the business (e.g., "Dr. Martens")
        location: City or area to narrow search (e.g., "London")
        max_reviews: Maximum number of reviews to scrape (default 50)
    
    Returns:
        List of review dictionaries with author, rating, text, and date
    """
    driver = setup_driver()
    reviews = []
    
    try:
        # Build search query
        search_query = f"{place_name} {location}".strip()
        search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        print(f"🔍 Searching Google Maps for: {search_query}")
        driver.get(search_url)
        time.sleep(4)
        
        # Click on the first search result
        try:
            first_result = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.hfpxzc"))
            )
            first_result.click()
            print("✅ Found place, loading details...")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Could not find place: {e}")
            return reviews
        
        # Try to find and click the reviews button
        try:
            # Wait for reviews section to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='Reviews']"))
            )
            
            # Click reviews tab
            reviews_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Reviews']")
            driver.execute_script("arguments[0].click();", reviews_button)
            print("✅ Opened reviews section")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Could not open reviews section: {e}")
            # Try alternative method
            try:
                reviews_elements = driver.find_elements(By.XPATH, "//button[contains(text(), 'Reviews')]")
                if reviews_elements:
                    driver.execute_script("arguments[0].click();", reviews_elements[0])
                    time.sleep(3)
            except:
                print("❌ Failed to access reviews")
                return reviews
        
        # Find the scrollable container
        try:
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))
            )
        except:
            print("❌ Could not find scrollable container")
            return reviews
        
        # Scroll to load more reviews
        print(f"📜 Scrolling to load reviews (target: {max_reviews})...")
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        scroll_attempts = 0
        max_scrolls = 15  # Adjust based on how many reviews you want
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2.5)
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if new_height == last_height:
                print("   Reached end of reviews")
                break
            
            last_height = new_height
            scroll_attempts += 1
            
            # Check current count
            current_reviews = len(driver.find_elements(By.CSS_SELECTOR, "div.jftiEf"))
            print(f"   Loaded {current_reviews} reviews so far...")
            
            if current_reviews >= max_reviews:
                break
        
        # Expand "More" buttons to see full review text
        print("📖 Expanding review texts...")
        more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
        for idx, button in enumerate(more_buttons[:max_reviews]):
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.2)
            except:
                pass
        
        # Extract all reviews
        print("🔍 Extracting review data...")
        review_elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
        
        for idx, element in enumerate(review_elements[:max_reviews]):
            try:
                review_data = {}
                
                # Extract rating
                try:
                    rating_element = element.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                    rating_aria = rating_element.get_attribute("aria-label")
                    # Extract number from "5 stars", "4 stars", etc.
                    rating_match = re.search(r'(\d+)', rating_aria)
                    review_data['rating'] = int(rating_match.group(1)) if rating_match else 0
                except:
                    review_data['rating'] = 0
                
                # Extract review text
                try:
                    text_element = element.find_element(By.CSS_SELECTOR, "span.wiI7pd")
                    review_data['text'] = text_element.text.strip()
                except:
                    review_data['text'] = ""
                
                # Extract author name
                try:
                    author_element = element.find_element(By.CSS_SELECTOR, "div.d4r55")
                    review_data['author'] = author_element.text.strip()
                except:
                    review_data['author'] = "Anonymous"
                
                # Extract date
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, "span.rsqaWe")
                    review_data['date'] = date_element.text.strip()
                except:
                    review_data['date'] = "Unknown"
                
                # Only add reviews that have actual text
                if review_data['text'] and len(review_data['text']) > 10:
                    reviews.append(review_data)
                    
            except Exception as e:
                print(f"   ⚠️ Error extracting review {idx + 1}: {e}")
                continue
        
        print(f"✅ Successfully scraped {len(reviews)} reviews")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    
    finally:
        driver.quit()
    
    return reviews

def scrape_from_place_id(place_id, max_reviews=50):
    """
    Scrape reviews using a Google Maps place ID
    Note: This builds a Google Maps URL from the place_id
    
    Args:
        place_id: Google Places API place_id
        max_reviews: Maximum number of reviews to scrape
    
    Returns:
        List of review dictionaries
    """
    driver = setup_driver()
    reviews = []
    
    try:
        # Construct Google Maps URL from place_id
        maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        
        print(f"🔍 Loading Google Maps from place_id...")
        driver.get(maps_url)
        time.sleep(4)
        
        # The rest is similar to scrape_google_maps_reviews
        # Try to open reviews
        try:
            reviews_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Reviews']"))
            )
            driver.execute_script("arguments[0].click();", reviews_button)
            print("✅ Opened reviews section")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Could not open reviews: {e}")
            return reviews
        
        # Find scrollable container
        try:
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))
            )
        except:
            print("❌ Could not find scrollable container")
            return reviews
        
        # Scroll to load reviews
        print(f"📜 Scrolling to load reviews...")
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        scroll_attempts = 0
        max_scrolls = 15
        
        while scroll_attempts < max_scrolls:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2.5)
            
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
            
            current_count = len(driver.find_elements(By.CSS_SELECTOR, "div.jftiEf"))
            print(f"   Loaded {current_count} reviews...")
            if current_count >= max_reviews:
                break
        
        # Expand "More" buttons
        more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
        for button in more_buttons[:max_reviews]:
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.2)
            except:
                pass
        
        # Extract reviews
        review_elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
        
        for element in review_elements[:max_reviews]:
            try:
                review_data = {}
                
                # Extract rating
                try:
                    rating_element = element.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                    rating_aria = rating_element.get_attribute("aria-label")
                    rating_match = re.search(r'(\d+)', rating_aria)
                    review_data['rating'] = int(rating_match.group(1)) if rating_match else 0
                except:
                    review_data['rating'] = 0
                
                # Extract text
                try:
                    text_element = element.find_element(By.CSS_SELECTOR, "span.wiI7pd")
                    review_data['text'] = text_element.text.strip()
                except:
                    review_data['text'] = ""
                
                # Extract author
                try:
                    author_element = element.find_element(By.CSS_SELECTOR, "div.d4r55")
                    review_data['author'] = author_element.text.strip()
                except:
                    review_data['author'] = "Anonymous"
                
                # Extract date
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, "span.rsqaWe")
                    review_data['date'] = date_element.text.strip()
                except:
                    review_data['date'] = "Unknown"
                
                if review_data['text'] and len(review_data['text']) > 10:
                    reviews.append(review_data)
                    
            except Exception as e:
                continue
        
        print(f"✅ Successfully scraped {len(reviews)} reviews")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
    
    return reviews

if __name__ == "__main__":
    # Test the scraper
    print("=" * 60)
    print("Testing Google Maps Review Scraper")
    print("=" * 60)
    
    # Test with place name
    reviews = scrape_google_maps_reviews("Dr. Martens", "Covent Garden London", max_reviews=20)
    
    if reviews:
        print(f"\n✅ SUCCESS! Scraped {len(reviews)} reviews\n")
        print("Sample review:")
        print(f"  Author: {reviews[0]['author']}")
        print(f"  Rating: {reviews[0]['rating']}/5")
        print(f"  Date: {reviews[0]['date']}")
        print(f"  Text: {reviews[0]['text'][:150]}...")
    else:
        print("\n❌ No reviews found. Check the place name and try again.")
