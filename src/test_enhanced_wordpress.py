#!/usr/bin/env python3
"""Test enhanced WordPress post generation with product photos and countdown format"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.wordpress_mcp import WordPressMCP

async def test_enhanced_wordpress():
    """Test the enhanced WordPress post generation"""
    
    print("🌐 Testing Enhanced WordPress Post Generation")
    print("=" * 60)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Test data with full product information including images
    test_data = {
        'VideoTitle': '🔥 Top 5 Car Amplifiers for INSANE Bass in 2025! 🚗',
        'VideoDescription': 'Discover the most powerful car amplifiers that will transform your audio experience! From budget-friendly options to premium powerhouses, we\'ve tested them all.',
        
        # Product 1 (will be shown as #5 in countdown)
        'ProductNo1Title': 'Rockford Fosgate T3000-1bdCP Power Series',
        'ProductNo1Description': 'Delivers 3000 watts of pure power with advanced thermal management and Class BD technology for the ultimate bass experience. Features precision engineering and rock-solid reliability.',
        'ProductNo1ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/71xKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo1AffiliateLink': 'https://www.amazon.com/dp/B001P2UKS6/ref=nosim?tag=reviewch3kr0d-20',
        'ProductNo1ReviewCount': '3456',
        'ProductNo1Rating': 4.7,
        
        # Product 2 (will be shown as #4)
        'ProductNo2Title': 'JL Audio XD1000/1v2 Monoblock Amplifier',
        'ProductNo2Description': 'Compact monoblock with 1000W RMS, NexD2 switching technology, and studio-quality sound reproduction. Perfect balance of power and efficiency.',
        'ProductNo2ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/81qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo2AffiliateLink': 'https://www.amazon.com/dp/B00U2K13S8/ref=nosim?tag=reviewch3kr0d-20',
        'ProductNo2ReviewCount': '2891',
        'ProductNo2Rating': 4.8,
        
        # Product 3 (will be shown as #3)
        'ProductNo3Title': 'Kicker CXA1200.1 Amplifier',
        'ProductNo3Description': 'Powerful 1200W mono amp with FIT2 technology, optimized for precise bass control and maximum efficiency. Built for serious bass enthusiasts.',
        'ProductNo3ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/71qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo3AffiliateLink': 'https://www.amazon.com/dp/B07QF8P2QX/ref=nosim?tag=reviewch3kr0d-20',
        'ProductNo3ReviewCount': '5234',
        'ProductNo3Rating': 4.5,
        
        # Product 4 (will be shown as #2)
        'ProductNo4Title': 'Alpine MRV-M1200 Monoblock Amplifier',
        'ProductNo4Description': 'Alpine excellence with 1200W RMS, variable bass boost, and sophisticated protection circuitry. Premium build quality meets outstanding performance.',
        'ProductNo4ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/61qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo4AffiliateLink': 'https://www.amazon.com/dp/B01GQYVLVO/ref=nosim?tag=reviewch3kr0d-20',
        'ProductNo4ReviewCount': '4123',
        'ProductNo4Rating': 4.6,
        
        # Product 5 (will be shown as #1 - WINNER)
        'ProductNo5Title': 'Skar Audio RP-2000.1D Champion Series',
        'ProductNo5Description': 'The champion! 2000W RMS Class D monoblock with remote bass knob and competition-grade components. Unmatched power and reliability for serious installations.',
        'ProductNo5ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/91qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo5AffiliateLink': 'https://www.amazon.com/dp/B01M1I6FN8/ref=nosim?tag=reviewch3kr0d-20',
        'ProductNo5ReviewCount': '12567',
        'ProductNo5Rating': 4.9,
        
        # Video URL
        'VideoURL': 'https://youtube.com/watch?v=test123',
        'GoogleDriveURL': 'https://drive.google.com/file/d/test123/view'
    }
    
    # Initialize WordPress MCP
    wp_mcp = WordPressMCP(config)
    
    try:
        print("\n📝 Generating enhanced post content...")
        
        # Generate the post content (without actually posting)
        content = wp_mcp._generate_post_content(test_data)
        
        # Save to file for inspection
        output_file = '/home/claude-workflow/test_output/enhanced_wordpress_post.html'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>{test_data['VideoTitle']}</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .responsive {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <h1>{test_data['VideoTitle']}</h1>
    {content}
</body>
</html>
            """)
        
        print(f"✅ Enhanced post content generated!")
        print(f"💾 Saved to: {output_file}")
        
        # Analyze the generated content
        print(f"\n📊 Content Analysis:")
        print(f"   - Length: {len(content):,} characters")
        print(f"   - Contains images: {'<img src=' in content}")
        print(f"   - Has countdown format: {'countdown-header' in content}")
        print(f"   - Includes pros/cons: {'PROS' in content and 'CONS' in content}")
        print(f"   - Has affiliate buttons: {'amazon-button' in content}")
        print(f"   - Winner highlighting: {'WINNER' in content}")
        
        # Test pros/cons extraction
        print(f"\n🔍 Testing Pros/Cons Extraction:")
        for i in range(1, 6):
            title = test_data.get(f'ProductNo{i}Title', '')
            description = test_data.get(f'ProductNo{i}Description', '')
            if title:
                pros, cons = wp_mcp._extract_pros_cons(description)
                print(f"   Product {i}: {title[:30]}...")
                print(f"      Pros: {pros}")
                print(f"      Cons: {cons}")
        
        # Check if WordPress is enabled for actual posting
        if config.get('wordpress_enabled', False):
            print(f"\n⚠️  WordPress is enabled. To test actual posting, uncomment the create_review_post call below.")
            # result = await wp_mcp.create_review_post(test_data)
            # print(f"📝 Post result: {result}")
        else:
            print(f"\n⚠️  WordPress posting is disabled in config.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_wordpress())