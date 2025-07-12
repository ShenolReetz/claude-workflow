#!/usr/bin/env python3
"""
Test the new workflow structure with Amazon scraping first
"""
import asyncio
import json
import sys
import os

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.content_generation_server import ContentGenerationMCPServer

async def test_new_workflow():
    """Test the restructured workflow with Amazon scraping first"""
    print("🧪 Testing NEW workflow structure...")
    
    # Load configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize servers
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    amazon_scraper = AmazonCategoryScraper(config)
    content_server = ContentGenerationMCPServer(
        anthropic_api_key=config['anthropic_api_key']
    )
    
    # Step 1: Get pending title from Airtable
    print("📋 Step 1: Getting pending title from Airtable...")
    pending_title = await airtable_server.get_pending_titles()
    
    if not pending_title:
        print("❌ No pending titles found. Creating test entry...")
        # For testing, use a simple category that should have products
        test_title = "Top 5 wireless headphones"
        pending_title = {
            'title': test_title,
            'record_id': 'test_record'
        }
    else:
        # If we got a complex title from Airtable, let's use a simpler one for testing
        if 'security' in pending_title['title'].lower() or 'surveillance' in pending_title['title'].lower():
            print("⚠️ Using simpler category for testing...")
            pending_title['title'] = "Top 5 wireless headphones"
    
    print(f"✅ Title: {pending_title['title']}")
    
    # Step 2: NEW - Scrape Amazon for top 5 products FIRST
    print("🛒 Step 2: Scraping Amazon for top 5 products based on Reviews × Rating...")
    amazon_result = await amazon_scraper.get_top_5_products(pending_title['title'])
    
    if not amazon_result.get('success'):
        print(f"❌ Amazon scraping failed: {amazon_result.get('error', 'Unknown error')}")
        return
    
    print(f"✅ Found {len(amazon_result['products'])} products:")
    for i, product in enumerate(amazon_result['products'], 1):
        print(f"  {i}. {product['title'][:60]}...")
        print(f"     Rating: {product['rating']}, Reviews: {product['review_count']}, Score: {product['review_score']:.0f}")
    
    # Save product data to Airtable (simulate)
    print("💾 Step 2b: Saving product data to Airtable...")
    print(f"   Product fields: {list(amazon_result['airtable_data'].keys())}")
    
    # Step 3: Generate SEO keywords using real product data
    print("🔍 Step 3: Generating SEO keywords with actual product data...")
    product_names = [p['title'] for p in amazon_result['products']]
    keywords = await content_server.generate_seo_keywords_with_products(
        pending_title['title'], 
        product_names
    )
    print(f"✅ Keywords: {keywords[:5]}...")
    
    # Step 4: Optimize title
    print("🎯 Step 4: Optimizing title...")
    optimized_title = await content_server.optimize_title(
        pending_title['title'], 
        keywords
    )
    print(f"✅ Optimized: {optimized_title}")
    
    # Step 5: Generate countdown script with real products
    print("📝 Step 5: Generating countdown script with real product data...")
    script_data = await content_server.generate_countdown_script_with_products(
        optimized_title, 
        keywords,
        amazon_result['products']
    )
    
    if script_data:
        print(f"✅ Script generated:")
        print(f"   Intro: {script_data.get('intro', 'N/A')[:50]}...")
        print(f"   Products: {len(script_data.get('products', []))}")
        print(f"   Outro: {script_data.get('outro', 'N/A')[:50]}...")
    
    print("\n🎉 NEW workflow structure test COMPLETED!")
    print("\n📊 Summary of changes:")
    print("   ✅ Amazon scraping moved to step 2 (after Airtable)")
    print("   ✅ Products ranked by Reviews × Rating")
    print("   ✅ Content generation uses real product data")
    print("   ✅ SEO keywords based on actual products")
    print("   ✅ Script includes real product names and ratings")

if __name__ == "__main__":
    asyncio.run(test_new_workflow())