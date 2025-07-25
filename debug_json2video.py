#!/usr/bin/env python3
"""
Debug JSON2Video API call to see what's happening
"""

import asyncio
import json
import httpx
from mcp_servers.Test_json2video_enhanced_server_v2 import JSON2VideoEnhancedMCPServerV2

async def debug_json2video():
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Create server
    server = JSON2VideoEnhancedMCPServerV2(config['json2video_api_key'])
    
    # Create test data
    test_record = {
        'VideoTitle': 'Test Video - Debug Mode',
        'IntroHook': 'Welcome to test video',
        'OutroCallToAction': 'Thanks for watching',
        'ProductNo1Title': 'Test Product 1',
        'ProductNo1Description': 'This is test product 1',
        'ProductNo1Price': '29.99',
        'ProductNo1Rating': '4.5',
        'ProductNo1Reviews': '150',
        'Product1VoiceText': 'Test voice 1',
        'ProductNo2Title': 'Test Product 2',
        'ProductNo2Description': 'This is test product 2',
        'ProductNo2Price': '39.99',
        'ProductNo2Rating': '4.3',
        'ProductNo2Reviews': '200',
        'Product2VoiceText': 'Test voice 2',
        'ProductNo3Title': 'Test Product 3',
        'ProductNo3Description': 'This is test product 3',
        'ProductNo3Price': '49.99',
        'ProductNo3Rating': '4.7',
        'ProductNo3Reviews': '180',
        'Product3VoiceText': 'Test voice 3',
        'ProductNo4Title': 'Test Product 4',
        'ProductNo4Description': 'This is test product 4',
        'ProductNo4Price': '19.99',
        'ProductNo4Rating': '4.2',
        'ProductNo4Reviews': '120',
        'Product4VoiceText': 'Test voice 4',
        'ProductNo5Title': 'Test Product 5',
        'ProductNo5Description': 'This is test product 5',
        'ProductNo5Price': '34.99',
        'ProductNo5Rating': '4.6',
        'ProductNo5Reviews': '250',
        'Product5VoiceText': 'Test voice 5'
    }
    
    print("🔍 Starting JSON2Video debug test...")
    
    # Build the movie JSON
    movie_json, project_name = server.build_perfect_timing_video(test_record)
    
    print(f"📋 Project name: {project_name}")
    print(f"📊 Movie JSON scenes: {len(movie_json['scenes'])}")
    print(f"📐 Resolution: {movie_json['resolution']}")
    print(f"🎨 Quality: {movie_json['quality']}")
    
    # Try to create the video
    print("\n🎬 Attempting to create video...")
    
    try:
        # Manual API call to debug
        headers = {
            "x-api-key": config['json2video_api_key'],
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            print(f"📡 Making POST request to: https://api.json2video.com/v2/movies")
            print(f"📋 JSON size: {len(json.dumps(movie_json))} characters")
            
            response = await client.post(
                "https://api.json2video.com/v2/movies",
                json=movie_json
            )
            
            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response headers: {dict(response.headers)}")
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                print(f"✅ Success! Response: {result}")
                project_id = result.get('project', '')
                if project_id:
                    print(f"🎯 Project ID: {project_id}")
                    print(f"🔗 Check at: https://json2video.com/app/projects/{project_id}")
                else:
                    print("⚠️ No project ID in response")
            else:
                print(f"❌ Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    await server.close()

if __name__ == "__main__":
    asyncio.run(debug_json2video())