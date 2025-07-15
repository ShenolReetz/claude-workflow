#!/usr/bin/env python3
"""
Test fresh workflow with direct record fetching
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer
from mcp_servers.amazon_category_scraper import AmazonCategoryScraper

async def test_fresh_workflow():
    """Test fresh workflow with direct record fetching"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize servers
    airtable = AirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_name']
    )
    extractor = ProductCategoryExtractorMCPServer(config['anthropic_api_key'])
    scraper = AmazonCategoryScraper(config)
    
    print("🚀 Starting fresh workflow test...")
    
    # Step 1: Get the specific record directly
    record_id = "rec00Yb60qB6jOXSE"
    record = await airtable.get_record_by_id(record_id)
    
    if not record:
        print("❌ Could not fetch record")
        return False
    
    title = record.get('fields', {}).get('VideoTitle', '')
    status = record.get('fields', {}).get('Status', '')
    
    print(f"📋 Record: {record_id}")
    print(f"📋 Title: {title}")
    print(f"📋 Status: {status}")
    
    # Step 2: Extract category
    print("\n🔍 Extracting product category...")
    category_result = await extractor.extract_product_category(title)
    
    if not category_result['success']:
        print(f"❌ Category extraction failed: {category_result.get('error')}")
        return False
    
    clean_category = category_result['primary_category']
    print(f"✅ Extracted category: {clean_category}")
    print(f"🎯 Alternative terms: {', '.join(category_result['search_terms'][:3])}")
    
    # Step 3: Try Amazon scraping
    print("\n🛒 Testing Amazon scraping...")
    search_terms = [clean_category] + category_result['search_terms']
    
    for term in search_terms[:3]:
        print(f"🔍 Trying search term: {term}")
        result = await scraper.get_top_5_products(term)
        
        if result['success']:
            print(f"✅ Found {len(result['products'])} products with term: {term}")
            print(f"📦 Products:")
            for i, product in enumerate(result['products'][:3], 1):
                print(f"   {i}. {product['title'][:50]}...")
            return True
        else:
            print(f"❌ Failed with term '{term}': {result.get('error', 'Unknown error')}")
    
    print("❌ No search terms worked")
    return False

if __name__ == "__main__":
    result = asyncio.run(test_fresh_workflow())
    if result:
        print("\n🎉 Fresh workflow test successful!")
    else:
        print("\n💥 Fresh workflow test failed")