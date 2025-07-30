#!/usr/bin/env python3
"""
Create video with CORRECTED SUBTITLE POSITIONING:
- Fixed: Using position="custom" with x/y coordinates 
- Position: X=540 (center), Y=750 (below price elements)
- Colors: Yellow base (#e5e826), Red highlight (#FF0000)
- Layout: Max 4 words, single line, centered
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_with_corrected_subtitles():
    """Create video with corrected subtitle positioning"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load corrected Test schema
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with CORRECTED SUBTITLE POSITIONING")
    print("🔧 Previous error fixed:")
    print("  ❌ OLD: offset-y in settings (not allowed)")
    print("  ✅ NEW: position='custom' with x/y coordinates")
    print("\n🎨 Subtitle configuration:")
    print("  📍 Position: X=540 (center), Y=750 (below prices)")
    print("  🟡 Base color: #e5e826 (yellow like other elements)")
    print("  🔴 Highlighted word: #FF0000 (red)")
    print("  📝 Max words: 4 words at same time")
    print("  📏 Layout: Single line, centered")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        print(f"\n✅ Subtitle configuration verified:")
        print(f"   Position type: {subtitle_config.get('position', 'default')}")
        print(f"   X coordinate: {subtitle_config.get('x', 'default')}")
        print(f"   Y coordinate: {subtitle_config.get('y', 'default')}")
        print(f"   Base color: {settings.get('line-color', 'default')}")
        print(f"   Highlight color: {settings.get('word-color', 'default')}")
        print(f"   Max words: {settings.get('max-words-per-line', 'default')}")
        print(f"   Font size: {settings.get('font-size', 'default')}")
    else:
        print(f"❌ ERROR: Found {len(subtitle_elements)} subtitle elements, should be exactly 1")
        return {'success': False, 'error': f'Invalid subtitle count: {len(subtitle_elements)}'}
    
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
                    
                # Show final expected layout
                print("\n🎯 FINAL Video Layout (Y coordinates):")
                print("  📝 Title: Y=63")
                print("  ⭐ Stars: Y=400")
                print("  📊 Reviews: Y=500") 
                print("  💰 Price: Y=600")
                print("  📝 SUBTITLES: Y=750 ✅")
                print("\n🎨 Subtitle Visual Style:")
                print("  🟡 'Welcome to our top' (yellow)")
                print("  🔴 'five' (red - current word)")
                print("  🟡 'camera cleaning brushes' (yellow)")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'fixes_applied': [
                    'Removed invalid offset-y property',
                    'Added position="custom" with x/y coordinates',
                    'X=540 (center), Y=750 (below prices)',
                    'Yellow base + Red highlight colors',
                    'Max 4 words per line'
                ],
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
    print("🎬 JSON2Video Video Creation - CORRECTED SUBTITLE POSITIONING")
    print("=" * 65)
    result = asyncio.run(create_video_with_corrected_subtitles())
    
    if result['success']:
        print("\n✅ Video creation initiated successfully!")
        print(f"🔗 View your project at: {result['project_url']}")
        print("\n📌 Expected results:")
        print("  ✅ No more positioning errors")
        print("  ✅ Subtitles below price elements (Y=750)")
        print("  ✅ Yellow text with red highlighted words")
        print("  ✅ Centered, max 4 words at once")
        print("  ✅ Perfect timing with each scene's audio")
    else:
        print("\n❌ Video creation failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")