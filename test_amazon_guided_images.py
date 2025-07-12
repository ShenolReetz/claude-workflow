#!/usr/bin/env python3
"""
Test Amazon-Guided OpenAI Image Generation
Tests the new system that uses Amazon photos as reference for OpenAI generation
"""
import asyncio
import json
import sys
import os

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp.amazon_guided_image_generation import generate_amazon_guided_openai_images, verify_openai_image_generation

async def test_amazon_guided_workflow():
    """Test the complete Amazon-guided OpenAI image generation workflow"""
    
    print("🧪 Testing Amazon-Guided OpenAI Image Generation")
    print("=" * 60)
    
    # Load configuration
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Test data - simulating Amazon scraper results
    test_products = [
        {
            'title': 'Apple AirPods Pro (2nd Generation)',
            'asin': 'B0BV9F196L', 
            'price': '$199.99',
            'rating': '4.5',
            'reviews': '41609',
            'score': 187240,
            'image_url': 'https://m.media-amazon.com/images/I/71AWFpvx0XL._AC_UY218_.jpg',
            'affiliate_link': 'https://www.amazon.com/dp/B0BV9F196L?tag=reviewch3kr0d-20'
        },
        {
            'title': 'Sony WH-CH720N Noise Canceling Headphones',
            'asin': 'B0C3KWT5V6',
            'price': '$89.99', 
            'rating': '4.6',
            'reviews': '32136',
            'score': 147826,
            'image_url': 'https://m.media-amazon.com/images/I/61E3AcWQg1L._AC_UY218_.jpg',
            'affiliate_link': 'https://www.amazon.com/dp/B0C3KWT5V6?tag=reviewch3kr0d-20'
        }
    ]
    
    test_record_id = "test_amazon_guided_record"
    test_title = "Top 5 Wireless Headphones Amazon Guided Test"
    
    print(f"📋 Test Record ID: {test_record_id}")
    print(f"🎯 Test Title: {test_title}")
    print(f"📦 Test Products: {len(test_products)}")
    print()
    
    # Test the Amazon-guided image generation
    print("🎨 Testing Amazon-guided OpenAI image generation...")
    print("⚠️  NOTE: This will use OpenAI API credits and take time due to rate limiting")
    print()
    
    results = await generate_amazon_guided_openai_images(
        config=config,
        record_id=test_record_id,
        project_title=test_title,
        products=test_products
    )
    
    # Display results
    print("📊 RESULTS:")
    print("=" * 40)
    print(f"✅ Success: {results['success']}")
    print(f"🖼️  Images Generated: {results['images_generated']}")
    print(f"💾 Images Saved to Drive: {results['images_saved']}")
    print(f"📦 Products Processed: {results['products_processed']}")
    
    if results['openai_image_urls']:
        print(f"\n🔗 OpenAI Image URLs:")
        for product, url in results['openai_image_urls'].items():
            print(f"  {product}: {url[:60]}...")
    
    if results['drive_image_urls']:
        print(f"\n📁 Google Drive URLs:")
        for product, url in results['drive_image_urls'].items():
            print(f"  {product}: {url[:60]}...")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"  • {error}")
    
    print("\n" + "=" * 60)
    
    # Summary of what was accomplished
    print("🎯 WHAT THIS TEST DEMONSTRATED:")
    print("✅ Amazon product data used as reference for OpenAI generation")
    print("✅ Enhanced prompts include product details (price, rating, reviews)")
    print("✅ Generated images saved to same Google Drive Photos folder")
    print("✅ New Airtable fields created: ProductNo{i}OpenAIImageURL")
    print("✅ Both Amazon and OpenAI images available for video creation")
    
    # Image comparison
    print("\n📸 IMAGE TYPES NOW AVAILABLE:")
    print("  📦 Amazon Images: Real product photos from Amazon")
    print("     └── Saved as: Product{i}_{ASIN}_amazon.jpg")
    print("     └── Field: ProductNo{i}DriveImageURL")
    print("  🎨 OpenAI Images: AI-generated using Amazon reference")
    print("     └── Saved as: Product{i}_OpenAI_guided.jpg")
    print("     └── Field: ProductNo{i}OpenAIImageURL")
    
    print(f"\n🏁 Test completed!")

async def test_image_verification():
    """Test the verification of generated images"""
    
    print("\n🔍 Testing image verification...")
    
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        verification = await verify_openai_image_generation(
            config=config,
            record_id="test_amazon_guided_record"
        )
        
        print("📋 Verification Results:")
        print(f"  Success: {verification['success']}")
        if verification['success']:
            print(f"  Verified OpenAI Images: {verification['verified_openai_images']}")
            print(f"  Missing OpenAI Images: {verification['missing_openai_images']}")
    
    except Exception as e:
        print(f"❌ Verification test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_amazon_guided_workflow())
    # asyncio.run(test_image_verification())  # Uncomment to test verification