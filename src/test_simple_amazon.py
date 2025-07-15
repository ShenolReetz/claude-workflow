#!/usr/bin/env python3
"""
Test Amazon scraping with simple, common search terms
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.amazon_category_scraper import AmazonCategoryScraper

async def test_simple_search():
    """Test Amazon search with simple terms"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize scraper
    scraper = AmazonCategoryScraper(config)
    
    # Test simple terms that should work
    test_terms = [
        "headphones",
        "bluetooth speakers", 
        "phone cases",
        "wireless chargers",
        "gaming headsets"
    ]
    
    for term in test_terms:
        print(f"\n🔍 Testing: {term}")
        
        try:
            result = await scraper.get_top_5_products(term)
            
            if result['success']:
                print(f"✅ Success! Found {len(result['products'])} products")
                for i, product in enumerate(result['products'][:2], 1):
                    print(f"   {i}. {product['title'][:50]}...")
                break
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n📊 Final test result: {'Success' if result.get('success') else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(test_simple_search())