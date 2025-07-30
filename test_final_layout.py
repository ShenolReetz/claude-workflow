#!/usr/bin/env python3
"""
Test Final Layout with Correct Order and Price Format
Tests: Star ratings, Review count, Price (with original price formatting)
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.append('/home/claude-workflow')

from mcp_servers.Test_json2video_enhanced_server_v2 import JSON2VideoEnhancedMCPServerV2

async def test_final_layout():
    """Test video generation with final layout: Stars | Reviews | Price"""
    
    # Load API configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('json2video_api_key')
    if not api_key:
        print("❌ JSON2Video API key not found")
        return
    
    # Initialize JSON2Video server
    json2video_server = JSON2VideoEnhancedMCPServerV2(api_key)
    
    # Create test record data with final layout requirements
    test_record_data = {
        'VideoTitle': 'Final Layout Test - Stars | Reviews | Price',
        'VideoDescription': 'Testing final layout with correct order and price format',
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
    
    print("🎯 TESTING FINAL LAYOUT: ⭐ STARS | 📊 REVIEWS | 💰 PRICE")
    print("=" * 70)
    print("📐 FINAL LAYOUT SPECIFICATIONS:")
    print("   ⭐ Star Ratings: X=80, Y=700, Size=6vw")
    print("   📊 Review Count: X=350, Y=700, Size=5vw (numbers only)")
    print("   💰 Price: X=550, Y=700, Size=10vw (original format restored)")
    print("   📏 All elements horizontally aligned at Y=700")
    print()
    print("🔄 CHANGES MADE:")
    print("   🔀 Swapped positions: Review count moved to middle, Price to right")
    print("   📈 Price font restored to 10vw (original large size)")
    print("   📊 Review count shows numbers only (no 'Reviews' text)")
    print()
    print(f"🧪 Test Data:")
    print(f"   Product 1: {test_record_data['ProductNo1Rating']}⭐ | {test_record_data['ProductNo1Reviews']} | ${test_record_data['ProductNo1Price']}")
    print(f"   Product 2: {test_record_data['ProductNo2Rating']}⭐ | {test_record_data['ProductNo2Reviews']} | ${test_record_data['ProductNo2Price']}")
    print(f"   Product 3: {test_record_data['ProductNo3Rating']}⭐ | {test_record_data['ProductNo3Reviews']} | ${test_record_data['ProductNo3Price']}")
    print(f"   Product 4: {test_record_data['ProductNo4Rating']}⭐ | {test_record_data['ProductNo4Reviews']} | ${test_record_data['ProductNo4Price']}")
    print(f"   Product 5: {test_record_data['ProductNo5Rating']}⭐ | {test_record_data['ProductNo5Reviews']} | ${test_record_data['ProductNo5Price']}")
    print()
    
    try:
        # Create video with final layout
        result = await json2video_server.create_perfect_timing_video(test_record_data)
        
        if result.get('success'):
            project_id = result.get('movie_id')
            video_url = result.get('video_url')
            
            print("✅ FINAL LAYOUT VIDEO CREATED SUCCESSFULLY!")
            print(f"🎬 Project ID: {project_id}")
            print(f"🔗 Video URL: {video_url}")
            print()
            print("🎯 FINAL LAYOUT FEATURES:")
            print("   📏 Perfect horizontal alignment at Y=700")
            print("   ⭐ Stars (X=80) - Yellow symbols, 6vw size")
            print("   📊 Reviews (X=350) - White numbers, 5vw size")
            print("   💰 Price (X=550) - Yellow $, 10vw size (prominent)")
            print("   🎨 Logical left-to-right reading order")
            print()
            print("✨ Layout order: ⭐ Stars → 📊 Reviews → 💰 Price")
            print(f"📹 Watch your video at: {video_url}")
            
        else:
            print(f"❌ Video creation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during final layout test: {str(e)}")
    
    finally:
        await json2video_server.close()

if __name__ == "__main__":
    asyncio.run(test_final_layout())