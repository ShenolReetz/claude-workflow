#!/usr/bin/env python3
"""
Debug the product structure to understand the issue
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer

async def debug_product_structure():
    """Debug the product structure"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize servers
    scraper = AmazonCategoryScraper(config)
    extractor = ProductCategoryExtractorMCPServer(config['anthropic_api_key'])
    
    # Test title
    test_title = "🔥 TOP 5 Gaming Headsets That Will Blow Your Mind! 🎮"
    
    print(f"🧪 Testing product structure for: {test_title}")
    
    # Step 1: Extract category
    category_result = await extractor.extract_product_category(test_title)
    
    if category_result['success']:
        print(f"✅ Primary category: {category_result['primary_category']}")
        
        # Step 2: Try Amazon scraping
        search_terms = [category_result['primary_category']] + category_result['search_terms']
        
        for term in search_terms[:3]:
            print(f"\n🔍 Searching Amazon for: {term}")
            
            try:
                result = await scraper.get_top_5_products(term)
                
                if result['success']:
                    print(f"✅ Found {len(result['products'])} products")
                    print(f"📦 Product structure:")
                    
                    for i, product in enumerate(result['products'], 1):
                        print(f"   Product {i}:")
                        print(f"      Title: {product.get('title', 'N/A')}")
                        print(f"      Price: {product.get('price', 'N/A')}")
                        print(f"      Rating: {product.get('rating', 'N/A')}")
                        print(f"      Reviews: {product.get('review_count', 'N/A')}")
                        print(f"      Image URL: {product.get('image_url', 'N/A')}")
                        print(f"      Affiliate: {product.get('affiliate_link', 'N/A')}")
                        print()
                    
                    print(f"📊 Airtable data structure:")
                    airtable_data = result.get('airtable_data', {})
                    for key, value in airtable_data.items():
                        print(f"   {key}: {value}")
                    
                    return result
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    return None

if __name__ == "__main__":
    result = asyncio.run(debug_product_structure())
    if result:
        print("\n🎉 Product structure debugging complete!")
    else:
        print("\n💥 Product structure debugging failed")