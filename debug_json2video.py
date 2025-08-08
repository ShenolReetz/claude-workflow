#!/usr/bin/env python3
"""
Debug JSON2Video API response to see what's actually returned
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def debug_json2video_api():
    """Test JSON2Video API with minimal payload to see response format"""
    
    api_key = "s9gn6aT4ASaFaDbEpfbBsftbvf0IfEVZ9yD2FJKd"  # From config
    
    # Simple test schema
    test_schema = {
        "resolution": "instagram-story",
        "width": 1080,
        "height": 1920,
        "quality": "high",
        "draft": True,  # Use draft to avoid creating actual video
        "scenes": [{
            "comment": "Test scene",
            "duration": 3,
            "backgroundColor": "#000000",
            "elements": [{
                "type": "text",
                "text": "JSON2Video Test",
                "x": 540,
                "y": 960,
                "fontSize": 48,
                "color": "#FFFFFF"
            }]
        }]
    }
    
    print("🔍 Testing JSON2Video API response format...")
    print(f"📋 API Key: {api_key[:10]}...")
    print(f"📝 Test Schema: {json.dumps(test_schema, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.json2video.com/v2/movies"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            print(f"\n⏰ Making request to: {url}")
            start_time = datetime.now()
            
            async with session.post(url, headers=headers, json=test_schema) as response:
                request_time = (datetime.now() - start_time).total_seconds()
                print(f"⏰ Response received in {request_time:.2f} seconds")
                print(f"📊 Status Code: {response.status}")
                print(f"🔧 Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                response_text = await response.text()
                print(f"📏 Response length: {len(response_text)} characters")
                
                if response.status in [200, 201]:
                    try:
                        data = json.loads(response_text)
                        print(f"\n✅ JSON Response Structure:")
                        print("-" * 50)
                        print(json.dumps(data, indent=2))
                        print("-" * 50)
                        
                        # Extract key fields - JSON2Video returns project as STRING, not object
                        if 'project' in data:
                            project_id = data['project']  # Direct string value
                            print(f"\n🔍 Key Fields Extracted:")
                            print(f"   🆔 Project ID: {project_id}")
                            print(f"   📊 Type: {type(project_id)}")
                            
                            if project_id and isinstance(project_id, str):
                                dashboard_url = f"https://app.json2video.com/projects/{project_id}"
                                video_url = f"https://app.json2video.com/projects/{project_id}"  # Same URL format
                                print(f"   🌐 Dashboard URL: {dashboard_url}")
                                print(f"   🎬 Video URL: {video_url}")
                                print("✅ JSON2Video response parsing FIXED!")
                            else:
                                print(f"❌ Project ID not valid: {project_id}")
                                
                        else:
                            print(f"⚠️ No 'project' key in response")
                            print(f"🔍 Available keys: {list(data.keys())}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"📋 Raw response: {response_text}")
                        
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"❌ Response: {response_text}")
                    
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_json2video_api())