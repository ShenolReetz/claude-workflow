#!/usr/bin/env python3
"""
Test Component-Based Video Generation
Tests the new JSON2Video component approach for review elements
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.append('/home/claude-workflow')

from mcp_servers.Test_json2video_enhanced_server_v2 import JSON2VideoEnhancedMCPServerV2

async def test_component_video():
    """Test video generation with component-based review elements"""
    
    # Load API configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('json2video_api_key')
    if not api_key:
        print("❌ JSON2Video API key not found")
        return
    
    # Initialize JSON2Video server
    json2video_server = JSON2VideoEnhancedMCPServerV2(api_key)
    
    # Create test record data with proper review elements
    test_record_data = {
        'VideoTitle': 'Component Test - Review Elements',
        'VideoDescription': 'Testing component-based review elements',
        'ProductNo1Title': 'Amazing Product #1',
        'ProductNo1Rating': 5,  # Integer for component
        'ProductNo1Reviews': 2847,  # Integer for component 
        'ProductNo1Price': 999,  # Integer for component
        'ProductNo1Photo': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
        'ProductNo2Title': 'Great Product #2',
        'ProductNo2Rating': 5,  # Integer for component
        'ProductNo2Reviews': 1923,  # Integer for component
        'ProductNo2Price': 199,  # Integer for component
        'ProductNo2Photo': 'https://drive.google.com/uc?id=10-vElXFcVhVU5FDJUEGdh4I_ZziDN2lJ&export=download',
        'ProductNo3Title': 'Excellent Product #3',
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
    
    print("🧪 TESTING COMPONENT-BASED REVIEW ELEMENTS")
    print("=" * 60)
    print(f"🎯 Test Data:")
    print(f"   Product 1: {test_record_data['ProductNo1Rating']}⭐ | {test_record_data['ProductNo1Reviews']} reviews | ${test_record_data['ProductNo1Price']}")
    print(f"   Product 2: {test_record_data['ProductNo2Rating']}⭐ | {test_record_data['ProductNo2Reviews']} reviews | ${test_record_data['ProductNo2Price']}")
    print(f"   Product 3: {test_record_data['ProductNo3Rating']}⭐ | {test_record_data['ProductNo3Reviews']} reviews | ${test_record_data['ProductNo3Price']}")
    print(f"   Product 4: {test_record_data['ProductNo4Rating']}⭐ | {test_record_data['ProductNo4Reviews']} reviews | ${test_record_data['ProductNo4Price']}")
    print(f"   Product 5: {test_record_data['ProductNo5Rating']}⭐ | {test_record_data['ProductNo5Reviews']} reviews | ${test_record_data['ProductNo5Price']}")
    print()
    
    try:
        # Create video with component-based approach
        result = await json2video_server.create_perfect_timing_video(test_record_data)
        
        if result.get('success'):
            project_id = result.get('movie_id')
            video_url = result.get('video_url')
            
            print("✅ COMPONENT VIDEO CREATED SUCCESSFULLY!")
            print(f"🎬 Project ID: {project_id}")
            print(f"🔗 Video URL: {video_url}")
            print()
            print("🔍 KEY IMPROVEMENTS:")
            print("   ⭐ Star ratings use JSON2Video component 'advanced/070'")
            print("   💰 Prices use JSON2Video component 'advanced/060' with counter animation")
            print("   📊 Review counts use JSON2Video component 'advanced/060' with counter animation")
            print("   🎨 Professional Anton font for counters, star symbols for ratings")
            print()
            print("✨ This should fix the review element rendering issue!")
            print(f"📹 Watch your video at: {video_url}")
            
        else:
            print(f"❌ Video creation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during component video test: {str(e)}")
    
    finally:
        await json2video_server.close()

if __name__ == "__main__":
    asyncio.run(test_component_video())