#!/usr/bin/env python3
"""
Create a new video with FIXED subtitles configuration
- Subtitles moved to movie-level elements array
- Only one subtitle element (as required by JSON2Video)
- Auto-caption should now work properly
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_with_fixed_subtitles():
    """Create real video with fixed subtitle configuration"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load corrected Test schema
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with FIXED SUBTITLES configuration")
    print("🔧 Fixes applied:")
    print("  ✅ Subtitles moved to movie-level elements array")
    print("  ✅ Only one subtitle element (JSON2Video requirement)")
    print("  ✅ pan-distance values: 1 → 0.5")
    print("  ✅ Auto-caption should now work from audio")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"📊 Schema loaded: {len(movie_json['scenes'])} scenes")
    print(f"🎵 Movie elements: {len(movie_json.get('elements', []))} (including subtitles)")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        print(f"✅ Subtitle configuration correct:")
        print(f"   Language: {subtitle_config.get('language', 'auto')}")
        print(f"   Font: {subtitle_config.get('settings', {}).get('font-family', 'default')}")
        print(f"   Style: {subtitle_config.get('settings', {}).get('style', 'default')}")
        print(f"   Max words per line: {subtitle_config.get('settings', {}).get('max-words-per-line', 'default')}")
    else:
        print(f"❌ ERROR: Found {len(subtitle_elements)} subtitle elements, should be exactly 1")
        return {'success': False, 'error': f'Invalid subtitle count: {len(subtitle_elements)}'}
    
    # Verify no subtitle elements in scenes
    scene_subtitle_count = 0
    for scene in movie_json['scenes']:
        for element in scene.get('elements', []):
            if element.get('type') == 'subtitles':
                scene_subtitle_count += 1
    
    if scene_subtitle_count > 0:
        print(f"❌ ERROR: Found {scene_subtitle_count} subtitle elements in scenes (should be 0)")
        return {'success': False, 'error': f'Subtitles found in scenes: {scene_subtitle_count}'}
    
    print(f"✅ Scene validation: 0 subtitle elements in scenes (correct)")
    
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
                    
                # Show what should now work
                print("\n🎯 Expected Results:")
                print("  🎬 Review elements: Stars, count, price on same line")
                print("  📝 SUBTITLES: Auto-generated captions at bottom from audio")
                print("  🎵 Audio: Google Drive URLs should work properly")
                print("  ⏱️  Duration: ~50 seconds total")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'fixes_applied': [
                    'Subtitles moved to movie-level elements',
                    'Only one subtitle element',
                    'pan-distance: 1 → 0.5',
                    'Auto-caption from audio enabled'
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
    print("🎬 JSON2Video Video Creation with FIXED SUBTITLES")
    print("=" * 50)
    result = asyncio.run(create_video_with_fixed_subtitles())
    
    if result['success']:
        print("\n✅ Video creation initiated successfully!")
        print(f"🔗 View your project at: {result['project_url']}")
        print("\n📌 What should now work:")
        print("  1. Review elements positioned correctly (no overlap)")
        print("  2. SUBTITLES appearing at bottom with auto-captions")
        print("  3. Audio playing from Google Drive files")
        print("  4. Clean video rendering without errors")
    else:
        print("\n❌ Video creation failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")