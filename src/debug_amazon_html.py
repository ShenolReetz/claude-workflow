#!/usr/bin/env python3
"""
Debug Amazon HTML structure to understand why titles are empty
"""

import asyncio
import json
import sys
import httpx
from bs4 import BeautifulSoup

sys.path.append('/home/claude-workflow')

async def debug_amazon_html():
    """Debug Amazon HTML structure"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Test search
    search_term = "headsets for gaming"
    api_key = config['scrapingdog_api_key']
    
    print(f"🔍 Debugging Amazon HTML for: {search_term}")
    
    try:
        # Call ScrapingDog API
        url = f"https://api.scrapingdog.com/scrape"
        params = {
            'api_key': api_key,
            'url': f"https://www.amazon.com/s?k={search_term.replace(' ', '%20')}&s=review-rank",
            'dynamic': 'false',
            'country': 'us'
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                html = response.text
                print(f"✅ Got HTML response ({len(html)} characters)")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find products
                products = soup.find_all('div', {'data-component-type': 's-search-result'})
                print(f"📦 Found {len(products)} products")
                
                if products:
                    first_product = products[0]
                    print(f"\n🔍 Analyzing first product:")
                    print(f"   ASIN: {first_product.get('data-asin', 'N/A')}")
                    
                    # Try different title selectors
                    title_selectors = [
                        'h2 a span',
                        'h2 span',
                        'h2 a',
                        '.a-link-normal .a-truncate-cut',
                        '.a-link-normal span',
                        '[data-cy="title-recipe-title"]'
                    ]
                    
                    for selector in title_selectors:
                        title_elem = first_product.select_one(selector)
                        title = title_elem.text.strip() if title_elem else ''
                        print(f"   Title ({selector}): '{title}'")
                    
                    # Check if there's any text in h2
                    h2_elem = first_product.select_one('h2')
                    if h2_elem:
                        print(f"   H2 raw text: '{h2_elem.get_text().strip()}'")
                    
                    # Save first product HTML for inspection
                    with open('/home/claude-workflow/debug_product.html', 'w') as f:
                        f.write(str(first_product))
                    print(f"💾 Saved first product HTML to debug_product.html")
                
                return True
            else:
                print(f"❌ ScrapingDog API error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_amazon_html())
    if result:
        print("\n🎉 Amazon HTML debugging complete!")
    else:
        print("\n💥 Amazon HTML debugging failed")