#!/usr/bin/env python3
"""Test affiliate link integration in platform metadata"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.content_generation_server import ContentGenerationMCPServer

async def test_affiliate_integration():
    """Test affiliate link integration across all platforms"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize server
    content_server = ContentGenerationMCPServer(config['anthropic_api_key'])
    
    # Sample data with affiliate information
    title = "Top 5 Gaming Keyboards Under $100"
    
    sample_products = [
        {
            'title': 'Corsair K55 RGB PRO',
            'optimized_title': 'Corsair K55 RGB PRO - Budget Gaming Excellence',
            'price': '79.99',
            'rating': '4.5'
        },
        {
            'title': 'Razer Cynosa V2',
            'optimized_title': 'Razer Cynosa V2 - Essential RGB Gaming Keyboard',
            'price': '59.99',
            'rating': '4.3'
        }
    ]
    
    # Sample affiliate data (as would come from Airtable)
    affiliate_data = [
        {
            'title': 'Corsair K55 RGB PRO Gaming Keyboard',
            'affiliate_link': 'https://amazon.com/dp/B087LBCTMB?tag=reviewch3kr0d-20',
            'image_url': 'https://m.media-amazon.com/images/I/71abc123.jpg',
            'price': '79.99',
            'rating': '4.5'
        },
        {
            'title': 'Razer Cynosa V2 Gaming Keyboard',
            'affiliate_link': 'https://amazon.com/dp/B084DGZP1L?tag=reviewch3kr0d-20', 
            'image_url': 'https://m.media-amazon.com/images/I/71def456.jpg',
            'price': '59.99',
            'rating': '4.3'
        },
        {
            'title': 'HyperX Alloy Core RGB Gaming Keyboard',
            'affiliate_link': 'https://amazon.com/dp/B07DMLFQWQ?tag=reviewch3kr0d-20',
            'image_url': 'https://m.media-amazon.com/images/I/71ghi789.jpg',
            'price': '49.99',
            'rating': '4.4'
        },
        {
            'title': 'SteelSeries Apex 3 Gaming Keyboard',
            'affiliate_link': 'https://amazon.com/dp/B07ZGDPT4M?tag=reviewch3kr0d-20',
            'image_url': 'https://m.media-amazon.com/images/I/71jkl012.jpg',
            'price': '69.99',
            'rating': '4.2'
        },
        {
            'title': 'Logitech G213 Prodigy Gaming Keyboard',
            'affiliate_link': 'https://amazon.com/dp/B01K1HJPQ0?tag=reviewch3kr0d-20',
            'image_url': 'https://m.media-amazon.com/images/I/71mno345.jpg',
            'price': '39.99',
            'rating': '4.1'
        }
    ]
    
    # Generate platform keywords
    platform_keywords = {
        'youtube': ['gaming keyboard 2025', 'best budget keyboard', 'RGB gaming setup', 'keyboard review'],
        'tiktok': ['gaming setup', 'keyboard test', 'amazon finds', 'budget gaming'],
        'instagram': ['#gamersetup', '#keyboardlover', '#budgetgaming', '#amazonfinds'],
        'wordpress': ['best gaming keyboards under 100', 'budget gaming keyboard review', 'RGB keyboard comparison']
    }
    
    print("🛒 Testing Affiliate Link Integration\n")
    print("=" * 80)
    
    # Test platform metadata generation with affiliate links
    print("\n📱 Generating platform-specific metadata with affiliate links...")
    platform_metadata = await content_server.generate_platform_upload_metadata(
        title, sample_products, platform_keywords, affiliate_data
    )
    
    if platform_metadata:
        # YouTube
        youtube = platform_metadata.get('youtube', {})
        if youtube:
            print(f"\n📺 YOUTUBE:")
            print(f"   Title: {youtube.get('title', 'N/A')}")
            print(f"   Description preview: {youtube.get('description', '')[:100]}...")
            print(f"   Has affiliate links: {'amazon.com' in youtube.get('description', '')}")
        
        # TikTok 
        tiktok = platform_metadata.get('tiktok', {})
        if tiktok:
            print(f"\n🎵 TIKTOK:")
            print(f"   Title: {tiktok.get('title', 'N/A')}")
            print(f"   Caption: {tiktok.get('caption', 'N/A')[:100]}...")
            print(f"   Has bio CTA: {'bio' in tiktok.get('caption', '').lower()}")
        
        # Instagram
        instagram = platform_metadata.get('instagram', {})
        if instagram:
            print(f"\n📸 INSTAGRAM:")
            print(f"   Title: {instagram.get('title', 'N/A')}")
            print(f"   Caption: {instagram.get('caption', 'N/A')[:100]}...")
            print(f"   Has bio CTA: {'bio' in instagram.get('caption', '').lower()}")
        
        # WordPress
        wordpress = platform_metadata.get('wordpress', {})
        if wordpress:
            print(f"\n📝 WORDPRESS:")
            print(f"   Title: {wordpress.get('title', 'N/A')}")
            print(f"   Meta Description: {wordpress.get('meta_description', 'N/A')[:100]}...")
            content = wordpress.get('content', '')
            print(f"   Has product images: {'<img' in content}")
            print(f"   Has affiliate links: {'amazon.com' in content}")
            print(f"   Has affiliate disclosure: {'affiliate' in content.lower()}")
    
    print("\n" + "=" * 80)
    
    # Show sample affiliate structure for Airtable
    print("\n📋 Required Airtable Fields for Affiliate Integration:")
    required_fields = [
        "ProductNo1AffiliateLink",
        "ProductNo1ImageURL", 
        "ProductNo1Price",
        "ProductNo1Rating",
        "ProductNo2AffiliateLink",
        "ProductNo2ImageURL",
        "ProductNo2Price", 
        "ProductNo2Rating",
        "... (continue for ProductNo3-5)"
    ]
    
    for field in required_fields:
        print(f"   • {field}")
    
    print("\n✅ Affiliate integration test completed!")
    
    # Show WordPress content preview
    if wordpress and wordpress.get('content'):
        print(f"\n📝 WordPress Content Preview (first 300 chars):")
        print("-" * 60)
        print(wordpress['content'][:300] + "...")

if __name__ == "__main__":
    asyncio.run(test_affiliate_integration())