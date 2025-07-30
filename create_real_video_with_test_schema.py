#!/usr/bin/env python3
"""
Create a real video using the Test_json2video_schema.json file
This will make actual API calls to JSON2Video
"""

import asyncio
import json
import httpx
import sys
import os

sys.path.append('/home/claude-workflow')

async def create_video_with_test_schema():
    """Create real video using Test schema file"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load Test schema
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating REAL video with Test_json2video_schema.json")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"📊 Schema loaded: {len(movie_json['scenes'])} scenes")
    
    # Make API request
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n🚀 Sending request to JSON2Video API...")
        response = await client.post(
            "https://api.json2video.com/v2/movies",
            json=movie_json,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project')
            print(f"✅ Video project created successfully!")
            print(f"🎥 Project ID: {project_id}")
            print(f"🔗 Project URL: https://json2video.com/app/projects/{project_id}")
            print(f"⏰ Video is being processed...")
            
            # Wait a moment then check status
            await asyncio.sleep(5)
            
            print("\n📊 Checking project status...")
            status_response = await client.get(
                f"https://api.json2video.com/v2/movies?project={project_id}",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                movie_data = status_data.get('movie', {})
                status = movie_data.get('status')
                video_url = movie_data.get('url')
                
                print(f"📋 Status: {status}")
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video still processing. Check back in a few minutes.")
                    print(f"📱 Monitor progress at: https://json2video.com/app/projects/{project_id}")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}"
            }
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return {
                'success': False,
                'error': response.text
            }

if __name__ == "__main__":
    print("🎬 JSON2Video Real Video Creation with Test Schema")
    print("=" * 50)
    result = asyncio.run(create_video_with_test_schema())
    
    if result['success']:
        print("\n✅ Video creation initiated successfully!")
        print(f"🔗 View your project at: {result['project_url']}")
    else:
        print("\n❌ Video creation failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")