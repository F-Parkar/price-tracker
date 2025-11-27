"""
Enhanced Price Scraper with Selenium Support for React/SPA apps
File: services/price_scraper.py
"""

import re
import requests
from bs4 import BeautifulSoup

def extract_price(html, css_selector=None):
    """Extract price from HTML content"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # If user provided a CSS selector, try that first
    if css_selector:
        elements = soup.select(css_selector)
        for element in elements:
            price_text = element.get_text()
            price = parse_price(price_text)
            if price:
                print(f"  Found with CSS selector: {price_text.strip()[:50]} → R{price}")
                return price
    
    # Common price patterns to search for
    price_patterns = [
        {'class': re.compile(r'price', re.I)},
        {'id': re.compile(r'price', re.I)},
        {'itemprop': 'price'},
        {'class': re.compile(r'cost', re.I)},
        {'class': re.compile(r'amount', re.I)},
        {'data-price': True},
        {'class': re.compile(r'product-price', re.I)},
    ]
    
    for pattern in price_patterns:
        elements = soup.find_all(attrs=pattern)
        for element in elements:
            price_text = element.get_text()
            price = parse_price(price_text)
            if price:
                print(f"  Found with pattern {pattern}: {price_text.strip()[:50]} → R{price}")
                return price
    
    # Try to find any price-like pattern in the entire page
    # Look for currency symbols followed by numbers
    price_regex = r'[R$]\s*\d+(?:[,\s]\d{3})*(?:\.\d{2})?'
    matches = re.findall(price_regex, html)
    if matches:
        # Try each match and return the first valid price
        for match in matches:
            price = parse_price(match)
            if price:
                print(f"  Found with regex: {match} → R{price}")
                return price
    
    return None

def parse_price(text):
    """Extract numeric price from text (handles R and $ symbols and formatting)"""
    text = text.strip()
    
    # Try to find price with currency symbol first (more accurate)
    # Match R or $ followed by numbers
    currency_patterns = [
        r'[$R]\s*(\d+(?:[,\s]\d{3})*(?:\.\d{2})?)',  # $495 or R495 or $ 495
        r'(\d+(?:[,\s]\d{3})*(?:\.\d{2})?)\s*[$R]',  # 495$ or 495R
    ]
    
    for pattern in currency_patterns:
        match = re.search(pattern, text)
        if match:
            price_str = match.group(1).replace(',', '').replace(' ', '')
            try:
                price = float(price_str)
                # Sanity check: price should be reasonable (between 0.01 and 1,000,000)
                if 0.01 < price < 1000000:
                    return price
            except ValueError:
                continue
    
    # Fallback: find any numbers in the text
    # But only if they look like prices (2+ digits or have decimals)
    all_numbers = re.findall(r'\d+(?:\.\d{2})?', text)
    for num_str in all_numbers:
        try:
            price = float(num_str)
            # Only accept if it looks like a real price
            if price >= 10:  # Minimum price threshold
                return price
        except ValueError:
            continue
    
    return None

def fetch_price_simple(url, css_selector=None):
    """Fetch price using simple requests (fast, but won't work for React/SPA)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-ZA,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return extract_price(response.text, css_selector)
    except Exception as e:
        print(f"Error fetching with requests: {e}")
        return None

def fetch_price_selenium(url, css_selector=None):
    """Fetch price from JavaScript-rendered pages using Selenium (works for React/SPA)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Setup headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load (wait for body to be present)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content to load
        import time
        time.sleep(3)  # Wait 3 seconds for JavaScript to render
        
        html = driver.page_source
        driver.quit()
        
        return extract_price(html, css_selector)
    except ImportError:
        print("❌ Selenium not installed. Install with: pip install selenium")
        return None
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        return None

def fetch_price(url, css_selector=None, force_selenium=False):
    """
    Main function to fetch price with automatic fallback
    
    Args:
        url: Product URL
        css_selector: Optional CSS selector
        force_selenium: If True, skip requests and go straight to Selenium
    
    Returns:
        float: Price or None
    """
    # If force_selenium flag is set, use Selenium directly
    if force_selenium:
        print("🌐 Using Selenium (JavaScript rendering enabled)...")
        return fetch_price_selenium(url, css_selector)
    
    # Try simple requests first (faster)
    print("🔍 Trying simple fetch...")
    price = fetch_price_simple(url, css_selector)
    
    if price:
        print(f"✓ Price found: R{price}")
        return price
    
    # If simple fetch fails, try Selenium (for React/SPA apps)
    print("🌐 Simple fetch failed. Trying Selenium (JavaScript rendering)...")
    price = fetch_price_selenium(url, css_selector)
    
    if price:
        print(f"✓ Price found with Selenium: R{price}")
        return price
    
    print("❌ Could not detect price")
    return None