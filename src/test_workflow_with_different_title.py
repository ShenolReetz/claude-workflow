#!/usr/bin/env python3
"""
Test workflow with a title that should work better
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer
from mcp_servers.amazon_category_scraper import AmazonCategoryScraper

async def test_workflow_with_different_title():
    """Test workflow with a title that should work better"""
    
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
    
    # Test with different titles
    test_titles = [
        "🔥 TOP 5 Gaming Headsets That Will Blow Your Mind! 🎮",
        "BEST Bluetooth Speakers You Need! 🔊 (Bass Test)",
        "TOP 5 Phone Cases That Actually Work! 📱",
        "🔥 5 INSANE Wireless Chargers You Need! ⚡️",
        "INSANE Monitors You NEED in 2025! 🔥"
    ]
    
    for title in test_titles:
        print(f"\n🧪 Testing title: {title}")
        
        # Step 1: Extract category
        print("🔍 Extracting category...")
        category_result = await extractor.extract_product_category(title)
        
        if not category_result['success']:
            print(f"❌ Category extraction failed: {category_result.get('error')}")
            continue
        
        clean_category = category_result['primary_category']
        print(f"✅ Extracted: {clean_category}")
        
        # Step 2: Try Amazon scraping
        print("🛒 Testing Amazon scraping...")
        search_terms = [clean_category] + category_result['search_terms']
        
        for term in search_terms[:3]:
            print(f"   🔍 Trying: {term}")
            result = await scraper.get_top_5_products(term)
            
            if result['success']:
                print(f"   ✅ Success! Found {len(result['products'])} products")
                print(f"   🎯 Working title: {title}")
                print(f"   🎯 Working search term: {term}")
                return True
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n❌ No working titles found")
    return False

if __name__ == "__main__":
    result = asyncio.run(test_workflow_with_different_title())
    if result:
        print("\n🎉 Found a working combination!")
    else:
        print("\n💥 No working combinations found")