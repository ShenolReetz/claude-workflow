#!/usr/bin/env python3
"""Test enhanced product optimization with SEO control"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.content_generation_server import ContentGenerationMCPServer
from mcp_servers.seo_optimization_control_server import SEOOptimizationControlServer

async def test_enhanced_optimization():
    """Test the complete enhanced optimization workflow"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize servers
    content_server = ContentGenerationMCPServer(config['anthropic_api_key'])
    seo_server = SEOOptimizationControlServer(config)
    
    # Test data
    title = "Top 5 Gaming Keyboards Under $100"
    
    print("🚀 Enhanced Product Optimization Test\n")
    print("=" * 80)
    
    # Step 1: Generate multi-platform keywords
    print("\n1️⃣ Generating multi-platform keywords...")
    sample_products = [
        {'title': 'Corsair K55 RGB PRO', 'price': '79.99', 'rating': '4.5'},
        {'title': 'Razer Cynosa V2', 'price': '59.99', 'rating': '4.3'},
        {'title': 'HyperX Alloy Core RGB', 'price': '49.99', 'rating': '4.4'}
    ]
    
    platform_keywords = await content_server.generate_multi_platform_keywords(title, sample_products)
    print(f"   Generated keywords for {len(platform_keywords)} platforms")
    
    # Get universal keywords
    universal_keywords = platform_keywords.get('universal', [])
    print(f"   Universal keywords: {', '.join(universal_keywords[:5])}...")
    
    # Step 2: Generate optimized product descriptions
    print("\n2️⃣ Optimizing product descriptions...")
    optimized_products = await content_server.generate_optimized_product_descriptions(
        sample_products, universal_keywords, title
    )
    
    if optimized_products:
        print(f"   Optimized {len(optimized_products)} products")
        for product in optimized_products[:2]:  # Show first 2
            print(f"     Rank #{product.get('rank', 'N/A')}: {product.get('optimized_title', '')}")
            print(f"       Description ({product.get('word_count', 0)} words): {product.get('optimized_description', '')[:60]}...")
    
    # Step 3: Generate attention-grabbing intro
    print("\n3️⃣ Generating attention-grabbing intro...")
    intro_data = await content_server.generate_attention_grabbing_intro(
        title, universal_keywords, "shocking"
    )
    
    if intro_data:
        print(f"   Intro: {intro_data.get('intro_text', '')}")
        print(f"   Hook type: {intro_data.get('hook_type', '')} | Retention score: {intro_data.get('retention_score', 0)}")
    
    # Step 4: Generate platform-specific metadata
    print("\n4️⃣ Generating platform-specific upload metadata...")
    platform_metadata = await content_server.generate_platform_upload_metadata(
        title, optimized_products, platform_keywords
    )
    
    if platform_metadata:
        for platform, metadata in platform_metadata.items():
            if metadata and 'title' in metadata:
                print(f"   {platform.capitalize()}: {metadata['title'][:50]}...")
    
    # Step 5: Calculate SEO score
    print("\n5️⃣ Calculating SEO optimization score...")
    content_data = {
        'intro_text': intro_data.get('intro_text', ''),
        'products': optimized_products,
        'outro': 'Check the affiliate links in our description for the best deals!'
    }
    
    seo_result = await seo_server.calculate_seo_score(
        content_data, universal_keywords, platform_metadata
    )
    
    if seo_result:
        print(f"   🎯 Overall SEO Score: {seo_result['overall_seo_score']}/100 ({seo_result.get('grade', 'N/A')})")
        print(f"   Status: {seo_result.get('optimization_status', 'Unknown')}")
        
        print("\n   📊 Component Scores:")
        components = seo_result.get('component_scores', {})
        for component, score in components.items():
            print(f"     {component.replace('_', ' ').title()}: {score}/100")
        
        print("\n   💡 Recommendations:")
        for rec in seo_result.get('recommendations', []):
            print(f"     • {rec}")
    
    # Step 6: Validate platform requirements
    print("\n6️⃣ Validating platform requirements...")
    validation_results = await seo_server.validate_platform_requirements(platform_metadata)
    
    for platform, validation in validation_results.items():
        status = "✅ VALID" if validation['is_valid'] else "❌ INVALID"
        print(f"   {platform.capitalize()}: {status}")
        
        if validation['issues']:
            for issue in validation['issues']:
                print(f"     - {issue}")
    
    print("\n" + "=" * 80)
    print("✅ Enhanced optimization test completed!")
    
    # Sample Airtable data structure
    print("\n📝 Sample Airtable Data Structure:")
    airtable_data = {
        'ProductNo1Title': optimized_products[0].get('optimized_title', '') if optimized_products else '',
        'ProductNo1Description': optimized_products[0].get('optimized_description', '') if optimized_products else '',
        'IntroHook': intro_data.get('intro_text', ''),
        'SEOScore': seo_result.get('overall_seo_score', 0),
        'YouTubeTitle': platform_metadata.get('youtube', {}).get('title', ''),
        'TikTokTitle': platform_metadata.get('tiktok', {}).get('title', ''),
        'InstagramTitle': platform_metadata.get('instagram', {}).get('title', ''),
        'WordPressTitle': platform_metadata.get('wordpress', {}).get('title', '')
    }
    
    print(json.dumps(airtable_data, indent=2))

if __name__ == "__main__":
    asyncio.run(test_enhanced_optimization())