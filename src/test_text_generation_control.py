#!/usr/bin/env python3
"""Test text generation control integration"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.content_generation_server import ContentGenerationMCPServer
from mcp_servers.text_generation_control_server import TextGenerationControlMCPServer

async def test_text_generation_control():
    """Test the text generation control workflow"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize servers
    content_server = ContentGenerationMCPServer(config['anthropic_api_key'])
    control_server = TextGenerationControlMCPServer(config)
    
    # Test title
    title = "Top 5 Gaming Keyboards Under $100"
    
    print("🎯 Text Generation Control Test\n")
    print("=" * 80)
    
    # Step 1: Generate keywords
    print("\n1️⃣ Generating SEO keywords...")
    keywords = await content_server.generate_seo_keywords(title, "Gaming Peripherals")
    print(f"   Generated {len(keywords)} keywords")
    
    # Step 2: Optimize title
    print("\n2️⃣ Optimizing title...")
    optimized_title = await content_server.optimize_title(title, keywords)
    print(f"   Original: {title}")
    print(f"   Optimized: {optimized_title}")
    
    # Step 3: Generate countdown script
    print("\n3️⃣ Generating countdown script...")
    script_data = await content_server.generate_countdown_script(optimized_title, keywords)
    
    if script_data and 'products' in script_data:
        print(f"   Generated script with {len(script_data['products'])} products")
        
        # Step 4: Validate with control server
        print("\n4️⃣ Validating with text generation control...")
        
        # Check intro/outro
        intro_result = await control_server.check_intro_outro(
            script_data.get('intro', ''),
            script_data.get('outro', '')
        )
        print(f"   Intro validation: {'✅ PASSED' if intro_result['intro']['is_valid'] else '❌ FAILED'}")
        if not intro_result['intro']['is_valid']:
            print(f"     Issue: {intro_result['intro']['issue']}")
        
        print(f"   Outro validation: {'✅ PASSED' if intro_result['outro']['is_valid'] else '❌ FAILED'}")
        if not intro_result['outro']['is_valid']:
            print(f"     Issue: {intro_result['outro']['issue']}")
        
        # Check each product
        print("\n   Product validations:")
        for i, product in enumerate(script_data['products'], 1):
            product_result = await control_server.check_countdown_products(
                products=[{
                    'title': product.get('name', ''),
                    'description': product.get('script', ''),
                    'rank': product.get('rank', i)
                }],
                keywords=keywords[:5],
                category=title
            )
            
            validation = product_result['validation_results'][0] if product_result['validation_results'] else None
            is_valid = validation['is_valid'] if validation else False
            print(f"     Product #{product.get('rank', i)}: {'✅' if is_valid else '❌'} {product.get('name', 'Unknown')[:40]}...")
            
            if not is_valid and validation:
                issues = validation.get('issues', [])
                print(f"       Issues: {', '.join(issues)}")
    
    # Step 5: Test generate_single_product method
    print("\n5️⃣ Testing generate_single_product method...")
    single_product_prompt = """
    Generate a product description for a gaming keyboard under $100.
    Make it exactly 20-25 words, mentioning key features like RGB, mechanical switches.
    Format: Brief, punchy description focusing on main selling points.
    """
    
    single_product = await content_server.generate_single_product(single_product_prompt)
    if single_product:
        print(f"   Generated: {single_product}")
        print(f"   Word count: {len(single_product.split())} words")
    else:
        print("   ❌ Failed to generate single product")
    
    print("\n" + "=" * 80)
    print("✅ Text generation control test completed!")

if __name__ == "__main__":
    asyncio.run(test_text_generation_control())