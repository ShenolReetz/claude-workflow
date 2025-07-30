#!/usr/bin/env python3
"""
Debug script to test JSON2Video creation with minimal schema
"""

import httpx
import json
import asyncio
import sys

sys.path.append('/home/claude-workflow')

async def test_minimal_video():
    """Test with minimal schema to identify the issue"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config.get('json2video_api_key')
    
    print(f"🔑 Using API key: {api_key[:8]}...")
    
    # Create minimal schema - just intro and outro
    movie_json = {
        "resolution": "instagram-story",
        "width": 1080,
        "height": 1920,
        "quality": "high",
        "draft": False,
        "scenes": [
            {
                "id": "intro_scene",
                "comment": "Intro Scene",
                "duration": 5,
                "elements": [
                    {
                        "id": "intro_bg",
                        "type": "image",
                        "src": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop",
                        "x": 0,
                        "y": 0,
                        "width": None,
                        "height": None
                    },
                    {
                        "id": "intro_title",
                        "type": "text",
                        "text": "Test Video",
                        "style": "003",
                        "settings": {
                            "font-family": "Roboto",
                            "font-size": "6.5vw",
                            "color": "#FFD700"
                        },
                        "position": "custom",
                        "x": 100,
                        "y": 100,
                        "width": 880,
                        "height": 200
                    }
                ]
            }
        ]
    }
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    print("📡 Sending minimal video request...")
    print(json.dumps(movie_json, indent=2))
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.json2video.com/v2/movies",
            json={
                "movie": movie_json,
                "name": "Debug_Test_Video"
            },
            headers=headers
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project')
            print(f"✅ Project created: {project_id}")
            
            # Wait a bit then check status
            await asyncio.sleep(10)
            
            status_response = await client.get(
                f"https://api.json2video.com/v2/movies?project={project_id}",
                headers=headers
            )
            
            print(f"📊 Status check: {status_response.status_code}")
            print(f"📊 Status response: {status_response.text}")

if __name__ == "__main__":
    asyncio.run(test_minimal_video())