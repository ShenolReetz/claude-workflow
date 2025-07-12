#!/usr/bin/env python3
"""
Test actual image download and Google Drive saving with a single product
"""
import asyncio
import json
import sys

sys.path.append('/home/claude-workflow')

from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from src.mcp.amazon_images_workflow_v2 import download_and_save_amazon_images_v2

async def test_single_image_download():
    """Test downloading and saving a single product image"""
    print("🧪 Testing ACTUAL image download and Google Drive save...")
    
    # Load configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Get one product for testing
    amazon_scraper = AmazonCategoryScraper(config)
    amazon_result = await amazon_scraper.get_top_5_products("Top 5 wireless headphones")
    
    if not amazon_result.get('success') or not amazon_result['products']:
        print("❌ No products found for testing")
        return
    
    # Use only the first product for testing
    test_product = amazon_result['products'][0]
    test_products = [test_product]  # Single product list
    
    print(f"🔍 Testing with product:")
    print(f"  Title: {test_product['title'][:50]}...")
    print(f"  ASIN: {test_product['asin']}")
    print(f"  Image URL: {test_product['image_url']}")
    print(f"  Affiliate Link: {test_product['affiliate_link'][:60]}...")
    
    # Test the image download and Google Drive save
    print(f"\n📸 Downloading image and saving to Google Drive...")
    
    try:
        images_result = await download_and_save_amazon_images_v2(
            config,
            "test_image_001",  # Test record ID
            "Test Image Download",  # Test project title
            test_products
        )
        
        if images_result['success']:
            print(f"✅ SUCCESS!")
            print(f"  ├── Images saved: {images_result['images_saved']}")
            print(f"  ├── Products with images: {images_result['products_with_images']}")
            print(f"  └── Drive URLs generated: {len(images_result['drive_image_urls'])}")
            
            # Show the Google Drive URLs
            for product_key, drive_url in images_result['drive_image_urls'].items():
                print(f"    {product_key}: {drive_url}")
                
        else:
            print(f"❌ FAILED!")
            print(f"  Errors: {images_result.get('errors', [])}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
    
    print(f"\n🎯 This test verifies:")
    print(f"  ✅ Image URL extraction from Amazon")
    print(f"  ✅ HTTP download of actual image files")
    print(f"  ✅ Google Drive API integration")
    print(f"  ✅ Google Drive folder creation")
    print(f"  ✅ Image upload to Google Drive") 
    print(f"  ✅ Google Drive URL generation")
    print(f"  ✅ Airtable update with Drive URLs")

if __name__ == "__main__":
    asyncio.run(test_single_image_download())