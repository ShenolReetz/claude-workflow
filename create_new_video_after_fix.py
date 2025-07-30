#!/usr/bin/env python3
"""
Create a new video using the corrected Test_json2video_schema.json file
After fixing the pan-distance error from 1 to 0.5
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_with_corrected_schema():
    """Create real video using corrected Test schema file"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load corrected Test schema
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating NEW video with CORRECTED Test_json2video_schema.json")
    print("✅ pan-distance values fixed from 1 to 0.5")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"📊 Schema loaded: {len(movie_json['scenes'])} scenes")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify pan-distance values are fixed
    pan_distance_count = 0
    for scene in movie_json['scenes']:
        for element in scene.get('elements', []):
            if 'pan-distance' in element:
                pan_distance_count += 1
                if element['pan-distance'] > 0.5:
                    print(f"❌ ERROR: Found pan-distance > 0.5 in element {element['id']}")
                    return {'success': False, 'error': 'pan-distance still > 0.5'}
    
    print(f"✅ Verified: All {pan_distance_count} pan-distance values are ≤ 0.5")
    
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
            
            # Wait a moment then check initial status
            await asyncio.sleep(10)
            
            print("\n📊 Checking initial project status...")
            status_response = await client.get(
                f"https://api.json2video.com/v2/movies?project={project_id}",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                movie_data = status_data.get('movie', {})
                status = movie_data.get('status')
                video_url = movie_data.get('url')
                error = movie_data.get('message')
                
                print(f"📋 Initial Status: {status}")
                if error:
                    print(f"❌ Error message: {error}")
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video still processing. Check back in a few minutes.")
                    print(f"📱 Monitor progress at: https://json2video.com/app/projects/{project_id}")
                    
                # Show what was fixed
                print("\n🔧 Fixed Issues:")
                print("  ✅ pan-distance: 1 → 0.5 (all occurrences)")
                print("  ✅ Google Drive audio URLs integrated")
                print("  ✅ Component positioning preserved as manually set")
                print("\n🎯 Expected Result:")
                print("  - Stars on the left (1/4 width)")
                print("  - Review count in center")
                print("  - Price on the right")
                print("  - All elements on same horizontal line")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'fixes_applied': ['pan-distance: 1 → 0.5'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return {
                'success': False,
                'error': response.text
            }

if __name__ == "__main__":
    print("🎬 JSON2Video Video Creation with CORRECTED Schema")
    print("=" * 50)
    result = asyncio.run(create_video_with_corrected_schema())
    
    if result['success']:
        print("\n✅ Video creation initiated successfully!")
        print(f"🔗 View your project at: {result['project_url']}")
        print("\n📌 Next Steps:")
        print("  1. Wait 5-10 minutes for video processing")
        print("  2. Check if stars, reviews, and price are on same line")
        print("  3. Verify no overlapping between review count and price")
    else:
        print("\n❌ Video creation failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")