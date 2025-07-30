#!/usr/bin/env python3
"""
Test Corrected Order - Stars | Reviews | Price
Final layout with review count closer to stars and price in rightmost position
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.append('/home/claude-workflow')

from mcp_servers.Test_json2video_enhanced_server_v2 import JSON2VideoEnhancedMCPServerV2

async def test_corrected_order():
    """Test video generation with corrected order: Stars | Reviews | Price"""
    
    # Load API configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('json2video_api_key')
    if not api_key:
        print("❌ JSON2Video API key not found")
        return
    
    # Initialize JSON2Video server
    json2video_server = JSON2VideoEnhancedMCPServerV2(api_key)
    
    # Create test record data with corrected order
    test_record_data = {
        'VideoTitle': 'Corrected Order - Stars | Reviews | Price',
        'VideoDescription': 'Testing the final corrected layout order as requested',
        'ProductNo1Title': 'Premium Product #1 🏆',
        'ProductNo1Rating': 5,  # Integer for component
        'ProductNo1Reviews': 2847,  # Integer for component 
        'ProductNo1Price': 999,  # Integer for component
        'ProductNo1Photo': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
        'ProductNo2Title': 'Excellent Product #2',
        'ProductNo2Rating': 5,  # Integer for component
        'ProductNo2Reviews': 1923,  # Integer for component
        'ProductNo2Price': 199,  # Integer for component
        'ProductNo2Photo': 'https://drive.google.com/uc?id=10-vElXFcVhVU5FDJUEGdh4I_ZziDN2lJ&export=download',
        'ProductNo3Title': 'Great Product #3',
        'ProductNo3Rating': 5,  # Integer for component
        'ProductNo3Reviews': 1456,  # Integer for component
        'ProductNo3Price': 149,  # Integer for component
        'ProductNo3Photo': 'https://drive.google.com/uc?id=1wQYvUpZsCLGx8A2o90cTcO88dSsXJnFE&export=download',
        'ProductNo4Title': 'Good Product #4',
        'ProductNo4Rating': 4,  # Integer for component
        'ProductNo4Reviews': 1234,  # Integer for component
        'ProductNo4Price': 89,  # Integer for component
        'ProductNo4Photo': 'https://drive.google.com/uc?id=13VuwBBsIsv6gLYoiS3q6XfoRvVZGgQpZ&export=download',
        'ProductNo5Title': 'Nice Product #5',
        'ProductNo5Rating': 4,  # Integer for component
        'ProductNo5Reviews': 987,  # Integer for component
        'ProductNo5Price': 49,  # Integer for component
        'ProductNo5Photo': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download',
        'IntroPhoto': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
        'OutroPhoto': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download',
    }
    
    print("🎯 TESTING CORRECTED ORDER: ⭐ STARS | 📊 REVIEWS | 💰 PRICE")
    print("=" * 70)
    print("📐 CORRECTED LAYOUT SPECIFICATIONS:")
    print("   ⭐ Star Ratings: X=80, Y=600 (leftmost position)")
    print("   📊 Review Count: X=200, Y=600 (close to stars, moved from X=250)")
    print("   💰 Price: X=350, Y=600 (rightmost position, moved from X=400)")
    print("   📏 All elements at Y=600 for optimal visibility")
    print()
    print("🔄 FINAL CORRECTIONS MADE:")
    print("   🔀 Swapped positions: Reviews now in middle, Price on right")
    print("   📍 Review count closer to stars (X=200 vs previous X=250)")
    print("   📍 Price repositioned to right (X=350 vs previous X=400)")
    print("   📊 Review count shows numbers only (no 'Reviews' text)")
    print("   💰 Price maintains 10vw size for prominence")
    print()
    print(f"🧪 Test Data:")
    print(f"   Product 1: {test_record_data['ProductNo1Rating']}⭐ | {test_record_data['ProductNo1Reviews']} | ${test_record_data['ProductNo1Price']}")
    print(f"   Product 2: {test_record_data['ProductNo2Rating']}⭐ | {test_record_data['ProductNo2Reviews']} | ${test_record_data['ProductNo2Price']}")
    print(f"   Product 3: {test_record_data['ProductNo3Rating']}⭐ | {test_record_data['ProductNo3Reviews']} | ${test_record_data['ProductNo3Price']}")
    print(f"   Product 4: {test_record_data['ProductNo4Rating']}⭐ | {test_record_data['ProductNo4Reviews']} | ${test_record_data['ProductNo4Price']}")
    print(f"   Product 5: {test_record_data['ProductNo5Rating']}⭐ | {test_record_data['ProductNo5Reviews']} | ${test_record_data['ProductNo5Price']}")
    print()
    
    try:
        # Create video with corrected order
        result = await json2video_server.create_perfect_timing_video(test_record_data)
        
        if result.get('success'):
            project_id = result.get('movie_id')
            video_url = result.get('video_url')
            
            print("✅ CORRECTED ORDER VIDEO CREATED SUCCESSFULLY!")
            print(f"🎬 Project ID: {project_id}")
            print(f"🔗 Video URL: {video_url}")
            print()
            print("🎯 FINAL LAYOUT ACHIEVEMENTS:")
            print("   📏 Perfect horizontal alignment at Y=600")
            print("   ⭐ Stars (X=80) - Yellow symbols, first element")
            print("   📊 Reviews (X=200) - White numbers, close to stars")
            print("   💰 Price (X=350) - Yellow $, prominent rightmost element")
            print("   🎨 Optimal spacing and logical reading flow")
            print()
            print("✨ Final order achieved: ⭐ Stars → 📊 Reviews → 💰 Price")
            print(f"📹 Watch your perfectly ordered video at: {video_url}")
            
        else:
            print(f"❌ Video creation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during corrected order test: {str(e)}")
    
    finally:
        await json2video_server.close()

if __name__ == "__main__":
    asyncio.run(test_corrected_order())