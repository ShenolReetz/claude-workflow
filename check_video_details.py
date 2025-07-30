#!/usr/bin/env python3
"""
Check the generated video details
"""

import httpx
import json
import asyncio
import sys

sys.path.append('/home/claude-workflow')

async def check_video_details():
    """Check the video that was created"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config.get('json2video_api_key')
    
    project_id = "DOsGbsjv8ZqCRlxi"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"https://api.json2video.com/v2/movies?project={project_id}",
            headers=headers
        )
        
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            movie_data = data.get('movie', {})
            
            print(f"\n🎥 Video Details:")
            print(f"Project ID: {project_id}")
            print(f"Status: {movie_data.get('status')}")
            print(f"URL: {movie_data.get('url')}")
            print(f"Duration: {movie_data.get('duration')} seconds")
            print(f"Resolution: {movie_data.get('width')}x{movie_data.get('height')}")
            print(f"Created: {movie_data.get('created_at')}")
            print(f"Completed: {movie_data.get('ended_at')}")
            
            # Parse the JSON to check components
            json_str = movie_data.get('json', '{}')
            video_json = json.loads(json_str)
            
            print(f"\n📊 Video Structure:")
            print(f"Scenes: {len(video_json.get('scenes', []))}")
            
            # Check for review components
            component_count = 0
            for scene in video_json.get('scenes', []):
                for element in scene.get('elements', []):
                    if element.get('type') == 'component':
                        component_count += 1
                        component_type = element.get('component', '')
                        if 'rating' in element.get('settings', {}):
                            print(f"✅ Star Rating Component found in {scene.get('id')}")
                            rating_val = element.get('settings', {}).get('rating', {}).get('value', 'N/A')
                            print(f"   Rating value: {rating_val}")
                        elif 'counter' in element.get('settings', {}):
                            counter_text = element.get('settings', {}).get('counter', {}).get('text', '')
                            if 'Reviews' in counter_text:
                                print(f"✅ Review Count Component found in {scene.get('id')}")
                            elif '$' in counter_text:
                                print(f"✅ Price Component found in {scene.get('id')}")
            
            print(f"\nTotal Components: {component_count}")
            print(f"\n🔗 Video URL: {movie_data.get('url')}")

if __name__ == "__main__":
    asyncio.run(check_video_details())