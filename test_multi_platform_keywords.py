#!/usr/bin/env python3
"""
Test Multi-Platform Keyword Generation
Tests the new system that generates platform-specific keywords for all social media
"""
import asyncio
import json
import sys
import os

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp_servers.content_generation_server import ContentGenerationMCPServer
from mcp_servers.airtable_server import AirtableMCPServer

async def test_multi_platform_keywords():
    """Test the complete multi-platform keyword generation"""
    
    print("🧪 Testing Multi-Platform Keyword Generation")
    print("=" * 60)
    
    # Load configuration
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Initialize servers
    content_server = ContentGenerationMCPServer(config['anthropic_api_key'])
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    # Test data - simulating Amazon scraper results
    test_title = "Top 5 Wireless Headphones 2025"
    test_products = [
        {
            'title': 'Apple AirPods Pro (2nd Generation)',
            'asin': 'B0BV9F196L', 
            'price': '$199.99',
            'rating': '4.5',
            'reviews': '41609'
        },
        {
            'title': 'Sony WH-CH720N Noise Canceling Headphones',
            'asin': 'B0C3KWT5V6',
            'price': '$89.99', 
            'rating': '4.6',
            'reviews': '32136'
        },
        {
            'title': 'Bose QuietComfort 45 Headphones',
            'asin': 'B098FKXT8L',
            'price': '$329.00',
            'rating': '4.4',
            'reviews': '16271'
        }
    ]
    
    print(f"🎯 Test Title: {test_title}")
    print(f"📦 Test Products: {len(test_products)}")
    print()
    
    # Test multi-platform keyword generation
    print("🔍 Generating multi-platform keywords...")
    print("⚠️  NOTE: This will use Claude API credits")
    print()
    
    multi_keywords = await content_server.generate_multi_platform_keywords(
        title=test_title,
        products=test_products
    )
    
    # Display results
    print("\n📊 MULTI-PLATFORM KEYWORD RESULTS:")
    print("=" * 50)
    
    platforms = ['youtube', 'instagram', 'tiktok', 'wordpress', 'universal']
    for platform in platforms:
        keywords = multi_keywords.get(platform, [])
        print(f"\n🎯 {platform.upper()} ({len(keywords)} keywords):")
        
        if platform == 'instagram':
            # Display hashtags in a more readable format
            hashtag_lines = []
            current_line = ""
            for hashtag in keywords:
                if len(current_line + hashtag + " ") > 60:
                    hashtag_lines.append(current_line.strip())
                    current_line = hashtag + " "
                else:
                    current_line += hashtag + " "
            if current_line:
                hashtag_lines.append(current_line.strip())
            
            for line in hashtag_lines:
                print(f"   {line}")
        else:
            # Display other keywords as list
            for i, keyword in enumerate(keywords, 1):
                print(f"   {i:2d}. {keyword}")
    
    print(f"\n📋 TOTAL KEYWORDS GENERATED: {sum(len(keywords) for keywords in multi_keywords.values())}")
    
    # Test Airtable integration
    print("\n💾 Testing Airtable integration...")
    test_record_id = "test_multi_platform_record"
    
    success = await airtable_server.update_multi_platform_keywords(
        record_id=test_record_id,
        keywords_data=multi_keywords
    )
    
    if success:
        print("✅ Airtable update simulation successful")
    else:
        print("❌ Airtable update simulation failed")
    
    print("\n" + "=" * 60)
    
    # Show what each platform optimizes for
    print("🎯 PLATFORM OPTIMIZATION BREAKDOWN:")
    print("""
    📺 YOUTUBE KEYWORDS:
       → Search optimization, buyer intent, product-specific
       → Used for: Video tags, description hashtags, SEO
       
    📷 INSTAGRAM HASHTAGS:
       → Mix of trending and niche hashtags with # symbol
       → Used for: Post captions, Reels discovery
       
    🎵 TIKTOK KEYWORDS:
       → Gen Z search terms, trending challenges, discovery
       → Used for: Video captions, For You Page algorithm
       
    📝 WORDPRESS SEO:
       → Long-tail keywords, question-based, comparison terms
       → Used for: Blog post optimization, organic search
       
    🌐 UNIVERSAL KEYWORDS:
       → Core terms that work across all platforms
       → Used for: Cross-platform consistency, backup keywords
    """)
    
    print("🏁 Multi-platform keyword test completed!")

async def test_keyword_formatting():
    """Test the keyword formatting for each platform"""
    
    print("\n🧪 Testing Keyword Formatting...")
    
    # Test data
    sample_keywords = {
        'youtube': ['wireless headphones 2025', 'best earbuds review', 'apple airpods pro'],
        'instagram': ['techfinds', 'gadgetlover', 'wirelessheadphones', 'audiophile'],
        'tiktok': ['POV headphones', 'tech haul', 'must have gadgets'],
        'wordpress': ['best wireless headphones 2025', 'how to choose earbuds', 'airpods vs sony comparison'],
        'universal': ['headphones', 'audio', 'wireless', 'bluetooth']
    }
    
    print("📄 FORMATTED OUTPUT EXAMPLES:")
    
    # YouTube formatting
    youtube_str = ', '.join(sample_keywords['youtube'])
    print(f"\n📺 YouTube Keywords (comma-separated):")
    print(f"   {youtube_str}")
    
    # Instagram formatting  
    instagram_hashtags = []
    for tag in sample_keywords['instagram']:
        if not tag.startswith('#'):
            tag = f"#{tag}"
        instagram_hashtags.append(tag)
    instagram_str = ' '.join(instagram_hashtags)
    print(f"\n📷 Instagram Hashtags (space-separated with #):")
    print(f"   {instagram_str}")
    
    # TikTok formatting
    tiktok_str = ', '.join(sample_keywords['tiktok'])
    print(f"\n🎵 TikTok Keywords (comma-separated):")
    print(f"   {tiktok_str}")
    
    # WordPress formatting
    wordpress_str = ', '.join(sample_keywords['wordpress'])
    print(f"\n📝 WordPress SEO (comma-separated):")
    print(f"   {wordpress_str}")
    
    # Universal formatting
    universal_str = ', '.join(sample_keywords['universal'])
    print(f"\n🌐 Universal Keywords (comma-separated):")
    print(f"   {universal_str}")

if __name__ == "__main__":
    asyncio.run(test_multi_platform_keywords())
    asyncio.run(test_keyword_formatting())