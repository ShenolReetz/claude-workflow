#!/usr/bin/env python3
"""
Test Amazon scraping with different search terms
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer

async def test_amazon_search():
    """Test Amazon search with different terms"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize servers
    scraper = AmazonCategoryScraper(config)
    extractor = ProductCategoryExtractorMCPServer(config['anthropic_api_key'])
    
    # Test title
    test_title = "Top 5 New Car Mono Amplifiers Releases 2025"
    
    print(f"🧪 Testing Amazon search for: {test_title}")
    
    # Step 1: Extract category
    category_result = await extractor.extract_product_category(test_title)
    
    if category_result['success']:
        print(f"✅ Primary category: {category_result['primary_category']}")
        print(f"🎯 Search terms: {', '.join(category_result['search_terms'])}")
        
        # Step 2: Try different search terms
        search_terms = [category_result['primary_category']] + category_result['search_terms']
        
        for term in search_terms[:3]:  # Try first 3 terms
            print(f"\n🔍 Searching Amazon for: {term}")
            
            try:
                result = await scraper.get_top_5_products(term)
                
                if result['success']:
                    print(f"✅ Found {len(result['products'])} products")
                    for i, product in enumerate(result['products'][:2], 1):
                        print(f"   {i}. {product['title'][:50]}...")
                    break
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
        
        print(f"\n📊 Final result: {'Success' if result.get('success') else 'Failed'}")
    else:
        print(f"❌ Category extraction failed: {category_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_amazon_search())